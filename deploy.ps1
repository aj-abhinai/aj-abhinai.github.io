# Quartz Deployment Script (PowerShell)
# Usage: Run ".\deploy.ps1" or "powershell -ExecutionPolicy Bypass -File deploy.ps1"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Quartz Auto-Deployment Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$hasPrivateChanges = $false
$hasPublicChanges = $false

# Step 1: Check and push content to private repository
Write-Host "[1/4] Checking private repository (content)..." -ForegroundColor Yellow
Push-Location temp-content

git add .

# Check if there are any changes (staged or unstaged)
git diff-index --quiet HEAD --
if ($LASTEXITCODE -ne 0) {
    $hasPrivateChanges = $true
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

    Write-Host "Found changes in content repository. Committing..." -ForegroundColor Green
    git commit -m "Update content - $timestamp"

    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to commit changes" -ForegroundColor Red
        Pop-Location
        Read-Host "Press Enter to exit"
        exit 1
    }

    Write-Host "Pushing to private repository..." -ForegroundColor Green
    git push origin main

    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to push to private repository" -ForegroundColor Red
        Pop-Location
        Read-Host "Press Enter to exit"
        exit 1
    }

    Write-Host "Content pushed successfully!" -ForegroundColor Green
} else {
    Write-Host "No changes in content repository." -ForegroundColor Gray
}

Pop-Location
Write-Host ""

# Step 2: Check and commit public repository changes (config, themes, docs)
Write-Host "[2/4] Checking public repository (config/docs)..." -ForegroundColor Yellow

git add .

# Check if there are any changes in public repo (excluding temp-content)
git diff-index --quiet HEAD --
if ($LASTEXITCODE -ne 0) {
    $hasPublicChanges = $true
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

    Write-Host "Found changes in public repository. Committing..." -ForegroundColor Green
    git commit -m "Update configuration/documentation - $timestamp"

    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to commit public repository changes" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }

    Write-Host "Public repository changes committed!" -ForegroundColor Green
} else {
    Write-Host "No changes in public repository." -ForegroundColor Gray
}

Write-Host ""

# Step 3: Always create deployment trigger (even if no changes, to force rebuild)
Write-Host "[3/4] Creating deployment trigger..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
"Last deployed: $timestamp" | Out-File -FilePath ".last-deploy" -Encoding UTF8

git add .last-deploy
git diff-index --quiet HEAD -- .last-deploy
if ($LASTEXITCODE -ne 0) {
    git commit -m "Deploy: Trigger rebuild - $timestamp"

    if ($LASTEXITCODE -ne 0) {
        Write-Host "WARNING: Could not create deployment trigger commit" -ForegroundColor Yellow
    }
}

Write-Host ""

# Step 4: Push to public repository (triggers GitHub Actions)
Write-Host "[4/4] Pushing to public repository and triggering deployment..." -ForegroundColor Yellow
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

# Show summary
if ($hasPrivateChanges -or $hasPublicChanges) {
    Write-Host "Summary:" -ForegroundColor Cyan
    if ($hasPrivateChanges) {
        Write-Host "  ✓ Content changes deployed" -ForegroundColor Green
    }
    if ($hasPublicChanges) {
        Write-Host "  ✓ Configuration/documentation changes deployed" -ForegroundColor Green
    }
} else {
    Write-Host "Summary:" -ForegroundColor Cyan
    Write-Host "  ✓ No changes detected, triggered rebuild anyway" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Your site will be updated in ~2-5 minutes." -ForegroundColor Cyan
Write-Host "Check status at: https://github.com/aj-abhinai/aj-abhinai.github.io/actions" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to exit"
