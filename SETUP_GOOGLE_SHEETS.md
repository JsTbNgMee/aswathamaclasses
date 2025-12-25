# Google Sheets Integration Setup Guide

## Step 1: Prepare Your Google Sheet

1. Create a new Google Sheet or use an existing one
2. Note your **Sheet ID** from the URL:
   - URL format: `https://docs.google.com/spreadsheets/d/SHEET_ID/edit`
   - Copy the `SHEET_ID` part

3. Create a sheet named `Students` (or it will use the active sheet)

## Step 2: Create Google Apps Script

1. Open your Google Sheet
2. Click **Extensions → Apps Script**
3. Delete any existing code
4. Copy the entire content from `google_sheets_api.gs`
5. Replace `YOUR_SHEET_ID` with your actual Sheet ID
6. Click **Save**

## Step 3: Deploy the Script

1. In Apps Script editor, click **Deploy → New Deployment**
2. Select **Type: Web app**
3. Set:
   - **Execute as:** Your Google account
   - **Who has access:** Anyone
4. Click **Deploy**
5. Copy the **Deployment URL** (it will look like: `https://script.google.com/macros/d/.../usercurrentapp`)

## Step 4: Set Environment Variable

In your Replit project, set the environment variable:
```
GOOGLE_APPS_SCRIPT_URL=<paste_your_deployment_url_here>
```

## Step 5: Update Python Dependencies

The Python app now requires the `requests` library (for API calls to Apps Script).

Run:
```bash
pip install requests
```

Or add to `requirements.txt`:
```
requests>=2.32.5
```

## How It Works

- **Google Apps Script** acts as an API server for your Google Sheet
- **Python Flask app** calls the Apps Script endpoints to read/write student data
- All student data is stored in the Google Sheet, not a traditional database
- The connection is stateless and works from anywhere

## Testing

After setup, test the connection by running your Flask app:
```bash
python main.py
```

The app should initialize without database connection errors and use Google Sheets for all student operations.
