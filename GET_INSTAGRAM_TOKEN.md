# 🔑 Get Instagram Access Token - Quick Guide

## Fastest Way:

### Option 1: Using Graph API Explorer (Easiest)

1. **Go to:** https://developers.facebook.com/tools/explorer/

2. **Select Your App:**
   - Top left dropdown → Select your app (or create one first)
   - If no app: Go to https://developers.facebook.com/ → Create App → Business → Add Instagram product

3. **Select Instagram Account:**
   - Second dropdown → Select your Instagram Business account

4. **Generate Token:**
   - Click **"Generate Access Token"** button
   - Approve permissions
   - **Copy the token**

5. **Extend Token (60 days):**
   - Go to: https://developers.facebook.com/tools/debug/accesstoken/
   - Paste token → Click **"Debug"**
   - Click **"Extend Access Token"**
   - **Copy the extended token**

6. **Add to .env:**
   ```env
   INSTAGRAM_ACCESS_TOKEN=your_extended_token_here
   ```

---

## What Your .env Should Have:

```env
INSTAGRAM_ACCESS_TOKEN=EAABwzLixZBT8BO7ZCZCHZC...your_token
INSTAGRAM_BUSINESS_ACCOUNT_ID=3474793
```

---

## Test It:

1. Save .env file
2. Restart backend: `python run_app.py`
3. Open app → Analytics → Instagram
4. Should see real data! ✅
