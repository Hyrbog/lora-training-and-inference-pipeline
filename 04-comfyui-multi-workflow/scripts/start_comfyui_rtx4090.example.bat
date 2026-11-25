@echo off
title ComfyUI RTX 4090 Launcher (VS2022 Build Env + SageAttention)

echo [1/4] Loading Visual Studio 2022 C++ Build Environment (required for Triton / SageAttention JIT)...
if exist "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" (
    call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" amd64
) else (
    echo [WARNING] VS2022 vcvarsall.bat not found at default path. Skipping C++ compiler init.
)

echo [2/4] Activating ComfyUI Python virtual environment...
if exist "%~dp0ComfyUI\venv\Scripts\activate.bat" (
    call "%~dp0ComfyUI\venv\Scripts\activate.bat"
)

echo [3/4] Configuring dynamic PYTHONPATH...
set "RAW_BASE_DIR=%~dp0"
if "%RAW_BASE_DIR:~-1%"=="\" set "RAW_BASE_DIR=%RAW_BASE_DIR:~0,-1%"

set "PYTHONPATH=%RAW_BASE_DIR%;%RAW_BASE_DIR%\ComfyUI;%RAW_BASE_DIR%\ComfyUI\custom_nodes;%PYTHONPATH%"
set "BASE_DIR="%RAW_BASE_DIR%""
set "TMP_DIR="%RAW_BASE_DIR%\ComfyUI\temp""

echo [4/4] Starting ComfyUI with RTX 4090 optimizations...
cd /d "%~dp0ComfyUI"
python main.py --use-sage-attention --disable-smart-memory --base-directory %BASE_DIR% --auto-launch --temp-directory %TMP_DIR%

pause