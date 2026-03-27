# Subir a Streamlit Community Cloud

## Pasos Rápidos

### 1. Crea una cuenta en GitHub (si no tienes)
- Ve a [github.com](https://github.com) y regístrate

### 2. Crea un nuevo repositorio
- Ve a [github.com/new](https://github.com/new)
- Nombre: `analytics-dashboard`
- Privado o público (tú eliges)
- **NO** inicializar con README

### 3. Prepara tu proyecto
Abre PowerShell en la carpeta del proyecto y ejecuta:

```powershell
cd "C:\Users\USER\Documents\Maquina de produccion masiva\ExtraerDatosGoogleAnalitics_Generic"

# Inicializar git
git init

# Agregar todos los archivos (excepto los ignorados)
git add .

# Primer commit
git commit -m "Dashboard analytics"

# Conectar con GitHub (reemplaza TU_USUARIO)
git remote add origin https://github.com/TU_USUARIO/analytics-dashboard.git

# Subir
git push -u origin main
```

### 4. Para incluir los datos (opcional)
Si quieres incluir los archivos .db para que funcione en la nube:

```powershell
# Forzar agregar los archivos de datos
git add -f data/woocommerce.db
git add -f data/analytics.db
git commit -m "Add database files"
git push
```

### 5. Despliega en Streamlit Cloud
1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Inicia sesión con GitHub
3. Clic en **"New app"**
4. Configura:
   - **Repository**: `TU_USUARIO/analytics-dashboard`
   - **Branch**: `main`
   - **Main file path**: `dashboard/app_woo_v2.py`

### 6. Configura los Secrets
En **Advanced settings** → **Secrets**, pega tus credenciales:

```toml
WC_URL = "https://tu-tienda.com"
WC_CONSUMER_KEY = "ck_xxxxx"
WC_CONSUMER_SECRET = "cs_xxxxx"
COMPANY_NAME = "Tu Empresa"
```

### 7. Clic en "Deploy!"

---

## ⚠️ Notas importantes
- Los datos serán una **foto estática** del momento que subiste
- Para actualizar datos, debes hacer `git push` nuevamente
- Los cambios hechos en la nube (cerrar tickets, etc.) **no persisten**
