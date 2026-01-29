/**
 * HARD RESET - Resets the spreadsheet to a clean state
 * 
 * This script will:
 * 1. Delete all tabs NOT in the allowed list
 * 2. Clear and recreate headers for allowed tabs
 * 3. Preserve SETTINGS key/value pairs
 * 4. Apply basic formatting and freeze header rows
 * 
 * HOW TO RUN:
 * 1. Open Apps Script Editor (Extensions > Apps Script)
 * 2. Paste this code into a new file (e.g., HardReset.gs)
 * 3. Run hardResetSpreadsheet() function
 * 4. Authorize when prompted
 */

// ========================================
// CONFIGURATION - Tab definitions
// ========================================

const ALLOWED_TABS = {
  visible: ['HOME', 'ORDERS', 'FINANCE', 'METRICS', 'CHARTS', 'PRODUCTS', 'COSTS', 'SETTINGS'],
  hidden: ['RAW_ORDERS', 'MANUAL_OVERRIDES']
};

const ALL_ALLOWED_TABS = [...ALLOWED_TABS.visible, ...ALLOWED_TABS.hidden];

// Headers for each tab
const TAB_HEADERS = {
  'HOME': ['Section', 'Value', 'Updated'],
  
  'ORDERS': [
    'Order ID', 'Order Number', 'Customer Name', 'Product Name', 'Size', 
    'Quantity', 'Sold Price', 'Shipping Cost', 'PSL', 'Unit Cost', 
    'Profit', 'Profit Margin %', 'Date', 'Order Status', 'Shipping Status'
  ],
  
  'FINANCE': [
    'Metric', 'Value', 'Period', 'Notes'
  ],
  
  'METRICS': [
    'Metric', '7 Days', '30 Days', 'All Time'
  ],
  
  'CHARTS': [
    'Chart Name', 'Data Source', 'Last Updated'
  ],
  
  'PRODUCTS': [
    'Product ID', 'SKU', 'Product Name', 'Product Type', 'Variant Title',
    'Price', 'Unit Cost', 'Margin %', 'Inventory Qty', 'Status'
  ],
  
  'COSTS': [
    'Date', 'Category', 'Item Description', 'Amount', 'Quantity', 
    'Total Cost', 'Notes', 'Type'
  ],
  
  'SETTINGS': [
    'Key', 'Value'
  ],
  
  'RAW_ORDERS': [
    'Customer Name', 'Product Name', 'Size', 'Quantity', 'Sold Price',
    'Shipping Cost', 'PSL', 'Unit Cost', 'Profit', 'Profit Margin %',
    'Date', 'Order Status', 'Shipping Status'
  ],
  
  'MANUAL_OVERRIDES': [
    'order_id', 'order_number', 'psl', 'shipping_label_cost', 'notes', 
    'updated_at', 'updated_by'
  ]
};

// Default SETTINGS keys (if creating from scratch)
const DEFAULT_SETTINGS = [
  ['api_url', ''],
  ['last_sync_at', ''],
  ['shopify_store_url', ''],
  ['theme_color_primary', '#4285F4'],
  ['theme_color_accent', '#34A853'],
  ['logo_url', ''],
  ['auto_sync_enabled', 'FALSE'],
  ['default_unit_cost', '12.26']
];

// ========================================
// MAIN FUNCTION
// ========================================

/**
 * Hard reset the spreadsheet to clean state
 * - Deletes unauthorized tabs
 * - Clears and recreates allowed tabs with proper headers
 * - Preserves SETTINGS values
 */
function hardResetSpreadsheet() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const ui = SpreadsheetApp.getUi();
  
  // Confirmation prompt
  const response = ui.alert(
    '⚠️ HARD RESET WARNING',
    'This will:\n' +
    '• DELETE all tabs not in the allowed list\n' +
    '• CLEAR all data from allowed tabs (except SETTINGS values)\n' +
    '• Recreate headers and formatting\n\n' +
    'This cannot be undone! Continue?',
    ui.ButtonSet.YES_NO
  );
  
  if (response !== ui.Button.YES) {
    ui.alert('Reset cancelled.');
    return;
  }
  
  Logger.log('=== HARD RESET STARTED ===');
  
  try {
    // Step 1: Backup SETTINGS values
    let settingsBackup = backupSettingsValues(ss);
    Logger.log('Backed up ' + settingsBackup.length + ' SETTINGS values');
    
    // Step 2: Get all existing sheet names
    const allSheets = ss.getSheets();
    const existingSheetNames = allSheets.map(s => s.getName());
    Logger.log('Found ' + existingSheetNames.length + ' existing sheets');
    
    // Step 3: Delete unauthorized sheets
    const sheetsToDelete = existingSheetNames.filter(name => !ALL_ALLOWED_TABS.includes(name));
    Logger.log('Sheets to delete: ' + sheetsToDelete.join(', '));
    
    for (const sheetName of sheetsToDelete) {
      try {
        const sheet = ss.getSheetByName(sheetName);
        if (sheet) {
          // Can't delete the last sheet, so we need at least one allowed sheet first
          ensureAtLeastOneSheet(ss);
          ss.deleteSheet(sheet);
          Logger.log('Deleted sheet: ' + sheetName);
        }
      } catch (e) {
        Logger.log('Could not delete sheet ' + sheetName + ': ' + e.toString());
      }
    }
    
    // Step 4: Create/recreate all allowed tabs with headers
    for (const tabName of ALL_ALLOWED_TABS) {
      resetTab(ss, tabName);
    }
    
    // Step 5: Restore SETTINGS values
    restoreSettingsValues(ss, settingsBackup);
    Logger.log('Restored SETTINGS values');
    
    // Step 6: Hide hidden tabs
    for (const hiddenTab of ALLOWED_TABS.hidden) {
      try {
        const sheet = ss.getSheetByName(hiddenTab);
        if (sheet) {
          sheet.hideSheet();
          Logger.log('Hidden sheet: ' + hiddenTab);
        }
      } catch (e) {
        Logger.log('Could not hide sheet ' + hiddenTab + ': ' + e.toString());
      }
    }
    
    // Step 7: Reorder tabs (visible first, then hidden)
    reorderTabs(ss);
    
    Logger.log('=== HARD RESET COMPLETED ===');
    
    ui.alert(
      '✅ Hard Reset Complete',
      'The spreadsheet has been reset successfully!\n\n' +
      'Tabs created: ' + ALL_ALLOWED_TABS.join(', ') + '\n\n' +
      'Next steps:\n' +
      '1. Run apply/setup if needed\n' +
      '2. Run sync orders\n' +
      '3. Check SETTINGS tab for configuration',
      ui.ButtonSet.OK
    );
    
  } catch (error) {
    Logger.log('ERROR: ' + error.toString());
    Logger.log('Stack: ' + error.stack);
    ui.alert('Error', 'Reset failed: ' + error.toString(), ui.ButtonSet.OK);
  }
}

// ========================================
// HELPER FUNCTIONS
// ========================================

/**
 * Backup SETTINGS key/value pairs
 */
function backupSettingsValues(ss) {
  const sheet = ss.getSheetByName('SETTINGS');
  if (!sheet) {
    Logger.log('No existing SETTINGS sheet to backup');
    return [];
  }
  
  try {
    const data = sheet.getDataRange().getValues();
    if (data.length <= 1) {
      return []; // Only headers or empty
    }
    
    // Skip header row, get key-value pairs
    const backup = [];
    for (let i = 1; i < data.length; i++) {
      const key = data[i][0];
      const value = data[i][1];
      if (key && key.toString().trim() !== '') {
        backup.push([key.toString().trim(), value]);
      }
    }
    return backup;
  } catch (e) {
    Logger.log('Error backing up SETTINGS: ' + e.toString());
    return [];
  }
}

/**
 * Restore SETTINGS values after reset
 */
function restoreSettingsValues(ss, backup) {
  const sheet = ss.getSheetByName('SETTINGS');
  if (!sheet) {
    Logger.log('SETTINGS sheet not found for restore');
    return;
  }
  
  // If we have backup values, use them; otherwise use defaults
  const valuesToWrite = backup.length > 0 ? backup : DEFAULT_SETTINGS;
  
  if (valuesToWrite.length > 0) {
    const startRow = 2; // After header
    const range = sheet.getRange(startRow, 1, valuesToWrite.length, 2);
    range.setValues(valuesToWrite);
    Logger.log('Wrote ' + valuesToWrite.length + ' SETTINGS values');
  }
}

/**
 * Ensure at least one sheet exists (to avoid deletion error)
 */
function ensureAtLeastOneSheet(ss) {
  const sheets = ss.getSheets();
  if (sheets.length <= 1) {
    // Create a placeholder that we'll keep
    let homeSheet = ss.getSheetByName('HOME');
    if (!homeSheet) {
      homeSheet = ss.insertSheet('HOME');
    }
  }
}

/**
 * Reset a single tab (clear, add headers, format)
 */
function resetTab(ss, tabName) {
  let sheet = ss.getSheetByName(tabName);
  
  // Create sheet if it doesn't exist
  if (!sheet) {
    sheet = ss.insertSheet(tabName);
    Logger.log('Created new sheet: ' + tabName);
  } else {
    // Clear all content
    sheet.clear();
    Logger.log('Cleared sheet: ' + tabName);
  }
  
  // Get headers for this tab
  const headers = TAB_HEADERS[tabName];
  if (!headers || headers.length === 0) {
    Logger.log('No headers defined for: ' + tabName);
    return;
  }
  
  // Write headers
  sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
  
  // Apply header formatting (blue background, white bold text)
  const headerRange = sheet.getRange(1, 1, 1, headers.length);
  headerRange
    .setBackground('#4285F4')
    .setFontColor('#FFFFFF')
    .setFontWeight('bold')
    .setFontSize(11)
    .setHorizontalAlignment('center')
    .setVerticalAlignment('middle');
  
  // Add borders to header
  headerRange.setBorder(true, true, true, true, true, true, '#000000', SpreadsheetApp.BorderStyle.SOLID);
  
  // Freeze header row
  sheet.setFrozenRows(1);
  
  // Auto-resize columns
  try {
    for (let i = 1; i <= headers.length; i++) {
      sheet.autoResizeColumn(i);
    }
  } catch (e) {
    Logger.log('Could not auto-resize columns for ' + tabName + ': ' + e.toString());
  }
  
  // Ensure minimum column width
  try {
    for (let i = 1; i <= headers.length; i++) {
      const currentWidth = sheet.getColumnWidth(i);
      if (currentWidth < 80) {
        sheet.setColumnWidth(i, 100);
      }
    }
  } catch (e) {
    // Ignore width errors
  }
  
  Logger.log('Reset complete for: ' + tabName);
}

/**
 * Reorder tabs: visible tabs first (in order), then hidden tabs
 */
function reorderTabs(ss) {
  try {
    const totalTabs = ALLOWED_TABS.visible.length + ALLOWED_TABS.hidden.length;
    let position = 0;
    
    // Move visible tabs to front
    for (const tabName of ALLOWED_TABS.visible) {
      const sheet = ss.getSheetByName(tabName);
      if (sheet) {
        ss.setActiveSheet(sheet);
        ss.moveActiveSheet(position + 1);
        position++;
      }
    }
    
    // Move hidden tabs to end
    for (const tabName of ALLOWED_TABS.hidden) {
      const sheet = ss.getSheetByName(tabName);
      if (sheet) {
        ss.setActiveSheet(sheet);
        ss.moveActiveSheet(position + 1);
        position++;
      }
    }
    
    // Set HOME as active sheet
    const homeSheet = ss.getSheetByName('HOME');
    if (homeSheet) {
      ss.setActiveSheet(homeSheet);
    }
    
    Logger.log('Tabs reordered successfully');
  } catch (e) {
    Logger.log('Could not reorder tabs: ' + e.toString());
  }
}

// ========================================
// MENU INTEGRATION (Optional)
// ========================================

/**
 * Add Hard Reset to the AI Agent menu
 * Call this from onOpen() if you want it in the menu
 */
function addHardResetToMenu() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('🔧 Admin Tools')
    .addItem('🔄 Hard Reset Spreadsheet', 'hardResetSpreadsheet')
    .addToUi();
}
