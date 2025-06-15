@echo off
echo ==========================================
echo    🚀 INICIANDO FRONTEND MEDSTUDY PRO
echo ==========================================
echo.

cd /d "C:\reumai_tts\MedStudyPro\Study1\web\frontend\frontend-lovable"

echo 📍 Carpeta: %CD%
echo.

echo 📦 Verificando dependencias...
if not exist node_modules (
    echo 📥 Instalando dependencias...
    npm install
    echo.
)

echo 🔍 Verificando que el backend esté corriendo...
curl -s http://localhost:8000/api/health >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ⚠️  IMPORTANTE: El backend no está corriendo en puerto 8000
    echo 💡 Asegúrate de ejecutar el backend primero:
    echo    cd web\backend
    echo    python -m uvicorn app.main:app --reload --port 8000
    echo.
    echo ❓ ¿Quieres continuar sin backend? (Y/N)
    set /p "choice=Respuesta: "
    if /i "%choice%" neq "Y" (
        echo Cerrando...
        pause
        exit /b 1
    )
)

echo.
echo 🌐 Iniciando servidor de desarrollo...
echo 📱 Frontend corriendo en: http://localhost:3000
echo 🔗 Backend conectado en: http://localhost:8000
echo.
echo ✨ Interfaz lista en unos segundos...
echo.

npm run dev

pause