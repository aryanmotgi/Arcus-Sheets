# 🚀 Deploy to Railway - Access From Anywhere, No ngrok!

**Deploy your FastAPI server to Railway so you can use it from any device, anywhere, without ngrok!**

---

## ⚡ Quick Deploy (5 Minutes)

### Step 1: Sign Up for Railway

1. Go to: https://railway.app/
2. Click **"Sign Up"** or **"Login"**
3. Sign up with **GitHub** (easiest)

---

### Step 2: Create New Project

1. In Railway dashboard, click **"+ New Project"**
2. Choose **"Deploy from GitHub repo"**
3. Select your repository (or connect GitHub if needed)
4. Railway will auto-detect it's a Python app

---

### Step 3: Add Environment Variables

In Railway dashboard, go to your project → **"Variables"** tab and add:

```
GOOGLE_SHEETS_SPREADSHEET_ID=1wK6aA1Sny5Ie3Ef8gU8LMgaBMjpNKW7ol1pxVWmGihE
```

**For credentials:**
- Click **"Add Variable"**
- **Key:** `GOOGLE_CREDENTIALS`
- **Value:** Paste the entire contents of `credentials/service_account.json`

**For config:**
- **Key:** `SHOPIFY_STORE_URL`
- **Value:** `https://arcuswear.myshopify.com`
- **Key:** `SHOPIFY_CLIENT_ID`
- **Value:** Your client ID
- **Key:** `SHOPIFY_CLIENT_SECRET`
- **Value:** Your client secret

---

### Step 4: Deploy!

1. Railway will automatically start deploying
2. Wait 2-3 minutes for deployment
3. Click on your service → **"Settings"** tab
4. Under **"Domains"**, Railway will generate a URL like:
   ```
   https://arcus-sheets-production.up.railway.app
   ```
5. **Copy this URL!**

---

### Step 5: Update Google Apps Script

1. Open your Google Sheet
2. **Extensions → Apps Script**
3. Find this line:
   ```javascript
   const API_URL = 'https://07be8759cd80.ngrok-free.app/api/agent/command';
   ```
4. Replace with your Railway URL:
   ```javascript
   const API_URL = 'https://arcus-sheets-production.up.railway.app/api/agent/command';
   ```
5. **Save** (Ctrl+S)
6. **Refresh Google Sheet**

---

## ✅ Done!

**Now you can:**
- ✅ Access the agent from anywhere
- ✅ Use it on any device (phone, tablet, another computer)
- ✅ No need to run ngrok or local server
- ✅ It runs 24/7 automatically

---

## 🔧 Troubleshooting

**"Failed to connect"**
- Check Railway dashboard - is deployment successful?
- Make sure URL is correct in Apps Script
- Try visiting the Railway URL directly in browser

**"Module not found" errors**
- Railway should auto-install from `requirements.txt`
- Check Railway logs for errors

**Environment variables not working**
- Make sure all variables are added in Railway dashboard
- Redeploy after adding variables

---

## 💡 Pro Tips

1. **Railway gives you a free tier** - perfect for this!
2. **Auto-deploys** when you push to GitHub
3. **Logs available** in Railway dashboard
4. **Can pause when not needed** to save resources

---

**No more ngrok headaches! 🎉**
