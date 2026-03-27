# 🔒 Security Remediation Checklist

This checklist guides you through securing the Analytics Pipeline project after the security audit.

---

## ⚠️ CRITICAL - Do These IMMEDIATELY

### 1. Revoke Exposed Facebook Token ⏰ URGENT

**Location**: `test_fb_token.py` (now protected by .gitignore)

**Token**: `EAAhS7TP1JYkBQHh7MUIK0ha1bZAeEZB9AQE...`

**Steps to Revoke:**

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Select your App
3. Go to **Settings > Basic**
4. Scroll to **App Secret** section
5. Click "Reset App Secret" (this invalidates all tokens)

**OR** use Graph API:

```bash
curl -X DELETE "https://graph.facebook.com/v19.0/me/permissions?access_token=YOUR_TOKEN"
```

**Verify Revocation:**
```bash
curl "https://graph.facebook.com/v19.0/debug_token?input_token=OLD_TOKEN&access_token=OLD_TOKEN"
```
Should return `"is_valid": false`

- [ ] Token revoked in Facebook
- [ ] Verified token is invalid
- [ ] Generated new token (store in .env)

---

### 2. Secure Google Cloud Credentials

**Location**: `config/credentials/`
- `frutostayen-aa2351af50e6 (1).json`
- `stately-math-481515-s3-8d7500e96ca0.json`

**Risk Assessment:**
- [ ] Was this repository EVER public on GitHub/GitLab?
- [ ] Was it shared with external parties?
- [ ] Were these keys used in production?

**If YES to any above - ROTATE IMMEDIATELY:**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **IAM & Admin > Service Accounts**
3. Find the service account
4. Click **Keys** tab
5. Click **Add Key > Create new key > JSON**
6. Download new key
7. **Delete old key** from Google Cloud
8. Update `.env` file with new key path
9. Test connection via setup page

**If NO - Still Recommended:**
- [ ] Move JSON files outside repository (e.g., `~/.gcloud/`)
- [ ] Update `GA4_KEY_FILE` in `.env` to new path
- [ ] Delete files from `config/credentials/`

---

## 🗄️ Clean Sensitive Data from Databases

### Current Database Status

**woocommerce.db**: 14,139 orders, 3,038 customers
- Contains: Names, emails, phones, addresses

**analytics.db**: Google Analytics data
**facebook.db**: Facebook Page Insights

### Option A: Complete Cleanup (Recommended)

Run the automated cleanup script:

```bash
python scripts/clean_databases.py
```

This will:
- ✅ Create timestamped backups
- ✅ Delete all data from tables
- ✅ Vacuum databases to reclaim space
- ✅ Preserve database structure

**After cleanup:**
- [ ] Databases cleaned
- [ ] Backups created in `backups/`
- [ ] Ready for fresh data extraction

### Option B: Manual Cleanup (Advanced)

If you want to keep some data:

```bash
# Delete specific date ranges or customers
python
>>> import sqlite3
>>> conn = sqlite3.connect('data/woocommerce.db')
>>> # Delete orders before a date
>>> conn.execute("DELETE FROM wc_orders WHERE date_created < '2024-01-01'")
>>> conn.commit()
```

---

## 🧹 Remove Sensitive Files

### Option A: Automated (Recommended)

```bash
python scripts/clean_sensitive_files.py
```

This will:
- Find sensitive files automatically
- Create backups in `security_backups/`
- Remove original files
- Generate security report

### Option B: Manual

**Files to remove/secure:**

1. **test_fb_token.py** (blocked by gitignore now)
   ```bash
   # If you want to keep for testing:
   git rm test_fb_token.py  # Remove from git
   # Update to use environment variable (already done)
   ```

2. **Google Cloud Credentials**
   ```bash
   mkdir -p ~/analytics_credentials
   mv config/credentials/*.json ~/analytics_credentials/
   # Update .env
   echo "GA4_KEY_FILE=~/analytics_credentials/your-key.json" >> .env
   ```

3. **Database Files** (already in .gitignore)
   - No action needed if not committed

   **Verify:**
   ```bash
   git status --ignored
   ```
   Should show `data/` as ignored

---

## ✅ Verify .gitignore Configuration

The `.gitignore` has been created with proper protections.

**Verify it's working:**

```bash
# Check git sees .gitignore
git add .gitignore
git commit -m "Add comprehensive gitignore for security"

# Verify sensitive files are ignored
git status --ignored

# Should see (among others):
#   data/
#   .env
#   config/credentials/
#   *.db
```

**Test protection:**
```bash
# Try to add a .env file (should fail or be ignored)
touch .env
git add .env
# Should see: "The following paths are ignored by one of your .gitignore files"
```

- [ ] .gitignore committed
- [ ] Sensitive files are ignored
- [ ] Verified with `git status --ignored`

---

## 🔄 Generate New Credentials

After revoking old credentials, generate fresh ones:

### Facebook

1. [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app and permissions
3. Generate **Page Access Token** (doesn't expire)
4. Add to `.env`:
   ```bash
   FB_ACCESS_TOKEN=EAA_new_token_here
   ```

### Google Analytics (if rotated)

1. Created new service account key (see step 2 above)
2. Update `.env`:
   ```bash
   GA4_KEY_FILE=path/to/new-key.json
   ```

### WooCommerce (optional rotation)

1. WooCommerce > Settings > Advanced > REST API
2. Create new key
3. Update `.env`:
   ```bash
   WC_CONSUMER_KEY=ck_new_key
   WC_CONSUMER_SECRET=cs_new_secret
   ```

- [ ] New Facebook token generated
- [ ] New Google key (if needed)
- [ ] New WooCommerce keys (if needed)
- [ ] All stored in `.env`
- [ ] Tested via setup page

---

## 🧪 Test New Configuration

After completing all steps above:

1. **Test Configuration Interface:**
   ```bash
   streamlit run dashboard/app_woo_v2.py
   ```
   - Navigate to Setup page
   - Verify all services show ✅ configured
   - Test connections for each service

2. **Run ETL Extractors:**
   ```bash
   python etl/extract_woocommerce.py
   python etl/extract_analytics.py
   python etl/extract_facebook.py
   ```
   - Should complete without credential errors
   - Check logs for any issues

3. **Verify Dashboard:**
   - Refresh dashboard
   - Should show new data
   - No configuration warnings

- [ ] Setup page shows all green
- [ ] ETL extractors run successfully
- [ ] Dashboard displays data
- [ ] No security warnings

---

## 📊 Final Security Checks

### Documentation Review
- [ ] Read `docs/SECURITY.md`
- [ ] Review `docs/SECURITY_AUDIT_REPORT.md`
- [ ] Team trained on security practices

### Repository Check (if using Git)
- [ ] No sensitive files in git history
- [ ] `.gitignore` in place and working
- [ ] All team members aware of .env usage

### Monitoring
- [ ] Set calendar reminder to rotate credentials (90 days)
- [ ] Monitor API usage for anomalies
- [ ] Keep logs for security review

---

## 🎯 Completion Checklist

**Critical Actions:**
- [ ] Facebook token revoked and replaced
- [ ] Google credentials secured/rotated
- [ ] Databases cleaned or backed up
- [ ] Sensitive files removed/backed up
- [ ] .gitignore created and tested

**Verification:**
- [ ] New credentials working
- [ ] ETL pipeline functional
- [ ] Dashboard operational
- [ ] No sensitive data in repository

**Documentation:**
- [ ] Team notified of changes
- [ ] Security procedures documented
- [ ] Next audit scheduled

---

## 📞 Need Help?

**If you get stuck:**
1. Review `docs/SECURITY_AUDIT_REPORT.md` for details
2. Check `docs/SECURITY.md` for best practices
3. See `docs/SETUP_GUIDE.md` for credential setup

**If credentials were leaked:**
1. Revoke immediately (don't wait)
2. Check access logs for unauthorized usage
3. Rotate ALL credentials as precaution
4. Document incident

---

**Last Updated**: December 21, 2025  
**Estimated Time**: 30-45 minutes  
**Difficulty**: Medium
