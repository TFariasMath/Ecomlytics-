@echo off
chcp 65001 >nul
color 0B
title 🚀 Analytics Pipeline - Dashboard

echo.
echo ════════════════════════════════════════════════════════════════
echo    📊 ANALYTICS PIPELINE - DASHBOARD
echo ════════════════════════════════════════════════════════════════
echo.

REM Verificar si existe el entorno virtual
if not exist venv (
    color 0C
    echo ❌ ERROR: No se encontró el entorno virtual
    echo.
    echo Por favor ejecuta primero: SETUP.bat
    echo.
    pause
    exit /b 1
)

REM Activar entorno virtual
echo 🔄 Activando entorno virtual...
call venv\Scripts\activate.bat

REM Verificar si Streamlit está instalado
python -c "import streamlit" 2>nul
if %errorlevel% neq 0 (
    color 0C
    echo ❌ ERROR: Streamlit no está instalado
    echo.
    echo Por favor ejecuta: SETUP.bat
    echo.
    pause
    exit /b 1
)

echo ✅ Entorno preparado
echo.
echo ════════════════════════════════════════════════════════════════
echo.
echo    🚀 Iniciando aplicación...
echo.
echo    📍 La aplicación se abrirá automáticamente en tu navegador
echo    🌐 URL: http://localhost:8501
echo.
echo    ⚠️  Para detener la aplicación, presiona Ctrl+C
echo.
echo ════════════════════════════════════════════════════════════════
echo.

REM Iniciar Streamlit
python -m streamlit run dashboard\app_woo_v2.py

REM Si Streamlit se cierra, mostrar mensaje
echo.
echo ════════════════════════════════════════════════════════════════
echo    ⚠️  La aplicación se ha detenido
echo ════════════════════════════════════════════════════════════════
echo.
pause
