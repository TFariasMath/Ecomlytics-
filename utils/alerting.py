"""
Sistema de Notificaciones y Alertas

Este módulo proporciona notificaciones por Email y Slack para eventos importantes:
- Errores en ETL después de reintentos fallidos
- Alertas de negocio (ventas caídas, stock bajo)
- Reportes automáticos diarios/semanales

Uso:
    from utils.alerting import AlertingService, AlertLevel
    
    alerter = AlertingService()
    alerter.send_alert(
        AlertLevel.ERROR,
        "WooCommerce ETL Failed",
        "Error extracting orders after 3 retries",
        error_type="ConnectionError",
        timestamp=datetime.now()
    )
"""

import os
import requests
import smtplib
import logging
from enum import Enum
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Niveles de alerta para prioridades diferentes."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertingService:
    """Servicio de notificaciones por Slack y Email."""
    
    def __init__(self):
        """Inicializa el servicio con configuración desde variables de entorno."""
        # Slack configuration
        self.slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
        self.slack_enabled = bool(self.slack_webhook)
        
        # Email configuration
        self.email_enabled = os.getenv('EMAIL_ALERTS_ENABLED', 'false').lower() == 'true'
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.email_from = os.getenv('EMAIL_FROM', '')
        self.email_password = os.getenv('EMAIL_PASSWORD', '')
        self.email_to = os.getenv('EMAIL_ALERTS_TO', '').split(',')
        
        # Validate email config
        if self.email_enabled:
            if not all([self.email_from, self.email_password, self.email_to]):
                logger.warning("Email alerts enabled but configuration incomplete. Disabling email.")
                self.email_enabled = False
        
        logger.info(f"AlertingService initialized: Slack={self.slack_enabled}, Email={self.email_enabled}")
    
    def send_alert(
        self,
        level: AlertLevel,
        title: str,
        message: str,
        **metadata
    ) -> bool:
        """
        Envía una alerta a los canales configurados.
        
        Args:
            level: Nivel de la alerta (INFO, WARNING, ERROR, CRITICAL)
            title: Título de la alerta
            message: Mensaje detallado
            **metadata: Información adicional (key-value pairs)
        
        Returns:
            True si se envió al menos a un canal, False si falló en todos
        """
        success = False
        
        # Solo enviar email/slack para ERROR y CRITICAL
        if level in [AlertLevel.ERROR, AlertLevel.CRITICAL]:
            if self.slack_enabled:
                if self._send_slack(level, title, message, metadata):
                    success = True
            
            if self.email_enabled:
                if self._send_email(level, title, message, metadata):
                    success = True
        
        # Siempre loggear
        self._log_alert(level, title, message, metadata)
        
        return success
    
    def _send_slack(
        self,
        level: AlertLevel,
        title: str,
        message: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """Envía notificación a Slack."""
        if not self.slack_webhook:
            return False
        
        try:
            # Color map para diferentes niveles
            color_map = {
                AlertLevel.INFO: "#36a64f",      # Verde
                AlertLevel.WARNING: "#ff9800",   # Naranja
                AlertLevel.ERROR: "#f44336",     # Rojo
                AlertLevel.CRITICAL: "#9c27b0"   # Púrpura
            }
            
            # Iconos emoji para cada nivel
            emoji_map = {
                AlertLevel.INFO: ":information_source:",
                AlertLevel.WARNING: ":warning:",
                AlertLevel.ERROR: ":x:",
                AlertLevel.CRITICAL: ":fire:"
            }
            
            # Construir fields para metadata
            fields = []
            for key, value in metadata.items():
                fields.append({
                    "title": key.replace('_', ' ').title(),
                    "value": str(value),
                    "short": True
                })
            
            # Payload de Slack
            payload = {
                "text": f"{emoji_map[level]} *{level.value.upper()}*: {title}",
                "attachments": [{
                    "color": color_map[level],
                    "text": message,
                    "fields": fields,
                    "footer": "Analytics Pipeline Alert",
                    "ts": int(datetime.now().timestamp())
                }]
            }
            
            response = requests.post(
                self.slack_webhook,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.debug(f"Slack alert sent: {title}")
                return True
            else:
                logger.error(f"Slack API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Slack alert: {e}")
            return False
    
    def _send_email(
        self,
        level: AlertLevel,
        title: str,
        message: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """Envía notificación por email."""
        if not self.email_enabled:
            return False
        
        try:
            # Crear mensaje
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"[{level.value.upper()}] {title}"
            msg['From'] = self.email_from
            msg['To'] = ', '.join(self.email_to)
            
            # Construir cuerpo del email en HTML
            html_body = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .header {{ background-color: {self._get_level_color_html(level)}; color: white; padding: 20px; }}
                    .content {{ padding: 20px; }}
                    .metadata {{ background-color: #f5f5f5; padding: 15px; margin-top: 20px; }}
                    .metadata-item {{ margin: 5px 0; }}
                    .footer {{ color: #666; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h2>{level.value.upper()}: {title}</h2>
                </div>
                <div class="content">
                    <p><strong>Mensaje:</strong></p>
                    <p>{message}</p>
                    
                    {self._format_metadata_html(metadata)}
                </div>
                <div class="footer">
                    <p>Analytics Pipeline Monitoring System</p>
                    <p>Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </body>
            </html>
            """
            
            # Adjuntar HTML
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            # Enviar email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_from, self.email_password)
                server.send_message(msg)
            
            logger.debug(f"Email alert sent: {title}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email alert: {e}")
            return False
    
    def _get_level_color_html(self, level: AlertLevel) -> str:
        """Retorna color HTML para el nivel de alerta."""
        colors = {
            AlertLevel.INFO: "#4CAF50",
            AlertLevel.WARNING: "#FF9800",
            AlertLevel.ERROR: "#F44336",
            AlertLevel.CRITICAL: "#9C27B0"
        }
        return colors.get(level, "#666")
    
    def _format_metadata_html(self, metadata: Dict[str, Any]) -> str:
        """Formatea metadata como HTML."""
        if not metadata:
            return ""
        
        items_html = ""
        for key, value in metadata.items():
            key_formatted = key.replace('_', ' ').title()
            items_html += f'<div class="metadata-item"><strong>{key_formatted}:</strong> {value}</div>'
        
        return f'<div class="metadata"><h3>Detalles Adicionales</h3>{items_html}</div>'
    
    def _log_alert(
        self,
        level: AlertLevel,
        title: str,
        message: str,
        metadata: Dict[str, Any]
    ):
        """Loggea la alerta en el sistema de logs."""
        log_message = f"ALERT [{level.value.upper()}] {title}: {message}"
        if metadata:
            log_message += f" | Metadata: {metadata}"
        
        if level == AlertLevel.CRITICAL:
            logger.critical(log_message)
        elif level == AlertLevel.ERROR:
            logger.error(log_message)
        elif level == AlertLevel.WARNING:
            logger.warning(log_message)
        else:
            logger.info(log_message)
    
    def send_business_alert(
        self,
        alert_type: str,
        details: Dict[str, Any]
    ) -> bool:
        """
        Envía alertas de negocio predefinidas.
        
        Args:
            alert_type: Tipo de alerta ("low_stock", "sales_drop", "high_orders")
            details: Detalles específicos del alerta
        
        Returns:
            True si se envió exitosamente
        """
        alerts_config = {
            'low_stock': {
                'level': AlertLevel.WARNING,
                'title': 'Alerta de Stock Bajo',
                'message_template': 'El producto "{product_name}" tiene solo {quantity} unidades en stock'
            },
            'sales_drop': {
                'level': AlertLevel.WARNING,
                'title': 'Caída en Ventas Detectada',
                'message_template': 'Las ventas han caído {percentage}% comparado con {period}'
            },
            'high_orders': {
                'level': AlertLevel.INFO,
                'title': 'Alto Volumen de Pedidos',
                'message_template': 'Se recibieron {count} pedidos en las últimas {hours} horas'
            },
            'etl_failure': {
                'level': AlertLevel.ERROR,
                'title': 'Fallo en ETL Pipeline',
                'message_template': 'El extractor {extractor} falló después de {retries} reintentos'
            }
        }
        
        config = alerts_config.get(alert_type)
        if not config:
            logger.warning(f"Unknown alert type: {alert_type}")
            return False
        
        # Formatear mensaje con detalles
        message = config['message_template'].format(**details)
        
        return self.send_alert(
            config['level'],
            config['title'],
            message,
            **details
        )


# Singleton global
_alerting_instance: Optional[AlertingService] = None

def get_alerting_service() -> AlertingService:
    """Obtiene instancia singleton del servicio de alertas."""
    global _alerting_instance
    if _alerting_instance is None:
        _alerting_instance = AlertingService()
    return _alerting_instance
