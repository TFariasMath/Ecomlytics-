"""
Re-extracción rápida solo del 18 de diciembre para capturar el pedido faltante.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from etl.extract_woocommerce import get_wc_api, extract_orders, init_db_if_needed
from utils.monitoring import ETLMetrics
from config.logging_config import setup_logger

logger = setup_logger(__name__)

def main():
    logger.info("="*50)
    logger.info("Re-extracción del 18 de diciembre 2025")
    logger.info("="*50)
    
    init_db_if_needed()
    wcapi = get_wc_api()
    metrics = ETLMetrics('reextract_dic18')
    
    # Extract orders del 18 de diciembre
    extract_orders(wcapi, start_date='2025-12-18', metrics=metrics)
    
    metrics.mark_success()
    metrics.log_summary()
    
    logger.info("="*50)
    logger.info("✅ Re-extracción completada")
    logger.info("="*50)

if __name__ == "__main__":
    main()
