"""
Utilidades para operaciones de base de datos.

Funciones compartidas para conexión, guardado y consultas.
Soporta SQLite (local) y PostgreSQL (cloud).

v1.3: Añadido soporte para PostgreSQL con compatibilidad hacia atrás.
"""

import sqlite3
import pandas as pd
from contextlib import contextmanager
from typing import Optional, List, Union
import os
import sys

# Agregar path para imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config.logging_config import setup_logger

# Import adapter for dual-database support
try:
    from utils.db_adapter import get_db_adapter, DatabaseNames
    ADAPTER_AVAILABLE = True
except ImportError:
    ADAPTER_AVAILABLE = False

logger = setup_logger(__name__)


def _is_postgresql() -> bool:
    """Check if using PostgreSQL."""
    if ADAPTER_AVAILABLE:
        return get_db_adapter().is_postgresql()
    return False


def _get_placeholder() -> str:
    """Get parameter placeholder for current database type."""
    return '%s' if _is_postgresql() else '?'


@contextmanager
def get_db_connection(db_path_or_name: str):
    """
    Context manager para conexiones a base de datos.
    
    Soporta tanto SQLite (path) como PostgreSQL (nombre lógico).
    
    Args:
        db_path_or_name: Ruta a la base de datos SQLite o nombre de DB para PostgreSQL
    
    Yields:
        Conexión a base de datos
    
    Example:
        >>> with get_db_connection('data/analytics.db') as conn:
        ...     df.to_sql('tabla', conn, if_exists='append')
    """
    conn = None
    
    try:
        if _is_postgresql() and ADAPTER_AVAILABLE:
            # PostgreSQL mode - use adapter
            adapter = get_db_adapter()
            # Extract db name from path if needed
            if '.db' in db_path_or_name:
                db_name = os.path.basename(db_path_or_name).replace('.db', '')
            else:
                db_name = db_path_or_name
            
            import psycopg2
            conn = psycopg2.connect(adapter.database_url)
            logger.debug(f"PostgreSQL connection opened for {db_name}")
        else:
            # SQLite mode - direct connection
            conn = sqlite3.connect(db_path_or_name)
            logger.debug(f"SQLite connection opened: {db_path_or_name}")
        
        yield conn
        conn.commit()
        logger.debug("Cambios commiteados")
        
    except Exception as e:
        if conn:
            conn.rollback()
            logger.error(f"Error en DB, rollback ejecutado: {e}")
        raise
    finally:
        if conn:
            conn.close()
            logger.debug("Conexión cerrada")


def save_dataframe_to_db(
    df: pd.DataFrame,
    table_name: str,
    db_path: str,
    if_exists: str = 'append'
) -> None:
    """
    Guarda DataFrame en base de datos con manejo de errores.
    
    Soporta SQLite y PostgreSQL.
    
    Args:
        df: DataFrame a guardar
        table_name: Nombre de la tabla
        db_path: Ruta a la base de datos (SQLite) o nombre lógico (PostgreSQL)
        if_exists: Acción si existe ('append', 'replace', 'fail')
    
    Raises:
        ValueError: Si el DataFrame está vacío
    """
    if df.empty:
        logger.warning(f"DataFrame vacío, no se guardó en {table_name}")
        return
    
    # Asegurar que el directorio existe (solo para SQLite)
    if not _is_postgresql() and db_path:
        dir_path = os.path.dirname(db_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
    
    try:
        with get_db_connection(db_path) as conn:
            df.to_sql(table_name, conn, if_exists=if_exists, index=False)
            logger.info(f"✅ Guardadas {len(df)} filas en {table_name} ({if_exists})")
    except Exception as e:
        logger.error(f"Error guardando en {table_name}: {e}", exc_info=True)
        raise


def upsert_dataframe(
    df: pd.DataFrame,
    table_name: str,
    db_path: str,
    unique_keys: List[str],
    batch_size: int = 1000
) -> None:
    """
    Inserta o actualiza datos usando lógica UPSERT.
    
    - SQLite: INSERT OR REPLACE
    - PostgreSQL: INSERT ... ON CONFLICT DO UPDATE
    
    Args:
        df: DataFrame a guardar
        table_name: Nombre de la tabla
        db_path: Ruta a la base de datos
        unique_keys: Lista de columnas que forman la clave única
        batch_size: Tamaño de lote para inserciones
    
    Example:
        >>> df = pd.DataFrame({'order_id': [1, 2], 'total': [100, 200]})
        >>> upsert_dataframe(df, 'orders', 'data/wc.db', unique_keys=['order_id'])
    
    Raises:
        ValueError: Si faltan columnas de unique_keys en el DataFrame
    """
    if df.empty:
        logger.warning(f"DataFrame vacío, no se guardó en {table_name}")
        return
    
    # Validar que existan las columnas de unique_keys
    missing_keys = set(unique_keys) - set(df.columns)
    if missing_keys:
        raise ValueError(f"Faltan columnas de unique_keys: {missing_keys}")
    
    # Asegurar que el directorio existe (solo SQLite)
    if not _is_postgresql() and db_path:
        dir_path = os.path.dirname(db_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
    
    try:
        with get_db_connection(db_path) as conn:
            # Crear tabla si no existe (usando pandas)
            temp_df = df.head(0)
            temp_df.to_sql(table_name, conn, if_exists='append', index=False)
            
            # Preparar columnas y placeholders
            columns = df.columns.tolist()
            placeholder = _get_placeholder()
            placeholders = ', '.join([placeholder for _ in columns])
            col_names = ', '.join(columns)
            
            if _is_postgresql():
                # PostgreSQL: ON CONFLICT DO UPDATE
                unique_cols = ', '.join(unique_keys)
                update_cols = ', '.join([
                    f"{col} = EXCLUDED.{col}" 
                    for col in columns if col not in unique_keys
                ])
                
                if update_cols:
                    upsert_sql = f"""
                        INSERT INTO {table_name} ({col_names})
                        VALUES ({placeholders})
                        ON CONFLICT ({unique_cols}) DO UPDATE SET {update_cols}
                    """
                else:
                    upsert_sql = f"""
                        INSERT INTO {table_name} ({col_names})
                        VALUES ({placeholders})
                        ON CONFLICT ({unique_cols}) DO NOTHING
                    """
            else:
                # SQLite: INSERT OR REPLACE
                # Create unique index first
                index_name = f"idx_unique_{'_'.join(unique_keys)}"
                unique_cols = ', '.join(unique_keys)
                
                try:
                    conn.execute(f"""
                        CREATE UNIQUE INDEX IF NOT EXISTS {index_name}
                        ON {table_name} ({unique_cols})
                    """)
                    logger.debug(f"Índice único creado/verificado: {index_name}")
                except Exception as e:
                    logger.debug(f"Índice único ya existe o error: {e}")
                
                upsert_sql = f"""
                    INSERT OR REPLACE INTO {table_name} ({col_names})
                    VALUES ({placeholders})
                """
            
            # Convertir timestamps a strings antes de insertar
            df_copy = df.copy()
            for col in df_copy.select_dtypes(include=['datetime64', 'datetime']).columns:
                df_copy[col] = df_copy[col].astype(str)
            
            # Insertar en batches
            cursor = conn.cursor()
            rows_inserted = 0
            
            for i in range(0, len(df_copy), batch_size):
                batch = df_copy.iloc[i:i + batch_size]
                values = [tuple(row) for row in batch.values]
                
                cursor.executemany(upsert_sql, values)
                rows_inserted += len(batch)
                
                if (i + batch_size) % (batch_size * 10) == 0:
                    logger.debug(f"Procesadas {rows_inserted}/{len(df_copy)} filas")
            
            logger.info(f"✅ Upsert completado: {rows_inserted} filas en {table_name}")
            
    except Exception as e:
        logger.error(f"Error en upsert a {table_name}: {e}", exc_info=True)
        raise


def _table_exists(cursor, table_name: str) -> bool:
    """Check if a table exists in the database."""
    if _is_postgresql():
        cursor.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_name = %s",
            (table_name,)
        )
    else:
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        )
    return cursor.fetchone() is not None


def remove_duplicates(
    table_name: str,
    db_path: str,
    unique_keys: List[str]
) -> int:
    """
    Elimina duplicados de una tabla existente.
    
    Args:
        table_name: Nombre de la tabla
        db_path: Ruta a la base de datos
        unique_keys: Columnas que definen duplicados
    
    Returns:
        Número de filas eliminadas
    
    Example:
        >>> removed = remove_duplicates('wc_orders', 'data/wc.db', ['order_id'])
        >>> print(f"Eliminadas {removed} filas duplicadas")
    """
    # For SQLite, check if file exists
    if not _is_postgresql() and not os.path.exists(db_path):
        logger.warning(f"Base de datos no existe: {db_path}")
        return 0
    
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            
            # Verificar si la tabla existe
            if not _table_exists(cursor, table_name):
                logger.warning(f"Tabla {table_name} no existe")
                return 0
            
            # Contar duplicados antes
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count_before = cursor.fetchone()[0]
            
            # Crear tabla temporal sin duplicados
            unique_cols = ', '.join(unique_keys)
            
            if _is_postgresql():
                # PostgreSQL: Use DISTINCT ON
                cursor.execute(f"""
                    CREATE TEMP TABLE {table_name}_temp AS
                    SELECT DISTINCT ON ({unique_cols}) * FROM {table_name}
                """)
            else:
                # SQLite: Use GROUP BY
                cursor.execute(f"""
                    CREATE TEMPORARY TABLE {table_name}_temp AS
                    SELECT * FROM {table_name}
                    GROUP BY {unique_cols}
                """)
            
            # Reemplazar tabla original
            cursor.execute(f"DELETE FROM {table_name}")
            cursor.execute(f"""
                INSERT INTO {table_name}
                SELECT * FROM {table_name}_temp
            """)
            cursor.execute(f"DROP TABLE {table_name}_temp")
            
            # Contar después
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count_after = cursor.fetchone()[0]
            
            removed = count_before - count_after
            
            if removed > 0:
                logger.info(f"🗑️ Eliminadas {removed} filas duplicadas de {table_name}")
            else:
                logger.info(f"✅ No se encontraron duplicados en {table_name}")
            
            return removed
            
    except Exception as e:
        logger.error(f"Error eliminando duplicados: {e}", exc_info=True)
        raise


def _get_table_columns(cursor, table_name: str) -> set:
    """Get existing column names from a table."""
    if _is_postgresql():
        cursor.execute(
            """
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = %s
            """,
            (table_name,)
        )
        return {row[0] for row in cursor.fetchall()}
    else:
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns_info = cursor.fetchall()
        if not columns_info:
            return set()
        return {info[1] for info in columns_info}


def ensure_schema_match(
    table_name: str,
    df: pd.DataFrame,
    db_path: str
) -> None:
    """
    Ensures that the database table has all columns present in the DataFrame.
    Automatically adds missing columns to the table schema.
    
    Args:
        table_name: Name of the table
        df: DataFrame containing the data to be inserted
        db_path: Path to the database
    """
    if df.empty:
        return

    # For SQLite, check if DB exists
    if not _is_postgresql() and not os.path.exists(db_path):
        return

    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            
            # Get existing columns from database
            existing_columns = _get_table_columns(cursor, table_name)
            
            # If table doesn't exist, return (it will be created by to_sql or similar)
            if not existing_columns:
                return
            
            df_columns = set(df.columns)
            
            # Find missing columns
            missing_columns = df_columns - existing_columns
            
            if missing_columns:
                logger.info(f"🔧 Schema drift detected in {table_name}. Adding columns: {missing_columns}")
                
                for col in missing_columns:
                    # Determine basic type
                    dtype = df[col].dtype
                    
                    if _is_postgresql():
                        sql_type = "TEXT"
                        if pd.api.types.is_integer_dtype(dtype):
                            sql_type = "BIGINT"
                        elif pd.api.types.is_float_dtype(dtype):
                            sql_type = "DOUBLE PRECISION"
                    else:
                        sql_type = "TEXT"
                        if pd.api.types.is_integer_dtype(dtype):
                            sql_type = "INTEGER"
                        elif pd.api.types.is_float_dtype(dtype):
                            sql_type = "REAL"
                    
                    alter_query = f"ALTER TABLE {table_name} ADD COLUMN {col} {sql_type}"
                    logger.info(f"Executing: {alter_query}")
                    cursor.execute(alter_query)
                
                logger.info(f"✅ Schema updated for {table_name}")
                
    except Exception as e:
        logger.error(f"Error checking/updating schema for {table_name}: {e}", exc_info=True)
        # Don't raise, try to proceed, maybe it works or will fail at insert


def get_last_extraction_date(
    table_name: str,
    date_column: str,
    db_path: str,
    default_date: str = '2023-01-01'
) -> str:
    """
    Obtiene la última fecha de extracción de una tabla.
    
    Args:
        table_name: Nombre de la tabla
        date_column: Nombre de la columna de fecha
        db_path: Ruta a la base de datos
        default_date: Fecha por defecto si la tabla está vacía
    
    Returns:
        Última fecha en formato YYYY-MM-DD
    
    Example:
        >>> last_date = get_last_extraction_date('wc_orders', 'date_only', 'data/woocommerce.db')
        >>> print(last_date)  # '2025-12-15'
    """
    # For SQLite, check if DB exists
    if not _is_postgresql() and not os.path.exists(db_path):
        logger.info(f"BD no existe, usando fecha por defecto: {default_date}")
        return default_date
    
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            
            # Verificar si la tabla existe
            if not _table_exists(cursor, table_name):
                logger.info(f"Tabla {table_name} no existe, usando fecha por defecto: {default_date}")
                return default_date
            
            # Obtener última fecha
            query = f"SELECT MAX({date_column}) FROM {table_name}"
            result = pd.read_sql(query, conn)
            last_date = result.iloc[0, 0]
            
            if pd.isna(last_date) or last_date is None:
                logger.info(f"Tabla {table_name} vacía, usando fecha por defecto: {default_date}")
                return default_date
            
            # Convertir a string en formato YYYY-MM-DD
            if isinstance(last_date, pd.Timestamp):
                last_date = last_date.strftime('%Y-%m-%d')
            else:
                # Si es string, intentar normalizar el formato
                last_date_str = str(last_date)
                # Si está en formato YYYYMMDD (sin guiones), convertir a YYYY-MM-DD
                if len(last_date_str) == 8 and last_date_str.isdigit():
                    last_date = f"{last_date_str[:4]}-{last_date_str[4:6]}-{last_date_str[6:8]}"
                else:
                    # Intentar parsear y reformatear
                    try:
                        parsed_date = pd.to_datetime(last_date_str)
                        last_date = parsed_date.strftime('%Y-%m-%d')
                    except ValueError:
                        last_date = last_date_str
            
            logger.info(f"Última extracción de {table_name}: {last_date}")
            return str(last_date)
            
    except Exception as e:
        logger.error(f"Error obteniendo última fecha: {e}", exc_info=True)
        logger.info(f"Usando fecha por defecto: {default_date}")
        return default_date


def create_indexes(db_path: str, indexes_sql: str) -> None:
    """
    Crea índices en la base de datos.
    
    Args:
        db_path: Ruta a la base de datos
        indexes_sql: Script SQL con los índices a crear
    """
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            # Ejecutar cada statement SQL
            for statement in indexes_sql.split(';'):
                statement = statement.strip()
                if statement:
                    cursor.execute(statement)
            logger.info("✅ Índices creados correctamente")
    except Exception as e:
        logger.error(f"Error creando índices: {e}", exc_info=True)
        raise


def execute_query(db_path: str, query: str, params: Optional[tuple] = None) -> pd.DataFrame:
    """
    Ejecuta una query y retorna el resultado como DataFrame.
    
    Args:
        db_path: Ruta a la base de datos
        query: Query SQL a ejecutar
        params: Parámetros para la query (opcional)
    
    Returns:
        DataFrame con los resultados
    """
    try:
        with get_db_connection(db_path) as conn:
            # Adapt query placeholders if needed
            if _is_postgresql() and '?' in query:
                query = query.replace('?', '%s')
            
            if params:
                df = pd.read_sql(query, conn, params=params)
            else:
                df = pd.read_sql(query, conn)
            logger.debug(f"Query ejecutada, {len(df)} filas retornadas")
            return df
    except Exception as e:
        logger.error(f"Error ejecutando query: {e}", exc_info=True)
        raise
