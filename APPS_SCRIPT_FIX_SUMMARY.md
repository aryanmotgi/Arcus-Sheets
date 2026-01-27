# Apps Script Dialog Fix Summary

## Problem
Commands from Google Sheets dialog were returning generic help message instead of executing. This indicated the Apps Script wasn't sending the request in the correct format.

## Root Cause
The Apps Script code was correct (`{ "command": "..." }`), but:
1. No logging to debug what was being sent/received
2. Response handling in dialog was too strict
3. Backend didn't accept fallback keys
4. No way to test connection

## Fixes Applied

### 1. Enhanced Apps Script (`GOOGLE_SHEETS_SCRIPT.js`)
- ✅ Added comprehensive logging (request payload, response code, response body)
- ✅ Added command validation (empty command check)
- ✅ Better error handling with detailed messages
- ✅ Added `pingApi()` function for testing
- ✅ Added "Ping API" menu item

### 2. Enhanced FastAPI Endpoint (`app/routers/ai_agent.py`)
- ✅ Accepts multiple key formats: `command`, `text`, `message`, `prompt`
- ✅ Primary key is `command` (required)
- ✅ Added request/response logging
- ✅ Better error handling
- ✅ Returns proper response format even on errors

### 3. Enhanced Dialog (`CommandDialog.html`)
- ✅ Better response parsing (handles multiple response formats)
- ✅ Added Ping button for testing
- ✅ Added console logging for debugging
- ✅ More robust error display

### 4. Added Ping Command (`src/ai_agent.py`)
- ✅ "ping" command returns simple success response
- ✅ Useful for testing API connection

## How to Use

### Step 1: Update Apps Script
1. Open Google Sheet
2. Extensions > Apps Script
3. Copy entire `GOOGLE_SHEETS_SCRIPT.js` file
4. Paste into `Code.gs` (or create new file)
5. Update `API_URL` on line 18:
   ```javascript
   const API_URL = 'https://your-render-url.onrender.com/api/agent/command';
   ```
6. Save (Ctrl+S)
7. Run `onOpen()` function to create menu

### Step 2: Update Dialog HTML
1. In Apps Script, open `CommandDialog.html`
2. Copy entire `CommandDialog.html` file
3. Paste into Apps Script
4. Save

### Step 3: Test Connection
1. In Google Sheet, click "🤖 AI Agent" > "🔍 Ping API (Debug)"
2. Check Apps Script Execution log (View > Execution log)
3. Should see:
   ```
   === API Request ===
   API_URL: https://...
   Command: ping
   Payload: {"command":"ping"}
   === API Response ===
   Response Code: 200
   Response Body: {"success":true,...}
   ```

### Step 4: Test Commands
1. Click "🤖 AI Agent" > "💬 Open Command Dialog"
2. Type: "sync orders"
3. Click "Execute Command"
4. Should see success message, not help list

## Debugging

### View Logs
1. Apps Script: View > Execution log
2. Backend: Check server logs (Render/Railway/etc)

### Common Issues

**Issue: "Failed to connect to API"**
- Check API_URL is correct
- Check server is running
- Check CORS settings

**Issue: "Empty command"**
- Check command input isn't empty
- Check Apps Script logs for actual payload

**Issue: "HTTP 404"**
- Check API_URL ends with `/api/agent/command`
- Check backend route is registered

**Issue: "HTTP 500"**
- Check backend logs for error
- Check environment variables are set

## Expected Request Format

```json
{
  "command": "sync orders"
}
```

## Expected Response Format

```json
{
  "success": true,
  "message": "✅ **Sync Complete!**\n\n...",
  "data": { ... },
  "command": "sync orders"
}
```

## Testing Checklist

- [ ] Apps Script code updated
- [ ] CommandDialog.html updated
- [ ] API_URL set correctly
- [ ] Ping API works
- [ ] "sync orders" executes
- [ ] "reset arcus ui apply" executes
- [ ] Logs show correct payload
- [ ] Response displays correctly
