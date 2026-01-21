# 🚀 Push Code to GitHub for Render Deploy

**Your Render service says the GitHub repo is empty. Here's how to fix it:**

---

## Step 1: Check if Git is installed

Open PowerShell/Command Prompt and run:
```bash
git --version
```

If it says "command not found", install Git:
- Download: https://git-scm.com/download/win
- Install (keep all defaults)
- Restart terminal

---

## Step 2: Initialize Git Repository

In your project folder, run:
```bash
cd "C:\Users\Aryan\OneDrive\Rishab Fun Code"
git init
```

---

## Step 3: Add All Files

```bash
git add .
```

---

## Step 4: Make First Commit

```bash
git commit -m "Initial commit - Arcus Sheets API"
```

---

## Step 5: Connect to GitHub

1. **Go to your GitHub repo:** https://github.com/aryanmotgi/Arcus-Sheets
2. **Copy the repository URL** (should be: `https://github.com/aryanmotgi/Arcus-Sheets.git`)

Then run:
```bash
git remote add origin https://github.com/aryanmotgi/Arcus-Sheets.git
git branch -M main
git push -u origin main
```

If it asks for credentials:
- **Username:** your GitHub username (aryanmotgi)
- **Password:** Use a **Personal Access Token** (not your GitHub password)

---

## Step 6: Get GitHub Personal Access Token

If you need a token:

1. Go to: https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Name it: `Render Deploy`
4. Select scopes:
   - ✅ `repo` (Full control of private repositories)
5. Click **"Generate token"**
6. **Copy the token** (you'll only see it once!)

Use this token as your password when pushing.

---

## Step 7: Render Will Auto-Deploy!

Once you push to GitHub:
1. Render will automatically detect the new code
2. It will start building and deploying
3. Check the Render dashboard - you'll see deployment progress
4. Wait 3-5 minutes for deployment

---

## Quick Commands (All at once)

Copy and paste these in order:

```bash
cd "C:\Users\Aryan\OneDrive\Rishab Fun Code"
git init
git add .
git commit -m "Initial commit - Arcus Sheets API"
git remote add origin https://github.com/aryanmotgi/Arcus-Sheets.git
git branch -M main
git push -u origin main
```

---

## ⚠️ Important Notes

1. **Don't push sensitive files!** Your `.gitignore` should already exclude:
   - `credentials/service_account.json`
   - `config/config.yaml`
   - `.env` files

2. **If repository already exists:** You might need to pull first:
   ```bash
   git pull origin main --allow-unrelated-histories
   ```

3. **After push:** Check Render dashboard - deployment should start automatically!

---

## ✅ Once Deployed

1. Your URL will be: `https://arcus-sheets.onrender.com`
2. Update Google Apps Script:
   ```javascript
   const API_URL = 'https://arcus-sheets.onrender.com/api/agent/command';
   ```
3. **Done!** No more ngrok! 🎉
