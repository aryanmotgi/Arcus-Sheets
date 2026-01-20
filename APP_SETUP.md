# Arcus Analytics & Task Management App

A mobile-friendly web application for viewing analytics (TikTok, Instagram, Google Sheets) and managing team tasks with deadlines.

## Features

- **Analytics Dashboard**: View analytics for TikTok, Instagram, and Google Sheets
- **Task Management**: Create, assign, and track tasks with deadlines
- **Mobile-Friendly**: Responsive design that works great on phones
- **Real-time Updates**: Refresh data to see latest analytics and tasks

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables (Optional)

Create a `.env` file in the project root for API keys:

```env
TIKTOK_API_KEY=your_tiktok_api_key_here
INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token_here
```

**Note**: The app will work with mock data if these are not set. To get real analytics:

- **TikTok**: Set up TikTok Business API access
- **Instagram**: Set up Instagram Graph API (via Facebook Developer)

### 3. Run the Backend Server

```bash
python run_app.py
```

The API will be available at `http://localhost:8000`

### 4. Open the Frontend

Open `frontend/index.html` in your web browser, or:

- **Option 1**: Use a local server (recommended):
  ```bash
  # Python
  cd frontend
  python -m http.server 8080
  
  # Then open: http://localhost:8080
  ```

- **Option 2**: Use VS Code Live Server extension
- **Option 3**: Just open `frontend/index.html` directly in your browser

### 5. Access on Mobile

To use on your phone:

1. Find your computer's local IP address:
   - Windows: `ipconfig` (look for IPv4 Address)
   - Mac/Linux: `ifconfig` or `ip addr`

2. Update `frontend/app.js`:
   ```javascript
   const API_BASE_URL = 'http://YOUR_IP_ADDRESS:8000/api';
   ```

3. Make sure your phone and computer are on the same WiFi network

4. Access from phone:
   - Open browser on phone
   - Go to: `http://YOUR_IP_ADDRESS:8080` (for frontend)
   - Make sure backend is running on `http://YOUR_IP_ADDRESS:8000`

## API Endpoints

### Analytics
- `GET /api/analytics/all` - Get all analytics
- `GET /api/analytics/tiktok` - Get TikTok analytics
- `GET /api/analytics/instagram` - Get Instagram analytics
- `GET /api/analytics/sheets` - Get Google Sheets analytics

### Tasks
- `GET /api/tasks` - Get all tasks (query params: `status`, `assigned_to`)
- `GET /api/tasks/{id}` - Get specific task
- `POST /api/tasks` - Create new task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task

### Users
- `GET /api/tasks/users` - Get all users
- `POST /api/tasks/users` - Create new user

## Usage

### Adding Users

Users are created automatically when you assign a task to someone new, or you can create them via the API.

### Adding Tasks

1. Click the "+ Add Task" button
2. Fill in the task details:
   - Title (required)
   - Description (optional)
   - Assign to a user (optional)
   - Set status
   - Set deadline (optional)
3. Click "Save Task"

### Viewing Analytics

- Switch between platforms using the tabs (All, TikTok, Instagram, Sheets)
- Analytics refresh when you load the page

## Database

The app uses SQLite database (`arcus_app.db`) which is created automatically on first run. This stores:
- Users
- Tasks
- Task assignments and deadlines

## Troubleshooting

### Backend won't start
- Make sure port 8000 is not in use
- Check that all dependencies are installed

### Can't see analytics
- TikTok/Instagram: The app uses mock data unless API keys are configured
- Google Sheets: Make sure your service account has access to the spreadsheet

### Mobile access doesn't work
- Ensure both devices are on the same WiFi
- Check firewall settings on your computer
- Try using your computer's IP address instead of `localhost`

## Next Steps

### To get real TikTok analytics:
1. Create a TikTok Business account
2. Apply for TikTok Business API access
3. Get your API key
4. Add it to `.env` as `TIKTOK_API_KEY`

### To get real Instagram analytics:
1. Create a Facebook Developer account
2. Create a Facebook App
3. Get Instagram Business Account ID
4. Generate an access token
5. Add it to `.env` as `INSTAGRAM_ACCESS_TOKEN`

## Development

The app structure:
- `app/` - Backend API (FastAPI)
- `frontend/` - Frontend (HTML/CSS/JS)
- `src/` - Existing Shopify integration code
- `config/` - Configuration files

