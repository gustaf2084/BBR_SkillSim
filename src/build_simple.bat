@echo off
chcp 65001 >nul
echo ============================================================
echo   BBR Skill Simulator - 简易打包
echo ============================================================
echo.
REM 检查 python 是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 找不到 python 命令，请确认已安装 Python 3.10+ 并加入 PATH。
    echo.
    pause
    exit /b 1
)
REM 检查 PyInstaller 是否已安装
python -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未安装 PyInstaller，正在尝试自动安装...
    python -m pip install PyInstaller
    if errorlevel 1 (
        echo [错误] PyInstaller 安装失败，请手动执行： python -m pip install PyInstaller
        echo.
        pause
        exit /b 1
    )
)
REM 检查 build_safe.spec 是否存在
if not exist build_safe.spec (
    echo [错误] 当前目录找不到 build_safe.spec，请在 src 目录下运行本脚本。
    echo.
    pause
    exit /b 1
)
echo 开始 PyInstaller 打包，请等待 3-8 分钟...
echo.
python -m PyInstaller build_safe.spec --noconfirm
if errorlevel 1 (
    echo.
    echo ============================================================
    echo   [失败] 打包过程中出现错误，请查看上方日志。
    echo ============================================================
    pause
    exit /b 1
)
echo.
echo ============================================================
echo   完成。如果上方无报错，产物在 dist\BBR_SkillSimulator.exe
echo ============================================================
pause
