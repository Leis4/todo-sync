@echo off
cd /d "%~dp0"
set "PY=python"
where py >nul 2>&1
if not errorlevel 1 set "PY=py -3"
%PY% --version >nul 2>&1
if errorlevel 1 goto no_python
%PY% -c "import fastapi, uvicorn, requests, PySide6" >nul 2>&1
if not errorlevel 1 goto ready
echo Installing Python packages. Internet connection is needed.
%PY% -m pip install -r requirements.txt
if errorlevel 1 goto install_failed
:ready
echo Starting server and two windows...
start "ToDo SERVER" cmd /k %PY% -m uvicorn server:app --host 0.0.0.0 --port 8000
timeout /t 3 /nobreak >nul
start "ToDo WINDOW 1" %PY% client.py
start "ToDo WINDOW 2" %PY% client.py
echo Done. Keep the server window open.
echo Close old server windows before starting this project.
pause
exit /b 0
:no_python
echo Python 3 was not found. Install Python 3 and enable PATH.
pause
exit /b 1
:install_failed
echo Package installation failed. Check internet and Python version.
pause
exit /b 1
