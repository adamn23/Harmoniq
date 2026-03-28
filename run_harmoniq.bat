@echo off
title Harmoniq Launcher
echo.
set /p APPDIR=Paste the folder path where streamlit_app.py is located: 
if "%APPDIR%"=="" (
    echo No folder entered.
    pause
    exit /b
)
if not exist "%APPDIR%\streamlit_app.py" (
    echo streamlit_app.py was not found in:
    echo %APPDIR%
    pause
    exit /b
)
cd /d "%APPDIR%"
start "Harmoniq Streamlit" cmd /k py -m streamlit run streamlit_app.py
timeout /t 5 /nobreak >nul
start "" chrome http://localhost:8501
exit