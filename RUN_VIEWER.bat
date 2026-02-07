@echo off
echo Starting FITS Viewer...
echo.

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Run the application
python main.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo An error occurred. Press any key to exit...
    pause >nul
)
