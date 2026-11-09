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
echo Enter the IPv4 address of the server computer.
set /p "SERVERIP=Server IPv4: "
if "%SERVERIP%"=="" goto missing_address
%PY% client.py http://%SERVERIP%:8000
pause
exit /b 0
:missing_address
echo Address is empty.
pause
exit /b 1
:no_python
echo Python 3 was not found. Install Python 3 and enable PATH.
pause
exit /b 1
:install_failed
echo Package installation failed. Check internet and Python version.
pause
exit /b 1
