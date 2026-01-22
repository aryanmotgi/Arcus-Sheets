# 🚀 Local Testing Workflow - Test Before Deploying!

**You DON'T need to deploy to Render every time!** Test locally first, then deploy when you're happy.

---

## ✅ Quick Workflow

```
1. Make code changes
2. Test locally (localhost)
3. See results in Google Sheets
4. If good → Deploy to Render
5. If not → Fix and test again (back to step 2)
```

---

## 🧪 Step-by-Step: Test Locally First

### Step 1: Start Your Local Server

**Option A: Double-click (Easiest)**
```
Double-click: start_server_and_ngrok.bat
```

**Option B: Command Line**
```bash
python run_app.py
```

You'll see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

✅ **Server is running on `http://localhost:8000`**

---

### Step 2: Update Google Apps Script (One Time Setup)

1. Open your Google Sheet
2. **Extensions → Apps Script**
3. Find this line in `code.gs`:
   ```javascript
   const API_URL = 'https://your-render-url.onrender.com/api/agent/command';
   ```
4. **Change it to:**
   ```javascript
   const API_URL = 'http://localhost:8000/api/agent/command';
   ```
5. **Save** (Ctrl+S or Cmd+S)

---

### Step 3: Test Your Changes!

1. In Google Sheets, click **AI Agent → Open Command Dialog**
2. Type any command:
   - `"create setup costs sheet"`
   - `"sync orders"`
   - `"fix profit per shirt formula"`
3. **See results immediately!** No waiting for Render.

---

### Step 4: Make Changes & Test Again

1. Edit your code in Cursor/VS Code
2. **The server auto-reloads** (thanks to `reload=True`)
3. Test again in Google Sheets
4. Repeat until it works perfectly!

---

### Step 5: Deploy to Render (Only When Ready!)

Once everything works locally:

1. **Commit and push:**
   ```bash
   git add .
   git commit -m "Your changes"
   git push origin main
   ```

2. **Render auto-deploys** (takes 2-3 minutes)

3. **Update Google Apps Script back to Render URL:**
   ```javascript
   const API_URL = 'https://your-render-url.onrender.com/api/agent/command';
   ```

4. **Done!** Your changes are live.

---

## 🔄 Using ngrok (Optional - For Testing from Anywhere)

If you want to test from your phone or another computer:

1. **Run:**
   ```bash
   start_server_and_ngrok.bat
   ```

2. **Copy the ngrok HTTPS URL** (e.g., `https://abc123.ngrok-free.app`)

3. **Update Google Apps Script:**
   ```javascript
   const API_URL = 'https://abc123.ngrok-free.app/api/agent/command';
   ```

4. **Test from anywhere!**

---

## 📝 Quick Reference

| Task | Command |
|------|---------|
| Start local server | `python run_app.py` |
| Start server + ngrok | `start_server_and_ngrok.bat` |
| Create Setup Costs sheet | `python create_setup_costs_only.py` |
| Test sync | Use AI Agent: `"sync orders"` |
| Deploy to Render | `git push origin main` |

---

## ⚡ Pro Tips

1. **Keep localhost running** while developing - it auto-reloads on file changes
2. **Use localhost for testing** - it's instant, no waiting
3. **Only deploy to Render** when you're happy with the changes
4. **Switch back to Render URL** when done testing locally

---

## 🐛 Troubleshooting

**"Failed to connect to API"**
- Make sure `python run_app.py` is running
- Check Google Apps Script has `http://localhost:8000`
- Try refreshing Google Sheets

**"Server already running"**
- Close the terminal running the server
- Or use a different port (change `port=8000` to `port=8001`)

**Changes not showing?**
- Check the terminal for errors
- Make sure you saved the file
- The server should auto-reload (look for "Reloading..." in terminal)

---

## 🎯 Summary

✅ **Test locally first** → Fast, instant feedback  
✅ **Deploy to Render** → Only when you're happy  
✅ **No waiting** → See changes immediately  

**You're in control!** 🚀
