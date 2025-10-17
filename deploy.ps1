# Quartz Deployment Script (PowerShell)
# Usage: Run ".\deploy.ps1" or "powershell -ExecutionPolicy Bypass -File deploy.ps1"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Quartz Auto-Deployment Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Push content to private repository
Write-Host "[1/3] Pushing content to private repository..." -ForegroundColor Yellow
Push-Location temp-content

git add .
$contentChanges = git diff --quiet --exit-code; $LASTEXITCODE
$stagedChanges = git diff --cached --quiet --exit-code; $LASTEXITCODE

if ($contentChanges -eq 0 -and $stagedChanges -eq 0) {
    Write-Host "No changes in content repository." -ForegroundColor Gray
} else {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    git commit -m "Update content - $timestamp"

    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to commit changes" -ForegroundColor Red
        Pop-Location
        Read-Host "Press Enter to exit"
        exit 1
    }

    git push origin main

    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to push to private repository" -ForegroundColor Red
        Pop-Location
        Read-Host "Press Enter to exit"
        exit 1
    }

    Write-Host "Content pushed successfully!" -ForegroundColor Green
}

Pop-Location
Write-Host ""

# Step 2: Update timestamp in public repository to trigger deployment
Write-Host "[2/3] Triggering deployment via public repository..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
"Last deployed: $timestamp" | Out-File -FilePath ".last-deploy" -Encoding UTF8

git add .last-deploy
git commit -m "Deploy: Trigger rebuild - $timestamp"

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to commit deployment trigger" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Step 3: Push to public repository (triggers GitHub Actions)
git push origin v4

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to push to public repository" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Deployment triggered successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your site will be updated in ~2-5 minutes." -ForegroundColor Cyan
Write-Host "Check status at: https://github.com/aj-abhinai/aj-abhinai.github.io/actions" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to exit"
