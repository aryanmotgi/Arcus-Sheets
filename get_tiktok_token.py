#!/usr/bin/env python3
"""
Helper script to get TikTok access token via OAuth
Run this after setting up your TikTok app
"""

import requests
import webbrowser
from urllib.parse import urlencode

# Step 1: Replace these with your values from TikTok Developer Portal
CLIENT_KEY = "your_client_key_here"
CLIENT_SECRET = "your_client_secret_here"
REDIRECT_URI = "http://localhost:8000/callback"

def get_authorization_url():
    """Generate the authorization URL"""
    params = {
        "client_key": CLIENT_KEY,
        "scope": "user.info.basic,video.list,video.insights",
        "response_type": "code",
        "redirect_uri": REDIRECT_URI
    }
    auth_url = f"https://www.tiktok.com/v2/auth/authorize/?{urlencode(params)}"
    return auth_url

def exchange_code_for_token(authorization_code):
    """Exchange authorization code for access token"""
    url = "https://open.tiktokapis.com/v2/oauth/token/"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "client_key": CLIENT_KEY,
        "client_secret": CLIENT_SECRET,
        "code": authorization_code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI
    }
    
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        token_data = response.json()
        return token_data.get("access_token"), token_data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None, None

if __name__ == "__main__":
    print("=" * 60)
    print("TikTok Access Token Generator")
    print("=" * 60)
    print()
    
    if CLIENT_KEY == "your_client_key_here":
        print("⚠️  First, update this script with your credentials:")
        print("   - CLIENT_KEY: From TikTok Developer Portal")
        print("   - CLIENT_SECRET: From TikTok Developer Portal")
        print()
        print("Then run this script again.")
        exit(1)
    
    print("Step 1: Opening authorization URL in browser...")
    auth_url = get_authorization_url()
    print(f"URL: {auth_url}")
    print()
    webbrowser.open(auth_url)
    
    print("Step 2: Authorize the app in the browser")
    print("Step 3: You'll be redirected - copy the 'code' from the URL")
    print("   The URL will look like: http://localhost:8000/callback?code=XXXXX")
    print()
    
    code = input("Paste the authorization code here: ").strip()
    
    print()
    print("Step 4: Exchanging code for access token...")
    access_token, token_data = exchange_code_for_token(code)
    
    if access_token:
        print("✅ Success!")
        print()
        print("=" * 60)
        print("Your TikTok Access Token:")
        print("=" * 60)
        print(access_token)
        print()
        print("Add this to your .env file:")
        print(f'TIKTOK_ACCESS_TOKEN={access_token}')
        print()
        print("Token expires in:", token_data.get("expires_in", "unknown"), "seconds")
    else:
        print("❌ Failed to get access token")
        print("Check your credentials and try again")
