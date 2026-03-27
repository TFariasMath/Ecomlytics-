# ⚡ English Quick Start Guide

This guide will help you get the **Analytics & E-commerce Data Pipeline** up and running in minutes.

---

## 🚀 One-Click Installation (Windows)

1.  **Clone/Download** this repository to your computer.
2.  **Open the folder** and locate the file named `SETUP.bat`.
3.  **Double-click `SETUP.bat`**. This script will:
    - Check if Python 3.10+ is installed.
    - Create a local virtual environment (`venv`).
    - Upgrade `pip` and install all required libraries.
4.  **Double-click `LAUNCH.bat`**. This will:
    - Activate the virtual environment.
    - Start the Streamlit Dashboard.
5.  **Configure Credentials**:
    - Once the dashboard opens in your browser, look for **"⚙️ Configure Credentials"** in the sidebar.
    - Enter your WooCommerce, Google Analytics, and Facebook details.
    - Click **"Test Connection"** to ensure everything is working.
    - Click **"Save Configuration"**.

---

## 🔧 Component Overview

### 1. Data Extractors (ETL)
The pipeline includes scripts to pull data from your connected services:
- **WooCommerce**: Downloads orders, items, products, and customer data.
- **Google Analytics 4**: Fetches traffic, audience, and e-commerce event data.
- **Facebook**: Retrieves Page Insights and basic engagement metrics.

### 2. The Dashboard
A premium Streamlit interface for visualization:
- **Executive Summary**: Real-time sales and revenue KPIs.
- **Sales Analysis**: Historical trends with seasonal annotations.
- **Order History**: Searchable list of all store transactions.
- **Configuration Hub**: A dedicated page to manage API keys and settings.

### 3. Automation
The project uses `scheduler.py` to keep your data fresh. By default, it runs:
- **GA4 Extraction**: Every night at 2:00 AM.
- **WooCommerce Extraction**: Every night at 3:00 AM.

---

## 📁 Where is my data?

All extracted data is stored locally in SQLite databases within the `/data` folder:
- `data/woocommerce.db`: Store and order data.
- `data/analytics.db`: Traffic and conversion metrics.
- `data/monitoring.db`: Tracking of ETL execution and errors.
