# 📋 How to Copy Enhanced Dialog to Google Apps Script

If you're getting an error when copying, follow these steps:

---

## ✅ Method 1: Copy in Sections (Recommended)

### Step 1: Delete Old Content
1. Open Google Apps Script
2. Open `CommandDialog.html` file
3. Select ALL (Ctrl+A)
4. Delete (Delete key)
5. You should have a completely blank file

### Step 2: Copy the File
1. Open `ENHANCED_COMMAND_DIALOG.html` in your code editor (Cursor)
2. Select ALL (Ctrl+A)
3. Copy (Ctrl+C)

### Step 3: Paste into Apps Script
1. Go back to Google Apps Script
2. Click in the blank `CommandDialog.html` file
3. Paste (Ctrl+V)
4. **Wait a few seconds** for it to process
5. Click **Save** (Ctrl+S or floppy disk icon)

---

## ✅ Method 2: Copy Line by Line (If Method 1 Fails)

If the full copy doesn't work, try copying in smaller chunks:

1. Copy lines 1-200
2. Paste into Apps Script
3. Copy lines 201-400
4. Paste (append to existing)
5. Copy lines 401-697
6. Paste (append to existing)
7. Save

---

## ✅ Method 3: Use File Upload (Alternative)

1. In Google Apps Script, click **File** > **New** > **HTML file**
2. Name it: `CommandDialog` (exactly this name)
3. Delete the default code
4. Instead of pasting, try:
   - Click **File** > **Upload**
   - Select `ENHANCED_COMMAND_DIALOG.html` from your computer
   - This might work better than copy/paste

---

## 🔧 Troubleshooting

### Problem: "File too large" or "Character limit exceeded"
**Solution:**
- The file is 697 lines, which should be fine
- Try Method 2 (copy in sections)
- Or use Method 3 (file upload)

### Problem: "Syntax error" or "Invalid HTML"
**Solution:**
- Make sure you copied the ENTIRE file
- Check that the file starts with `<!DOCTYPE html>` and ends with `</html>`
- Make sure there are no extra characters

### Problem: "File not found" or "@ENHANCED_COMMAND_DIALOG.html"
**Solution:**
- This error means Apps Script is trying to reference the file name
- Make sure you're pasting INTO `CommandDialog.html`, not creating a new file
- The file should be named exactly `CommandDialog` (no spaces, no .html extension in Apps Script)

### Problem: Copy/Paste not working
**Solution:**
1. Try copying smaller sections
2. Or download the file and use File > Upload
3. Or manually type the key sections

---

## ✅ Quick Checklist

- [ ] Opened `CommandDialog.html` in Apps Script
- [ ] Deleted all old content
- [ ] Copied entire `ENHANCED_COMMAND_DIALOG.html` file
- [ ] Pasted into Apps Script
- [ ] Saved the file (Ctrl+S)
- [ ] No error messages
- [ ] File shows all 697 lines

---

## 🎯 Alternative: Simplified Version

If the enhanced version is too large, I can create a simpler version that's easier to copy. Would you like me to create a simplified version?

---

**Try Method 1 first, then Method 2 if needed!** Let me know if you still have issues.
