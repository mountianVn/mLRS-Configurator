@echo off
echo ====================================
echo   BUILD mLRS CONFIGURATOR - FULL
echo ====================================
echo.

REM Xoa build cu
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__
if exist mainVersion0.4.spec del mainVersion0.4.spec

echo.
echo Dang build production...
echo.

pyinstaller ^
--noconfirm ^
--clean ^
--onefile ^
--windowed ^
--name "mLRS_Config_v0.4" ^
--icon=mLRS.ico ^
--add-data "mLRS.ico;." ^
--hidden-import=customtkinter ^
--hidden-import=serial ^
--hidden-import=serial.tools.list_ports ^
--collect-all customtkinter ^
--collect-all serial ^
mainVersion0.4_new.py

echo.
echo ====================================
echo   BUILD HOAN TAT
echo ====================================
echo.
pause