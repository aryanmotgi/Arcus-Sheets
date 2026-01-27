# Tab Manifest Implementation Summary

## ✅ COMPLETE: Tab Manifest System

### What Was Implemented

**1. Tab Manifest (`src/tab_manifest.py`)**
- Defines ONLY allowed tabs:
  - **Visible:** HOME, ORDERS, FINANCE, METRICS, CHARTS, PRODUCTS, COSTS, SETTINGS
  - **Hidden:** RAW_ORDERS, MANUAL_OVERRIDES
- Tab purposes dictionary with descriptions for each tab
- Helper functions for tab management

**2. Tab Management (`src/sheets_manager.py`)**
- `list_sheet_titles()` - Get all sheet titles
- `detect_extra_tabs()` - Find tabs NOT in manifest
- `ensure_tabs_exist_and_named()` - Create missing manifest tabs only
- `hide_tabs()` / `unhide_tabs()` - Hide/show tabs
- `delete_sheet_safe()` - Safe deletion (only non-manifest tabs)
- `cleanup_extra_tabs()` - Clean up duplicates and extras
- `add_tab_purpose_header()` - Add purpose banner to each tab

**3. FormatAgent Updates (`src/format_agent.py`)**
- **Idempotent:** Checks if theme already applied (SETTINGS!A1 marker)
- **No duplicates:** Only creates/manages manifest tabs
- **Purpose headers:** Adds purpose banner to each tab
- **New commands:**
  - `"cleanup tabs"` (dry-run) / `"cleanup tabs apply"` - Remove duplicates
  - `"reset arcus ui"` (dry-run) / `"reset arcus ui apply"` - Full UI reset
- **Guard:** Checks for extra tabs before formatting

**4. SyncAgent Guard (`src/sync_agent.py`)**
- Checks for extra tabs BEFORE syncing
- Returns error if extras found (prevents creating more)
- Ensures manifest tabs exist before sync
- Only writes to: RAW_ORDERS, ORDERS, METRICS

**5. AI Agent Commands (`src/ai_agent.py`)**
- `"what is each tab for?"` - Shows all tab purposes
- `"open workflow"` - Shows daily workflow using tabs
- Routes cleanup/reset commands to FormatAgent

**6. Sheet Name Normalization**
- `create_setup_costs_sheet.py` now uses "COSTS" instead of "Setup and Costs"
- `update_orders_sheet.py` removed auto-creation of Setup and Costs sheet

### Tab Purposes

Each tab now has a clear purpose header explaining:
- **What it's for**
- **Use cases**
- **What NOT to do**
- **Data source**

### Commands Added

1. **`"cleanup tabs"`** (dry-run)
   - Shows what would be deleted
   - Lists extras that need manual review

2. **`"cleanup tabs apply"`**
   - Deletes duplicate tabs (with "(1)", "copy", etc.)
   - Only deletes if safe (blank or has Arcus marker)
   - Never deletes manifest tabs

3. **`"reset arcus ui"`** (dry-run)
   - Shows what would happen

4. **`"reset arcus ui apply"`**
   - Cleans up extra tabs
   - Ensures all manifest tabs exist
   - Applies Arcus theme
   - Adds purpose headers
   - Hides system tabs

5. **`"what is each tab for?"`**
   - Returns formatted list of all tab purposes

6. **`"open workflow"`**
   - Shows daily workflow using the tabs

### Safety Features

- **Guard at sync:** Prevents syncing if extra tabs exist
- **Guard at format:** Prevents formatting if extra tabs exist
- **Safe deletion:** Only deletes non-manifest tabs with safety checks
- **Idempotent:** Commands safe to run multiple times
- **No duplicates:** System never creates "(1)" or "copy" tabs

### Remaining Work

Some files still reference "Orders" (lowercase) instead of "ORDERS":
- `src/ai_agent.py` (some references)
- `src/costs_agent.py`
- `src/backup_restore_psl.py`
- `src/sheet_manager_agent.py`
- `src/migrate_psl_to_manual_overrides.py` (checks both "Orders" and "RAW_ORDERS" for migration)

These are mostly in legacy code paths. The main sync/format paths now use manifest tabs correctly.

### Usage

**First Time Setup:**
```
"reset arcus ui apply"
```

**Daily Use:**
```
"sync orders"  # Only works if no extra tabs
"apply Arcus theme"  # Idempotent, safe to run multiple times
```

**Cleanup:**
```
"cleanup tabs apply"  # Remove duplicates
```

**Info:**
```
"what is each tab for?"
"open workflow"
```
