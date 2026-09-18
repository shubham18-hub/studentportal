@echo off
REM E-Cell Task Portal - Complete System Test
REM This script verifies the entire system works

setlocal enabledelayedexpansion

echo.
echo ================================================
echo  E-Cell Task Portal - System Test
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.10+
    exit /b 1
)

REM Check if the test script exists
if not exist "scripts\test-system.py" (
    echo ERROR: scripts\test-system.py not found
    exit /b 1
)

REM Run the test
echo Running comprehensive system tests...
echo.

python scripts/test-system.py

if errorlevel 1 (
    echo.
    echo ================================================
    echo  TESTS FAILED
    echo ================================================
    exit /b 1
) else (
    echo.
    echo ================================================
    echo  ALL TESTS PASSED!
    echo ================================================
    echo.
    echo Next steps:
    echo 1. Configure .env with your credentials
    echo 2. Run: docker-compose up
    echo 3. Access: http://localhost:3000
    echo.
    exit /b 0
)
