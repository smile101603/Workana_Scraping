# Google Sheets Export Setup Guide

This guide explains how to set up Google Sheets export for the Workana scraper.

## Overview

The scraper can automatically export jobs to a Google Spreadsheet with the following features:
- Creates a new sheet every day named after the date (e.g., "12/09")
- Exports all jobs that were first seen that day
- Applies conditional formatting based on price ranges:
  - **Green**: Price >= 1000 or hourly jobs
  - **Yellow**: Price between 500-1000 (fixed jobs only)
  - **Light Orange**: Price between 250-500 (fixed jobs only)

## Prerequisites

1. A Google account
2. A Google Spreadsheet (the ID is already configured: `1cwP7M2acOs6kohi6KZY__nnT7ys_-DW4iNun_-XBVcY`)
3. Google Cloud Project with Sheets API enabled

## Step 1: Create Google Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **Google Sheets API** and **Google Drive API**:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Sheets API" and enable it
   - Search for "Google Drive API" and enable it

## Step 2: Create Service Account Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Fill in the service account details:
   - Name: `workana-scraper` (or any name you prefer)
   - Click "Create and Continue"
   - Skip role assignment (click "Continue")
   - Click "Done"
4. Click on the created service account
5. Go to the "Keys" tab
6. Click "Add Key" > "Create new key"
7. Select "JSON" format
8. Download the JSON file and save it securely

## Step 3: Share Spreadsheet with Service Account

1. Open your Google Spreadsheet: `https://docs.google.com/spreadsheets/d/1cwP7M2acOs6kohi6KZY__nnT7ys_-DW4iNun_-XBVcY`
2. Click the "Share" button
3. Find the **email address** in the downloaded JSON file (look for `"client_email"` field)
   - It will look like: `workana-scraper@your-project.iam.gserviceaccount.com`
4. Add this email address as an editor with "Editor" permissions
5. Click "Send" (you don't need to notify them)

## Step 4: Configure Environment Variables

1. Place the downloaded JSON credentials file in your project directory (e.g., `credentials.json`)
2. Add the following to your `.env` file:

```env
# Google Sheets Export
GOOGLE_SHEETS_SPREADSHEET_ID=1cwP7M2acOs6kohi6KZY__nnT7ys_-DW4iNun_-XBVcY
GOOGLE_SHEETS_CREDENTIALS_PATH=./credentials.json
```

**Important**: 
- Replace `./credentials.json` with the actual path to your downloaded JSON file
- Keep the credentials file secure and never commit it to version control
- The spreadsheet ID is already set by default, but you can override it if needed

## Step 5: Install Dependencies

Make sure you have the required packages installed:

```bash
pip install -r requirements.txt
```

This will install:
- `gspread>=5.12.0` - Google Sheets API client
- `google-auth>=2.23.0` - Google authentication library

## Step 6: Test the Setup

Run the scraper once to test the Google Sheets export:

```bash
python main.py
```

You should see:
```
[4/6] Initializing Google Sheets exporter...
✅ Google Sheets export enabled
   Spreadsheet ID: 1cwP7M2acOs6kohi6KZY__nnT7ys_-DW4iNun_-XBVcY
```

After scraping, check your Google Spreadsheet. You should see:
- A new sheet with today's date (e.g., "12/09")
- Jobs exported with headers
- Conditional formatting applied based on price ranges

## Troubleshooting

### Error: "Failed to connect to Google Sheets"
- Verify the credentials JSON file path is correct
- Ensure the service account email has been shared with the spreadsheet
- Check that both Google Sheets API and Google Drive API are enabled

### Error: "Permission denied"
- Make sure the service account email has "Editor" permissions on the spreadsheet
- Verify the spreadsheet ID is correct

### Jobs not appearing in sheets
- Check that jobs were actually scraped (look at console output)
- Verify that `exported_to_sheets` tracking is working (check database)
- Ensure the date format matches (MM/DD)

### Conditional formatting not working
- The formatting is applied row-by-row, which may take a moment
- If formatting fails, the jobs will still be exported but without colors
- Check the console for any formatting warnings

## Security Notes

- **Never commit** the credentials JSON file to version control
- Add `credentials.json` to your `.gitignore` file
- Keep the service account credentials secure
- Only share the spreadsheet with the service account email (not publicly)

## Daily Sheet Format

Each day, a new sheet is created with:
- **Name**: Date in MM/DD format (e.g., "12/09" for December 9th)
- **Headers**: All job fields from the database
- **Data**: All jobs that were first seen on that date
- **Formatting**: Conditional formatting based on price ranges

The sheet structure matches the database schema exactly, so you can easily analyze the data in Google Sheets.

