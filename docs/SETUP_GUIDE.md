# 📖 Setup Guide - Analytics Pipeline Configuration

Complete guide to configure your API credentials for WooCommerce, Google Analytics 4, and Facebook.

## Table of Contents

1. [First-Time Setup](#first-time-setup)
2. [WooCommerce Configuration](#woocommerce-configuration)
3. [Google Analytics 4 Configuration](#google-analytics-4-configuration)
4. [Facebook Configuration](#facebook-configuration)
5. [Troubleshooting](#troubleshooting)

---

## First-Time Setup

### Option 1: Using the Web Interface (Recommended)

1. Start the application:
   ```bash
   streamlit run dashboard/app_woo_v2.py
   ```

2. In the sidebar, click on "⚙️ Configurar Credenciales" (if any service is not configured)

3. Navigate to the service tabs (WooCommerce, Google Analytics, Facebook)

4. Fill in the credentials for each service

5. Click "🔍 Test Connection" to validate

6. Click "💾 Save Configuration" to persist your settings

7. Restart the application

### Option 2: Manual .env File

1. Copy the `.env.example` file:
   ```bash
   copy .env.example .env
   ```

2. Edit `.env` with your credenciales (see specific sections below)

3. Save the file

4. Start the application

---

## WooCommerce Configuration

### Where to Find Your Credentials

1. Log in to your WordPress admin panel
2. Navigate to: **WooCommerce > Settings > Advanced > REST API**
3. Click "Add key"
4. Configure the key:
   - **Description**: "Analytics Pipeline" (or your preferred name)
   - **User**: Select an administrator user
   - **Permissions**: Select "Read"
5. Click "Generate API Key"
6. **Copy immediately!** Consumer Key and Consumer Secret (they won't be shown again)

### Configuring in .env

```bash
WC_URL=https://your-store.com
WC_CONSUMER_KEY=ck_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
WC_CONSUMER_SECRET=cs_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Common Issues

**Error: "Invalid signature"**
- Verify that the URL is correct and includes `https://`
- Ensure Consumer Key and Secret are complete
- Check that the user has administrator permissions

**Error: "Connection timeout"**
- Verify your internet connection
- Check if your WooCommerce site is accessible
- Try increasing the timeout in `etl/extract_woocommerce.py`

---

## Google Analytics 4 Configuration

### Step 1: Create Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select or create a project
3. Navigate to: **IAM & Admin > Service Accounts**
4. Click "Create Service Account"
5. Fill in:
   - **Name**: "Analytics Pipeline"
   - **Description**: "Service account for data extraction"
6. Click "Create and Continue"
7. Skip roles for now (click "Continue")
8. Click "Done"

### Step 2: Generate JSON Key

1. Click on the created service account
2. Go to "Keys" tab
3. Click "Add Key" > "Create new key"
4. Select "JSON" format
5.  Click "Create"
6. **Save the downloaded JSON file** to your project root directory

### Step 3: Grant Access to GA4

1. Go to [Google Analytics](https://analytics.google.com/)
2. Select your property
3. Go to: **Admin > Property Access Management**
4. Click "+" in the top right
5. Add the service account email (found in the JSON file, looks like `xxx@xxx.iam.gserviceaccount.com`)
6. Assign "Viewer" role
7. Click "Add"

### Step 4: Get Property ID

1. In Google Analytics, go to **Admin > Property Settings**
2. Copy the "Property ID" (numeric value, e.g., `123456789`)

### Configuring in .env

```bash
GA4_KEY_FILE=your-service-account-file.json
GA4_PROPERTY_ID=123456789
```

### Common Issues

**Error: "Key file not found"**
- Verify the JSON file is in the project root
- Check the filename in `.env` matches the actual file

**Error: "Permission denied"**
- Ensure the service account has been added to the GA4 property
- Verify it has "Viewer" role
- Wait up to 24 hours for permissions to propagate

**Error: "Property not found"**
- Double-check the Property ID
- Ensure you're using the GA4 property ID, not Universal Analytics

---

## Facebook Configuration

### Step 1: Get Access Token

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create app or select an existing one
3. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
4. Select your app
5. Click "Generate Access Token"
6. Grant the following permissions:
   - `pages_show_list`
   - `pages_read_engagement`
   - `read_insights`
7. Click "Generate Token"
8. **Copy the token immediately**

### Step 2: Get Page ID

#### Method 1: Via Facebook Page
1. Go to your Facebook Page
2. Click "About"
3. Scroll down to find "Page ID"

#### Method 2: Via Graph API Explorer
1. In Graph API Explorer (from step 1)
2. Use endpoint: `/me/accounts`
3. Click "Submit"
4. Find your page in the response and copy the `id` field

### Configuring in .env

```bash
FB_ACCESS_TOKEN=EAAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
FB_PAGE_ID=1234567890123456
FB_API_VERSION=v19.0
```

### Common Issues

**Error: "Invalid access token"**
- Token may have expired (User Access Tokens expire in 1-2 hours)
- Request a Page Access Token instead (doesn't expire)
- Use the Graph API Explorer to debug token

**Error: "Permissions error"**
- Ensure you granted all required permissions
- Regenerate the token with correct permissions

**Error: "Page not found"**
- Verify the Page ID is correct
- Ensure the token has access to that page

---

## Troubleshooting

### General Issues

**Dashboard shows "Configuration incomplete"**
- Check which service is missing in the sidebar warning
- Navigate to Setup page and configure the missing service
- Verify `.env` file exists and has correct values

**Changes not taking effect**
- Restart the Streamlit application
- Clear browser cache
- Check console logs for errors

**Data not loading**
- Verify ETL extractors have run successfully
- Check database files exist in `data/` directory
- Run extractors manually: `python etl/extract_woocommerce.py`

### Security Best Practices

✅ **DO:**
- Store credentials in `.env` file only
- Add `.env` to `.gitignore`
- Use read-only API permissions when possible
- Rotate tokens regularly
- Use Page Access Tokens for Facebook (longer validity)

❌ **DON'T:**
- Commit `.env` to version control
- Share tokens publicly
- Use production keys for testing
- Hardcode credentials in source code

### Getting Help

If you encounter issues:

1. Check the logs in `logs/etl.log`
2. Review error messages in the console
3. Verify all credentials are correct and up-to-date
4. Try testing connections via the Setup page
5. Ensure all services are accessible from your network

---

## Next Steps

After successful configuration:

1. Run the ETL extractors:
   ```bash
   python etl/extract_woocommerce.py
   python etl/extract_analytics.py
   python etl/extract_facebook.py
   ```

2. Verify data in the dashboard:
   ```bash
   streamlit run dashboard/app_woo_v2.py
   ```

3. Set up automated extraction (optional):
   ```bash
   python scheduler.py
   ```

---

**Last Updated**: December 21, 2025
