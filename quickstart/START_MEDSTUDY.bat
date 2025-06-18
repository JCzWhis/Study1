@echo off
echo ==========================================
echo    🧠 INICIANDO MEDSTUDY PRO COMPLETO
echo ==========================================
echo.

cd /d "C:\reumai_tts\MedStudyPro\Study1"

echo 📍 Directorio base: %CD%
echo.

echo 🔍 Verificando configuración...
if not exist "web\backend\app\main.py" (
    echo ❌ Backend no encontrado. Ejecuta SETUP_COMPLETO.bat primero.
    pause
    exit /b 1
)

if not exist "web\frontend\frontend-lovable\package.json" (
    echo ❌ Frontend no encontrado. Ejecuta SETUP_COMPLETO.bat primero.
    pause
    exit /b 1
)

echo ✅ Configuración verificada
echo.

echo 🤖 Verificando Ollama...
ollama list >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Ollama no está corriendo. Iniciando...
    start "Ollama" ollama serve
    timeout 5 >nul 2>&1
)

echo 🚀 INICIANDO BACKEND...
echo 📡 Puerto: 8000
echo.
start "MedStudy Backend" cmd /k "cd /d C:\reumai_tts\MedStudyPro\Study1\web\backend && python -m uvicorn app.main:app --reload --port 8000"

echo ⏳ Esperando que el backend inicie...
timeout 8 >nul 2>&1

echo 🌐 INICIANDO FRONTEND LOVABLE...
echo 📡 Puerto: 3000
echo 🎨 Interfaz: MODERNA (React + TailwindCSS)
echo.
start "MedStudy Frontend (Lovable)" cmd /k "cd /d C:\reumai_tts\MedStudyPro\Study1\web\frontend\frontend-lovable && echo. && echo =================== && echo 🎨 FRONTEND LOVABLE MODERNO && echo =================== && echo. && npm run dev"

echo ⏳ Esperando que el frontend inicie...
timeout 10 >nul 2>&1

echo.
echo ==========================================
echo    ✅ MEDSTUDY PRO INICIADO
echo ==========================================
echo.
echo 🎉 ¡MedStudy Pro está corriendo!
echo.
echo 🌐 URLs disponibles:
echo    📱 Frontend LOVABLE:  http://localhost:3000
echo    🔧 Backend API:       http://localhost:8000
echo    📚 Docs API:          http://localhost:8000/docs
echo.
echo 🎨 NUEVA INTERFAZ LOVABLE incluye:
echo    ✨ Dashboard médico moderno
echo    🧠 Sistema de estudio con IA
echo    📊 Analíticas visuales
echo    🎯 Diseño especializado para medicina
echo.
echo 🖥️  Se han abierto 2 ventanas de terminal:
echo    🟦 Backend (puerto 8000)
echo    🟩 Frontend (puerto 3000)
echo.
echo ⚠️  IMPORTANTE:
echo    - Mantén ambas ventanas abiertas
echo    - La aplicación se abrirá automáticamente en tu navegador
echo    - Si no se abre, ve a http://localhost:3000
echo.
echo 🔄 Para detener la aplicación:
echo    - Cierra ambas ventanas de terminal
echo    - O presiona Ctrl+C en cada una
echo.

echo ⏳ Abriendo navegador en 5 segundos...
timeout 5 >nul 2>&1

start http://localhost:3000

echo.
echo 🎯 ¡Listo para estudiar medicina con IA!
echo.
pause