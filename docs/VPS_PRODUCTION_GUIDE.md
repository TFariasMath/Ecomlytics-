# VPS Production Deployment Guide - With Antigravity/Claude

**For AI-Assisted Deployment**  
**Target**: Ubuntu 20.04+ VPS  
**Time Required**: 45-60 minutes  
**Support**: tomas.farias.e@ug.uchile.cl

---

## 🎯 Overview

This guide walks you through deploying the Analytics Pipeline on a production VPS server using Antigravity/Claude Code for assistance. You'll set up:

- ✅ Python environment
- ✅ Application as system services (24/7 running)
- ✅ Nginx reverse proxy
- ✅ SSL/HTTPS with automatic renewal
- ✅ Automated ETL scheduler
- ✅ Firewall and security
- ✅ Automatic backups

**Prerequisites:**
- VPS with Ubuntu 20.04+ (2GB RAM minimum, 4GB recommended)
- SSH access with sudo privileges
- Domain name pointed to VPS IP (optional but recommended)
- WooCommerce and Google Analytics credentials ready

---

## 📋 Quick Checklist

Before starting, have ready:

- [ ] VPS IP address
- [ ] SSH credentials
- [ ] Domain name (if using)
- [ ] WooCommerce URL, Consumer Key, Consumer Secret
- [ ] Google Analytics service account JSON file
- [ ] Google Analytics Property ID

---

## Step 1: Connect and Prepare Server

### Connect via SSH

```bash
ssh your-username@your-vps-ip
```

**If using SSH key:**
```bash
ssh -i /path/to/your-key.pem username@vps-ip
```

### Using Antigravity to Help

**Prompt:**
```
I'm connected to my Ubuntu VPS via SSH. I need to:
1. Update the system
2. Install Python 3.10
3. Install build dependencies

Generate the complete command sequence.
```

### Commands to Run

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.10 and tools
sudo apt install python3.10 python3.10-venv python3-pip git curl wget -y

# Install build dependencies
sudo apt install build-essential libssl-dev libffi-dev python3-dev -y

# Verify installation
python3.10 --version
pip3 --version
git --version
```

**Expected output:**
```
Python 3.10.x
pip 22.x.x
git version 2.x.x
```

---

## Step 2: Upload Code to Server

### Option A: Using Git (Recommended)

**If you have the code in a Git repository:**

```bash
# Navigate to home directory
cd ~

# Clone repository
git clone https://github.com/your-username/analytics-pipeline.git

# Or if private repo:
git clone https://your-username:your-token@github.com/your-username/analytics-pipeline.git

# Navigate to project
cd analytics-pipeline
```

### Option B: Using SCP from Local Machine

**On your LOCAL computer (Windows PowerShell, Mac/Linux Terminal):**

```bash
# Compress the project
tar -czf analytics-pipeline.tar.gz ExtraerDatosGoogleAnalitics_Generic/

# Upload to VPS
scp analytics-pipeline.tar.gz username@vps-ip:/home/username/

# If using SSH key:
scp -i /path/to/key.pem analytics-pipeline.tar.gz username@vps-ip:/home/username/
```

**Back on the VPS:**

```bash
# Extract
cd ~
tar -xzf analytics-pipeline.tar.gz
cd ExtraerDatosGoogleAnalitics_Generic

# Or if it created a subdirectory:
cd analytics-pipeline  # or whatever the directory is named
```

### Option C: Using SFTP (GUI Method)

Use FileZilla, WinSCP, or Cyberduck to upload the entire project folder to `/home/your-username/analytics-pipeline`

---

## Step 3: Set Up Python Environment

```bash
# Ensure you're in the project directory
cd ~/analytics-pipeline

# Create virtual environment
python3.10 -m venv venv

# Activate environment
source venv/bin/activate

# Verify activation (prompt should show (venv))
which python
# Should show: /home/username/analytics-pipeline/venv/bin/python

# Upgrade pip
pip install --upgrade pip

# Install dependencies (this takes 3-5 minutes)
pip install -r requirements.txt
```

**Monitor installation:**
```bash
# If you want to see detailed progress
pip install -r requirements.txt --verbose
```

**If installation fails**, use Antigravity:

**Prompt:**
```
I'm getting this error when running pip install -r requirements.txt:
[PASTE ERROR]

My system is Ubuntu 20.04. How do I fix this?
```

---

## Step 4: Configure Application

### A. Upload Google Analytics JSON

**From your LOCAL machine:**

```bash
# Upload the service account JSON file
scp your-ga4-credentials.json username@vps-ip:/home/username/analytics-pipeline/

# If using SSH key:
scp -i /path/to/key.pem your-ga4-credentials.json username@vps-ip:/home/username/analytics-pipeline/
```

### B. Create .env Configuration

**On the VPS:**

```bash
# Copy template
cp .env.example .env

# Edit configuration
nano .env
```

**Configure these variables:**

```bash
# ===========================================
# WOOCOMMERCE
# ===========================================
WC_URL=https://your-store.com
WC_CONSUMER_KEY=ck_xxxxxxxxxxxxx
WC_CONSUMER_SECRET=cs_xxxxxxxxxxxxx

# ===========================================
# GOOGLE ANALYTICS 4
# ===========================================
GA4_KEY_FILE=your-ga4-credentials.json
GA4_PROPERTY_ID=123456789

# ===========================================
# FACEBOOK (Optional)
# ===========================================
FB_ACCESS_TOKEN=EAAxxxxxxxxx
FB_PAGE_ID=123456789

# ===========================================
# NOTIFICATIONS (Optional)
# ===========================================
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
EMAIL_ALERTS_ENABLED=false

# ===========================================
# DATABASE
# ===========================================
DATABASE_TYPE=sqlite
```

**Save and exit:**
- Press `Ctrl+O` to save
- Press `Enter` to confirm
- Press `Ctrl+X` to exit

**Verify file was saved:**
```bash
cat .env | grep WC_URL
# Should show your WooCommerce URL
```

---

## Step 5: Test Installation

### Test WooCommerce Extraction

```bash
# Make sure venv is activated
source venv/bin/activate

# Run WooCommerce extractor
python etl/extract_woocommerce.py
```

**Expected output:**
```
🚀 Iniciando extracción de WooCommerce
✅ Extracted X orders
✅ Extracción completada
```

**Verify database created:**
```bash
ls -lh data/
# Should show: woocommerce.db with size > 0
```

### Test Google Analytics Extraction

```bash
python etl/extract_analytics.py
```

**If you get errors**, use Antigravity:

**Prompt:**
```
I'm testing the ETL extraction and getting this error:
[PASTE ERROR]

The error is from this file: etl/extract_woocommerce.py
My .env configuration has:
- WC_URL correct
- WC_CONSUMER_KEY configured
- WC_CONSUMER_SECRET configured

What's wrong and how do I fix it?
```

### Test Dashboard (Temporarily)

```bash
# Test that dashboard starts
streamlit run dashboard/app_woo_v2.py --server.port 8501 --server.address 0.0.0.0
```

**Access in browser:**
- Open: `http://your-vps-ip:8501`
- Dashboard should load with data

**Stop the test:**
- Press `Ctrl+C` in terminal

---

## Step 6: Configure Systemd Services

### A. Create Dashboard Service

```bash
sudo nano /etc/systemd/system/analytics-dashboard.service
```

**Paste this configuration** (replace `username` with YOUR username):

```ini
[Unit]
Description=Analytics Dashboard - Streamlit Application
After=network.target
Documentation=https://github.com/your-repo/analytics-pipeline

[Service]
Type=simple
User=username
Group=username
WorkingDirectory=/home/username/analytics-pipeline
Environment="PATH=/home/username/analytics-pipeline/venv/bin"
Environment="PYTHONUNBUFFERED=1"
ExecStart=/home/username/analytics-pipeline/venv/bin/streamlit run dashboard/app_woo_v2.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**💡 Tip:** Replace `username` with your actual username. Find it with:
```bash
whoami
```

### B. Create Scheduler Service

```bash
sudo nano /etc/systemd/system/analytics-scheduler.service
```

**Paste this:**

```ini
[Unit]
Description=Analytics ETL Scheduler
After=network.target
Documentation=https://github.com/your-repo/analytics-pipeline

[Service]
Type=simple
User=username
Group=username
WorkingDirectory=/home/username/analytics-pipeline
Environment="PATH=/home/username/analytics-pipeline/venv/bin"
Environment="PYTHONUNBUFFERED=1"
ExecStart=/home/username/analytics-pipeline/venv/bin/python scheduler.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### C. Enable and Start Services

```bash
# Reload systemd to read new service files
sudo systemctl daemon-reload

# Enable services (start on boot)
sudo systemctl enable analytics-dashboard
sudo systemctl enable analytics-scheduler

# Start services now
sudo systemctl start analytics-dashboard
sudo systemctl start analytics-scheduler

# Check status
sudo systemctl status analytics-dashboard
sudo systemctl status analytics-scheduler
```

**Expected output:**
```
● analytics-dashboard.service - Analytics Dashboard
   Loaded: loaded
   Active: active (running)
```

**If service fails**, check logs:
```bash
sudo journalctl -u analytics-dashboard -n 50 --no-pager
```

**Use Antigravity for troubleshooting:**

**Prompt:**
```
My systemd service analytics-dashboard is failing. Here are the logs:
[PASTE LOGS from journalctl command]

The service file is configured for user "username" and workdir "/home/username/analytics-pipeline"

What's wrong and how do I fix it?
```

---

## Step 7: Install and Configure Nginx

### Install Nginx

```bash
sudo apt install nginx -y

# Start and enable
sudo systemctl start nginx
sudo systemctl enable nginx

# Verify it's running
sudo systemctl status nginx
```

### Configure Nginx for the Dashboard

```bash
sudo nano /etc/nginx/sites-available/analytics
```

**For HTTP (testing):**

```nginx
server {
    listen 80;
    server_name your-domain.com;  # or your VPS IP

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Increase timeouts for large data processing
        proxy_connect_timeout 600;
        proxy_send_timeout 600;
        proxy_read_timeout 600;
    }
}
```

**Enable the configuration:**

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/analytics /etc/nginx/sites-enabled/

# Remove default site (optional)
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

**Test in browser:**
- Visit: `http://your-domain.com` or `http://your-vps-ip`
- Dashboard should appear

---

## Step 8: Set Up SSL/HTTPS with Let's Encrypt

### Install Certbot

```bash
sudo apt install certbot python3-certbot-nginx -y
```

### Obtain SSL Certificate

```bash
# Replace with your domain
sudo certbot --nginx -d your-domain.com

# If you have multiple domains:
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

**Follow the prompts:**
1. Enter your email
2. Agree to terms of service (Y)
3. Choose whether to redirect HTTP to HTTPS (recommended: 2 for redirect)

**Certbot will automatically:**
- ✅ Obtain SSL certificate
- ✅ Modify nginx configuration
- ✅ Set up auto-renewal

**Verify auto-renewal:**
```bash
sudo certbot renew --dry-run
```

**Now access via HTTPS:**
- Visit: `https://your-domain.com`
- Should show secure padlock 🔒

---

## Step 9: Configure Firewall

### Set Up UFW (Uncomplicated Firewall)

```bash
# Allow SSH (IMPORTANT: do this first!)
sudo ufw allow 22/tcp

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Block direct access to Streamlit port
sudo ufw deny 8501/tcp

# Enable firewall
sudo ufw --force enable

# Check status
sudo ufw status numbered
```

**Expected output:**
```
Status: active

     To                         Action      From
     --                         ------      ----
[ 1] 22/tcp                     ALLOW IN    Anywhere
[ 2] 80/tcp                     ALLOW IN    Anywhere
[ 3] 443/tcp                    ALLOW IN    Anywhere
[ 4] 8501/tcp                   DENY IN     Anywhere
```

---

## Step 10: Set Up Automated Backups

### Create Backup Script

```bash
# Create backups directory
mkdir -p ~/backups

# Create backup script
nano ~/backup-analytics.sh
```

**Paste this:**

```bash
#!/bin/bash
# Analytics Pipeline Database Backup Script

BACKUP_DIR=~/backups
PROJECT_DIR=~/analytics-pipeline/data
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup
cp $PROJECT_DIR/*.db $BACKUP_DIR/backup_$DATE.db 2>/dev/null

# Keep only last 30 days
find $BACKUP_DIR -name "backup_*.db" -mtime +30 -delete

echo "Backup completed: backup_$DATE.db"
```

**Make executable:**
```bash
chmod +x ~/backup-analytics.sh

# Test it
~/backup-analytics.sh

# Verify backup created
ls -lh ~/backups/
```

### Schedule with Cron

```bash
crontab -e

# If asked, choose nano (option 1)
```

**Add this line at the end:**

```cron
# Daily backup at 1:00 AM
0 1 * * * /home/username/backup-analytics.sh >> /home/username/backups/backup.log 2>&1
```

**Save and exit** (Ctrl+O, Enter, Ctrl+X)

**Verify cron job:**
```bash
crontab -l
```

---

## Step 11: Monitoring and Maintenance

### View Service Logs

```bash
# Dashboard logs (live)
sudo journalctl -u analytics-dashboard -f

# Scheduler logs (live)
sudo journalctl -u analytics-scheduler -f

# Application logs
tail -f ~/analytics-pipeline/logs/etl.log

# View last 100 lines
sudo journalctl -u analytics-dashboard -n 100 --no-pager
```

### Check Service Status

```bash
# Quick status
systemctl is-active analytics-dashboard
systemctl is-active analytics-scheduler

# Detailed status
sudo systemctl status analytics-dashboard
sudo systemctl status analytics-scheduler
```

### Restart Services

```bash
# Restart dashboard
sudo systemctl restart analytics-dashboard

# Restart scheduler
sudo systemctl restart analytics-scheduler

# Restart both
sudo systemctl restart analytics-dashboard analytics-scheduler
```

### View Database Contents

```bash
cd ~/analytics-pipeline
source venv/bin/activate
python scripts/view_db.py
```

---

## Step 12: Verification Checklist

After completing all steps, verify:

### ✅ Services Running

```bash
sudo systemctl status analytics-dashboard
sudo systemctl status analytics-scheduler
```

Both should show: `Active: active (running)`

### ✅ Dashboard Accessible

- Visit: `https://your-domain.com`
- Dashboard loads successfully
- Shows "Analytics Pipeline" header
- Has data (if ETL ran)

### ✅ SSL Working

- Padlock icon in browser
- No security warnings
- Auto-redirects HTTP → HTTPS

### ✅ ETL Scheduler Working

```bash
# Check next scheduled runs
cd ~/analytics-pipeline
source venv/bin/activate
python -c "from scheduler import scheduler; jobs = scheduler.get_jobs(); [print(f'{j.id}: {j.next_run_time}') for j in jobs]"
```

### ✅ Backups Working

```bash
ls -lh ~/backups/
# Should show backup files
```

### ✅ Firewall Active

```bash
sudo ufw status
# Should show: Status: active
```

---

## 🆘 Troubleshooting with Antigravity

### Dashboard Not Loading

**Diagnostic commands:**
```bash
sudo systemctl status analytics-dashboard
sudo journalctl -u analytics-dashboard -n 50
curl http://localhost:8501
```

**Antigravity Prompt:**
```
My analytics dashboard service is not loading. Here is the status and logs:

Status:
[PASTE output of systemctl status]

Logs:
[PASTE output of journalctl]

What's the issue and how do I fix it?
```

### Scheduler Not Running ETL

**Diagnostic:**
```bash
sudo systemctl status analytics-scheduler
sudo journalctl -u analytics-scheduler -n 50
cat ~/analytics-pipeline/logs/etl.log | tail -n 30
```

**Antigravity Prompt:**
```
The ETL scheduler service is running but not executing extractions. 

Scheduler logs:
[PASTE journalctl output]

Application logs:
[PASTE etl.log content]

What could be wrong?
```

### SSL Certificate Issues

**Diagnostic:**
```bash
sudo certbot certificates
sudo nginx -t
```

**Antigravity Prompt:**
```
I'm having SSL certificate issues. Here's the certbot output:
[PASTE output]

And nginx configuration test:
[PASTE nginx -t output]

How do I fix this?
```

### Database Errors

**Antigravity Prompt:**
```
I'm getting database errors in the application. Here's the error:
[PASTE ERROR]

The database file exists at: ~/analytics-pipeline/data/woocommerce.db
File permissions: [PASTE output of ls -lh data/woocommerce.db]

What's wrong?
```

---

## 📊 Performance Optimization (Optional)

### Increase Streamlit Performance

Edit dashboard service:
```bash
sudo nano /etc/systemd/system/analytics-dashboard.service
```

Add to ExecStart:
```
--server.maxMessageSize 500
```

### Enable WAL Mode for SQLite

```bash
cd ~/analytics-pipeline
source venv/bin/activate
python -c "
import sqlite3
for db in ['data/woocommerce.db', 'data/analytics.db']:
    conn = sqlite3.connect(db)
    conn.execute('PRAGMA journal_mode=WAL')
    conn.close()
print('WAL mode enabled')
"
```

---

## 🔄 Updating the Application

### Pull Latest Code

```bash
cd ~/analytics-pipeline

# Backup current .env
cp .env .env.backup

# Pull updates
git pull

# Or if you uploaded new files via SCP, extract them

# Activate environment
source venv/bin/activate

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart services
sudo systemctl restart analytics-dashboard
sudo systemctl restart analytics-scheduler

# Verify
sudo systemctl status analytics-dashboard analytics-scheduler
```

---

## 📞 Getting Help

### Check Documentation

1. **Troubleshooting Guide**: `docs/TROUBLESHOOTING.md`
2. **Developer Guide**: `docs/DEVELOPER_GUIDE.md`
3. **API Reference**: `docs/API_REFERENCE.md`

### Use Antigravity Effectively

**Good prompt structure:**
```
Problem: [Clear description]

Context:
- OS: Ubuntu 20.04
- Service: analytics-dashboard
- What I was doing: [specific action]

Error/Output:
[PASTE EXACT ERROR OR OUTPUT]

What I've tried:
1. [First attempt]
2. [Second attempt]

How do I fix this?
```

### Contact Support

**Email**: tomas.farias.e@ug.uchile.cl

Include:
- Description of the issue
- Output of diagnostic commands
- What you've tried
- Service logs if relevant

---

## ✅ Success Criteria

Your deployment is successful when:

- ✅ Dashboard accessible via HTTPS
- ✅ No security warnings
- ✅ Dashboard shows data
- ✅ Services survive server reboot
- ✅ ETL runs on schedule (check logs next day)
- ✅ Backups being created
- ✅ Firewall protecting unused ports

---

## 🎉 You're Done!

Your Analytics Pipeline is now running 24/7 on your VPS!

**What happens now:**
- Dashboard is accessible at your domain
- ETL extracts data automatically (default: 2 AM GA4, 3 AM WooCommerce)
- Databases backed up daily
- SSL renews automatically
- Services restart if they crash

**Recommended next steps:**
1. Set up monitoring alerts (email/Slack)
2. Review data quality after first few days
3. Customize dashboard for your needs
4. Document any custom configurations

---

**Last Updated**: January 14, 2026  
**Version**: 1.0  
**Support**: tomas.farias.e@ug.uchile.cl
