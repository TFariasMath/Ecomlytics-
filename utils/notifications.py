"""
Sistema de Notificaciones.

Envía alertas por email cuando ocurren eventos importantes en el ETL:
- Errores en extracción
- Completado exitoso
- Anomalías en datos
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List
from datetime import datetime
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config.logging_config import setup_logger

logger = setup_logger(__name__)


class EmailNotifier:
    """Cliente para enviar notificaciones por email."""
    
    def __init__(
        self,
        smtp_host: str = "smtp.gmail.com",
        smtp_port: int = 587,
        from_email: Optional[str] = None,
        password: Optional[str] = None,
        to_emails: Optional[List[str]] = None
    ):
        """
        Inicializa el notificador de email.
        
        Args:
            smtp_host: Servidor SMTP
            smtp_port: Puerto SMTP
            from_email: Email remitente
            password: Contraseña del email
            to_emails: Lista de emails destino
        
        Note:
            Si no se proveen credenciales, se buscan en variables de entorno:
            - EMAIL_FROM
            - EMAIL_PASSWORD
            - EMAIL_TO (separados por coma)
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.from_email = from_email or os.getenv('EMAIL_FROM')
        self.password = password or os.getenv('EMAIL_PASSWORD')
        
        if to_emails:
            self.to_emails = to_emails
        else:
            to_env = os.getenv('EMAIL_TO', '')
            self.to_emails = [e.strip() for e in to_env.split(',') if e.strip()]
        
        self.enabled = bool(self.from_email and self.password and self.to_emails)
        
        if not self.enabled:
            logger.warning("⚠️ Email notifier no configurado (faltan credenciales)")
    
    def send_email(
        self,
        subject: str,
        body: str,
        is_html: bool = False
    ) -> bool:
        """
        Envía un email.
        
        Args:
            subject: Asunto del email
            body: Cuerpo del mensaje
            is_html: Si el body es HTML
        
        Returns:
            True si se envió exitosamente
        """
        if not self.enabled:
            logger.debug("Email notifier deshabilitado, no se envía notificación")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.to_emails)
            
            # Agregar cuerpo
            mime_type = 'html' if is_html else 'plain'
            msg.attach(MIMEText(body, mime_type))
            
            # Enviar
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.from_email, self.password)
                server.send_message(msg)
            
            logger.info(f"✅ Email enviado: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error enviando email: {e}", exc_info=True)
            return False
    
    def send_etl_success(
        self,
        etl_name: str,
        rows_extracted: int,
        duration_seconds: float
    ) -> bool:
        """
        Notifica extracción exitosa.
        
        Args:
            etl_name: Nombre del ETL
            rows_extracted: Filas extraídas
            duration_seconds: Duración en segundos
        """
        subject = f"✅ ETL {etl_name} - Exitoso"
        
        body = f"""
        <h2>ETL Completado Exitosamente</h2>
        <p><strong>Proceso:</strong> {etl_name}</p>
        <p><strong>Timestamp:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Filas extraídas:</strong> {rows_extracted:,}</p>
        <p><strong>Duración:</strong> {duration_seconds:.2f} segundos</p>
        <hr>
        <p style="color: green;">Estado: EXITOSO ✅</p>
        """
        
        return self.send_email(subject, body, is_html=True)
    
    def send_etl_failure(
        self,
        etl_name: str,
        error_message: str,
        traceback: Optional[str] = None
    ) -> bool:
        """
        Notifica fallo en ETL.
        
        Args:
            etl_name: Nombre del ETL
            error_message: Mensaje de error
            traceback: Stack trace completo
        """
        subject = f"❌ ETL {etl_name} - FALLÓ"
        
        body = f"""
        <h2 style="color: red;">ETL Falló</h2>
        <p><strong>Proceso:</strong> {etl_name}</p>
        <p><strong>Timestamp:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Error:</strong> {error_message}</p>
        """
        
        if traceback:
            body += f"""
            <hr>
            <h3>Stack Trace:</h3>
            <pre style="background: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto;">
{traceback}
            </pre>
            """
        
        body += """
        <hr>
        <p style="color: red;">Estado: FALLIDO ❌</p>
        <p>Por favor revisar los logs para más detalles.</p>
        """
        
        return self.send_email(subject, body, is_html=True)
    
    def send_data_quality_alert(
        self,
        issue: str,
        details: str
    ) -> bool:
        """
        Notifica problema de calidad de datos.
        
        Args:
            issue: Descripción del problema
            details: Detalles adicionales
        """
        subject = f"⚠️ Alerta de Calidad de Datos"
        
        body = f"""
        <h2 style="color: orange;">Alerta de Calidad de Datos</h2>
        <p><strong>Timestamp:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Problema:</strong> {issue}</p>
        <hr>
        <h3>Detalles:</h3>
        <p>{details}</p>
        <hr>
        <p style="color: orange;">Acción requerida: Revisar y corregir ⚠️</p>
        """
        
        return self.send_email(subject, body, is_html=True)


# Instancia global para uso fácil
default_notifier = EmailNotifier()


def notify_success(etl_name: str, rows: int, duration: float) -> None:
    """Shortcut para notificar éxito."""
    default_notifier.send_etl_success(etl_name, rows, duration)


def notify_failure(etl_name: str, error: str, traceback: str = None) -> None:
    """Shortcut para notificar fallo."""
    default_notifier.send_etl_failure(etl_name, error, traceback)


def notify_data_quality(issue: str, details: str) -> None:
    """Shortcut para alertas de calidad."""
    default_notifier.send_data_quality_alert(issue, details)
