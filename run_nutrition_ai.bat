@echo off
title Nutrition Agentic AI — IBM Granite LLM
color 0A

echo.
echo  ============================================================
echo    ####   Nutrition Agentic AI   ####
echo    Powered by IBM Granite LLM
echo    Agentic AI with Ethics, Guardrails and Medical Safety
echo  ============================================================
echo.

:: ── Step 1: Check Python ──────────────────────────────────────
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  ERROR: Python not found!
    echo  Please install Python 3.9+ from https://www.python.org/downloads/
    echo  Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)
python --version
echo  Python OK.
echo.

:: ── Step 2: Navigate to app directory ────────────────────────
echo [2/5] Setting up application directory...
cd /d "%~dp0nutrition_ai"
if %errorlevel% neq 0 (
    echo  ERROR: Could not find nutrition_ai folder.
    echo  Make sure this .bat file is in the same directory as nutrition_ai/
    pause
    exit /b 1
)
echo  Directory: %CD%
echo.

:: ── Step 3: Create virtual environment ───────────────────────
echo [3/5] Setting up Python virtual environment...
if not exist "venv" (
    echo  Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo  ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo  Virtual environment created.
) else (
    echo  Virtual environment already exists.
)
echo.

:: ── Step 4: Install dependencies ─────────────────────────────
echo [4/5] Installing required packages...
call venv\Scripts\activate.bat
pip install -r requirements.txt --quiet --disable-pip-version-check
if %errorlevel% neq 0 (
    echo  ERROR: Failed to install dependencies.
    echo  Try running: pip install -r requirements.txt
    pause
    exit /b 1
)
echo  All packages installed successfully.
echo.

:: ── Step 5: Copy .env if not exists ──────────────────────────
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo  NOTE: .env file created from template.
        echo  To use IBM Granite LLM, edit nutrition_ai\.env and add your:
        echo    - WATSONX_API_KEY
        echo    - WATSONX_PROJECT_ID
        echo  App will run in DEMO mode until credentials are added.
        echo.
    )
)

:: ── Launch Application ─────────────────────────────────────────
echo [5/5] Starting Nutrition Agentic AI server...
echo.
echo  ============================================================
echo    Server starting at: http://localhost:5000
echo    Press Ctrl+C to stop the server
echo  ============================================================
echo.

:: Open browser after short delay
start /b cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:5000"

:: Start the Flask app
python app.py

echo.
echo  Server stopped.
pause
