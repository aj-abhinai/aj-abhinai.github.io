# Quartz Deployment Guide - Private Content Setup

## Quick Start

After editing your content, simply run:

**Command Prompt:**
```cmd
deploy.bat
```

**PowerShell:**
```powershell
.\deploy.ps1
```

That's it! Your site will be updated in 2-5 minutes.

---

## What Happens When You Deploy?

The script automatically handles everything:

1. **Step 1:** Checks for content changes in `temp-content/` (private repo)
   - If changes found, commits and pushes to private repository
   - Commit message: `"Update content - [timestamp]"`

2. **Step 2:** Checks for config/documentation changes in main directory (public repo)
   - If changes found, commits them
   - Commit message: `"Update configuration/documentation - [timestamp]"`

3. **Step 3:** Creates deployment trigger
   - Updates `.last-deploy` timestamp file
   - Ensures GitHub Actions will run even if no changes detected

4. **Step 4:** Pushes to public repository
   - Triggers GitHub Actions workflow automatically
   - Workflow fetches latest from both repos, builds site, and deploys to GitHub Pages

---

## Two Ways to Deploy

### Option 1: Command Prompt (Windows)

```cmd
cd "path\to\your\quartz\directory"
deploy.bat
```

### Option 2: PowerShell (Recommended)

```powershell
cd "path\to\your\quartz\directory"
.\deploy.ps1
```

**Note:** If PowerShell blocks execution, run this first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
```

---

## Daily Workflow

### Scenario 1: Edit Content (Markdown Notes)

1. **Edit** your markdown files in the `content/` directory
   - Use Obsidian, VS Code, or any text editor
2. **Run deployment script**
3. **Done!** The script handles everything

### Scenario 2: Edit Configuration/Theme/Docs

1. **Edit** Quartz config files, themes, or documentation
   - Files like `quartz.config.ts`, `DEPLOYMENT_GUIDE.md`, etc.
2. **Run deployment script**
3. **Done!** The script handles everything

### Scenario 3: Edit Both Content AND Configuration

1. **Edit** whatever you want in any location
2. **Run deployment script once**
3. **Done!** The script detects and deploys all changes

### Running the Deployment:

**Command Prompt:**
```cmd
deploy.bat
```

**PowerShell:**
```powershell
.\deploy.ps1
```

**Wait** 2-5 minutes, then check your site: `https://YOUR_USERNAME.github.io`

---

## Troubleshooting

### Script says "No changes detected"

This is normal if you haven't edited any files since last deployment. The script will still trigger a rebuild.

### Script fails with "ERROR: Failed to commit changes"

This error should not occur with the updated scripts. If it does:
- Make sure you're in the correct directory
- Check that git is installed and configured
- Verify you have internet connection

### Script fails with "Permission denied" or "Authentication failed"

- Check your internet connection
- Verify your GitHub credentials are set up correctly
- Make sure you have push access to both repositories

### Want to check deployment status?

Go to: `https://github.com/YOUR_USERNAME/YOUR_USERNAME.github.io/actions`

---

## Important: Don't Use `npx quartz sync`

**❌ OLD WAY (Don't use):**
```cmd
npx quartz sync   # This pushes content to public repo!
```

**✅ NEW WAY (Use these scripts):**
```cmd
deploy.bat        # Keeps content private, handles everything!
```
or
```powershell
.\deploy.ps1      # Keeps content private, handles everything!
```

## What Makes These Scripts Better?

The deployment scripts automatically:
- ✅ Detect changes in both content AND configuration
- ✅ Commit changes to the appropriate repositories
- ✅ Keep private content in private repo
- ✅ Keep public config in public repo
- ✅ Handle all git operations for you
- ✅ Trigger deployment to GitHub Pages
- ✅ Show clear summary of what was deployed

**One command does everything - no manual git commits needed!**

---

## Local Preview (Optional)

If you want to preview changes before deploying:

```cmd
cd "path\to\your\quartz\directory"
npx quartz build --serve -d temp-content
```

Then open: http://localhost:8080

**Note:** The `-d temp-content` flag tells Quartz to use your private content folder instead of the default `content` folder.

---

## Repository Structure

```
your-quartz-directory/
├── content/               # Your local working directory (edit here)
├── temp-content/          # Git repo linked to private GitHub repo
├── deploy.bat             # Deployment script (Windows)
├── deploy.ps1             # Deployment script (PowerShell)
└── ... (other Quartz files)
```

**How it works:**
- You edit files in `content/`
- Script copies and pushes them from `temp-content/` to private repo
- GitHub Actions fetches from private repo and builds site

---

## Quick Reference

| Task | Command |
|------|---------|
| Deploy changes (CMD) | `deploy.bat` |
| Deploy changes (PowerShell) | `   ` |
| Check deployment status | Visit GitHub Actions page of your repo |
| Local preview | `npx quartz build --serve -d temp-content` |
| View your site | `https://YOUR_USERNAME.github.io` |

---

## Setup Overview

This deployment setup uses a **two-repository architecture**:

1. **Private Repository** - Stores your markdown content files
2. **Public Repository** - Stores Quartz configuration and site code

**Benefits:**
- ✅ Website is fully public and accessible
- ✅ Content source files are NOT forkable or bulk-downloadable
- ✅ People can fork your Quartz setup without getting your content
- ✅ Automated deployment via GitHub Actions

---

## Need Help?

- **Deployment issues:** Check GitHub Actions logs in your repository
- **Quartz documentation:** https://quartz.jzhao.xyz/
- **Git issues:** Make sure you're in the correct directory and have internet connection

---

## About This Setup

This guide assumes you have:
- A private repository for your content
- A public repository with Quartz setup
- GitHub Actions workflow configured to fetch from private repo
- Personal Access Token configured as `PRIVATE_CONTENT_TOKEN` secret

For complete setup instructions, see the Private Content Setup Guide.
`python sync-notes.py` to sync notes
