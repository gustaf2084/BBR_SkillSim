@echo off
echo ============================================================
echo   BBR Skill Simulator — 简易打包
echo ============================================================
echo.
echo 开始 PyInstaller 打包，请等待 3-8 分钟...
echo.
pyinstaller build_safe.spec --noconfirm
echo.
echo ============================================================
echo   完成。如果上方无报错，产物在 dist\BBR_SkillSimulator.exe
echo ============================================================
pause
