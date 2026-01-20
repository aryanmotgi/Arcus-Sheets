# 🔧 Troubleshooting Guide

## Problem: White Screen / Page Not Loading

### Step 1: Check if Backend is Running

Open a new terminal and run:
```bash
python run_app.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**If you see an error**, make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Step 2: Check if Frontend Server is Running

Open another terminal and run:
```bash
cd frontend
python -m http.server 8080
```

You should see:
```
Serving HTTP on 0.0.0.0 port 8080
```

### Step 3: Test Backend Connection

Open your browser and go to:
```
http://localhost:8000/api/health
```

You should see:
```json
{"status":"healthy","timestamp":"..."}
```

**If this doesn't work**, the backend isn't running correctly.

### Step 4: Test Frontend Connection

Open your browser and go to:
```
http://localhost:8080/test.html
```

This will test all connections and show you what's working.

### Step 5: Check Browser Console

1. Open the browser developer tools (F12)
2. Go to the "Console" tab
3. Look for any red error messages
4. Share those errors - they'll tell us what's wrong

### Step 6: Clear Service Worker Cache

If you see a white screen, the service worker might be caching a broken page.

**In your browser:**
1. Open Developer Tools (F12)
2. Go to "Application" tab (Chrome) or "Storage" tab (Firefox)
3. Find "Service Workers" on the left
4. Click "Unregister" for any service workers
5. Go to "Cache Storage" and delete all caches
6. Refresh the page (Ctrl+F5 or Cmd+Shift+R)

### Step 7: Check Firewall

Windows Firewall might be blocking ports 8000 and 8080.

**To allow them:**
1. Open Windows Defender Firewall
2. Click "Advanced settings"
3. Click "Inbound Rules" → "New Rule"
4. Select "Port" → Next
5. Select "TCP" and enter port "8000" → Next
6. Select "Allow the connection" → Next
7. Check all profiles → Next
8. Name it "Arcus Backend" → Finish
9. Repeat for port 8080 (name it "Arcus Frontend")

### Step 8: Test from Phone

1. Make sure both servers are running on your computer
2. Make sure phone is on the same WiFi network
3. Try accessing: `http://192.168.1.242:8080/test.html` from your phone
4. This will test if the connection works

## Common Issues:

### ❌ "Connection refused"
- Backend server is not running
- Port 8000 is blocked by firewall
- Wrong IP address

### ❌ "404 Not Found"
- Frontend server is not running
- Wrong URL path
- Files are in the wrong location

### ❌ "CORS error"
- Backend CORS settings are correct, but check if backend is actually running
- Try accessing backend directly: `http://192.168.1.242:8000/api/health`

### ❌ "Failed to fetch"
- Backend server is not running
- Wrong API URL in app.js
- Network connection issue

## Quick Fix Checklist:

- [ ] Backend server running? (`python run_app.py`)
- [ ] Frontend server running? (`cd frontend && python -m http.server 8080`)
- [ ] Backend health check works? (`http://localhost:8000/api/health`)
- [ ] Test page works? (`http://localhost:8080/test.html`)
- [ ] Firewall allows ports 8000 and 8080?
- [ ] Phone on same WiFi network?
- [ ] Service worker cache cleared?
- [ ] Browser console checked for errors?

## Still Not Working?

1. Open the test page: `http://localhost:8080/test.html`
2. Take a screenshot of the results
3. Check browser console for errors (F12 → Console tab)
4. Share the error messages you see

This will help identify the exact problem!

