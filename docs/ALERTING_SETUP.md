# 📢 Sistema de Notificaciones y Alertas

Esta guía explica cómo configurar y usar el sistema de notificaciones automáticas del Analytics Pipeline.

## 🎯 Características

El sistema puede enviar notificaciones a través de:
- **Slack** - Mensajes instantáneos a canales de Slack
- **Email** - Alertas por correo electrónico con formato HTML

### Tipos de Alertas

1. **Alertas de Sistema**:
   - Fallos en el ETL después de reintentos
   - Errores de conexión a APIs
   - Problemas de autenticación

2. **Alertas de Negocio**:
   - Stock bajo en productos críticos
   - Caída significativa en ventas
   - Alto volumen de pedidos

3. **Reportes Automáticos** (futuro):
   - Resumen diario de ventas
   - Reporte semanal de performance
   - Análisis mensual

---

## 🔧 Configuración

### 1. Slack Notifications

#### Paso 1: Crear Webhook URL

1. Ve a https://api.slack.com/messaging/webhooks
2. Click en "Create your Slack app"
3. Selecciona "From scratch"
4. Nombre: "Analytics Pipeline Alerts"
5. Elige tu workspace
6. En "Incoming Webhooks", actívalo
7. Click "Add New Webhook to Workspace"
8. Selecciona el canal (#alerts, #monitoring, etc.)
9. Copia la Webhook URL

#### Paso 2: Configurar en .env

```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX
```

### 2. Email Notifications

#### Opción A: Gmail

1. Habilita "Verificación en 2 pasos" en tu cuenta de Google
2. Ve a https://myaccount.google.com/apppasswords
3. Genera una "Contraseña de aplicación"
4. Usa esa contraseña (no tu contraseña normal)

```bash
EMAIL_ALERTS_ENABLED=true
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_FROM=tu-email@gmail.com
EMAIL_PASSWORD=xxxx-xxxx-xxxx-xxxx  # Contraseña de aplicación
EMAIL_ALERTS_TO=destino@example.com,otro@example.com
```

#### Opción B: Otro Proveedor SMTP

Para Outlook/Office365:
```bash
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
```

Para SendGrid:
```bash
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
EMAIL_FROM=tu-email@tudominio.com
EMAIL_PASSWORD=tu-api-key-de-sendgrid
```

---

## 💻 Uso en Código

### Ejemplo Básico

```python
from utils.alerting import get_alerting_service, AlertLevel

# Obtener servicio
alerter = get_alerting_service()

# Enviar alerta simple
alerter.send_alert(
    AlertLevel.ERROR,
    "WooCommerce ETL Failed",
    "Error extracting orders after 3 retries",
    extractor="WooCommerce",
    error_type="ConnectionTimeout",
    retry_count=3
)
```

### Alertas de Negocio Predefinidas

```python
# Stock bajo
alerter.send_business_alert(
    'low_stock',
    {
        'product_name': 'iPhone 15 Pro',
        'quantity': 3
    }
)

# Caída en ventas
alerter.send_business_alert(
    'sales_drop',
    {
        'percentage': 35.5,
        'period': 'semana anterior'
    }
)

# Fallo en ETL
alerter.send_business_alert(
    'etl_failure',
    {
        'extractor': 'Google Analytics',
        'retries': 3
    }
)
```

### Integración en ETL

```python
# etl/extract_woocommerce.py
from utils.alerting import get_alerting_service, AlertLevel
from tenacity import retry, stop_after_attempt, wait_exponential

alerter = get_alerting_service()

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=60)
)
def extract_orders():
    try:
        # Lógica de extracción
        return fetch_woocommerce_orders()
    except Exception as e:
        # Si falla después de todos los reintentos
        alerter.send_alert(
            AlertLevel.ERROR,
            "WooCommerce Extraction Failed",
            f"Error: {str(e)}",
            extractor="WooCommerce",
            error=str(e),
            timestamp=datetime.now()
        )
        raise
```

---

## 📊 Niveles de Alerta

| Nivel | Uso | Canales |
|-------|-----|---------|
| `INFO` | Información general | Solo logs |
| `WARNING` | Advertencias | Solo logs |
| `ERROR` | Errores recuperables | Slack + Email + Logs |
| `CRITICAL` | Errores críticos | Slack + Email + Logs |

**Nota**: Solo `ERROR` y `CRITICAL` envían notificaciones a Slack/Email para evitar spam.

---

## 🎨 Personalización

### Custom Alert Types

Edita `utils/alerting.py` para agregar nuevos tipos:

```python
alerts_config = {
    # ...tipos existentes...
    'custom_alert': {
        'level': AlertLevel.WARNING,
        'title': 'Mi Alerta Personalizada',
        'message_template': 'Mensaje con {variable1} y {variable2}'
    }
}
```

Uso:
```python
alerter.send_business_alert(
    'custom_alert',
    {'variable1': 'valor1', 'variable2': 'valor2'}
)
```

### Cambiar Colores de Slack

En `_send_slack()`:
```python
color_map = {
    AlertLevel.ERROR: "#your_hex_color",
    # ...
}
```

---

## 🧪 Testing

```bash
# Ejecutar tests del sistema de alertas
python -m pytest tests/unit/test_alerting.py -v

# Test con coverage
python -m pytest tests/unit/test_alerting.py -v --cov=utils.alerting
```

---

## 🔍 Troubleshooting

### Slack no recibe mensajes

1. Verifica que el Webhook URL sea correcto
2. Asegúrate que el app tenga permisos en el canal
3. Revisa logs: `logs/etl.log`

### Emails no llegan

1. **Gmail**: Verifica que uses "Contraseña de aplicación", no tu contraseña normal
2. **Firewall**: Asegura que el puerto 587 esté abierto
3. **Spam**: Revisa carpeta de spam del destinatario
4. **Logs**: Busca errores en `logs/etl.log`

### Errores comunes

```
SMTPAuthenticationError: Username and Password not accepted
→ Solución: Usa contraseña de aplicación (Gmail)

ConnectionRefusedError: [Errno 111] Connection refused
→ Solución: Verifica SMTP_SERVER y SMTP_PORT

requests.exceptions.ConnectTimeout
→ Solución: Verifica tu conexión a internet y el Webhook URL
```

---

## 📈 Mejores Prácticas

1. **No hacer spam**: Solo envía `ERROR` y `CRITICAL` para cosas importantes
2. **Metadata útil**: Incluye información que ayude a debuggear
3. **Testing**: Usa variables de entorno diferentes para testing
4. **Monitoreo**: Revisa regularmente que las alertas funcionen

### Ejemplo: Testing sin enviar alerts reales

```bash
# .env.test
SLACK_WEBHOOK_URL=  # Vacío = deshabilitado
EMAIL_ALERTS_ENABLED=false
```

```python
# En tests
import os
os.environ['SLACK_WEBHOOK_URL'] = ''
os.environ['EMAIL_ALERTS_ENABLED'] = 'false'

# Ahora puedes probar sin enviar notificaciones reales
```

---

## 📚 Recursos

- [Slack Incoming Webhooks](https://api.slack.com/messaging/webhooks)
- [Gmail App Passwords](https://support.google.com/accounts/answer/185833)
- [Python smtplib Docs](https://docs.python.org/3/library/smtplib.html)

---

**Última actualización**: 22 de diciembre de 2025
