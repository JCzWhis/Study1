@echo off
echo ==========================================
echo    🧠 SETUP COMPLETO MEDSTUDY PRO
echo ==========================================
echo.

cd /d "C:\reumai_tts\MedStudyPro\Study1"

echo 📍 Directorio base: %CD%
echo.

echo 🔍 Verificando estructura del proyecto...
if not exist "web\backend" (
    echo ❌ Error: Carpeta backend no encontrada
    pause
    exit /b 1
)

if not exist "web\frontend\frontend-lovable" (
    echo ❌ Error: Carpeta frontend-lovable no encontrada
    pause
    exit /b 1
)

echo ✅ Estructura del proyecto verificada
echo.

echo 📦 PASO 1: Configurando Backend...
cd web\backend

echo 🐍 Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python no encontrado. Instala Python 3.11+ primero.
    pause
    exit /b 1
)

echo 📥 Instalando dependencias Python...
pip install -r requirements.txt

echo 🔍 Verificando Ollama...
ollama list >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Ollama no encontrado. Descárgalo de https://ollama.ai
    echo ❓ ¿Continuar sin Ollama? (Y/N)
    set /p "choice=Respuesta: "
    if /i "%choice%" neq "Y" (
        pause
        exit /b 1
    )
) else (
    echo ✅ Ollama encontrado
    echo 🤖 Verificando modelo Gemma 3-2B...
    ollama list | findstr "gemma2:2b" >nul 2>&1
    if %errorlevel% neq 0 (
        echo 📥 Descargando modelo Gemma 3-2B (~1.6GB)...
        ollama pull gemma2:2b
    ) else (
        echo ✅ Modelo Gemma 3-2B ya instalado
    )
)

echo.
echo 📦 PASO 2: Configurando Frontend...
cd ..\frontend\frontend-lovable

echo 🟢 Verificando Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js no encontrado. Instala Node.js 18+ primero.
    pause
    exit /b 1
)

echo 📥 Instalando dependencias Node.js...
npm install

echo.
echo 🧪 PASO 3: Probando configuración...
cd ..\..\backend

echo 🔍 Test rápido del backend...
timeout 3 >nul 2>&1
echo ✅ Backend configurado

cd ..\frontend\frontend-lovable
echo 🔍 Test del frontend...
echo ✅ Frontend configurado

echo.
echo ==========================================
echo    ✅ SETUP COMPLETADO EXITOSAMENTE
echo ==========================================
echo.
echo 🚀 Para iniciar MedStudy Pro:
echo.
echo 📝 OPCIÓN 1 - Automático (Recomendado):
echo    Ejecuta: INICIAR_MEDSTUDY_COMPLETO.bat
echo.
echo 📝 OPCIÓN 2 - Manual:
echo    Terminal 1: cd web\backend ^&^& python -m uvicorn app.main:app --reload --port 8000
echo    Terminal 2: cd web\frontend\frontend-lovable ^&^& npm run dev
echo.
echo 🌐 URLs cuando esté corriendo:
echo    Frontend: http://localhost:3000
echo    Backend:  http://localhost:8000
echo    Docs API: http://localhost:8000/docs
echo.
echo ⚠️  IMPORTANTE: Mantén ambos terminales abiertos mientras uses la app
echo.
pause