# 🚀 START HERE - Quick Setup Guide

Follow these steps in order to get your AI Agent working with Google Sheets!

---

## ⚡ Quick Setup (5 Minutes)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Set Up Google Sheets Access
1. Download service account JSON from Google Cloud Console
2. Save it as: `credentials/service_account.json`
3. Share your Google Sheet with the service account email
   - Find the email in `service_account.json` under `"client_email"`
   - Share the sheet with "Editor" access

### Step 3: Configure Settings
1. Open `config/config.yaml`
2. Add your:
   - Shopify credentials
   - Google Spreadsheet ID (from the sheet URL)
   - Service account path

### Step 4: Test It!
```bash
python src/ai_agent.py "show revenue"
```

If you see revenue data, **you're all set!** ✅

---

## 📚 Detailed Guides

Choose what you need:

### 🆕 **New to this?**
→ Read: `SETUP_AND_USAGE_GUIDE.md` (Complete step-by-step setup)

### 📊 **Want to use it in Google Sheets?**
→ Read: `GOOGLE_SHEETS_INTEGRATION.md` (Apps Script integration)

### 🎯 **Need quick commands?**
→ Read: `AGENT_QUICK_START.md` (Command reference)

### 📖 **Want full documentation?**
→ Read: `AI_AGENT_GUIDE.md` (Complete guide)

---

## 🎯 Quick Commands

```bash
# Sync orders from Shopify to Google Sheets
python src/ai_agent.py "sync orders"

# Show revenue
python src/ai_agent.py "show revenue"

# Get orders summary
python src/ai_agent.py "orders summary"

# Profit breakdown
python src/ai_agent.py "profit breakdown"
```

---

## 🆘 Need Help?

1. **Check troubleshooting section** in `SETUP_AND_USAGE_GUIDE.md`
2. **Verify your setup:**
   - `config/config.yaml` exists and is correct
   - `credentials/service_account.json` exists
   - Google Sheet is shared with service account

---

## ✅ You're Ready!

Start using your AI Agent:
```bash
python src/ai_agent.py "sync orders"
```

🎉 **That's it!** Check your Google Sheet to see the updated data.
