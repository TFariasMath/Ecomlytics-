@echo off
REM ====================================================================
REM  Analytics Pipeline - Instalador Automático
REM  Para Windows
REM ====================================================================

echo.
echo ========================================
echo   Analytics Pipeline - Instalacion
echo ========================================
echo.

REM Verificar que Python esté instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado
    echo.
    echo Por favor instala Python 3.10 o superior desde:
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANTE: Durante la instalacion, marca la opcion:
    echo   [X] Add Python to PATH
    echo.
    pause
    exit /b 1
)

echo [OK] Python detectado
python --version
echo.

REM Crear entorno virtual
echo [1/5] Creando entorno virtual...
if exist venv (
    echo Entorno virtual ya existe, omitiendo...
) else (
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] No se pudo crear entorno virtual
        pause
        exit /b 1
    )
    echo [OK] Entorno virtual creado
)
echo.

REM Activar entorno virtual
echo [2/5] Activando entorno virtual...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] No se pudo activar entorno virtual
    pause
    exit /b 1
)
echo [OK] Entorno virtual activado
echo.

REM Instalar dependencias
echo [3/5] Instalando dependencias...
echo Esto puede tomar 2-3 minutos...
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERROR] Error instalando dependencias
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas
echo.

REM Crear archivo .env si no existe
echo [4/5] Configurando ambiente...
if exist .env (
    echo Archivo .env ya existe, omitiendo...
) else (
    if exist .env.example (
        copy .env.example .env >nul
        echo [OK] Archivo .env creado desde .env.example
        echo IMPORTANTE: Debes configurar tus credenciales en el dashboard
    ) else (
        echo [AVISO] .env.example no encontrado
    )
)
echo.

REM Crear directorios necesarios
echo [5/5] Creando directorios...
if not exist data mkdir data
if not exist logs mkdir logs
if not exist backups mkdir backups
echo [OK] Directorios creados
echo.

echo ========================================
echo   Instalacion Completada!
echo ========================================
echo.
echo Proximos pasos:
echo.
echo 1. Abrir el dashboard:
echo    streamlit run dashboard\app_woo_v2.py
echo.
echo 2. Configurar credenciales:
echo    - Click en "Configurar Credenciales"
echo    - Ingresa tus datos de WooCommerce / Google Analytics
echo    - Prueba las conexiones
echo    - Guarda la configuracion
echo.
echo 3. Extraer datos:
echo    - Click en "Extraer datos nuevos"
echo    - Espera a que complete
echo    - Refresca el dashboard
echo.
echo Ver documentacion completa en: docs\SETUP_GUIDE.md
echo.
echo ========================================
echo.

REM Preguntar si quiere abrir el dashboard ahora
set /p OPEN_DASHBOARD="Quieres abrir el dashboard ahora? (s/n): "
if /i "%OPEN_DASHBOARD%"=="s" (
    echo.
    echo Abriendo dashboard...
    echo NOTA: Presiona Ctrl+C en la terminal para detener el servidor
    echo.
    streamlit run dashboard\app_woo_v2.py
) else (
    echo.
    echo Para abrir el dashboard mas tarde, ejecuta:
    echo   venv\Scripts\activate
    echo   streamlit run dashboard\app_woo_v2.py
    echo.
)

pause
