# 📦 Guía de Distribución

Esta guía explica cómo distribuir la aplicación a otros usuarios o clientes.

---

## 🎯 Métodos de Distribución

### Método 1: Carpeta Completa (Más Simple)

**Ideal para:** Usuarios con conocimientos básicos de informática

#### Pasos para distribuir:

1. **Crear paquete de distribución:**
   ```powershell
   # Copiar carpeta completa del proyecto
   # EXCLUIR estos archivos/carpetas:
   - venv/
   - data/
   - logs/
   - backups/
   - .env
   - __pycache__/
   - *.pyc
   ```

2. **Archivos que DEBE incluir:**
   ```
   ✅ SETUP.bat              (Instalador)
   ✅ LAUNCH.bat             (Lanzador)
   ✅ QUICK_START.md         (Guía rápida)
   ✅ README.md              (Documentación)
   ✅ .env.example           (Plantilla de config)
   ✅ requirements.txt       (Dependencias)
   ✅ Todo el código fuente
   ```

3. **Crear archivo `LEEME.txt` en la raíz:**
   ```
   ════════════════════════════════════════════════════════
   📊 ANALYTICS PIPELINE - INSTALACIÓN
   ════════════════════════════════════════════════════════

   1. Instala Python 3.10+ desde python.org
   2. Haz doble click en: SETUP.bat
   3. Sigue las instrucciones en pantalla

   Para más información, lee: QUICK_START.md
   ```

4. **Comprimir en .zip:**
   ```
   Analytics_Pipeline_v1.0.zip
   ```

#### Instrucciones para el usuario:

1. Descomprimir el archivo .zip
2. Leer `LEEME.txt`
3. Ejecutar `SETUP.bat`
4. Configurar credenciales en la web
5. ¡Listo!

---

### Método 2: Docker (Profesional)

**Ideal para:** Distribución empresarial o técnica

#### Pasos para distribuir:

1. **Incluir archivos Docker:**
   ```
   ✅ Dockerfile
   ✅ docker-compose.yml
   ✅ docker-start.bat
   ✅ .env.example
   ✅ .dockerignore
   ```

2. **Crear `INSTALL_DOCKER.md`:**
   ```markdown
   # Instalación con Docker

   1. Instala Docker Desktop:
      https://www.docker.com/products/docker-desktop

   2. Copia el archivo .env.example a .env
      ```
      copy .env.example .env
      ```

   3. Edita .env con tus credenciales

   4. Ejecuta:
      ```
      docker-start.bat
      ```

   5. Abre: http://localhost:8501
   ```

3. **Ventajas:**
   - No requiere instalar Python
   - Entorno aislado y reproducible
   - Funciona en Windows, Mac y Linux

---

### Método 3: Repositorio Git

**Ideal para:** Desarrolladores o equipos técnicos

#### Pasos:

1. **Subir a GitHub/GitLab:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <tu-repo>
   git push -u origin main
   ```

2. **El usuario clona:**
   ```bash
   git clone <tu-repo>
   cd Analytics_Pipeline
   SETUP.bat
   ```

3. **Crear buen README.md** (ya lo tienes)

---

### Método 4: Streamlit Cloud (Online)

**Ideal para:** Acceso web sin instalación

#### Pasos:

1. **Subir código a GitHub** (público o privado)

2. **Deploy en Streamlit Cloud:**
   - Ir a [share.streamlit.io](https://share.streamlit.io)
   - Conectar repositorio
   - Configurar secretos (.env)
   - Deploy

3. **Compartir URL:**
   ```
   https://tu-app.streamlit.app
   ```

4. **Ventajas:**
   - Acceso desde navegador
   - No requiere instalación
   - Multiplataforma
   - GRATIS para uso personal

---

## 📋 Checklist de Distribución

### Antes de distribuir:

- [ ] Probé la instalación en una máquina limpia
- [ ] Revisé que `SETUP.bat` funciona correctamente
- [ ] Incluí toda la documentación necesaria
- [ ] Eliminé archivos sensibles (.env, databases)
- [ ] Eliminé archivos temporales (venv/, __pycache__)
- [ ] Actualicé el README.md con info relevante
- [ ] Creé un archivo `LEEME.txt` claro
- [ ] Probé en Windows 10 y 11

### Archivos a NUNCA incluir:

❌ `.env` (contiene credenciales)
❌ `venv/` (entorno virtual)
❌ `data/*.db` (bases de datos con datos)
❌ `logs/*.log` (logs con información sensible)
❌ `backups/` (backups de bases de datos)
❌ `__pycache__/` (archivos compilados de Python)
❌ `*.pyc` (bytecode de Python)
❌ Credenciales JSON de Google
❌ Archivos personales

### Archivos SIEMPRE incluir:

✅ Código fuente completo
✅ `requirements.txt`
✅ `.env.example`
✅ `SETUP.bat`
✅ `LAUNCH.bat`
✅ `QUICK_START.md`
✅ `README.md`
✅ Toda la carpeta `docs/`
✅ Licencia (LICENSE)

---

## 🎁 Paquete de Distribución Recomendado

### Estructura ideal:

```
Analytics_Pipeline_v1.0/
│
├── 📄 LEEME.txt                    ← Instrucciones básicas
├── 📄 QUICK_START.md               ← Guía de inicio rápido
├── 📄 README.md                    ← Documentación completa
│
├── 🚀 SETUP.bat                    ← Instalador automático
├── 🚀 LAUNCH.bat                   ← Lanzador
├── 🗑️ UNINSTALL.bat               ← Desinstalador
│
├── ⚙️ .env.example                 ← Plantilla de configuración
├── 📦 requirements.txt             ← Dependencias
│
├── 📁 config/                      ← Configuraciones
├── 📁 dashboard/                   ← Aplicación web
├── 📁 docs/                        ← Documentación
├── 📁 etl/                         ← Extractores
├── 📁 scripts/                     ← Scripts auxiliares
├── 📁 tests/                       ← Tests
└── 📁 utils/                       ← Utilidades
```

---

## 🔐 Seguridad

### Antes de distribuir, ASEGÚRATE de:

1. **Eliminar credenciales:**
   ```powershell
   # Buscar credenciales en el código
   findstr /s /i "password\|secret\|token\|key" *.py
   ```

2. **Limpiar bases de datos:**
   ```powershell
   # Eliminar datos de ejemplo
   del /q data\*.db
   ```

3. **Revisar .gitignore:**
   ```
   # Archivo .gitignore debe incluir:
   .env
   *.db
   venv/
   __pycache__/
   logs/
   backups/
   ```

4. **Ejecutar script de limpieza:**
   ```powershell
   python scripts\clean_sensitive_files.py
   ```

---

## 💡 Consejos Profesionales

### 1. Versionado

Usa versionado semántico:
```
Analytics_Pipeline_v1.0.0
                    │ │ │
                    │ │ └─ Patch (bugs)
                    │ └─── Minor (features)
                    └───── Major (breaking changes)
```

### 2. Changelog

Crea un archivo `CHANGELOG.md`:
```markdown
# Changelog

## [1.0.0] - 2025-12-22
### Added
- Instalador de un click
- Dashboard interactivo
- Soporte para WooCommerce y Google Analytics
```

### 3. Licencia

Incluye un archivo `LICENSE`:
- MIT License (más permisiva)
- GPL (código abierto)
- Comercial (uso restringido)

### 4. Soporte

Incluye información de contacto:
```markdown
## 📞 Soporte

Email: soporte@tuempresa.com
WhatsApp: +56 9 XXXX XXXX
Website: https://tuempresa.com
```

---

## 📊 Opciones de Monetización (Opcional)

Si deseas vender la aplicación:

### Modelo SaaS
- Deploy en Streamlit Cloud
- Cobro mensual por usuario
- Sin instalación para el cliente

### Licencia por Instalación
- Cobro único por instalación
- Incluye soporte por X meses
- Actualizaciones incluidas

### Freemium
- Versión básica gratuita
- Versión premium con features avanzados
- Reportes, multi-usuario, etc.

---

## 🚀 Recursos Adicionales

### Para crear instaladores profesionales:

1. **Inno Setup** (Windows)
   - Crea archivos .exe instaladores
   - https://jrsoftware.org/isinfo.php

2. **PyInstaller** (Ejecutable único)
   ```bash
   pip install pyinstaller
   pyinstaller --onefile app.py
   ```

3. **NSIS** (Nullsoft Scriptable Install System)
   - Instalador avanzado
   - https://nsis.sourceforge.io/

---

## ✅ Testing de Distribución

Antes de distribuir, probar en:

- [ ] VM limpia con Windows 10
- [ ] VM limpia con Windows 11
- [ ] Computador sin Python instalado
- [ ] Computador con Python ya instalado
- [ ] Usuario sin conocimientos técnicos
- [ ] Usuario avanzado

---

**Última actualización:** 22 de diciembre de 2025  
**Versión:** 1.0 - Generic Edition
