# API Reference - Analytics Pipeline

**Version**: 1.0 Generic Edition  
**Last Updated**: January 14, 2026  
**Support**: tomas.farias.e@ug.uchile.cl

---

## Table of Contents

1. [Configuration](#configuration)
2. [ETL Modules](#etl-modules)
3. [Utility Functions](#utility-functions)
4. [Database Operations](#database-operations)
5. [Monitoring & Alerts](#monitoring--alerts)
6. [Error Codes](#error-codes)

---

## Configuration

### Environment Variables Reference

All configuration is managed via `.env` file. Copy `.env.example` to `.env` and configure.

#### WooCommerce Configuration

| Variable | Type | Required | Description | Example |
|----------|------|----------|-------------|---------|
| `WC_URL` | string | Yes | WooCommerce store URL | `https://mystore.com` |
| `WC_CONSUMER_KEY` | string | Yes | WooCommerce API consumer key | `ck_abc123...` |
| `WC_CONSUMER_SECRET` | string | Yes | WooCommerce API consumer secret | `cs_xyz789...` |

**How to obtain**: WooCommerce Admin → Settings → Advanced → REST API → Add Key

#### Google Analytics 4 Configuration

| Variable | Type | Required | Description | Example |
|----------|------|----------|-------------|---------|
| `GA4_KEY_FILE` | string | Yes | Path to service account JSON | `credentials.json` |
| `GA4_PROPERTY_ID` | string | Yes | GA4 Property ID | `123456789` |

**How to obtain**:
1. Create service account in Google Cloud Console
2. Download JSON key file
3. Grant access to GA4 property

#### Facebook Configuration

| Variable | Type | Required | Description | Example |
|----------|------|----------|-------------|---------|
| `FB_ACCESS_TOKEN` | string | Optional | Facebook Page Access Token | `EAAxxxxx...` |
| `FB_PAGE_ID` | string | Optional | Facebook Page ID | `123456789` |

**How to obtain**: See [FACEBOOK_TOKEN_SETUP.md](FACEBOOK_TOKEN_SETUP.md)

#### Database Configuration

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `DATABASE_TYPE` | string | No | `sqlite` | Database type: `sqlite` or `postgresql` |
| `DATABASE_URL` | string | No* | - | PostgreSQL connection URL (*required if type=postgresql) |

#### Notification Configuration

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `SLACK_WEBHOOK_URL` | string | No | - | Slack webhook for notifications |
| `EMAIL_ALERTS_ENABLED` | boolean | No | `false` | Enable email alerts |
| `SMTP_SERVER` | string | No | - | SMTP server hostname |
| `SMTP_PORT` | integer | No | `587` | SMTP server port |
| `EMAIL_FROM` | string | No | - | Sender email address |
| `EMAIL_PASSWORD` | string | No | - | Email password or app password |
| `EMAIL_ALERTS_TO` | string | No | - | Comma-separated recipient emails |

#### Cache Configuration

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `CACHE_ENABLED` | boolean | No | `true` | Enable data caching |
| `CACHE_TTL_HOURS` | integer | No | `6` | Cache time-to-live in hours |
| `CACHE_COMPRESSION` | boolean | No | `true` | Enable cache compression |

---

## ETL Modules

### `etl.extract_analytics`

Google Analytics 4 data extraction module.

#### `main()`

Main execution function for GA4 extraction.

```python
def main() -> None
```

**Description**: Extracts all configured GA4 reports and saves to database.

**Returns**: None

**Raises**:
- `FileNotFoundError`: If GA4 key file not found
- `ValueError`: If property ID not configured
- `google.auth.exceptions.RefreshError`: If credentials invalid

**Example**:
```bash
python etl/extract_analytics.py
```

**Reports extracted**:
1. Channels (sessions by channel)
2. Countries (users by country)
3. Pages (page views)
4. Ecommerce (daily transactions and revenue)
5. Products (items sold)
6. Traffic Sources (source/medium)

#### `extract_report(property_id, creds, report_config, usd_to_clp, start_date)`

Extract a specific GA4 report.

```python
def extract_report(
    property_id: str,
    creds: service_account.Credentials,
    report_config: Dict,
    usd_to_clp: Optional[float] = None,
    start_date: str = "2023-01-01"
) -> pd.DataFrame
```

**Parameters**:
- `property_id` (str): GA4 Property ID
- `creds` (Credentials): Google service account credentials
- `report_config` (dict): Report configuration with dimensions/metrics
- `usd_to_clp` (float, optional): USD to CLP exchange rate
- `start_date` (str): Start date for extraction (YYYY-MM-DD)

**Returns**: DataFrame with extracted data

**Example**:
```python
report_config = {
    'name': 'Channels',
    'table_name': 'ga4_channels',
    'dimensions': ['date', 'sessionDefaultChannelGroup'],
    'metrics': ['sessions']
}
df = extract_report(property_id, creds, report_config)
```

---

### `etl.extract_woocommerce`

WooCommerce data extraction module.

#### `main()`

Main execution function for WooCommerce extraction.

```python
def main() -> None
```

**Description**: Extracts orders, products, and customers from WooCommerce.

**Returns**: None

**Raises**:
- `ConnectionError`: If cannot connect to WooCommerce API
- `ValueError`: If credentials not configured

**Example**:
```bash
python etl/extract_woocommerce.py
```

#### `extract_orders(wcapi, start_date, metrics=None)`

Extract orders incrementally from WooCommerce.

```python
def extract_orders(
    wcapi: API,
    start_date: str = "2025-01-01",
    metrics: Optional[ETLMetrics] = None
) -> None
```

**Parameters**:
- `wcapi` (API): WooCommerce API client
- `start_date` (str): Start date for extraction
- `metrics` (ETLMetrics, optional): Metrics tracking object

**Returns**: None (saves directly to database)

**Side effects**: Inserts data into `wc_orders` and `wc_order_items` tables

**Example**:
```python
wcapi = get_wc_api()
extract_orders(wcapi, start_date="2026-01-01")
```

#### `extract_products(wcapi, metrics=None)`

Extract all products from WooCommerce.

```python
def extract_products(wcapi: API, metrics=None) -> None
```

**Parameters**:
- `wcapi` (API): WooCommerce API client
- `metrics` (ETLMetrics, optional): Metrics tracking object

**Returns**: None

**Side effects**: Replaces `wc_products` table

---

### `etl.extract_facebook`

Facebook Page Insights extraction module.

#### `main()`

Main execution function for Facebook extraction.

```python
def main() -> None
```

**Description**: Extracts page insights and post metrics.

**Returns**: None

**Example**:
```bash
python etl/extract_facebook.py
```

---

## Utility Functions

### `utils.database`

Database operations module.

#### `get_db_connection(db_path)`

Get database connection with context manager.

```python
@contextmanager
def get_db_connection(db_path: str) -> Generator[sqlite3.Connection, None, None]
```

**Parameters**:
- `db_path` (str): Path to database file

**Yields**: Database connection

**Example**:
```python
from utils.database import get_db_connection

with get_db_connection('data/woocommerce.db') as conn:
    df = pd.read_sql("SELECT * FROM wc_orders", conn)
```

#### `save_dataframe_to_db(df, table_name, db_path, if_exists='append')`

Save DataFrame to database.

```python
def save_dataframe_to_db(
    df: pd.DataFrame,
    table_name: str,
    db_path: str,
    if_exists: str = 'append'
) -> None
```

**Parameters**:
- `df` (DataFrame): Data to save
- `table_name` (str): Target table name
- `db_path` (str): Database file path
- `if_exists` (str): Mode: 'append', 'replace', or 'fail'

**Returns**: None

**Raises**:
- `ValueError`: If if_exists value invalid

**Example**:
```python
save_dataframe_to_db(df_orders, 'wc_orders', 'data/woocommerce.db')
```

#### `get_last_extraction_date(table_name, date_column, db_path)`

Get last extraction date for incremental loading.

```python
def get_last_extraction_date(
    table_name: str,
    date_column: str,
    db_path: str
) -> Optional[str]
```

**Parameters**:
- `table_name` (str): Table to check
- `date_column` (str): Date column name
- `db_path` (str): Database file path

**Returns**: Last date as string (YYYY-MM-DD) or None if table empty

**Example**:
```python
last_date = get_last_extraction_date('wc_orders', 'date_only', 'data/woocommerce.db')
# Returns: "2026-01-13"
```

---

### `utils.api_client`

HTTP client with retry logic.

#### `make_api_request(url, method='GET', **kwargs)`

Make HTTP request with automatic retry.

```python
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def make_api_request(url: str, method: str = 'GET', **kwargs) -> dict
```

**Parameters**:
- `url` (str): Request URL
- `method` (str): HTTP method (GET, POST, etc.)
- `**kwargs`: Additional arguments for requests library

**Returns**: JSON response as dict

**Raises**:
- `requests.exceptions.HTTPError`: If request fails after retries

**Retry behavior**: 3 attempts with exponential backoff (2s, 4s, 8s)

**Example**:
```python
from utils.api_client import make_api_request

data = make_api_request(
    'https://api.example.com/data',
    headers={'Authorization': 'Bearer token'}
)
```

#### `get_usd_clp_rate()`

Get current USD to CLP exchange rate.

```python
def get_usd_clp_rate() -> float
```

**Returns**: Exchange rate as float

**Source**: mindicador.cl API

**Fallback**: 950.0 if API fails

**Example**:
```python
rate = get_usd_clp_rate()
# Returns: 975.5
```

---

### `utils.monitoring`

ETL execution monitoring.

#### `ETLMetrics` class

Track ETL execution metrics.

```python
class ETLMetrics:
    def __init__(self, etl_name: str)
    def start(self)
    def end(self, status: str = 'success')
    def add_rows_loaded(self, count: int)
    def add_error(self, error: str)
    def add_warning(self, warning: str)
```

**Example**:
```python
from utils.monitoring import ETLMetrics

metrics = ETLMetrics('extract_woocommerce')
metrics.start()
metrics.add_rows_loaded(150)
metrics.end(status='success')
```

---

### `utils.alerting`

Notification system.

#### `send_alert(message, level='INFO', channels=None)`

Send alert to configured channels.

```python
def send_alert(
    message: str,
    level: str = 'INFO',
    channels: Optional[List[str]] = None
) -> bool
```

**Parameters**:
- `message` (str): Alert message
- `level` (str): Alert level: INFO, WARNING, ERROR, CRITICAL
- `channels` (list, optional): Channels to use: ['slack', 'email']

**Returns**: True if sent to at least one channel

**Example**:
```python
from utils.alerting import send_alert

send_alert(
    "ETL completed: 150 orders processed",
    level='INFO',
    channels=['slack']
)
```

---

### `utils.export`

Data export utilities.

#### `export_to_pdf(df, filename, title)`

Export DataFrame to PDF.

```python
def export_to_pdf(
    df: pd.DataFrame,
    filename: str,
    title: str = "Report"
) -> str
```

**Parameters**:
- `df` (DataFrame): Data to export
- `filename` (str): Output filename
- `title` (str): Report title

**Returns**: Path to created PDF file

**Example**:
```python
from utils.export import export_to_pdf

pdf_path = export_to_pdf(df_sales, "sales_report.pdf", "Monthly Sales")
```

#### `export_to_excel(df, filename, sheet_name='Sheet1')`

Export DataFrame to Excel.

```python
def export_to_excel(
    df: pd.DataFrame,
    filename: str,
    sheet_name: str = 'Sheet1'
) -> str
```

**Returns**: Path to created Excel file

---

## Database Operations

### Database Paths

Access via `config.settings.DatabaseConfig`:

```python
from config.settings import DatabaseConfig

# Get database paths
analytics_db = DatabaseConfig.get_analytics_db_path()
woocommerce_db = DatabaseConfig.get_woocommerce_db_path()
monitoring_db = DatabaseConfig.get_monitoring_db_path()
```

**Default paths**:
- Analytics: `data/analytics.db`
- WooCommerce: `data/woocommerce.db`
- Monitoring: `data/monitoring.db`

### Common Queries

#### Get orders by date range

```python
import pandas as pd
from utils.database import get_db_connection

with get_db_connection('data/woocommerce.db') as conn:
    df = pd.read_sql("""
        SELECT * FROM wc_orders 
        WHERE date_created BETWEEN ? AND ?
        AND status = 'completed'
    """, conn, params=('2026-01-01', '2026-01-31'))
```

#### Get top products

```python
df = pd.read_sql("""
    SELECT product_name, SUM(quantity) as total_sold
    FROM wc_order_items
    GROUP BY product_name
    ORDER BY total_sold DESC
    LIMIT 10
""", conn)
```

---

## Monitoring & Alerts

### Alert Levels

| Level | Code | Use Case |
|-------|------|----------|
| `INFO` | 20 | Normal operations, milestones |
| `WARNING` | 30 | Potential issues, degraded performance |
| `ERROR` | 40 | Errors that need attention |
| `CRITICAL` | 50 | System failures, data loss |

### Monitoring Queries

#### Check last ETL execution

```python
from utils.monitoring import get_latest_execution

exec_info = get_latest_execution('extract_woocommerce')
print(f"Status: {exec_info['status']}")
print(f"Rows: {exec_info['rows_loaded']}")
```

---

## Error Codes

### Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `Configuration not found` | Missing `.env` file | Copy `.env.example` to `.env` |
| `WooCommerce API timeout` | Network/server issue | Check internet, increase timeout |
| `GA4 Permission denied` | Service account lacks access | Grant viewer role to service account |
| `Database locked` | Concurrent access | Use WAL mode or PostgreSQL |
| `Invalid credentials` | Wrong API keys | Verify credentials in `.env` |

### Exception Hierarchy

```
Exception
├── ConfigurationError (missing/invalid config)
├── APIConnectionError (API unreachable)
│   ├── WooCommerceAPIError
│   ├── GoogleAnalyticsAPIError
│   └── FacebookAPIError
└── DatabaseError (DB operations)
    ├── TableNotFoundError
    └── DataValidationError
```

---

## Extension Guide

### Adding Custom Data Source

See [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md#adding-a-new-data-source) for complete example.

**Quick checklist**:
1. Create `etl/extract_<source>.py`
2. Add configuration to `.env.example`
3. Add to scheduler if needed
4. Write tests
5. Document in API reference

---

**Support**: tomas.farias.e@ug.uchile.cl  
**See also**: [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md), [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
