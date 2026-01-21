# 🚀 Quick Start: Google Sheets AI Agent

**Follow these 3 simple steps to use the AI agent in Google Sheets:**

---

## Step 1: Start Server & ngrok

**Double-click this file:**
```
start_server_and_ngrok.bat
```

**Wait for:**
- ✅ Server running on `http://localhost:8000`
- ✅ ngrok showing a URL like `https://abc123.ngrok.io`

**Copy the ngrok HTTPS URL** (e.g., `https://abc123.ngrok.io`)

---

## Step 2: Update Google Apps Script

1. Open your Google Sheet
2. Go to **Extensions → Apps Script**
3. Find this line (around line 10):
   ```javascript
   const API_URL = 'YOUR_NGROK_URL_HERE';
   ```
4. Replace `YOUR_NGROK_URL_HERE` with your ngrok URL:
   ```javascript
   const API_URL = 'https://abc123.ngrok.io';
   ```
5. **Save** (Ctrl+S or Cmd+S)

---

## Step 3: Update Dialog HTML

1. In Apps Script, find the `showCommandDialog()` function
2. Look for the `HtmlService.createHtmlOutput()` part
3. **Replace the HTML content** with the contents of `FIXED_COMMAND_DIALOG.html`
   - Open `FIXED_COMMAND_DIALOG.html` in your editor
   - Copy ALL the content
   - Paste it into Apps Script where it says `<!-- HTML content here -->`
4. **Save** (Ctrl+S or Cmd+S)

---

## Step 4: Use the Agent! 🎉

1. **Refresh your Google Sheet**
2. You'll see a new menu: **"AI Agent"**
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

**"Failed to connect to API"**
- Make sure server is running
- Check ngrok URL is correct in Apps Script
- Make sure ngrok URL is HTTPS (not HTTP)

**"Authorization required"**
- Click "Review Permissions" in Apps Script
- Click "Advanced" → "Go to [Your Project] (unsafe)"
- Click "Allow"

**Menu doesn't appear**
- Refresh the Google Sheet
- Check Apps Script saved successfully

---

**That's it! You're ready to use the AI agent! 🎉**
