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
// Option 1: If running locally with ngrok, use your ngrok URL
// Option 2: If deployed online, use your deployed URL
const API_URL = 'http://localhost:8000/api/agent/command';

// If you're using ngrok or a deployed server, replace the URL above with:
// const API_URL = 'https://your-ngrok-url.ngrok.io/api/agent/command';
// const API_URL = 'https://your-domain.com/api/agent/command';

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
    var payload = {
      'command': command
    };
    
    var options = {
      'method': 'post',
      'contentType': 'application/json',
      'payload': JSON.stringify(payload),
      'muteHttpExceptions': true,
      'followRedirects': true,
      'validateHttpsCertificates': false
    };
    
    // For localhost, we need to use a workaround
    // If you're using localhost, you'll need ngrok or a deployed server
    var response = UrlFetchApp.fetch(API_URL, options);
    var result = JSON.parse(response.getContentText());
    
    return {
      success: true,
      data: result
    };
  } catch (error) {
    return {
      success: false,
      error: error.toString(),
      message: 'Failed to connect to API. Make sure:\n1. Your server is running (python run_app.py)\n2. API_URL is correct in the script\n3. If using localhost, use ngrok or deploy your server'
    };
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
