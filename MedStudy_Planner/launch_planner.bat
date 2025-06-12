@echo off
echo MedStudy Planner Launcher
cd /d "C:\Users\Cruz Migueles\reumai_tts\MeDDocente_github\MedStudy_Planner"
echo Activando entorno virtual...
call "..\Study1\venv\Scripts\activate.bat"
echo Iniciando planificador...
python main_planner.py
pause
