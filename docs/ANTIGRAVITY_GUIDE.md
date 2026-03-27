# Antigravity/Claude User Guide - Analytics Pipeline

**For Developers using AI-Assisted Coding Tools**  
**Version**: 1.0  
**Last Updated**: January 14, 2026

---

## Welcome! 👋

This guide is specifically for developers using **Antigravity** (Google's AI coding assistant) or **Claude Code** to work with this codebase. The project is structured to be AI-assistant-friendly with clear documentation, consistent patterns, and comprehensive examples.

---

## Quick Start with Antigravity

### 1. Initial Code Understanding

When you first open the project, start with these prompts:

```
📍 "Give me an overview of this codebase structure and what it does"

📍 "Explain the main data flow from API extraction to dashboard visualization"

📍 "Show me where the WooCommerce data extraction logic is implemented"
```

### 2. Navigating the Codebase

Use these prompts to explore:

```
📍 "Where is the database connection logic implemented?"

📍 "Show me all the functions related to Google Analytics extraction"

📍 "Find where the Streamlit dashboard queries WooCommerce data"

📍 "List all configuration options available in .env"
```

### 3. Understanding Specific Features

```
📍 "Explain how incremental loading works in this system"

📍 "Show me the retry logic implementation for API calls"

📍 "How does the system handle database connection errors?"
```

---

## Common Development Tasks with AI Assistance

### Task 1: Adding a New Data Source

**Prompt Pattern**:
```
I want to add extraction from [DATA SOURCE]. 

Current extractors are in /etl/ folder and follow this pattern:
1. Get credentials from .env
2. Use incremental loading with get_last_extraction_date()
3. Fetch data with retry logic
4. Transform to DataFrame
5. Save with save_dataframe_to_db()

Please create a new extractor following this pattern for [DATA SOURCE].
Include:
- Error handling
- Logging statements
- Type hints
- Docstrings
```

**Follow-up prompts**:
```
📍 "Now add the configuration variables to .env.example"

📍 "Add this extractor to the scheduler to run daily at 4 AM"

📍 "Create a test function for this new extractor"
```

### Task 2: Modifying the Dashboard

**Prompt Pattern**:
```
I want to add a new chart to the dashboard showing [METRIC].

The dashboard is in dashboard/app_woo_v2.py. It uses:
- Streamlit for UI
- Plotly for charts
- Data from SQLite databases in /data

Please:
1. Query the necessary data from the database
2. Create a Plotly chart
3. Add it to the appropriate section
4. Include filtering options
```

**Example**:
```
📍 "Add a line chart showing daily revenue trend for the last 30 days"

📍 "Create a bar chart comparing product categories by sales volume"

📍 "Add a pie chart showing revenue distribution by payment method"
```

### Task 3: Debugging Issues

**Effective Debug Prompts**:
```
📍 "I'm getting this error: [PASTE ERROR]. 
    Looking at the code in [FILE], what's causing this?"

📍 "The GA4 extractor is not loading any new data. 
    Check the incremental loading logic and identify the issue"

📍 "Dashboard shows $0 revenue but database has orders. 
    Trace

 the data flow and find where it breaks"
```

### Task 4: Adding Tests

**Prompt Pattern**:
```
Create pytest tests for the function [FUNCTION_NAME] in [FILE].

The test should:
- Use fixtures from tests/conftest.py
- Mock external API calls
- Test success and failure scenarios
- Follow the existing test patterns in tests/

Include edge cases like empty data, invalid credentials, and network errors.
```

### Task 5: Improving Code Quality

```
📍 "Add comprehensive Google-style docstrings to all functions in utils/database.py"

📍 "Add type hints to the extract_orders function in etl/extract_woocommerce.py"

📍 "Refactor the data transformation logic in extract_analytics.py to be more modular"

📍 "Identify any code smells or anti-patterns in [FILE]"
```

---

## Prompts for Common Questions

### Understanding Configuration

```
📍 "What environment variables are required to run this system?"

📍 "How do I configure WooCommerce API credentials?"

📍 "Explain the database configuration options (SQLite vs PostgreSQL)"
```

### Data Flow Questions

```
📍 "Trace a WooCommerce order from API extraction to dashboard display"

📍 "How is the USD to CLP exchange rate fetched and applied?"

📍 "Explain the incremental loading mechanism with examples"
```

### Testing & Validation

```
📍 "How can I test the WooCommerce API connection without running full extraction?"

📍 "Show me how to validate that data was extracted correctly"

📍 "Create a diagnostic script to check database health"
```

---

## Project-Specific AI Workflows

### Workflow 1: Extending Analytics Metrics

```markdown
Step 1: Understand current metrics
📍 "List all metrics currently extracted from Google Analytics 4"

Step 2: Identify extension point
📍 "Where in extract_analytics.py should I add a new report?"

Step 3: Generate code
📍 "Add a new report for 'Device Category' with dimensions 
    [date, deviceCategory] and metrics [sessions, activeUsers]"

Step 4: Test
📍 "Create a test to verify the new report extraction works"

Step 5: Update dashboard
📍 "Add a visualization for device category breakdown in the dashboard"
```

### Workflow 2: Performance Optimization

```markdown
Step 1: Identify bottlenecks
📍 "Analyze extract_woocommerce.py for performance bottlenecks"

Step 2: Suggest improvements
📍 "Suggest optimizations for the batch processing logic"

Step 3: Implement caching
📍 "Add caching to the dashboard query that loads top products"

Step 4: Add indexes
📍 "Generate SQL to create optimal indexes for this query: [QUERY]"
```

### Workflow 3: Adding Alerts

```markdown
Step 1: Understand alerting system
📍 "Explain how the notification system works in utils/alerting.py"

Step 2: Design alert
📍 "I want to send a Slack alert when daily revenue drops >20%. 
    Where and how should I implement this?"

Step 3: Generate code
📍 "Implement the revenue drop alert with the following logic: [LOGIC]"

Step 4: Test
📍 "Create a test that simulates a revenue drop and verifies the alert"
```

---

## Code Patterns to Know

When working with Antigravity, knowing these patterns helps you give better prompts:

### Pattern 1: ETL Function Structure

```python
def main():
    """Standard ETL main function pattern"""
    # 1. Setup
    logger.info("🚀 Starting extraction")
    credentials = get_credentials()
    
    # 2. Get last extraction date (incremental)
    last_date = get_last_extraction_date(table, column, db)
    
    # 3. Initialize monitoring
    metrics = ETLMetrics('extractor_name')
    metrics.start()
    
    # 4. Extract data
    data = extract_data(credentials, start_date=last_date)
    
    # 5. Transform
    df = transform_data(data)
    
    # 6. Load
    save_dataframe_to_db(df, table, db, if_exists='append')
    
    # 7. Complete
    metrics.add_rows_loaded(len(df))
    metrics.end(status='success')
    logger.info(f"✅ Loaded {len(df)} rows")
```

**Use this when**: Asking to create new extractors or modify existing ones

### Pattern 2: Dashboard Query Pattern

```python
# Standard dashboard data loading
@st.cache_data(ttl=3600)
def load_orders_data(start_date, end_date):
    """Cache-enabled data loading"""
    with get_db_connection('data/woocommerce.db') as conn:
        df = pd.read_sql("""
            SELECT * FROM wc_orders
            WHERE date_created BETWEEN ? AND ?
        """, conn, params=(start_date, end_date))
    return df
```

**Use this when**: Adding new dashboard visualizations

### Pattern 3: Configuration Access

```python
# Get config from environment
from config.settings import WooConfig, GAConfig, DatabaseConfig

wc_config = WooConfig.get_config()
db_path = DatabaseConfig.get_woocommerce_db_path()
```

**Use this when**: Working with credentials or database paths

---

## Debugging with AI

### Effective Error Sharing

When you hit an error, share:

```
I'm getting this error:
[FULL ERROR TRACEBACK]

Context:
- I was running: [COMMAND]
- Expected: [EXPECTED BEHAVIOR]
- Actually got: [ACTUAL BEHAVIOR]

Relevant code (lines X-Y of file.py):
[CODE SNIPPET]

Recent changes:
[WHAT YOU MODIFIED]
```

### Using Logs for Context

```
📍 "Here are the last 50 lines of logs: [PASTE LOGS]
    What went wrong in the ETL extraction?"
```

### Database State Questions

```
📍 "I ran this query: [QUERY] and got: [RESULTS]
    Is this expected? What might be wrong?"
```

---

## Testing with AI

### Generate Test Cases

```
📍 "Generate pytest test cases for utils/database.py covering:
    - Normal operation
    - Empty database
    - Invalid parameters
    - Database locked scenario
    - Connection failures"
```

### Mock External Dependencies

```
📍 "Create mocks for the WooCommerce API in conftest.py so I can 
    test extract_woocommerce.py without real API calls"
```

### Test Data Generation

```
📍 "Generate realistic sample data for wc_orders table with 100 rows 
    covering various statuses and date ranges"
```

---

## Best Practices for AI-Assisted Development

### ✅ DO

1. **Provide context**: Always mention which file/function you're working with
2. **Share code snippets**: Paste relevant code sections
3. **Reference existing patterns**: "Like how it's done in extract_analytics.py"
4. **Specify requirements**: Type hints, docstrings, error handling needed
5. **Ask for explanations**: Understanding helps you modify later

### ❌ DON'T

1. **Assume AI knows latest state**: Always provide current code
2. **Skip error messages**: Full tracebacks are helpful
3. **Request everything at once**: Break into smaller tasks
4. **Forget to test**: Always ask for test code too
5. **Ignore project conventions**: Follow existing patterns

---

## Quick Reference Commands

### File Navigation Prompts

```
📍 "Show me the structure of the /etl directory"
📍 "List all utility functions in utils/database.py"
📍 "Find all references to get_last_extraction_date"
📍 "Show me imports in dashboard/app_woo_v2.py"
```

### Code Analysis Prompts

```
📍 "Explain what this function does: [PASTE FUNCTION]"
📍 "What are the dependencies between these modules: [LIST]"
📍 "Find potential bugs in this code: [PASTE CODE]"
📍 "Suggest improvements for this implementation: [CODE]"
```

### Documentation Prompts

```
📍 "Generate a docstring for this function following Google style"
📍 "Create README section explaining how to add a new data source"
📍 "Write API documentation for utils/export.py functions"
```

---

## Project-Specific Knowledge Base

### Key Files to Understand

1. **`config/settings.py`**: Central configuration, all path definitions
2. **`utils/database.py`**: All database operations, critical for data flow
3. **`etl/extract_*.py`**: Data extraction logic, follow these patterns
4. **`dashboard/app_woo_v2.py`**: Main dashboard, large file (~4400 lines)

### Important Concepts

- **Incremental Loading**: Only fetch new data since last run
- **Database Adapter**: Supports both SQLite and PostgreSQL
- **ETL Monitoring**: Tracks every extraction in monitoring.db
- **Retry Logic**: Automatic retry with exponential backoff
- **Caching**: Dashboard queries cached for performance

---

## Advanced AI Workflows

### Refactoring Large Functions

```
📍 "The main() function in extract_woocommerce.py is 100+ lines.
    Suggest how to refactor it into smaller, testable functions.
    Show the refactored code."
```

### Migrating to New Patterns

```
📍 "I want to migrate from SQLite to PostgreSQL.
    Analyze db_adapter.py and create a migration strategy.
    What code needs to change?"
```

### Performance Analysis

```
📍 "Analyze this query for performance issues: [QUERY]
    The table has 100K rows. Suggest optimizations."
```

---

## Troubleshooting with AI

### When Stuck

```
📍 "I've tried [A, B, C] but still getting [ERROR].
    What else could be wrong?"

📍 "The documentation says [X] but I see [Y] in the code.
    Which is correct?"
```

### Understanding Error Messages

```
📍 "Explain this error in simple terms: [ERROR]
    What does it mean for this specific codebase?"
```

---

## Support Resources

- **Email**: tomas.farias.e@ug.uchile.cl
- **Docs**: [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)
- **API Ref**: [API_REFERENCE.md](API_REFERENCE.md)  
- **Troubleshooting**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## Example: Complete Feature Addition

Let's walk through adding a "Customer Lifetime Value" metric:

```markdown
Step 1: Understand requirements
📍 "I want to calculate and display Customer Lifetime Value (CLV) 
    in the dashboard. CLV = total spend per customer divided by months active.
    Which files need to be modified?"

Step 2: Create helper function
📍 "Create a function in utils/metrics.py that calculates CLV from 
    the wc_orders DataFrame. Include type hints and docstring."

Step 3: Add to dashboard
📍 "Add a CLV metric card to the main dashboard page.
    It should show average CLV and a distribution chart."

Step 4: Add tests
📍 "Create pytest tests for the CLV calculation function.
    Include edge cases like single-order customers and refunds."

Step 5: Document
📍 "Add documentation for the CLV feature to USER_GUIDE.md"
```

---

**Remember**: This codebase is designed to be readable and maintainable. Take time to understand existing patterns before adding new code. When in doubt, ask AI to explain before modifying!
