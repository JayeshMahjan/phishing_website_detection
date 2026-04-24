@echo off
REM This script will set up and run the application
REM with authentication system enabled.

echo.
echo ============================================
echo   PhishGuard AI - Quick Start
echo ============================================
echo.

REM Step 1: Check Python installation
echo [1/5] Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)
echo.

REM Step 2: Install dependencies
echo [2/5] Installing dependencies...
echo This may take a few minutes...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo.

REM Step 3: Train ML model (if not already trained)
echo [3/5] Checking if ML model exists...
if not exist "model\phishing_model.pkl" (
    echo Model not found. Training new model...
    python train_model.py
    if errorlevel 1 (
        echo ERROR: Failed to train model
        pause
        exit /b 1
    )
) else (
    echo Model already exists. Skipping training.
)
echo.

REM Step 4: Create .env file if it doesn't exist
echo [4/5] Setting up environment variables...
if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env
    echo .env file created. Please edit it to add your GROQ_API_KEY if desired.
) else (
    echo .env file already exists.
)
echo.

REM Step 5: Start the application
echo [5/5] Starting PhishGuard AI...
echo.
echo ============================================
echo   Application is starting!
echo ============================================
echo.
echo Access the app at: http://127.0.0.1:5000
echo.
echo To stop the application, press Ctrl+C
echo.
echo ============================================
echo.

python app.py

pause
