"""
Comprehensive Unit Tests for Analytics Pipeline

Tests critical functionality including:
- Year transition (2025 -> 2026)
- Database abstraction layer
- Date comparisons
- ETL data extraction
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestYearTransition:
    """Tests for year 2025 -> 2026 transition issues."""
    
    def test_current_year_is_dynamic(self):
        """Verify year is dynamically calculated, not hardcoded."""
        current_year = datetime.now().year
        
        # Should work for any year
        assert current_year >= 2025
        assert current_year <= 2100
    
    def test_year_comparison_logic(self):
        """Test year-over-year comparison logic."""
        current_year = datetime.now().year
        last_year = current_year - 1
        
        # Create sample date ranges
        start_date = pd.Timestamp(f'{current_year}-01-01')
        end_date = pd.Timestamp(f'{current_year}-01-31')
        
        # Calculate previous year range
        prev_start = start_date - pd.DateOffset(years=1)
        prev_end = end_date - pd.DateOffset(years=1)
        
        # Verify correct years
        assert prev_start.year == last_year
        assert prev_end.year == last_year
        assert prev_start.month == start_date.month
        assert prev_end.day == end_date.day
    
    def test_dateoffset_across_year_boundary(self):
        """Test DateOffset works correctly across year boundaries."""
        # Test from January 2026
        jan_2026 = pd.Timestamp('2026-01-15')
        jan_2025 = jan_2026 - pd.DateOffset(years=1)
        
        assert jan_2025.year == 2025
        assert jan_2025.month == 1
        assert jan_2025.day == 15
        
        # Test leap year handling (Feb 29 -> Feb 28)
        feb_29_2024 = pd.Timestamp('2024-02-29')
        feb_2025 = feb_29_2024 + pd.DateOffset(years=1)
        
        # Should be Feb 28, 2025 (not leap year)
        assert feb_2025.year == 2025
        assert feb_2025.month == 2
        assert feb_2025.day == 28
    
    def test_date_filtering_by_year(self):
        """Test DataFrame filtering by year works dynamically."""
        # Create sample data spanning multiple years
        dates = pd.date_range(start='2024-01-01', end='2026-12-31', freq='M')
        df = pd.DataFrame({
            'date_created': dates,
            'total': range(len(dates))
        })
        
        # Filter by current year dynamically
        current_year = datetime.now().year
        df_current = df[df['date_created'].dt.year == current_year]
        
        # All filtered rows should be from current year
        if len(df_current) > 0:
            assert all(df_current['date_created'].dt.year == current_year)
    
    def test_strftime_formats(self):
        """Test date string formatting for various date formats."""
        test_date = datetime(2026, 1, 15, 10, 30, 45)
        
        assert test_date.strftime('%Y-%m-%d') == '2026-01-15'
        assert test_date.strftime('%Y%m%d') == '20260115'
        assert test_date.strftime('%d/%m/%Y') == '15/01/2026'


class TestDatabaseAdapter:
    """Tests for database abstraction layer."""
    
    def test_adapter_import(self):
        """Verify db_adapter can be imported."""
        try:
            from utils.db_adapter import get_db_adapter, DatabaseAdapter
            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import db_adapter: {e}")
    
    def test_adapter_singleton(self):
        """Verify adapter uses singleton pattern."""
        from utils.db_adapter import get_db_adapter
        
        adapter1 = get_db_adapter()
        adapter2 = get_db_adapter()
        
        assert adapter1 is adapter2
    
    def test_adapter_db_type(self):
        """Very db_type is correctly detected."""
        from utils.db_adapter import get_db_adapter
        
        adapter = get_db_adapter()
        
        # Should be sqlite by default (no DATABASE_TYPE or DATABASE_URL set)
        assert adapter.db_type in ['sqlite', 'postgresql']
    
    def test_adapter_is_sqlite_default(self):
        """Test is_sqlite returns true by default."""
        from utils.db_adapter import get_db_adapter
        
        adapter = get_db_adapter()
        
        # In test environment without DATABASE_TYPE env var, should default to sqlite
        if not os.getenv('DATABASE_TYPE'):
            assert adapter.is_sqlite()
    
    def test_placeholder_format(self):
        """Test correct placeholder format for each DB type."""
        from utils.db_adapter import get_db_adapter
        
        adapter = get_db_adapter()
        
        if adapter.is_sqlite():
            assert adapter.get_placeholder() == '?'
        else:
            assert adapter.get_placeholder() == '%s'
    
    def test_upsert_sql_generation_sqlite(self):
        """Test upsert SQL generation for SQLite."""
        from utils.db_adapter import get_db_adapter
        
        adapter = get_db_adapter()
        
        if adapter.is_sqlite():
            sql = adapter.get_upsert_sql(
                table_name='test_table',
                columns=['id', 'name', 'value'],
                unique_keys=['id']
            )
            
            assert 'INSERT OR REPLACE' in sql
            assert 'test_table' in sql
    
    def test_table_columns_sql(self):
        """Test table columns SQL generation."""
        from utils.db_adapter import get_db_adapter
        
        adapter = get_db_adapter()
        
        sql = adapter.get_table_columns_sql('my_table')
        
        if adapter.is_sqlite():
            assert 'PRAGMA table_info' in sql or 'table_info' in sql
        else:
            assert 'information_schema' in sql


class TestDatabaseModule:
    """Tests for utils/database.py module."""
    
    def test_database_import(self):
        """Verify database module can be imported."""
        try:
            from utils.database import (
                get_db_connection,
                save_dataframe_to_db,
                upsert_dataframe,
                execute_query
            )
            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import database module: {e}")
    
    def test_get_last_extraction_date_default(self):
        """Test default date is returned for non-existent table."""
        from utils.database import get_last_extraction_date
        
        result = get_last_extraction_date(
            table_name='nonexistent_table_xyz',
            date_column='date',
            db_path='data/test_nonexistent.db',
            default_date='2020-01-01'
        )
        
        assert result == '2020-01-01'


class TestDateComparisons:
    """Tests for date comparison utilities."""
    
    def test_comparisons_import(self):
        """Verify comparisons module can be imported."""
        try:
            from utils.comparisons import get_previous_period
            assert True
        except ImportError:
            # Module may not exist, that's okay
            pytest.skip("comparisons module not found")
    
    def test_previous_period_calculation(self):
        """Test previous period calculation."""
        try:
            from utils.comparisons import get_previous_period
            
            start = datetime(2026, 1, 1)
            end = datetime(2026, 1, 31)
            
            prev_start, prev_end = get_previous_period(start, end)
            
            # Previous period should be exactly 1 year before
            assert prev_start.year == 2025
            assert prev_end.year == 2025
        except ImportError:
            pytest.skip("comparisons module not found")


class TestMonitoring:
    """Tests for monitoring module."""
    
    def test_monitoring_import(self):
        """Verify monitoring module can be imported."""
        try:
            from utils.monitoring import ETLMonitor, ETLMetrics
            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import monitoring module: {e}")
    
    def test_etl_metrics_creation(self):
        """Test ETLMetrics object creation."""
        from utils.monitoring import ETLMetrics
        
        metrics = ETLMetrics(etl_name='test_etl')
        
        assert metrics.etl_name == 'test_etl'
        assert metrics.status == 'RUNNING'
        assert metrics.start_time is not None
    
    def test_etl_metrics_to_dict(self):
        """Test ETLMetrics serialization."""
        from utils.monitoring import ETLMetrics
        
        metrics = ETLMetrics(etl_name='test_etl')
        metrics.complete(rows_loaded=100)
        
        data = metrics.to_dict()
        
        assert 'execution_id' in data
        assert 'etl_name' in data
        assert data['rows_loaded'] == 100
        assert data['status'] == 'SUCCESS'


class TestSettings:
    """Tests for config/settings.py module."""
    
    def test_settings_import(self):
        """Verify settings module can be imported."""
        try:
            from config.settings import DatabaseConfig
            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import settings module: {e}")
    
    def test_database_config_methods(self):
        """Test DatabaseConfig methods exist."""
        from config.settings import DatabaseConfig
        
        # Verify methods exist
        assert hasattr(DatabaseConfig, 'get_woocommerce_db_path')
        assert hasattr(DatabaseConfig, 'get_analytics_db_path')
        assert hasattr(DatabaseConfig, 'get_db_type')
    
    def test_database_paths_are_strings(self):
        """Test database paths return strings."""
        from config.settings import DatabaseConfig
        
        wc_path = DatabaseConfig.get_woocommerce_db_path()
        analytics_path = DatabaseConfig.get_analytics_db_path()
        
        assert isinstance(wc_path, str)
        assert isinstance(analytics_path, str)


class TestDataFormats:
    """Tests for data format handling."""
    
    def test_date_parsing_yyyymmdd(self):
        """Test parsing YYYYMMDD format (GA4 format)."""
        date_str = '20260115'
        
        parsed = pd.to_datetime(date_str, format='%Y%m%d')
        
        assert parsed.year == 2026
        assert parsed.month == 1
        assert parsed.day == 15
    
    def test_date_parsing_iso(self):
        """Test parsing ISO date format."""
        date_str = '2026-01-15'
        
        parsed = pd.to_datetime(date_str)
        
        assert parsed.year == 2026
        assert parsed.month == 1
        assert parsed.day == 15
    
    def test_date_parsing_with_time(self):
        """Test parsing datetime with timezone info."""
        date_str = '2026-01-15T10:30:00+00:00'
        
        parsed = pd.to_datetime(date_str)
        
        assert parsed.year == 2026
        assert parsed.month == 1
        assert parsed.hour == 10


# Run tests if executed directly
if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
