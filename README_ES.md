# 📊 Analytics & E-commerce Data Pipeline - Generic Edition

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen)
![Docker](https://img.shields.io/badge/docker-ready-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B)
![Status](https://img.shields.io/badge/status-production-success)

Pipeline ETL automatizado y **100% configurable** que extrae datos de **Google Analytics 4**, **WooCommerce** y **Facebook**, los procesa y visualiza mediante dashboards interactivos de Streamlit.

> **🆕 Versión Genérica**: Ahora puedes configurar tus propias credenciales mediante una interfaz web, sin modificar código. Ideal para múltiples proyectos o clientes.

---

## 🚀 Características

- ✅ **Sistema 100% Genérico** - Configurable para cualquier tienda/proyecto sin modificar código
- ✅ **Interfaz Web de Configuración** - Setup intuitivo mediante Streamlit
- ✅ **Validación en Tiempo Real** - Prueba tus credenciales antes de guardar
- ✅ **Multi-Fuentes** - WooCommerce + Google Analytics 4 + Facebook
- ✅ **Extracción automatizada** con carga incremental
- ✅ **Docker Ready** - Containerización para deployment fácil
- ✅ **CI/CD Pipeline** - GitHub Actions para testing y deployment automático
- ✅ **Logging estructurado** con rotación de archivos
- ✅ **Retry logic** automático para APIs externas
- ✅ **Tests automatizados** con pytest
- ✅ **Dashboards interactivos** con Streamlit
- ✅ **Optimización de queries** con índices de base de datos
- ✅ **Gestión segura de credenciales** mediante variables de entorno

---

## 📋 Requisitos Previos

- **Python 3.10+**
- **Credenciales de los servicios que desees conectar:**
  - WooCommerce: URL de tienda, Consumer Key, Consumer Secret
  - Google Analytics 4: Archivo JSON de Service Account, Property ID
  - Facebook: Access Token, Page ID (opcional)
- **Acceso a internet** para APIs externas

---

## ⚡ Inicio Rápido (Recomendado)

### 🚀 Instalación de Un Click

1. **Haz doble click en:**
   ```
   SETUP.bat
   ```
   El instalador verificará Python, creará el entorno virtual e instalará todas las dependencias automáticamente.

2. **Inicia la aplicación:**
   ```
   LAUNCH.bat
   ```

3. **Configura tus credenciales** en la interfaz web

4. **¡Listo!** 🎉

> 📖 **Guía completa de inicio rápido**: Ver [QUICK_START.md](QUICK_START.md)  
> 📦 **Para distribución**: Ver [DISTRIBUCION.md](DISTRIBUCION.md)

---

## 🔧 Instalación Manual (Avanzada)

### 1. Clonar o descargar el proyecto

```bash
cd "path/to/ExtraerDatosGoogleAnalitics_Generic"
```

### 2. Crear entorno virtual

```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar credenciales (NUEVO - Versión Genérica)

#### Opción A: Interfaz Web (Recomendado) ⭐

1. Iniciar el dashboard:
   ```bash
   streamlit run dashboard/app_woo_v2.py
   ```

2. En el sidebar, hacer click en **"⚙️ Configurar Credenciales"**

3. Seguir el wizard de configuración:
   - **WooCommerce**: URL, Consumer Key, Consumer Secret
   - **Google Analytics**: Subir archivo JSON, ingresar Property ID
   - **Facebook**: Access Token, Page ID

4. Hacer click en **"🔍 Test Connection"** para validar

5. Hacer click en **"💾 Save Configuration"**

6. Reiniciar la aplicación

#### Opción B: Manual (.env file)

1. Copiar el template:
   ```bash
   copy .env.example .env
   ```

2. Editar `.env` con tus credenciales:
   ```bash
   WC_URL=https://tu-tienda.com
   WC_CONSUMER_KEY=ck_xxxxx
   WC_CONSUMER_SECRET=cs_xxxxx
   
   GA4_KEY_FILE=tu-archivo.json
   GA4_PROPERTY_ID=123456789
   
   FB_ACCESS_TOKEN=EAAxxxxx
   FB_PAGE_ID=123456789
   ```

3. Para WooCommerce: Guardar archivo JSON de Google Analytics en el directorio raíz

📚 **Guía Detallada**: Ver [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md) para instrucciones paso a paso

### 5. Crear índices de base de datos (Opcional - Mejora rendimiento)

```bash
python config/apply_indexes.py
```

---

## 📖 Uso

### Ejecución Manual

#### Extraer datos de Google Analytics

```bash
python etl/extract_analytics.py
```

#### Extraer datos de WooCommerce

```bash
python etl/extract_woocommerce.py
```

#### Lanzar Dashboard

```bash
python -m streamlit run dashboard/app_woo_v2.py
```

### Ejecución Automática con Scheduler

```bash
python scheduler.py
```

El scheduler ejecutará automáticamente:
- **2:00 AM**: Extracción de Google Analytics
- **3:00 AM**: Extracción de WooCommerce

### 🐳 Deployment con Docker (Recomendado para Producción)

**Quick Start:**

```bash
# Windows
docker-start.bat

# Linux/Mac
chmod +x docker-start.sh
./docker-start.sh
```

**O manualmente:**

```bash
# Build y start en un comando
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener
docker-compose down
```

Accede al dashboard en: **http://localhost:8501**

📚 **Ver guía completa**: [docs/DOCKER_DEPLOYMENT.md](docs/DOCKER_DEPLOYMENT.md)

### ☁️ Deploy a Streamlit Cloud

Deploy gratis a Streamlit Cloud en 3 pasos:

1. Push tu código a GitHub
2. Conecta tu repo en [share.streamlit.io](https://share.streamlit.io)
3. Configura secretos y deploy

📚 **Ver guía completa**: [docs/STREAMLIT_CLOUD_DEPLOYMENT.md](docs/STREAMLIT_CLOUD_DEPLOYMENT.md)


---

## 🧪 Testing

### Ejecutar todos los tests

```bash
pytest tests/ -v
```

### Ejecutar tests con coverage

```bash
pytest tests/ -v --cov=etl --cov=utils --cov-report=html
```

### Ver reporte de coverage

```bash
# Windows
start htmlcov/index.html

# Linux/Mac
open htmlcov/index.html
```

---

## 📁 Estructura del Proyecto

```
ExtraerDatosGoogleAnalitics/
├── config/                          # Configuraciones
│   ├── logging_config.py            # Sistema de logging
│   ├── create_indexes.sql           # Índices SQL
│   └── apply_indexes.py             # Script para crear índices
├── etl/                             # Extractores ETL
│   ├── extract_analytics.py         # Extractor de GA4
│   └── extract_woocommerce.py       # Extractor de WooCommerce
├── utils/                           # Utilidades compartidas
│   ├── database.py                  # Operaciones de BD
│   ├── api_client.py                # Cliente API con retry
│   ├── notifications.py             # Sistema de notificaciones
│   ├── validators.py                # Validadores de datos
│   └── db_maintenance.py            # Mantenimiento de BD
├── dashboard/                       # Dashboard Streamlit
│   └── app_woo_v2.py                # Dashboard principal (responsive)
├── tests/                           # Suite de tests
│   ├── conftest.py                  # Fixtures compartidos
│   └── test_extractors.py           # Tests unitarios
├── logs/                            # Archivos de log
│   └── etl.log                      # Log principal
├── data/                            # Bases de datos SQLite
│   ├── analytics.db                 # Datos de GA4
│   └── woocommerce.db               # Datos de WooCommerce
├── docs/                            # Documentación
├── backups/                         # Backups de bases de datos
├── audit_data.py                    # Script de auditoría de datos
├── scheduler.py                     # Orquestador automático
├── requirements.txt                 # Dependencias Python
├── .gitignore                       # Archivos ignorados por git
└── README.md                        # Este archivo
```

---

## 🗄️ Esquema de Bases de Datos

### Analytics DB (`analytics.db`)

| Tabla | Descripción |
|-------|-------------|
| `ga4_channels` | Sesiones por canal de tráfico |
| `ga4_countries` | Usuarios activos por país |
| `ga4_pages` | Vistas de páginas |
| `ga4_ecommerce` | Métricas de e-commerce diarias |
| `ga4_products` | Productos vendidos |
| `ga4_traffic_sources` | Fuentes de tráfico |

### WooCommerce DB (`woocommerce.db`)

| Tabla | Descripción |
|-------|-------------|
| `wc_orders` | Órdenes de compra |
| `wc_order_items` | Items de cada orden |

---

## 📊 Dashboard

### `app_woo_v2.py` - Dashboard Principal

- **Diseño futurista** con tema responsive
- **Optimizado para móvil** (viewport adaptive)
- **Insights automáticos** con alertas contextuales
- **Comparaciones anuales** acumulativas
- **Filtros avanzados** por periodo y comparación
- **Gráficos interactivos** con Plotly
- **Métricas en tiempo real** de ventas y tráfico
- **Análisis de productos** (más/menos vendidos)
- **Fuentes de tráfico** normalizadas con iconos

---

## 🔍 Logs

Los logs se almacenan en `logs/etl.log` con rotación automática:
- **Tamaño máximo**: 10 MB por archivo
- **Backups**: 5 archivos históricos
- **Formato**: Timestamp, módulo, nivel, mensaje

Ejemplo:
```
2025-12-18 20:00:00 - etl.extract_analytics - INFO - 🚀 Iniciando extracción de Google Analytics
2025-12-18 20:00:15 - etl.extract_analytics - INFO - ✅ Extracted 1250 rows for Channels
```

---

## 🛠️ Mantenimiento

### Ver última fecha de extracción

```python
from utils.database import get_last_extraction_date

last_date = get_last_extraction_date('wc_orders', 'date_only', 'data/woocommerce.db')
print(f"Última extracción: {last_date}")
```

### Recrear índices

```bash
python config/apply_indexes.py
```

### Auditar datos

```bash
python audit_data.py
```

## ⚠️ Troubleshooting

### Error: `Configuration not found`
- Verificar que el archivo `.env` existe en el directorio raíz
- Usar la interfaz web de configuración: `streamlit run dashboard/app_woo_v2.py`
- Revisar que todas las variables requeridas están en `.env`

### Error: `WooCommerce API timeout`
- Verificar conexión a internet
- Probar conexión mediante página de Setup
- Aumentar timeout en `etl/extract_woocommerce.py`

### Error: `GA4 Permission denied`
- Asegurar que la service account tiene acceso al Property
- Verificar que el archivo JSON es válido
- Esperar hasta 24 horas para propagación de permisos

### Dashboard no carga datos
- Verificar que existan los archivos `.db` en `/data`
- Ejecutar primero los extractores ETL
- Revisar logs en `logs/etl.log`

### Configuración no funciona después de guardar
- Reiniciar la aplicación Streamlit
- Verificar que el archivo `.env` se creó correctamente
- Revisar permisos de escritura en el directorio

---

## 📈 Mejoras Futuras

- [ ] Soporte para más plataformas e-commerce (Shopify, Magento)
- [ ] Integración con más redes sociales (Instagram Insights, TikTok)
- [ ] Migración a PostgreSQL para mejor concurrencia
- [ ] Implementar Airflow para orquestación enterprise
- [ ] Agregar Great Expectations para validación de calidad
- [ ] CI/CD con GitHub Actions
- [ ] Modelo dimensional (Star Schema)
- [ ] Alertas automáticas por email/Slack
- [ ] Exportación de reportes a PDF/Excel
- [ ] API REST para acceso programático a datos

---

## 📞 Soporte y Documentación

- 📖 **Setup Guide**: [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md) - Guía detallada de configuración
- 🚀 **Deployment**: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) - Guía de despliegue en producción
- 📋 **Architecture**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Documentación técnica

Para reportar problemas o sugerir mejoras, revisar los logs en `logs/etl.log` y documentar el error con contexto.

---

## 🆕 Novedades de la Versión Genérica

### v1.0 - Generic Edition (Diciembre 2025)

**Nuevas Características:**
- ✨ Sistema 100% configurable sin modificar código
- 🌐 Interfaz web de configuración con Streamlit
- ✅ Validación en tiempo real de credenciales
- 🔐 Gestión segura mediante variables de entorno (.env)
- 📊 Dashboard de estado de configuración
- 🔌 Soporte para Facebook Page Insights
- 📚 Documentación completa de setup

**Migración desde versión anterior:**
1. Copiar `.env.example` a `.env`
2. Transferir credenciales hardcoded a `.env`
3. Probar extractores con nueva configuración

---

**Última actualización**: 21 de diciembre de 2025  
**Versión**: 1.0 - Generic Edition
