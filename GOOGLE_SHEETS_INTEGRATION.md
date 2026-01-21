# 📊 Google Sheets Integration Guide

How to use the AI Agent directly within Google Sheets for seamless integration.

---

## 🎯 Overview

The AI Agent can interact with your Google Sheets in several ways:

1. **Read data** from your Google Sheets (revenue, profit, etc.)
2. **Write data** to your Google Sheets (sync orders, update information)
3. **Run commands** that affect your Google Sheets

---

## 🔧 Method 1: Using from Google Sheets (Simple Approach)

### Step 1: Set Up Automated Sync

Create a batch file on your computer that you can run:

**`sync_to_sheets.bat`:**
```batch
@echo off
echo Syncing orders to Google Sheets...
cd "C:\Users\Aryan\OneDrive\Rishab Fun Code"
python src/ai_agent.py "sync orders"
echo Sync complete! Check your Google Sheet.
pause
```

**To use:**
1. Double-click `sync_to_sheets.bat`
2. Wait for it to complete
3. Refresh your Google Sheet to see updated data

---

### Step 2: Add Buttons in Google Sheets

You can add buttons in your Google Sheet that trigger commands:

1. **Open your Google Sheet**
2. **Insert a drawing:**
   - Click "Insert" > "Drawing"
   - Draw a button (rectangle with text like "Sync Orders")
   - Click "Save and Close"

3. **Assign a script:**
   - Right-click the button
   - Click "Assign script"
   - Enter: `syncOrders` (we'll create this next)

4. **Open Apps Script:**
   - Click "Extensions" > "Apps Script"
   - Delete any existing code
   - Paste this code:

```javascript
function syncOrders() {
  // Show a message
  SpreadsheetApp.getUi().alert('Syncing orders...\n\nPlease run sync_to_sheets.bat on your computer.\n\nAfter it completes, refresh this sheet.');
  
  // Or optionally, you can call an external API if your server is running
  // var response = UrlFetchApp.fetch('http://localhost:8000/api/agent/command', {
  //   'method': 'post',
  //   'contentType': 'application/json',
  //   'payload': JSON.stringify({command: 'sync orders'})
  // });
}
```

**Note:** This is a placeholder that reminds you to run the batch file. For full automation, see Method 2.

---

## 🌐 Method 2: Google Apps Script with API (Advanced)

This method allows you to run commands directly from Google Sheets without leaving the browser.

### Prerequisites:
- Your FastAPI server must be accessible (running locally or deployed)
- For local access, use ngrok or similar tunnel service

### Step 1: Start Your API Server

```bash
python run_app.py
```

### Step 2: Make It Accessible (If Local)

If your server runs on `localhost`, Google Apps Script can't access it. Use ngrok:

1. **Download ngrok:** https://ngrok.com/download
2. **Start ngrok:**
   ```bash
   ngrok http 8000
   ```
3. **Copy the HTTPS URL** (e.g., `https://abc123.ngrok.io`)

### Step 3: Create Google Apps Script

1. **Open your Google Sheet**
2. **Click "Extensions" > "Apps Script"**
3. **Delete existing code and paste:**

```javascript
// Configuration - Update with your ngrok URL or server URL
const API_URL = 'https://your-ngrok-url.ngrok.io/api/agent/command';

/**
 * Creates a custom menu when the spreadsheet opens
 */
function onOpen() {
  var ui = SpreadsheetApp.getUi();
  ui.createMenu('🤖 AI Agent')
    .addItem('Sync Orders', 'syncOrders')
    .addItem('Show Revenue', 'showRevenue')
    .addItem('Orders Summary', 'ordersSummary')
    .addItem('Profit Breakdown', 'profitBreakdown')
    .addSeparator()
    .addItem('Backup PSL', 'backupPSL')
    .addItem('Restore PSL', 'restorePSL')
    .addToUi();
}

/**
 * Sync orders from Shopify to Google Sheets
 */
function syncOrders() {
  try {
    var ui = SpreadsheetApp.getUi();
    var response = ui.alert(
      'Sync Orders',
      'This will update all orders from Shopify. Continue?',
      ui.ButtonSet.YES_NO
    );
    
    if (response == ui.Button.YES) {
      var result = executeCommand('sync orders');
      ui.alert('Success!', 'Orders synced successfully.', ui.ButtonSet.OK);
      // Refresh the sheet
      SpreadsheetApp.getActiveSpreadsheet().getActiveSheet().getRange('A1').activate();
    }
  } catch (error) {
    SpreadsheetApp.getUi().alert('Error: ' + error.toString());
  }
}

/**
 * Show revenue information
 */
function showRevenue() {
  try {
    var result = executeCommand('show revenue');
    var revenue = result.data.revenue;
    
    var message = 'Revenue Information:\n\n';
    message += 'Total Revenue: ' + revenue.total_revenue + '\n';
    message += 'Net Profit: ' + revenue.net_profit + '\n';
    message += 'Units Sold: ' + revenue.units_sold + '\n';
    message += 'Shopify Payout: ' + revenue.shopify_payout;
    
    SpreadsheetApp.getUi().alert('Revenue', message, SpreadsheetApp.getUi().ButtonSet.OK);
  } catch (error) {
    SpreadsheetApp.getUi().alert('Error: ' + error.toString());
  }
}

/**
 * Get orders summary
 */
function ordersSummary() {
  try {
    var result = executeCommand('orders summary');
    var data = result.data;
    
    var message = 'Orders Summary:\n\n';
    message += 'Total Orders: ' + data.total_orders + '\n';
    message += 'Total Value: $' + data.total_value.toFixed(2) + '\n';
    message += '\nStatus Breakdown:\n';
    
    for (var status in data.status_breakdown) {
      message += status + ': ' + data.status_breakdown[status] + '\n';
    }
    
    SpreadsheetApp.getUi().alert('Orders Summary', message, SpreadsheetApp.getUi().ButtonSet.OK);
  } catch (error) {
    SpreadsheetApp.getUi().alert('Error: ' + error.toString());
  }
}

/**
 * Get profit breakdown
 */
function profitBreakdown() {
  try {
    var result = executeCommand('profit breakdown');
    var profit = result.data.profit_breakdown;
    
    var message = 'Profit Breakdown:\n\n';
    message += 'Total Revenue: ' + profit.total_revenue + '\n';
    message += 'Total Product Costs: ' + profit.total_product_costs + '\n';
    message += 'Total Costs: ' + profit.total_costs + '\n';
    message += 'Net Profit: ' + profit.net_profit + '\n';
    message += 'Profit Per Shirt: ' + profit.profit_per_shirt;
    
    SpreadsheetApp.getUi().alert('Profit Breakdown', message, SpreadsheetApp.getUi().ButtonSet.OK);
  } catch (error) {
    SpreadsheetApp.getUi().alert('Error: ' + error.toString());
  }
}

/**
 * Backup PSL values
 */
function backupPSL() {
  try {
    var result = executeCommand('backup PSL');
    var message = result.success ? 'PSL values backed up successfully!' : 'Backup failed: ' + result.message;
    SpreadsheetApp.getUi().alert('Backup PSL', message, SpreadsheetApp.getUi().ButtonSet.OK);
  } catch (error) {
    SpreadsheetApp.getUi().alert('Error: ' + error.toString());
  }
}

/**
 * Restore PSL values
 */
function restorePSL() {
  try {
    var ui = SpreadsheetApp.getUi();
    var response = ui.alert(
      'Restore PSL',
      'This will restore PSL values from backup. Continue?',
      ui.ButtonSet.YES_NO
    );
    
    if (response == ui.Button.YES) {
      var result = executeCommand('restore PSL');
      var message = result.success ? 'PSL values restored successfully!' : 'Restore failed: ' + result.message;
      ui.alert('Restore PSL', message, ui.ButtonSet.OK);
    }
  } catch (error) {
    SpreadsheetApp.getUi().alert('Error: ' + error.toString());
  }
}

/**
 * Execute a command via API
 */
function executeCommand(command) {
  var payload = {
    'command': command
  };
  
  var options = {
    'method': 'post',
    'contentType': 'application/json',
    'payload': JSON.stringify(payload),
    'muteHttpExceptions': true
  };
  
  try {
    var response = UrlFetchApp.fetch(API_URL, options);
    var result = JSON.parse(response.getContentText());
    
    if (!result.success) {
      throw new Error(result.message);
    }
    
    return result;
  } catch (error) {
    throw new Error('Failed to connect to API: ' + error.toString() + '\n\nMake sure:\n1. Your server is running (python run_app.py)\n2. ngrok is running (if using local server)\n3. API_URL is correct in the script');
  }
}
```

### Step 4: Update API URL

Replace `API_URL` in the script with your actual server URL:
- Local with ngrok: `https://abc123.ngrok.io/api/agent/command`
- Deployed server: `https://your-domain.com/api/agent/command`

### Step 5: Authorize and Test

1. **Save the script** (Ctrl+S)
2. **Run any function** (e.g., `syncOrders`) to trigger authorization
3. **Click "Review Permissions"**
4. **Choose your Google account**
5. **Click "Advanced" > "Go to [Project Name] (unsafe)"**
6. **Click "Allow"**

### Step 6: Use It!

1. **Refresh your Google Sheet**
2. **You'll see a new menu:** "🤖 AI Agent"
3. **Click the menu** to see all available commands
4. **Click any command** to execute it

---

## 🎨 Method 3: Custom Functions in Google Sheets

Create custom functions you can use directly in cells:

### Add to Apps Script:

```javascript
/**
 * Get total revenue (use in any cell: =TOTALREVENUE())
 */
function TOTALREVENUE() {
  try {
    var result = executeCommand('show revenue');
    var value = result.data.revenue.total_revenue;
    // Remove $ and convert to number
    return parseFloat(value.replace('$', '').replace(',', ''));
  } catch (error) {
    return 'Error: ' + error.toString();
  }
}

/**
 * Get net profit (use in any cell: =NETPROFIT())
 */
function NETPROFIT() {
  try {
    var result = executeCommand('show revenue');
    var value = result.data.revenue.net_profit;
    return parseFloat(value.replace('$', '').replace(',', ''));
  } catch (error) {
    return 'Error: ' + error.toString();
  }
}

/**
 * Get units sold (use in any cell: =UNITSSOLD())
 */
function UNITSSOLD() {
  try {
    var result = executeCommand('show revenue');
    return parseInt(result.data.revenue.units_sold);
  } catch (error) {
    return 'Error: ' + error.toString();
  }
}

/**
 * Sync orders and return status (use in any cell: =SYNCORDERS())
 */
function SYNCORDERS() {
  try {
    var result = executeCommand('sync orders');
    return result.success ? 'Synced successfully!' : 'Error: ' + result.message;
  } catch (error) {
    return 'Error: ' + error.toString();
  }
}
```

**To use:**
- In any cell, type: `=TOTALREVENUE()`
- The cell will show the total revenue from your summary section
- It updates when you refresh or recalculate the sheet

---

## 📋 Quick Setup Checklist

### For Method 1 (Simple):
- [ ] Create `sync_to_sheets.bat` file
- [ ] Test it works
- [ ] Add button in Google Sheets (optional)

### For Method 2 (Advanced):
- [ ] Install ngrok (for local server)
- [ ] Start API server (`python run_app.py`)
- [ ] Start ngrok tunnel
- [ ] Copy ngrok URL
- [ ] Create Apps Script with code above
- [ ] Update API_URL in script
- [ ] Authorize script
- [ ] Test the menu appears

### For Method 3 (Custom Functions):
- [ ] Add custom function code to Apps Script
- [ ] Save and authorize
- [ ] Test functions in cells

---

## 🎯 Recommended Workflow

1. **Morning routine:**
   - Open Google Sheet
   - Click "🤖 AI Agent" > "Sync Orders"
   - Review updated data

2. **Check metrics anytime:**
   - Use custom functions: `=TOTALREVENUE()`, `=NETPROFIT()`
   - Or click menu > "Show Revenue"

3. **Before syncing:**
   - Click "🤖 AI Agent" > "Backup PSL"
   - Then sync orders

---

## 🆘 Troubleshooting

### "Cannot access API" error:
- Make sure `python run_app.py` is running
- If using ngrok, make sure it's running and URL is correct
- Update API_URL in the script

### "Authorization required" error:
- Run any function once
- Click "Review Permissions"
- Authorize the script

### Functions return #ERROR:
- Check that the API server is running
- Verify API_URL is correct
- Check Apps Script execution log: "View" > "Execution log"

---

**Now you can control your Google Sheets with AI commands directly from within Google Sheets!** 🎉
