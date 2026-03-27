# Developer Guide - Analytics Pipeline

**Version**: 1.0 Generic Edition  
**Last Updated**: January 14, 2026  
**For**: Developers using Antigravity/Claude Code  
**Support**: tomas.farias.e@ug.uchile.cl

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Project Structure Deep Dive](#project-structure)
3. [Core Concepts](#core-concepts)
4. [Development Workflows](#development-workflows)
5. [Testing Guide](#testing-guide)
6. [Debugging Techniques](#debugging-techniques)
7. [Database Schema](#database-schema)
8. [Extension Points](#extension-points)

---

## Getting Started

### Prerequisites

- **Python 3.10+** installed
- **VS Code with Antigravity/Claude** or similar AI coding assistant
- Basic understanding of:
  - Python and pandas
  - REST APIs
  - SQL/SQLite
  - Streamlit (for dashboard development)

### Quick Setup

```bash
# Clone/download the project
cd path/to/ExtraerDatosGoogleAnalitics_Generic

# Run automated setup
SETUP.bat  # Windows
# or
./install.sh  # Linux/Mac

# Launch the application
LAUNCH.bat  # Windows
```

### For Antigravity/Claude Users

This codebase is optimized for AI-assisted development. See [ANTIGRAVITY_GUIDE.md](ANTIGRAVITY_GUIDE.md) for specific prompts and workflows.

---

## Project Structure

```
ExtraerDatosGoogleAnalitics_Generic/
├── 📁 config/              # Configuration and settings
│   ├── settings.py         # Central configuration (DB paths, API configs)
│   ├── logging_config.py   # Logging setup with rotation
│   ├── i18n.py            # Internationalization support
│   └── apply_indexes.py    # Database index creation
│
├── 📁 etl/                 # Extract, Transform, Load modules
│   ├── extract_analytics.py    # Google Analytics 4 extractor
│   ├── extract_woocommerce.py  # WooCommerce extractor
│   └── extract_facebook.py     # Facebook Page Insights extractor
│
├── 📁 utils/               # Shared utility modules
│   ├── database.py         # Database operations (CRUD, connections)
│   ├── api_client.py       # HTTP client with retry logic
│   ├── monitoring.py       # ETL execution monitoring
│   ├── data_quality.py     # Data validation and quality checks
│   ├── cache_manager.py    # Data caching system
│   ├── export.py          # Export to PDF/Excel
│   ├── alerting.py        # Notification system (Slack/Email)
│   ├── validators.py      # Input validation functions
│   └── db_adapter.py      # SQLite/PostgreSQL adapter
│
├── 📁 dashboard/           # Streamlit web interface
│   ├── app_woo_v2.py      # Main dashboard application
│   └── pages/             # Multi-page dashboard sections
│       ├── 01_📊_Analytics.py
│       ├── 02_🛒_Products.py
│       └── 03_⚙️_System_Reset.py
│
├── 📁 tests/               # Test suite
│   ├── conftest.py        # Pytest fixtures
│   ├── test_extractors.py # ETL extraction tests
│   └── unit/              # Unit tests
│
├── 📁 scripts/             # Utility and maintenance scripts
│   ├── diagnostics/       # Diagnostic tools
│   ├── analysis/          # Data analysis scripts
│   └── migrations/        # Database migration scripts
│
├── 📁 data/                # SQLite databases (created at runtime)
│   ├── analytics.db       # Google Analytics data
│   ├── woocommerce.db     # WooCommerce data
│   └── monitoring.db      # ETL monitoring data
│
├── 📁 logs/                # Application logs (auto-rotation)
│   └── etl.log           # Main log file
│
├── 📁 docs/                # Documentation
│   ├── ARCHITECTURE.md    # System architecture
│   ├── DEPLOYMENT.md      # Deployment guides
│   ├── DEVELOPER_GUIDE.md # This file
│   └── API_REFERENCE.md   # API documentation
│
├── .env                   # Environment variables (NOT in version control)
├── .env.example           # Environment template
├── requirements.txt       # Python dependencies
├── run_pipeline.py        # Manual ETL execution
├── scheduler.py           # Automated scheduling
└── README.md              # User-facing documentation
```

---

## Core Concepts

### 1. ETL Architecture

The system follows a classic **Extract-Transform-Load** pattern:

#### Extract (`etl/*.py`)
- Connect to external APIs (GA4, WooCommerce, Facebook)
- Fetch raw data using pagination
- Handle authentication and retries

#### Transform (within extractors)
- Parse JSON responses → pandas DataFrames
- Rename columns (English API → Spanish DB)
- Convert data types (dates, currency)
- Apply business logic (status filtering, calculations)

#### Load (`utils/database.py`)
- **Incremental loading**: Only new data since last extraction
- **Append mode**: Preserves historical data
- **Indexed tables**: Optimized for dashboard queries

```python
# Typical ETL flow
last_date = get_last_extraction_date('wc_orders', 'date_only')
data = fetch_from_api(start_date=last_date)
df = transform_data(data)
save_dataframe_to_db(df, table_name, if_exists='append')
```

### 2. Incremental Loading Pattern

**Why?** Avoids re-extracting all historical data every time.

```python
# Get last extraction date
last_date = get_last_extraction_date(
    table_name='wc_orders',
    date_column='date_only',
    db_path='data/woocommerce.db'
)
# Returns: "2026-01-10"

# Extract only new data
new_orders = extract_orders(wcapi, start_date=last_date)
```

**Benefits**:
- ⚡ Faster extraction (minutes vs hours)
- 💰 Saves API quota
- 📊 Maintains complete history

### 3. Retry Logic

All external API calls use exponential backoff retry:

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def make_api_request(url, **kwargs):
    response = requests.get(url, **kwargs)
    response.raise_for_status()
    return response.json()
```

**Retry behavior**:
- Attempt 1: Immediate
- Attempt 2: Wait 2 seconds
- Attempt 3: Wait 4 seconds
- Attempt 4: Wait 8 seconds

### 4. Logging System

Structured logging with automatic rotation:

```python
from config.logging_config import setup_logger

logger = setup_logger(__name__)

logger.info("Started extraction")
logger.warning("API returned fewer results than expected")
logger.error("Failed to connect")
```

**Log location**: `logs/etl.log`  
**Rotation**: 10 MB per file, keeps 5 backups

### 5. Configuration Management

Centralized in `config/settings.py`:

```python
from config.settings import DatabaseConfig, WooConfig, GAConfig

# Get database paths
db_path = DatabaseConfig.get_woocommerce_db_path()

# Get WooCommerce credentials
wc_config = WooConfig.get_config()
# Returns: {'url': '...', 'consumer_key': '...', ...}
```

All sensitive values come from `.env` file.

---

## Development Workflows

### Adding a New Data Source

Let's add a **Shopify** extractor as an example:

#### 1. Create extractor module

```bash
# Create new file
touch etl/extract_shopify.py
```

```python
# etl/extract_shopify.py
"""
Shopify data extractor.

Extracts orders and products from Shopify API.
"""
import os
import pandas as pd
from config.logging_config import setup_logger
from utils.database import save_dataframe_to_db, get_last_extraction_date
from utils.api_client import make_api_request

logger = setup_logger(__name__)

def get_shopify_client():
    """Initialize Shopify API client."""
    api_key = os.getenv('SHOPIFY_API_KEY')
    api_password = os.getenv('SHOPIFY_API_PASSWORD')
    shop_url = os.getenv('SHOPIFY_SHOP_URL')
    
    # Return configured client
    return {
        'url': shop_url,
        'auth': (api_key, api_password)
    }

def extract_orders(client, start_date):
    """Extract orders from Shopify."""
    logger.info(f"🚀 Extracting Shopify orders from {start_date}")
    
    orders = []
    page = 1
    
    while True:
        url = f"{client['url']}/admin/api/2024-01/orders.json"
        params = {
            'created_at_min': start_date,
            'limit': 250,
            'page': page
        }
        
        response = make_api_request(url, auth=client['auth'], params=params)
        
        if not response.get('orders'):
            break
            
        orders.extend(response['orders'])
        page += 1
    
    df = pd.DataFrame(orders)
    logger.info(f"✅ Extracted {len(df)} orders")
    return df

def main():
    """Main execution function."""
    client = get_shopify_client()
    last_date = get_last_extraction_date('shopify_orders', 'created_at', 'data/shopify.db')
    
    df_orders = extract_orders(client, last_date or '2023-01-01')
    save_dataframe_to_db(df_orders, 'shopify_orders', 'data/shopify.db')

if __name__ == "__main__":
    main()
```

#### 2. Add configuration

Edit `.env.example`:
```bash
# ============================================
# SHOPIFY
# ============================================
SHOPIFY_SHOP_URL=https://your-shop.myshopify.com
SHOPIFY_API_KEY=your_api_key
SHOPIFY_API_PASSWORD=your_api_password
```

#### 3. Add to scheduler

Edit `scheduler.py`:
```python
from etl.extract_shopify import main as extract_shopify

scheduler.add_job(
    extract_shopify,
    'cron',
    hour=4,
    minute=0,
    id='shopify_extraction'
)
```

#### 4. Test

```bash
python etl/extract_shopify.py
```

### Modifying the Dashboard

#### Adding a New Metric Card

In `dashboard/app_woo_v2.py`:

```python
# Add to metrics section
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Revenue",
        value=f"${total_revenue:,.0f}",
        delta=f"{revenue_growth}%" if revenue_growth else None
    )

# Add your new metric
with col4:
    st.metric(
        label="Average Order Value",
        value=f"${avg_order_value:.2f}",
        delta=f"{aov_change}%" if aov_change else None
    )
```

#### Adding a New Chart

```python
import plotly.express as px

# Prepare data
df_chart = df.groupby('category')['revenue'].sum().reset_index()

# Create chart
fig = px.bar(
    df_chart,
    x='category',
    y='revenue',
    title="Revenue by Category"
)

# Display
st.plotly_chart(fig, use_container_width=True)
```

### Creating a New Utility Function

In `utils/helpers.py` (create if needed):

```python
"""
Helper utilities for data processing.
"""

def calculate_growth_rate(current: float, previous: float) -> float:
    """
    Calculate percentage growth rate.
    
    Args:
        current: Current period value
        previous: Previous period value
        
    Returns:
        Growth rate as percentage
        
    Example:
        >>> calculate_growth_rate(150, 100)
        50.0
    """
    if previous == 0:
        return 0.0
    return ((current - previous) / previous) * 100
```

---

## Testing Guide

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=etl --cov=utils --cov-report=html

# Run specific test file
pytest tests/test_extractors.py -v

# Run specific test
pytest tests/test_extractors.py::test_woocommerce_extraction -v
```

### Writing Tests

Create tests in `tests/`:

```python
# tests/test_my_feature.py
import pytest
from etl.extract_analytics import extract_report

def test_extract_report_with_valid_creds():
    """Test that extract_report works with valid credentials."""
    # Arrange
    property_id = "123456"
    report_config = {
        'name': 'Channels',
        'dimensions': ['date', 'sessionDefaultChannelGroup'],
        'metrics': ['sessions']
    }
    
    # Act
    result = extract_report(property_id, mock_creds, report_config)
    
    # Assert
    assert result is not None
    assert len(result) > 0
    assert 'Fecha' in result.columns
```

### Test Fixtures

Use `conftest.py` for shared fixtures:

```python
# tests/conftest.py
import pytest
import pandas as pd

@pytest.fixture
def sample_orders_df():
    """Create sample orders DataFrame for testing."""
    return pd.DataFrame({
        'order_id': [1, 2, 3],
        'status': ['completed', 'completed', 'processing'],
        'total': [100.0, 200.0, 150.0]
    })
```

---

## Debugging Techniques

### 1. Check Logs

```bash
# View last 50 lines
tail -n 50 logs/etl.log

# Follow log in real-time
tail -f logs/etl.log

# Search for errors
grep "ERROR" logs/etl.log
```

### 2. Database Inspection

```bash
# Use built-in viewer
python scripts/view_db.py

# Or use SQLite CLI
sqlite3 data/woocommerce.db
> SELECT COUNT(*) FROM wc_orders;
> SELECT * FROM wc_orders LIMIT 5;
```

### 3. Test API Connections

```python
# For WooCommerce
from etl.extract_woocommerce import get_wc_api

wcapi = get_wc_api()
response = wcapi.get("orders", params={"per_page": 1})
print(response.status_code, response.json())
```

### 4. Debug with Breakpoints

```python
# Add breakpoint in code
def my_function():
    import pdb; pdb.set_trace()  # Debugger will stop here
    # ... rest of code
```

Run with:
```bash
python -m pdb etl/extract_analytics.py
```

### 5. Enable Verbose Logging

Edit `config/logging_config.py`:

```python
# Change level to DEBUG
logger.setLevel(logging.DEBUG)
```

Now you'll see all debug messages.

---

## Database Schema

### WooCommerce Database (`data/woocommerce.db`)

#### Table: `wc_orders`

| Column | Type | Description |
|--------|------|-------------|
| `order_id` | INTEGER | Unique order ID |
| `status` | TEXT | Order status (completed, processing, etc.) |
| `date_created` | TEXT | Order creation date (ISO format) |
| `date_paid` | TEXT | Payment date |
| `total` | REAL | Total order amount |
| `subtotal` | REAL | Subtotal before taxes/shipping |
| `shipping_total` | REAL | Shipping cost |
| `tax_total` | REAL | Tax amount |
| `discount_total` | REAL | Discount amount |
| `payment_method` | TEXT | Payment method used |
| `customer_id` | INTEGER | Customer ID |
| `currency` | TEXT | Currency code (CLP, USD, etc.) |

**Indexes**:
- `idx_wc_orders_date_created` on `date_created`
- `idx_wc_orders_status` on `status`
- `idx_wc_orders_date_status` on `(date_created, status)`

#### Table: `wc_order_items`

| Column | Type | Description |
|--------|------|-------------|
| `item_id` | INTEGER | Unique item ID |
| `order_id` | INTEGER | Foreign key to wc_orders |
| `product_id` | INTEGER | Product ID |
| `product_name` | TEXT | Product name |
| `quantity` | INTEGER | Quantity ordered |
| `subtotal` | REAL | Item subtotal |
| `total` | REAL | Item total (with discounts) |

### Analytics Database (`data/analytics.db`)

#### Table: `ga4_ecommerce`

| Column | Type | Description |
|--------|------|-------------|
| `Fecha` | TEXT | Date (YYYY-MM-DD) |
| `Transacciones` | INTEGER | Number of transactions |
| `Ganancias` | REAL | Total revenue (CLP) |
| `Compradores` | INTEGER | Number of purchasers |
| `AgregadosAlCarrito` | INTEGER | Items added to cart |

**Indexes**:
- `idx_ga4_ecommerce_fecha` on `Fecha`

### Monitoring Database (`data/monitoring.db`)

#### Table: `etl_executions`

| Column | Type | Description |
|--------|------|-------------|
| `execution_id` | TEXT | Unique execution UUID |
| `etl_name` | TEXT | ETL module name |
| `start_time` | TEXT | Start timestamp |
| `end_time` | TEXT | End timestamp |
| `status` | TEXT | success/failed/running |
| `rows_loaded` | INTEGER | Number of rows loaded |
| `error_message` | TEXT | Error if failed |

---

## Extension Points

### Adding Custom Metrics

Create a new module in `utils/metrics.py`:

```python
def calculate_customer_lifetime_value(df_orders):
    """
    Calculate average customer lifetime value.
    
    Args:
        df_orders: DataFrame with order data
        
    Returns:
        Dictionary with CLV metrics
    """
    clv = df_orders.groupby('customer_id')['total'].sum().mean()
    return {
        'average_clv': clv,
        'total_customers': df_orders['customer_id'].nunique()
    }
```

### Custom Exports

Extend `utils/export.py`:

```python
def export_to_google_sheets(df, spreadsheet_id):
    """Export DataFrame to Google Sheets."""
    # Implementation
    pass
```

### Custom Alerts

Extend `utils/alerting.py`:

```python
def send_teams_notification(message):
    """Send notification to Microsoft Teams."""
    # Implementation
    pass
```

---

## Common Development Tasks

### Update Dependencies

```bash
pip install --upgrade package_name
pip freeze > requirements.txt
```

### Add Database Index

Edit `config/create_indexes.sql`:

```sql
CREATE INDEX IF NOT EXISTS idx_custom_field 
ON table_name(custom_field);
```

Run:
```bash
python config/apply_indexes.py
```

### Backup Database

```bash
# Manual backup
cp data/woocommerce.db backups/woocommerce_backup_$(date +%Y%m%d).db

# Or use built-in
python -c "from utils.database import create_backup; create_backup('woocommerce')"
```

---

## Performance Tips

1. **Use indexes**: All date columns should be indexed
2. **Batch processing**: Process large datasets in chunks
3. **Cache dashboard queries**: Use `@st.cache_data` decorator
4. **Incremental loads**: Always prefer append over replace
5. **Connection pooling**: Reuse database connections

---

## Support

**Email**: tomas.farias.e@ug.uchile.cl

For bugs or issues, check:
1. `logs/etl.log` for error messages
2. [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
3. [API_REFERENCE.md](API_REFERENCE.md) for function documentation

---

**Next Steps**: See [ANTIGRAVITY_GUIDE.md](ANTIGRAVITY_GUIDE.md) for AI-assisted development workflows.
