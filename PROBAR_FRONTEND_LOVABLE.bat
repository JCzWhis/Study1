@echo off
echo ==========================================
echo    🎨 PROBANDO FRONTEND LOVABLE
echo ==========================================
echo.

cd /d "C:\reumai_tts\MedStudyPro\Study1\web\frontend\frontend-lovable"

echo 📍 Carpeta: %CD%
echo.

echo 🔍 Verificando configuración...
if not exist "package.json" (
    echo ❌ Frontend Lovable no encontrado
    pause
    exit /b 1
)

echo ✅ Frontend Lovable encontrado
echo.

echo 📦 Verificando dependencias...
if not exist "node_modules" (
    echo 📥 Instalando dependencias...
    npm install
)

echo.
echo 🌐 INICIANDO SOLO EL FRONTEND LOVABLE...
echo.
echo 🎯 URLs importantes:
echo    🟢 Frontend Lovable: http://localhost:3000
echo    🔵 Backend API: http://localhost:8000 (debe estar corriendo)
echo.
echo ✨ Características del Frontend Lovable:
echo    • Diseño moderno con TailwindCSS
echo    • Interfaz médica especializada  
echo    • Dashboard interactivo
echo    • Componentes React optimizados
echo.
echo ⏳ Iniciando en 3 segundos...
timeout 3 >nul 2>&1

echo 🚀 Ejecutando npm run dev...
echo.

start "Browser Lovable" http://localhost:3000

npm run dev

pause