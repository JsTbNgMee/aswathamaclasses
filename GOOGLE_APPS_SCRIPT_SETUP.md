# Google Apps Script Integration Setup Guide

## What is This?

This is a **much simpler alternative** to service accounts. Instead of complex API authentication, we use Google Apps Script to handle all data operations in your Google Sheet.

---

## Setup Steps (5 minutes)

### Step 1: Create/Open Your Google Sheet
- Go to [Google Sheets](https://sheets.google.com)
- Create a new blank spreadsheet
- Copy the **Sheet ID** from the URL
  ```
  https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit
  ```

### Step 2: Add the Google Apps Script
1. In your Google Sheet, click **Extensions → Apps Script**
2. Delete any existing code
3. Open file: `GOOGLE_APPS_SCRIPT_CODE.js` in this project
4. Copy the **entire code**
5. Paste it into the Apps Script editor
6. Click **Save** (Ctrl+S)

### Step 3: Deploy the Script as Web App
1. Click **Deploy** → **New Deployment**
2. Choose **Type: Web app**
3. Set **Execute as: Your account**
4. Set **Who has access: Anyone**
5. Click **Deploy**
6. A dialog appears with the deployment URL
7. **Copy this URL** (you'll need it next)

Example URL looks like:
```
https://script.google.com/macros/d/{DEPLOYMENT_ID}/usercontent
```

### Step 4: Add to Replit Secrets
1. Click the **Secrets** lock icon in left sidebar
2. Click **Create Secret**
3. Add:
   - **Key:** `GOOGLE_APPS_SCRIPT_URL`
   - **Value:** Paste the deployment URL from Step 3
4. Click **Save**

### Step 5: Test It!
1. Go to `/admin/login`
2. Password: `admin123`
3. Try adding a student
4. **Check your Google Sheet** → Student should appear! 🎉

---

## How It Works

```
Flask App → Sends HTTP Request → Google Apps Script → Updates Google Sheet
```

When you:
- **Add a student** → Script adds row to sheet
- **Mark attendance** → Script updates cells
- **View records** → Script reads from sheet
- **Delete student** → Script removes row

All data is **permanently stored** in Google Sheets!

---

## Troubleshooting

### "Failed to add student"
- Check if `GOOGLE_APPS_SCRIPT_URL` is correctly added to Secrets
- Make sure the deployment URL is correct (copy-paste exactly)
- Try reloading the page after adding the secret

### Apps Script shows error when running
- Make sure you copied the ENTIRE code from `GOOGLE_APPS_SCRIPT_CODE.js`
- Check that you selected **Web app** deployment (not Library)
- Make sure **Who has access** is set to **Anyone**

### Student added but doesn't appear in Google Sheet
- Make sure the sheet name matches: Class 8, Class 9, or Class 10
- Check that the script ran successfully (see logs in Apps Script)
- Refresh the Google Sheet page

---

## No Secrets Setup? No Problem!

If you don't set up the Apps Script URL, the system automatically uses **local storage** (data stored in memory). You can:
- ✓ Add students
- ✓ Mark attendance  
- ✓ View records

Data won't persist when server restarts, but everything works!

---

## Advanced: Update the Script Later

If you need to change the script:
1. Go back to **Extensions → Apps Script**
2. Edit the code
3. Click **Save**
4. No need to redeploy! Changes take effect immediately

---

## Need Help?

Check the logs in your Google Apps Script editor:
1. **Extensions → Apps Script**
2. Click **Execution log** at the bottom
3. You'll see detailed error messages

---

**That's it! Your attendance system is now connected to Google Sheets!** 🚀
