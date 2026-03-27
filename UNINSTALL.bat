@echo off
chcp 65001 >nul
color 0E
title 🗑️ Desinstalador - Analytics Pipeline

echo.
echo ════════════════════════════════════════════════════════════════
echo    🗑️  DESINSTALAR ANALYTICS PIPELINE
echo ════════════════════════════════════════════════════════════════
echo.
echo    ⚠️  ADVERTENCIA: Esta acción eliminará:
echo.
echo    • Entorno virtual (venv/)
echo    • Dependencias instaladas
echo.
echo    ℹ️  NO se eliminarán:
echo    • Bases de datos (data/)
echo    • Configuración (.env)
echo    • Backups (backups/)
echo    • Logs (logs/)
echo.
echo ════════════════════════════════════════════════════════════════
echo.

set /p CONFIRM="¿Estás seguro de que deseas desinstalar? (S/N): "
if /i not "%CONFIRM%"=="S" (
    echo.
    echo ℹ️  Desinstalación cancelada
    pause
    exit /b 0
)

echo.
echo 🗑️  Eliminando entorno virtual...

if exist venv (
    rmdir /s /q venv
    if %errorlevel% equ 0 (
        echo ✅ Entorno virtual eliminado
    ) else (
        color 0C
        echo ❌ Error al eliminar el entorno virtual
        echo ℹ️  Intenta cerrar todos los programas y ejecuta de nuevo
        pause
        exit /b 1
    )
) else (
    echo ℹ️  No se encontró el entorno virtual
)

echo.
set /p DELETE_DATA="¿Deseas también eliminar las bases de datos y configuración? (S/N): "
if /i "%DELETE_DATA%"=="S" (
    echo.
    echo ⚠️  ÚLTIMA ADVERTENCIA: Esto eliminará todos tus datos
    set /p FINAL_CONFIRM="¿Continuar? (S/N): "
    if /i "%FINAL_CONFIRM%"=="S" (
        if exist data rmdir /s /q data
        if exist logs rmdir /s /q logs
        if exist backups rmdir /s /q backups
        if exist exports rmdir /s /q exports
        if exist .env del /q .env
        echo ✅ Datos y configuración eliminados
    )
)

color 0A
echo.
echo ════════════════════════════════════════════════════════════════
echo    ✅ Desinstalación completada
echo ════════════════════════════════════════════════════════════════
echo.
echo    Para reinstalar, ejecuta: SETUP.bat
echo.
pause
