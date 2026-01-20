# 🚀 After Git is Installed - Next Steps

Once you've installed Git and verified it works (`git --version` shows a version), follow these steps:

## Step 1: Configure Git (First Time Only)

Open PowerShell and run:

```powershell
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

Replace with your actual name and email.

## Step 2: Create GitHub Repository

1. Go to: **https://github.com/new**
2. Repository name: `arcus-analytics-app`
3. Choose **Private** (recommended)
4. **DO NOT** check any boxes
5. Click **"Create repository"**
6. **Copy the repository URL** (you'll need it)

## Step 3: Push Your Code

Run these commands in PowerShell:

```powershell
# 1. Go to your project folder
cd "C:\Users\Aryan\OneDrive\Rishab Fun Code"

# 2. Initialize Git
git init

# 3. Add all files
git add .

# 4. Commit
git commit -m "Initial commit: Arcus Analytics App"

# 5. Add remote (REPLACE with your actual repo URL!)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# 6. Push to GitHub
git branch -M main
git push -u origin main
```

## Step 4: Authentication

When you push, GitHub will ask for:
- **Username:** Your GitHub username
- **Password:** Use a **Personal Access Token** (create one at https://github.com/settings/tokens)

---

**After Git is installed, let me know and I'll help you push!**
