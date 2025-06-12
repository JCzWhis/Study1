@echo off
title MedStudy Pro - Iniciando...

echo.
echo ┌──────────────────────────────────────────────────────────┐
echo │ 🧠 MedStudy Pro - Sistema de Estudio Médico con IA      │
echo │                                                          │
echo │ 🚀 Iniciando aplicación automáticamente...              │
echo └──────────────────────────────────────────────────────────┘
echo.

cd /d "%~dp0"

REM Verificar si Python está disponible
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no encontrado. Por favor instala Python 3.8+
    pause
    exit /b 1
)

REM Ejecutar instalador automático si es primera vez
if not exist "venv" (
    echo 📦 Primera vez - Ejecutando instalación automática...
    python install_medstudy.py
    echo.
)

REM Ejecutar launcher
echo 🚀 Iniciando MedStudy Pro...
python launch_medstudy.py

pause