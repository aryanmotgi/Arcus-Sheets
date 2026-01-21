# 🆓 Free Deployment Options - Access From Anywhere!

**100% FREE options to deploy your FastAPI server (no ngrok needed!)**

---

## 🎯 Option 1: Render (RECOMMENDED - Best Free Option)

### ✅ Free Tier Includes:
- ✅ Free tier with 750 hours/month
- ✅ Automatic HTTPS
- ✅ Custom domains
- ✅ Auto-deploy from GitHub
- ✅ Sleeps after 15 min inactivity (wakes on request)

### Step 1: Sign Up
1. Go to: https://render.com/
2. Click **"Get Started for Free"**
3. Sign up with **GitHub** (easiest)

### Step 2: Create Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Select your repository

### Step 3: Configure Settings
- **Name:** `arcus-sheets-api` (or whatever you want)
- **Region:** Choose closest to you
- **Branch:** `main` (or `master`)
- **Root Directory:** Leave empty (or `.` if needed)
- **Runtime:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Step 4: Add Environment Variables
Click **"Advanced"** → **"Add Environment Variable"**

Add these:
```
GOOGLE_SHEETS_SPREADSHEET_ID=1wK6aA1Sny5Ie3Ef8gU8LMgaBMjpNKW7ol1pxVWmGihE
SHOPIFY_STORE_URL=https://arcuswear.myshopify.com
SHOPIFY_CLIENT_ID=your_client_id
SHOPIFY_CLIENT_SECRET=your_client_secret
```

For Google credentials, add:
- **Key:** `GOOGLE_CREDENTIALS`
- **Value:** Paste entire JSON from `credentials/service_account.json`

### Step 5: Deploy!
1. Click **"Create Web Service"**
2. Wait 3-5 minutes for deployment
3. Your URL will be: `https://arcus-sheets-api.onrender.com`
4. **Copy this URL!**

### Step 6: Update Google Apps Script
Replace the API_URL with:
```javascript
const API_URL = 'https://arcus-sheets-api.onrender.com/api/agent/command';
```

**✅ Done! Access from anywhere, any device!**

---

## 🚀 Option 2: Fly.io (Free Tier Available)

### Step 1: Install Fly CLI
```powershell
# Windows PowerShell (run as Administrator)
iwr https://fly.io/install.ps1 -useb | iex
```

### Step 2: Sign Up
1. Go to: https://fly.io/
2. Sign up (free account)
3. Install Fly CLI (see above)

### Step 3: Login
```bash
fly auth login
```

### Step 4: Create fly.toml
Create file `fly.toml` in project root:
```toml
app = "arcus-sheets-api"
primary_region = "iad"

[build]

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256
```

### Step 5: Deploy
```bash
fly launch
# Answer prompts
fly secrets set GOOGLE_SHEETS_SPREADSHEET_ID="1wK6aA1Sny5Ie3Ef8gU8LMgaBMjpNKW7ol1pxVWmGihE"
fly secrets set SHOPIFY_STORE_URL="https://arcuswear.myshopify.com"
# Add other secrets...
fly deploy
```

### Step 6: Get URL
```bash
fly status
```
Your URL will be: `https://arcus-sheets-api.fly.dev`

---

## 🐍 Option 3: PythonAnywhere (Free Beginner Account)

### Step 1: Sign Up
1. Go to: https://www.pythonanywhere.com/
2. Click **"Create a Beginner account"** (FREE)
3. Sign up

### Step 2: Upload Files
1. Go to **"Files"** tab
2. Upload your project files OR clone from GitHub:
   ```bash
   git clone https://github.com/yourusername/your-repo.git
   ```

### Step 3: Install Dependencies
1. Go to **"Bash"** console
2. Run:
   ```bash
   pip3.10 install --user fastapi uvicorn gspread pandas pyyaml
   ```

### Step 4: Create Web App
1. Go to **"Web"** tab
2. Click **"Add a new web app"**
3. Choose **"Flask"** (we'll configure for FastAPI)
4. Choose Python 3.10

### Step 5: Configure
1. Click on **WSGI configuration file**
2. Replace with:
   ```python
   import sys
   path = '/home/yourusername/arcus-sheets'  # Your project path
   if path not in sys.path:
       sys.path.append(path)
   
   from app.main import app
   application = app
   ```

### Step 6: Set Environment Variables
1. Go to **"Files"** tab
2. Create `.env` file or add to web app config

### Step 7: Reload
1. Go back to **"Web"** tab
2. Click **"Reload"**
3. Your URL: `yourusername.pythonanywhere.com`

---

## 🏆 Best Option: Render.com

**Why Render:**
- ✅ 100% FREE for small apps
- ✅ Easiest setup
- ✅ Auto-deploy from GitHub
- ✅ HTTPS included
- ✅ No credit card required
- ⚠️ Sleeps after 15 min (but wakes automatically when requested)

**Setup Time:** 5-10 minutes

**Cost:** $0/month

---

## 📝 Quick Checklist for Render

- [ ] Sign up at render.com (GitHub)
- [ ] Create new Web Service
- [ ] Connect GitHub repo
- [ ] Set Build Command: `pip install -r requirements.txt`
- [ ] Set Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] Add environment variables
- [ ] Deploy and get URL
- [ ] Update Google Apps Script with Render URL
- [ ] Test!

---

## ⚡ Super Quick Start (Render)

1. Go to https://render.com → Sign up with GitHub
2. Click "New +" → "Web Service"
3. Connect repo
4. Set:
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables
6. Click "Create Web Service"
7. Wait 5 minutes
8. Copy URL → Update Google Apps Script
9. **Done!** 🎉

---

**Want me to walk you through Render step-by-step? It's the easiest and 100% free!**
