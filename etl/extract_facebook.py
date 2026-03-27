"""
Extractor de datos de Facebook Page Insights.

Este módulo extrae métricas de Facebook y las almacena en SQLite con:
- Logging estructurado
- Carga incremental
- Retry logic automático
- Type hints
"""

import os
import sys
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Agregar paths para imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config.logging_config import setup_logger, log_execution_time
from config.settings import FacebookConfig, DatabaseConfig
from utils.database import save_dataframe_to_db, get_last_extraction_date, upsert_dataframe
from utils.data_quality import FacebookDataValidator, validate_and_log
from utils.monitoring import track_etl_execution

# Setup logger
logger = setup_logger(__name__)

# Database configuration
DATABASE_NAME = DatabaseConfig.get_facebook_db_path()
MONITORING_DB = DatabaseConfig.get_monitoring_db_path()

# Metrics configuration
# Insights API is returning #100 errors for standard metrics (v19.0 permission/scope issue?)
# We fallback to Basic Page Fields for Growth Tracking.
METRICS_CONFIG = [
    'fan_count',
    'followers_count'
]

def get_page_access_token(user_token: str, page_id: str, api_version: str = "v19.0") -> Optional[str]:
    """
    Attempts to retrieve a Page Access Token using a User Access Token.
    Returns the user_token if it's already a page token (checked via debug_token) 
    or if we can't fetch accounts.
    """
    base_url = f"https://graph.facebook.com/{api_version}"
    url = f"{base_url}/me/accounts"
    params = {'access_token': user_token}
    
    try:
        logger.info("Intentando resolver Page Access Token...")
        resp = requests.get(url, params=params)
        
        if not resp.ok:
            # Maybe it's already a page token or scope is limited.
            logger.warning(f"No se pudo listar cuentas ({resp.status_code}). Intentando usar token original.")
            return user_token
            
        data = resp.json().get('data', [])
        for page in data:
            if page.get('id') == page_id:
                logger.info(f"✅ Page Token encontrado para {page.get('name')}")
                return page.get('access_token')
                
        logger.warning(f"Pagina {page_id} no encontrada en las cuentas del usuario. Usando token original.")
        return user_token
        
    except Exception as e:
        logger.error(f"Error resolviendo page token: {e}")
        return user_token

def fetch_basic_stats(page_id: str, access_token: str, api_version: str = "v19.0") -> List[Dict[str, Any]]:
    """Fetches basic page fields as a snapshot."""
    url = f"https://graph.facebook.com/{api_version}/{page_id}"
    params = {
        'access_token': access_token,
        'fields': 'fan_count,followers_count'
    }
    
    try:
        resp = requests.get(url, params=params)
        if resp.ok:
            data = resp.json()
            # Convert to 'metric' format
            rows = []
            today = datetime.now().strftime('%Y-%m-%d')
            
            if 'fan_count' in data:
                rows.append({
                    'name': 'page_fans', # Standardize name
                    'period': 'lifetime',
                    'values': [{'value': data['fan_count'], 'end_time': today}]
                })
            if 'followers_count' in data:
                rows.append({
                    'name': 'page_followers',
                    'period': 'lifetime',
                    'values': [{'value': data['followers_count'], 'end_time': today}]
                })
            return rows
        else:
            logger.error(f"Error fetching basic stats: {resp.text}")
            return []
    except Exception as e:
        logger.error(f"Exc fetching basic stats: {e}")
        return []

def get_facebook_insights(
    page_id: str,
    access_token: str,
    since: str,
    until: str,
    api_version: str = "v19.0",
    period: str = 'day'
) -> List[Dict[str, Any]]:
    """
    (DISABLED/LEGACY) Fetches Facebook Insights.
    Kept for future use if API issues resolve.
    """
    return []

def get_date_chunks(start_date: str, end_date: str, chunk_size_days: int = 90) -> List[tuple]:
    """Splits a date range into smaller chunks."""
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    
    chunks = []
    current = start
    
    while current < end:
        chunk_end = current + timedelta(days=chunk_size_days)
        if chunk_end > end:
            chunk_end = end
            
        chunks.append((
            current.strftime('%Y-%m-%d'),
            chunk_end.strftime('%Y-%m-%d')
        ))
        current = chunk_end + timedelta(days=1) # Start next day
        
    return chunks

def process_insights_data(raw_data: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Processes raw API response into a structured DataFrame.
    """
    processed_rows = []
    
    for metric_entry in raw_data:
        metric_name = metric_entry.get('name')
        period = metric_entry.get('period')
        values = metric_entry.get('values', [])
        
        for val in values:
            end_time = val.get('end_time')
            value = val.get('value', 0)
            
            try:
                if 'T' in str(end_time):
                    date_obj = pd.to_datetime(end_time)
                    date_str = date_obj.strftime('%Y-%m-%d')
                else:
                    date_str = str(end_time)
            except Exception:
                date_str = str(end_time)
            
            processed_rows.append({
                'date': date_str,
                'metric': metric_name,
                'value': value,
                'period': period
            })
            
    df = pd.DataFrame(processed_rows)
    return df

def pivot_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pivots the metrics DataFrame to have dates as rows and metrics as columns.
    """
    if df.empty:
        return df
        
    df_pivot = df.pivot_table(
        index='date',
        columns='metric',
        values='value',
        aggfunc='first'
    ).reset_index()
    
    return df_pivot

@log_execution_time(logger)
def main():
    """Main ETL execution."""
    
    with track_etl_execution('extract_facebook', MONITORING_DB) as metrics:
        try:
            logger.info("="*50)
            logger.info("🚀 Iniciando extracción de Facebook Data (Snapshot Mode)")
            logger.info("="*50)
            
            # Validate configuration first
            if not FacebookConfig.is_configured():
                error_msg = "Facebook no está configurado. Por favor configura las credenciales en .env o via interfaz web."
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # Get configuration
            access_token = FacebookConfig.get_access_token()
            page_id = FacebookConfig.get_page_id()
            api_version = FacebookConfig.get_api_version()
            
            # Resolve Token
            final_token = get_page_access_token(access_token, page_id)
            
            # === SNAPSHOT MODE ===
            # Since Insights are failing, we extract current status
            logger.info("📸 Obteniendo snapshot de fans/followers...")
            basic_data = fetch_basic_stats(page_id, final_token, api_version)
            
            if basic_data:
                # Process
                df = process_insights_data(basic_data)
                
                # Convert to wide format
                df_wide = pivot_metrics(df)
                
                # Upsert
                upsert_dataframe(
                    df=df_wide,
                    table_name='fb_page_insights',
                    db_path=DATABASE_NAME,
                    unique_keys=['date']
                )
                
                metrics.add_rows(len(df_wide))
                logger.info(f"✅ Datos básicos guardados para hoy: {len(df_wide)} registros (Fans/Followers)")
            else:
                logger.warning("⚠️ No se pudieron obtener datos básicos")
                
            metrics.set_metadata('metrics_count', 2)
            
            logger.info("="*50)
            logger.info("✅ Extracción de Facebook completada")
            logger.info("="*50)
            
        except Exception as e:
            logger.error(f"Error crítico en ETL Facebook: {e}", exc_info=True)
            raise

if __name__ == "__main__":
    main()
