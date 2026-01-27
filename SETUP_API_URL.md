# How to Set Up API_URL in Google Apps Script

## Problem
The ping button and all commands are not working because `API_URL` is not configured correctly.

## Solution: Update API_URL in Google Apps Script

### Step 1: Get Your Render URL
1. Go to your Render dashboard: https://dashboard.render.com
2. Click on your service
3. Copy the **Service URL** (e.g., `https://arcus-sheets-abc123.onrender.com`)

### Step 2: Update Google Apps Script
1. Open your Google Sheet
2. Click **Extensions** > **Apps Script**
3. Find this line at the top:
   ```javascript
   const API_URL = 'https://YOUR-APP-NAME.onrender.com/api/agent/command';
   ```
4. Replace `YOUR-APP-NAME.onrender.com` with your actual Render URL
   ```javascript
   const API_URL = 'https://arcus-sheets-abc123.onrender.com/api/agent/command';
   ```
5. **Important:** Make sure the URL ends with `/api/agent/command`
6. Click **Save** (Ctrl+S or Cmd+S)

### Step 3: Test the Connection
1. Go back to your Google Sheet
2. Click **🤖 AI Agent** > **🔍 Ping API (Debug)**
3. You should see "✅ Ping Success" if it works

## Troubleshooting

### Error: "API_URL not configured"
- **Fix:** Update the `API_URL` constant in Apps Script (see Step 2 above)

### Error: "Request timed out" or "502 Bad Gateway"
- **Cause:** Render free tier services sleep after 15 minutes of inactivity
- **Fix:** 
  1. Wait 30 seconds and try again (service needs to wake up)
  2. Or upgrade to a paid plan for always-on service

### Error: "404 Not Found"
- **Cause:** API_URL endpoint is wrong
- **Fix:** Make sure URL ends with `/api/agent/command`
  - ✅ Correct: `https://your-app.onrender.com/api/agent/command`
  - ❌ Wrong: `https://your-app.onrender.com`
  - ❌ Wrong: `https://your-app.onrender.com/api`

### Error: "Cannot resolve hostname"
- **Cause:** API_URL has a typo or wrong domain
- **Fix:** Double-check the Render URL in your dashboard

### Error: "Service not responding"
- **Cause:** Service might be down or not deployed
- **Fix:**
  1. Check Render dashboard - is service status "Live"?
  2. Check Render logs for errors
  3. Verify environment variables are set correctly

## How to View Apps Script Execution Logs

1. In Apps Script editor, click **Executions** (clock icon) in left sidebar
2. Click on a recent execution
3. View the logs to see:
   - API_URL being used
   - Request payload
   - Response code and body
   - Any errors

## Quick Test Commands

After setting up API_URL, test with:

1. **Ping:** `🤖 AI Agent` > `🔍 Ping API (Debug)`
2. **Simple command:** `🤖 AI Agent` > `💬 Open Command Dialog` > type "ping"
3. **Sync orders:** `🤖 AI Agent` > `🔄 Sync Orders`

## Example API_URL Formats

### Render (Production)
```javascript
const API_URL = 'https://arcus-sheets-abc123.onrender.com/api/agent/command';
```

### Ngrok (Local Testing)
```javascript
const API_URL = 'https://abc123.ngrok.io/api/agent/command';
```

### Localhost (Won't work from Google Sheets!)
```javascript
// ❌ This won't work - Google Sheets can't reach localhost
const API_URL = 'http://localhost:8000/api/agent/command';
```

## Next Steps

Once API_URL is configured:
1. ✅ Test ping button
2. ✅ Test a simple command
3. ✅ Run "sync orders"
4. ✅ Use the command dialog for other commands
