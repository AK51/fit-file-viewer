@echo off
echo Starting FITS Viewer with test file...
echo.

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Run the application with the test file
python main.py "E:\Seestar\MyWorks\M 31\Stacked_932_M 31_10.0s_IRCUT_20241230-002547.fit"

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo An error occurred. Press any key to exit...
    pause >nul
)
