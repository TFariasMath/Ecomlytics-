"""
Sistema de Monitoreo para ETL.

Proporciona tracking de métricas, alertas y registro de ejecuciones.
"""

import os
import sqlite3
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional, List
from contextlib import contextmanager
import logging

# Import adapter for dual-database support
try:
    from utils.db_adapter import get_db_adapter
    ADAPTER_AVAILABLE = True
except ImportError:
    ADAPTER_AVAILABLE = False

logger = logging.getLogger(__name__)


def _is_postgresql() -> bool:
    """Check if using PostgreSQL."""
    if ADAPTER_AVAILABLE:
        return get_db_adapter().is_postgresql()
    return False


def _get_placeholder() -> str:
    """Get parameter placeholder for current database type."""
    return '%s' if _is_postgresql() else '?'


class ETLMetrics:
    """Almacena métricas de una ejecución ETL."""
    
    def __init__(self, etl_name: str, execution_id: Optional[str] = None):
        self.etl_name = etl_name
        self.execution_id = execution_id or datetime.now().strftime('%Y%m%d_%H%M%S')
        self.start_time = datetime.now()
        self.end_time = None
        self.status = 'RUNNING'
        self.rows_extracted = 0
        self.rows_loaded = 0
        self.errors = []
        self.warnings = []
        self.metadata = {}
    
    def add_rows(self, count: int):
        """Incrementa el contador de filas."""
        self.rows_extracted += count
        self.rows_loaded += count
    
    def add_error(self, error: str):
        """Registra un error."""
        self.errors.append(error)
    
    def add_warning(self, warning: str):
        """Registra una advertencia."""
        self.warnings.append(warning)
    
    def set_metadata(self, key: str, value: Any):
        """Agrega metadata."""
        self.metadata[key] = value
    
    def mark_success(self):
        """Marca la ejecución como exitosa."""
        self.end_time = datetime.now()
        self.status = 'SUCCESS'
    
    def mark_failed(self, error: str):
        """Marca la ejecución como fallida."""
        self.end_time = datetime.now()
        self.status = 'FAILED'
        self.add_error(error)
    
    def get_duration_seconds(self) -> float:
        """Retorna la duración en segundos."""
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte las métricas a diccionario."""
        return {
            'execution_id': self.execution_id,
            'etl_name': self.etl_name,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.get_duration_seconds(),
            'status': self.status,
            'rows_extracted': self.rows_extracted,
            'rows_loaded': self.rows_loaded,
            'error_count': len(self.errors),
            'warning_count': len(self.warnings),
            'errors': '|'.join(self.errors) if self.errors else None,
            'warnings': '|'.join(self.warnings) if self.warnings else None,
            'metadata': str(self.metadata)
        }
    
    def log_summary(self):
        """Loggea un resumen de la ejecución."""
        duration = self.get_duration_seconds()
        
        if self.status == 'SUCCESS':
            logger.info("="*60)
            logger.info(f"✅ ETL {self.etl_name} - EXITOSO")
            logger.info(f"   Execution ID: {self.execution_id}")
            logger.info(f"   Duración: {duration:.2f}s")
            logger.info(f"   Filas procesadas: {self.rows_loaded:,}")
            if self.warnings:
                logger.info(f"   Advertencias: {len(self.warnings)}")
            logger.info("="*60)
        else:
            logger.error("="*60)
            logger.error(f"❌ ETL {self.etl_name} - FALLIDO")
            logger.error(f"   Execution ID: {self.execution_id}")
            logger.error(f"   Duración: {duration:.2f}s")
            logger.error(f"   Errores: {len(self.errors)}")
            for error in self.errors:
                logger.error(f"     - {error}")
            logger.error("="*60)


class ETLMonitor:
    """Monitor de ejecuciones ETL con persistencia en SQLite o PostgreSQL."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Inicializa la base de datos de monitoreo."""
        # Only create directory for SQLite
        if not _is_postgresql():
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS etl_executions (
                    execution_id TEXT PRIMARY KEY,
                    etl_name TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    duration_seconds REAL,
                    status TEXT NOT NULL,
                    rows_extracted INTEGER,
                    rows_loaded INTEGER,
                    error_count INTEGER,
                    warning_count INTEGER,
                    errors TEXT,
                    warnings TEXT,
                    metadata TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Índices para consultas rápidas
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_etl_name 
                ON etl_executions(etl_name)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_start_time 
                ON etl_executions(start_time DESC)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_status 
                ON etl_executions(status)
            """)
    
    @contextmanager
    def _get_connection(self):
        """Context manager para conexión a DB de monitoreo."""
        conn = None
        try:
            if _is_postgresql() and ADAPTER_AVAILABLE:
                import psycopg2
                adapter = get_db_adapter()
                conn = psycopg2.connect(adapter.database_url)
            else:
                conn = sqlite3.connect(self.db_path)
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    def save_execution(self, metrics: ETLMetrics):
        """Guarda las métricas de una ejecución."""
        try:
            data = metrics.to_dict()
            placeholder = _get_placeholder()
            
            with self._get_connection() as conn:
                columns = ', '.join(data.keys())
                
                if _is_postgresql():
                    # PostgreSQL: ON CONFLICT DO UPDATE
                    placeholders = ', '.join([placeholder for _ in data])
                    update_cols = ', '.join([
                        f"{col} = EXCLUDED.{col}" 
                        for col in data.keys() if col != 'execution_id'
                    ])
                    sql = f"""
                        INSERT INTO etl_executions ({columns}) 
                        VALUES ({placeholders})
                        ON CONFLICT (execution_id) DO UPDATE SET {update_cols}
                    """
                else:
                    # SQLite: INSERT OR REPLACE
                    placeholders = ', '.join([placeholder for _ in data])
                    sql = f"INSERT OR REPLACE INTO etl_executions ({columns}) VALUES ({placeholders})"
                
                conn.execute(sql, tuple(data.values()))
            
            logger.debug(f"Métricas guardadas: {metrics.execution_id}")
            
        except Exception as e:
            logger.error(f"Error guardando métricas: {e}")
    
    def get_last_execution(self, etl_name: str) -> Optional[Dict[str, Any]]:
        """Obtiene la última ejecución de un ETL."""
        try:
            placeholder = _get_placeholder()
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"""
                    SELECT * FROM etl_executions
                    WHERE etl_name = {placeholder}
                    ORDER BY start_time DESC
                    LIMIT 1
                """, (etl_name,))
                
                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    return dict(zip(columns, row))
                
        except Exception as e:
            logger.error(f"Error obteniendo última ejecución: {e}")
        
        return None
    
    def get_execution_history(
        self,
        etl_name: Optional[str] = None,
        limit: int = 10
    ) -> pd.DataFrame:
        """Obtiene el historial de ejecuciones."""
        try:
            placeholder = _get_placeholder()
            query = "SELECT * FROM etl_executions"
            params = []
            
            if etl_name:
                query += f" WHERE etl_name = {placeholder}"
                params.append(etl_name)
            
            query += f" ORDER BY start_time DESC LIMIT {placeholder}"
            params.append(limit)
            
            with self._get_connection() as conn:
                df = pd.read_sql(query, conn, params=params)
                return df
                
        except Exception as e:
            logger.error(f"Error obteniendo historial: {e}")
            return pd.DataFrame()
    
    def get_stats(self, etl_name: Optional[str] = None, days: int = 7) -> Dict[str, Any]:
        """Obtiene estadísticas de ejecuciones."""
        try:
            placeholder = _get_placeholder()
            
            if _is_postgresql():
                date_filter = f"start_time::timestamp >= NOW() - INTERVAL '{days} days'"
            else:
                date_filter = f"datetime(start_time) >= datetime('now', '-{days} days')"
            
            query = f"""
                SELECT 
                    COUNT(*) as total_executions,
                    SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) as successful,
                    SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) as failed,
                    AVG(duration_seconds) as avg_duration,
                    MAX(duration_seconds) as max_duration,
                    SUM(rows_loaded) as total_rows_loaded
                FROM etl_executions
                WHERE {date_filter}
            """
            
            params = []
            
            if etl_name:
                query += f" AND etl_name = {placeholder}"
                params.append(etl_name)
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params) if params else cursor.execute(query)
                row = cursor.fetchone()
                
                columns = [desc[0] for desc in cursor.description]
                stats = dict(zip(columns, row))
                
                # Calcular success rate
                total = stats['total_executions'] or 0
                successful = stats['successful'] or 0
                stats['success_rate'] = (successful / total * 100) if total > 0 else 0
                
                return stats
                
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {}
    
    def check_health(self, etl_name: str, max_failures: int = 3) -> Dict[str, Any]:
        """Verifica la salud de un ETL."""
        try:
            placeholder = _get_placeholder()
            # Obtener últimas ejecuciones
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"""
                    SELECT status FROM etl_executions
                    WHERE etl_name = {placeholder}
                    ORDER BY start_time DESC
                    LIMIT {placeholder}
                """, (etl_name, max_failures))
                
                recent_statuses = [row[0] for row in cursor.fetchall()]
            
            if not recent_statuses:
                return {
                    'status': 'UNKNOWN',
                    'message': 'No hay ejecuciones registradas',
                    'is_healthy': True
                }
            
            # Verificar fallos consecutivos
            consecutive_failures = 0
            for status in recent_statuses:
                if status == 'FAILED':
                    consecutive_failures += 1
                else:
                    break
            
            is_healthy = consecutive_failures < max_failures
            
            if is_healthy:
                return {
                    'status': 'HEALTHY',
                    'message': f'Última ejecución: {recent_statuses[0]}',
                    'is_healthy': True,
                    'consecutive_failures': consecutive_failures
                }
            else:
                return {
                    'status': 'UNHEALTHY',
                    'message': f'{consecutive_failures} fallos consecutivos',
                    'is_healthy': False,
                    'consecutive_failures': consecutive_failures
                }
                
        except Exception as e:
            logger.error(f"Error verificando salud: {e}")
            return {
                'status': 'ERROR',
                'message': str(e),
                'is_healthy': False
            }


@contextmanager
def track_etl_execution(etl_name: str, db_path: str):
    """
    Context manager para trackear una ejecución ETL.
    
    Example:
        >>> with track_etl_execution('extract_analytics', 'data/monitoring.db') as metrics:
        ...     # Tu código ETL aquí
        ...     metrics.add_rows(1000)
        ...     metrics.set_metadata('source', 'GA4')
    """
    monitor = ETLMonitor(db_path)
    metrics = ETLMetrics(etl_name)
    
    try:
        yield metrics
        metrics.mark_success()
    except Exception as e:
        metrics.mark_failed(str(e))
        raise
    finally:
        metrics.log_summary()
        monitor.save_execution(metrics)
