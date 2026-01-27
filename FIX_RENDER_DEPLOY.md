# 🔧 Fix Render Deployment Failure

**Your Render deploy failed. Here's how to fix it:**

---

## Step 1: Check the Logs

1. **In Render dashboard**, click **"Logs"** (in the left sidebar under MONITOR)
2. **Look for error messages** - usually red text at the bottom
3. **Copy the error** and we can fix it

---

## Common Errors & Fixes

### Error: "No module named 'app'"
**Fix:** Check your Start Command:
- Should be: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Error: "ModuleNotFoundError: No module named 'gspread'"
**Fix:** Check your Build Command:
- Should be: `pip install -r requirements.txt`

### Error: "Port already in use" or "Port binding failed"
**Fix:** Make sure Start Command uses `$PORT`:
- Should be: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Error: "Failed to find credentials"
**Fix:** You need to add environment variables in Render

---

## Step 2: Check Your Render Settings

1. Go to **"Settings"** in Render dashboard
2. Verify:

   **Build Command:**
   ```
   pip install -r requirements.txt
   ```

   **Start Command:**
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

---

## Step 3: Add Environment Variables

Your app needs these in Render:

1. Go to **"Environment"** tab in Render
2. Add these variables:

   ```
   GOOGLE_SHEETS_SPREADSHEET_ID=1wK6aA1Sny5Ie3Ef8gU8LMgaBMjpNKW7ol1pxVWmGihE
   
   SHOPIFY_STORE_URL=https://arcuswear.myshopify.com
   
   SHOPIFY_CLIENT_ID=7625899de2923f2831fe57d1fafc71b3
   
   SHOPIFY_CLIENT_SECRET=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
   ```

   **For Google credentials:**
   - Open `credentials/service_account.json` locally
   - Copy ALL the JSON content
   - In Render, add: `GOOGLE_CREDENTIALS`
   - Value: Paste the entire JSON

3. **Save** - Render will automatically redeploy

---

## Quick Fix Checklist

- [ ] Check Logs for specific error
- [ ] Verify Build Command: `pip install -r requirements.txt`
- [ ] Verify Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] Add all environment variables
- [ ] Click "Manual Deploy" to retry

---

**What does the Logs section show? Share the error and I'll help fix it!**
