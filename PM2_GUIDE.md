# PM2 Deployment Guide for Workana Scraper

Complete guide for deploying the Workana scraper using PM2 on Ubuntu VPS.

## Why PM2?

PM2 is an excellent choice for managing Python applications because it provides:
- ✅ Automatic process restarts on failure
- ✅ Built-in monitoring and logging
- ✅ Easy process management
- ✅ Auto-start on system boot
- ✅ Memory limit monitoring
- ✅ Zero-downtime reloads
- ✅ Beautiful web dashboard (optional)

## Prerequisites

- Ubuntu 20.04+ VPS
- Python 3.8+
- Node.js 16+ (for PM2)
- Google Chrome installed

## Installation

### Step 1: Install Node.js and PM2

```bash
# Install Node.js 18.x LTS
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify Node.js
node --version  # Should show v18.x.x or higher
npm --version   # Should show 9.x.x or higher

# Install PM2 globally
sudo npm install -g pm2

# Verify PM2
pm2 --version
```

### Step 2: Run PM2 Setup Script

```bash
cd /opt/workana-scraper  # or your project directory
chmod +x pm2-setup.sh
./pm2-setup.sh
```

This script will:
- Check/install Node.js and npm
- Install PM2 globally
- Create logs directory
- Update ecosystem.config.js with your current path

### Step 3: Configure ecosystem.config.js

Edit `ecosystem.config.js` and update the `cwd` path if needed:

```javascript
cwd: '/opt/workana-scraper',  // Change to your actual project path
```

### Step 4: Ensure .env File Exists

```bash
nano .env
```

Add your API keys:
```env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
DEEPL_API_KEY=your-deepl-api-key-here
```

## Starting the Scraper

### Start with PM2

```bash
cd /opt/workana-scraper
pm2 start ecosystem.config.js --env production
```

### Save PM2 Process List

This ensures PM2 remembers your processes after reboot:

```bash
pm2 save
```

### Enable PM2 on System Boot

```bash
# Generate startup script (run as regular user)
pm2 startup systemd -u $USER --hp $HOME

# PM2 will output a command like:
# sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u your-username --hp /home/your-username
# Copy and run that command with sudo
```

**Important**: You must run the generated command with `sudo` to enable PM2 on boot.

## PM2 Management Commands

### Basic Commands

```bash
# Check status of all processes
pm2 status

# View logs (real-time)
pm2 logs workana-scraper

# View last 100 lines
pm2 logs workana-scraper --lines 100

# Monitor resources (real-time dashboard)
pm2 monit

# Restart the scraper
pm2 restart workana-scraper

# Stop the scraper
pm2 stop workana-scraper

# Delete from PM2 (stops and removes)
pm2 delete workana-scraper

# Reload (zero-downtime restart)
pm2 reload workana-scraper

# View detailed information
pm2 info workana-scraper

# Show process list
pm2 list
```

### Advanced Commands

```bash
# View all logs (all processes)
pm2 logs

# Clear all logs
pm2 flush

# Restart all processes
pm2 restart all

# Stop all processes
pm2 stop all

# Save current process list
pm2 save

# Delete saved process list
pm2 kill
pm2 save  # This will save an empty list
```

## Log Management

### PM2 Log Locations

PM2 creates logs in the `logs/` directory:
- `logs/pm2-error.log` - Error output
- `logs/pm2-out.log` - Standard output
- `logs/pm2-combined.log` - Combined logs

Your application also writes to `scraper.log` (configured in `config/settings.py`).

### Enable Log Rotation

```bash
# Install PM2 log rotation module
pm2 install pm2-logrotate

# Configure log rotation
pm2 set pm2-logrotate:max_size 10M      # Max log file size
pm2 set pm2-logrotate:retain 7           # Keep 7 days of logs
pm2 set pm2-logrotate:compress true       # Compress old logs
pm2 set pm2-logrotate:dateFormat YYYY-MM-DD_HH-mm-ss
pm2 set pm2-logrotate:workerInterval 30   # Check every 30 seconds
pm2 set pm2-logrotate:rotateInterval 0 0 * * *  # Rotate daily at midnight
```

### View Logs

```bash
# Real-time logs
pm2 logs workana-scraper

# Last 50 lines
pm2 logs workana-scraper --lines 50

# Error logs only
pm2 logs workana-scraper --err

# Output logs only
pm2 logs workana-scraper --out

# No colors (useful for saving)
pm2 logs workana-scraper --no-color > logs.txt
```

## Monitoring

### Real-time Monitoring

```bash
# Open PM2 monitoring dashboard
pm2 monit
```

This shows:
- CPU usage
- Memory usage
- Process uptime
- Restart count
- Log output

### Check Status

```bash
# Quick status
pm2 status

# Detailed info
pm2 info workana-scraper

# Show process tree
pm2 prettylist
```

### Web Dashboard (Optional)

```bash
# Install PM2 web interface
pm2 install pm2-server-monit

# Access at http://your-server-ip:9615
```

## Important PM2 Considerations

### 1. Python Interpreter Path

The `ecosystem.config.js` uses:
```javascript
interpreter: 'venv/bin/python',
```

This is a **relative path** from the `cwd`. Ensure:
- Virtual environment exists at `venv/`
- Python interpreter is at `venv/bin/python`
- Path is correct relative to `cwd`

### 2. Environment Variables

PM2 automatically loads `.env` file from the project directory. You can also define them in `ecosystem.config.js`:

```javascript
env: {
  NODE_ENV: 'production',
  PYTHONUNBUFFERED: '1',  // Important for real-time logs
  SLACK_WEBHOOK_URL: 'your-url',  // Optional: override .env
},
```

**Important**: Set `PYTHONUNBUFFERED=1` to see real-time Python output in logs.

### 3. Auto-restart Configuration

In `ecosystem.config.js`:
```javascript
autorestart: true,           // Auto-restart on crash
max_restarts: 10,            // Max restarts in short time
restart_delay: 4000,         // Delay between restarts (ms)
min_uptime: '10s',           // Consider stable after 10s
```

### 4. Memory Limits

```javascript
max_memory_restart: '2G',  // Restart if memory exceeds 2GB
```

PM2 will automatically restart the process if memory usage exceeds this limit.

### 5. Working Directory

Ensure `cwd` in `ecosystem.config.js` matches your actual project path:
```javascript
cwd: '/opt/workana-scraper',  // Must be absolute path
```

### 6. Startup on Boot

After running `pm2 startup`, you must:
1. Run the generated command with `sudo`
2. Run `pm2 save` to persist your process list

Without both steps, PM2 won't start on boot.

## Troubleshooting

### PM2 Process Not Starting

```bash
# Check PM2 logs
pm2 logs workana-scraper --err

# Check if Python path is correct
pm2 info workana-scraper

# Test Python manually
cd /opt/workana-scraper
source venv/bin/activate
python main.py
```

### PM2 Not Starting on Boot

```bash
# Check if startup script exists
pm2 startup

# Regenerate startup script
pm2 unstartup
pm2 startup systemd -u $USER --hp $HOME

# Ensure process list is saved
pm2 save

# Check systemd service
sudo systemctl status pm2-your-username
```

### High Memory Usage

```bash
# Check memory usage
pm2 monit

# Lower memory limit in ecosystem.config.js
max_memory_restart: '1G',  # Reduce if needed

# Restart with new config
pm2 restart workana-scraper --update-env
```

### Logs Not Appearing

```bash
# Check log directory permissions
ls -la logs/

# Ensure PYTHONUNBUFFERED is set
pm2 env workana-scraper

# Check if logs directory exists
mkdir -p logs
```

### Process Keeps Restarting

```bash
# Check error logs
pm2 logs workana-scraper --err

# Check restart count
pm2 status

# Temporarily disable auto-restart for debugging
pm2 stop workana-scraper
# Then run manually: python main.py
```

## Updating the Scraper

### Update Code

```bash
cd /opt/workana-scraper

# Pull latest changes (if using git)
git pull

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Restart with PM2
pm2 restart workana-scraper
```

### Update Configuration

```bash
# Edit ecosystem.config.js
nano ecosystem.config.js

# Restart with new config
pm2 restart workana-scraper --update-env
```

## Comparison: PM2 vs systemd

| Feature | PM2 | systemd |
|---------|-----|---------|
| Setup Complexity | Easy | Medium |
| Monitoring | Built-in (`pm2 monit`) | Requires external tools |
| Log Management | Built-in rotation | Manual setup needed |
| Web Dashboard | Available | Not available |
| Process Management | Simple commands | Systemctl commands |
| Resource Limits | Easy to configure | More granular control |
| Best For | Development & Production | Production servers |

## Best Practices

1. **Always use `pm2 save`** after making changes
2. **Set memory limits** to prevent resource exhaustion
3. **Enable log rotation** to prevent disk space issues
4. **Monitor regularly** with `pm2 monit` or `pm2 status`
5. **Test manually first** before starting with PM2
6. **Keep ecosystem.config.js in version control**
7. **Never commit `.env` file**

## Quick Reference

```bash
# Start
pm2 start ecosystem.config.js --env production

# Stop
pm2 stop workana-scraper

# Restart
pm2 restart workana-scraper

# View logs
pm2 logs workana-scraper

# Monitor
pm2 monit

# Status
pm2 status

# Save
pm2 save

# Enable on boot
pm2 startup systemd -u $USER --hp $HOME
# Then run the generated sudo command
```

## Support

For PM2-specific issues:
- PM2 Documentation: https://pm2.keymetrics.io/docs/
- PM2 GitHub: https://github.com/Unitech/pm2

For scraper-specific issues, see `DEPLOYMENT.md` troubleshooting section.

