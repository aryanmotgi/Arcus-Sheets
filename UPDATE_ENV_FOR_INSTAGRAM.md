# 📝 Update Your .env File for Instagram

## Step 1: Open Your .env File

1. Go to: `C:\Users\Aryan\OneDrive\Rishab Fun Code`
2. **Right-click** on `.env` file
3. Select **"Open with"** → **"Notepad"**

## Step 2: Update Instagram Account ID

You said your Instagram user ID is `3474793`. 

**However**, for Instagram Graph API, we need the **Instagram Business Account ID** which is usually a longer number (like `17841405309211834`).

Let's try with your ID first, but if it doesn't work, we'll get the correct one.

**Update this line in your .env file:**
```env
INSTAGRAM_BUSINESS_ACCOUNT_ID=3474793
```

## Step 3: Get Your Access Token

### Quick Steps:
1. Go to: **https://developers.facebook.com/tools/explorer/**
2. If you don't have an app yet:
   - Go to: **https://developers.facebook.com/**
   - Click **"My Apps"** → **"Create App"** → Choose **"Business"**
   - Add **"Instagram"** product
   - Connect your Instagram account

3. In Graph API Explorer:
   - Select your app from the dropdown (top left)
   - Select your Instagram account from the second dropdown
   - Click **"Generate Access Token"**
   - Check permissions: `instagram_basic`, `instagram_manage_insights`
   - Click **"Generate"**
   - **Copy the token**

4. **Extend the token** (make it last 60 days):
   - Go to: **https://developers.facebook.com/tools/debug/accesstoken/**
   - Paste your token
   - Click **"Debug"**
   - Click **"Extend Access Token"**
   - **Copy the new extended token**

## Step 4: Add Token to .env File

Update this line in your .env file:
```env
INSTAGRAM_ACCESS_TOKEN=paste_your_extended_token_here
```

Replace `paste_your_extended_token_here` with your actual token.

## Step 5: Final .env File Should Look Like:

```env
# Instagram API Credentials
INSTAGRAM_ACCESS_TOKEN=EAABwzLixZBT8BO7ZCZCHZC...your_full_token_here
INSTAGRAM_BUSINESS_ACCOUNT_ID=3474793

# TikTok API Credentials (leave these for now)
TIKTOK_CLIENT_KEY=your_tiktok_client_key_here
TIKTOK_CLIENT_SECRET=your_tiktok_client_secret_here
TIKTOK_ACCESS_TOKEN=your_tiktok_access_token_here
```

## Step 6: Save and Test

1. **Save** the file (Ctrl+S)
2. **Close** Notepad
3. **Restart** your backend:
   ```bash
   python run_app.py
   ```
4. **Check** your app: `http://localhost:8080` → Analytics → Instagram

---

## ⚠️ If Account ID Doesn't Work

If you get an error about the account ID, we need to get the correct Business Account ID:

1. Go to: **https://business.facebook.com/settings**
2. Click **"Instagram Accounts"** (left menu)
3. Click on your Instagram account
4. Look for **"Instagram Account ID"** or **"Account ID"**
5. Copy that number (it's usually much longer, like `17841405309211834`)
6. Update `INSTAGRAM_BUSINESS_ACCOUNT_ID` in your .env file with that number

---

**Once you add the access token, the app will automatically use real Instagram data!**
