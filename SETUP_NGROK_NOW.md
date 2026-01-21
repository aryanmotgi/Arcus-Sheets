# 🔧 Fix the Connection Error - Set Up ngrok NOW

Your server is running ✅, but Google Apps Script **cannot access localhost**. You MUST use ngrok.

---

## 🚀 Quick Setup (5 Minutes)

### Step 1: Download ngrok
1. Go to: https://ngrok.com/download
2. Download the Windows version
3. Extract the zip file (you'll get `ngrok.exe`)

### Step 2: Start ngrok
1. **Open a NEW terminal** (keep your server running!)
2. Navigate to where you extracted ngrok, OR:
   - Put `ngrok.exe` in your project folder
   - Or use the full path

3. Run this command:
   ```bash
   ngrok http 8000
   ```
   
   Or if ngrok is in a different folder:
   ```bash
   C:\path\to\ngrok.exe http 8000
   ```

### Step 3: Copy the HTTPS URL
After running ngrok, you'll see:
```
Session Status                online
Account                       (Plan: Free)
Version                       3.x.x
Region                        United States (us)
Latency                       -
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123.ngrok.io -> http://localhost:8000
                                 ↑ COPY THIS URL!
```

**Copy the HTTPS URL** (e.g., `https://abc123.ngrok.io`)

### Step 4: Update Google Apps Script
1. Open your Google Sheet
2. Click **"Extensions"** > **"Apps Script"**
3. Find this line (around line 18):
   ```javascript
   const API_URL = 'http://localhost:8000/api/agent/command';
   ```
4. **Replace it** with:
   ```javascript
   const API_URL = 'https://YOUR-NGROK-URL.ngrok.io/api/agent/command';
   ```
   (Replace `YOUR-NGROK-URL` with the actual URL from ngrok!)

5. **Save** (Ctrl+S)

### Step 5: Test It!
1. Go back to your Google Sheet
2. Refresh (F5)
3. Click **"🤖 AI Agent"** > **"💬 Open Command Dialog"**
4. Type: `"show revenue"`
5. Click **"Execute Command"**
6. It should work! ✅

---

## ⚠️ IMPORTANT: Keep Both Running!

You need **TWO terminals** running at the same time:

**Terminal 1:** (Your server)
```bash
python run_app.py
```
✅ Keep this running!

**Terminal 2:** (ngrok)
```bash
ngrok http 8000
```
✅ Keep this running too!

**If you close either one, it won't work!**

---

## 🔍 Verify ngrok is Working

1. Open your browser
2. Go to: `http://127.0.0.1:4040` (ngrok web interface)
3. You should see requests coming through when you use the dialog

Or test the ngrok URL directly:
- Open: `https://YOUR-NGROK-URL.ngrok.io/api/agent/health`
- You should see: `{"status":"healthy",...}`

---

## 🆘 Troubleshooting

### Problem: "ngrok is not recognized"
**Solution:**
- Use the full path: `C:\path\to\ngrok.exe http 8000`
- Or add ngrok to your PATH
- Or put `ngrok.exe` in your project folder

### Problem: "Address already in use"
**Solution:**
- Something else is using port 8000
- Stop other programs
- Or change your server port

### Problem: "Still getting error after ngrok"
**Solution:**
1. Make sure ngrok is running (check terminal)
2. Make sure you copied the HTTPS URL (not HTTP)
3. Make sure you updated API_URL in Apps Script
4. Make sure you saved the script (Ctrl+S)
5. Refresh Google Sheet (F5)

### Problem: "ngrok URL changes every time"
**Solution:**
- This is normal for free ngrok
- Update API_URL each time you restart ngrok
- Or get a free ngrok account and reserve a domain

---

## ✅ Checklist

Before testing:
- [ ] Downloaded ngrok
- [ ] Started ngrok: `ngrok http 8000`
- [ ] Copied the HTTPS URL from ngrok
- [ ] Updated API_URL in Google Apps Script
- [ ] Saved the script (Ctrl+S)
- [ ] Both server and ngrok are running
- [ ] Refreshed Google Sheet (F5)

---

**Do this now and the error will be fixed!** 🎉
