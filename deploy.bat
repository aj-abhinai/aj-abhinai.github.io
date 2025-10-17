@echo off
REM Quartz Deployment Script - Deploys content and triggers site rebuild
REM Usage: Simply run "deploy.bat" after editing your content

echo ========================================
echo Quartz Auto-Deployment Script
echo ========================================
echo.

REM Step 1: Push content to private repository
echo [1/3] Pushing content to private repository...
cd temp-content
git add .
git diff --quiet && git diff --staged --quiet
if %errorlevel% equ 0 (
    echo No changes in content repository.
) else (
    git commit -m "Update content - %date% %time%"
    git push origin main
    if %errorlevel% neq 0 (
        echo ERROR: Failed to push to private repository
        cd ..
        pause
        exit /b 1
    )
    echo Content pushed successfully!
)
cd ..
echo.

REM Step 2: Update timestamp in public repository to trigger deployment
echo [2/3] Triggering deployment via public repository...
echo Last deployed: %date% %time% > .last-deploy
git add .last-deploy
git commit -m "Deploy: Trigger rebuild - %date% %time%"
if %errorlevel% neq 0 (
    echo No changes to deploy or commit failed.
    pause
    exit /b 1
)

REM Step 3: Push to public repository (triggers GitHub Actions)
git push origin v4
if %errorlevel% neq 0 (
    echo ERROR: Failed to push to public repository
    pause
    exit /b 1
)
echo.

echo ========================================
echo Deployment triggered successfully!
echo ========================================
echo.
echo Your site will be updated in ~2-5 minutes.
echo Check status at: https://github.com/aj-abhinai/aj-abhinai.github.io/actions
echo.
pause
