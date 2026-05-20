@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ======================================
echo   mLRS Configurator - Upload to GitHub
echo ======================================
echo.

REM Check git status
git status --short >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Git not found or not initialized.
    echo Make sure Git is installed and added to PATH.
    pause
    exit /b 1
)

REM Check if there are changes to commit
git diff --quiet
set CHANGES=%errorlevel%

REM If no changes, check both staged and unstaged
if %CHANGES% equ 0 (
    git diff --cached --quiet
    set STAGED=%errorlevel%
) else (
    set STAGED=1
)

if %CHANGES% equ 0 (
    if %STAGED% equ 0 (
        echo [OK] No changes to commit.
    ) else (
        echo [OK] No changes to commit.
    )
) else (
    echo [INFO] Changes detected. Proceeding with commit...
)

echo.
echo Staging all files...
git add -A

echo.
echo Current staged files:
git diff --cached --stat

echo.
REM Prompt for commit message
set /p MSG="Enter commit message (or press Enter for default): "
if "%MSG%"=="" set MSG=Update: auto-commit from upload script

echo.
echo Committing with message: "%MSG%"
git commit -m "%MSG%"

echo.
echo Pushing to origin/experiment...
git push origin experiment

echo.
if %errorlevel% equ 0 (
    echo [SUCCESS] Upload complete!
    echo.
    echo Commit pushed to:
    echo   - Branch: experiment
    echo   - Repo:   https://github.com/mountianVn/mLRS-Configurator
) else (
    echo [ERROR] Push failed! Check your credentials or network.
)

echo.
pause
