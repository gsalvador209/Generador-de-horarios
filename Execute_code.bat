@echo off

REM Define the name of the virtual environment directory
set VENV_DIR=venv

REM Define the name of the Python script to run
set SCRIPT_NAME=demo.py

REM Check if the virtual environment exists
if not exist %VENV_DIR% (
    echo Virtual environment not found. Please create it first.
    pause
    exit /b 1
)

REM Activate the virtual environment
call %VENV_DIR%\Scripts\activate

REM Check if the Python script exists
if not exist %SCRIPT_NAME% (
    echo Python script "%SCRIPT_NAME%" not found in the current directory.
    deactivate
    pause
    exit /b 1
)

REM Run the Python script
python %SCRIPT_NAME%

REM Deactivate the virtual environment
deactivate

echo Script execution complete!
pause
