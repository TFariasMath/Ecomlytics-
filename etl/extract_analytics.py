"""
Extractor de datos de Google Analytics 4.

Este módulo extrae datos de GA4 y los almacena en SQLite con:
- Logging estructurado
- Carga incremental
- Retry logic automático
- Type hints
"""

import os
import sys
import pandas as pd
from typing import Dict, List, Optional
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest
from google.oauth2 import service_account

# Agregar paths para imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config.logging_config import setup_logger, log_execution_time
from config.settings import GoogleAnalyticsConfig, DatabaseConfig
from utils.database import save_dataframe_to_db, get_last_extraction_date, upsert_dataframe
from utils.api_client import get_usd_clp_rate
from utils.retry_handler import retry_on_api_error
from utils.data_quality import GA4DataValidator, validate_and_log
from utils.monitoring import track_etl_execution

# Setup logger
logger = setup_logger(__name__)

# Database configuration
DATABASE_NAME = DatabaseConfig.get_analytics_db_path()
MONITORING_DB = DatabaseConfig.get_monitoring_db_path()

# Mapping Dictionary for Renaming (English API -> Spanish DB)
COLUMN_MAPPING = {
    'sessions': 'Sesiones',
    'activeUsers': 'UsuariosActivos',
    'screenPageViews': 'Vistas',
    'sessionDefaultChannelGroup': 'Canal',
    'country': 'Pais',
    'pageTitle': 'Pagina',
    'audienceName': 'Audiencia',
    'date': 'Fecha',
    'totalRevenue': 'Ganancias',
    'totalPurchasers': 'Compradores',
    'itemsAddedToCart': 'AgregadosAlCarrito',
    'itemName': 'Producto',
    'itemsPurchased': 'CantidadVendida',
    'sessionSource': 'Fuente',
    'sessionMedium': 'Medio'
}


REPORTS = [
    {
        'name': 'Channels',
        'table_name': 'ga4_channels',
        'dimensions': ['date', 'sessionDefaultChannelGroup'],
        'metrics': ['sessions']
    },
    {
        'name': 'Countries',
        'table_name': 'ga4_countries',
        'dimensions': ['date', 'country'],
        'metrics': ['activeUsers']
    },
    {
        'name': 'Pages',
        'table_name': 'ga4_pages',
        'dimensions': ['date', 'pageTitle'],
        'metrics': ['screenPageViews']
    },
    {
        'name': 'Audiences',
        'table_name': 'ga4_audiences',
        'dimensions': ['date', 'audienceName'],
        'metrics': ['activeUsers']
    },
    {
        'name': 'Ecommerce_Daily',
        'table_name': 'ga4_ecommerce',
        'dimensions': ['date'],
        'metrics': ['activeUsers', 'totalPurchasers', 'totalRevenue', 'itemsAddedToCart']
    },
    {
        'name': 'Products',
        'table_name': 'ga4_products',
        'dimensions': ['date', 'itemName'],
        'metrics': ['itemsPurchased']
    },
    {
        'name': 'Traffic_Sources',
        'table_name': 'ga4_traffic_sources',
        'dimensions': ['date', 'sessionSource', 'sessionMedium'],
        'metrics': ['sessions']
    }
]


def get_credentials() -> Optional[service_account.Credentials]:
    """
    Loads Google Service Account credentials from configured path.
    
    Returns:
        Credentials object or None if error
    """
    try:
        key_file_path = GoogleAnalyticsConfig.get_key_file_path()
        
        logger.info(f"Loading credentials from {key_file_path}")
        creds = service_account.Credentials.from_service_account_file(key_file_path)
        logger.info("✅ Credentials loaded successfully")
        return creds
        
    except Exception as e:
        logger.error(f"Error loading credentials: {e}", exc_info=True)
        return None


@retry_on_api_error(max_attempts=3, min_wait=4, max_wait=60)
def extract_report(
    property_id: str,
    creds: service_account.Credentials,
    report_config: Dict,
    usd_to_clp: Optional[float] = None,
    start_date: str = "2023-01-01"
) -> pd.DataFrame:
    """
    Extracts data for a specific report configuration.
    
    Args:
        property_id: GA4 Property ID
        creds: Google credentials
        report_config: Report configuration dict
        usd_to_clp: USD to CLP exchange rate
        start_date: Start date for extraction (format: YYYY-MM-DD)
    
    Returns:
        DataFrame with report data
    """
    report_name = report_config['name']
    logger.info(f"📊 Extracting report: {report_name} (desde {start_date})")
    
    try:
        client = BetaAnalyticsDataClient(credentials=creds)
        
        if not property_id.startswith('properties/'):
            property_id = f'properties/{property_id}'

        dimensions = [Dimension(name=d) for d in report_config['dimensions']]
        metrics = [Metric(name=m) for m in report_config['metrics']]

        request = RunReportRequest(
            property=property_id,
            dimensions=dimensions,
            metrics=metrics,
            date_ranges=[DateRange(start_date=start_date, end_date="today")],
        )

        response = client.run_report(request)
        
        data = []
        for row in response.rows:
            item = {}
            # Map dimensions
            for i, dim in enumerate(report_config['dimensions']):
                col_name = COLUMN_MAPPING.get(dim, dim)
                item[col_name] = row.dimension_values[i].value
            
            # Map metrics
            for i, met in enumerate(report_config['metrics']):
                col_name = COLUMN_MAPPING.get(met, met)
                val = row.metric_values[i].value
                
                try:
                    if '.' in val:
                        val_float = float(val)
                        # Currency conversion logic
                        if col_name == 'Ganancias' and usd_to_clp:
                            val_float = val_float * usd_to_clp
                        item[col_name] = val_float
                    else:
                        item[col_name] = int(val)
                except ValueError:
                    item[col_name] = val
            
            data.append(item)

        if not data:
            logger.warning(f"No data found for report '{report_name}'")
            return pd.DataFrame()
        
        df = pd.DataFrame(data)
        logger.info(f"✅ Extracted {len(df)} rows for {report_name}")
        return df
        
    except Exception as e:
        logger.error(f"Error fetching report '{report_name}': {e}", exc_info=True)
        return pd.DataFrame()


@log_execution_time(logger)
def main() -> None:
    """Main execution function with monitoring and data quality."""
    
    with track_etl_execution('extract_analytics', MONITORING_DB) as metrics:
        try:
            logger.info("="*50)
            logger.info("🚀 Iniciando extracción de Google Analytics")
            logger.info("="*50)
            
            # Validate configuration first
            if not GoogleAnalyticsConfig.is_configured():
                error_msg = "Google Analytics no está configurado. Por favor configura las credenciales en .env o via interfaz web."
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # Get credentials
            creds = get_credentials()
            if not creds:
                error_msg = "No se pudieron cargar las credenciales"
                logger.error(f"❌ {error_msg}. Abortando.")
                metrics.add_error(error_msg)
                return

            # Fetch exchange rate
            current_exchange_rate = get_usd_clp_rate()
            metrics.set_metadata('exchange_rate', current_exchange_rate)
            
            # Always fetch all historical data (upsert prevents duplicates)
            # Using 2015-01-01 to get all possible data (GA4 launched 2020, but this ensures we get everything)
            start_date = '2015-01-01'
            
            logger.info(f"📅 Extrayendo datos desde: {start_date} (carga completa)")
            metrics.set_metadata('start_date', start_date)
            
            total_rows = 0
            successful_reports = 0
            
            # Extract all reports
            for report in REPORTS:
                try:
                    df = extract_report(
                        GoogleAnalyticsConfig.get_property_id(),
                        creds,
                        report,
                        usd_to_clp=current_exchange_rate,
                        start_date=start_date
                    )
                    
                    if not df.empty:
                        # Validar calidad de datos
                        is_valid = validate_and_log(
                            df,
                            lambda d: GA4DataValidator.validate_report(d, report['name']),
                            report['name']
                        )
                        
                        if not is_valid:
                            metrics.add_warning(f"Validación fallida para {report['name']}")
                            logger.warning(f"⚠️ Guardando datos a pesar de validación fallida")
                        
                        # Usar upsert para prevenir duplicados
                        # Clave única: Fecha + dimensiones del reporte
                        unique_keys = ['Fecha']
                        for dim in report['dimensions']:
                            mapped_dim = COLUMN_MAPPING.get(dim, dim)
                            if mapped_dim != 'Fecha' and mapped_dim in df.columns:
                                unique_keys.append(mapped_dim)
                        
                        upsert_dataframe(
                            df=df,
                            table_name=report['table_name'],
                            db_path=DATABASE_NAME,
                            unique_keys=unique_keys
                        )
                        
                        total_rows += len(df)
                        successful_reports += 1
                    else:
                        logger.warning(f"Skipping save for empty report: {report['name']}")
                        metrics.add_warning(f"Reporte vacío: {report['name']}")
                        
                except Exception as e:
                    error_msg = f"Error procesando report {report['name']}: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    metrics.add_error(error_msg)
                
                logger.info("-" * 30)
            
            # Registrar métricas finales
            metrics.add_rows(total_rows)
            metrics.set_metadata('successful_reports', successful_reports)
            metrics.set_metadata('total_reports', len(REPORTS))
            
            logger.info("="*50)
            logger.info(f"✅ Extracción completada")
            logger.info(f"   Reportes exitosos: {successful_reports}/{len(REPORTS)}")
            logger.info(f"   Total filas extraídas: {total_rows}")
            logger.info("="*50)
            
        except Exception as e:
            logger.error(f"Error crítico en ETL: {e}", exc_info=True)
            raise


if __name__ == "__main__":
    main()
