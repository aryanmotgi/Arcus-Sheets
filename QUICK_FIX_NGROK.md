# ⚡ Quick Fix: "Failed to connect to API"

## 🎯 The Problem
Google Sheets can't access `localhost:8000` directly. You need **ngrok** to make your server accessible.

---

## 🚀 Fix in 2 Minutes

### 1️⃣ Start Your Server
```bash
python run_app.py
```
**Keep this running!** ✅

### 2️⃣ Start ngrok (in a NEW terminal)
```bash
ngrok http 8000
```
**Keep this running too!** ✅

### 3️⃣ Copy the HTTPS URL
From ngrok output, copy the HTTPS URL:
```
Forwarding    https://abc123.ngrok.io -> http://localhost:8000
                           ↑ Copy this!
```

### 4️⃣ Update Google Apps Script
1. Open Google Sheet → **Extensions** → **Apps Script**
2. Find: `const API_URL = 'http://localhost:8000/api/agent/command';`
3. Change to: `const API_URL = 'https://YOUR-NGROK-URL.ngrok.io/api/agent/command';`
4. **Save** (Ctrl+S)

### 5️⃣ Test It!
- Refresh Google Sheet (F5)
- Click **🤖 AI Agent** → **💬 Open Command Dialog**
- Type: `"show revenue"`
- Click **Execute**

---

## 📋 Keep Both Running!
- ✅ Terminal 1: `python run_app.py` 
- ✅ Terminal 2: `ngrok http 8000`

If you close either, it won't work!

---

## 🔧 Don't Have ngrok?
Download: https://ngrok.com/download
Extract and run: `ngrok.exe http 8000`

---

**That's it!** Try again - it should work now! 🎉
