# Ubuntu VPS Deployment Checklist

Use this checklist to ensure a smooth deployment.

## Pre-Deployment

- [ ] Ubuntu 20.04+ installed
- [ ] At least 2GB RAM available (4GB+ recommended)
- [ ] Python 3.8+ installed (`python3 --version`)
- [ ] sudo/root access available
- [ ] Stable internet connection

## System Setup

- [ ] System packages updated (`sudo apt update && sudo apt upgrade`)
- [ ] Google Chrome installed and verified (`google-chrome --version`)
- [ ] ChromeDriver accessible (managed by webdriver-manager)

## Project Setup

- [ ] Project files uploaded to `/opt/workana-scraper` (or your preferred location)
- [ ] Python virtual environment created (`python3 -m venv venv`)
- [ ] Virtual environment activated (`source venv/bin/activate`)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] All Python packages installed successfully

## Configuration

- [ ] `.env` file created with API keys
- [ ] `.env` file permissions set to 600 (`chmod 600 .env`)
- [ ] `SLACK_WEBHOOK_URL` configured (if using Slack)
- [ ] `DEEPL_API_KEY` configured (if using translation)
- [ ] `config/settings.py` reviewed and adjusted if needed
- [ ] Database directory is writable

## Testing

- [ ] Manual test run successful (`python main.py`)
- [ ] Scraper successfully connects to Workana
- [ ] Jobs are being scraped and saved
- [ ] Database file created (`workana_jobs.db`)
- [ ] Slack notifications working (if enabled)
- [ ] Logs are being written to `scraper.log`

## Service Setup (systemd)

- [ ] `workana-scraper.service` file created
- [ ] `YOUR_USERNAME` replaced with actual username in service file
- [ ] Service file copied to `/etc/systemd/system/`
- [ ] systemd daemon reloaded (`sudo systemctl daemon-reload`)
- [ ] Service enabled for auto-start (`sudo systemctl enable workana-scraper`)
- [ ] Service started successfully (`sudo systemctl start workana-scraper`)
- [ ] Service status verified (`sudo systemctl status workana-scraper`)

## Monitoring & Maintenance

- [ ] Log rotation configured (`/etc/logrotate.d/workana-scraper`)
- [ ] Database backup script created (optional but recommended)
- [ ] Cron job for backups set up (if using backups)
- [ ] Monitoring method established (logs, status checks)
- [ ] Resource limits configured in service file (if needed)

## Security

- [ ] Service running as non-root user
- [ ] File permissions set correctly
- [ ] `.env` file not committed to version control
- [ ] Firewall configured (UFW) if needed
- [ ] SSH access secured

## Post-Deployment Verification

- [ ] Service running after server reboot
- [ ] Scraper continues running after 24 hours
- [ ] No memory leaks or excessive resource usage
- [ ] Logs are rotating properly
- [ ] Database growing as expected
- [ ] Notifications working consistently

## Troubleshooting Resources

- [ ] Know how to check service status
- [ ] Know how to view logs
- [ ] Know how to restart service
- [ ] Know how to check resource usage
- [ ] Have access to DEPLOYMENT.md for reference

## Quick Commands Reference

```bash
# Service management
sudo systemctl status workana-scraper
sudo systemctl start workana-scraper
sudo systemctl stop workana-scraper
sudo systemctl restart workana-scraper
sudo systemctl enable workana-scraper
sudo systemctl disable workana-scraper

# View logs
tail -f /opt/workana-scraper/scraper.log
sudo journalctl -u workana-scraper -f
sudo journalctl -u workana-scraper -n 100

# Check resources
free -h
df -h
htop

# Test manually
cd /opt/workana-scraper
source venv/bin/activate
python main.py
```

