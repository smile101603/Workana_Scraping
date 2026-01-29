# Quick Start Guide - Workana Scraper

## Step-by-Step Setup

### 1. Install Python Dependencies

Open terminal/command prompt in the project directory and run:

```bash
pip install -r requirements.txt
```

This installs:
- Selenium (for web scraping)
- webdriver-manager (auto-downloads ChromeDriver)
- beautifulsoup4 & lxml (HTML parsing)
- requests (for Slack notifications)

### 2. Install Chrome Browser

Make sure you have Google Chrome installed:
- Download from: https://www.google.com/chrome/
- ChromeDriver will be automatically downloaded on first run

### 3. (Optional) Configure Slack Notifications & Translation

If you want Slack notifications with automatic English translation:

**Get Slack Webhook URL:**
1. Go to https://api.slack.com/apps
2. Create a new app or select existing
3. Go to "Incoming Webhooks" → Activate
4. Click "Add New Webhook to Workspace"
5. Select your channel and copy the webhook URL

**Get DeepL API Key (for translation):**
1. Go to https://www.deepl.com/pro-api
2. Sign up for free account (500,000 characters/month free)
3. Get your API key from the dashboard

**Configure .env file:**

1. Copy the example file:
   ```bash
   # Windows
   copy .env.example .env
   
   # Linux/Mac
   cp .env.example .env
   ```

2. Edit `.env` file and add your credentials:
   ```
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
   DEEPL_API_KEY=your_deepl_api_key_here
   ```

**Note:** Translation is optional. If you don't set DEEPL_API_KEY, jobs will be sent in their original language.

**Alternative: Environment Variable**
```powershell
# Windows PowerShell
$env:SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

**Alternative: Edit config/settings.py**
```python
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

### 4. (Optional) Customize Settings

Edit `config/settings.py` if needed:
- `DEFAULT_CATEGORY`: Change job category (default: "it-programming")
- `MAX_PAGES`: Limit pages to scrape (default: None = no limit)
- `HEADLESS`: Set to `False` to see browser (default: `True`)

### 5. Run the Scraper

**Windows:**
```bash
python main.py
```

**Linux/Mac:**
```bash
python3 main.py
```

## What Happens When You Run

1. **Database Initialization**
   - Creates `workana_jobs.db` if it doesn't exist
   - Creates tables and indexes

2. **Load Existing Jobs**
   - Loads all existing job IDs from database
   - Used to detect new jobs

3. **Start Scraping**
   - Opens Chrome browser (headless by default)
   - Navigates to Workana job listings
   - Scrapes job data from each page

4. **Save to Database**
   - Saves all scraped jobs
   - Identifies new vs existing jobs

5. **Send Notifications**
   - Sends Slack notification if new jobs found (if configured)
   - Shows summary statistics

6. **Display Results**
   - Shows total jobs scraped
   - Shows new jobs count
   - Lists new jobs in console

## Example Output

```
============================================================
Workana Job Scraper
============================================================

[1/5] Initializing database...
[2/5] Slack notifications disabled (no webhook URL)
[3/5] Loading existing job IDs...
Found 150 existing jobs in database
[4/5] Initializing scraper...
[5/5] Starting scrape...
Category: it-programming
Language: xx
Max pages: No limit
Stop on known job: True
------------------------------------------------------------

Scraping page 1/5
Found 20 jobs on page
Scraped 20 jobs from page 1
Waiting 1.5 seconds before next page...

Scraping page 2/5
Found 20 jobs on page
Found known job desenvolvedor-expert-em-webhook..., stopping scrape
Stopping scrape: found known job

Scraped 25 jobs total

Saving jobs to database...
New jobs: 5
Updated jobs: 20

============================================================
Scraping Statistics
============================================================
Total jobs in database: 155
New jobs (last 24h): 5
Total scrape sessions: 10
Duration: 45.23 seconds

============================================================
New Jobs Found (5)
============================================================
1. Webhook Developer Expert for Fixing...
   Posted: 20 hours ago
   Budget: USD 50 - 100
   URL: https://www.workana.com/job/...

2. Developing Professional Dashboards...
   Posted: 13 hours ago
   Budget: USD 250 - 500
   URL: https://www.workana.com/job/...
...
```

## Troubleshooting

### ChromeDriver Issues
- ChromeDriver is automatically downloaded by `webdriver-manager`
- Make sure Chrome browser is installed
- If issues persist, update Chrome to latest version

### No Jobs Found
- Check internet connection
- Verify category in `config/settings.py`
- Try running with `HEADLESS = False` to see what's happening

### Database Errors
- Make sure you have write permissions in project directory
- Delete `workana_jobs.db` to start fresh (you'll lose existing data)

### Slack Notifications Not Working
- Verify webhook URL is correct
- Check if webhook URL is set (environment variable or config file)
- Test webhook URL manually with curl:
  ```bash
  curl -X POST -H 'Content-type: application/json' \
    --data '{"text":"Test"}' \
    YOUR_WEBHOOK_URL
  ```

## Running on Schedule

### Windows Task Scheduler
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., Daily at 9 AM)
4. Action: Start a program
5. Program: `python`
6. Arguments: `D:\Project\Workana Scraping\main.py`
7. Start in: `D:\Project\Workana Scraping`

### Linux/Mac Cron
```bash
# Edit crontab
crontab -e

# Add line to run every hour
0 * * * * cd /path/to/project && /usr/bin/python3 main.py >> scraper.log 2>&1
```

### Python Script (Windows/Linux/Mac)
Create `run_scheduled.py`:
```python
import schedule
import time
import subprocess

def run_scraper():
    subprocess.run(["python", "main.py"])

# Schedule to run every 6 hours
schedule.every(6).hours.do(run_scraper)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## Next Steps

- Check `workana_jobs.db` with SQLite browser
- Query database for specific jobs
- Customize notification format
- Add more categories to scrape
- Set up automated scheduling

## Need Help?

- Check `README.md` for detailed documentation
- Review `APPROACH.md` for technical details
- Check console output for error messages

