# Deployment Guide

## Quick Start

After editing your content, simply run:

```cmd
deploy.bat
```

That's it! Your site will be updated in 2-5 minutes.

---

## What Happens When You Deploy?

1. **Step 1:** Your content changes are committed and pushed to the **private** repository (`content-ajabhinai`)
2. **Step 2:** A timestamp file is created in the **public** repository to trigger GitHub Actions
3. **Step 3:** GitHub Actions workflow automatically:
   - Fetches latest content from private repo
   - Fetches latest config from public repo
   - Builds the Quartz site
   - Deploys to GitHub Pages

---

## Two Ways to Deploy

### Option 1: Batch File (Recommended for Windows)

```cmd
cd "d:\My\my Codes\ajabhinai\quartz"
deploy.bat
```

### Option 2: PowerShell Script

```powershell
cd "d:\My\my Codes\ajabhinai\quartz"
.\deploy.ps1
```

---

## Daily Workflow

### When You Add/Edit Notes:

1. **Edit** your markdown files in `d:\My\my Codes\ajabhinai\quartz\content\`
   - Use Obsidian, VS Code, or any text editor

2. **Deploy** by running:
   ```cmd
   deploy.bat
   ```

3. **Wait** 2-5 minutes for GitHub Actions to build and deploy

4. **Check** your site: https://aj-abhinai.github.io

---

## Troubleshooting

### Script says "No changes in content repository"

This is normal if you haven't edited any files since last deployment.

### Script fails with "Permission denied"

Make sure you've committed any changes and have internet connection.

### Want to check deployment status?

Go to: https://github.com/aj-abhinai/aj-abhinai.github.io/actions

---

## Important: Don't Use `npx quartz sync`

**OLD WAY (Don't use):**
```cmd
npx quartz sync   # ❌ This pushes content to public repo!
```

**NEW WAY (Use this):**
```cmd
deploy.bat        # ✅ This keeps content in private repo!
```

---

## Local Preview (Optional)

If you want to preview changes before deploying:

```cmd
cd "d:\My\my Codes\ajabhinai\quartz"
npx quartz build --serve
```

Then open: http://localhost:8080

**Note:** Local preview uses your local content files, not the private repo.

---

## Repository Structure

```
d:\My\my Codes\ajabhinai\quartz\
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
| Deploy changes | `deploy.bat` |
| Check deployment status | Visit [Actions page](https://github.com/aj-abhinai/aj-abhinai.github.io/actions) |
| Local preview | `npx quartz build --serve` |
| View your site | https://aj-abhinai.github.io |

---

## Need Help?

- **Deployment issues:** Check [GitHub Actions logs](https://github.com/aj-abhinai/aj-abhinai.github.io/actions)
- **Quartz documentation:** https://quartz.jzhao.xyz/
- **Git issues:** Make sure you're in the correct directory and have internet connection
