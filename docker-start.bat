@echo off
REM Docker Quick Start Script for Windows

echo ============================================
echo   Analytics Pipeline - Docker Quick Start
echo ============================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not running. Please start Docker Desktop first.
    echo Visit: https://docs.docker.com/desktop/install/windows-install/
    pause
    exit /b 1
)

echo [OK] Docker is running
echo.

REM Check if .env file exists
if not exist .env (
    echo WARNING: .env file not found. Creating from .env.example...
    copy .env.example .env >nul
    echo.
    echo Please edit .env file with your credentials before continuing.
    echo.
    pause
)

echo Building Docker image...
docker-compose build
if errorlevel 1 (
    echo ERROR: Failed to build Docker image
    pause
    exit /b 1
)

echo [OK] Docker image built successfully
echo.

echo Starting containers...
docker-compose up -d
if errorlevel 1 (
    echo ERROR: Failed to start containers
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Analytics Pipeline started successfully!
echo ============================================
echo.
echo Dashboard: http://localhost:8501
echo.
echo Useful commands:
echo   - View logs:        docker-compose logs -f
echo   - Stop containers:  docker-compose down
echo   - Restart:          docker-compose restart
echo.
pause
