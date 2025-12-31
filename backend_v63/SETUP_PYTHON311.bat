@echo off
echo ========================================================
echo   CONFIGURACION DE BACKEND V63 CON PYTHON 3.11
echo ========================================================
echo.

REM Verificar que Python 3.11 este instalado
echo [1/5] Verificando Python 3.11...
py -3.11 --version
if errorlevel 1 (
    echo.
    echo ERROR: Python 3.11 no esta instalado.
    echo Por favor instala Python 3.11 desde python.org
    pause
    exit /b 1
)

echo.
echo [2/5] Creando entorno virtual con Python 3.11...
cd /d "C:\Users\kevin\.gemini\antigravity\scratch\ker_solutions\backend_v63"
if exist venv_311 (
    echo Eliminando entorno virtual existente...
    rmdir /s /q venv_311
)
py -3.11 -m venv venv_311

echo.
echo [3/5] Activando entorno virtual...
call venv_311\Scripts\activate.bat

echo.
echo [4/5] Actualizando pip...
python -m pip install --upgrade pip

echo.
echo [5/5] Instalando dependencias desde requirements_mvp.txt...
pip install -r requirements_mvp.txt

echo.
echo ========================================================
echo   CONFIGURACION COMPLETADA
echo ========================================================
echo.
echo Entorno virtual creado en: venv_311
echo Python version:
python --version
echo.
echo Para iniciar el backend, ejecuta:
echo   START_V63_PY311.bat
echo.
pause
