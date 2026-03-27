# ⚙️ Setup and Configuration Guide

This guide details how to configure the API credentials required to run the Analytics Pipeline.

> **Tip**: The easiest way to configure the system is using the Web Interface. Start the app (`LAUNCH.bat`) and click **"⚙️ Configure Credentials"** in the sidebar.

If you prefer manual configuration, you must edit the `.env` file in the root directory.

---

## 🛒 WooCommerce Setup

You need to create read-only API keys in your WooCommerce store.

1. Log into your WordPress admin dashboard.
2. Go to **WooCommerce** > **Settings**.
3. Click on the **Advanced** tab, then click the **REST API** link.
4. Click **Add key**.
5. Fill out the details:
   - **Description**: Add a friendly name (e.g., "Analytics Pipeline").
   - **User**: Select your admin user.
   - **Permissions**: **Read** is usually sufficient, but **Read/Write** is required if you plan to update order statuses from the dashboard later.
6. Click **Generate API key**.
7. Copy the **Consumer Key** and **Consumer Secret**.
8. In the `.env` file, set:
   ```env
   WC_URL=https://your-store.com
   WC_CONSUMER_KEY=ck_your_key_here
   WC_CONSUMER_SECRET=cs_your_secret_here
   ```

---

## 📈 Google Analytics 4 Setup

Connecting to GA4 requires creating a Google Cloud Service Account.

### Step 1: Create a Service Account
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing one.
3. Search for "Google Analytics Data API" and **Enable** it.
4. Go to **IAM & Admin** > **Service Accounts**.
5. Click **Create Service Account**, name it, and click Done.
6. Click on the new service account email, go to the **Keys** tab, click **Add Key** > **Create new key** > **JSON**.
7. Download the JSON file to your computer.

### Step 2: Grant Access to GA4
1. Open the downloaded JSON file and copy the `client_email` address.
2. Go to your [Google Analytics Admin panel](https://analytics.google.com/).
3. Select your GA4 Property and click **Property Access Management**.
4. Click the **+** button > **Add users**.
5. Paste the `client_email` address and give it **Viewer** permission.

### Step 3: Configure the Pipeline
1. Find your **Property ID** in GA4 (Admin > Property Settings).
2. Through the Web Interface: Upload the JSON file and enter the Property ID.
3. Or manually in the `.env` file:
   ```env
   GA4_KEY_FILE=your-credentials-file.json
   GA4_PROPERTY_ID=123456789
   ```
   *(Ensure the JSON file is placed in the project root if configuring manually)*.

---

## 📘 Facebook Insights Setup (Optional)

1. Go to [Facebook Developers](https://developers.facebook.com/).
2. Create an App (Type: Business).
3. Generate a long-lived **Page Access Token** with `read_insights` permissions.
4. Find your **Page ID**.
5. In the `.env` file:
   ```env
   FB_ACCESS_TOKEN=EAA...
   FB_PAGE_ID=your_page_id
   ```
