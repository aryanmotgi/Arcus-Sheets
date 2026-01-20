# 🎵 TikTok Analytics Integration - Step by Step

Since you already have a TikTok account, here's exactly how to connect it to see real analytics in your app.

## 📋 Prerequisites
- ✅ You have a TikTok account
- ✅ For Business API, you need a **TikTok Business Account** (not personal)

## Step 1: Convert to TikTok Business Account (If Needed)

If your TikTok account is personal, convert it to Business:

1. **Open TikTok app** on your phone
2. Go to **Profile** → **Settings** (three lines, top right)
3. Tap **"Creator tools"** → **"Switch to Business Account"**
4. Follow the prompts to convert
5. This is **free** and allows you to access analytics

---

## Step 2: Apply for TikTok Business API Access

### Step 2.1: Go to TikTok Developers
1. Open browser and go to: **https://developers.tiktok.com/**
2. Click **"Get Started"** or **"Log In"** (top right)
3. **Log in** with your TikTok Business account

### Step 2.2: Create Developer Account
1. If this is your first time, click **"Sign Up"** or **"Apply"**
2. Fill in:
   - Your business information
   - Company name
   - Email address
   - Phone number
3. Click **"Submit"**

### Step 2.3: Apply for API Access
1. After logging in, you'll see the dashboard
2. Click **"Apply for Access"** or **"Create App"** button
3. Fill out the application form:

   **App Information:**
   - **App Name:** `Arcus Analytics Dashboard`
   - **App Category:** Choose **"Analytics"** or **"Other"**
   - **App Type:** Select **"Web App"** or **"Server-side App"**

   **Business Information:**
   - Your business details
   - **Use Case:** Describe: "Internal analytics dashboard for tracking TikTok performance metrics and engagement"

   **Description Example:**
   ```
   We need API access to build an internal analytics dashboard that displays 
   TikTok metrics (followers, views, likes, engagement rate) for our business. 
   This is for internal use only to monitor our social media performance.
   ```

4. Click **"Submit Application"**
5. **Wait for approval** - This can take **1-7 business days**
6. You'll receive an **email** when approved

---

## Step 3: Create Your App (After Approval)

Once you get the approval email:

### Step 3.1: Log Back In
1. Go to: **https://developers.tiktok.com/**
2. Log in with your TikTok Business account

### Step 3.2: Create App
1. Click **"My Apps"** or **"Create App"**
2. You should see your application approved
3. Click **"Create App"** or **"Set Up App"**

### Step 3.3: Get Your Credentials
1. After creating the app, you'll see your **App Dashboard**
2. Go to **"Basic Information"** or **"App Info"** tab
3. You'll see:

   **Client Key** (also called App ID)
   - Copy this - it looks like: `aw1234567890abcdef`

   **Client Secret**
   - Click **"View"** or **"Reveal"** to see it
   - Copy this - it's a long string

### Step 3.4: Set Up OAuth Redirect
1. Go to **"Platform"** or **"Settings"** section
2. Add **Redirect URI:**
   - For local development: `http://localhost:8000/callback`
   - Or: `http://localhost:8000/api/tiktok/callback`
3. Click **"Save"**

---

## Step 4: Generate Access Token

There are two ways to get an access token:

### Option A: User Access Token (Easier for Testing)

1. Go to **"Tools"** → **"Generate Token"** or **"Authorization"**
2. Click **"Generate Token"**
3. Select the permissions you need:
   - ✅ `user.info.basic` - Get user info
   - ✅ `video.list` - List videos
   - ✅ `video.insights` - Video analytics
   - ✅ `analytics.basic` - Basic analytics
4. Click **"Authorize"** or **"Generate"**
5. **Copy the Access Token** - it looks like: `act.abc123...`

### Option B: OAuth Flow (For Production)

If you need a permanent token, use OAuth:

1. Construct the OAuth URL:
   ```
   https://www.tiktok.com/v2/auth/authorize/?client_key=YOUR_CLIENT_KEY&scope=user.info.basic,video.list,video.insights&response_type=code&redirect_uri=http://localhost:8000/callback
   ```
   (Replace `YOUR_CLIENT_KEY` with your actual Client Key)

2. Open this URL in your browser
3. Log in and authorize the app
4. You'll be redirected with a code
5. Exchange the code for an access token (see Step 5 below)

---

## Step 5: Exchange Code for Token (If Using OAuth)

If you got a code from OAuth redirect:

1. Use this Python script or API call:

```python
import requests

CLIENT_KEY = "your_client_key"
CLIENT_SECRET = "your_client_secret"
AUTHORIZATION_CODE = "code_from_redirect"

url = "https://open.tiktokapis.com/v2/oauth/token/"
headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}
data = {
    "client_key": CLIENT_KEY,
    "client_secret": CLIENT_SECRET,
    "code": AUTHORIZATION_CODE,
    "grant_type": "authorization_code",
    "redirect_uri": "http://localhost:8000/callback"
}

response = requests.post(url, headers=headers, data=data)
token_data = response.json()
access_token = token_data["access_token"]
print(f"Access Token: {access_token}")
```

Save this as `get_tiktok_token.py` and run it.

---

## Step 6: Create .env File

### Step 6.1: Create the File
1. Navigate to your project folder: `C:\Users\Aryan\OneDrive\Rishab Fun Code`
2. **Right-click** in the folder (empty space)
3. **New** → **Text Document**
4. Name it: `.env` (with the dot at the start)
5. If Windows warns you, click **"Yes"**

### Step 6.2: Add TikTok Credentials
1. **Right-click** on `.env` → **Open with** → **Notepad**
2. Copy and paste this:

```env
TIKTOK_CLIENT_KEY=paste_your_client_key_here
TIKTOK_CLIENT_SECRET=paste_your_client_secret_here
TIKTOK_ACCESS_TOKEN=paste_your_access_token_here
```

3. **Replace** `paste_your_..._here` with your actual values:
   ```env
   TIKTOK_CLIENT_KEY=aw1234567890abcdef
   TIKTOK_CLIENT_SECRET=xyz789abc123def456ghi789
   TIKTOK_ACCESS_TOKEN=act.abc123def456ghi789jkl012
   ```

4. **Save** (Ctrl+S)
5. **Close** Notepad

**Important:**
- No spaces around the `=`
- No quotes around the values
- Each on its own line

---

## Step 7: Test the Integration

### Step 7.1: Restart Backend
1. Stop your backend server (if running): Press **Ctrl+C**
2. Start it again:
   ```bash
   python run_app.py
   ```

### Step 7.2: Check the App
1. Open your browser: `http://localhost:8080`
2. Go to **Analytics** section
3. Click on **TikTok** tab
4. You should see **real data** from your TikTok account!

---

## 🎯 What You Should See

Once connected, your TikTok analytics will show:
- ✅ **Followers** - Current follower count
- ✅ **Views** - Total video views
- ✅ **Likes** - Total likes across videos
- ✅ **Posts Count** - Number of videos
- ✅ **Engagement Rate** - Calculated percentage

---

## ⚠️ Troubleshooting

### "Still seeing mock data"
- ✅ Check that `.env` file is in project root (same folder as `run_app.py`)
- ✅ Check that variable names are exactly: `TIKTOK_CLIENT_KEY`, `TIKTOK_CLIENT_SECRET`, `TIKTOK_ACCESS_TOKEN`
- ✅ Check no extra spaces or quotes
- ✅ **Restart backend** after editing `.env`

### "API Error" or "Invalid Token"
- ✅ Make sure token hasn't expired (user tokens expire after 24 hours)
- ✅ Generate a new token
- ✅ Check that you approved all required permissions

### "Access Denied" or "Not Approved"
- ✅ Wait for API access approval (can take 1-7 days)
- ✅ Check your email for approval notification
- ✅ Make sure you're using a Business account

### "Can't find .env file"
- ✅ In File Explorer, click **View** → Check **"Hidden items"**
- ✅ The file should be at: `C:\Users\Aryan\OneDrive\Rishab Fun Code\.env`

---

## 📝 Quick Checklist

- [ ] Converted TikTok account to Business (if needed)
- [ ] Applied for TikTok API access at developers.tiktok.com
- [ ] Received approval email
- [ ] Created app in TikTok Developer Portal
- [ ] Got Client Key (App ID)
- [ ] Got Client Secret
- [ ] Generated Access Token
- [ ] Created `.env` file in project root
- [ ] Added all 3 credentials to `.env`
- [ ] Saved `.env` file
- [ ] Restarted backend server
- [ ] Checked app - seeing real TikTok data! 🎉

---

## 🔄 Getting a New Token (When It Expires)

Access tokens expire. To get a new one:

1. Go to TikTok Developer Portal
2. Go to **"Tools"** → **"Generate Token"**
3. Generate a new token
4. Update the `TIKTOK_ACCESS_TOKEN` in your `.env` file
5. Restart backend

---

**That's it!** Once you complete these steps, you'll see real TikTok analytics in your app. 

**Need help?** Let me know which step you're on and I'll help you through it!
