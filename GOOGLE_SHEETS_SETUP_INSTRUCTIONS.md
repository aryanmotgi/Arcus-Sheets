# 🎯 Setup Instructions: AI Agent Popup in Google Sheets

Follow these steps to add a popup dialog in your Google Sheets where you can type commands!

---

## 📋 Step-by-Step Setup

### Step 1: Open Your Google Sheet
1. Open your Google Sheet: https://docs.google.com/spreadsheets/d/1wK6aA1Sny5Ie3Ef8gU8LMgaBMjpNKW7ol1pxVWmGihE/edit
2. Make sure you're signed in with your Google account

### Step 2: Open Apps Script Editor
1. Click **"Extensions"** in the menu bar (top)
2. Click **"Apps Script"**
3. A new tab will open with the Apps Script editor

### Step 3: Delete Existing Code
1. In the Apps Script editor, select all existing code (Ctrl+A)
2. Delete it (Delete key)
3. You should have a blank editor

### Step 4: Paste the Main Script
1. Open the file `GOOGLE_SHEETS_SCRIPT.js` from your project folder
2. Copy all the code (Ctrl+A, then Ctrl+C)
3. Paste it into the Apps Script editor (Ctrl+V)

### Step 5: Create the Dialog HTML File
1. In Apps Script editor, click **"File"** > **"New"** > **"HTML file"**
2. Name it: `CommandDialog` (exactly this name, no spaces)
3. Delete all existing code in the new file
4. Open the file `CommandDialog.html` from your project folder
5. Copy all the code (Ctrl+A, then Ctrl+C)
6. Paste it into the Apps Script HTML file (Ctrl+V)
7. Save (Ctrl+S)

### Step 6: Update the API URL (IMPORTANT!)
1. Go back to the main script (Code.gs)
2. Find this line near the top:
   ```javascript
   const API_URL = 'http://localhost:8000/api/agent/command';
   ```
3. **If you're running the server locally**, you have 2 options:

   **Option A: Use ngrok (Recommended)**
   - Download ngrok: https://ngrok.com/download
   - Start your server: `python run_app.py`
   - In a new terminal, run: `ngrok http 8000`
   - Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)
   - Replace the API_URL with:
     ```javascript
     const API_URL = 'https://abc123.ngrok.io/api/agent/command';
     ```

   **Option B: Use localhost (may not work)**
   - Keep it as `http://localhost:8000/api/agent/command`
   - Note: This might not work because Google Apps Script cannot access localhost
   - You'll need to use ngrok or deploy your server online

### Step 7: Save and Authorize
1. Click **"Save"** button (floppy disk icon) or press Ctrl+S
2. Give your project a name (e.g., "AI Agent Integration")
3. Click **"Run"** button (play icon) at the top
4. You'll be asked to authorize:
   - Click **"Review Permissions"**
   - Choose your Google account
   - Click **"Advanced"** > **"Go to [Project Name] (unsafe)"**
   - Click **"Allow"**
   - You may see a warning - click **"Allow"** anyway

### Step 8: Refresh Your Google Sheet
1. Go back to your Google Sheet tab
2. Refresh the page (F5 or Ctrl+R)
3. You should now see a new menu: **"🤖 AI Agent"** in the menu bar!

### Step 9: Test It!
1. Click **"🤖 AI Agent"** menu
2. You'll see options:
   - **"💬 Open Command Dialog"** - This opens the popup!
   - **"🔄 Sync Orders"** - Quick sync
   - **"💰 Show Revenue"** - Quick revenue check
   - And more...

3. Click **"💬 Open Command Dialog"**
4. A popup will appear where you can:
   - Type any command (e.g., "sync orders")
   - Click quick command buttons
   - See the results

---

## 🚀 Quick Start with ngrok (For Localhost)

Since Google Apps Script cannot access `localhost`, you need ngrok:

### Install ngrok:
1. Download: https://ngrok.com/download
2. Extract the zip file
3. Add to PATH or use full path

### Use ngrok:
1. **Start your API server:**
   ```bash
   python run_app.py
   ```

2. **In a new terminal, start ngrok:**
   ```bash
   ngrok http 8000
   ```

3. **Copy the HTTPS URL** (looks like: `https://abc123.ngrok.io`)

4. **Update your Apps Script:**
   - Open Apps Script editor
   - Find `const API_URL = ...`
   - Change to: `const API_URL = 'https://abc123.ngrok.io/api/agent/command';`
   - Save

5. **Use it!** The popup will now work!

**Note:** Each time you restart ngrok, you'll get a new URL. Update the script with the new URL.

---

## ✅ What You Can Do Now

### Using the Popup Dialog:
1. Click **"🤖 AI Agent"** > **"💬 Open Command Dialog"**
2. Type any command:
   - `"sync orders"`
   - `"show revenue"`
   - `"orders summary"`
   - `"profit breakdown"`
   - `"product sales"`
   - `"backup PSL"`
   - `"restore PSL"`
3. Click **"Execute Command"** or press Enter
4. See results in the popup!

### Using Quick Menu Items:
- Click **"🤖 AI Agent"** menu
- Click any quick action:
  - **🔄 Sync Orders** - Syncs orders immediately
  - **💰 Show Revenue** - Shows revenue in a popup
  - **📊 Orders Summary** - Shows orders summary
  - And more...

---

## 🔧 Troubleshooting

### Problem: "Menu doesn't appear"
- **Solution:** Refresh your Google Sheet (F5)
- Make sure you authorized the script
- Check if `onOpen()` function exists in your script

### Problem: "Failed to connect to API"
- **Solution:** 
  - Make sure `python run_app.py` is running
  - If using localhost, use ngrok
  - Update API_URL in the script with correct URL
  - Check ngrok is running if using it

### Problem: "Authorization error"
- **Solution:**
  - Click "Run" button in Apps Script editor
  - Authorize again
  - Accept all permissions

### Problem: "Dialog doesn't open"
- **Solution:**
  - Make sure `CommandDialog.html` file exists in Apps Script
  - Check the file is named exactly `CommandDialog` (no spaces)
  - Save and refresh the sheet

### Problem: "ngrok URL changes every time"
- **Solution:** 
  - Sign up for free ngrok account
  - Get a fixed domain in ngrok dashboard
  - Use that domain in your script

---

## 🎉 You're Done!

Now you can:
- ✅ Type commands directly in Google Sheets
- ✅ Use the popup dialog for any command
- ✅ Quick access via menu items
- ✅ See results without leaving Google Sheets

**Try it now:**
1. Click **"🤖 AI Agent"** menu
2. Click **"💬 Open Command Dialog"**
3. Type: `"sync orders"`
4. Click **"Execute Command"**
5. Wait for the results!

---

**Need help?** Make sure:
1. Your server is running (`python run_app.py`)
2. ngrok is running (if using localhost)
3. API_URL is correct in the script
4. Script is authorized
