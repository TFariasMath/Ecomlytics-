"""
Database Adapter for PostgreSQL/SQLite dual support.

This module provides a unified interface for database operations,
supporting both SQLite (local development) and PostgreSQL (cloud deployment).

Usage:
    from utils.db_adapter import get_db_adapter, get_connection
    
    # Get connection using adapter
    with get_connection('woocommerce') as conn:
        df = pd.read_sql("SELECT * FROM wc_orders", conn)
"""

import os
import sys
from contextlib import contextmanager
from typing import Optional, Union, List, Any
from pathlib import Path

# Try importing psycopg2, but don't fail if not available (SQLite-only mode)
try:
    import psycopg2
    import psycopg2.extras
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    psycopg2 = None

import sqlite3
import pandas as pd

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.logging_config import setup_logger

logger = setup_logger(__name__)


class DatabaseType:
    """Database type constants."""
    SQLITE = 'sqlite'
    POSTGRESQL = 'postgresql'


class DatabaseAdapter:
    """
    Unified database adapter supporting SQLite and PostgreSQL.
    
    Provides a consistent interface for database operations regardless
    of the underlying database engine.
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure single adapter instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize adapter with database type from environment."""
        if self._initialized:
            return
            
        self.db_type = os.getenv('DATABASE_TYPE', 'sqlite').lower()
        self.database_url = os.getenv('DATABASE_URL', '')
        
        # Validate PostgreSQL availability
        if self.db_type == DatabaseType.POSTGRESQL and not POSTGRES_AVAILABLE:
            logger.warning(
                "PostgreSQL requested but psycopg2 not installed. "
                "Falling back to SQLite."
            )
            self.db_type = DatabaseType.SQLITE
        
        # Data directory for SQLite
        self.data_dir = PROJECT_ROOT / 'data'
        self.data_dir.mkdir(exist_ok=True)
        
        self._initialized = True
        logger.info(f"🔌 DatabaseAdapter initialized: {self.db_type}")
    
    def is_postgresql(self) -> bool:
        """Check if using PostgreSQL."""
        return self.db_type == DatabaseType.POSTGRESQL
    
    def is_sqlite(self) -> bool:
        """Check if using SQLite."""
        return self.db_type == DatabaseType.SQLITE
    
    def get_sqlite_path(self, db_name: str) -> str:
        """
        Get SQLite database file path.
        
        Args:
            db_name: Database name (e.g., 'woocommerce', 'analytics')
        
        Returns:
            Full path to SQLite database file
        """
        if not db_name.endswith('.db'):
            db_name = f"{db_name}.db"
        return str(self.data_dir / db_name)
    
    def get_connection_params(self, db_name: str) -> Union[str, dict]:
        """
        Get connection parameters for the specified database.
        
        Args:
            db_name: Database name (used for SQLite path or PostgreSQL schema)
        
        Returns:
            Connection string (SQLite) or dict (PostgreSQL)
        """
        if self.is_sqlite():
            return self.get_sqlite_path(db_name)
        else:
            # PostgreSQL uses single connection URL
            return self.database_url
    
    @contextmanager
    def get_connection(self, db_name: str = 'woocommerce'):
        """
        Context manager for database connections.
        
        Args:
            db_name: Database name (for SQLite file selection)
        
        Yields:
            Database connection object
        
        Example:
            >>> with adapter.get_connection('woocommerce') as conn:
            ...     df = pd.read_sql("SELECT * FROM wc_orders", conn)
        """
        conn = None
        try:
            if self.is_sqlite():
                db_path = self.get_sqlite_path(db_name)
                conn = sqlite3.connect(db_path)
                logger.debug(f"SQLite connection opened: {db_path}")
            else:
                conn = psycopg2.connect(self.database_url)
                logger.debug("PostgreSQL connection opened")
            
            yield conn
            conn.commit()
            
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
                logger.debug("Connection closed")
    
    def get_upsert_sql(
        self,
        table_name: str,
        columns: List[str],
        unique_keys: List[str]
    ) -> str:
        """
        Generate UPSERT SQL statement for the current database type.
        
        Args:
            table_name: Target table name
            columns: List of column names
            unique_keys: List of columns forming the unique constraint
        
        Returns:
            SQL statement string
        """
        col_names = ', '.join(columns)
        placeholders = ', '.join(['?' if self.is_sqlite() else '%s' for _ in columns])
        
        if self.is_sqlite():
            # SQLite uses INSERT OR REPLACE
            return f"""
                INSERT OR REPLACE INTO {table_name} ({col_names})
                VALUES ({placeholders})
            """
        else:
            # PostgreSQL uses ON CONFLICT
            unique_cols = ', '.join(unique_keys)
            update_cols = ', '.join([
                f"{col} = EXCLUDED.{col}" 
                for col in columns if col not in unique_keys
            ])
            
            if update_cols:
                return f"""
                    INSERT INTO {table_name} ({col_names})
                    VALUES ({placeholders})
                    ON CONFLICT ({unique_cols}) DO UPDATE SET {update_cols}
                """
            else:
                return f"""
                    INSERT INTO {table_name} ({col_names})
                    VALUES ({placeholders})
                    ON CONFLICT ({unique_cols}) DO NOTHING
                """
    
    def get_table_columns_sql(self, table_name: str) -> tuple:
        """
        Get SQL to retrieve table column information.
        
        Args:
            table_name: Table name to inspect
        
        Returns:
            Tuple of (sql_query, params)
        """
        if self.is_sqlite():
            return (f"PRAGMA table_info({table_name})", None)
        else:
            return (
                """
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = %s
                ORDER BY ordinal_position
                """,
                (table_name,)
            )
    
    def get_table_exists_sql(self, table_name: str) -> tuple:
        """
        Get SQL to check if a table exists.
        
        Args:
            table_name: Table name to check
        
        Returns:
            Tuple of (sql_query, params)
        """
        if self.is_sqlite():
            return (
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table_name,)
            )
        else:
            return (
                """
                SELECT table_name FROM information_schema.tables 
                WHERE table_name = %s
                """,
                (table_name,)
            )
    
    def get_date_subtract_sql(self, column: str, days: int) -> str:
        """
        Get SQL for date subtraction.
        
        Args:
            column: Date column name
            days: Number of days to subtract
        
        Returns:
            SQL condition string
        """
        if self.is_sqlite():
            return f"datetime({column}) >= datetime('now', '-{days} days')"
        else:
            return f"{column} >= NOW() - INTERVAL '{days} days'"
    
    def get_placeholder(self) -> str:
        """Get parameter placeholder character for the database type."""
        return '?' if self.is_sqlite() else '%s'
    
    def adapt_query_params(self, query: str) -> str:
        """
        Adapt query placeholders for the current database type.
        
        Converts ? placeholders to %s for PostgreSQL.
        
        Args:
            query: SQL query with ? placeholders
        
        Returns:
            Query with correct placeholders
        """
        if self.is_postgresql():
            return query.replace('?', '%s')
        return query


# Module-level singleton instance
_adapter: Optional[DatabaseAdapter] = None


def get_db_adapter() -> DatabaseAdapter:
    """
    Get the global DatabaseAdapter instance.
    
    Returns:
        DatabaseAdapter singleton instance
    """
    global _adapter
    if _adapter is None:
        _adapter = DatabaseAdapter()
    return _adapter


@contextmanager
def get_connection(db_name: str = 'woocommerce'):
    """
    Convenience function to get a database connection.
    
    Args:
        db_name: Database name (for SQLite file selection)
    
    Yields:
        Database connection object
    
    Example:
        >>> from utils.db_adapter import get_connection
        >>> with get_connection('woocommerce') as conn:
        ...     df = pd.read_sql("SELECT * FROM wc_orders", conn)
    """
    adapter = get_db_adapter()
    with adapter.get_connection(db_name) as conn:
        yield conn


def reset_adapter():
    """
    Reset the adapter singleton (useful for testing).
    """
    global _adapter
    if _adapter is not None:
        _adapter._initialized = False
        _adapter = None


# Database name constants for convenience
class DatabaseNames:
    """Standard database names used in the application."""
    WOOCOMMERCE = 'woocommerce'
    ANALYTICS = 'analytics'
    FACEBOOK = 'facebook'
    MONITORING = 'monitoring'
