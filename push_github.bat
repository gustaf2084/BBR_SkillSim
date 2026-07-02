@echo off
REM ============================================================
REM  BBR_SkillSim - one-click upload to GitHub
REM  Repo: https://github.com/gustaf2084/BBR_SkillSim
REM
REM  Usage:
REM    push_github.bat                  -> commit message "update <date> <time>"
REM    push_github.bat fix reverse bug  -> custom commit message
REM
REM  Notes:
REM    - Never force-pushes. If the remote is ahead, it tells you
REM      to run: git pull --rebase origin main
REM    - Pushing triggers CI (test.yml). Tag pushes (v*) trigger
REM      the EXE build workflow separately.
REM ============================================================
setlocal
cd /d "%~dp0"

where git >nul 2>nul
if errorlevel 1 (
    echo [ERROR] git not found in PATH.
    pause
    exit /b 1
)

git rev-parse --git-dir >nul 2>nul
if errorlevel 1 (
    echo [ERROR] not a git repository: %cd%
    pause
    exit /b 1
)

REM ensure remote "origin" points at the repo
git remote get-url origin >nul 2>nul
if errorlevel 1 (
    git remote add origin https://github.com/gustaf2084/BBR_SkillSim.git
) else (
    git remote set-url origin https://github.com/gustaf2084/BBR_SkillSim.git
)

for /f "delims=" %%b in ('git branch --show-current') do set "BRANCH=%%b"
if not defined BRANCH (
    echo [ERROR] cannot determine current branch.
    pause
    exit /b 1
)

set "MSG=%*"
if not defined MSG set "MSG=update %date% %time%"

echo [1/3] staging changes...
git add -A

git diff --cached --quiet
if errorlevel 1 (
    echo [2/3] committing: %MSG%
    git commit -m "%MSG%"
    if errorlevel 1 (
        echo [ERROR] commit failed.
        pause
        exit /b 1
    )
) else (
    echo [2/3] nothing new to commit, pushing existing commits...
)

echo [3/3] pushing to origin/%BRANCH% ...
git push -u origin %BRANCH%
if errorlevel 1 (
    echo.
    echo [ERROR] push rejected or failed.
    echo   If the remote has newer commits, run:
    echo       git pull --rebase origin %BRANCH%
    echo   resolve conflicts if any, then run this script again.
    pause
    exit /b 1
)

echo.
echo [OK] pushed to https://github.com/gustaf2084/BBR_SkillSim  (branch: %BRANCH%)
pause
