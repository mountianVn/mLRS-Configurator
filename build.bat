@echo off
chcp 65001 >nul
title Build MAVLink CLI Configurator EXE

echo ========================================
echo  Build MAVLink CLI Configurator EXE
echo ========================================
echo.

REM Get script directory
set SCRIPT_DIR=%~dp0

REM Check if virtual environment exists
if exist "%SCRIPT_DIR%.venv\Scripts\python.exe" (
    set PYTHON="%SCRIPT_DIR%.venv\Scripts\python.exe"
    set PYINSTALLER="%SCRIPT_DIR%.venv\Scripts\pyinstaller.exe"
) else (
    set PYTHON=python
    set PYINSTALLER=pyinstaller
)

REM Install PyInstaller if not present
echo [1/4] Checking PyInstaller...
%PYTHON% -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo Installing PyInstaller...
    %PYTHON% -m pip install pyinstaller -q
)

REM Clean previous builds
echo [2/4] Cleaning previous builds...
if exist "%SCRIPT_DIR%dist" rmdir /s /q "%SCRIPT_DIR%dist"
if exist "%SCRIPT_DIR%build" rmdir /s /q "%SCRIPT_DIR%build"
if exist "%SCRIPT_DIR%main.spec" del /q "%SCRIPT_DIR%main.spec"

REM Build executable
echo [3/4] Building executable...
%PYTHON% -m PyInstaller ^
    --name="MAVLink_CLI_Configurator" ^
    --windowed ^
    --onefile ^
    --console ^
    --icon=NONE ^
    --add-data="%SCRIPT_DIR%ui;ui" ^
    --hidden-import=PySide6 ^
    --hidden-import=PySide6.QtCore ^
    --hidden-import=PySide6.QtGui ^
    --hidden-import=PySide6.QtWidgets ^
    --hidden-import=pyserial ^
    --hidden-import=pymavlink ^
    --collect-all=PySide6 ^
    --noconfirm ^
    "%SCRIPT_DIR%main.py"

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

REM Rename output to include version
echo [4/4] Finalizing...
if exist "%SCRIPT_DIR%dist\main.exe" (
    move /y "%SCRIPT_DIR%dist\main.exe" "%SCRIPT_DIR%dist\MAVLink_CLI_Configurator.exe" >nul
)

echo.
echo ========================================
echo  Build completed successfully!
echo  Output: %SCRIPT_DIR%dist\MAVLink_CLI_Configurator.exe
echo ========================================
echo.
pause
