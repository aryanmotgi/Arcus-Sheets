# 🌐 Deploy Your App Online - Access From Anywhere

Here are the best options to host your app so you can access it from anywhere, not just localhost!

## 🚀 Option 1: Railway (Recommended - Easiest & Free Tier)

Railway is the easiest way to deploy - it's free for small apps and very simple!

### Step 1: Prepare Your App

1. Create a file called `Procfile` in your project root:
   ```
   web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

2. Create a file called `runtime.txt`:
   ```
   python-3.11
   ```

3. Make sure `requirements.txt` is up to date (it already is!)

### Step 2: Deploy to Railway

1. **Sign up for Railway:**
   - Go to: https://railway.app/
   - Click **"Start a New Project"**
   - Sign up with GitHub (easiest) or email

2. **Create New Project:**
   - Click **"New Project"**
   - Choose **"Deploy from GitHub repo"** (recommended)
   - OR **"Deploy from local directory"**

3. **If using GitHub:**
   - Connect your GitHub account
   - Select your repository
   - Railway will auto-detect Python

4. **Configure Environment Variables:**
   - Go to your project → **"Variables"** tab
   - Add all your `.env` variables:
     ```
     INSTAGRAM_ACCESS_TOKEN=your_token
     INSTAGRAM_BUSINESS_ACCOUNT_ID=3474793
     ```
   - Add your Google Sheets credentials path (might need to adjust)

5. **Deploy:**
   - Railway will automatically build and deploy
   - It will give you a URL like: `https://your-app.up.railway.app`

6. **Update Frontend:**
   - Open `frontend/app.js`
   - Change the API URL to your Railway URL:
     ```javascript
     const API_BASE_URL = 'https://your-app.up.railway.app/api';
     ```
   - Deploy frontend to Railway too, or use a static host

---

## 🌟 Option 2: Render (Free & Easy)

### Step 1: Prepare Files

1. Create `Procfile`:
   ```
   web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

2. Create `render.yaml` in project root:
   ```yaml
   services:
     - type: web
       name: arcus-backend
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
       envVars:
         - key: INSTAGRAM_ACCESS_TOKEN
           sync: false
         - key: INSTAGRAM_BUSINESS_ACCOUNT_ID
           value: 3474793
   ```

### Step 2: Deploy

1. Go to: https://render.com/
2. Sign up (free)
3. Click **"New +"** → **"Web Service"**
4. Connect GitHub repo or upload files
5. Render will auto-detect settings
6. Add environment variables in dashboard
7. Deploy!

---

## ☁️ Option 3: PythonAnywhere (Free for Beginners)

### Step 1: Sign Up

1. Go to: https://www.pythonanywhere.com/
2. Sign up for free **Beginner account**

### Step 2: Upload Your Files

1. Go to **"Files"** tab
2. Upload your project files
3. Or clone from GitHub

### Step 3: Set Up Virtual Environment

1. Open **"Bash"** console
2. Run:
   ```bash
   mkvirtualenv arcus --python=python3.11
   pip install -r requirements.txt
   ```

### Step 4: Create Web App

1. Go to **"Web"** tab
2. Click **"Add a new web app"**
3. Choose **Flask** (we'll configure it for FastAPI)
4. Set source code to your project folder

### Step 5: Configure WSGI

1. Click on **WSGI configuration file**
2. Replace content with:
   ```python
   import sys
   path = '/home/yourusername/path/to/project'
   if path not in sys.path:
       sys.path.append(path)
   
   from app.main import app
   application = app
   ```

### Step 6: Set Environment Variables

1. Go to **"Files"** → `.env` file
2. Edit and add your credentials

### Step 7: Reload Web App

1. Go back to **"Web"** tab
2. Click **"Reload"**
3. Your app will be at: `yourusername.pythonanywhere.com`

---

## 🔧 Option 4: Fly.io (Free Tier Available)

### Step 1: Install Fly CLI

```bash
# Windows PowerShell
iwr https://fly.io/install.ps1 -useb | iex
```

### Step 2: Create fly.toml

Create `fly.toml` in project root:
```toml
app = "arcus-app"
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

### Step 3: Deploy

```bash
fly launch
fly secrets set INSTAGRAM_ACCESS_TOKEN=your_token
fly secrets set INSTAGRAM_BUSINESS_ACCOUNT_ID=3474793
fly deploy
```

---

## 📝 Quick Setup Checklist (Railway - Recommended)

- [ ] Create `Procfile` with: `web: uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] Create `runtime.txt` with: `python-3.11`
- [ ] Sign up at railway.app
- [ ] Create new project
- [ ] Connect GitHub repo or upload files
- [ ] Add environment variables in Railway dashboard
- [ ] Deploy and get URL
- [ ] Update frontend `app.js` with Railway URL
- [ ] Deploy frontend (Railway or separate host)

---

## 🎯 Simplest Solution: Use Railway for Everything

### Deploy Backend to Railway:

1. **Create Procfile:**
   ```
   web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

2. **Push to GitHub** (if not already)

3. **Railway Setup:**
   - Sign up: railway.app
   - New Project → GitHub repo
   - Add environment variables
   - Auto-deploys!

4. **Get your backend URL:** `https://arcus-backend.up.railway.app`

### Deploy Frontend to Railway or Vercel:

**Option A: Railway (Same place):**
- Create separate service for frontend
- Point it to your `frontend` folder
- Set build command: none (static files)
- Set start: serve static files

**Option B: Vercel (Easier for frontend):**
- Go to: vercel.com
- Import project
- Select `frontend` folder
- Deploy!
- Get frontend URL: `https://arcus-app.vercel.app`

### Update Frontend to Use Backend URL:

1. Open `frontend/app.js`
2. Change line 2:
   ```javascript
   const API_BASE_URL = 'https://your-backend-url.up.railway.app/api';
   ```
3. Redeploy frontend

---

## 🔐 Environment Variables Setup

When deploying, add these in your hosting platform's dashboard:

```
INSTAGRAM_ACCESS_TOKEN=your_token
INSTAGRAM_BUSINESS_ACCOUNT_ID=3474793
```

(And any other secrets from your .env file)

---

## ✅ Recommended: Railway + Vercel Combo

1. **Backend → Railway** (free tier)
2. **Frontend → Vercel** (free tier, better for static sites)
3. Update frontend to point to Railway backend URL
4. **Done!** Access from anywhere! 🌍

---

**Need help with a specific platform?** Let me know which one you want to use!
