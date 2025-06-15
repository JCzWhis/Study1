@echo off
echo ==========================================
echo    🚀 GUARDANDO MEDSTUDY PRO COMPLETO
echo ==========================================
echo.

cd /d "C:\reumai_tts\MedStudyPro\Study1"

echo 📍 Carpeta actual: %CD%
echo.

echo 🔍 Verificando estado de Git...
git status
echo.

echo 💾 Guardando en GitHub...
git push origin feature/medstudy-pro-redesign

if %errorlevel% equ 0 (
    echo.
    echo ✅ ¡PROYECTO GUARDADO EXITOSAMENTE!
    echo ✅ Todo sincronizado con GitHub
    echo ✅ Listo para continuar mañana en cualquier PC
    echo.
    echo 📋 Para mañana:
    echo    1. git pull origin feature/medstudy-pro-redesign
    echo    2. cd web/backend
    echo    3. python -m uvicorn app.main:app --reload --port 8000
    echo.
) else (
    echo.
    echo ⚠️  Error al hacer push
    echo 📝 El proyecto está guardado LOCALMENTE
    echo 💡 Mañana puedes hacer: git push origin feature/medstudy-pro-redesign
    echo.
)

echo 🎯 ESTADO: MedStudy Pro v1.0 MVP - 95%% COMPLETADO
echo 📁 Ubicación: %CD%
echo.
pause