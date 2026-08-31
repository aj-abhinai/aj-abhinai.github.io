@echo off
REM Quartz Deployment Script - Syncs published notes and pushes to content branch
REM Usage: Run "deploy.bat" from the repo root after editing your notes in Obsidian
setlocal enabledelayedexpansion

echo ========================================
echo Quartz Auto-Deployment Script
echo ========================================
echo.

REM Verify we are on the content branch
for /f "delims=" %%b in ('git rev-parse --abbrev-ref HEAD') do set "currentBranch=%%b"
if not "!currentBranch!"=="content" (
    echo ERROR: You are on branch "!currentBranch!" but this script must run on "content".
    pause
    exit /b 1
)

REM Step 1: Sync published notes from Obsidian vault
echo [1/3] Syncing published notes from Obsidian vault...
set PYTHONIOENCODING=utf-8
python sync-notes.py
if !errorlevel! neq 0 (
    echo ERROR: Failed to sync notes from vault
    pause
    exit /b 1
)
echo.

REM Step 2: Commit synced notes (only content/ changes, leaves other work untouched)
echo [2/3] Committing synced notes...
git add content
git diff-index --quiet HEAD -- content
if !errorlevel! neq 0 (
    git commit -m "content: sync published notes" -- content
    if !errorlevel! neq 0 (
        echo ERROR: Failed to commit content changes
        pause
        exit /b 1
    )
    echo Content committed!
) else (
    echo No content changes detected.
)
echo.

REM Step 3: Push to content branch (triggers site rebuild)
echo [3/3] Pushing to content branch...
git push origin content
if !errorlevel! neq 0 (
    echo ERROR: Failed to push to content branch
    pause
    exit /b 1
)

echo.
echo ========================================
echo Deployment triggered successfully!
echo ========================================
echo.
echo Your site will be updated once the build finishes.
echo Check status at: https://github.com/aj-abhinai/aj-abhinai.github.io/actions
echo.
pause
