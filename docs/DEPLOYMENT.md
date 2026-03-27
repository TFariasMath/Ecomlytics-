# 🚀 Deployment Guide - Analytics Pipeline

Complete guide for deploying the Analytics & E-commerce Data Pipeline in different environments.

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Local Development](#local-development)
3. [Production Deployment](#production-deployment)
4. [Server Deployment (Linux)](#server-deployment-linux)
5. [Cloud Deployment](#cloud-deployment)
6. [Environment Configuration](#environment-configuration)
7. [Security Best Practices](#security-best-practices)
8. [Monitoring & Maintenance](#monitoring--maintenance)

---

## System Requirements

### Minimum Requirements

- **OS**: Windows 10+, Linux (Ubuntu 20.04+), macOS 11+
- **Python**: 3.10 or higher
- **RAM**: 4 GB minimum (8 GB recommended)
- **Storage**: 10 GB available space
- **Network**: Stable internet connection for API calls

### Dependencies

All dependencies are managed via `requirements.txt`:
```bash
pip install -r requirements.txt
```

---

## Local Development

### Quick Start

1. **Clone repository:**
   ```bash
   git clone <repository-url>
   cd ExtraerDatosGoogleAnalitics_Generic
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   
   # Windows
   .\venv\Scripts\activate
   
   # Linux/macOS
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configure credentials:**
   ```bash
   streamlit run dashboard/app_woo_v2.py
   ```
   Navigate to setup page and configure your API credentials.

5. **Test ETL extractors:**
   ```bash
   python etl/extract_woocommerce.py
   python etl/extract_analytics.py
   python etl/extract_facebook.py
   ```

6. **Launch dashboard:**
   ```bash
   streamlit run dashboard/app_woo_v2.py
   ```

---

## Production Deployment

### Option 1: Windows Server

#### Install Python
```powershell
# Download Python 3.10+ from python.org
# Ensure "Add to PATH" is checked during installation

python --version
```

#### Setup Application
```powershell
# Clone project
git clone <repository-url>
cd ExtraerDatosGoogleAnalitics_Generic

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure .env file
copy .env.example .env
# Edit .env with production credentials
```

#### Create Windows Service (Optional)

Create `start_dashboard.bat`:
```batch
@echo off
cd C:\path\to\ExtraerDatosGoogleAnalitics_Generic
call venv\Scripts\activate
streamlit run dashboard/app_woo_v2.py --server.port 8501 --server.address 0.0.0.0
```

Use Task Scheduler to run at startup.

#### Schedule ETL Jobs

Create `run_etl.bat`:
```batch
@echo off
cd C:\path\to\ExtraerDatosGoogleAnalitics_Generic
call venv\Scripts\activate
python etl/extract_woocommerce.py
python etl/extract_analytics.py
python etl/extract_facebook.py
```

Schedule via Windows Task Scheduler:
- **Trigger**: Daily at 2:00 AM
- **Action**: Run `run_etl.bat`

---

## Server Deployment (Linux)

### Ubuntu 20.04+ Setup

#### 1. Install System Dependencies
```bash
sudo apt update
sudo apt install -y python3.10 python3.10-venv python3-pip git
```

#### 2. Clone and Setup Project
```bash
cd /opt
sudo git clone <repository-url> analytics-pipeline
cd analytics-pipeline
sudo chown -R $USER:$USER /opt/analytics-pipeline

python3.10 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### 3. Configure Environment
```bash
cp .env.example .env
nano .env  # Edit with production credentials
```

#### 4. Create Systemd Service for Dashboard

Create `/etc/systemd/system/analytics-dashboard.service`:
```ini
[Unit]
Description=Analytics Dashboard
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/opt/analytics-pipeline
Environment="PATH=/opt/analytics-pipeline/venv/bin"
ExecStart=/opt/analytics-pipeline/venv/bin/streamlit run dashboard/app_woo_v2.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable analytics-dashboard
sudo systemctl start analytics-dashboard
sudo systemctl status analytics-dashboard
```

#### 5. Schedule ETL with Cron

Edit crontab:
```bash
crontab -e
```

Add:
```cron
# Run ETL daily at 2:00 AM
0 2 * * * cd /opt/analytics-pipeline && /opt/analytics-pipeline/venv/bin/python etl/extract_woocommerce.py >> /var/log/analytics-etl.log 2>&1
0 2 * * * cd /opt/analytics-pipeline && /opt/analytics-pipeline/venv/bin/python etl/extract_analytics.py >> /var/log/analytics-etl.log 2>&1
0 2 * * * cd /opt/analytics-pipeline && /opt/analytics-pipeline/venv/bin/python etl/extract_facebook.py >> /var/log/analytics-etl.log 2>&1
```

#### 6. Setup Nginx Reverse Proxy (Optional)

Install Nginx:
```bash
sudo apt install nginx
```

Create `/etc/nginx/sites-available/analytics`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/analytics /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Cloud Deployment

### AWS Deployment

#### Using EC2

1. **Launch EC2 Instance:**
   - AMI: Ubuntu 20.04 LTS
   - Instance Type: t3.medium (recommended)
   - Storage: 20 GB gp3
   - Security Group: Allow ports 22 (SSH), 80 (HTTP), 8501 (Streamlit)

2. **Connect and Setup:**
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   ```
   Follow [Server Deployment (Linux)](#server-deployment-linux) steps

3. **Configure Security:**
   - Use IAM roles instead of hardcoded credentials when possible
   - Store `.env` in AWS Secrets Manager
   - Enable CloudWatch for logging

#### Using ECS (Containerized)

Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8501

# Run dashboard
CMD ["streamlit", "run", "dashboard/app_woo_v2.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and push to ECR, then deploy via ECS.

### Google Cloud Platform (GCP)

#### Using Compute Engine

Similar to AWS EC2 - follow Linux deployment steps on a GCE instance.

#### Using Cloud Run (Serverless)

1. Build container with Dockerfile above
2. Push to Google Container Registry
3. Deploy to Cloud Run
4. Configure environment variables via Cloud Run console

### Azure

#### Using Azure VM

Follow Linux deployment steps on an Ubuntu Azure VM.

#### Using Azure Container Instances

Deploy using the same Dockerfile approach as AWS ECS.

---

## Environment Configuration

### Production .env Template

Create a production-specific `.env`:

```bash
# ========================================
# PRODUCTION ENVIRONMENT
# ========================================

# WooCommerce
WC_URL=https://production-store.com
WC_CONSUMER_KEY=ck_prod_xxxxxx
WC_CONSUMER_SECRET=cs_prod_xxxxxx

# Google Analytics
GA4_KEY_FILE=/path/to/production-service-account.json
GA4_PROPERTY_ID=987654321

# Facebook
FB_ACCESS_TOKEN=EAAprod_xxxxx
FB_PAGE_ID=prod_page_id
FB_API_VERSION=v19.0

# ========================================
# OPTIONAL: ADVANCED SETTINGS
# ========================================

# Logging level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# ETL schedule (if using scheduler.py)
ETL_SCHEDULE_ENABLED=true
ETL_SCHEDULE_TIME=02:00
```

### Environment-Specific Settings

Consider using different `.env` files:
- `.env.development`
- `.env.staging`
- `.env.production`

Load dynamically based on environment variable:
```python
import os
from dotenv import load_dotenv

env = os.getenv('APP_ENV', 'development')
load_dotenv(f'.env.{env}')
```

---

## Security Best Practices

### Credential Management

✅ **DO:**
- Use environment variables (`.env` files) for credentials
- Store production `.env` in secure vault (AWS Secrets Manager, Azure Key Vault)
- Use read-only API permissions when possible
- Rotate credentials regularly (every 90 days)
- Use different credentials for dev/staging/production

❌ **DON'T:**
- Commit `.env` to version control
- Share credentials via email/chat
- Use production keys in development
- Hardcode credentials in source code

### Network Security

- **Firewall**: Only expose necessary ports (80, 443, 8501)
- **SSH**: Disable password auth, use key-based only
- **HTTPS**: Use SSL/TLS certificates (Let's Encrypt)
- **VPN**: Restrict admin access to VPN only

### Application Security

- Keep dependencies updated: `pip list --outdated`
- Regular security audits: `pip-audit`
- Monitor logs for suspicious activity
- Implement rate limiting for API calls

---

## Monitoring & Maintenance

### Logging

Logs are stored in `logs/etl.log`:
- **Rotation**: Automatic rotation at 10 MB
- **Retention**: 5 backup files
- **Location**: `logs/` directory

Monitor logs:
```bash
# Tail live logs
tail -f logs/etl.log

# Search for errors
grep ERROR logs/etl.log

# Count warnings
grep -c WARNING logs/etl.log
```

### Database Maintenance

#### Backup Databases
```bash
# Create backups
cp data/woocommerce.db backups/woocommerce_$(date +%Y%m%d).db
cp data/analytics.db backups/analytics_$(date +%Y%m%d).db
cp data/facebook.db backups/facebook_$(date +%Y%m%d).db
```

#### Vacuum SQLite (Optimize)
```bash
sqlite3 data/woocommerce.db "VACUUM;"
sqlite3 data/analytics.db "VACUUM;"
sqlite3 data/facebook.db "VACUUM;"
```

### Health Checks

Create `health_check.py`:
```python
import os
from config.settings import check_configuration_status

def health_check():
    status = check_configuration_status()
    if all(status.values()):
        print("✅ All services configured")
        return 0
    else:
        print("❌ Configuration incomplete")
        return 1

if __name__ == "__main__":
    exit(health_check())
```

Run periodically to ensure system health.

### Performance Monitoring

- **CPU/RAM**: Monitor system resources
- **Disk Space**: Ensure adequate storage
- **API Limits**: Track API usage to avoid rate limits
- **Database Size**: Monitor SQLite file sizes

---

## Troubleshooting Production Issues

### Dashboard Not Accessible

1. Check service status:
   ```bash
   sudo systemctl status analytics-dashboard
   ```

2. Check firewall:
   ```bash
   sudo ufw status
   sudo ufw allow 8501
   ```

3. Check logs:
   ```bash
   sudo journalctl -u analytics-dashboard -f
   ```

### ETL Jobs Failing

1. Check cron logs:
   ```bash
   grep CRON /var/log/syslog
   ```

2. Run manually to see errors:
   ```bash
   cd /opt/analytics-pipeline
   source venv/bin/activate
   python etl/extract_woocommerce.py
   ```

3. Verify credentials:
   ```bash
   python -c "from config.settings import check_configuration_status; print(check_configuration_status())"
   ```

### High Memory Usage

- Reduce batch size in ETL scripts
- Schedule ETL during off-peak hours
- Consider upgrading server resources

---

## Support and Updates

### Updating the Application

```bash
cd /opt/analytics-pipeline
git pull origin main
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart analytics-dashboard
```

### Rollback

```bash
git log  # Find previous commit
git checkout <commit-hash>
pip install -r requirements.txt
sudo systemctl restart analytics-dashboard
```

---

**Last Updated**: December 21, 2025  
**Version**: 1.0 - Generic Edition
