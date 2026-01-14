# Deployment Guide for Ubuntu VPS

This guide covers deploying the Workana scraper to an Ubuntu VPS server.

## Prerequisites

- Ubuntu 20.04+ (recommended: 22.04 LTS)
- Python 3.8+ (check with `python3 --version`)
- sudo/root access
- At least 2GB RAM (4GB+ recommended for Chrome)
- Stable internet connection

## 1. System Dependencies

### Install Chrome/Chromium and ChromeDriver

```bash
# Update package list
sudo apt update

# Install required system packages
sudo apt install -y \
    python3-pip \
    python3-venv \
    wget \
    curl \
    unzip \
    gnupg \
    software-properties-common \
    apt-transport-https \
    ca-certificates

# Install Google Chrome
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install -y google-chrome-stable

# Verify Chrome installation
google-chrome --version

# ChromeDriver is automatically managed by webdriver-manager, but you can install it manually:
# Download ChromeDriver (match your Chrome version)
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+\.\d+' | head -1)
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION%.*.*}")
wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
sudo unzip /tmp/chromedriver.zip -d /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
```

### Alternative: Use Chromium (lighter weight)

```bash
sudo apt install -y chromium-browser chromium-chromedriver
```

## 2. Project Setup

### Clone/Upload Project

```bash
# Create project directory
sudo mkdir -p /opt/workana-scraper
sudo chown $USER:$USER /opt/workana-scraper

# Upload your project files or clone from git
cd /opt/workana-scraper
# ... upload your files here ...
```

### Create Python Virtual Environment

```bash
cd /opt/workana-scraper
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

## 3. Environment Configuration

### Create .env File

```bash
cd /opt/workana-scraper
nano .env
```

Add your configuration:

```env
# Slack Webhook (optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# DeepL API Key (optional)
DEEPL_API_KEY=your-deepl-api-key-here
```

**Important:** Never commit `.env` to version control!

### Set Proper Permissions

```bash
# Make .env readable only by owner
chmod 600 .env

# Ensure database directory is writable
chmod 755 /opt/workana-scraper
```

## 4. Test the Installation

```bash
cd /opt/workana-scraper
source venv/bin/activate

# Test run (single scrape)
python main.py

# If SCRAPE_INTERVAL is set, press Ctrl+C to stop after testing
```

## 5. Run as a Systemd Service (Recommended)

### Create Service File

```bash
sudo nano /etc/systemd/system/workana-scraper.service
```

Add the following content:

```ini
[Unit]
Description=Workana Job Scraper
After=network.target

[Service]
Type=simple
User=your-username
Group=your-username
WorkingDirectory=/opt/workana-scraper
Environment="PATH=/opt/workana-scraper/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/opt/workana-scraper/venv/bin/python /opt/workana-scraper/main.py
Restart=always
RestartSec=10
StandardOutput=append:/opt/workana-scraper/scraper.log
StandardError=append:/opt/workana-scraper/scraper.log

# Resource limits (adjust based on your VPS)
MemoryLimit=2G
CPUQuota=50%

[Install]
WantedBy=multi-user.target
```

**Important:** Replace `your-username` with your actual username!

### Enable and Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable workana-scraper

# Start the service
sudo systemctl start workana-scraper

# Check status
sudo systemctl status workana-scraper

# View logs
sudo journalctl -u workana-scraper -f
# Or view the log file directly
tail -f /opt/workana-scraper/scraper.log
```

### Service Management Commands

```bash
# Stop service
sudo systemctl stop workana-scraper

# Restart service
sudo systemctl restart workana-scraper

# Check status
sudo systemctl status workana-scraper

# Disable auto-start on boot
sudo systemctl disable workana-scraper
```

## 6. Alternative: Using PM2

PM2 is a popular process manager that works well for Python applications. It provides excellent monitoring, logging, and auto-restart capabilities.

### Install Node.js and PM2

```bash
# Install Node.js 18.x LTS
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install PM2 globally
sudo npm install -g pm2

# Verify installation
node --version
npm --version
pm2 --version
```

### Configure PM2

1. **Update ecosystem.config.js**:
   - Edit `ecosystem.config.js` and change the `cwd` path to your project directory
   - The file is already configured with appropriate settings

2. **Create logs directory**:
   ```bash
   mkdir -p /opt/workana-scraper/logs
   ```

3. **Start the scraper**:
   ```bash
   cd /opt/workana-scraper
   pm2 start ecosystem.config.js --env production
   ```

4. **Save PM2 process list** (for persistence):
   ```bash
   pm2 save
   ```

5. **Enable PM2 on system boot**:
   ```bash
   pm2 startup systemd -u your-username --hp /home/your-username
   # Run the command that PM2 outputs (it will include sudo)
   ```

### PM2 Management Commands

```bash
# Check status
pm2 status

# View logs
pm2 logs workana-scraper
pm2 logs workana-scraper --lines 100  # Last 100 lines

# Monitor resources (real-time)
pm2 monit

# Restart
pm2 restart workana-scraper

# Stop
pm2 stop workana-scraper

# Delete from PM2
pm2 delete workana-scraper

# Reload (zero-downtime restart)
pm2 reload workana-scraper

# View detailed info
pm2 info workana-scraper

# Save current process list
pm2 save

# List all processes
pm2 list
```

### PM2 Log Management

PM2 automatically manages logs, but you can configure rotation:

```bash
# Install PM2 log rotation module
pm2 install pm2-logrotate

# Configure log rotation
pm2 set pm2-logrotate:max_size 10M
pm2 set pm2-logrotate:retain 7
pm2 set pm2-logrotate:compress true
```

### PM2 Important Considerations

1. **Python Interpreter Path**: 
   - The `ecosystem.config.js` uses `venv/bin/python` as interpreter
   - Ensure the virtual environment path is correct

2. **Environment Variables**:
   - PM2 reads from `.env` file automatically
   - You can also add them in `ecosystem.config.js` under `env` section
   - `PYTHONUNBUFFERED=1` is set to ensure real-time log output

3. **Auto-restart**:
   - PM2 automatically restarts on failure
   - Configured with `max_restarts: 10` and `restart_delay: 4000`

4. **Memory Limits**:
   - Set `max_memory_restart: '2G'` in config
   - PM2 will restart if memory exceeds this limit

5. **Log Files**:
   - Logs go to `./logs/pm2-error.log`, `./logs/pm2-out.log`, and `./logs/pm2-combined.log`
   - These are separate from your `scraper.log` file

6. **Startup on Boot**:
   - Must run `pm2 startup` and execute the generated command
   - Then run `pm2 save` to persist the process list

### Quick PM2 Setup Script

Use the provided `pm2-setup.sh` script:

```bash
chmod +x pm2-setup.sh
./pm2-setup.sh
```

This will:
- Install Node.js and npm if needed
- Install PM2 globally
- Create logs directory
- Update ecosystem.config.js with current path
- Generate PM2 startup command

## 7. Alternative: Using Supervisor

If you prefer Supervisor over systemd or PM2:

```bash
# Install supervisor
sudo apt install -y supervisor

# Create config file
sudo nano /etc/supervisor/conf.d/workana-scraper.conf
```

Add:

```ini
[program:workana-scraper]
command=/opt/workana-scraper/venv/bin/python /opt/workana-scraper/main.py
directory=/opt/workana-scraper
user=your-username
autostart=true
autorestart=true
stderr_logfile=/opt/workana-scraper/scraper-error.log
stdout_logfile=/opt/workana-scraper/scraper.log
environment=PATH="/opt/workana-scraper/venv/bin"
```

Then:

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start workana-scraper
```

## 8. Important Considerations

### Memory Management

- Chrome/Chromium can be memory-intensive
- Monitor memory usage: `free -h`
- Consider using `--memory-pressure-off` Chrome flag if needed
- Set appropriate `MemoryLimit` in systemd service

### Disk Space

- Database file (`workana_jobs.db`) will grow over time
- Log files can accumulate
- Set up log rotation:

```bash
sudo nano /etc/logrotate.d/workana-scraper
```

Add:

```
/opt/workana-scraper/scraper.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 your-username your-username
}
```

### Network & Firewall

- Ensure outbound HTTPS (443) is allowed
- No inbound ports needed (unless you add a web interface)
- Consider rate limiting to avoid IP bans

### Security

1. **File Permissions:**
   ```bash
   chmod 600 .env
   chmod 644 *.py
   chmod 755 /opt/workana-scraper
   ```

2. **Run as Non-Root User:**
   - Always run the service as a regular user, not root
   - Use `User=` in systemd service file

3. **Environment Variables:**
   - Never commit `.env` file
   - Use strong API keys
   - Rotate keys periodically

4. **Firewall (UFW):**
   ```bash
   sudo ufw allow 22/tcp  # SSH
   sudo ufw enable
   ```

### Monitoring

1. **Check Service Status:**
   ```bash
   sudo systemctl status workana-scraper
   ```

2. **Monitor Logs:**
   ```bash
   tail -f /opt/workana-scraper/scraper.log
   sudo journalctl -u workana-scraper -n 100
   ```

3. **Check Resource Usage:**
   ```bash
   htop  # or top
   df -h  # disk space
   free -h  # memory
   ```

4. **Database Health:**
   ```bash
   sqlite3 /opt/workana-scraper/workana_jobs.db "SELECT COUNT(*) FROM jobs;"
   ```

### Troubleshooting

#### Chrome/ChromeDriver Issues

```bash
# Check Chrome version
google-chrome --version

# Test Chrome headless
google-chrome --headless --disable-gpu --dump-dom https://www.google.com

# Check if ChromeDriver is in PATH
which chromedriver
chromedriver --version
```

#### Permission Issues

```bash
# Fix ownership
sudo chown -R your-username:your-username /opt/workana-scraper

# Fix permissions
chmod +x /opt/workana-scraper/main.py
```

#### Service Won't Start

```bash
# Check service logs
sudo journalctl -u workana-scraper -n 50

# Check if Python path is correct
which python3
/opt/workana-scraper/venv/bin/python --version

# Test manual run
cd /opt/workana-scraper
source venv/bin/activate
python main.py
```

#### Out of Memory

- Reduce `MAX_PAGES` in `config/settings.py`
- Increase VPS RAM
- Add swap space:
  ```bash
  sudo fallocate -l 2G /swapfile
  sudo chmod 600 /swapfile
  sudo mkswap /swapfile
  sudo swapon /swapfile
  echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
  ```

## 9. Updates and Maintenance

### Updating the Scraper

```bash
cd /opt/workana-scraper
source venv/bin/activate

# Pull latest changes (if using git)
git pull

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart service
sudo systemctl restart workana-scraper
```

### Database Backup

```bash
# Create backup script
nano /opt/workana-scraper/backup.sh
```

Add:

```bash
#!/bin/bash
BACKUP_DIR="/opt/workana-scraper/backups"
mkdir -p $BACKUP_DIR
cp /opt/workana-scraper/workana_jobs.db "$BACKUP_DIR/workana_jobs_$(date +%Y%m%d_%H%M%S).db"
# Keep only last 7 days
find $BACKUP_DIR -name "*.db" -mtime +7 -delete
```

Make executable and add to crontab:

```bash
chmod +x /opt/workana-scraper/backup.sh
crontab -e
# Add: 0 2 * * * /opt/workana-scraper/backup.sh
```

## 10. Performance Optimization

### For Low-Resource VPS

Edit `config/settings.py`:

```python
# Reduce memory usage
MAX_PAGES = 1
IMPLICIT_WAIT = 2
PAGE_LOAD_TIMEOUT = 15

# Add more Chrome options for low memory
CHROME_OPTIONS = [
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--disable-gpu',
    '--disable-software-rasterizer',
    '--disable-background-timer-throttling',
    '--disable-backgrounding-occluded-windows',
    '--disable-renderer-backgrounding',
    '--memory-pressure-off',  # Disable memory pressure features
    '--max_old_space_size=512',  # Limit V8 heap size
]
```

## 11. Quick Setup Script

Save this as `setup-ubuntu.sh` and run it:

```bash
#!/bin/bash
set -e

echo "Setting up Workana Scraper on Ubuntu..."

# Install system dependencies
sudo apt update
sudo apt install -y python3-pip python3-venv wget curl unzip

# Install Chrome
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install -y google-chrome-stable

# Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "Setup complete! Don't forget to:"
echo "1. Create .env file with your API keys"
echo "2. Test run: python main.py"
echo "3. Set up systemd service (see DEPLOYMENT.md)"
```

## Support

If you encounter issues:

1. Check logs: `tail -f scraper.log`
2. Check service status: `sudo systemctl status workana-scraper`
3. Test manually: `python main.py`
4. Verify Chrome: `google-chrome --version`

