"""
Re-extracción completa de WooCommerce desde el 2023 para capturar todos los pedidos
con el filtro correcto que incluye el estado 'porsalir'.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from etl.extract_woocommerce import get_wc_api, extract_orders, init_db_if_needed
from utils.monitoring import track_etl_execution
from config.logging_config import setup_logger

logger = setup_logger(__name__)

DATABASE_NAME = os.path.join(os.path.dirname(__file__), '..', 'data', 'woocommerce.db')
MONITORING_DB = os.path.join(os.path.dirname(__file__), '..', 'data', 'monitoring.db')

def main():
    logger.info("="*70)
    logger.info("🔄 RE-EXTRACCIÓN COMPLETA DE WOOCOMMERCE")
    logger.info("   Desde: 2017-07-01 (TODO EL HISTÓRICO)")
    logger.info("   Filtro: completed, completoenviado, processing, porsalir")
    logger.info("="*70)
    
    with track_etl_execution('full_reextract_woocommerce', MONITORING_DB) as metrics:
        try:
            # Initialize DB
            init_db_if_needed()
            
            # Get WooCommerce API client
            wcapi = get_wc_api()
            
            # Extract orders desde 2017 (primera orden: 2017-07-05)
            logger.info("\n📦 Extrayendo TODAS las órdenes históricas desde 2017...")
            extract_orders(wcapi, start_date='2017-07-01', metrics=metrics)
            
            logger.info("\n" + "="*70)
            logger.info("✅ Re-extracción completa finalizada")
            logger.info("="*70)
            
        except Exception as e:
            logger.error(f"Error en re-extracción: {e}", exc_info=True)
            raise

if __name__ == "__main__":
    main()
