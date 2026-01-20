# 📱 Instagram & TikTok API Setup Guide

This guide will help you connect your Instagram and TikTok accounts to get real analytics data in your Arcus app.

## 🔵 Instagram Setup (Instagram Graph API)

### Step 1: Create Facebook App
1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Click **"My Apps"** → **"Create App"**
3. Choose **"Business"** as the app type
4. Fill in app details:
   - App Name: "Arcus Analytics"
   - Contact Email: Your email
5. Click **"Create App"**

### Step 2: Add Instagram Product
1. In your app dashboard, click **"Add Product"**
2. Find **"Instagram"** and click **"Set Up"**
3. You'll need an **Instagram Business Account** (not personal)

### Step 3: Get Instagram Business Account ID
1. Go to [Facebook Business Settings](https://business.facebook.com/settings)
2. Click **"Instagram Accounts"** in the left menu
3. Find your Instagram account and copy the **Instagram Business Account ID**

### Step 4: Get Access Token
1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app from the dropdown
3. Add these permissions:
   - `instagram_basic`
   - `instagram_manage_insights`
   - `pages_read_engagement`
   - `pages_read_user_content`
4. Click **"Generate Access Token"**
5. Copy the token (it's temporary - you'll need to make it permanent)

### Step 5: Make Token Permanent (Optional but Recommended)
1. Go to your app dashboard → **"Tools"** → **"Graph API Explorer"**
2. Generate a long-lived token (60 days) or use **App Review** for permanent access
3. For production, you'll need to submit for App Review

### Step 6: Add to Your App
Create a `.env` file in your project root:
```env
INSTAGRAM_ACCESS_TOKEN=your_access_token_here
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_instagram_account_id_here
```

## 🎵 TikTok Setup (TikTok Business API)

### Step 1: Create TikTok Business Account
1. Go to [TikTok Business](https://www.tiktok.com/business/)
2. Sign up or log in with your business account
3. Complete business verification if required

### Step 2: Apply for TikTok Business API Access
1. Go to [TikTok Developers](https://developers.tiktok.com/)
2. Click **"Get Started"** or **"Apply for Access"**
3. Fill out the application form:
   - Business information
   - Use case: "Analytics dashboard for internal use"
   - Expected API usage
4. Wait for approval (can take a few days to weeks)

### Step 3: Create App in TikTok Developer Portal
1. Once approved, go to [TikTok Developer Portal](https://developers.tiktok.com/)
2. Click **"Create App"**
3. Fill in app details:
   - App Name: "Arcus Analytics"
   - App Category: "Business"
   - Description: "Internal analytics dashboard"
4. Select scopes/permissions:
   - `user.info.basic`
   - `video.list`
   - `video.insights`
   - `analytics.basic`

### Step 4: Get API Credentials
1. After creating the app, you'll get:
   - **Client Key** (App ID)
   - **Client Secret**
2. You'll need to generate an **Access Token** using OAuth 2.0

### Step 5: Generate Access Token
1. Use TikTok's OAuth flow to get user authorization
2. Exchange authorization code for access token
3. Or use **Client Credentials** flow for server-to-server access

### Step 6: Add to Your App
Add to your `.env` file:
```env
TIKTOK_CLIENT_KEY=your_client_key_here
TIKTOK_CLIENT_SECRET=your_client_secret_here
TIKTOK_ACCESS_TOKEN=your_access_token_here
```

## 🔧 Update Your Code

### Option 1: Environment Variables (Recommended)
Create a `.env` file in your project root:
```env
INSTAGRAM_ACCESS_TOKEN=your_instagram_token
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_instagram_account_id
TIKTOK_CLIENT_KEY=your_tiktok_client_key
TIKTOK_CLIENT_SECRET=your_tiktok_client_secret
TIKTOK_ACCESS_TOKEN=your_tiktok_token
```

### Option 2: Update config.yaml
Add to `config/config.yaml`:
```yaml
social_media:
  instagram:
    access_token: "your_token_here"
    business_account_id: "your_account_id_here"
  tiktok:
    client_key: "your_client_key"
    client_secret: "your_client_secret"
    access_token: "your_token"
```

## 📝 Quick Start Checklist

### Instagram:
- [ ] Facebook Developer account created
- [ ] Facebook App created
- [ ] Instagram product added
- [ ] Instagram Business Account connected
- [ ] Access token generated
- [ ] Token added to `.env` file

### TikTok:
- [ ] TikTok Business account created
- [ ] API access application submitted
- [ ] API access approved
- [ ] App created in Developer Portal
- [ ] Credentials obtained
- [ ] Access token generated
- [ ] Credentials added to `.env` file

## ⚠️ Important Notes

1. **Instagram**: Requires Instagram Business or Creator account (not personal)
2. **TikTok**: API access requires approval - not instant
3. **Tokens Expire**: Instagram tokens expire after 60 days (unless permanent)
4. **Rate Limits**: Both APIs have rate limits - be mindful of requests
5. **Privacy**: Keep your tokens secret - never commit them to git

## 🧪 Testing

Once you've added your credentials:
1. Restart your backend server
2. Go to the app and check Analytics
3. You should see real data instead of mock data

## 🔄 If You Don't Have Access Yet

The app will continue to work with mock data until you:
- Get API access approved
- Add your credentials
- The code will automatically switch to real data when credentials are available

## 📚 Resources

- [Instagram Graph API Docs](https://developers.facebook.com/docs/instagram-api)
- [TikTok Business API Docs](https://developers.tiktok.com/doc/)
- [Facebook Graph API Explorer](https://developers.facebook.com/tools/explorer/)
