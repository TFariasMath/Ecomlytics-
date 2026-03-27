# Troubleshooting Guide - Analytics Pipeline

**Version**: 1.0 Generic Edition  
**Last Updated**: January 14, 2026  
**Support**: tomas.farias.e@ug.uchile.cl

---

## Quick Diagnostics

**Before diving into specific issues, run these quick checks:**

```bash
# 1. Check if databases exist
ls data/*.db

# 2. Check last 20 log lines
tail -n 20 logs/etl.log

# 3. Test database connectivity
python scripts/view_db.py

# 4. View ETL execution history
python utils/etl_monitor_cli.py
```

---

## Common Issues

### 1. Configuration Errors

#### ❌ Error: `Configuration not found`

**Symptoms**:
```
FileNotFoundError: .env file not found
```

**Cause**: Missing environment file

**Solution**:
```bash
# Copy example file
copy .env.example .env

# Edit with your credentials
notepad .env  # Windows
nano .env     # Linux/Mac
```

#### ❌ Error: `Invalid WooCommerce credentials`

**Symptoms**:
```
401 Unauthorized: Consumer key is invalid
```

**Cause**:  Invalid or expired API keys

**Solution**:
1. Log into WooCommerce Admin
2. Go to Settings → Advanced → REST API
3. Create new key with Read/Write permissions
4. Update `.env` with new credentials:
   ```
   WC_CONSUMER_KEY=ck_new_key_here
   WC_CONSUMER_SECRET=cs_new_secret_here
   ```

#### ❌ Error: `GA4_KEY_FILE not found`

**Symptoms**:
```
FileNotFoundError: credentials.json not found
```

**Cause**: Service account JSON file missing or wrong path

**Solution**:
```bash
# Check file exists
ls *.json

# Update .env with correct filename
GA4_KEY_FILE=your-service-account-file.json
```

---

### 2. API Connection Issues

#### ❌ Error: `WooCommerce API timeout`

**Symptoms**:
```
requests.exceptions.Timeout: Connection timeout after 30 seconds
```

**Possible causes**:
- Poor internet connection
- WooCommerce server slow/down
- Firewall blocking requests

**Solutions**:

**A. Check internet connection**:
```bash
ping google.com
curl https://your-store.com
```

**B. Increase timeout** in `etl/extract_woocommerce.py`:
```python
wcapi = API(
    url=config['url'],
    consumer_key=config['consumer_key'],
    consumer_secret=config['consumer_secret'],
    timeout=60  # Increase from 30 to 60 seconds
)
```

**C. Test direct API access**:
```bash
curl "https://your-store.com/wp-json/wc/v3/orders?per_page=1" \
  -u "ck_xxx:cs_xxx"
```

#### ❌ Error: `GA4 Permission denied`

**Symptoms**:
```
google.api_core.exceptions.PermissionDenied: 
User does not have sufficient permissions
```

**Cause**: Service account lacks access to GA4 property

**Solution**:
1. Open Google Analytics
2. Go to Admin → Property Access Management
3. Click "+" to add users
4. Add service account email (found in JSON file: `client_email`)
5. Assign **Viewer** role
6. Wait 5-10 minutes for propagation
7. Retry extraction

#### ❌ Error: `Facebook token expired`

**Symptoms**:
```
Error validating access token: Session has expired
```

**Cause**: Facebook access tokens expire (60 days for Page tokens)

**Solution**:
```bash
# Get new permanent token
python scripts/get_permanent_facebook_token.py

# Follow prompts to update .env
```

---

### 3. Database Issues

#### ❌ Error: `Database locked`

**Symptoms**:
```
sqlite3.OperationalError: database is locked
```

**Cause**: Another process accessing the database

**Solutions**:

**A. Close other programs**:
- Close Streamlit dashboard if running
- Check for other Python processes:
  ```bash
  ps aux | grep python  # Linux/Mac
  tasklist | findstr python  # Windows
  ```

**B. Wait and retry** (SQLite auto-releases after timeout)

**C. Enable WAL mode** (better concurrency):
```python
# Run once
python -c "
import sqlite3
conn = sqlite3.connect('data/woocommerce.db')
conn.execute('PRAGMA journal_mode=WAL')
conn.close()
"
```

**D. Migrate to PostgreSQL** for production (see [DEPLOYMENT.md](DEPLOYMENT.md))

#### ❌ Error: `Table not found`

**Symptoms**:
```
pandas.io.sql.DatabaseError: no such table: wc_orders
```

**Cause**: Database not initialized or corrupted

**Solution**:
```bash
# Run ETL to create tables
python etl/extract_woocommerce.py

# Or initialize manually
python -c "
from etl.extract_woocommerce import init_db_if_needed
init_db_if_needed()
"
```

#### ❌ Data looks wrong / Missing data

**Diagnostic steps**:

1. **Check extraction date**:
```python
from utils.database import get_last_extraction_date

last = get_last_extraction_date('wc_orders', 'date_only', 'data/woocommerce.db')
print(f"Last extraction: {last}")
```

2. **Check row counts**:
```bash
python scripts/view_db.py
# Shows row counts for all tables
```

3. **Verify data manually**:
```python
import pandas as pd
import sqlite3

conn = sqlite3.connect('data/woocommerce.db')
df = pd.read_sql("SELECT * FROM wc_orders ORDER BY date_created DESC LIMIT 10", conn)
print(df)
```

4. **Re-extract specific date range**:
```python
# In etl/extract_woocommerce.py, temporarily modify:
extract_orders(wcapi, start_date="2026-01-01")  # Force specific date
```

---

### 4. Dashboard Issues

#### ❌ Dashboard shows no data

**Symptoms**: All metrics show zero or "N/A"

**Diagnostic steps**:

1. **Check databases exist**:
```bash
ls -lh data/*.db
# Should show files with size > 0 bytes
```

2. **Check table contents**:
```bash
python scripts/view_db.py
```

3. **Check dashboard query** (look for errors in terminal):
```bash
streamlit run dashboard/app_woo_v2.py
# Watch terminal for error messages
```

**Common fixes**:
- Run ETL first: `python run_pipeline.py`
- Check date filters in dashboard sidebar
- Verify `date_created` column has valid dates

#### ❌ Dashboard loads slowly

**Causes**:
- Large dataset without indexes
- Multiple concurrent users
- Complex queries

**Solutions**:

**A. Create database indexes**:
```bash
python config/apply_indexes.py
```

**B. Enable caching** in `.env`:
```
CACHE_ENABLED=true
CACHE_TTL_HOURS=6
```

**C. Use date filters** to limit data range

**D. Optimize queries** - add indexes to frequently filtered columns

#### ❌ Dashboard crashes / Shows error

**Check Streamlit logs**:
```bash
# Logs appear in terminal where you ran streamlit
# Look for Python traceback

# Common errors:
# - KeyError: Missing column in DataFrame
# - TypeError: Invalid data type
# - MemoryError: Dataset too large
```

**Solutions**:
- Restart dashboard: `Ctrl+C` then rerun
- Clear cache: `Shift+C` in browser
- Check logs: `tail -f logs/etl.log`

---

### 5. Scheduler Issues

#### ❌ Scheduler not running

**Check if process running**:
```bash
ps aux | grep scheduler  # Linux/Mac
tasklist | findstr python  # Windows
```

**Start scheduler**:
```bash
python scheduler.py
# Should show: "Scheduler started, press Ctrl+C to exit"
```

**Run as background process**:
```bash
# Linux/Mac
nohup python scheduler.py > scheduler.log 2>&1 &

# Windows (use Task Scheduler or pythonw)
pythonw scheduler.py
```

#### ❌ Scheduled jobs not executing

**Check scheduler logs**:
```bash
tail -f logs/etl.log
# Wait for scheduled time to see execution
```

**Test manual execution**:
```bash
# Test individual extractors
python etl/extract_analytics.py
python etl/extract_woocommerce.py
```

**Verify schedule** in `scheduler.py`:
```python
# Default schedules:
# GA4: 2:00 AM
# WooCommerce: 3:00 AM
```

---

### 6. Data Quality Issues

#### ❌ Revenue numbers don't match WooCommerce

**Diagnostic**:

1. **Check order statuses**:
```python
import pandas as pd
import sqlite3

conn = sqlite3.connect('data/woocommerce.db')
df = pd.read_sql("""
    SELECT status, COUNT(*) as count, SUM(total) as revenue
    FROM wc_orders
    WHERE date_created >= '2026-01-01'
    GROUP BY status
""", conn)
print(df)
```

2. **Compare with WooCommerce**:
- Go to WooCommerce → Reports
- Select same date range
- Compare totals

**Common causes**:
- Different status filters (completed only vs all statuses)
- Date field differences (created vs paid)
- Refunds not accounted for
- Currency conversion issues

**Solutions**:
- Verify status filter in dashboard matches WooCommerce reports
- Use `date_paid` instead of `date_created` for revenue calculations
- Account for refunds separately

#### ❌ Missing orders

**Check extraction history**:
```bash
python utils/etl_monitor_cli.py
# Shows last executions and row counts
```

**Force full re-extraction**:
```python
# Backup current database
cp data/woocommerce.db backups/woocommerce_backup.db

# Delete and re-extract
rm data/woocommerce.db
python etl/extract_woocommerce.py
```

---

### 7. Performance Issues

#### ❌ ETL takes too long

**Profile execution**:
```bash
# Run with time tracking
time python etl/extract_woocommerce.py
```

**Common bottlenecks**:
- API rate limiting (add delays)
- Large date range (use incremental)
- No indexes (run `apply_indexes.py`)
- Network latency

**Optimizations**:

1. **Enable incremental loading** (should be default)
2. **Reduce batch size** if memory issues:
   ```python
   # In extract_woocommerce.py
   BATCH_SIZE = 250  # Reduce from 500
   ```
3. **Add indexes** to database
4. **Use caching** for dashboard queries

#### ❌ High memory usage

**Monitor memory**:
```bash
# During extraction
htop  # Linux
top   # Mac
Task Manager  # Windows
```

**Solutions**:
- Process data in smaller chunks
- Clear variables after use: `del df`
- Use generators instead of loading all data
- Increase system RAM or use swap

---

### 8. Installation Issues

#### ❌ `pip install` fails

**Check Python version**:
```bash
python --version
# Should be 3.10 or higher
```

**Common fixes**:

**A. Upgrade pip**:
```bash
python -m pip install --upgrade pip
```

**B. Install build tools**:
```bash
# Windows: Install Visual Studio Build Tools
# Linux: sudo apt-get install python3-dev build-essential
# Mac: xcode-select --install
```

**C. Use pre-built wheels**:
```bash
pip install --only-binary=:all: -r requirements.txt
```

#### ❌ Import errors

**Symptoms**:
```
ModuleNotFoundError: No module named 'streamlit'
```

**Cause**: Wrong Python environment

**Solution**:
```bash
# Activate virtual environment
.\\venv\\Scripts\\activate  # Windows
source venv/bin/activate   # Linux/Mac

# Verify environment
which python  # Should show venv path

# Reinstall if needed
pip install -r requirements.txt
```

---

## Log Interpretation

### Understanding Log Levels

```
INFO    - Normal operations, milestones
WARNING - Potential issues (retrying, degraded performance)
ERROR   - Errors requiring attention
CRITICAL - System failures
```

### Common Log Patterns

#### ✅ Successful extraction:
```
2026-01-14 02:00:00 - INFO - 🚀 Iniciando extracción de Google Analytics
2026-01-14 02:00:15 - INFO - ✅ Extracted 1250 rows for Channels
2026-01-14 02:00:20 - INFO - ✅ Extracción completada
```

#### ⚠️ Retry in progress:
```
2026-01-14 02:00:05 - WARNING - API request failed, retrying (attempt 1/3)
2026-01-14 02:00:07 - WARNING - API request failed, retrying (attempt 2/3)
2026-01-14 02:00:11 - INFO - API request succeeded on retry
```

#### ❌ Critical failure:
```
2026-01-14 02:00:05 - ERROR - Failed to connect to database
2026-01-14 02:00:05 - CRITICAL - ETL execution failed
```

---

## Getting Help

### Before Contacting Support

Collect this information:

1. **Error message** (full traceback)
2. **Log excerpt** (`tail -n 100 logs/etl.log`)
3. **Configuration** (`.env` without sensitive values)
4. **System info**:
   ```bash
   python --version
   pip list
   ```
5. **Steps to reproduce**

### Contact

**Email**: tomas.farias.e@ug.uchile.cl

**Include**:
- Clear description of the issue
- What you've tried
- Logs and error messages
- Expected vs actual behavior

---

## Advanced Troubleshooting

### Enable Debug Logging

Edit `config/logging_config.py`:
```python
# Change
logger.setLevel(logging.INFO)

# To
logger.setLevel(logging.DEBUG)
```

### Database Forensics

```bash
# Check database integrity
sqlite3 data/woocommerce.db "PRAGMA integrity_check;"

# Analyze table sizes
sqlite3 data/woocommerce.db "
SELECT name, 
       (SELECT COUNT(*) FROM sqlite_master sm WHERE sm.name=m.name) as rows
FROM sqlite_master m 
WHERE type='table';
"
```

### Network Debugging

```bash
# Test API connectivity
curl -v "https://your-store.com/wp-json/wc/v3/orders?per_page=1" \
  -u "consumer_key:consumer_secret"

# Check SSL certificates
openssl s_client -connect your-store.com:443
```

---

**See also**:
- [API_REFERENCE.md](API_REFERENCE.md) - Function documentation
- [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) - Development workflows
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
