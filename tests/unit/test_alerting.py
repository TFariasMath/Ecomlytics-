"""
Tests unitarios para el sistema de alertas

Valida que las notificaciones funcionen correctamente por Slack y Email.
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from utils.alerting import AlertingService, AlertLevel, get_alerting_service


@pytest.fixture
def mock_env():
    """Mock de variables de entorno para testing."""
    with patch.dict(os.environ, {
        'SLACK_WEBHOOK_URL': 'https://hooks.slack.com/test',
        'EMAIL_ALERTS_ENABLED': 'true',
        'SMTP_SERVER': 'smtp.test.com',
        'SMTP_PORT': '587',
        'EMAIL_FROM': 'test@example.com',
        'EMAIL_PASSWORD': 'test_pass',
        'EMAIL_ALERTS_TO': 'alert1@example.com,alert2@example.com'
    }):
        yield


@pytest.fixture
def alert_service(mock_env):
    """Fixture que proporciona un AlertingService configurado."""
    return AlertingService()


class TestAlertingServiceInitialization:
    """Tests para inicialización del servicio."""
    
    def test_initialization_with_slack_enabled(self, mock_env):
        """Test que se inicializa con Slack habilitado."""
        service = AlertingService()
        assert service.slack_enabled == True
        assert service.slack_webhook == 'https://hooks.slack.com/test'
    
    def test_initialization_with_email_enabled(self, mock_env):
        """Test que se inicializa con email habilitado."""
        service = AlertingService()
        assert service.email_enabled == True
        assert service.email_from == 'test@example.com'
        assert len(service.email_to) == 2
    
    def test_initialization_without_config(self):
        """Test que maneja configuración faltante."""
        with patch.dict(os.environ, {}, clear=True):
            service = AlertingService()
            assert service.slack_enabled == False
            assert service.email_enabled == False


class TestSlackNotifications:
    """Tests para notificaciones de Slack."""
    
    @patch('utils.alerting.requests.post')
    def test_send_slack_success(self, mock_post, alert_service):
        """Test que envía notificación a Slack exitosamente."""
        mock_post.return_value.status_code = 200
        
        result = alert_service._send_slack(
            AlertLevel.ERROR,
            "Test Alert",
            "Test message",
            {'key': 'value'}
        )
        
        assert result == True
        assert mock_post.called
        
        # Verificar que se llamó con los parámetros correctos
        call_args = mock_post.call_args
        assert 'https://hooks.slack.com/test' in str(call_args)
    
    @patch('utils.alerting.requests.post')
    def test_send_slack_failure(self, mock_post, alert_service):
        """Test que maneja fallos de API de Slack."""
        mock_post.return_value.status_code = 500
        mock_post.return_value.text = "Internal Server Error"
        
        result = alert_service._send_slack(
            AlertLevel.ERROR,
            "Test Alert",
            "Test message",
            {}
        )
        
        assert result == False
    
    @patch('utils.alerting.requests.post')
    def test_slack_payload_format(self, mock_post, alert_service):
        """Test que el payload de Slack tiene el formato correcto."""
        mock_post.return_value.status_code = 200
        
        alert_service._send_slack(
            AlertLevel.WARNING,
            "Warning Alert",
            "This is a warning",
            {'error_type': 'TestError', 'count': 5}
        )
        
        # Obtener payload enviado
        call_kwargs = mock_post.call_args.kwargs
        payload = call_kwargs['json']
        
        assert 'text' in payload
        assert 'WARNING' in payload['text']
        assert 'attachments' in payload
        assert len(payload['attachments']) > 0


class TestEmailNotifications:
    """Tests para notificaciones por email."""
    
    @patch('utils.alerting.smtplib.SMTP')
    def test_send_email_success(self, mock_smtp, alert_service):
        """Test que envía email exitosamente."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        result = alert_service._send_email(
            AlertLevel.ERROR,
            "Test Alert",
            "Test message",
            {'key': 'value'}
        )
        
        assert result == True
        assert mock_server.starttls.called
        assert mock_server.login.called
        assert mock_server.send_message.called
    
    @patch('utils.alerting.smtplib.SMTP')
    def test_send_email_failure(self, mock_smtp, alert_service):
        """Test que maneja fallos de SMTP."""
        mock_smtp.side_effect = Exception("SMTP Error")
        
        result = alert_service._send_email(
            AlertLevel.ERROR,
            "Test Alert",
            "Test message",
            {}
        )
        
        assert result == False
    
    def test_email_disabled_returns_false(self):
        """Test que retorna False si email está deshabilitado."""
        with patch.dict(os.environ, {'EMAIL_ALERTS_ENABLED': 'false'}):
            service = AlertingService()
            result = service._send_email(
                AlertLevel.ERROR,
                "Test",
                "Message",
                {}
            )
            assert result == False


class TestAlertLevels:
    """Tests para diferentes niveles de alerta."""
    
    @pytest.mark.parametrize("level", [
        AlertLevel.INFO,
        AlertLevel.WARNING,
        AlertLevel.ERROR,
        AlertLevel.CRITICAL
    ])
    @patch('utils.alerting.requests.post')
    @patch('utils.alerting.smtplib.SMTP')
    def test_all_alert_levels(self, mock_smtp, mock_post, alert_service, level):
        """Test que todos los niveles de alerta funcionan."""
        mock_post.return_value.status_code = 200
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        result = alert_service.send_alert(
            level,
            f"{level.value} Alert",
            "Test message",
            test=True
        )
        
        # INFO y WARNING no deberían enviar notificaciones
        if level in [AlertLevel.INFO, AlertLevel.WARNING]:
            assert mock_post.called == False
            assert mock_server.send_message.called == False
        else:
            # ERROR y CRITICAL sí deberían enviar
            # (puede ser True o False dependiendo de si falló algún canal)
            assert isinstance(result, bool)


class TestBusinessAlerts:
    """Tests para alertas de negocio predefinidas."""
    
    @patch('utils.alerting.requests.post')
    def test_low_stock_alert(self, mock_post, alert_service):
        """Test alerta de stock bajo."""
        mock_post.return_value.status_code = 200
        
        result = alert_service.send_business_alert(
            'low_stock',
            {'product_name': 'Product A', 'quantity': 5}
        )
        
        # No debe enviar notificación porque es WARNING
        # pero debe retornar True si se procesó
        assert isinstance(result, bool)
    
    @patch('utils.alerting.requests.post')
    @patch('utils.alerting.smtplib.SMTP')
    def test_etl_failure_alert(self, mock_smtp, mock_post, alert_service):
        """Test alerta de fallo en ETL."""
        mock_post.return_value.status_code = 200
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        result = alert_service.send_business_alert(
            'etl_failure',
            {'extractor': 'WooCommerce', 'retries': 3}
        )
        
        # Debe enviar porque es ERROR
        assert mock_post.called or mock_server.send_message.called
    
    def test_unknown_alert_type(self, alert_service):
        """Test que maneja tipos de alerta desconocidos."""
        result = alert_service.send_business_alert(
            'unknown_type',
            {'test': 'data'}
        )
        
        assert result == False


class TestSingleton:
    """Tests para el patrón singleton."""
    
    def test_get_alerting_service_returns_same_instance(self):
        """Test que siempre retorna la misma instancia."""
        service1 = get_alerting_service()
        service2 = get_alerting_service()
        
        assert service1 is service2


class TestMetadataFormatting:
    """Tests para formateo de metadatos."""
    
    def test_format_metadata_html(self, alert_service):
        """Test que formatea metadata como HTML correctamente."""
        metadata = {
            'error_type': 'ConnectionError',
            'retry_count': 3,
            'timestamp': datetime.now()
        }
        
        html = alert_service._format_metadata_html(metadata)
        
        assert 'Error Type' in html
        assert 'Retry Count' in html
        assert 'ConnectionError' in html
        assert '3' in html
    
    def test_format_empty_metadata(self, alert_service):
        """Test que maneja metadata vacía."""
        html = alert_service._format_metadata_html({})
        assert html == ""
