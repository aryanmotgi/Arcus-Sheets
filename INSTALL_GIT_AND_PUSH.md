# 🚀 Install Git and Push to GitHub

## ⚠️ IMPORTANT: Git is NOT installed yet!

You need to install Git first before you can push to GitHub.

## Step 1: Install Git

1. **Download Git:**
   - Go to: https://git-scm.com/download/win
   - Click "Click here to download" if it doesn't start automatically

2. **Install Git:**
   - Run the downloaded `.exe` file (looks like `Git-2.xx.x-64-bit.exe`)
   - Click "Next" through all screens
   - **Keep all defaults checked** ✅
   - Click "Install"
   - Click "Finish"

3. **Restart your computer** (or close and reopen PowerShell/terminal)

## Step 2: Push to GitHub

After installing Git and restarting:

### Option A: Use the Batch File (Easiest!)

1. **Double-click:** `PUSH_TO_GITHUB_NOW.bat` in your project folder
2. **Follow the prompts:**
   - When asked for password, use your Personal Access Token
   - Create token at: https://github.com/settings/tokens
   - **DO NOT use your GitHub password** - use the token!

### Option B: Manual Commands

After installing Git, open PowerShell in your project folder and run:

```powershell
# Navigate to project (if not already there)
cd "C:\Users\Aryan\OneDrive\Rishab Fun Code"

# Initialize git
git init

# Configure git
git config --global user.name "Aryan Motgi"
git config --global user.email "aryanmotgi@users.noreply.github.com"

# Add all files
git add .

# Commit
git commit -m "Initial commit: Arcus Analytics App with PSL backup system"

# Add remote repository
git remote add origin https://github.com/aryanmotgi/Arcus-Sheets.git

# Push to GitHub
git branch -M main
git push -u origin main
```

   **When asked for password, use your Personal Access Token**
   (Create one at: https://github.com/settings/tokens)

## Step 3: Verify

1. Go to: https://github.com/aryanmotgi/Arcus-Sheets
2. Refresh the page
3. You should see all your files! 🎉

## Step 4: Open on MacBook

1. **Open Cursor** on your MacBook
2. **Clone repository:**
   - Click "Clone Repository" or use Command Palette (Cmd+Shift+P)
   - Enter: `https://github.com/aryanmotgi/Arcus-Sheets.git`
   - Choose a folder
   - Click "Clone"

3. **Set up on MacBook:**
   ```bash
   cd /path/to/cloned/folder
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## ✅ Summary

1. **Install Git** from https://git-scm.com/download/win
2. **Restart your computer** (or terminal)
3. **Run:** `PUSH_TO_GITHUB_NOW.bat`
4. **Use your token** (not password) when prompted
5. **Done!** 🎉

---

**Your Repository:** https://github.com/aryanmotgi/Arcus-Sheets
