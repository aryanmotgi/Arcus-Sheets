# 🔧 Fix: "Failed to connect to API" Error

Your Google Sheets script can't access `localhost` directly. You need to use **ngrok** to expose your local server.

---

## 🚀 Quick Fix (3 Steps)

### Step 1: Start Your Server
Open a terminal and run:
```bash
python run_app.py
```
Keep this terminal open! You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 2: Start ngrok
**Option A: If you have ngrok installed:**
1. Open a **new terminal** (keep the server running!)
2. Run:
   ```bash
   ngrok http 8000
   ```

**Option B: If you don't have ngrok:**
1. Download ngrok: https://ngrok.com/download
2. Extract the zip file
3. Open a **new terminal** in the ngrok folder
4. Run:
   ```bash
   ngrok.exe http 8000
   ```
   (Or just double-click ngrok.exe and type: `http 8000`)

### Step 3: Copy the ngrok URL
After starting ngrok, you'll see something like:
```
Forwarding    https://abc123.ngrok.io -> http://localhost:8000
```
Copy the **HTTPS URL** (e.g., `https://abc123.ngrok.io`)

---

## 📝 Update Your Google Apps Script

### Step 1: Open Apps Script
1. Go to your Google Sheet
2. Click **"Extensions"** > **"Apps Script"**

### Step 2: Update API_URL
1. Find this line in your script:
   ```javascript
   const API_URL = 'http://localhost:8000/api/agent/command';
   ```

2. Replace it with your ngrok URL:
   ```javascript
   const API_URL = 'https://abc123.ngrok.io/api/agent/command';
   ```
   (Use YOUR ngrok URL, not this example!)

3. **Save** (Ctrl+S)

### Step 3: Test It!
1. Go back to your Google Sheet
2. Click **"🤖 AI Agent"** > **"💬 Open Command Dialog"**
3. Type: `"show revenue"`
4. Click **"Execute Command"**
5. It should work now! ✅

---

## ⚠️ Important Notes

### Keep Both Running!
- ✅ **Terminal 1**: Keep `python run_app.py` running
- ✅ **Terminal 2**: Keep `ngrok http 8000` running

If you close either one, the connection will break!

### ngrok URL Changes
- Free ngrok gives you a **random URL** each time
- Every time you restart ngrok, you'll get a new URL
- **You need to update the API_URL in your script each time**

### Permanent Solution (Optional)
If you want a permanent URL:
1. Sign up for free ngrok account: https://dashboard.ngrok.com/signup
2. Get your authtoken
3. Run: `ngrok config add-authtoken YOUR_TOKEN`
4. Get a reserved domain in ngrok dashboard
5. Use that domain in your script (it won't change!)

---

## 🔍 Troubleshooting

### Problem: "ngrok is not recognized"
**Solution:**
- Download ngrok: https://ngrok.com/download
- Extract and use full path: `C:\path\to\ngrok.exe http 8000`

### Problem: "Address already in use"
**Solution:**
- Port 8000 is already in use
- Stop other programs using port 8000
- Or change your server port in `run_app.py` to something else (e.g., 8001)

### Problem: "Still can't connect"
**Solution:**
1. Make sure server is running: `python run_app.py`
2. Make sure ngrok is running: `ngrok http 8000`
3. Check ngrok URL is correct (use HTTPS, not HTTP)
4. Update API_URL in Apps Script with the correct URL
5. Save and try again

### Problem: "ngrok URL changes every time"
**Solution:**
- This is normal for free ngrok
- Update the API_URL each time you restart ngrok
- Or get a reserved domain (see above)

---

## ✅ Quick Checklist

Before testing:
- [ ] Server is running (`python run_app.py`)
- [ ] ngrok is running (`ngrok http 8000`)
- [ ] Copied the HTTPS URL from ngrok
- [ ] Updated API_URL in Apps Script
- [ ] Saved the script (Ctrl+S)
- [ ] Refreshed Google Sheet (F5)

---

**Now try again!** The error should be fixed. 🎉
