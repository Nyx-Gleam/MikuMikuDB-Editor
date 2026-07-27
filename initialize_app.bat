@echo off
cd /d "%~dp0"

call .\venv\Scripts\activate.bat
py main.py

echo.
echo La aplicacion ha finalizado.
pause