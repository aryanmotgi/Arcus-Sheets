# ⚡ Quick Deploy Guide - Access From Anywhere

## Fastest Way: Railway (Free & Easy)

### 1. Create Procfile (Done! ✅)
Already created for you in project root.

### 2. Push to GitHub

If you haven't already:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin your-github-repo-url
git push -u origin main
```

### 3. Deploy to Railway

1. **Go to:** https://railway.app/
2. **Sign up** (free)
3. **Click:** "New Project"
4. **Choose:** "Deploy from GitHub repo"
5. **Select your repository**
6. **Add Environment Variables:**
   - Click "Variables" tab
   - Add:
     ```
     INSTAGRAM_ACCESS_TOKEN=your_token
     INSTAGRAM_BUSINESS_ACCOUNT_ID=3474793
     ```
7. **Wait for deployment** (~2 minutes)
8. **Get your URL:** `https://your-app.up.railway.app`

### 4. Update Frontend

1. Open `frontend/app.js`
2. Line 2, change to:
   ```javascript
   const API_BASE_URL = 'https://your-app.up.railway.app/api';
   ```
   (Replace `your-app` with your actual Railway app name)

### 5. Deploy Frontend to Vercel

1. **Go to:** https://vercel.com/
2. **Sign up** (free)
3. **Import project** → Select your GitHub repo
4. **Root Directory:** Set to `frontend`
5. **Deploy!**
6. **Get frontend URL:** `https://arcus-app.vercel.app`

### 6. Access From Anywhere!

- Open the Vercel URL on any device
- Works from anywhere in the world! 🌍

---

## Alternative: Everything on Railway

1. Deploy backend to Railway (steps above)
2. Create second service in Railway for frontend
3. Set root directory to `frontend` folder
4. Deploy!

---

**That's it!** Your app will be accessible from anywhere, no localhost or WiFi needed!
