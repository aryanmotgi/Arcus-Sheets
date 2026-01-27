# 📋 Complete Project State Documentation for AI

## 🎯 Project Overview

This is a **Shopify-to-Google Sheets Integration System** with a **Specialized Multi-Agent AI Architecture**. The system syncs order data from Shopify to Google Sheets, provides natural language command processing through Google Sheets, and includes specialized AI agents for different tasks.

**Key Purpose:** Enable users to manage their Shopify store data in Google Sheets and interact with it using natural language commands through a Google Sheets custom dialog.

---

## 🏗️ Architecture: Multi-Agent System

The system uses a **modular agent-based architecture** where the main `SheetsAIAgent` acts as a **router/orchestrator** that delegates commands to specialized agents:

### Core Agents:

1. **`SyncAgent`** (`src/sync_agent.py`)
   - **Purpose:** Handles all order syncing from Shopify to Google Sheets
   - **Key Features:**
     - Syncs ALL orders from Shopify API (no caching, fresh data)
     - **Automatic PSL Backup/Restore:** Before sync, backs up PSL (Private Shipping Label) values; after sync, automatically restores them
     - Creates "Setup and Costs" sheet
   - **Commands:**
     - `"sync orders"` - Full sync from Shopify
     - `"backup PSL"` - Manual backup of PSL column values
     - `"restore PSL"` - Manual restore of PSL column values
     - `"create setup costs sheet"` - Creates cost tracking sheet

2. **`CostsAgent`** (`src/costs_agent.py`)
   - **Purpose:** Handles all cost-related operations and formulas
   - **Key Features:**
     - Updates TOTAL COSTS value (currently $809.32)
     - Fixes "Profit Per Shirt" formula to `=SUM(I2:I{last_row})` (sums Profit column)
     - Gets/updates cost per shirt
     - Manages product costs
   - **Commands:**
     - `"update total costs to 1000"` - Updates TOTAL COSTS
     - `"fix profit per shirt formula"` - Fixes formula to sum column I
     - `"what's the total cost?"` - Gets current total costs

3. **`FinanceAgent`** (`src/finance_agent.py`)
   - **Purpose:** Handles financial calculations and formula fixes
   - **Key Features:**
     - Fixes NET PROFIT formula to `=P2-P4` (Total Revenue - TOTAL COSTS)
     - Gets revenue, costs, profit margin
   - **Commands:**
     - `"fix net profit formula"` - Sets NET PROFIT = Total Revenue - Total Costs
     - `"what's the total revenue?"` - Gets revenue
     - `"calculate profit margin"` - Calculates profit margin %

4. **`SheetManagerAgent`** (`src/sheet_manager_agent.py`)
   - **Purpose:** Handles sheet formatting, organization, column manipulation
   - **Key Features:**
     - Moves/swaps columns
     - Formats cells (colors, borders, alignment)
     - Organizes sheet layout
   - **Commands:**
     - `"swap shipping cost with PSL"` - Moves columns
     - `"format orders sheet"` - Applies formatting
     - `"add borders"` - Adds cell borders

5. **`ChartAgent`** (`src/chart_agent.py`)
   - **Purpose:** Handles chart creation (placeholder for future implementation)
   - **Status:** Basic structure exists, features coming soon

### Main Orchestrator:

**`SheetsAIAgent`** (`src/ai_agent.py`)
- **Role:** Command router that analyzes user input and delegates to appropriate agent
- **Process:**
  1. Receives natural language command
  2. Analyzes keywords to determine intent
  3. Routes to appropriate specialized agent
  4. Returns formatted response
- **Also includes:** Legacy methods for revenue queries, order summaries, product sales, customer insights, etc.

---

## 📁 File Structure & Key Files

### Core System Files:

- **`src/ai_agent.py`** - Main AI agent orchestrator (765 lines)
- **`src/sync_agent.py`** - Sync operations agent (220 lines)
- **`src/costs_agent.py`** - Cost management agent (247 lines)
- **`src/finance_agent.py`** - Finance calculations agent (190 lines)
- **`src/sheet_manager_agent.py`** - Sheet formatting/organization agent
- **`src/chart_agent.py`** - Chart creation agent (placeholder)

### Data Processing:

- **`src/update_orders_sheet.py`** - Core sync logic that fetches from Shopify and writes to Google Sheets
  - **Critical:** This is called by `SyncAgent._sync_orders()`
  - Handles all formatting, formulas, data processing
  - **Key Formula Fixes:**
    - NET PROFIT: `=P2-P4` (Total Revenue - TOTAL COSTS)
    - Profit Per Shirt: `=SUM(I2:I{last_row})` (Sum of Profit column)

- **`src/sheets_manager.py`** - Google Sheets API wrapper
  - Handles authentication (supports both file path and JSON string from env vars)
  - Creates sheets, formats cells, manages data

- **`src/shopify_client.py`** - Shopify API client
  - Fetches orders, products, customers

- **`src/data_processor.py`** - Processes Shopify order data into structured format

### Backup/Restore System:

- **`src/backup_restore_psl.py`** - PSL (Private Shipping Label) backup/restore
  - **Purpose:** Preserves user-entered PSL values during sheet updates
  - **Process:**
    1. Reads PSL column values from Google Sheets
    2. Saves to local JSON file
    3. After sync, restores values back to sheet
  - **Automatic:** Called automatically by `SyncAgent` before/after sync

### Setup & Costs Sheet:

- **`src/create_setup_costs_sheet.py`** - Creates enhanced "Setup and Costs" tracking sheet
  - **Features:**
    - Date, Category, Description, Vendor columns
    - Amount, Shipping Fee, Sales Fees columns
    - Auto-calculated Total Cost column
    - Status (Paid/Pending/Reimbursed) with color coding
    - Payment Method dropdown
    - Notes column
    - Smart summaries by Status and Category
    - Data validation dropdowns

### API & Web Interface:

- **`app/main.py`** - FastAPI application entry point
- **`app/routers/ai_agent.py`** - REST API endpoint for AI agent commands
  - **Endpoint:** `POST /api/agent/command`
  - **Request:** `{"command": "sync orders"}`
  - **Response:** `{"success": true, "message": "...", "data": {...}}`

### Google Apps Script Integration:

- **`code.gs`** - Google Apps Script that runs in Google Sheets
  - Opens custom dialog (`CommandDialog.html`)
  - Sends commands to FastAPI server (localhost or Render)
  - Displays responses in Google Sheets

- **`CommandDialog.html`** - Custom dialog UI in Google Sheets
  - Text input for commands
  - Buttons for common actions
  - Displays AI agent responses

---

## 🔄 Data Flow & Workflows

### Order Sync Workflow:

1. **User triggers sync** via Google Sheets dialog: `"sync orders"`
2. **Google Apps Script** sends POST to FastAPI: `/api/agent/command`
3. **FastAPI** routes to `SheetsAIAgent.process_command()`
4. **AI Agent** detects "sync" keyword → routes to `SyncAgent.process_command()`
5. **SyncAgent** executes:
   - **Step 1:** `_backup_psl()` - Saves PSL values to JSON
   - **Step 2:** `update_orders_sheet()` - Fetches ALL orders from Shopify, writes to Google Sheets
   - **Step 3:** `_restore_psl()` - Restores PSL values from backup
6. **Response** sent back to Google Sheets dialog

### Formula Fix Workflow:

1. **User command:** `"fix profit per shirt formula"`
2. **AI Agent** routes to `CostsAgent.process_command()`
3. **CostsAgent** detects "profit per shirt" → calls `_fix_profit_per_shirt_formula()`
4. **Method:**
   - Finds summary section (Column P, Row 6)
   - Calculates last row with data
   - Updates formula to: `=SUM(I2:I{last_row})`
5. **Response** confirms fix

### PSL Backup/Restore Workflow:

**Automatic (during sync):**
- Backup happens BEFORE `update_orders_sheet()`
- Restore happens AFTER `update_orders_sheet()`

**Manual:**
- User can run `"backup PSL"` or `"restore PSL"` anytime
- Values saved to `psl_backup.json` in project root

---

## 🔐 Configuration & Environment Variables

### Local Development:
- **`config/config.yaml`** - Contains:
  - Shopify credentials (store_url, client_id, client_secret)
  - Google Sheets spreadsheet_id
  - Service account path
  - Profit settings (cost_per_shirt, default_shipping_label_cost)

### Cloud Deployment (Render):
Uses **environment variables** (no config files):
- `SHOPIFY_STORE_URL`
- `SHOPIFY_CLIENT_ID`
- `SHOPIFY_CLIENT_SECRET`
- `GOOGLE_SHEETS_SPREADSHEET_ID`
- `GOOGLE_CREDENTIALS` - Service account JSON as string

**Priority:** Environment variables override `config.yaml` values.

### Google Sheets Access:
- **Service Account:** `shopify-sheets-sync@arcus-app-484801.iam.gserviceaccount.com`
- **Spreadsheet ID:** `1wK6aA1Sny5Ie3Ef8gU8LMgaBMjpNKW7ol1pxVWmGihE`
- **Permissions:** Service account must be shared with spreadsheet

---

## 📊 Google Sheets Structure

### "Orders" Sheet:

**Columns:**
- A: Order Number
- B: Date
- C: Customer Name
- D: Quantity
- E: Product Name
- F: Unit Price
- G: Total Revenue
- H: Unit Cost
- **I: Profit** (calculated per row)
- J: Shipping Cost
- K: PSL (Private Shipping Label) - **User-editable, preserved during sync**
- L: Shopify Payout
- M: Notes
- N: (empty)
- **O-P: Summary Section** (labels and values)

**Summary Section (Columns O-P):**
- Row 2: Total Revenue (P2)
- Row 3: Total Product Costs (P3)
- Row 4: TOTAL COSTS (P4) - **Fixed at $809.32**
- Row 5: NET PROFIT (P5) - **Formula: =P2-P4**
- Row 6: Profit Per Shirt (Overall) (P6) - **Formula: =SUM(I2:I{last_row})**
- Row 7: Total Units Sold (P7)
- Row 8: Shopify Payout (P8)

**Key Formulas:**
- **NET PROFIT:** `=P2-P4` (Total Revenue - TOTAL COSTS)
- **Profit Per Shirt:** `=SUM(I2:I{last_row})` (Sum of all Profit values in column I)
- **Profit (per row):** Calculated as `Total Revenue - (Unit Cost * Quantity) - Shipping Cost`

### "Setup and Costs" Sheet:

**Columns:**
- A: Date
- B: Category (dropdown: Manufacturing, Samples, Supplies, Shipping, Other)
- C: Description
- D: Vendor
- E: Amount ($)
- F: Shipping Fee
- G: Sales Fees
- H: Total Cost (auto-calculated: =SUM(E:G))
- I: Status (dropdown: Paid, Pending, Reimbursed) - **Color coded**
- J: Payment Method (dropdown: Credit Card, Bank Transfer, PayPal, Cash, Check, Other)
- K: Notes

**Summary Section:**
- Total Costs (all categories)
- By Status (Paid vs Pending)
- By Category (Manufacturing, Samples, Supplies, Other)

---

## 🚀 Deployment

### Local Development:
1. **Start server:** `python run_app.py` (runs on `localhost:8000`)
2. **Update Google Apps Script:** Set `API_URL = 'http://localhost:8000/api/agent/command'`
3. **Test in Google Sheets:** Use command dialog

### Cloud Deployment (Render):
1. **Push to GitHub:** `git push origin main`
2. **Render auto-deploys** (takes 2-3 minutes)
3. **Update Google Apps Script:** Set `API_URL = 'https://your-render-url.onrender.com/api/agent/command'`

**Environment Variables in Render:**
- All Shopify credentials
- Google Sheets credentials (as JSON string)
- Spreadsheet ID

---

## 🔧 Key Technical Details

### Command Routing Logic:

The `SheetsAIAgent.process_command()` method uses **keyword matching** to route commands:

```python
# Sync commands → SyncAgent
if 'sync' in command or 'update' in command or 'refresh' in command:
    return self.sync_agent.process_command(command)

# Cost commands → CostsAgent
if 'cost' in command or 'profit per shirt' in command:
    return self.costs_agent.process_command(command)

# Finance commands → FinanceAgent
if 'net profit' in command or 'revenue' in command:
    return self.finance_agent.process_command(command)

# Sheet management → SheetManagerAgent
if 'format' in command or 'swap' in command or 'move' in command:
    return self.sheet_manager_agent.process_sheet_command(command)
```

### PSL Backup/Restore Mechanism:

1. **Backup:** Reads column K (PSL) from all rows, saves to `psl_backup.json`
2. **Sync:** `update_orders_sheet()` overwrites entire sheet (including PSL column)
3. **Restore:** Reads `psl_backup.json`, writes values back to column K

**File Format:**
```json
{
  "backup_date": "2024-01-15T10:30:00",
  "values": {
    "2": "user_value_1",
    "5": "user_value_2",
    ...
  }
}
```

### Formula Fixes (Critical):

**NET PROFIT (P5):**
- **Must be:** `=P2-P4`
- **Why:** Total Revenue (P2) minus TOTAL COSTS (P4 = $809.32)
- **Fixed by:** `FinanceAgent._fix_net_profit_formula()`

**Profit Per Shirt (P6):**
- **Must be:** `=SUM(I2:I{last_row})`
- **Why:** Sum of all Profit values in column I
- **Fixed by:** `CostsAgent._fix_profit_per_shirt_formula()`

**TOTAL COSTS (P4):**
- **Must be:** Fixed value `809.32` (not a formula)
- **Why:** Represents fixed setup/manufacturing costs
- **Updated by:** `CostsAgent._update_total_costs()`

---

## 🐛 Known Issues & Solutions

### Issue: PSL Values Lost During Sync
**Solution:** Automatic backup/restore implemented in `SyncAgent._sync_orders()`

### Issue: Formulas Getting Overwritten
**Solution:** Formula fixes implemented in:
- `FinanceAgent._fix_net_profit_formula()`
- `CostsAgent._fix_profit_per_shirt_formula()`
- `update_orders_sheet.add_summary_section()` sets correct formulas

### Issue: Render Deployment Fails
**Solution:** Use environment variables instead of config files. Code checks `os.getenv()` first.

### Issue: Google Sheets API Errors
**Solution:** Ensure service account JSON is valid and shared with spreadsheet.

---

## 📝 Current State Summary

✅ **Working:**
- Multi-agent architecture with specialized agents
- Order syncing from Shopify to Google Sheets
- Automatic PSL backup/restore
- Formula fixes (NET PROFIT, Profit Per Shirt)
- Setup and Costs sheet creation
- Natural language command processing
- Local and cloud deployment

🚧 **In Progress:**
- Chart creation features (ChartAgent placeholder)
- Enhanced sheet management features

📋 **Key Files to Understand:**
1. `src/ai_agent.py` - Main orchestrator
2. `src/sync_agent.py` - Sync operations
3. `src/update_orders_sheet.py` - Core sync logic
4. `src/backup_restore_psl.py` - PSL preservation
5. `app/routers/ai_agent.py` - API endpoint

---

## 🎯 User Workflow

1. **Open Google Sheets** → Click "AI Agent" → "Open Command Dialog"
2. **Type command:** e.g., `"sync orders"`
3. **System:**
   - Routes to SyncAgent
   - Backs up PSL values
   - Fetches orders from Shopify
   - Writes to Google Sheets
   - Restores PSL values
4. **Response displayed** in dialog with summary

---

## 🔄 Development Workflow

1. **Make changes** in code
2. **Test locally:** `python run_app.py` + update Google Apps Script to localhost
3. **Iterate** until working
4. **Deploy:** `git push origin main` → Render auto-deploys
5. **Switch Google Apps Script** back to Render URL

---

## 📚 Important Notes

- **No code changes needed** - This document is for understanding only
- **Environment variables** take priority over config files
- **PSL backup/restore** is automatic during sync
- **Formulas are fixed** programmatically to prevent errors
- **Multi-agent system** allows easy extension with new agents
- **Local testing** is recommended before deploying to Render

---

**Last Updated:** Current state as of latest commit
**System Status:** Fully operational with multi-agent architecture
