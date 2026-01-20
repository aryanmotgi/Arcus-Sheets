# 📝 Step-by-Step: Creating .env File & Getting Credentials

## Part 1: Create the .env File

### Step 1.1: Navigate to Your Project Folder
1. Open File Explorer
2. Go to: `C:\Users\Aryan\OneDrive\Rishab Fun Code`
3. You should see folders like `app`, `frontend`, `config`, etc.

### Step 1.2: Create the .env File
1. **Right-click** in the folder (not on any file)
2. Select **"New"** → **"Text Document"**
3. Name it exactly: `.env` (including the dot at the start)
   - If Windows asks if you're sure about the name, click **"Yes"**
   - If it shows as "Text Document" that's okay - we'll fix it

### Step 1.3: If You Can't See the .env File
- Windows might hide files starting with a dot
- In File Explorer, click the **"View"** tab
- Check the box for **"Hidden items"**
- Now you should see your `.env` file

---

## Part 2: Get Instagram Credentials

Since you already have a Business Instagram account, let's get the credentials:

### Step 2.1: Get Instagram Business Account ID

1. **Open Facebook Business Manager:**
   - Go to: https://business.facebook.com/settings
   - Log in with your Facebook account (the one connected to your Instagram Business account)

2. **Find Your Instagram Account:**
   - Click **"Instagram Accounts"** in the left menu
   - You should see your Instagram account listed
   - **Click on it**

3. **Copy the Account ID:**
   - Look for **"Instagram Account ID"** or **"Account ID"**
   - It's a long number (like: `17841405309211834`)
   - **Copy this number** - you'll need it later

### Step 2.2: Create Facebook App & Get Access Token

1. **Go to Facebook Developers:**
   - Visit: https://developers.facebook.com/
   - Log in with your Facebook account

2. **Create a New App:**
   - Click **"My Apps"** button (top right)
   - Click **"Create App"**
   - Select **"Business"** type
   - Click **"Next"**

3. **Fill in App Details:**
   - **App Name:** `Arcus Analytics` (or any name you want)
   - **App Contact Email:** Your email
   - Click **"Create App"**

4. **Add Instagram Product:**
   - In your app dashboard, find **"Add Product"** or the **"Products"** section
   - Look for **"Instagram"** and click **"Set Up"**
   - It might ask you to select use case - choose **"Other"** or **"Analytics"**

5. **Connect Your Instagram Account:**
   - It should show your Instagram Business account
   - Click to connect/link it to the app

6. **Get Access Token:**
   - Go to: https://developers.facebook.com/tools/explorer/
   - At the top, select your app from the dropdown (next to "Meta App")
   - In the "User or Page" dropdown, select your Instagram Business account
   - Click the **"Generate Access Token"** button
   - It might ask for permissions - click **"Continue"** and **"OK"**
   - **Copy the token** that appears (it's a long string like `EAABwzLix...`)

### Step 2.3: Make Token Long-Lived (Recommended)

The token you got expires in 1-2 hours. Let's make it last 60 days:

1. Go to: https://developers.facebook.com/tools/debug/accesstoken/
2. Paste your token in the "Access Token" field
3. Click **"Debug"**
4. Click **"Extend Access Token"** button
5. Copy the new token (this one lasts 60 days)

---

## Part 3: Get TikTok Credentials

Since you already have a TikTok account, let's get the API credentials:

### Step 3.1: Apply for TikTok Business API Access

1. **Go to TikTok Developers:**
   - Visit: https://developers.tiktok.com/
   - Click **"Get Started"** or **"Log In"**
   - Log in with your TikTok Business account

2. **Apply for Access:**
   - Click **"Apply for Access"** or **"Create App"**
   - Fill out the application:
     - **App Name:** `Arcus Analytics`
     - **App Type:** Select **"Web App"** or **"Server-side App"**
     - **Use Case:** Select **"Analytics"** or **"Other"**
     - **Description:** "Internal analytics dashboard for tracking social media metrics"
     - **Business Information:** Fill in your details
   - Click **"Submit"**

3. **Wait for Approval:**
   - Approval can take 1-7 days
   - You'll get an email when approved

### Step 3.2: Create App & Get Credentials (After Approval)

Once you're approved:

1. **Log back into TikTok Developers:**
   - Go to: https://developers.tiktok.com/
   - You should see your app listed

2. **Get Your Credentials:**
   - Click on your app
   - Go to **"App Info"** or **"Basic Information"**
   - You'll see:
     - **Client Key** (this is your App ID)
     - **Client Secret** 
   - **Copy both of these**

3. **Generate Access Token:**
   - Go to **"Auth"** or **"Access Token"** section
   - Click **"Generate Token"** or follow the OAuth flow
   - For server-side apps, you might use **"Client Credentials"** flow
   - Copy the **Access Token**

---

## Part 4: Fill in the .env File

Now let's put everything together:

### Step 4.1: Open the .env File

1. **Right-click** on the `.env` file
2. Select **"Open with"** → **"Notepad"** (or any text editor)
3. The file will be empty (that's okay)

### Step 4.2: Copy This Template

Copy and paste this into your `.env` file:

```env
# Instagram API Credentials
INSTAGRAM_ACCESS_TOKEN=PASTE_YOUR_INSTAGRAM_TOKEN_HERE
INSTAGRAM_BUSINESS_ACCOUNT_ID=PASTE_YOUR_INSTAGRAM_ACCOUNT_ID_HERE

# TikTok API Credentials  
TIKTOK_CLIENT_KEY=PASTE_YOUR_TIKTOK_CLIENT_KEY_HERE
TIKTOK_CLIENT_SECRET=PASTE_YOUR_TIKTOK_CLIENT_SECRET_HERE
TIKTOK_ACCESS_TOKEN=PASTE_YOUR_TIKTOK_ACCESS_TOKEN_HERE
```

### Step 4.3: Replace the Placeholders

Replace each `PASTE_YOUR_..._HERE` with your actual credentials:

**Example:**
```env
# Instagram API Credentials
INSTAGRAM_ACCESS_TOKEN=EAABwzLixZBT8BO7ZCZCHZC...your_actual_token
INSTAGRAM_BUSINESS_ACCOUNT_ID=17841405309211834

# TikTok API Credentials
TIKTOK_CLIENT_KEY=awabcdef123456789
TIKTOK_CLIENT_SECRET=xyz789abc123def456ghi
TIKTOK_ACCESS_TOKEN=act.abc123def456ghi789jkl012
```

**Important:**
- **NO spaces** around the `=` sign
- **NO quotes** around the values
- Keep each value on one line
- Don't add any extra blank lines at the top

### Step 4.4: Save the File

1. Press **Ctrl + S** to save
2. Close Notepad

---

## Part 5: Test It Works

### Step 5.1: Restart Your Backend Server

1. If your backend is running, **stop it** (press Ctrl+C)
2. Start it again:
   ```bash
   python run_app.py
   ```

### Step 5.2: Check the App

1. Open your app in the browser: `http://localhost:8080`
2. Go to **Analytics** section
3. Check Instagram and TikTok cards
4. If credentials are working, you'll see **real data** (not mock data)
5. If not working, you'll see a message about mock data or an error

---

## ⚠️ Troubleshooting

### "Still seeing mock data"
- Check that `.env` file is in the correct location (project root)
- Check that variable names are exactly correct (case-sensitive)
- Check that there are no extra spaces or quotes
- Restart the backend server after editing `.env`

### "Instagram API error"
- Make sure your Instagram account is a **Business** account (not Personal)
- Make sure you generated a **long-lived token** (60 days)
- Check that the token hasn't expired

### "TikTok API error"  
- Make sure you've been **approved** for API access
- Check that you're using the correct credentials
- Make sure your access token is still valid

### "Can't find .env file"
- Make sure you created it in the **project root** folder
- Check **"View" → "Hidden items"** in File Explorer
- The file should be at: `C:\Users\Aryan\OneDrive\Rishab Fun Code\.env`

---

## ✅ Quick Checklist

- [ ] Created `.env` file in project root
- [ ] Got Instagram Business Account ID
- [ ] Created Facebook App
- [ ] Got Instagram Access Token (long-lived)
- [ ] Applied for TikTok API access
- [ ] Got TikTok Client Key, Client Secret, and Access Token
- [ ] Filled in `.env` file with all credentials
- [ ] Saved `.env` file
- [ ] Restarted backend server
- [ ] Tested in app - seeing real data!

---

**Need help?** If you get stuck at any step, let me know which step and what error you see!
