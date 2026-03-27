# 🛠️ Troubleshooting Guide

If you encounter issues while running the Analytics Pipeline, consult this guide for common solutions.

## Common Errors & Solutions

### 1. Dashboard Shows "Configuration Not Found"

**Symptom**: The dashboard loads but prominently displays warnings that services are not configured.

**Causes & Solutions**:
- **Missing `.env` file**: The system expects a `.env` file in the root directory. If you haven't created one, use the Web Interface (click "⚙️ Configure Credentials" in the sidebar) to generate it automatically, or copy `.env.example` to `.env`.
- **Invalid Paths**: If you configured Google Analytics manually, ensure the `GA4_KEY_FILE` path is correct and the JSON file actually exists in that location.

---

### 2. WooCommerce Extraction Fails (Timeout)

**Symptom**: Running `python etl/extract_woocommerce.py` hangs or fails with a connection error.

**Causes & Solutions**:
- **Firewall blocking API calls**: Ensure your WordPress server doesn't have an aggressive firewall blocking requests from your script's IP address.
- **Incorrect URL Format**: Ensure your `WC_URL` begins with `https://` and does not end with a trailing slash (e.g., use `https://mystore.com`, not `mystore.com/`).
- **Heavy Load**: Try running the extraction during off-peak hours or adjust the `BATCH_SIZE` in `etl/extract_woocommerce.py`.

---

### 3. Google Analytics "Permission Denied"

**Symptom**: The ETL script returns a 403 Forbidden error stating the caller does not have permission.

**Causes & Solutions**:
- **Service Account not added to GA4**: You *must* add the service account email (found inside the JSON key file) as a 'Viewer' in the GA4 Property Access Management settings.
- **Wrong Property ID**: Double-check that you are using the correct 9-digit GA4 Property ID, not a Universal Analytics (UA-) tracking ID.

---

### 4. Data Is Missing from the Dashboard

**Symptom**: The dashboard works, but it says "No data available for this period."

**Causes & Solutions**:
- **ETL hasn't run**: The dashboard only reads from the local SQLite databases. You must run the extraction scripts first. Run `python run_pipeline.py`.
- **Date Filters**: Ensure the date range selected at the top of the dashboard actually contains sales or traffic data.

---

### 5. Web Configuration Errors Out Saving

**Symptom**: When trying to save credentials via the Streamlit web interface, it fails.

**Causes & Solutions**:
- **File Permissions**: The Python process running Streamlit needs write permissions to the project directory to create/modify the `.env` file and save uploaded JSON keys. Run the terminal as Administrator or check folder permissions.

---

## 🔍 Checking Logs
If the solutions above don't work, always check the application logs for detailed error tracebacks.

Logs are located in the `logs/` directory:
- `logs/etl.log`: Contains detailed output from all extraction attempts.

**How to read the log**:
```
[TIMESTAMP] - [MODULE] - [LEVEL] - [MESSAGE]
2026-03-27 15:00:00 - etl.extract_woocommerce - ERROR - Failed to connect to API: ...
```
Look for lines marked `ERROR` or `CRITICAL`.
