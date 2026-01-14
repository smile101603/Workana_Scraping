# Workana Job Scraper

A Python-based web scraper for extracting job listings from Workana.com using Selenium.

## Features

- ✅ Scrapes job listings from Workana.com
- ✅ Detects newly posted jobs using job ID tracking
- ✅ Stores data in SQLite database
- ✅ **Slack notifications for new jobs** 🔔
- ✅ **Automatic description summarization** 📝
- ✅ Handles pagination automatically
- ✅ Parses relative dates ("20 hours ago", "Just now")
- ✅ Extracts comprehensive job information
- ✅ Rate limiting and respectful scraping
- ✅ Error handling and logging

## Requirements

- Python 3.8+
- Chrome browser (for Selenium WebDriver)
- Internet connection

## Installation

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. ChromeDriver will be automatically downloaded by `webdriver-manager` on first run

## Configuration

Edit `config/settings.py` to customize:

- `DEFAULT_CATEGORY`: Job category (default: "it-programming")
- `DEFAULT_LANGUAGE`: Language filter (default: "xx" for all)
- `MAX_PAGES`: Maximum pages to scrape (None for no limit)
- `STOP_ON_KNOWN_JOB`: Stop when encountering known job (default: True)
- `HEADLESS`: Run browser in headless mode (default: True)
- `DELAY_BETWEEN_REQUESTS`: Delay between page requests in seconds

### Slack Notifications & Translation

To enable Slack notifications with automatic English translation:

1. **Create a Slack Incoming Webhook**:
   - Go to https://api.slack.com/apps
   - Create a new app or select existing one
   - Go to "Incoming Webhooks" and activate it
   - Click "Add New Webhook to Workspace"
   - Select your channel and copy the webhook URL

2. **Get DeepL API Key (for translation)**:
   - Go to https://www.deepl.com/pro-api
   - Sign up for free account (500,000 characters/month free)
   - Get your API key from the dashboard

3. **Configure .env file**:
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and add your credentials
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
   DEEPL_API_KEY=your_deepl_api_key_here
   ```
   
   **Option B: Environment Variable**
   ```bash
   # Windows (PowerShell)
   $env:SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
   
   # Windows (CMD)
   set SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
   
   # Linux/Mac
   export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
   ```
   
   **Option C: Edit config/settings.py**
   ```python
   SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
   ```

3. **Run the scraper** - notifications will be sent automatically when new jobs are found!

**What Slack messages include:**
- Header with count of new jobs
- For each job:
  - Title (clickable link)
  - Posted date, Budget, Number of bids
  - Client location and rating
  - Skills required
  - **Summarized description** (intelligent summary, not just truncation)
  - **Key points** extracted from description (bullet points, requirements)
  - "View Job" button
- Summary statistics (total jobs, duration, etc.)

**Description Summarization:**
- Automatically summarizes long descriptions to 2-3 key sentences
- Extracts important bullet points and key requirements
- Keeps summaries concise (max 250 characters) while preserving important information

**Automatic Translation:**
- Job titles and descriptions are automatically translated to English using DeepL AI
- Supports translation from Spanish, Portuguese, and other languages
- Translation happens before sending to Slack
- Requires DeepL API key (free tier available: 500,000 chars/month)

## Usage

### Basic Usage

Run the scraper:
```bash
python main.py
```

The scraper will:
1. Connect to the database (creates `workana_jobs.db` if it doesn't exist)
2. Load existing job IDs
3. Scrape new jobs from Workana
4. Save new jobs to database
5. Display statistics and new jobs found

### Database

The scraper uses SQLite database (`workana_jobs.db`) to store:
- All job listings with full details
- Scraping history and statistics
- Tracks when jobs were first seen and last seen

### New Job Detection

The scraper uses **Job ID tracking** as the primary method:
- Each job has a unique ID extracted from its URL
- New jobs are identified by comparing with existing job IDs in database
- This method is 100% reliable and fast

## Project Structure

```
Workana Scraping/
├── config/
│   ├── settings.py          # Configuration settings
│   └── selectors.py          # CSS selectors
├── storage/
│   └── database.py           # SQLite database operations
├── parsers/
│   ├── date_parser.py        # Relative date parsing
│   └── job_parser.py         # Job data extraction
├── scrapers/
│   └── workana_scraper.py    # Selenium scraper
├── main.py                   # Main execution script
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Data Extracted

For each job, the scraper extracts:
- Job ID (unique identifier)
- Title and URL
- Description
- Posting date (relative and absolute timestamp)
- Number of bids
- Budget (min, max, type: fixed/hourly)
- Required skills
- Client information (name, country, rating)
- Featured/Max project flags

## Ethical Scraping

This scraper follows ethical scraping practices:
- Respects rate limits (3-5 second delays)
- Uses proper User-Agent headers
- Implements error handling
- Doesn't overwhelm servers

## Deployment to Ubuntu VPS

For production deployment on an Ubuntu VPS server, see the comprehensive **[DEPLOYMENT.md](DEPLOYMENT.md)** guide.

### Quick Setup

1. **Run the setup script:**
   ```bash
   chmod +x setup-ubuntu.sh
   ./setup-ubuntu.sh
   ```

2. **Create `.env` file with your API keys:**
   ```bash
   nano .env
   ```

3. **Set up as a systemd service:**
   ```bash
   # Edit workana-scraper.service and replace YOUR_USERNAME
   sudo cp workana-scraper.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable workana-scraper
   sudo systemctl start workana-scraper
   ```

### Key Considerations for VPS Deployment

- **Chrome/Chromium**: Must be installed on the server
- **Memory**: Chrome needs 2GB+ RAM (4GB+ recommended)
- **Permissions**: Run as non-root user
- **Logging**: Logs to `scraper.log` and systemd journal
- **Auto-restart**: Service automatically restarts on failure
- **Resource Limits**: Configured in systemd service file

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions, troubleshooting, and optimization tips.

## Troubleshooting

### ChromeDriver Issues
If you encounter ChromeDriver issues:
- Make sure Chrome browser is installed
- `webdriver-manager` will automatically download the correct driver version
- For manual installation, see [ChromeDriver documentation](https://chromedriver.chromium.org/)

### No Jobs Found
- Check your internet connection
- Verify the category and language settings in `config/settings.py`
- Try running with `HEADLESS = False` to see what's happening

### Database Errors
- Make sure you have write permissions in the project directory
- Delete `workana_jobs.db` to start fresh (you'll lose existing data)

### VPS Deployment Issues
- Check service status: `sudo systemctl status workana-scraper`
- View logs: `tail -f scraper.log` or `sudo journalctl -u workana-scraper -f`
- Verify Chrome: `google-chrome --version`
- Check memory: `free -h`
- See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed troubleshooting

## License

This project is for educational purposes. Please respect Workana's Terms of Service and robots.txt when using this scraper.

## Disclaimer

This scraper is provided as-is. Use responsibly and in accordance with Workana's Terms of Service. The authors are not responsible for any misuse of this tool.

