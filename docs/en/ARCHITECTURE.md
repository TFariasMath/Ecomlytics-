# 🏢 System Architecture

The Analytics & E-commerce Data Pipeline is designed with a modular architecture, separating data extraction (ETL), storage, and presentation (Dashboard).

## High-Level Architecture

```mermaid
graph TD
    subgraph External Sources
        Woo[WooCommerce API]
        GA4[Google Analytics 4 API]
        FB[Facebook Insights API]
    end

    subgraph Data Extraction Layer (ETL)
        ExWoo[extract_woocommerce.py]
        ExGA4[extract_analytics.py]
        ExFB[extract_facebook.py]
    end

    subgraph Data Storage Layer
        DBWoo[(woocommerce.db)]
        DBGA4[(analytics.db)]
        DBFB[(facebook.db)]
        DBMon[(monitoring.db)]
    end

    subgraph Presentation Layer
        Streamlit[Streamlit Dashboard\napp_woo_v2.py]
    end

    Woo --> ExWoo
    GA4 --> ExGA4
    FB --> ExFB

    ExWoo --> DBWoo
    ExGA4 --> DBGA4
    ExFB --> DBFB
    
    ExWoo -.-> DBMon
    ExGA4 -.-> DBMon
    ExFB -.-> DBMon

    DBWoo --> Streamlit
    DBGA4 --> Streamlit
    DBFB --> Streamlit
```

## Key Components

### 1. External APIs
- **WooCommerce**: The primary source of truth for sales, orders, and customer data.
- **Google Analytics 4 (GA4)**: Provides insights into web traffic, user acquisition, and on-site behavior.
- **Facebook**: Offers metrics on page engagement and social reach.

### 2. Extraction Scripts (ETL)
Located in the `etl/` directory. These Python scripts are responsible for fetching data from the APIs, cleaning it, and loading it into local databases.
- They implement **exponential backoff** (retry logic) to handle API rate limits and temporary failures gracefully.
- They log execution metrics and errors to the `monitoring.db`.

### 3. SQLite Databases
For simplicity and ease of deployment, the system uses entirely local SQLite databases stored in the `data/` directory.
- `woocommerce.db`: Contains `wc_orders`, `wc_order_items`, `wc_products`, `wc_customers`.
- `analytics.db`: Contains tables like `ga4_channels`, `ga4_pages`, `ga4_ecommerce`.
- Custom indexes are automatically built during initialization to optimize query performance for the dashboard.

### 4. Streamlit Dashboard
Located in `dashboard/app_woo_v2.py`. This is the interactive frontend.
- It pulls data directly from the SQLite databases using optimized SQL queries.
- Utilizes **Plotly** for responsive, interactive charting.
- Implements a modular layout with a sidebar for navigation and dynamic content rendering based on the selected view.
- Features a built-in Setup page (`pages/setup.py`) for managing API credentials dynamically without touching `.env` files directly.

## Data Flow
1. The **Scheduler** (`scheduler.py`) or a human user triggers the ETL scripts.
2. The ETL scripts read credentials from the `.env` file via `config/settings.py`.
3. APIs are queried for incremental updates.
4. Data is validated and upserted into the SQLite databases.
5. A user accesses `http://localhost:8501`.
6. Streamlit reads the fresh data from SQLite and renders the visualizations.
