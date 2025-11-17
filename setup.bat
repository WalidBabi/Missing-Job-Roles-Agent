@echo off
REM Setup script for Windows - Missing Job Roles AI Agent

echo ========================================
echo Missing Job Roles AI Agent Setup
echo ========================================
echo.

REM Check Python version
echo Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.10 or higher.
    pause
    exit /b 1
)
echo.

REM Create virtual environment
echo Creating virtual environment...
if exist venv (
    echo Virtual environment already exists. Skipping...
) else (
    python -m venv venv
    echo Virtual environment created.
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Install dependencies
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)
echo Dependencies installed successfully.
echo.

REM Check for .env file
echo Checking environment configuration...
if exist .env (
    echo .env file found.
) else (
    echo WARNING: .env file not found!
    echo Please copy .env.example to .env and configure your settings.
    echo.
    echo Run this command:
    echo   copy .env.example .env
    echo.
    echo Then edit .env with your database credentials and API keys.
    pause
)
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Configure your .env file (if not done)
echo 2. Setup MySQL database
echo 3. Run: python manage.py migrate
echo 4. Generate sample data: python manage.py generate_sample_data
echo 5. Start server: python manage.py runserver
echo.
echo See README.md for detailed instructions.
echo.
pause

