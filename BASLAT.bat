@echo off
title ITU Aday Sistemi - Backend
cd /d "%~dp0backend"
echo.
echo  ==========================================
echo   ITU Aday Sistemi baslatiliyor...
echo   Tarayicida ac:  http://127.0.0.1:8000
echo   Durdurmak icin: Ctrl+C veya pencereyi kapat
echo  ==========================================
echo.
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
pause
