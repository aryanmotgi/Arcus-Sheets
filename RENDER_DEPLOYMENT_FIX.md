# Render Deployment Fix - Server Binding

## Problem
Google Sheets cannot reach Render backend - all commands hang. This indicates the FastAPI app isn't responding on Render.

## Root Cause
The server must bind to:
- **Host:** `0.0.0.0` (not `localhost` or `127.0.0.1`)
- **Port:** `$PORT` environment variable (Render sets this dynamically)

## Fixes Applied

### 1. Updated `run_app.py`
- ✅ Uses `PORT` environment variable (defaults to 8000 for local)
- ✅ Binds to `0.0.0.0` (required for Render)
- ✅ Disables reload in production
- ✅ Added startup logging

### 2. Verified `Procfile`
- ✅ Already correct: `web: uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- ✅ This is what Render uses to start the service

### 3. Enhanced Health Checks
- ✅ Added `/api/health` endpoint (used by Render)
- ✅ Added `/health` endpoint (simple check)
- ✅ Health checks work even if agent initialization fails

### 4. Improved Error Handling
- ✅ Agent initialization is lazy (only when needed)
- ✅ Health checks don't require agent
- ✅ Better logging for debugging

## Render Configuration Checklist

### In Render Dashboard:

1. **Service Settings:**
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - ✅ Should match Procfile exactly

2. **Environment Variables:**
   - `PORT` - Automatically set by Render (don't set manually)
   - `GOOGLE_CREDENTIALS` - Your service account JSON
   - `GOOGLE_SHEETS_SPREADSHEET_ID` - Your spreadsheet ID
   - `SHOPIFY_STORE_URL` - Your Shopify store URL
   - `SHOPIFY_CLIENT_ID` - Shopify client ID
   - `SHOPIFY_CLIENT_SECRET` - Shopify client secret

3. **Build Settings:**
   - **Build Command:** (leave empty or `pip install -r requirements.txt`)
   - **Python Version:** 3.11 or 3.12

## Testing

### 1. Test Health Endpoint
```bash
curl https://your-render-url.onrender.com/api/health
```

Should return:
```json
{
  "status": "healthy",
  "timestamp": "...",
  "service": "Arcus Analytics & Task Management API"
}
```

### 2. Test Root Endpoint
```bash
curl https://your-render-url.onrender.com/api/agent/health
```

Should return agent health status.

### 3. Test Command Endpoint
```bash
curl -X POST https://your-render-url.onrender.com/api/agent/command \
  -H "Content-Type: application/json" \
  -d '{"command": "ping"}'
```

Should return:
```json
{
  "success": true,
  "message": "✅ **Ping Successful!**...",
  "data": {...}
}
```

## Common Issues

### Issue: "Service not responding"
**Check:**
1. Render logs show server starting
2. Start command is correct
3. No errors in build logs
4. Environment variables are set

### Issue: "Connection timeout"
**Check:**
1. Service is actually running (check Render dashboard)
2. URL is correct (no typos)
3. Service isn't sleeping (free tier sleeps after inactivity)

### Issue: "502 Bad Gateway"
**Check:**
1. Server is binding to `0.0.0.0` (not localhost)
2. Port is using `$PORT` (not hardcoded)
3. Procfile is correct

## Verification Steps

1. ✅ Procfile exists: `web: uvicorn app.main:app --host 0.0.0.0 --port $PORT`
2. ✅ `run_app.py` uses `PORT` env var
3. ✅ Health endpoints work
4. ✅ Command endpoint responds
5. ✅ Google Sheets can reach the API

## After Deployment

1. **Update Apps Script API_URL:**
   ```javascript
   const API_URL = 'https://your-render-url.onrender.com/api/agent/command';
   ```

2. **Test from Google Sheets:**
   - Click "🤖 AI Agent" > "🔍 Ping API (Debug)"
   - Should see success message
   - Check Apps Script Execution log for request/response

3. **Test Commands:**
   - "sync orders"
   - "reset arcus ui apply"
   - Should execute and return results

## Files Changed

- ✅ `run_app.py` - Uses PORT env var, binds to 0.0.0.0
- ✅ `app/main.py` - Added startup logging, better health checks
- ✅ `app/routers/ai_agent.py` - Lazy agent initialization, better error handling
- ✅ `Procfile` - Already correct (verified)
