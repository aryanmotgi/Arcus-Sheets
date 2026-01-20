# 📸 Instagram Analytics Setup - Step by Step

Since you already have a Business Instagram account, let's connect it to see real analytics in your app!

## ✅ What You Need
- Instagram Business Account ✅ (You have this!)
- Facebook account (connected to your Instagram)

---

## Step 1: Create the .env File

### Step 1.1: Create the File
1. Open **File Explorer**
2. Go to: `C:\Users\Aryan\OneDrive\Rishab Fun Code`
3. **Right-click** in empty space (not on a file)
4. Click **"New"** → **"Text Document"**
5. Name it exactly: `.env` (with the dot at the start)
   - Windows might warn you - click **"Yes"**

### Step 1.2: If You Can't See .env File
- Click **"View"** tab in File Explorer
- Check the box: **"Hidden items"**
- Now you should see it

---

## Step 2: Get Your Instagram Business Account ID

### Step 2.1: Go to Facebook Business Settings
1. Open browser
2. Go to: **https://business.facebook.com/settings**
3. **Log in** with your Facebook account (the one connected to Instagram)

### Step 2.2: Find Your Instagram Account
1. In the left menu, click **"Instagram Accounts"**
2. You should see your Instagram account listed
3. **Click on your Instagram account**

### Step 2.3: Copy the Account ID
1. Look for **"Instagram Account ID"** or **"Account ID"**
2. It's a long number like: `17841405309211834`
3. **Copy this number** - you'll need it later!

**Example:**
```
Instagram Account ID: 17841405309211834
```

---

## Step 3: Create Facebook App & Get Access Token

### Step 3.1: Go to Facebook Developers
1. Go to: **https://developers.facebook.com/**
2. **Log in** with your Facebook account
3. If this is your first time, you might need to verify your account

### Step 3.2: Create a New App
1. Click **"My Apps"** button (top right, next to your profile)
2. Click **"Create App"**
3. Choose **"Business"** type
4. Click **"Next"**

### Step 3.3: Fill in App Details
- **App Name:** `Arcus Analytics` (or any name you want)
- **App Contact Email:** Your email address
- Click **"Create App"**

### Step 3.4: Add Instagram Product
1. In your app dashboard, scroll down to find **"Products"** section
2. Look for **"Instagram"** and click **"Set Up"**
3. It might ask what you want to do - just click **"Continue"**

### Step 3.5: Connect Your Instagram Account
1. It should show your Instagram Business account
2. Click **"Connect"** or **"Add"** to link it
3. Click **"Continue"**

---

## Step 4: Generate Access Token

### Step 4.1: Go to Graph API Explorer
1. Go to: **https://developers.facebook.com/tools/explorer/**
2. At the top, you'll see a dropdown that says **"Meta App"** or **"App"**
3. **Click the dropdown** and select your app (`Arcus Analytics`)

### Step 4.2: Select Your Instagram Account
1. Next to "Meta App", there's another dropdown
2. Click it and select **your Instagram Business account**
   - It might show as your Instagram username

### Step 4.3: Get Permissions
1. Click **"Generate Access Token"** button
2. It will ask for permissions - check these:
   - ✅ `instagram_basic`
   - ✅ `instagram_manage_insights`
   - ✅ `pages_read_engagement`
   - ✅ `pages_read_user_content`
3. Click **"Generate Access Token"**
4. **Copy the token** that appears - it's a long string like:
   ```
   EAABwzLixZBT8BO7ZCZCHZC...
   ```

⚠️ **This token expires in 1-2 hours!** We'll make it last longer next.

---

## Step 5: Make Token Long-Lived (60 Days)

### Step 5.1: Go to Access Token Debugger
1. Go to: **https://developers.facebook.com/tools/debug/accesstoken/**
2. **Paste your token** in the "Access Token" field
3. Click **"Debug"**

### Step 5.2: Extend the Token
1. You'll see token information
2. Look for button: **"Extend Access Token"**
3. Click it
4. **Copy the new token** that appears
5. This one lasts **60 days**!

---

## Step 6: Fill in the .env File

### Step 6.1: Open .env File
1. Go back to your project folder
2. **Right-click** on `.env` file
3. Select **"Open with"** → **"Notepad"**

### Step 6.2: Add Your Credentials
1. Copy and paste this into the file:

```env
INSTAGRAM_ACCESS_TOKEN=paste_your_extended_token_here
INSTAGRAM_BUSINESS_ACCOUNT_ID=paste_your_account_id_here
```

2. **Replace** the placeholders:
   - Replace `paste_your_extended_token_here` with your 60-day token
   - Replace `paste_your_account_id_here` with your Instagram Account ID

**Example of what it should look like:**
```env
INSTAGRAM_ACCESS_TOKEN=EAABwzLixZBT8BO7ZCZCHZC...your_full_token
INSTAGRAM_BUSINESS_ACCOUNT_ID=17841405309211834
```

**Important:**
- ✅ NO spaces around the `=` sign
- ✅ NO quotes around the values
- ✅ Each value on its own line
- ✅ No blank lines at the top

### Step 6.3: Save the File
1. Press **Ctrl + S** to save
2. Close Notepad

---

## Step 7: Test It Works!

### Step 7.1: Restart Backend Server
1. Open terminal/command prompt
2. If backend is running, **stop it** (press **Ctrl+C**)
3. Start it again:
   ```bash
   python run_app.py
   ```
4. Wait until you see: `Uvicorn running on http://0.0.0.0:8000`

### Step 7.2: Check Your App
1. Open browser
2. Go to: `http://localhost:8080`
3. Click **"Analytics"** tab (bottom navigation)
4. Click **"Instagram"** tab at the top
5. You should see **real data** from your Instagram account! 🎉

**What you'll see:**
- ✅ Real follower count
- ✅ Number of posts
- ✅ Engagement rate
- ✅ Average likes
- ✅ Average comments
- ✅ Reach

---

## ✅ Quick Checklist

Before testing, make sure:
- [ ] Created `.env` file in project root
- [ ] Got Instagram Business Account ID from Facebook Business Settings
- [ ] Created Facebook App
- [ ] Added Instagram product to app
- [ ] Generated access token
- [ ] Extended token to 60 days
- [ ] Added both credentials to `.env` file
- [ ] Saved `.env` file
- [ ] Restarted backend server
- [ ] Checked app - seeing real Instagram data!

---

## ⚠️ Troubleshooting

### "Still seeing mock data"
- ✅ Check that `.env` file is in: `C:\Users\Aryan\OneDrive\Rishab Fun Code\.env`
- ✅ Check variable names are exactly: `INSTAGRAM_ACCESS_TOKEN` and `INSTAGRAM_BUSINESS_ACCOUNT_ID`
- ✅ Check no extra spaces or quotes
- ✅ **Restart backend** after editing `.env`

### "Instagram API error" or "Invalid token"
- ✅ Make sure you used the **extended token** (60 days), not the short one
- ✅ Check that token hasn't expired
- ✅ Make sure Instagram account is **Business** type (not Personal)
- ✅ Regenerate token if needed

### "Can't find Instagram Account ID"
- ✅ Make sure you're logged into Facebook Business Settings
- ✅ Make sure Instagram is connected to your Facebook account
- ✅ Check that it's a Business account (convert in Instagram app if needed)

### "Token expired"
- ✅ Go back to Step 5 and extend the token again
- ✅ Or generate a new token in Graph API Explorer

---

## 🔄 When Token Expires (After 60 Days)

When your token expires after 60 days:

1. Go back to: **https://developers.facebook.com/tools/explorer/**
2. Select your app and Instagram account
3. Click **"Generate Access Token"**
4. Extend it again (Step 5)
5. Update `INSTAGRAM_ACCESS_TOKEN` in your `.env` file
6. Restart backend

---

## 🎯 That's It!

Once you complete these steps, you'll see **real Instagram analytics** in your app instead of mock data!

**Need help?** If you get stuck at any step, tell me which step number and what's happening, and I'll help you through it!
