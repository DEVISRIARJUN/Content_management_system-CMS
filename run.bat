@echo off
title NovaCMS - Enterprise Content Management Studio
echo ========================================================
echo   Starting NovaCMS Server (Django Backend + Studio UI)
echo ========================================================
cd /d "%~dp0backend"

echo.
echo [1/2] Checking database migrations...
python manage.py migrate

echo.
echo [2/2] Starting development server on http://127.0.0.1:8000
echo Access Studio UI at   : http://127.0.0.1:8000
echo Django Admin Panel at : http://127.0.0.1:8000/admin/
echo REST API Base at      : http://127.0.0.1:8000/api/
echo Default credentials   : admin / admin123
echo.
python manage.py runserver 127.0.0.1:8000
pause
