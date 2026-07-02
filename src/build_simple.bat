@echo off
chcp 65001 >nul
echo ============================================================
echo   BBR Skill Simulator - One-click Build
echo ============================================================
echo.
REM Check python availability
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install Python 3.10+ and add to PATH.
    echo.
    pause
    exit /b 1
)
REM Check PyInstaller
python -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo [INFO] PyInstaller not found. Installing...
    python -m pip install PyInstaller
    if errorlevel 1 (
        echo [ERROR] PyInstaller install failed. Run: python -m pip install PyInstaller
        echo.
        pause
        exit /b 1
    )
)
REM Verify build_safe.spec exists
if not exist build_safe.spec (
    echo [ERROR] build_safe.spec not found. Run this script from the src/ directory.
    echo.
    pause
    exit /b 1
)
echo Starting PyInstaller build (est. 3-8 min)...
echo.
python -m PyInstaller build_safe.spec --noconfirm
if errorlevel 1 (
    echo.
    echo ============================================================
    echo   [FAILED] Build errors detected. Check log above.
    echo ============================================================
    pause
    exit /b 1
)
echo.
echo ============================================================
echo   Done! Output at: dist\BBR_SkillSimulator.exe
echo ============================================================
pause
