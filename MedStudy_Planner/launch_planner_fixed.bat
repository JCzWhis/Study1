@echo off
echo 🧠 MedStudy Planner - Launcher Automático
echo =========================================

cd /d "C:\Users\Cruz Migueles\reumai_tts\MeDDocente_github\MedStudy_Planner"

echo 📁 Activando entorno virtual...
call "..\Study1\venv\Scripts\activate.bat"

echo 🔍 Verificando dependencias...
python -c "import customtkinter; print('✅ CustomTkinter OK')" 2>nul || (
    echo ❌ CustomTkinter no encontrado
    echo 💡 Instalando CustomTkinter...
    pip install customtkinter
)

echo 🚀 Iniciando MedStudy Planner...
python main_planner.py

echo.
echo 👋 Presiona cualquier tecla para cerrar...
pause >nul
