#!/bin/bash
# PM2 Setup Script for Workana Scraper on Ubuntu VPS

set -e

echo "=========================================="
echo "Workana Scraper - PM2 Setup"
echo "=========================================="

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo "Please do not run as root. Run as a regular user with sudo privileges."
   exit 1
fi

# Get current directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo ""
echo "[1/5] Checking Node.js and npm..."
if ! command -v node &> /dev/null; then
    echo "Node.js not found. Installing Node.js 18.x LTS..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y nodejs
    echo "✅ Node.js installed: $(node --version)"
else
    echo "✅ Node.js already installed: $(node --version)"
fi

if ! command -v npm &> /dev/null; then
    echo "npm not found. Installing..."
    sudo apt-get install -y npm
    echo "✅ npm installed: $(npm --version)"
else
    echo "✅ npm already installed: $(npm --version)"
fi

echo ""
echo "[2/5] Installing PM2 globally..."
if ! command -v pm2 &> /dev/null; then
    sudo npm install -g pm2
    echo "✅ PM2 installed: $(pm2 --version)"
else
    echo "✅ PM2 already installed: $(pm2 --version)"
fi

echo ""
echo "[3/5] Creating logs directory..."
mkdir -p "$SCRIPT_DIR/logs"
touch "$SCRIPT_DIR/logs/pm2-error.log"
touch "$SCRIPT_DIR/logs/pm2-out.log"
touch "$SCRIPT_DIR/logs/pm2-combined.log"
chmod 644 "$SCRIPT_DIR/logs"/*.log
echo "✅ Logs directory created"

echo ""
echo "[4/5] Updating ecosystem.config.js with current path..."
# Update the path in ecosystem.config.js
CURRENT_PATH=$(pwd)
sed -i "s|/opt/workana-scraper|$CURRENT_PATH|g" ecosystem.config.js
echo "✅ Ecosystem config updated with path: $CURRENT_PATH"

echo ""
echo "[5/5] Setting up PM2 startup script..."
# Generate startup script
pm2 startup systemd -u $USER --hp $HOME
echo ""
echo "⚠️  IMPORTANT: Run the command shown above with sudo to enable PM2 on boot"

echo ""
echo "=========================================="
echo "PM2 Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Ensure .env file exists with your API keys:"
echo "   nano .env"
echo ""
echo "2. Start the scraper with PM2:"
echo "   pm2 start ecosystem.config.js --env production"
echo ""
echo "3. Save PM2 process list (for auto-restart on reboot):"
echo "   pm2 save"
echo ""
echo "4. Enable PM2 on system boot (run the command from above):"
echo "   sudo env PATH=\$PATH:/usr/bin pm2 startup systemd -u $USER --hp $HOME"
echo ""
echo "5. Useful PM2 commands:"
echo "   pm2 status              # Check status"
echo "   pm2 logs workana-scraper # View logs"
echo "   pm2 monit               # Monitor resources"
echo "   pm2 restart workana-scraper  # Restart"
echo "   pm2 stop workana-scraper     # Stop"
echo "   pm2 delete workana-scraper    # Remove from PM2"
echo ""
echo "For detailed PM2 instructions, see DEPLOYMENT.md"
echo ""

