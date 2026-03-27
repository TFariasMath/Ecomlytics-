"""
SQLite to PostgreSQL Migration Script.

This script migrates all data from local SQLite databases to a PostgreSQL instance.
Run this once when switching from SQLite to PostgreSQL.

Usage:
    1. Set DATABASE_URL environment variable with your PostgreSQL connection string
    2. Run: python scripts/migrate_to_postgres.py

Example:
    export DATABASE_URL="postgresql://user:pass@host:5432/dbname"
    python scripts/migrate_to_postgres.py
"""

import os
import sys
import sqlite3
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd

try:
    import psycopg2
    from psycopg2 import sql
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    print("❌ psycopg2 not installed. Run: pip install psycopg2-binary")
    sys.exit(1)

from config.logging_config import setup_logger

logger = setup_logger(__name__)


# Database configuration
DATA_DIR = PROJECT_ROOT / 'data'
SQLITE_DATABASES = [
    ('woocommerce.db', ['wc_orders', 'wc_order_items', 'wc_products', 'wc_customers']),
    ('analytics.db', ['ga4_channels', 'ga4_countries', 'ga4_pages', 'ga4_ecommerce', 'ga4_traffic_sources']),
    ('facebook.db', ['fb_metrics']),
    ('monitoring.db', ['etl_executions']),
]


def get_postgres_connection():
    """Get PostgreSQL connection from environment variable."""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError(
            "DATABASE_URL environment variable not set. "
            "Set it to your PostgreSQL connection string."
        )
    return psycopg2.connect(database_url)


def get_sqlite_tables(db_path: str) -> list:
    """Get list of tables in SQLite database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables


def migrate_table(sqlite_path: str, table_name: str, pg_conn) -> int:
    """
    Migrate a single table from SQLite to PostgreSQL.
    
    Args:
        sqlite_path: Path to SQLite database file
        table_name: Name of table to migrate
        pg_conn: PostgreSQL connection
    
    Returns:
        Number of rows migrated
    """
    try:
        # Read from SQLite
        sqlite_conn = sqlite3.connect(sqlite_path)
        df = pd.read_sql(f"SELECT * FROM {table_name}", sqlite_conn)
        sqlite_conn.close()
        
        if df.empty:
            logger.info(f"  ⏭️  {table_name}: Empty table, skipping")
            return 0
        
        # Write to PostgreSQL using pandas
        from sqlalchemy import create_engine
        database_url = os.getenv('DATABASE_URL')
        engine = create_engine(database_url)
        
        # Use 'replace' to overwrite existing data during migration
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        
        logger.info(f"  ✅ {table_name}: {len(df)} rows migrated")
        return len(df)
        
    except Exception as e:
        logger.error(f"  ❌ {table_name}: Error - {e}")
        return 0


def create_indexes(pg_conn):
    """Create indexes for better query performance."""
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_wc_orders_date ON wc_orders(date_only)",
        "CREATE INDEX IF NOT EXISTS idx_wc_orders_status ON wc_orders(status)",
        "CREATE INDEX IF NOT EXISTS idx_wc_order_items_order ON wc_order_items(order_id)",
        "CREATE INDEX IF NOT EXISTS idx_ga4_ecommerce_date ON ga4_ecommerce(\"Fecha\")",
        "CREATE INDEX IF NOT EXISTS idx_etl_start_time ON etl_executions(start_time)",
    ]
    
    cursor = pg_conn.cursor()
    for idx_sql in indexes:
        try:
            cursor.execute(idx_sql)
            logger.info(f"  ✅ Index created")
        except Exception as e:
            logger.warning(f"  ⚠️ Index error (may already exist): {e}")
    
    pg_conn.commit()


def main():
    """Run the migration."""
    print("=" * 60)
    print("🚀 SQLite to PostgreSQL Migration")
    print("=" * 60)
    
    # Verify PostgreSQL connection
    try:
        pg_conn = get_postgres_connection()
        logger.info("✅ PostgreSQL connection successful")
    except Exception as e:
        logger.error(f"❌ PostgreSQL connection failed: {e}")
        sys.exit(1)
    
    total_rows = 0
    
    for db_file, expected_tables in SQLITE_DATABASES:
        db_path = DATA_DIR / db_file
        
        if not db_path.exists():
            logger.warning(f"⚠️ {db_file}: File not found, skipping")
            continue
        
        logger.info(f"\n📁 Migrating {db_file}...")
        
        # Get actual tables in the database
        actual_tables = get_sqlite_tables(str(db_path))
        
        for table in actual_tables:
            rows = migrate_table(str(db_path), table, pg_conn)
            total_rows += rows
    
    # Create indexes
    logger.info("\n📇 Creating indexes...")
    create_indexes(pg_conn)
    
    pg_conn.close()
    
    print("\n" + "=" * 60)
    print(f"✅ Migration complete! {total_rows:,} total rows migrated")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Update your .env file:")
    print("   DATABASE_TYPE=postgresql")
    print("   DATABASE_URL=your_connection_string")
    print("2. Restart your application")
    print("3. Verify data in the dashboard")


if __name__ == "__main__":
    main()
