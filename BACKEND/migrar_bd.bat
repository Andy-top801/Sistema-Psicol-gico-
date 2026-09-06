@echo off
echo ========================================================
echo Ejecutando Migraciones Multi-Tenant para SIGEPSI...
echo ========================================================
echo.

call venv\Scripts\activate.bat
python manage.py makemigrations
python manage.py migrate_schemas --shared

echo.
echo ========================================================
echo Migraciones finalizadas. Revisa pgAdmin para confirmar.
echo ========================================================
pause
