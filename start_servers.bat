@echo off
REM UniPlanner Server Starter Script for Windows
REM This script starts both the Django backend and React frontend servers

echo 🚀 Starting UniPlanner Development Servers...
echo ==============================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if npm is installed
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm is not installed or not in PATH
    pause
    exit /b 1
)

echo ✅ All prerequisites found

REM Get the directory where the script is located
set SCRIPT_DIR=%~dp0
set BACKEND_DIR=%SCRIPT_DIR%backend
set FRONTEND_DIR=%SCRIPT_DIR%frontend

REM Check if directories exist
if not exist "%BACKEND_DIR%" (
    echo ❌ Backend directory not found: %BACKEND_DIR%
    pause
    exit /b 1
)

if not exist "%FRONTEND_DIR%" (
    echo ❌ Frontend directory not found: %FRONTEND_DIR%
    pause
    exit /b 1
)

REM Start backend server
echo 🐍 Starting Django Backend Server...
cd /d "%BACKEND_DIR%"

REM Check if virtual environment exists
if not exist "venv" (
    echo ⚠️  Virtual environment not found. Creating one...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies if needed
python -c "import django" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Installing Python dependencies...
    pip install django djangorestframework django-cors-headers python-decouple
)

REM Run migrations if needed
echo 📊 Checking database migrations...
python manage.py makemigrations --check >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Running database migrations...
    python manage.py makemigrations
    python manage.py migrate
)

REM Start Django server in background
echo ✅ Django server starting on http://127.0.0.1:8000
start "Django Backend" cmd /k "python manage.py runserver"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend server
echo ⚛️  Starting React Frontend Server...
cd /d "%FRONTEND_DIR%"

REM Check if node_modules exists
if not exist "node_modules" (
    echo ⚠️  Installing Node.js dependencies...
    npm install
)

REM Start React server
echo ✅ React server starting on http://localhost:3000
start "React Frontend" cmd /k "npm start"

echo.
echo 🎉 UniPlanner is now running!
echo 📱 Frontend: http://localhost:3000
echo 🔧 Backend API: http://127.0.0.1:8000
echo 👤 Admin Panel: http://127.0.0.1:8000/admin
echo.
echo Press any key to exit...
pause >nul

