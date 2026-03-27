# 🚀 Guía de Inicio Rápido

## Instalación en 1 Click

### 📋 Requisitos Previos

**Antes de comenzar, necesitas tener instalado Python:**

1. Descarga Python 3.10 o superior desde: [python.org/downloads](https://www.python.org/downloads/)
2. Durante la instalación, **marca la opción "Add Python to PATH"**
3. Reinicia tu computadora después de instalar Python

---

## 🎯 Instalación Automática

### Opción 1: Instalador de Un Click (Recomendado)

1. **Haz doble click en:**
   ```
   SETUP.bat
   ```

2. **El instalador hará todo automáticamente:**
   - ✅ Verificará que Python esté instalado
   - ✅ Creará el entorno virtual
   - ✅ Instalará todas las dependencias
   - ✅ Configurará el proyecto
   - ✅ Te preguntará si quieres iniciar la app

3. **¡Listo!** Al finalizar, podrás usar la aplicación

---

## 🚀 Uso Diario

### Iniciar la Aplicación

**Método 1: Launcher de Un Click**
```
Haz doble click en: LAUNCH.bat
```

**Método 2: Manual**
```powershell
# 1. Activar entorno virtual
.\venv\Scripts\activate

# 2. Iniciar dashboard
streamlit run dashboard/app_woo_v2.py
```

La aplicación se abrirá en tu navegador en: **http://localhost:8501**

---

## ⚙️ Configuración de Credenciales

### Primera Vez

1. **Inicia la aplicación** con `LAUNCH.bat`

2. **En el sidebar**, haz click en **"⚙️ Configurar Credenciales"**

3. **Ingresa tus credenciales:**

   **WooCommerce:**
   - URL de la tienda: `https://tu-tienda.com`
   - Consumer Key: `ck_xxxxx`
   - Consumer Secret: `cs_xxxxx`

   **Google Analytics 4:**
   - Sube el archivo JSON de Service Account
   - Ingresa el Property ID

   **Facebook (Opcional):**
   - Access Token
   - Page ID

4. **Prueba la conexión** con el botón "🔍 Test Connection"

5. **Guarda** con el botón "💾 Save Configuration"

6. **Reinicia** la aplicación

---

## 📊 Extracción de Datos

### Automática (Recomendado)

El sistema extraerá datos automáticamente cada día a las 2:00 AM.

### Manual

Si quieres extraer datos ahora mismo:

1. **En el sidebar**, ve a **"Monitoreo ETL"**
2. Click en **"▶️ Run WooCommerce Extraction"**
3. Click en **"▶️ Run Google Analytics Extraction"**
4. Los datos se actualizarán en tiempo real

---

## 🆘 Solución de Problemas

### Error: "Python no está instalado"

**Solución:**
1. Instala Python desde [python.org](https://www.python.org/downloads/)
2. **IMPORTANTE:** Marca "Add Python to PATH" durante la instalación
3. Reinicia tu computadora
4. Ejecuta `SETUP.bat` nuevamente

### Error: "No se encontró el entorno virtual"

**Solución:**
1. Ejecuta primero `SETUP.bat`
2. Luego ejecuta `LAUNCH.bat`

### La aplicación no se abre en el navegador

**Solución:**
1. Abre manualmente tu navegador
2. Ve a: `http://localhost:8501`

### Error: "Configuration not found"

**Solución:**
1. Ve a "⚙️ Configurar Credenciales" en el sidebar
2. Ingresa todas las credenciales requeridas
3. Guarda y reinicia la aplicación

### Los datos no se cargan

**Solución:**
1. Ve a "Monitoreo ETL" en el sidebar
2. Ejecuta las extracciones manualmente
3. Verifica que las credenciales sean correctas

---

## 📁 Estructura de Archivos

```
Analytics Pipeline/
├── SETUP.bat              ← Instalador de un click
├── LAUNCH.bat             ← Lanzador de un click
├── QUICK_START.md         ← Esta guía
├── README.md              ← Documentación completa
├── .env                   ← Configuración (se crea automáticamente)
├── venv/                  ← Entorno virtual (se crea automáticamente)
├── data/                  ← Bases de datos
├── dashboard/             ← Aplicación web
└── etl/                   ← Extractores de datos
```

---

## 🎓 Tutoriales

### Video Tutorial
> 🎥 [Ver en YouTube](#) (próximamente)

### Pasos Visuales

#### 1. Instalación
![Instalación](docs/images/install.png)

#### 2. Configuración
![Configuración](docs/images/config.png)

#### 3. Dashboard
![Dashboard](docs/images/dashboard.png)

---

## 📞 Soporte

### Documentación Completa
- 📖 [README.md](README.md) - Documentación principal
- 🔧 [SETUP_GUIDE.md](docs/SETUP_GUIDE.md) - Guía de configuración detallada
- 🚀 [DEPLOYMENT.md](docs/DEPLOYMENT.md) - Guía de deployment

### Problemas Comunes
- Ver sección [Troubleshooting en README](README.md#troubleshooting)

---

## ✅ Checklist de Instalación

- [ ] Python 3.10+ instalado
- [ ] Ejecuté `SETUP.bat` exitosamente
- [ ] Ejecuté `LAUNCH.bat` y la app se abrió
- [ ] Configuré mis credenciales en la interfaz web
- [ ] Probé la conexión y funcionó
- [ ] Ejecuté la extracción de datos inicial
- [ ] Veo mis datos en el dashboard

**Si completaste todos los pasos, ¡estás listo para usar la aplicación! 🎉**

---

## 🎁 Características Principales

- ✅ **Dashboard Interactivo** - Visualiza tus datos en tiempo real
- ✅ **Multi-Fuente** - WooCommerce + Google Analytics + Facebook
- ✅ **Automático** - Extracción programada de datos
- ✅ **Comparaciones** - Compara períodos y años
- ✅ **Exportación** - Genera reportes en PDF y Excel
- ✅ **Responsive** - Funciona en móvil, tablet y desktop

---

**Última actualización:** 22 de diciembre de 2025  
**Versión:** 1.0 - Generic Edition
