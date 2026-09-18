@echo off
REM E-Cell Portal Development Setup Script for Windows

echo.
echo ================================================
echo E-Cell Portal - Development Setup
echo ================================================
echo.

REM Check if .env exists
if not exist .env (
    echo Creating .env from .env.example...
    copy .env.example .env
    echo Please edit .env with your credentials
)

REM Backend setup
echo.
echo Setting up backend...
cd backend

if not exist venv (
    echo Creating Python virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

if not exist .env (
    copy .env.example .env
)

echo Installing Python dependencies...
pip install -r requirements.txt

cd ..

REM Frontend setup
echo.
echo Setting up frontend...
cd frontend

if not exist .env.local (
    copy .env.example .env.local
    echo Please edit frontend\.env.local with your credentials
)

echo Installing Node dependencies...
call npm install

cd ..

echo.
echo ✓ Setup complete!
echo.
echo Next steps:
echo 1. Edit backend\.env with MongoDB and OAuth credentials
echo 2. Edit frontend\.env.local with API URL and Google Client ID
echo 3. Run 'npm run dev:backend' in one terminal
echo 4. Run 'npm run dev:frontend' in another terminal
echo.
echo Or use Docker:
echo   docker-compose up
