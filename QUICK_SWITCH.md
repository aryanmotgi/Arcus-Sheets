# 🔄 Quick Switch: Localhost ↔ Render

## Switch to Localhost (For Testing)

**In Google Apps Script (`code.gs`):**
```javascript
const API_URL = 'http://localhost:8000/api/agent/command';
```

**Then:**
1. Start server: `python run_app.py`
2. Test in Google Sheets
3. Make changes, see results instantly!

---

## Switch to Render (For Production)

**In Google Apps Script (`code.gs`):**
```javascript
const API_URL = 'https://your-render-url.onrender.com/api/agent/command';
```

**Then:**
- Your changes are live on Render
- Anyone can use it
- No need to keep local server running

---

## 💡 Pro Tip

**Keep both URLs as comments:**
```javascript
// Local testing:
// const API_URL = 'http://localhost:8000/api/agent/command';

// Production (Render):
const API_URL = 'https://your-render-url.onrender.com/api/agent/command';
```

Just uncomment the one you want to use!
