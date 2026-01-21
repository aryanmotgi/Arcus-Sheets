# 📚 Complete Setup & Usage Guide - AI Agent for Google Sheets

This guide will walk you through setting up and using the AI agent step-by-step, from installation to daily usage.

---

## 🚀 PART 1: Initial Setup

### Step 1: Verify Python Installation

1. **Check if Python is installed:**
   ```bash
   python --version
   ```
   You should see Python 3.8 or higher.

2. **If Python is not installed:**
   - Download from: https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"

---

### Step 2: Install Required Packages

1. **Open Command Prompt or PowerShell** in your project folder:
   ```bash
   cd "C:\Users\Aryan\OneDrive\Rishab Fun Code"
   ```

2. **Install all required packages:**
   ```bash
   pip install -r requirements.txt
   ```

   This installs:
   - `gspread` - Google Sheets API
   - `pandas` - Data processing
   - `pyyaml` - Configuration files
   - `requests` - Shopify API
   - `fastapi` - Web API (optional, for web interface)
   - And other dependencies

3. **Verify installation:**
   ```bash
   pip list | findstr gspread
   ```
   You should see `gspread` listed.

---

### Step 3: Set Up Google Sheets Credentials

1. **Create a Google Cloud Project:**
   - Go to: https://console.cloud.google.com/
   - Click "Create Project" or select an existing one
   - Give it a name (e.g., "Arcus Sheets")

2. **Enable Google Sheets API:**
   - In the Google Cloud Console, go to "APIs & Services" > "Library"
   - Search for "Google Sheets API"
   - Click "Enable"

3. **Enable Google Drive API:**
   - In the same library, search for "Google Drive API"
   - Click "Enable"

4. **Create Service Account:**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Give it a name (e.g., "arcus-sheets-bot")
   - Click "Create and Continue"
   - Skip role assignment for now
   - Click "Done"

5. **Download Service Account Key:**
   - Click on the service account you just created
   - Go to "Keys" tab
   - Click "Add Key" > "Create New Key"
   - Choose "JSON"
   - Download the file

6. **Save the Credentials:**
   - Move the downloaded JSON file to your project's `credentials` folder
   - Rename it to `service_account.json`
   - Your path should be: `credentials/service_account.json`

---

### Step 4: Set Up Config File

1. **Create or edit `config/config.yaml`:**

   ```yaml
   shopify:
     store_url: https://arcuswear.myshopify.com
     client_id: YOUR_SHOPIFY_CLIENT_ID
     client_secret: YOUR_SHOPIFY_CLIENT_SECRET
   
   google_sheets:
     spreadsheet_id: YOUR_SPREADSHEET_ID
     service_account_path: credentials/service_account.json
   
   profit:
     cost_per_shirt: 12.26
     default_shipping_label_cost: 0.00
   
   sync:
     frequency: daily
     time: "09:00"
   ```

2. **Get Your Spreadsheet ID:**
   - Open your Google Sheet
   - Look at the URL: `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`
   - Copy the `SPREADSHEET_ID` part
   - Paste it in `config.yaml`

3. **Share the Google Sheet:**
   - Open your Google Sheet
   - Click "Share" button
   - Copy the email address from your `service_account.json` file
     - Look for `"client_email"` in the JSON file
     - It looks like: `arcus-sheets-bot@your-project.iam.gserviceaccount.com`
   - Paste the email in the "Share with people and groups" field
   - Give it "Editor" access
   - Click "Send"

---

## ✅ PART 2: Test the AI Agent

### Step 5: Test Basic Functionality

1. **Open Command Prompt** in your project folder

2. **Test the agent:**
   ```bash
   python src/ai_agent.py "show revenue"
   ```

3. **What you should see:**
   ```
   ======================================================================
   Command: show revenue
   ======================================================================
   Status: SUCCESS
   Message: Revenue information retrieved
   
   Data:
   {
     "revenue": {
       "total_revenue": "$353.26",
       "net_profit": "$34.50",
       "units_sold": "26",
       "shopify_payout": "$337.02"
     }
   }
   ======================================================================
   ```

4. **If you get an error:**
   - Check that `config/config.yaml` exists and has correct values
   - Verify `credentials/service_account.json` exists
   - Make sure the Google Sheet is shared with the service account email

---

### Step 6: Test Different Commands

Try these commands one by one:

```bash
# 1. Get orders summary
python src/ai_agent.py "orders summary"

# 2. Get product sales
python src/ai_agent.py "product sales"

# 3. Get profit breakdown
python src/ai_agent.py "profit breakdown"

# 4. Get customer insights
python src/ai_agent.py "customer insights"
```

Each should return relevant data from your Shopify store and Google Sheets.

---

## 📊 PART 3: Using AI Agent with Google Sheets

There are **3 ways** to use the AI agent with Google Sheets:

---

### **Method 1: Direct from Command Line (Easiest)**

This is the simplest method - run commands directly from your computer:

1. **Sync orders to Google Sheets:**
   ```bash
   python src/ai_agent.py "sync orders"
   ```
   This will:
   - Fetch all orders from Shopify
   - Update the "Orders" sheet in Google Sheets
   - Preserve your PSL values
   - Format everything properly

2. **Get revenue info from Google Sheets:**
   ```bash
   python src/ai_agent.py "show revenue"
   ```
   This reads data directly from your Google Sheet's summary section.

3. **Get profit breakdown from Google Sheets:**
   ```bash
   python src/ai_agent.py "profit breakdown"
   ```
   This retrieves profit metrics from the summary section of your Orders sheet.

---

### **Method 2: Web Interface (More Convenient)**

Create a simple web interface you can open in your browser:

1. **Start the web server:**
   ```bash
   python run_app.py
   ```
   You should see:
   ```
   INFO:     Uvicorn running on http://0.0.0.0:8000
   ```

2. **Open the web interface:**
   - Open `test_agent.html` in your browser
   - Or create a shortcut to this file

3. **Use the interface:**
   - Click quick command buttons (Sync Orders, Show Revenue, etc.)
   - Or type your own command in the text box
   - Click "Execute" or press Enter

4. **See the results:**
   - The response appears below in a formatted box
   - You can see success/failure status
   - Data is displayed in JSON format

---

### **Method 3: Google Apps Script Integration (Advanced)**

This allows you to run commands directly from within Google Sheets:

1. **Open your Google Sheet**

2. **Open Apps Script Editor:**
   - Click "Extensions" > "Apps Script"

3. **Create a new script:**
   ```javascript
   function syncOrders() {
     // This would call your API endpoint
     var response = UrlFetchApp.fetch('http://localhost:8000/api/agent/command', {
       'method': 'post',
       'contentType': 'application/json',
       'payload': JSON.stringify({
         'command': 'sync orders'
       })
     });
     
     var result = JSON.parse(response.getContentText());
     Logger.log(result);
     return result;
   }
   ```

4. **Create a custom menu:**
   ```javascript
   function onOpen() {
     var ui = SpreadsheetApp.getUi();
     ui.createMenu('AI Agent')
       .addItem('Sync Orders', 'syncOrders')
       .addItem('Show Revenue', 'showRevenue')
       .addToUi();
   }
   ```

5. **Use it:**
   - Refresh your Google Sheet
   - You'll see a new "AI Agent" menu
   - Click the commands you want to run

**Note:** For this to work, you need to:
- Deploy your FastAPI server to a public URL (use ngrok or similar)
- Or run it on a server that Google Apps Script can access

---

## 🎯 PART 4: Daily Usage Examples

### Scenario 1: Update Orders Every Morning

**Create a batch file** (`sync_orders.bat`):
```batch
@echo off
cd "C:\Users\Aryan\OneDrive\Rishab Fun Code"
python src/ai_agent.py "sync orders"
pause
```

Double-click this file every morning to sync orders.

---

### Scenario 2: Check Revenue Quickly

**Create a batch file** (`check_revenue.bat`):
```batch
@echo off
cd "C:\Users\Aryan\OneDrive\Rishab Fun Code"
python src/ai_agent.py "show revenue"
pause
```

Run this anytime to see current revenue stats.

---

### Scenario 3: Backup PSL Before Syncing

**Create a batch file** (`backup_and_sync.bat`):
```batch
@echo off
cd "C:\Users\Aryan\OneDrive\Rishab Fun Code"
echo Backing up PSL values...
python src/ai_agent.py "backup PSL"
echo Syncing orders...
python src/ai_agent.py "sync orders"
echo Done!
pause
```

This ensures your PSL values are safe before syncing.

---

## 🔧 Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'gspread'"
**Solution:** Run `pip install -r requirements.txt`

### Problem: "FileNotFoundError: credentials/service_account.json"
**Solution:** Download the service account JSON from Google Cloud Console and save it as `credentials/service_account.json`

### Problem: "Permission denied" or "Spreadsheet not found"
**Solution:** Share your Google Sheet with the service account email (found in `service_account.json` under `client_email`)

### Problem: "Invalid credentials" for Shopify
**Solution:** Check your `client_id` and `client_secret` in `config/config.yaml`

### Problem: "Connection refused" when using web interface
**Solution:** Make sure `python run_app.py` is running in a separate terminal

---

## 📝 Quick Reference Card

### Available Commands:
- `"sync orders"` - Sync orders from Shopify to Google Sheets
- `"show revenue"` - Get total revenue from Google Sheets
- `"orders summary"` - Get summary of orders from Shopify
- `"product sales"` - Get product sales breakdown
- `"profit breakdown"` - Get profit analysis from Google Sheets
- `"backup PSL"` - Backup PSL values to file
- `"restore PSL"` - Restore PSL values from backup
- `"customer insights"` - Get customer purchase insights

### File Locations:
- Main agent: `src/ai_agent.py`
- Config: `config/config.yaml`
- Credentials: `credentials/service_account.json`
- Web interface: `test_agent.html`
- API server: `run_app.py`

---

## 🎉 You're All Set!

You now have a fully functional AI agent that can:
- ✅ Sync orders from Shopify to Google Sheets
- ✅ Read and display data from Google Sheets
- ✅ Provide insights and breakdowns
- ✅ Backup and restore PSL values
- ✅ Work from command line or web interface

**Start using it now:**
```bash
python src/ai_agent.py "sync orders"
```

---

**Need help?** Check the other guides:
- `AI_AGENT_GUIDE.md` - Detailed documentation
- `AGENT_QUICK_START.md` - Quick reference
