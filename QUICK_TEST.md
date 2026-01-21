# Quick Local Testing Guide

## Test Changes Locally (No Render Deployment Needed!)

### Option 1: Just Create the Setup and Costs Sheet

Run this to create the sheet immediately:
```bash
python create_setup_costs_only.py
```

This will create the "Setup and Costs" sheet in your Google Sheet right away!

---

### Option 2: Test the Full AI Agent Locally

1. **Start the local server:**
   ```bash
   python run_app.py
   ```
   OR double-click: `TEST_LOCALLY.bat`

2. **Update Google Apps Script** to use localhost:
   - Open your Google Sheet
   - Extensions → Apps Script
   - Change `API_URL` to: `http://localhost:8000/api/agent/command`
   - Save and refresh

3. **Test commands in Google Sheets:**
   - AI Agent → Open Command Dialog
   - Type commands like "sync orders" or "create setup costs sheet"
   - See changes immediately!

4. **If using ngrok (to test from anywhere):**
   - Run `start_server_and_ngrok.bat`
   - Copy the ngrok HTTPS URL
   - Update Google Apps Script with that URL

---

### Option 3: Direct Script Testing

Test individual scripts directly:
```bash
# Create Setup and Costs sheet
python create_setup_costs_only.py

# Run full sync
python src/update_orders_sheet.py

# Backup PSL
python src/backup_restore_psl.py backup
```

---

## Why the Sheet Didn't Appear Yet

The "Setup and Costs" sheet is created when you run `update_orders_sheet()`, which happens when:
- You run "sync orders" from the AI Agent
- OR you run `python src/update_orders_sheet.py`

**To see it NOW:**
```bash
python create_setup_costs_only.py
```

This creates just the Setup and Costs sheet without syncing orders.

---

## Workflow Recommendation

1. **Make changes** in code
2. **Test locally** using `python run_app.py` + Google Sheets
3. **Once it works**, push to GitHub → Render auto-deploys
4. **Update Google Apps Script** back to Render URL for production

This way you test quickly without waiting for deployment!
