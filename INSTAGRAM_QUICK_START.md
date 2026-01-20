# ⚡ Instagram Quick Start

## Fastest Way to Connect Instagram:

### 1. Create `.env` file
Location: `C:\Users\Aryan\OneDrive\Rishab Fun Code\.env`

### 2. Get Instagram Account ID
- Go to: https://business.facebook.com/settings
- Click "Instagram Accounts" → Click your account
- Copy the **Account ID** (long number)

### 3. Get Access Token
- Go to: https://developers.facebook.com/
- Create App → Add Instagram product
- Go to: https://developers.facebook.com/tools/explorer/
- Select your app and Instagram account
- Generate token → Extend it (60 days)
- Copy the token

### 4. Add to .env file
```env
INSTAGRAM_ACCESS_TOKEN=your_token_here
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_account_id_here
```

### 5. Restart backend
```bash
python run_app.py
```

### 6. Check app
- Open: `http://localhost:8080`
- Analytics → Instagram
- See real data! ✅

---

**Full guide:** See `INSTAGRAM_SETUP_STEP_BY_STEP.md`
