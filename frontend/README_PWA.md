# Add App to Home Screen

This app is now a Progressive Web App (PWA) that you can add to your phone's home screen!

## How to Add to Home Screen:

### 📱 iPhone (iOS):
1. Open Safari browser (Chrome doesn't support this on iOS)
2. Go to: `http://192.168.1.242:8080`
3. Tap the **Share button** (square with arrow pointing up) at the bottom
4. Scroll down and tap **"Add to Home Screen"**
5. Edit the name if you want (default: "Arcus")
6. Tap **"Add"** in the top right
7. The app icon will appear on your home screen!

### 🤖 Android:
1. Open Chrome browser
2. Go to: `http://192.168.1.242:8080`
3. Tap the **menu button** (three dots) in the top right
4. Tap **"Add to Home screen"** or **"Install app"**
5. Tap **"Add"** or **"Install"**
6. The app icon will appear on your home screen!

### 🎯 Once Added:
- Tap the icon to open the app
- It will open fullscreen like a native app (no browser UI)
- Works offline for cached pages
- Updates automatically when you refresh

## Creating Icons:

Icons are needed for the app to look good on your home screen. Run:

```bash
pip install Pillow
python create_icons.py
```

This will create the icon files automatically. If you prefer custom icons, create:
- `icon-192.png` (192x192 pixels)
- `icon-512.png` (512x512 pixels)

With a blue background and your logo/design.

## Notes:

- Make sure both servers are running (backend on port 8000, frontend on port 8080)
- The app works best when accessed via the home screen icon
- Your phone needs to be on the same WiFi network as your computer

