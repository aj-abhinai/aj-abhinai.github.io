@echo off
REM Quartz Deployment Script - Deploys content and triggers site rebuild
REM Usage: Simply run "deploy.bat" after editing your content

setlocal enabledelayedexpansion

echo ========================================
echo Quartz Auto-Deployment Script
echo ========================================
echo.

set "hasPrivateChanges=0"
set "hasPublicChanges=0"

REM Step 0: Sync published notes from Obsidian vault
echo [0/5] Syncing published notes from Obsidian vault...
set PYTHONIOENCODING=utf-8
python sync-notes.py
echo.

REM Step 1: Check and push content to private repository
echo [1/5] Checking private repository (content)...
cd temp-content
git add .

REM Check if there are any changes
git diff-index --quiet HEAD --
if !errorlevel! neq 0 (
    set "hasPrivateChanges=1"
    echo Found changes in content repository. Committing...
    git commit -m "Update content - %date% %time%"

    if !errorlevel! neq 0 (
        echo ERROR: Failed to commit changes
        cd ..
        pause
        exit /b 1
    )

    echo Pushing to private repository...
    git push origin main

    if !errorlevel! neq 0 (
        echo ERROR: Failed to push to private repository
        cd ..
        pause
        exit /b 1
    )

    echo Content pushed successfully!
) else (
    echo No changes in content repository.
)

cd ..
echo.

REM Step 2: Check and commit public repository changes (config, themes, docs)
echo [2/5] Checking public repository (config/docs)...
git add .

REM Check if there are any changes in public repo
git diff-index --quiet HEAD --
if !errorlevel! neq 0 (
    set "hasPublicChanges=1"
    echo Found changes in public repository. Committing...
    git commit -m "Update configuration/documentation - %date% %time%"

    if !errorlevel! neq 0 (
        echo ERROR: Failed to commit public repository changes
        pause
        exit /b 1
    )

    echo Public repository changes committed!
) else (
    echo No changes in public repository.
)

echo.

REM Step 3: Always create deployment trigger (even if no changes, to force rebuild)
echo [3/5] Creating deployment trigger...
echo Last deployed: %date% %time% > .last-deploy

git add .last-deploy
git diff-index --quiet HEAD -- .last-deploy
if !errorlevel! neq 0 (
    git commit -m "Deploy: Trigger rebuild - %date% %time%"

    if !errorlevel! neq 0 (
        echo WARNING: Could not create deployment trigger commit
    )
)

echo.

REM Step 4: Push to public repository (triggers GitHub Actions)
echo [4/5] Pushing to public repository and triggering deployment...
git push origin v4

if !errorlevel! neq 0 (
    echo ERROR: Failed to push to public repository
    pause
    exit /b 1
)

echo.
echo ========================================
echo Deployment triggered successfully!
echo ========================================
echo.

REM Show summary
if !hasPrivateChanges! equ 1 (
    echo Summary:
    echo   [+] Content changes deployed
    if !hasPublicChanges! equ 1 (
        echo   [+] Configuration/documentation changes deployed
    )
) else if !hasPublicChanges! equ 1 (
    echo Summary:
    echo   [+] Configuration/documentation changes deployed
) else (
    echo Summary:
    echo   [!] No changes detected, triggered rebuild anyway
)

echo.
echo Your site will be updated in ~2-5 minutes.
echo Check status at: https://github.com/aj-abhinai/aj-abhinai.github.io/actions
echo.
pause
