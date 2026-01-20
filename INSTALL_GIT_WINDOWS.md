# 🔧 Install Git on Windows - Step by Step

Git is not installed on your computer. Here's how to install it:

## 📥 Step 1: Download Git

1. **Go to:** https://git-scm.com/download/win
2. The download should start automatically
3. Or click **"Click here to download"** if it doesn't

## 💿 Step 2: Install Git

1. **Find the downloaded file** (usually in `Downloads` folder)
   - It's called something like: `Git-2.42.0-64-bit.exe`

2. **Double-click** the installer file

3. **Follow the installation wizard:**
   - Click **"Next"** on the welcome screen
   - Click **"Next"** on the license screen
   - **Choose installation location:** Leave default (or change if you want)
   - Click **"Next"**
   - **Select components:** Keep all defaults checked ✅
   - Click **"Next"**
   - **Choose default editor:** Leave as "Nano" or choose "Visual Studio Code" if you prefer
   - Click **"Next"**
   - **Adjust PATH environment:** Keep default "Git from the command line and also from 3rd-party software"
   - Click **"Next"**
   - **Choose HTTPS transport:** Leave default "Use the OpenSSL library"
   - Click **"Next"**
   - **Line ending conversions:** Leave default "Checkout Windows-style, commit Unix-style"
   - Click **"Next"**
   - **Terminal emulator:** Leave default "Use MinTTY"
   - Click **"Next"**
   - **Default behavior of 'git pull':** Leave default
   - Click **"Next"**
   - **Credential helper:** Leave default
   - Click **"Next"**
   - **Extra options:** Leave defaults
   - Click **"Next"**
   - **Experimental options:** Leave unchecked
   - Click **"Install"**
   - Wait for installation to complete
   - Click **"Finish"**

## ✅ Step 3: Verify Installation

1. **Close** your current PowerShell/Command Prompt window
2. **Open a NEW** PowerShell window:
   - Press **Windows Key**
   - Type: `PowerShell`
   - Press **Enter**

3. **Navigate to your project:**
   ```powershell
   cd "C:\Users\Aryan\OneDrive\Rishab Fun Code"
   ```

4. **Test Git:**
   ```powershell
   git --version
   ```

5. **You should see:**
   ```
   git version 2.42.0
   ```
   (Version number may be different)

## 🎉 Success!

If you see a version number, Git is installed correctly!

Now you can proceed with pushing to GitHub.

---

## 🚀 Next Steps

After Git is installed, come back and we'll:
1. Set up your GitHub repository
2. Push your code to GitHub
3. Deploy to Railway

---

## ⚠️ If Installation Fails

- Make sure you have administrator rights
- Try running the installer as Administrator (right-click → "Run as administrator")
- Restart your computer after installation
