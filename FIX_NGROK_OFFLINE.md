# 🔧 Fix: ngrok Endpoint is Offline

The error "The endpoint is offline" means either:
1. Your server isn't running
2. ngrok isn't running
3. Both need to be restarted

---

## ✅ Quick Fix

### Step 1: Make Sure Server is Running

**Open Terminal 1:**
```bash
cd "C:\Users\Aryan\OneDrive\Rishab Fun Code"
python run_app.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Keep this terminal open!** ✅

---

### Step 2: Start ngrok (in a NEW terminal)

**Open Terminal 2 (NEW terminal):**
```bash
ngrok http 8000
```

You should see:
```
Session Status                online
Forwarding                    https://abc123.ngrok.io -> http://localhost:8000
                                 ↑ This is your URL!
```

**Keep this terminal open too!** ✅

---

### Step 3: Verify It's Working

1. **Copy the HTTPS URL** from ngrok (e.g., `https://abc123.ngrok.io`)
2. **Test it in your browser:**
   - Go to: `https://YOUR-NGROK-URL.ngrok.io/api/agent/health`
   - You should see: `{"status":"healthy",...}`
   
   If you see the error page, ngrok or server isn't running correctly.

---

### Step 4: Update Google Apps Script

1. Open your Google Sheet
2. Click **"Extensions"** > **"Apps Script"**
3. Find: `const API_URL = 'http://localhost:8000/api/agent/command';`
4. Replace with: `const API_URL = 'https://YOUR-NGROK-URL.ngrok.io/api/agent/command';`
5. **Save** (Ctrl+S)

---

## ⚠️ Important: Both Must Be Running!

You need **TWO terminals** running:

**Terminal 1:**
```
python run_app.py
```
✅ Server running on port 8000

**Terminal 2:**
```
ngrok http 8000
```
✅ ngrok forwarding to localhost:8000

**If you close either terminal, it stops working!**

---

## 🔍 Troubleshooting

### Problem: "Server not running"
**Solution:**
- Make sure `python run_app.py` is running
- Check terminal 1 shows "Uvicorn running on http://0.0.0.0:8000"
- If not, start it!

### Problem: "ngrok not running"
**Solution:**
- Make sure `ngrok http 8000` is running
- Check terminal 2 shows "Forwarding https://..."
- If not, start it!

### Problem: "Still showing offline"
**Solution:**
1. Stop both (Ctrl+C in each terminal)
2. Start server first: `python run_app.py`
3. Wait 2 seconds
4. Start ngrok: `ngrok http 8000`
5. Copy the NEW ngrok URL
6. Update Google Apps Script with new URL
7. Test again

### Problem: "ngrok URL keeps changing"
**Solution:**
- This is normal for free ngrok
- Each time you restart ngrok, you get a new URL
- Update the API_URL in your script each time
- Or get a free ngrok account and reserve a domain

---

## ✅ Checklist

Before testing:
- [ ] Terminal 1: Server running (`python run_app.py`)
- [ ] Terminal 2: ngrok running (`ngrok http 8000`)
- [ ] Copied the HTTPS URL from ngrok
- [ ] Tested URL in browser (should show JSON)
- [ ] Updated API_URL in Google Apps Script
- [ ] Saved the script (Ctrl+S)
- [ ] Refreshed Google Sheet (F5)

---

**Do this and it will work!** 🎉
