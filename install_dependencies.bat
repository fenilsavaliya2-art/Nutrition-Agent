@echo off
title Installing Nutrition AI Dependencies...
color 0B

echo.
echo  ============================================================
echo    Installing Nutrition Agentic AI — Dependencies
echo  ============================================================
echo.

cd /d "%~dp0nutrition_ai"

echo Checking Python...
python --version
echo.

echo Creating virtual environment...
if not exist "venv" python -m venv venv

echo Activating environment and installing packages...
call venv\Scripts\activate.bat
pip install flask==3.0.3 flask-cors==4.0.1 requests==2.32.3 python-dotenv==1.0.1 markdown==3.6 ibm-watsonx-ai==1.1.2

echo.
echo  ============================================================
echo    Installation complete!
echo    Run: run_nutrition_ai.bat  to start the application
echo  ============================================================
echo.
pause
