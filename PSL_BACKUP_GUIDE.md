# PSL Backup & Restore Guide

## Problem
The Google Sheets API has rate limits and sometimes can't read your manually entered PSL (Private Shipping Label) values before updating the sheet. This can cause your PSL values to be deleted.

## Solution: Backup Before Sync

**Always backup your PSL values before running the main sync script!**

### Step 1: Backup PSL Values

Before running `python src/update_orders_sheet.py`, first backup your PSL values:

```bash
python src/backup_restore_psl.py backup
```

This will:
- Read all PSL values from column G in your Orders sheet
- Save them to `config/psl_backup.json`
- Show you how many values were backed up

### Step 2: Run Normal Sync

Then run your normal sync:

```bash
python src/update_orders_sheet.py
```

The sync script will automatically try to restore PSL values from the backup file if it can't read them from the sheet.

### Step 3: Manual Restore (if needed)

If the automatic restore doesn't work, you can manually restore:

```bash
python src/backup_restore_psl.py restore
```

## Quick Commands

**Backup PSL values:**
```bash
python src/backup_restore_psl.py backup
```

**Restore PSL values:**
```bash
python src/backup_restore_psl.py restore
```

## Workflow

1. Enter/edit PSL values in Google Sheets
2. Run backup: `python src/backup_restore_psl.py backup`
3. Run sync: `python src/update_orders_sheet.py`
4. Check your sheet - PSL values should be preserved
5. If values are missing, run restore: `python src/backup_restore_psl.py restore`

## Backup File Location

Backups are saved to: `config/psl_backup.json`

This file contains a JSON map of row numbers to PSL values, like:
```json
{
  "2": "3.75",
  "17": "5.49",
  "21": "3.16"
}
```

You can edit this file manually if needed, or delete it to force a fresh backup.
