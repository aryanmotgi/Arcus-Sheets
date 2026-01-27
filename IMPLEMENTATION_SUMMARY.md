# 🚀 Arcus Dashboard Upgrade - Implementation Summary

## ✅ Completed Components

### 1. **MANUAL_OVERRIDES Sheet** ✅
- Created `MANUAL_OVERRIDES` sheet structure in `sheets_manager.py`
- Columns: `order_id`, `order_number`, `psl`, `shipping_label_cost`, `notes`, `updated_at`, `updated_by`
- Helper methods:
  - `create_manual_overrides_sheet()` - Creates the sheet
  - `upsert_manual_override()` - Upserts manual values
  - `get_manual_override()` - Retrieves manual values by order_id/order_number
  - `get_all_manual_overrides()` - Gets all overrides

### 2. **OpsAgent** ✅
- Created `src/ops_agent.py` for fulfillment & manual overrides
- Commands supported:
  - `"set shipping label cost to 4.85 for order 1042"`
  - `"set PSL to XYZ for order 1042"`
  - `"add note 'USPS ground' to order 1042"`
  - `"show unfulfilled orders"`
  - `"show missing shipping label cost"`
  - `"show negative profit orders"`
  - `"set shipping label cost to 4.12 for the last 6 unfulfilled orders"`
- **Plan→Apply pattern:** Commands return a plan by default; add `" apply"` to execute
- Automatically looks up `order_id` from `order_number`

### 3. **View Sheets Architecture** ✅
- Created `src/view_sheets_builder.py` to build view sheets
- `build_orders_view()` - Merges RAW_ORDERS with MANUAL_OVERRIDES using XLOOKUP formulas
- `build_fulfillment_view()` - Filters to unfulfilled orders
- Updated `update_orders_sheet.py` to:
  - Write to `RAW_ORDERS` instead of `Orders`
  - Automatically build view sheets after sync
  - Hide `RAW_ORDERS` sheet by default

### 4. **PSL Backup/Restore Removal** ✅
- Removed automatic PSL backup/restore from `SyncAgent._sync_orders()`
- Deprecated `_backup_psl()` and `_restore_psl()` methods
- Manual values now persist in `MANUAL_OVERRIDES` (no backup needed)

### 5. **FormatAgent** ✅
- Created `src/format_agent.py` for Arcus branding
- Arcus brand colors defined (premium streetwear aesthetic)
- Commands:
  - `"apply Arcus theme"` - Applies theme to all UI sheets
  - `"format HOME dashboard"` - Creates/formats HOME dashboard
- Features:
  - Dark backgrounds, white text
  - Hidden gridlines for cleaner look
  - Frozen headers
  - Consistent typography

### 6. **HOME Dashboard** ✅
- Created in `FormatAgent._build_dashboard_layout()`
- Features:
  - Arcus branding header ("ARCUS OPS" + tagline)
  - KPI cards: Revenue (7d/30d), Gross Profit, Units Sold, Unfulfilled, Missing Label Cost
  - Formulas pull from ORDERS and FULFILLMENT sheets
  - Premium streetwear aesthetic

### 7. **Extended SheetsManager** ✅
- New helper methods:
  - `hide_sheet()` / `show_sheet()` - Hide/show sheets
  - `freeze_header_row()` - Freeze header rows
  - `clear_gridlines()` - Hide gridlines
  - `insert_image()` - Insert images (using IMAGE formula)
  - `create_manual_overrides_sheet()` - Create MANUAL_OVERRIDES
  - `upsert_manual_override()` - Upsert manual values
  - `get_manual_override()` - Get manual values

### 8. **Updated AI Agent Routing** ✅
- Added `OpsAgent` and `FormatAgent` to `ai_agent.py`
- Updated routing logic:
  - Ops commands → `OpsAgent` (highest priority for write commands)
  - Format/branding → `FormatAgent`
  - Sync → `SyncAgent`
  - Costs → `CostsAgent`
  - Finance → `FinanceAgent`
  - Charts → `ChartAgent`
  - Sheet management → `SheetManagerAgent`
- Added `dry_run` parameter support
- Commands ending with `" apply"` execute immediately

## 🚧 Partially Implemented / Pending

### 1. **Profit Calculations Update** 🚧
- `view_sheets_builder.py` includes `_update_profit_formulas()` to use `shipping_label_cost` from MANUAL_OVERRIDES
- Formula: `Profit = Total Revenue - (Unit Cost * Quantity) - Shipping Label Cost`
- **Status:** Logic exists but needs testing with actual data

### 2. **METRICS Table** ⏳
- Not yet implemented
- Should replace hardcoded summary cells (P2/P4/etc)
- Planned structure: `metric_key`, `label`, `value`, `updated_at`

### 3. **CatalogAgent** ⏳
- Not yet implemented
- Planned for: products, costs, pricing, new product planning

### 4. **ChartAgent Improvements** ⏳
- Basic structure exists
- Needs real chart creation implementation

### 5. **Migration Script** ⏳
- Not yet created
- Should migrate existing PSL values from old "Orders" sheet to MANUAL_OVERRIDES

## 📋 New Commands Supported

### OpsAgent Commands:
- `"set shipping label cost to 4.85 for order 1042"` → Sets label cost (dry run by default)
- `"set shipping label cost to 4.85 for order 1042 apply"` → Executes immediately
- `"set PSL to XYZ123 for order 1042"`
- `"add note 'USPS ground' to order 1042"`
- `"show unfulfilled orders"`
- `"show missing shipping label cost"`
- `"show negative profit orders"`
- `"set shipping label cost to 4.12 for the last 6 unfulfilled orders"`

### FormatAgent Commands:
- `"apply Arcus theme"` → Applies branding to all UI sheets
- `"format HOME dashboard"` → Creates/formats HOME dashboard
- `"make it look like Arcus"` → Applies theme

### Existing Commands (Still Work):
- `"sync orders"` → Syncs to RAW_ORDERS, builds view sheets
- `"update total costs to 1000"`
- `"fix profit per shirt formula"`
- `"fix net profit formula"`

## 🔄 Migration Steps Needed

1. **Create MANUAL_OVERRIDES sheet:**
   - Run: `"sync orders"` (automatically creates it)
   - OR manually: The sheet is created on first sync

2. **Migrate existing PSL values:**
   - Need to create migration script to:
     - Read PSL column from old "Orders" sheet
     - Match by order_number or order_id
     - Write to MANUAL_OVERRIDES

3. **Switch to using ORDERS view:**
   - RAW_ORDERS is hidden by default
   - ORDERS view shows merged data (RAW + MANUAL_OVERRIDES)
   - FULFILLMENT view shows unfulfilled orders

4. **Apply Arcus theme:**
   - Run: `"apply Arcus theme"`
   - Run: `"format HOME dashboard"`

## 🎯 Key Architecture Changes

### Before:
- Single "Orders" sheet with manual PSL column
- PSL backup/restore during sync
- Hardcoded summary cells

### After:
- **RAW_ORDERS** - Raw synced data (hidden)
- **ORDERS** - View with MANUAL_OVERRIDES merged (via XLOOKUP)
- **FULFILLMENT** - Filtered view of unfulfilled
- **MANUAL_OVERRIDES** - Persistent manual values (no backup needed)
- **HOME** - Branded dashboard
- Profit calculations use `shipping_label_cost` from MANUAL_OVERRIDES

## ⚠️ Important Notes

1. **Order ID vs Order Number:**
   - System prefers `order_id` as primary key
   - OpsAgent automatically converts `order_number` → `order_id` when possible

2. **Dry Run Mode:**
   - Write commands return a plan by default
   - Add `" apply"` suffix to execute
   - Example: `"set shipping label cost to 4.85 for order 1042 apply"`

3. **View Sheets:**
   - ORDERS and FULFILLMENT are built automatically after sync
   - They use formulas (XLOOKUP) to merge MANUAL_OVERRIDES
   - Manual values persist forever (no sync overwrites them)

4. **RAW_ORDERS:**
   - Hidden by default
   - Contains raw synced data only
   - Never edited manually

## 🚀 Next Steps

1. Test the new system with real data
2. Create migration script for existing PSL values
3. Implement METRICS table
4. Create CatalogAgent
5. Improve ChartAgent with real charts
6. Add logo image to HOME dashboard (if URL provided)
7. Test profit calculations with shipping_label_cost

## 📝 Files Created/Modified

### New Files:
- `src/ops_agent.py` - Fulfillment & manual overrides agent
- `src/format_agent.py` - UI/branding agent
- `src/view_sheets_builder.py` - View sheet builder

### Modified Files:
- `src/sheets_manager.py` - Added MANUAL_OVERRIDES helpers and sheet utilities
- `src/sync_agent.py` - Removed PSL backup/restore, updated sync flow
- `src/update_orders_sheet.py` - Writes to RAW_ORDERS, builds view sheets
- `src/ai_agent.py` - Added new agents, updated routing, added dry_run support

---

**Status:** Core architecture implemented ✅ | Testing & refinement needed 🚧
