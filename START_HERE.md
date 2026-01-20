# Quick Start Guide - Using on Your Phone

## Your Setup:
- **Computer IP Address**: `192.168.1.242`
- **Backend URL**: `http://192.168.1.242:8000`
- **Frontend URL**: `http://192.168.1.242:8080`

## Step-by-Step Instructions:

### Step 1: Start the Backend Server
1. Open a terminal/command prompt
2. Navigate to your project folder:
   ```bash
   cd "C:\Users\Aryan\OneDrive\Rishab Fun Code"
   ```
3. Run the backend:
   ```bash
   python run_app.py
   ```
4. You should see: `Application startup complete. Uvicorn running on http://0.0.0.0:8000`

**Keep this terminal open!** The server needs to keep running.

### Step 2: Start the Frontend Server
1. Open a **NEW** terminal/command prompt window
2. Navigate to the frontend folder:
   ```bash
   cd "C:\Users\Aryan\OneDrive\Rishab Fun Code\frontend"
   ```
3. Start a simple web server:
   ```bash
   python -m http.server 8080
   ```
4. You should see: `Serving HTTP on 0.0.0.0 port 8080`

**Keep this terminal open too!**

### Step 3: Access from Your Phone

1. Make sure your phone is connected to the **same WiFi network** as your computer

2. Open a web browser on your phone (Chrome, Safari, etc.)

3. Type this URL in the address bar:
   ```
   http://192.168.1.242:8080
   ```

4. The app should load! You'll see:
   - Analytics dashboard with TikTok, Instagram, and Google Sheets data
   - Task management section

### Step 4: Test It Out!

- **View Analytics**: Tap on "Analytics" tab, switch between platforms
- **Add a Task**: 
  - Go to "Tasks" section
  - Tap "+ Add Task"
  - Fill in details and save
- **Track Progress**: View all your tasks, filter by user, mark as complete

## Troubleshooting:

### ❌ Can't connect from phone?
- Make sure both devices are on the **same WiFi network**
- Check Windows Firewall isn't blocking ports 8000 and 8080
- Try temporarily disabling Windows Firewall to test

### ❌ Backend won't start?
- Make sure port 8000 isn't already in use
- Check you installed all dependencies: `pip install -r requirements.txt`

### ❌ Frontend shows "Loading..." forever?
- Make sure the backend is running on port 8000
- Check the browser console for errors (on phone: use remote debugging)
- Try accessing the backend directly: `http://192.168.1.242:8000/api/health`

### ❌ "Connection refused" error?
- Make sure both servers are running
- Try accessing from your computer first: `http://localhost:8080` to test frontend
- Try accessing backend: `http://localhost:8000/api/health` to test backend

## Quick Test:
Open these URLs in your phone's browser:
- Frontend: `http://192.168.1.242:8080` ✅ Should show the app
- Backend Health: `http://192.168.1.242:8000/api/health` ✅ Should show `{"status":"healthy"}`

## That's it! 🎉
Your Arcus app is now accessible on your phone at `http://192.168.1.242:8080`

