@echo off

REM Define the name of the virtual environment
set VENV_DIR=venv

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install it and try again.
    exit /b 1
)

REM Create a virtual environment
echo Creating virtual environment...
python -m venv %VENV_DIR%

REM Activate the virtual environment
echo Activating virtual environment...
call %VENV_DIR%\Scripts\activate

REM Install required libraries
echo Installing libraries...
pip install pandas matplotlib beautifulsoup4 selenium lxml openpyxl

REM Freeze the installed libraries into requirements.txt
echo Freezing dependencies into requirements.txt...
pip freeze > requirements.txt

REM Deactivate the virtual environment
echo Deactivating virtual environment...
deactivate

echo Setup complete! Virtual environment is in the '%VENV_DIR%' folder.
echo Dependencies are listed in 'requirements.txt'.
