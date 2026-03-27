@echo off
chcp 65001 >nul
color 0B
title 🚀 Instalador Automático - Analytics Pipeline

echo.
echo ════════════════════════════════════════════════════════════════
echo    🚀 INSTALADOR AUTOMÁTICO - ANALYTICS PIPELINE
echo ════════════════════════════════════════════════════════════════
echo.
echo    Este instalador configurará todo automáticamente:
echo    ✓ Verificar Python
echo    ✓ Crear entorno virtual
echo    ✓ Instalar dependencias
echo    ✓ Configurar el proyecto
echo.
echo ════════════════════════════════════════════════════════════════
echo.
timeout /t 2 >nul

REM ============================================================
REM PASO 1: Verificar Python
REM ============================================================
echo [1/5] 🔍 Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo.
    echo ❌ ERROR: Python no está instalado
    echo.
    echo Por favor instala Python 3.10 o superior desde:
    echo 👉 https://www.python.org/downloads/
    echo.
    echo ⚠️  IMPORTANTE: Durante la instalación, marca la opción
    echo     "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% encontrado
echo.

REM ============================================================
REM PASO 2: Crear entorno virtual
REM ============================================================
echo [2/5] 📦 Creando entorno virtual...

if exist venv (
    echo ⚠️  El entorno virtual ya existe
    set /p RECREATE="¿Deseas recrearlo? (S/N): "
    if /i "%RECREATE%"=="S" (
        echo 🗑️  Eliminando entorno virtual anterior...
        rmdir /s /q venv
        echo ✅ Creando nuevo entorno virtual...
        python -m venv venv
    ) else (
        echo ℹ️  Usando entorno virtual existente
    )
) else (
    python -m venv venv
    if %errorlevel% neq 0 (
        color 0C
        echo ❌ Error al crear el entorno virtual
        pause
        exit /b 1
    )
    echo ✅ Entorno virtual creado
)
echo.

REM ============================================================
REM PASO 3: Activar entorno virtual
REM ============================================================
echo [3/5] ⚡ Activando entorno virtual...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    color 0C
    echo ❌ Error al activar el entorno virtual
    pause
    exit /b 1
)
echo ✅ Entorno virtual activado
echo.

REM ============================================================
REM PASO 4: Instalar dependencias
REM ============================================================
echo [4/5] 📥 Instalando dependencias...
echo ℹ️  Esto puede tardar unos minutos según tu conexión...
echo.

python -m pip install --upgrade pip --quiet
if %errorlevel% neq 0 (
    color 0C
    echo ❌ Error al actualizar pip
    pause
    exit /b 1
)

pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    color 0C
    echo ❌ Error al instalar dependencias
    echo.
    echo Intenta ejecutar manualmente:
    echo    pip install -r requirements.txt
    pause
    exit /b 1
)
echo ✅ Dependencias instaladas correctamente
echo.

REM ============================================================
REM PASO 5: Configurar proyecto
REM ============================================================
echo [5/5] ⚙️  Configurando proyecto...

REM Crear directorios si no existen
if not exist data mkdir data
if not exist logs mkdir logs
if not exist backups mkdir backups
if not exist exports mkdir exports
echo ✅ Directorios creados

REM Crear .env si no existe
if not exist .env (
    if exist .env.example (
        copy .env.example .env >nul
        echo ✅ Archivo .env creado desde plantilla
        echo ⚠️  IMPORTANTE: Debes configurar tus credenciales en la aplicación
    ) else (
        echo ⚠️  No se encontró .env.example
    )
) else (
    echo ℹ️  Archivo .env ya existe
)
echo.

REM ============================================================
REM INSTALACIÓN COMPLETADA
REM ============================================================
color 0A
echo.
echo ════════════════════════════════════════════════════════════════
echo    ✅ ¡INSTALACIÓN COMPLETADA EXITOSAMENTE!
echo ════════════════════════════════════════════════════════════════
echo.
echo    📋 Próximos pasos:
echo.
echo    1. Ejecuta LAUNCH.bat para iniciar la aplicación
echo    2. Configura tus credenciales en la interfaz web
echo    3. ¡Comienza a usar el dashboard!
echo.
echo ════════════════════════════════════════════════════════════════
echo.

set /p LAUNCH="¿Deseas iniciar la aplicación ahora? (S/N): "
if /i "%LAUNCH%"=="S" (
    echo.
    echo 🚀 Iniciando aplicación...
    echo.
    call LAUNCH.bat
) else (
    echo.
    echo ℹ️  Puedes iniciar la aplicación en cualquier momento con:
    echo    LAUNCH.bat
    echo.
    pause
)
