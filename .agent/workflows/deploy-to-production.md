---
description: How to deploy the application to production
---

# Deploy to Production

This workflow covers deploying the Analytics Pipeline to a production environment.

## Deployment Options

Choose deployment method based on your infrastructure:

1. **Docker** - Recommended for most cases
2. **VPS/Cloud Server** - More control, requires management
3. **Streamlit Cloud** - Simplest, limited control

## Option 1: Docker Deployment (Recommended)

### Prerequisites

- Docker and Docker Compose installed
- Server with public IP (or cloud instance)
- Domain name (optional but recommended)

### Steps

####  1. Prepare Environment

```bash
# On your production server
git clone [repository-url] analytics-pipeline
cd analytics-pipeline
```

#### 2. Configure Environment

```bash
# Copy and edit configuration
cp .env.example .env
nano .env  # or vim .env

# Add production credentials
```

#### 3. Build and Start

```bash
# Build Docker images
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f
```

#### 4. Verify Deployment

```bash
# Check if service is running
curl http://localhost:8501

# View logs
docker-compose logs dashboard

# Check database
docker-compose exec dashboard python scripts/view_db.py
```

#### 5. Set Up Scheduler

```bash
# The scheduler runs inside the container
# Check it's running:
docker-compose logs scheduler
```

#### 6. Configure Reverse Proxy (Optional but Recommended)

Install nginx:
```bash
sudo apt-get update
sudo apt-get install nginx
```

Configure nginx:
```nginx
# /etc/nginx/sites-available/analytics
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/analytics /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 7. Set Up SSL (Recommended)

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is set up automatically
```

## Option 2: VPS/Cloud Server Deployment

### Prerequisites

- Ubuntu 20.04+ or similar Linux server
- Python 3.10+
- SSH access with sudo privileges

### Steps

#### 1. Connect to Server

```bash
ssh user@your-server-ip
```

#### 2. Install Dependencies

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Python 3.10
sudo apt-get install python3.10 python3.10-venv python3-pip -y

# Install system dependencies
sudo apt-get install build-essential libssl-dev -y
```

#### 3. Transfer Application

```bash
# Option A: Git clone
git clone [repository-url] analytics-pipeline
cd analytics-pipeline

# Option B: SCP from local machine
# (run from your local machine)
scp -r /path/to/project user@server:/home/user/analytics-pipeline
```

#### 4. Set Up Application

```bash
cd analytics-pipeline

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Add your credentials
```

#### 5. Test Manually

```bash
# Test extraction
python etl/extract_woocommerce.py

# Test dashboard (temporarily)
streamlit run dashboard/app_woo_v2.py --server.port 8501
```

#### 6. Set Up Systemd Services

Create dashboard service:
```bash
sudo nano /etc/systemd/system/analytics-dashboard.service
```

```ini
[Unit]
Description=Analytics Dashboard
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/home/your-username/analytics-pipeline
Environment="PATH=/home/your-username/analytics-pipeline/venv/bin"
ExecStart=/home/your-username/analytics-pipeline/venv/bin/streamlit run dashboard/app_woo_v2.py --server.port 8501
Restart=always

[Install]
WantedBy=multi-user.target
```

Create scheduler service:
```bash
sudo nano /etc/systemd/system/analytics-scheduler.service
```

```ini
[Unit]
Description=Analytics ETL Scheduler
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/home/your-username/analytics-pipeline
Environment="PATH=/home/your-username/analytics-pipeline/venv/bin"
ExecStart=/home/your-username/analytics-pipeline/venv/bin/python scheduler.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start services:
```bash
sudo systemctl daemon-reload
sudo systemctl enable analytics-dashboard
sudo systemctl enable analytics-scheduler
sudo systemctl start analytics-dashboard
sudo systemctl start analytics-scheduler

# Check status
sudo systemctl status analytics-dashboard
sudo systemctl status analytics-scheduler
```

## Option 3: Streamlit Cloud Deployment

### Prerequisites

- GitHub account
- Code pushed to GitHub repository
- Streamlit Cloud account (free tier available)

### Steps

#### 1. Prepare Repository

Ensure your repo has:
- `requirements.txt`
- `.streamlit/config.toml` (for theme)
- `dashboard/app_woo_v2.py`

Add `.streamlit/secrets.toml` to `.gitignore` (important!)

#### 2. Push to GitHub

```bash
git add .
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin main
```

#### 3. Deploy on Streamlit Cloud

1. Go to https://share.streamlit.io
2. Click "New app"
3. Select your repository
4. Set main file: `dashboard/app_woo_v2.py`
5. Click "Deploy"

#### 4. Configure Secrets

In Streamlit Cloud dashboard:
1. Go to "Advanced settings"
2. Add secrets (contents of your `.env`):

```toml
WC_URL = "https://your-store.com"
WC_CONSUMER_KEY = "ck_xxx"
WC_CONSUMER_SECRET = "cs_xxx"
GA4_KEY_FILE = "credentials.json"
GA4_PROPERTY_ID = "123456"
```

For GA4 JSON file, paste entire JSON:
```toml
[GA4_CREDENTIALS]
type = "service_account"
project_id = "your-project"
# ... rest of JSON
```

#### 5. Limitations

Note: Streamlit Cloud has limitations:
- No scheduler (ETL won't run automatically)
- Limited resources
- SQLite may not persist

**Workaround**: Run ETL locally, sync database to cloud storage

## Post-Deployment Tasks

### 1. Verify All Services Running

```bash
# Docker
docker-compose ps

# VPS
sudo systemctl status analytics-dashboard
sudo systemctl status analytics-scheduler

# Streamlit Cloud
# Check dashboard URL loads
```

### 2. Test Data Extraction

```bash
# Manually trigger extraction
docker-compose exec dashboard python etl/extract_woocommerce.py

# Or on VPS
source venv/bin/activate
python etl/extract_woocommerce.py
```

### 3. Set Up Monitoring

Configure alerts in `.env`:
```
EMAIL_ALERTS_ENABLED=true
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK
```

### 4. Create Backups

```bash
# Add to crontab
crontab -e

# Daily database backup at 1 AM
0 1 * * * cp /path/to/analytics-pipeline/data/*.db /path/to/backups/
```

### 5. Security Checklist

- [ ] Firewall configured (only ports 80, 443, 22 open)
- [ ] SSL certificate installed
- [ ] Strong passwords for all services
- [ ] `.env` file has restricted permissions (600)
- [ ] Regular security updates enabled

## Troubleshooting Deployment

### Issue: Cannot connect to dashboard

**Check**:
```bash
# Is service running?
sudo systemctl status analytics-dashboard

# Are ports open?
sudo netstat -tlnp | grep 8501

# Check logs
sudo journalctl -u analytics-dashboard -f
```

### Issue: Database not found

**Solution**:
```bash
# Check database directory exists
ls -la data/

# Create if missing
mkdir -p data

# Run initial extraction
python etl/extract_woocommerce.py
```

### Issue: Scheduler not running jobs

**Check**:
```bash
# View scheduler logs
sudo journalctl -u analytics-scheduler -f

# Manually test scheduler
python scheduler.py
```

## Rollback Procedure

If deployment fails:

```bash
# Docker
docker-compose down
docker-compose up -d --force-recreate

# VPS
sudo systemctl stop analytics-dashboard
sudo systemctl stop analytics-scheduler
# Fix issues, then restart
sudo systemctl start analytics-dashboard
sudo systemctl start analytics-scheduler
```

## Monitoring Production

### Check Logs

```bash
# Application logs
tail -f logs/etl.log

# System logs (VPS)
sudo journalctl -u analytics-dashboard -f
```

### Monitor Resources

```bash
# Docker stats
docker stats

# VPS resources
htop
df -h
```

## Updating Production

```bash
# Docker deployment
git pull
docker-compose down
docker-compose build
docker-compose up -d

# VPS deployment
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart analytics-dashboard
sudo systemctl restart analytics-scheduler
```

## Additional Resources

- [DEPLOYMENT.md](../../docs/DEPLOYMENT.md) - Detailed deployment guide
- [DOCKER_DEPLOYMENT.md](../../docs/DOCKER_DEPLOYMENT.md) - Docker-specific guide
- [SECURITY.md](../../docs/SECURITY.md) - Security best practices
- [TROUBLESHOOTING.md](../../docs/TROUBLESHOOTING.md) - Common issues

## Support

For deployment issues, contact: tomas.farias.e@ug.uchile.cl
