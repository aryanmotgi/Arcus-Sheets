# 🚀 Push to GitHub - Quick Guide

Follow these steps to push your code to GitHub so you can open it on your MacBook!

## Step 1: Install Git (if not already installed)

1. **Download Git for Windows:**
   - Go to: https://git-scm.com/download/win
   - Download will start automatically

2. **Install Git:**
   - Run the downloaded `.exe` file
   - Click "Next" through all screens (keep defaults)
   - Click "Install"
   - Click "Finish"

3. **Restart your terminal:**
   - Close and reopen PowerShell/Command Prompt
   - Or restart your computer

4. **Verify installation:**
   ```bash
   git --version
   ```
   You should see a version number like `git version 2.xx.x`

## Step 2: Create GitHub Repository

1. **Go to GitHub:** https://github.com
2. **Sign in** (or create account if needed)
3. **Create new repository:**
   - Click the **"+"** icon (top right)
   - Click **"New repository"**
   - **Name:** `arcus-app` (or any name you like)
   - **Visibility:** Choose **Private** (recommended)
   - **DO NOT check:**
     - ❌ Add README
     - ❌ Add .gitignore  
     - ❌ Choose a license
   - Click **"Create repository"**

4. **Copy the repository URL:**
   - GitHub will show you a URL like: `https://github.com/yourusername/arcus-app.git`
   - **Copy this URL** - you'll need it!

## Step 3: Push Your Code

### Option A: Use the Batch File (Easiest!)

1. **Double-click** `PUSH_TO_GITHUB.bat` in your project folder
2. Follow the prompts:
   - Enter your name
   - Enter your email
   - When asked for the repository URL, paste the URL from Step 2
3. When asked for password, use a **Personal Access Token** (see Step 4)

### Option B: Manual Commands

Open PowerShell or Command Prompt in your project folder and run:

```bash
# 1. Navigate to project (if not already there)
cd "C:\Users\Aryan\OneDrive\Rishab Fun Code"

# 2. Initialize git (if first time)
git init

# 3. Configure git (if first time)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 4. Add all files
git add .

# 5. Commit
git commit -m "Initial commit: Arcus Analytics App"

# 6. Add remote (REPLACE with your actual repo URL from Step 2)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# 7. Push to GitHub
git branch -M main
git push -u origin main
```

## Step 4: Get Personal Access Token (for password)

GitHub requires a **Personal Access Token** instead of your password:

1. **Go to:** https://github.com/settings/tokens
2. **Click:** "Generate new token" → "Generate new token (classic)"
3. **Fill in:**
   - **Note:** `arcus-app-push`
   - **Expiration:** Choose 90 days (or longer)
   - **Scopes:** Check ✅ **repo** (full control of private repositories)
4. **Click:** "Generate token"
5. **COPY THE TOKEN IMMEDIATELY** (you won't see it again!)
   - It looks like: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
6. **Use this token** as your password when pushing

## Step 5: Verify It Worked

1. Go back to your GitHub repository page
2. Refresh the page
3. You should see all your files! 🎉

## Step 6: Open on MacBook

Once your code is on GitHub:

1. **On your MacBook:**
   - Open Cursor
   - Click "Clone Repository" or use Command Palette (Cmd+Shift+P)
   - Enter your repository URL: `https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git`
   - Choose a folder to save it
   - Click "Clone"

2. **Set up on MacBook:**
   ```bash
   cd /path/to/cloned/folder
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## ⚠️ Troubleshooting

### "git: command not found"
- Git is not installed or not in PATH
- Restart your terminal after installing Git
- Or restart your computer

### "fatal: remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
```

### "Authentication failed"
- Make sure you're using a **Personal Access Token**, not your password
- Generate a new token if needed

### "Please tell me who you are"
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### "Failed to push some refs"
```bash
# Pull first (if repo has files)
git pull origin main --allow-unrelated-histories

# Then push
git push -u origin main
```

---

**Need help?** If you get stuck, let me know what error message you see!
