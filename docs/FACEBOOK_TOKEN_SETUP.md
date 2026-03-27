# Configuración de Token Permanente de Facebook

## Problema
Los tokens de usuario de Facebook expiran en 1-2 horas. Para automatizar la extracción de datos necesitamos un **token permanente**.

## Solución: Obtener Page Access Token Permanente

### Opción 1: Usando Graph API Explorer (Recomendado para Testing)

1. **Ve al Graph API Explorer**: https://developers.facebook.com/tools/explorer/

2. **Selecciona tu aplicación** en el dropdown superior

3. **Genera User Token**:
   - Click en "Generate Access Token"
   - Selecciona permisos:
     - `pages_show_list`
     - `pages_read_engagement`
     - `pages_manage_metadata`
     - `instagram_basic`
     - `instagram_manage_insights`
   - Autoriza

4. **Obtén tu App ID y App Secret**:
   - Ve a https://developers.facebook.com/apps/
   - Selecciona tu app
   - Settings → Basic
   - Copia el **App ID** y **App Secret**

5. **Ejecuta el script de conversión**:
```bash
python scripts/get_permanent_facebook_token.py
```

El script te pedirá:
- User Access Token (del Graph API Explorer)
- App ID
- App Secret

Y generará un **Page Access Token permanente** que nunca expira.

### Opción 2: Facebook Business Manager (Recomendado para Producción)

1. **Ve a Facebook Business Settings**: https://business.facebook.com/settings/

2. **System Users**:
   - Users → System Users → Add
   - Dale nombre (ej: "Frutos Tayen API")
   - Asigna rol: Admin

3. **Generate Token**:
   - Click en el system user
   - Generate New Token
   - Selecciona tu página
   - Selecciona permisos (igual que arriba)
   - **IMPORTANTE**: Marca "Token never expires"
   - Copia y guarda el token

4. **Actualiza la configuración**:
```bash
# Edita config/facebook_config.py
PAGE_ACCESS_TOKEN = "EAAhS7TP1JYk..."  # Token permanente
PAGE_ID = "1602976260000834"
```

## Verificar Token

```python
import requests

token = "TU_TOKEN_AQUI"
response = requests.get(f"https://graph.facebook.com/v19.0/me?access_token={token}")
print(response.json())
```

Si ves información de la página (no del usuario), ¡el token es válido! ✅

## Storage Seguro

**NO** commitees tokens en Git. Usa variables de entorno:

```bash
# .env
FACEBOOK_PAGE_TOKEN=EAAhS7TP1JYk...
FACEBOOK_PAGE_ID=1602976260000834
```

```python
# En tu código
import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('FACEBOOK_PAGE_TOKEN')
```

## Troubleshooting

### Token expira en 1-2 horas
→ Es un User Token de corta duración. Sigue los pasos arriba para obtener un Page Token permanente.

### Error "(#100) The value must be a valid insights metric"
→ Las métricas de Page Insights fueron deprecadas en API v19.0. Usa datos de Instagram o información básica de página.

### Error "Session has expired"
→ El token ha expirado. Genera uno nuevo siguiendo los pasos arriba.
