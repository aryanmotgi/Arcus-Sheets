/**
 * AI Agent Integration for Google Sheets
 * 
 * INSTRUCTIONS:
 * 1. Open your Google Sheet
 * 2. Click "Extensions" > "Apps Script"
 * 3. Delete any existing code
 * 4. Paste this entire file
 * 5. Save (Ctrl+S)
 * 6. Click "Run" button and authorize
 * 7. Refresh your Google Sheet
 * 8. You'll see "🤖 AI Agent" menu at the top
 */

// ⚙️ CONFIGURATION - Update this with your server URL
// IMPORTANT: Replace with your actual Render URL (or ngrok URL for local testing)
// Format: https://your-app-name.onrender.com/api/agent/command
const API_URL = 'https://YOUR-APP-NAME.onrender.com/api/agent/command';

// ⚠️ SETUP INSTRUCTIONS:
// 1. Deploy your app to Render (or use ngrok for local testing)
// 2. Get your Render URL (e.g., https://arcus-sheets.onrender.com)
// 3. Replace 'YOUR-APP-NAME.onrender.com' above with your actual Render URL
// 4. Make sure the URL ends with '/api/agent/command'
// 5. Save this script and test with "Ping API" button

/**
 * Creates custom menu when spreadsheet opens
 */
function onOpen() {
  var ui = SpreadsheetApp.getUi();
  ui.createMenu('🤖 AI Agent')
    .addItem('💬 Open Command Dialog', 'showCommandDialog')
    .addSeparator()
    .addItem('🔄 Sync Orders', 'syncOrders')
    .addItem('💰 Show Revenue', 'showRevenue')
    .addItem('📊 Orders Summary', 'ordersSummary')
    .addItem('📈 Profit Breakdown', 'profitBreakdown')
    .addItem('🛍️ Product Sales', 'productSales')
    .addSeparator()
    .addItem('💾 Backup PSL', 'backupPSL')
    .addItem('📥 Restore PSL', 'restorePSL')
    .addSeparator()
    .addItem('🔍 Ping API (Debug)', 'pingApi')
    .addSeparator()
    .addItem('🔄 Hard Reset Sheet', 'hardResetSpreadsheet')
    .addToUi();
}

/**
 * Show dialog for typing custom commands
 */
function showCommandDialog() {
  // Load HTML from file (CommandDialog.html)
  // Make sure you've created CommandDialog.html in Apps Script
  var html = HtmlService.createHtmlOutputFromFile('CommandDialog')
    .setWidth(600)
    .setHeight(500)
    .setTitle('AI Agent - Command Interface');
  
  SpreadsheetApp.getUi().showModalDialog(html, '🤖 AI Agent Command Interface');
}

/**
 * Execute a command via API
 */
function executeCommand(command) {
  try {
    // Check if API_URL is configured
    if (API_URL.includes('YOUR-APP-NAME') || API_URL.includes('localhost')) {
      Logger.log('ERROR: API_URL not configured');
      return {
        success: false,
        error: 'API_URL not configured',
        message: '⚠️ API_URL is not set!\n\nPlease update API_URL in the script:\n1. Open Apps Script editor\n2. Find the API_URL constant at the top\n3. Replace with your Render URL:\n   https://your-app.onrender.com/api/agent/command\n4. Save and try again'
      };
    }
    
    // Validate command
    if (!command || command.trim() === '') {
      Logger.log('ERROR: Empty command received');
      return {
        success: false,
        error: 'Empty command',
        message: 'Please enter a command'
      };
    }
    
    var payload = {
      'command': command.trim()
    };
    
    var options = {
      'method': 'post',
      'contentType': 'application/json',
      'payload': JSON.stringify(payload),
      'muteHttpExceptions': true,
      'followRedirects': true,
      'validateHttpsCertificates': false,
      'timeout': 30000  // 30 second timeout
    };
    
    // Log request details
    Logger.log('=== API Request ===');
    Logger.log('API_URL: ' + API_URL);
    Logger.log('Command: ' + command);
    Logger.log('Payload: ' + JSON.stringify(payload));
    
    // Make request
    var response = UrlFetchApp.fetch(API_URL, options);
    var responseCode = response.getResponseCode();
    var responseText = response.getContentText();
    
    // Log response details
    Logger.log('=== API Response ===');
    Logger.log('Response Code: ' + responseCode);
    Logger.log('Response Body: ' + responseText.substring(0, 500)); // Limit log size
    
    // Check for HTTP errors
    if (responseCode < 200 || responseCode >= 300) {
      Logger.log('ERROR: HTTP error ' + responseCode);
      
      var errorMsg = 'Server returned error: ' + responseCode;
      if (responseCode === 0 || responseCode === 502 || responseCode === 503) {
        errorMsg += '\n\n⚠️ Service may be sleeping (free tier) or not responding.\n';
        errorMsg += 'Try:\n1. Wait 30 seconds and try again\n';
        errorMsg += '2. Check Render dashboard - is service running?\n';
        errorMsg += '3. Check API_URL is correct: ' + API_URL;
      } else if (responseCode === 404) {
        errorMsg += '\n\n⚠️ Endpoint not found. Check API_URL:\n' + API_URL;
        errorMsg += '\n\nShould end with: /api/agent/command';
      }
      errorMsg += '\n\nResponse: ' + responseText.substring(0, 200);
      
      return {
        success: false,
        error: 'HTTP ' + responseCode,
        message: errorMsg
      };
    }
    
    // Parse JSON response
    var result;
    try {
      result = JSON.parse(responseText);
    } catch (parseError) {
      Logger.log('ERROR: Failed to parse JSON response');
      Logger.log('Response text: ' + responseText.substring(0, 500));
      return {
        success: false,
        error: 'Parse error',
        message: 'Failed to parse server response:\n' + responseText.substring(0, 200)
      };
    }
    
    Logger.log('Parsed result: ' + JSON.stringify(result).substring(0, 500));
    
    return {
      success: true,
      data: result
    };
  } catch (error) {
    Logger.log('ERROR: Exception in executeCommand');
    Logger.log('Error: ' + error.toString());
    Logger.log('Stack: ' + error.stack);
    
    var errorMsg = 'Failed to connect to API.\n\n';
    if (error.toString().includes('timeout') || error.toString().includes('timed out')) {
      errorMsg += '⚠️ Request timed out. This usually means:\n';
      errorMsg += '1. Service is sleeping (free tier) - wait 30 seconds\n';
      errorMsg += '2. Service is not running - check Render dashboard\n';
      errorMsg += '3. API_URL is wrong - check: ' + API_URL;
    } else if (error.toString().includes('DNS') || error.toString().includes('hostname')) {
      errorMsg += '⚠️ Cannot resolve hostname. Check API_URL:\n' + API_URL;
    } else {
      errorMsg += 'Error: ' + error.toString();
      errorMsg += '\n\nMake sure:\n1. API_URL is correct\n2. Service is running on Render\n3. Check Apps Script Execution log for details';
    }
    
    return {
      success: false,
      error: error.toString(),
      message: errorMsg
    };
  }
}

/**
 * Ping API to test connection (debug function)
 */
function pingApi() {
  try {
    Logger.log('=== PING API ===');
    Logger.log('API_URL: ' + API_URL);
    
    // Check API_URL first
    if (API_URL.includes('YOUR-APP-NAME') || API_URL.includes('localhost')) {
      var ui = SpreadsheetApp.getUi();
      ui.alert(
        '⚠️ API URL Not Configured',
        'Please update API_URL in the script:\n\n' +
        '1. Open Apps Script editor (Extensions > Apps Script)\n' +
        '2. Find: const API_URL = ...\n' +
        '3. Replace with your Render URL:\n' +
        '   https://your-app.onrender.com/api/agent/command\n\n' +
        'Current URL: ' + API_URL,
        ui.ButtonSet.OK
      );
      return { success: false, error: 'API_URL not configured' };
    }
    
    var result = executeCommand('ping');
    Logger.log('Ping result: ' + JSON.stringify(result));
    
    var ui = SpreadsheetApp.getUi();
    if (result.success) {
      var responseData = result.data && result.data.data ? JSON.stringify(result.data.data, null, 2) : JSON.stringify(result.data, null, 2);
      ui.alert(
        '✅ Ping Success',
        'API is responding correctly!\n\n' +
        'Response:\n' + responseData.substring(0, 500),
        ui.ButtonSet.OK
      );
    } else {
      ui.alert(
        '❌ Ping Failed',
        'API connection failed:\n\n' + result.message + '\n\n' +
        'Check:\n' +
        '1. Is Render service running?\n' +
        '2. Is API_URL correct?\n' +
        '3. View Apps Script Execution log for details',
        ui.ButtonSet.OK
      );
    }
    return result;
  } catch (error) {
    Logger.log('Ping error: ' + error.toString());
    Logger.log('Stack: ' + error.stack);
    var ui = SpreadsheetApp.getUi();
    ui.alert(
      '❌ Ping Error',
      'Error: ' + error.toString() + '\n\n' +
      'Check Apps Script Execution log for details.',
      ui.ButtonSet.OK
    );
    return { success: false, error: error.toString() };
  }
}

/**
 * Sync orders (quick action)
 */
function syncOrders() {
  try {
    var ui = SpreadsheetApp.getUi();
    var response = ui.alert(
      'Sync Orders',
      'This will sync all orders from Shopify to Google Sheets. Continue?',
      ui.ButtonSet.YES_NO
    );
    
    if (response == ui.Button.YES) {
      var result = executeCommand('sync orders');
      
      if (result.success && result.data.success) {
        ui.alert('Success!', 'Orders synced successfully!\n\nRefresh your sheet to see updates.', ui.ButtonSet.OK);
        // Refresh the sheet
        SpreadsheetApp.getActiveSpreadsheet().getActiveSheet().getRange('A1').activate();
      } else {
        var errorMsg = result.success ? result.data.message : result.message;
        ui.alert('Error', 'Failed to sync orders:\n\n' + errorMsg, ui.ButtonSet.OK);
      }
    }
  } catch (error) {
    SpreadsheetApp.getUi().alert('Error', 'Error: ' + error.toString(), ui.ButtonSet.OK);
  }
}

/**
 * Show revenue (quick action)
 */
function showRevenue() {
  try {
    var result = executeCommand('show revenue');
    
    if (result.success && result.data.success) {
      var revenue = result.data.data.revenue;
      var message = '💰 Revenue Information\n\n';
      message += 'Total Revenue: ' + revenue.total_revenue + '\n';
      message += 'Net Profit: ' + revenue.net_profit + '\n';
      message += 'Units Sold: ' + revenue.units_sold + '\n';
      message += 'Shopify Payout: ' + revenue.shopify_payout;
      
      SpreadsheetApp.getUi().alert('Revenue', message, SpreadsheetApp.getUi().ButtonSet.OK);
    } else {
      var errorMsg = result.success ? result.data.message : result.message;
      SpreadsheetApp.getUi().alert('Error', 'Failed to get revenue:\n\n' + errorMsg, SpreadsheetApp.getUi().ButtonSet.OK);
    }
  } catch (error) {
    SpreadsheetApp.getUi().alert('Error', 'Error: ' + error.toString(), SpreadsheetApp.getUi().ButtonSet.OK);
  }
}

/**
 * Orders summary (quick action)
 */
function ordersSummary() {
  try {
    var result = executeCommand('orders summary');
    
    if (result.success && result.data.success) {
      var data = result.data.data;
      var message = '📊 Orders Summary\n\n';
      message += 'Total Orders: ' + data.total_orders + '\n';
      message += 'Total Value: $' + data.total_value.toFixed(2) + '\n\n';
      message += 'Status Breakdown:\n';
      
      for (var status in data.status_breakdown) {
        message += '  • ' + status + ': ' + data.status_breakdown[status] + '\n';
      }
      
      SpreadsheetApp.getUi().alert('Orders Summary', message, SpreadsheetApp.getUi().ButtonSet.OK);
    } else {
      var errorMsg = result.success ? result.data.message : result.message;
      SpreadsheetApp.getUi().alert('Error', 'Failed to get orders summary:\n\n' + errorMsg, SpreadsheetApp.getUi().ButtonSet.OK);
    }
  } catch (error) {
    SpreadsheetApp.getUi().alert('Error', 'Error: ' + error.toString(), SpreadsheetApp.getUi().ButtonSet.OK);
  }
}

/**
 * Profit breakdown (quick action)
 */
function profitBreakdown() {
  try {
    var result = executeCommand('profit breakdown');
    
    if (result.success && result.data.success) {
      var profit = result.data.data.profit_breakdown;
      var message = '📈 Profit Breakdown\n\n';
      message += 'Total Revenue: ' + profit.total_revenue + '\n';
      message += 'Total Product Costs: ' + profit.total_product_costs + '\n';
      message += 'Total Costs: ' + profit.total_costs + '\n';
      message += 'Net Profit: ' + profit.net_profit + '\n';
      message += 'Profit Per Shirt: ' + profit.profit_per_shirt;
      
      SpreadsheetApp.getUi().alert('Profit Breakdown', message, SpreadsheetApp.getUi().ButtonSet.OK);
    } else {
      var errorMsg = result.success ? result.data.message : result.message;
      SpreadsheetApp.getUi().alert('Error', 'Failed to get profit breakdown:\n\n' + errorMsg, SpreadsheetApp.getUi().ButtonSet.OK);
    }
  } catch (error) {
    SpreadsheetApp.getUi().alert('Error', 'Error: ' + error.toString(), SpreadsheetApp.getUi().ButtonSet.OK);
  }
}

/**
 * Product sales (quick action)
 */
function productSales() {
  try {
    var result = executeCommand('product sales');
    
    if (result.success && result.data.success) {
      var data = result.data.data;
      var message = '🛍️ Product Sales\n\n';
      message += 'Total Products: ' + data.total_products + '\n\n';
      
      if (data.product_sales) {
        message += 'Product Breakdown:\n';
        for (var product in data.product_sales) {
          var sales = data.product_sales[product];
          message += '  • ' + product + ':\n';
          message += '    - Quantity: ' + sales.Quantity + '\n';
          message += '    - Revenue: $' + sales['Unit Price'].toFixed(2) + '\n';
        }
      }
      
      SpreadsheetApp.getUi().alert('Product Sales', message, SpreadsheetApp.getUi().ButtonSet.OK);
    } else {
      var errorMsg = result.success ? result.data.message : result.message;
      SpreadsheetApp.getUi().alert('Error', 'Failed to get product sales:\n\n' + errorMsg, SpreadsheetApp.getUi().ButtonSet.OK);
    }
  } catch (error) {
    SpreadsheetApp.getUi().alert('Error', 'Error: ' + error.toString(), SpreadsheetApp.getUi().ButtonSet.OK);
  }
}

/**
 * Backup PSL (quick action)
 */
function backupPSL() {
  try {
    var result = executeCommand('backup PSL');
    
    if (result.success && result.data.success) {
      SpreadsheetApp.getUi().alert('Success!', 'PSL values backed up successfully!', SpreadsheetApp.getUi().ButtonSet.OK);
    } else {
      var errorMsg = result.success ? result.data.message : result.message;
      SpreadsheetApp.getUi().alert('Error', 'Failed to backup PSL:\n\n' + errorMsg, SpreadsheetApp.getUi().ButtonSet.OK);
    }
  } catch (error) {
    SpreadsheetApp.getUi().alert('Error', 'Error: ' + error.toString(), SpreadsheetApp.getUi().ButtonSet.OK);
  }
}

/**
 * Restore PSL (quick action)
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
      
      if (result.success && result.data.success) {
        ui.alert('Success!', 'PSL values restored successfully!', ui.ButtonSet.OK);
      } else {
        var errorMsg = result.success ? result.data.message : result.message;
        ui.alert('Error', 'Failed to restore PSL:\n\n' + errorMsg, ui.ButtonSet.OK);
      }
    }
  } catch (error) {
    SpreadsheetApp.getUi().alert('Error', 'Error: ' + error.toString(), SpreadsheetApp.getUi().ButtonSet.OK);
  }
}
