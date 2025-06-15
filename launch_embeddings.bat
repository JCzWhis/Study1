@echo off
title Medical Embeddings System - GTX 1080Ti Optimized

echo ============================================================
echo MEDICAL EMBEDDINGS SYSTEM LAUNCHER
echo GTX 1080Ti + CUDA 12.2 Optimized
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    echo Please install Python 3.8+ or add it to your PATH
    pause
    exit /b 1
)

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Check if main script exists
if not exist "medical_embeddings_system.py" (
    echo ERROR: medical_embeddings_system.py not found
    echo Please ensure you're in the correct directory
    pause
    exit /b 1
)

REM Check if documents directory exists
if not exist "Material para embeddings" (
    echo WARNING: 'Material para embeddings' directory not found
    echo Creating directory...
    mkdir "Material para embeddings"
    echo.
    echo Please add your medical documents to this folder:
    echo %CD%\Material para embeddings\
    echo.
    echo Supported formats: PDF, MD, DOCX, HTML, CSV, TXT
    echo.
    pause
)

REM Run installation check
echo Checking installation...
python -c "import torch, transformers, sentence_transformers, faiss" >nul 2>&1
if errorlevel 1 (
    echo Dependencies not installed. Running installation...
    python install_medical_embeddings.py
    if errorlevel 1 (
        echo Installation failed. Please check the error messages above.
        pause
        exit /b 1
    )
)

echo.
echo Starting Medical Embeddings System...
echo This process will:
echo   1. Process all documents in 'Material para embeddings'
echo   2. Generate high-quality embeddings using E5-large + CLIP-large
echo   3. Create GPU-optimized FAISS index
echo   4. Save results to 'medical_knowledge_base'
echo.
echo Estimated time: 10-20 minutes (depending on document collection)
echo Press Ctrl+C to stop gracefully at any time.
echo.
pause

REM Run the embeddings system
python launch_medical_embeddings.py

if errorlevel 1 (
    echo.
    echo ============================================================
    echo PROCESS FAILED
    echo ============================================================
    echo Check the error messages above for troubleshooting.
    echo Common issues:
    echo   - Insufficient GPU memory (need 11GB VRAM)
    echo   - CUDA driver issues
    echo   - Corrupted document files
    echo   - Insufficient disk space
    echo.
    echo For detailed logs, check: medical_knowledge_base\logs\
) else (
    echo.
    echo ============================================================
    echo SUCCESS! MEDICAL EMBEDDINGS GENERATED
    echo ============================================================
    echo Your medical knowledge base is ready!
    echo Location: %CD%\medical_knowledge_base\
    echo.
    echo Key files generated:
    echo   - text_e5_large.h5 (text embeddings)
    echo   - faiss_gpu_index.bin (search index)
    echo   - metadata.parquet (document metadata)
    echo.
    echo You can now use this for semantic search of medical documents.
)

echo.
pause