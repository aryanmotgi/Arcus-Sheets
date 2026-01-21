# 🚀 Google Sheets AI Agent - Setup Guide

**Copy this entire document into a Google Doc for easy reference!**

---

## 📋 Quick Setup (3 Steps)

### Step 1: Start Server & ngrok

1. **Double-click:** `start_server_and_ngrok.bat`
2. **Wait for:**
   - ✅ Server running on `http://localhost:8000`
   - ✅ ngrok showing URL like `https://abc123.ngrok.io`
3. **Copy the ngrok HTTPS URL** (the `https://` one)

---

### Step 2: Update Google Apps Script

1. Open your Google Sheet
2. Go to **Extensions → Apps Script**
3. Find this line (around line 18):
   ```javascript
   const API_URL = 'http://localhost:8000/api/agent/command';
   ```
4. Replace with:
   ```javascript
   const API_URL = 'https://YOUR_NGROK_URL/api/agent/command';
   ```
   (Replace `YOUR_NGROK_URL` with the URL you copied from Step 1)
5. **Save** (Ctrl+S or Cmd+S)

---

### Step 3: Update Dialog HTML (One Time Only)

1. In Apps Script, click **+ (Add file)** → **HTML** → Name it **"CommandDialog"**
2. Open `FIXED_COMMAND_DIALOG.html` in your editor
3. **Copy ALL the content**
4. **Paste** into the `CommandDialog.html` file in Apps Script
5. **Save** (Ctrl+S or Cmd+S)

---

## 🎉 Use the Agent!

1. **Refresh your Google Sheet**
2. You'll see a new menu: **"🤖 AI Agent"**
3. Click **"AI Agent → Open Command Dialog"**
4. Type commands like:
   - `"fix net profit function"`
   - `"show change log"`
   - `"swap shipping cost with PSL"`

---

## ⚠️ Important Notes

- **Keep the terminal window open** (don't close it)
- **If ngrok URL changes**, update it in Apps Script
- **Each time you restart**, you'll need to update the ngrok URL

---

## 🔧 Troubleshooting

### "Failed to connect to API"
- Make sure server is running
- Check ngrok URL is correct in Apps Script
- Make sure ngrok URL is HTTPS (not HTTP)

### "Authorization required"
- Click "Review Permissions" in Apps Script
- Click "Advanced" → "Go to [Your Project] (unsafe)"
- Click "Allow"

### Menu doesn't appear
- Refresh the Google Sheet
- Check Apps Script saved successfully

---

## 📝 Quick Commands Reference

| Command | What it does |
|---------|-------------|
| `"fix net profit function"` | Updates NET PROFIT formula |
| `"show change log"` | View all changes |
| `"revert last change"` | Undo last change |
| `"swap shipping cost with PSL"` | Swap two columns |
| `"format orders sheet"` | Format the sheet |
| `"center all text"` | Center all text |
| `"add borders"` | Add borders to cells |

---

**That's it! You're ready to use the AI agent! 🎉**
