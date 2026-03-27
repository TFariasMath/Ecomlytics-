@echo off
REM ============================================
REM Demo Data Reset Script
REM ============================================
REM Regenerates all demo data for fresh presentations

echo.
echo =========================================
echo  Analytics Pipeline - Demo Data Reset
echo =========================================
echo.
echo This script will:
echo  - Delete current databases
echo  - Generate fresh demo data (2025)
echo  - Restart the dashboard
echo.

pause

echo.
echo [1/3] Deleting old databases...
del /Q "data\woocommerce.db" 2>nul
del /Q "data\analytics.db" 2>nul
del /Q "data\facebook.db" 2>nul
del /Q "data\monitoring.db" 2>nul
echo Done!

echo.
echo [2/3] Generating new demo data...
echo This may take 1-2 minutes...
python scripts\generate_demo_data.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Demo data generation failed!
    pause
    exit /b 1
)

echo.
echo [3/3] Demo data reset complete!
echo.
echo =========================================
echo  Next Steps:
echo =========================================
echo 1. Run: LAUNCH.bat
echo 2. Open: http://localhost:8501
echo 3. Demo is ready for presentation!
echo.
echo TIP: You can reset demo data anytime
echo      by running this script again
echo =========================================
echo.

pause
