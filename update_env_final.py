
content = """# Analytics Pipeline - Variables de Entorno
# ESTE ARCHIVO FUE RECONSTRUIDO AUTOMATICAMENTE - POR FAVOR VERIFICA TUS CREDENCIALES

# ============================================
# WOOCOMMERCE
# ============================================
WC_URL=https://tu-tienda.com
WC_CONSUMER_KEY=ck_xxxxx
WC_CONSUMER_SECRET=cs_xxxxx

# ============================================
# GOOGLE ANALYTICS 4
# ============================================
GA4_KEY_FILE=tu-service-account.json
GA4_PROPERTY_ID=123456789

# ============================================
# FACEBOOK
# ============================================
FB_ACCESS_TOKEN=EAAxxxxx_REPLACE_WITH_YOUR_TOKEN
FB_PAGE_ID=123456789_REPLACE_WITH_YOUR_PAGE_ID

# ============================================
# SISTEMA DE NOTIFICACIONES (NUEVO)
# ============================================
# Slack Webhooks (obtén tu webhook en: https://api.slack.com/messaging/webhooks)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Email Notifications
EMAIL_ALERTS_ENABLED=false
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_FROM=tu-email@gmail.com
EMAIL_PASSWORD=tu-password-de-app
EMAIL_ALERTS_TO=destino1@example.com,destino2@example.com

# ============================================
# BASE DE DATOS
# ============================================
DATABASE_TYPE=sqlite
# Para PostgreSQL (futuro):
# DB_HOST=localhost
# DB_PORT=5432
# DB_NAME=analytics
# DB_USER=postgres
# DB_PASSWORD=your_password

# ============================================
# CONFIGURACIÓN DE CACHÉ
# ============================================
CACHE_ENABLED=true
CACHE_TTL_HOURS=6
CACHE_COMPRESSION=true
"""

with open('.env', 'w', encoding='utf-8') as f:
    f.write(content.strip())
print("Reconstructed .env successfully")
