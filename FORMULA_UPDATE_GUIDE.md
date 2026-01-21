# 🔧 Formula Update & Change Log Guide

Your AI agent can now update formulas and track all changes!

---

## 📝 Update Formulas

### Fix NET PROFIT Formula

**Command:**
```
"fix net profit function"
```

**What it does:**
- Updates NET PROFIT formula to: `=P4-P2` (TOTAL COSTS - Total Revenue)
- Logs the change for later reference
- Shows you the old and new formula

**Current Formula:**
- NET PROFIT = TOTAL COSTS (row 4) - Total Revenue (row 2)
- Formula location: Column P, Row 5

---

## 📋 View Change Log

### See All Changes

**Commands:**
```
"show change log"
"view changes"
"what did I change"
"recent changes"
```

**What you'll see:**
- List of all recent changes
- Timestamp for each change
- Description of what was changed
- Change type (formula_update, column_move, format, etc.)

---

## ⏪ Revert Changes

### Undo Last Change

**Command:**
```
"revert last change"
"undo last change"
"flashback"
```

**What it does:**
- Reverts the most recent change
- For formulas: restores the old formula
- Marks the change as reverted in the log

### Revert Specific Change

**Command:**
```
"revert change_20250119_123456"
```

(Use the change ID from the change log)

---

## 🎯 Example Workflow

### 1. Fix NET PROFIT Formula
```
"fix net profit function"
```
✅ Formula updated: `=P4-P2` (TOTAL COSTS - Total Revenue)

### 2. Check What Changed
```
"show change log"
```
✅ See: "Updated NET PROFIT formula" with timestamp

### 3. If Something's Wrong, Revert
```
"revert last change"
```
✅ Formula restored to previous value

---

## 📊 Supported Formula Updates

Currently supported:
- ✅ **NET PROFIT** - "fix net profit function"

Coming soon:
- Profit Margin %
- Profit Per Shirt
- Total Revenue
- Other summary formulas

---

## 🔍 Change Log Details

Each change includes:
- **ID**: Unique identifier (e.g., `change_20250119_123456`)
- **Timestamp**: When the change was made
- **Type**: Type of change (formula_update, column_move, format)
- **Description**: What was changed
- **Details**: Technical details (cell, old/new values, etc.)

---

## 💡 Tips

1. **Always check the log** after making changes
2. **Use revert** if something doesn't look right
3. **Formula updates are logged** automatically
4. **Change log persists** between sessions

---

**Try it now:**
```
"fix net profit function"
```

Then:
```
"show change log"
```

🎉 You'll see your change logged!
