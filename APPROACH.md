# Workana.com Scraping Approach

## 1. Website Analysis & Understanding

### Actual HTML Structure (Based on Analysis):

**Base URL Pattern**: `https://www.workana.com/jobs?category=it-programming&language=xx`

**Job Container**: 
- Main container: `<div id="projects">`
- Individual job: `<div class="project-item js-project">` (or `project-item-featured` for featured jobs)

**Key HTML Selectors**:
- **Job Title**: `h2.h3.project-title > span > a` (contains full title and link)
- **Job URL**: Extracted from `href` attribute in title link (e.g., `/job/desenvolvedor-expert-em-webhook...`)
- **Posting Date**: `div.project-main-details > span.date` (e.g., "Published: 20 hours ago", "Published: Just now")
- **Bids Count**: `div.project-main-details > span.bids` (e.g., "Bids: 16")
- **Description**: `div.html-desc.project-details > div > p` (truncated with "View more" link)
- **Skills**: `div.skills > div > a.skill.label.label-info > h3` (multiple skill tags)
- **Budget**: `p.budget.h4 > span.values > span` (e.g., "USD 50 - 100", "Over USD 45 / hour")
- **Client Name**: `div.project-author > span.author-info > button` (popover with client details)
- **Client Country**: `div.project-author > span.country > a > span.country-name`
- **Client Rating**: `div.project-author > span.rating > span.profile-stars` (visual stars, need to extract title attribute)
- **Featured Badge**: `span.label.label-max` (if present, indicates "Max project")

**Pagination**:
- Container: `<nav class="text-center">` with `<ul class="pagination">`
- Page links: `ul.pagination > li > a` (contains page numbers)
- Current page: `li.active > a`
- URL pattern: `?category=it-programming&language=xx&page=2`

**Date Format Challenges**:
- Uses relative dates: "Just now", "22 minutes ago", "1 hour ago", "Yesterday", "2 days ago"
- Need to convert to absolute timestamps for comparison
- May need to visit individual job pages for exact timestamps

**JavaScript Dependency**:
- Site uses Vue.js (`data-v-app` attribute)
- Content is dynamically rendered
- **Requires Selenium** for proper content loading

## 2. Technical Approach (Selenium-Based)

### Primary Approach: Selenium WebDriver
**Rationale**: Workana.com uses Vue.js and dynamically renders content. Selenium is required to properly load and interact with the page.

**Tools**:
- `selenium` - Browser automation (Chrome WebDriver recommended)
- `webdriver-manager` - Automatic driver management
- `beautifulsoup4` - HTML parsing after Selenium renders
- `lxml` - Fast HTML parser

**Selenium Setup**:
```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
```

**Process**:
1. Initialize Chrome WebDriver with headless mode
2. Navigate to job listing page
3. Wait for job containers to load (`WebDriverWait` for `#projects` or `.project-item`)
4. Scroll page if needed to trigger lazy loading
5. Extract rendered HTML using `driver.page_source`
6. Parse with BeautifulSoup using identified selectors
7. Handle pagination by clicking next page or constructing URLs
8. Extract individual job details (optional: visit job detail pages)

**Key Selenium Strategies**:
- **Explicit Waits**: Use `WebDriverWait` to wait for elements (e.g., `presence_of_element_located`)
- **Implicit Waits**: Set reasonable timeout for element finding
- **Scroll Handling**: May need to scroll to load all jobs on page
- **Headless Mode**: Use `--headless` for production, remove for debugging

### Alternative: API Discovery (If Available)
**Use Case**: If the site uses internal APIs for data fetching

**Tools**:
- Browser DevTools (Network tab)
- `mitmproxy` or `Charles Proxy` for traffic inspection

**Process**:
1. Monitor network requests while browsing with Selenium
2. Identify API endpoints that return job data (JSON)
3. Reverse engineer API parameters
4. Use direct API calls (more efficient than HTML scraping)

## 3. CSS Selectors Reference

### Complete Selector Mapping:

```python
SELECTORS = {
    # Container
    'job_container': '#projects',
    'job_item': '.project-item.js-project',
    'job_item_featured': '.project-item.js-project.project-item-featured',
    
    # Job Information
    'job_title': 'h2.h3.project-title > span > a',
    'job_url': 'h2.h3.project-title > span > a',  # href attribute
    'job_date': 'div.project-main-details > span.date',
    'job_bids': 'div.project-main-details > span.bids',
    'job_description': 'div.html-desc.project-details > div > p',
    'job_budget': 'p.budget.h4 > span.values > span',
    'job_skills': 'div.skills > div > a.skill.label.label-info > h3',
    'job_featured_badge': 'span.label.label-max',
    
    # Client Information
    'client_name': 'div.project-author > span.author-info > button',
    'client_country': 'div.project-author > span.country > a > span.country-name',
    'client_rating': 'div.project-author > span.rating > span.profile-stars',  # title attribute
    'client_payment_verified': 'div.project-author > span.payment > span.payment-verified',
    'client_last_reply': 'div.project-author > span.message-created > span',
    
    # Pagination
    'pagination': 'nav.text-center > ul.pagination',
    'pagination_pages': 'ul.pagination > li > a',
    'pagination_current': 'ul.pagination > li.active > a',
    'pagination_next': 'ul.pagination > li:not(.disabled) > a[aria-label="Next"]',
}
```

### Example Selenium Code:

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Wait for jobs to load
wait = WebDriverWait(driver, 10)
jobs_container = wait.until(
    EC.presence_of_element_located((By.ID, "projects"))
)

# Find all job items
jobs = driver.find_elements(By.CSS_SELECTOR, ".project-item.js-project")

for job in jobs:
    # Extract title and URL
    title_elem = job.find_element(By.CSS_SELECTOR, "h2.project-title a")
    title = title_elem.text
    url = title_elem.get_attribute("href")
    
    # Extract date
    try:
        date_elem = job.find_element(By.CSS_SELECTOR, "span.date")
        date_text = date_elem.text.replace("Published: ", "")
    except:
        date_text = None
    
    # Extract bids
    try:
        bids_elem = job.find_element(By.CSS_SELECTOR, "span.bids")
        bids_text = bids_elem.text.replace("Bids: ", "")
        bids_count = int(bids_text)
    except:
        bids_count = None
    
    # Extract budget
    try:
        budget_elem = job.find_element(By.CSS_SELECTOR, "p.budget span.values span")
        budget = budget_elem.text
    except:
        budget = None
    
    # Extract skills
    skills = []
    skill_elems = job.find_elements(By.CSS_SELECTOR, "div.skills a.skill h3")
    for skill in skill_elems:
        skills.append(skill.text)
```

## 4. Data Extraction Strategy

### Information to Extract (Based on Actual HTML):

**Core Fields**:
- **Job ID**: Extract from URL slug (e.g., `desenvolvedor-expert-em-webhook-para-correcao-de-integracao-de-pedidos-e-tratamento-de-erros`)
- **Job Title**: `h2.h3.project-title > span > a` (text content)
- **Job URL**: Full URL from `href` attribute (e.g., `/job/...`)
- **Description**: `div.html-desc.project-details > div > p` (may be truncated)
- **Posting Date**: `div.project-main-details > span.date` (relative format: "20 hours ago")
- **Bids Count**: `div.project-main-details > span.bids` (extract number from "Bids: 16")
- **Budget**: `p.budget.h4 > span.values > span` (e.g., "USD 50 - 100", "Over USD 45 / hour")
- **Skills**: `div.skills > div > a.skill > h3` (list of skill names)
- **Is Featured**: Check for `project-item-featured` class or `span.label.label-max`
- **Is Max Project**: Check for `span.label.label-max` badge

**Client Information** (from `div.project-author`):
- **Client Name**: `span.author-info > button` (text content)
- **Client Country**: `span.country > a > span.country-name` (text)
- **Client Rating**: Extract from `span.rating > span.profile-stars` title attribute (e.g., "5.00 of 5.00")
- **Payment Verified**: Check for `span.payment-verified` element
- **Last Reply**: `span.message-created > span` (relative time)

### Extraction Methods (Selenium + BeautifulSoup):

1. **Selenium Element Finding**:
   ```python
   # Wait for jobs to load
   jobs = WebDriverWait(driver, 10).until(
       EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".project-item.js-project"))
   )
   
   # Extract data from each job
   for job in jobs:
       title = job.find_element(By.CSS_SELECTOR, "h2.project-title a").text
       url = job.find_element(By.CSS_SELECTOR, "h2.project-title a").get_attribute("href")
   ```

2. **BeautifulSoup Parsing** (after getting page_source):
   ```python
   soup = BeautifulSoup(driver.page_source, 'lxml')
   jobs = soup.select('.project-item.js-project')
   for job in jobs:
       title = job.select_one('h2.project-title a').text.strip()
       url = job.select_one('h2.project-title a')['href']
   ```

3. **Regex for Data Cleaning**:
   - Extract numbers from "Bids: 16" → `re.search(r'(\d+)', text)`
   - Parse budget ranges → `re.search(r'USD\s+([\d,]+)\s*-\s*([\d,]+)', text)`
   - Extract rating from title attribute → `re.search(r'(\d+\.\d+)', title_attr)`

4. **Date Parsing**:
   - Convert relative dates ("20 hours ago", "Just now") to datetime
   - Use `dateutil.parser` or custom function
   - Store both relative string and calculated timestamp

## 5. Handling Newly Posted Jobs

### Detection Methods:

1. **Job ID Tracking** (Primary Method):
   - Extract unique job ID from URL slug (e.g., `desenvolvedor-expert-em-webhook-para-correcao-de-integracao-de-pedidos-e-tratamento-de-erros`)
   - Maintain a database/registry of seen job IDs
   - Compare current scrape with stored IDs
   - Flag jobs with IDs not in database as "new"

2. **Timestamp Comparison** (Secondary Method):
   - Parse relative dates ("Just now", "20 hours ago") to approximate timestamps
   - Store last scrape timestamp
   - Compare job posting dates with last scrape time
   - Flag jobs posted after last scrape
   - **Note**: Relative dates are approximate, so use job ID as primary method

3. **Incremental Scraping**:
   - Jobs appear to be sorted by "newest first" (based on HTML order)
   - Stop scraping when reaching previously seen job IDs
   - More efficient: only scrape until you hit known jobs

4. **Date-Based Filtering** (If Available):
   - Check if URL supports date filters (e.g., `?publication=1d` for past 24 hours)
   - Use filter to limit scraping to recent jobs only

### Storage for Tracking: SQLite Database

**Why SQLite?**
- **No server setup**: File-based database (single `.db` file)
- **Built into Python**: `sqlite3` module included in standard library
- **Fast performance**: Efficient for thousands of jobs
- **ACID compliant**: Data integrity guaranteed
- **Full SQL support**: Complex queries and indexing
- **Easy backup**: Just copy the database file
- **Portable**: Works across all platforms

**Complete Database Schema**:

```sql
-- Main jobs table
CREATE TABLE jobs (
    id TEXT PRIMARY KEY,                    -- Job URL slug (unique identifier)
    title TEXT NOT NULL,
    description TEXT,
    url TEXT NOT NULL,
    posted_date_relative TEXT,              -- "20 hours ago", "Just now", "Yesterday"
    posted_date_timestamp DATETIME,         -- Calculated absolute timestamp
    bids_count INTEGER,
    budget TEXT,                             -- "USD 50 - 100" or "Over USD 45 / hour"
    budget_min REAL,                         -- Extracted min value (optional)
    budget_max REAL,                         -- Extracted max value (optional)
    budget_type TEXT,                        -- "fixed" or "hourly" or NULL
    skills TEXT,                             -- JSON array or comma-separated string
    client_name TEXT,
    client_country TEXT,
    client_rating REAL,                      -- 0.00 to 5.00
    client_payment_verified BOOLEAN DEFAULT 0,
    client_last_reply TEXT,                  -- Relative time string
    is_featured BOOLEAN DEFAULT 0,
    is_max_project BOOLEAN DEFAULT 0,
    scraped_at DATETIME NOT NULL,
    first_seen_at DATETIME NOT NULL,
    last_seen_at DATETIME NOT NULL
);

-- Scraping history and statistics
CREATE TABLE scrape_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL,
    jobs_found INTEGER,
    new_jobs_count INTEGER,
    pages_scraped INTEGER,
    duration_seconds REAL,
    category TEXT,                           -- e.g., "it-programming"
    language TEXT                            -- e.g., "xx" for all languages
);

-- Indexes for performance optimization
CREATE INDEX idx_job_id ON jobs(id);
CREATE INDEX idx_posted_timestamp ON jobs(posted_date_timestamp);
CREATE INDEX idx_scraped_at ON jobs(scraped_at);
CREATE INDEX idx_first_seen ON jobs(first_seen_at);
CREATE INDEX idx_last_seen ON jobs(last_seen_at);
CREATE INDEX idx_client_country ON jobs(client_country);
CREATE INDEX idx_budget_type ON jobs(budget_type);
CREATE INDEX idx_is_featured ON jobs(is_featured);
CREATE INDEX idx_scrape_timestamp ON scrape_history(timestamp);
```

**Database Implementation Example**:

```python
import sqlite3
from datetime import datetime
from typing import Optional, Dict, List, Set
import json

class WorkanaDatabase:
    """SQLite database manager for Workana job scraping"""
    
    def __init__(self, db_path: str = 'workana_jobs.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # Access columns by name
        self.create_tables()
    
    def create_tables(self):
        """Create database tables if they don't exist"""
        cursor = self.conn.cursor()
        
        # Jobs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                url TEXT NOT NULL,
                posted_date_relative TEXT,
                posted_date_timestamp DATETIME,
                bids_count INTEGER,
                budget TEXT,
                budget_min REAL,
                budget_max REAL,
                budget_type TEXT,
                skills TEXT,
                client_name TEXT,
                client_country TEXT,
                client_rating REAL,
                client_payment_verified BOOLEAN DEFAULT 0,
                client_last_reply TEXT,
                is_featured BOOLEAN DEFAULT 0,
                is_max_project BOOLEAN DEFAULT 0,
                scraped_at DATETIME NOT NULL,
                first_seen_at DATETIME NOT NULL,
                last_seen_at DATETIME NOT NULL
            )
        ''')
        
        # Scrape history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scrape_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                jobs_found INTEGER,
                new_jobs_count INTEGER,
                pages_scraped INTEGER,
                duration_seconds REAL,
                category TEXT,
                language TEXT
            )
        ''')
        
        # Create indexes
        indexes = [
            'CREATE INDEX IF NOT EXISTS idx_posted_timestamp ON jobs(posted_date_timestamp)',
            'CREATE INDEX IF NOT EXISTS idx_scraped_at ON jobs(scraped_at)',
            'CREATE INDEX IF NOT EXISTS idx_first_seen ON jobs(first_seen_at)',
            'CREATE INDEX IF NOT EXISTS idx_last_seen ON jobs(last_seen_at)',
            'CREATE INDEX IF NOT EXISTS idx_client_country ON jobs(client_country)',
            'CREATE INDEX IF NOT EXISTS idx_budget_type ON jobs(budget_type)',
            'CREATE INDEX IF NOT EXISTS idx_is_featured ON jobs(is_featured)',
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        self.conn.commit()
    
    def job_exists(self, job_id: str) -> bool:
        """Check if a job ID exists in database"""
        cursor = self.conn.execute(
            'SELECT id FROM jobs WHERE id = ?', (job_id,)
        )
        return cursor.fetchone() is not None
    
    def get_existing_job_ids(self) -> Set[str]:
        """Get all existing job IDs as a set for fast lookup"""
        cursor = self.conn.execute('SELECT id FROM jobs')
        return {row[0] for row in cursor.fetchall()}
    
    def save_job(self, job_data: Dict) -> bool:
        """
        Save or update a job.
        Returns True if job is new, False if it already existed.
        """
        now = datetime.now()
        is_new = not self.job_exists(job_data['id'])
        
        if is_new:
            # Insert new job
            self.conn.execute('''
                INSERT INTO jobs (
                    id, title, description, url, posted_date_relative,
                    posted_date_timestamp, bids_count, budget, budget_min,
                    budget_max, budget_type, skills, client_name,
                    client_country, client_rating, client_payment_verified,
                    client_last_reply, is_featured, is_max_project,
                    scraped_at, first_seen_at, last_seen_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job_data.get('id'),
                job_data.get('title'),
                job_data.get('description'),
                job_data.get('url'),
                job_data.get('posted_date_relative'),
                job_data.get('posted_date_timestamp'),
                job_data.get('bids_count'),
                job_data.get('budget'),
                job_data.get('budget_min'),
                job_data.get('budget_max'),
                job_data.get('budget_type'),
                json.dumps(job_data.get('skills', [])) if job_data.get('skills') else None,
                job_data.get('client_name'),
                job_data.get('client_country'),
                job_data.get('client_rating'),
                job_data.get('client_payment_verified', False),
                job_data.get('client_last_reply'),
                job_data.get('is_featured', False),
                job_data.get('is_max_project', False),
                now,
                now,
                now
            ))
        else:
            # Update existing job (update last_seen_at and other fields that may have changed)
            self.conn.execute('''
                UPDATE jobs SET
                    title = ?,
                    description = ?,
                    bids_count = ?,
                    budget = ?,
                    budget_min = ?,
                    budget_max = ?,
                    budget_type = ?,
                    skills = ?,
                    client_rating = ?,
                    client_payment_verified = ?,
                    client_last_reply = ?,
                    scraped_at = ?,
                    last_seen_at = ?
                WHERE id = ?
            ''', (
                job_data.get('title'),
                job_data.get('description'),
                job_data.get('bids_count'),
                job_data.get('budget'),
                job_data.get('budget_min'),
                job_data.get('budget_max'),
                job_data.get('budget_type'),
                json.dumps(job_data.get('skills', [])) if job_data.get('skills') else None,
                job_data.get('client_rating'),
                job_data.get('client_payment_verified', False),
                job_data.get('client_last_reply'),
                now,
                now,
                job_data.get('id')
            ))
        
        self.conn.commit()
        return is_new
    
    def get_new_jobs_since(self, since_datetime: datetime) -> List[Dict]:
        """Get all jobs first seen after a specific datetime"""
        cursor = self.conn.execute(
            'SELECT * FROM jobs WHERE first_seen_at > ? ORDER BY first_seen_at DESC',
            (since_datetime,)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def get_jobs_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get jobs posted within a date range"""
        cursor = self.conn.execute(
            '''SELECT * FROM jobs 
               WHERE posted_date_timestamp BETWEEN ? AND ?
               ORDER BY posted_date_timestamp DESC''',
            (start_date, end_date)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def save_scrape_history(self, jobs_found: int, new_jobs_count: int, 
                           pages_scraped: int, duration_seconds: float,
                           category: str = None, language: str = None):
        """Record scraping session statistics"""
        self.conn.execute('''
            INSERT INTO scrape_history 
            (timestamp, jobs_found, new_jobs_count, pages_scraped, duration_seconds, category, language)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (datetime.now(), jobs_found, new_jobs_count, pages_scraped, duration_seconds, category, language))
        self.conn.commit()
    
    def get_last_scrape_time(self) -> Optional[datetime]:
        """Get timestamp of last scrape"""
        cursor = self.conn.execute(
            'SELECT timestamp FROM scrape_history ORDER BY timestamp DESC LIMIT 1'
        )
        row = cursor.fetchone()
        return datetime.fromisoformat(row[0]) if row else None
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        stats = {}
        
        # Total jobs
        cursor = self.conn.execute('SELECT COUNT(*) FROM jobs')
        stats['total_jobs'] = cursor.fetchone()[0]
        
        # Jobs from last 24 hours
        cursor = self.conn.execute('''
            SELECT COUNT(*) FROM jobs 
            WHERE first_seen_at > datetime('now', '-24 hours')
        ''')
        stats['new_jobs_24h'] = cursor.fetchone()[0]
        
        # Total scrape sessions
        cursor = self.conn.execute('SELECT COUNT(*) FROM scrape_history')
        stats['total_scrapes'] = cursor.fetchone()[0]
        
        return stats
    
    def close(self):
        """Close database connection"""
        self.conn.close()
```

**Usage Example**:

```python
# Initialize database
db = WorkanaDatabase('workana_jobs.db')

# Get existing job IDs for fast lookup
existing_ids = db.get_existing_job_ids()

# Process scraped jobs
new_jobs = []
for job_data in scraped_jobs:
    job_id = extract_job_id(job_data['url'])
    job_data['id'] = job_id
    
    is_new = db.save_job(job_data)
    if is_new:
        new_jobs.append(job_data)

# Save scrape history
db.save_scrape_history(
    jobs_found=len(scraped_jobs),
    new_jobs_count=len(new_jobs),
    pages_scraped=pages_scraped,
    duration_seconds=elapsed_time,
    category='it-programming',
    language='xx'
)

# Query new jobs from last hour
from datetime import datetime, timedelta
since = datetime.now() - timedelta(hours=1)
recent_jobs = db.get_new_jobs_since(since)

# Get statistics
stats = db.get_statistics()
print(f"Total jobs: {stats['total_jobs']}")
print(f"New jobs (24h): {stats['new_jobs_24h']}")

db.close()
```

**Alternative: JSON Files** (for simple use cases):
- `jobs.json`: Dictionary with job IDs as keys
- `last_scrape.json`: Metadata about last scrape
- `new_jobs.json`: List of new jobs from last scrape
- **Note**: JSON files are less efficient for large datasets and don't support complex queries

## 6. Project Structure

```
Workana Scraping/
├── config/
│   ├── settings.py          # Configuration (URLs, delays, selectors)
│   └── selectors.py         # CSS/XPath selectors
├── scrapers/
│   ├── base_scraper.py      # Base scraper class
│   ├── static_scraper.py    # HTML-based scraper
│   ├── dynamic_scraper.py   # Selenium/Playwright scraper
│   └── api_scraper.py       # API-based scraper (if discovered)
├── parsers/
│   ├── job_parser.py        # Parse job data from HTML/JSON
│   └── date_parser.py       # Parse and normalize dates
├── storage/
│   ├── database.py          # SQLite database operations (WorkanaDatabase class)
│   └── file_storage.py      # File-based storage (optional, for JSON backup)
├── utils/
│   ├── rate_limiter.py      # Rate limiting utilities
│   ├── logger.py            # Logging setup
│   └── validators.py        # Data validation
├── main.py                  # Main execution script
├── requirements.txt         # Python dependencies
└── README.md               # Documentation
```

## 7. Ethical Scraping Practices

### Rate Limiting:
- **Delay Between Requests**: 2-5 seconds minimum
- **Respectful Crawling**: Don't overwhelm servers
- **Random Delays**: Add randomness to avoid patterns

### Headers & Identification:
- **User-Agent**: Use a descriptive, honest user-agent
- **Referer**: Set appropriate referer headers
- **Cookies**: Handle session cookies if needed

### robots.txt Compliance:
- Check `workana.com/robots.txt`
- Respect disallowed paths
- Honor crawl-delay directives

### Error Handling:
- Handle 429 (Too Many Requests) gracefully
- Implement exponential backoff
- Log errors for debugging
- Don't retry excessively

## 8. Implementation Phases

### Phase 1: Exploration & Setup
1. Manually inspect workana.com structure
2. Identify job listing URLs and patterns
3. Check robots.txt
4. Set up project structure
5. Install dependencies

### Phase 2: Basic Scraper
1. Build basic HTML scraper
2. Extract job listings from first page
3. Test data extraction accuracy
4. Handle basic pagination

### Phase 3: Complete Scraper
1. Implement full pagination handling
2. Extract job details from individual pages
3. Handle edge cases (missing data, errors)
4. Implement rate limiting

### Phase 4: New Job Detection
1. Implement database/storage
2. Add job ID tracking
3. Implement "new job" detection logic
4. Create notification/alert system (optional)

### Phase 5: Robustness & Monitoring
1. Add comprehensive error handling
2. Implement logging
3. Add data validation
4. Create monitoring/alerting for failures

## 9. Tools & Libraries

### Core Libraries (Selenium-Based):
- **selenium**: Browser automation (required)
- **webdriver-manager**: Automatic ChromeDriver management
- **beautifulsoup4**: HTML parsing after Selenium renders
- **lxml**: Fast XML/HTML parser

### Data Handling:
- **pandas**: Data manipulation and analysis (optional)
- **sqlite3**: Database operations (built-in, no installation needed)
- **python-dateutil**: Parse relative dates ("20 hours ago")

### Utilities:
- **python-dotenv**: Environment variables
- **tenacity**: Retry logic with exponential backoff
- **time**: Built-in for delays and rate limiting
- **re**: Built-in for regex pattern matching

### Selenium-Specific:
- **selenium.webdriver.chrome.options**: Chrome options (headless, user-agent)
- **selenium.webdriver.common.by**: Element location strategies
- **selenium.webdriver.support.ui.WebDriverWait**: Explicit waits
- **selenium.webdriver.support.expected_conditions**: Wait conditions

## 10. Challenges & Considerations

### Potential Challenges:

1. **JavaScript Rendering**: 
   - Jobs are loaded via Vue.js
   - **Solution**: Use Selenium with proper waits for elements

2. **Relative Date Parsing**:
   - Dates are in relative format ("Just now", "20 hours ago", "Yesterday")
   - Need to convert to absolute timestamps for comparison
   - **Solution**: Use `dateutil` or custom parser, store both relative and calculated timestamp

3. **Anti-Scraping Measures**:
   - CAPTCHA, rate limiting, IP blocking possible
   - **Solution**: Implement proper rate limiting, use realistic delays, rotate user agents

4. **Pagination**:
   - Standard pagination with page numbers
   - URL pattern: `?category=it-programming&language=xx&page=2`
   - **Solution**: Construct URLs or click pagination links

5. **Truncated Descriptions**:
   - Descriptions may be truncated with "View more" link
   - **Solution**: Extract available text, optionally visit job detail pages for full description

6. **Data Structure Changes**:
   - Website updates may break selectors
   - **Solution**: Use robust selectors, implement fallbacks, regular monitoring

7. **Featured vs Regular Jobs**:
   - Some jobs have `project-item-featured` class
   - May need different handling
   - **Solution**: Check for class, extract accordingly

8. **Lazy Loading**:
   - Jobs may load as you scroll
   - **Solution**: Scroll page or wait for all elements to load

### Mitigation Strategies:

1. **Robust Element Waiting**:
   ```python
   WebDriverWait(driver, 10).until(
       EC.presence_of_element_located((By.CSS_SELECTOR, ".project-item"))
   )
   ```

2. **Rate Limiting**:
   - 3-5 second delays between page requests
   - Random delays to avoid patterns
   - Respect robots.txt

3. **Error Handling**:
   - Try-except blocks for missing elements
   - Log errors for debugging
   - Continue scraping even if one job fails

4. **Selector Fallbacks**:
   - Multiple selector strategies
   - XPath alternatives if CSS selectors fail

5. **Data Validation**:
   - Check for required fields before storing
   - Handle missing data gracefully
   - Store partial data if some fields missing

## 11. Testing Strategy

### Unit Tests:
- Test individual parsers
- Test data extraction functions
- Test date parsing and normalization

### Integration Tests:
- Test full scraping workflow
- Test pagination handling
- Test new job detection

### Manual Verification:
- Compare scraped data with manual inspection
- Verify accuracy of extracted fields
- Test edge cases (missing data, malformed HTML)

## 12. Implementation Plan

### Phase 1: Setup & Basic Scraper
1. **Install Dependencies**:
   ```bash
   pip install selenium webdriver-manager beautifulsoup4 lxml python-dateutil
   ```

2. **Set Up Selenium**:
   - Configure Chrome WebDriver
   - Test basic page loading
   - Verify job elements are accessible

3. **Build Basic Scraper**:
   - Load first page of job listings
   - Extract job titles, URLs, dates
   - Test with 5-10 jobs

### Phase 2: Complete Data Extraction
1. **Extract All Fields**:
   - Title, URL, description, date, bids, budget
   - Skills, client info, rating
   - Handle missing/optional fields

2. **Date Parsing**:
   - Implement relative date to timestamp conversion
   - Handle edge cases ("Just now", "Yesterday", etc.)

3. **Data Storage**:
   - Set up SQLite database
   - Create schema
   - Implement save functions

### Phase 3: Pagination & Scaling
1. **Pagination Handling**:
   - Detect total pages
   - Iterate through pages
   - Handle last page edge cases

2. **Rate Limiting**:
   - Implement delays between requests
   - Add random variation
   - Respect server load

3. **Error Handling**:
   - Handle missing elements
   - Retry logic for failed requests
   - Logging for debugging

### Phase 4: New Job Detection
1. **Job ID Tracking**:
   - Extract unique IDs from URLs
   - Compare with stored jobs
   - Flag new jobs

2. **Incremental Scraping**:
   - Stop when reaching known jobs
   - Optimize for speed

3. **Notification System** (Optional):
   - Alert when new jobs found
   - Export new jobs to file/email

### Phase 5: Robustness & Monitoring
1. **Testing**:
   - Test with different categories
   - Test pagination edge cases
   - Test date parsing accuracy

2. **Monitoring**:
   - Log scraping statistics
   - Track success/failure rates
   - Monitor for selector changes

3. **Documentation**:
   - Document all selectors
   - Create usage guide
   - Document known issues

