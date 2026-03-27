---
description: How to add a new data source to the ETL pipeline
---

# Adding a New Data Source

This workflow guides you through adding a new data source (API) to the Analytics Pipeline.

## Prerequisites

- New data source API credentials
- API documentation
- Understanding of data structure to extract

## Steps

### 1. Create the Extractor Module

Create a new file `etl/extract_<sourcename>.py`:

```bash
# Example: etl/extract_shopify.py
touch etl/extract_shopify.py
```

### 2. Implement the Base Structure

Use this template in your new extractor:

```python
"""
[Source Name] data extractor.

Extracts [data types] from [Source Name] API.
"""
import os
import pandas as pd
from config.logging_config import setup_logger
from utils.database import save_dataframe_to_db, get_last_extraction_date
from utils.api_client import make_api_request
from utils.monitoring import ETLMetrics

logger = setup_logger(__name__)

def get_client():
    """Initialize API client with credentials from .env"""
    api_key = os.getenv('[SOURCE]_API_KEY')
    # Add validation
    if not api_key:
        raise ValueError("[Source] API key not configured")
    return api_key

def extract_data(client, start_date):
    """Extract data incrementally"""
    logger.info(f"🚀 Extracting [Source] data from {start_date}")
    # Implementation here
    pass

def main():
    """Main execution function"""
    logger.info("🚀 Starting [Source] extraction")
    
    # Initialize metrics
    metrics = ETLMetrics('extract_[source]')
    metrics.start()
    
    try:
        # Get credentials
        client = get_client()
        
        # Get last extraction date
        last_date = get_last_extraction_date(
            '[source]_data',
            'date',
            'data/[source].db'
        )
        
        # Extract data
        df = extract_data(client, last_date or '2023-01-01')
        
        # Save to database
        save_dataframe_to_db(df, '[source]_data', 'data/[source].db')
        
        # Update metrics
        metrics.add_rows_loaded(len(df))
        metrics.end(status='success')
        logger.info(f"✅ Loaded {len(df)} rows")
        
    except Exception as e:
        logger.error(f"❌ Extraction failed: {e}")
        metrics.end(status='failed')
        raise

if __name__ == "__main__":
    main()
```

### 3. Add Configuration Variables

Edit `.env.example` to add new variables:

```bash
# ============================================
# [SOURCE NAME]
# ============================================
[SOURCE]_API_KEY=your_api_key_here
[SOURCE]_API_SECRET=your_secret_here
[SOURCE]_BASE_URL=https://api.example.com
```

### 4. Test the Extractor

Run manually to test:

```bash
python etl/extract_[sourcename].py
```

Check logs for errors:

```bash
tail -f logs/etl.log
```

### 5. Add to Scheduler (Optional)

Edit `scheduler.py`:

```python
from etl.extract_[sourcename] import main as extract_[sourcename]

scheduler.add_job(
    extract_[sourcename],
    'cron',
    hour=4,  # Choose appropriate time
    minute=0,
    id='[sourcename]_extraction'
)
```

### 6. Create Tests

Create `tests/test_extract_[sourcename].py`:

```python
import pytest
from etl.extract_[sourcename] import extract_data

def test_extract_data():
    """Test data extraction"""
    # Your test implementation
    pass
```

Run tests:

```bash
pytest tests/test_extract_[sourcename].py -v
```

### 7. Document the New Source

Update documentation:
- Add to README.md features list
- Document configuration in API_REFERENCE.md
- Add troubleshooting section if needed

## Verification

- [ ] Extractor runs without errors
- [ ] Data appears in database
- [ ] Incremental loading works
- [ ] Logging is informative
- [ ] Tests pass
- [ ] Documentation updated

## Using with Antigravity/Claude

Prompt example:
```
I want to add extraction from [SOURCE NAME] API.

Follow the workflow in .agent/workflows/add-new-data-source.md.

API documentation: [PASTE/LINK]
Data to extract: [DESCRIBE]
Authentication: [TYPE]

Please create the extractor following our project patterns.
```

## Common Issues

**Issue**: API authentication fails  
**Solution**: Verify credentials in .env, check API documentation

**Issue**: Data not saving to database  
**Solution**: Check database path exists, verify table schema

**Issue**: Scheduler not running new extractor  
**Solution**: Restart scheduler after adding new job

## Additional Resources

- [DEVELOPER_GUIDE.md](../../docs/DEVELOPER_GUIDE.md) - Development patterns
- [API_REFERENCE.md](../../docs/API_REFERENCE.md) - Function documentation
- [TROUBLESHOOTING.md](../../docs/TROUBLESHOOTING.md) - Common issues
