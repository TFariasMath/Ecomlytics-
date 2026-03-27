"""
Scheduler automático para ETL.

Ejecuta automáticamente los procesos ETL en horarios programados:
- 2:00 AM: Extracción de Google Analytics
- 3:00 AM: Extracción de WooCommerce
"""

import sys
import os
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

# Agregar paths para imports
sys.path.append(os.path.dirname(__file__))
from config.logging_config import setup_logger

logger = setup_logger(__name__)

# Importar las funciones main de los ETL
from etl import extract_analytics, extract_woocommerce


def run_analytics_etl():
    """Ejecuta el ETL de Google Analytics."""
    logger.info("="*60)
    logger.info("⏰ SCHEDULER: Iniciando ETL de Google Analytics programado")
    logger.info(f"   Timestamp: {datetime.now()}")
    logger.info("="*60)
    
    try:
        extract_analytics.main()
        logger.info("✅ SCHEDULER: ETL de Analytics completado exitosamente")
    except Exception as e:
        logger.error(f"❌ SCHEDULER: ETL de Analytics falló: {e}", exc_info=True)


def run_woocommerce_etl():
    """Ejecuta el ETL de WooCommerce."""
    logger.info("="*60)
    logger.info("⏰ SCHEDULER: Iniciando ETL de WooCommerce programado")
    logger.info(f"   Timestamp: {datetime.now()}")
    logger.info("="*60)
    
    try:
        extract_woocommerce.main()
        logger.info("✅ SCHEDULER: ETL de WooCommerce completado exitosamente")
    except Exception as e:
        logger.error(f"❌ SCHEDULER: ETL de WooCommerce falló: {e}", exc_info=True)


def main():
    """Configura y ejecuta el scheduler."""
    logger.info("🚀 Iniciando Scheduler de ETL")
    logger.info("-" * 60)
    logger.info("Horarios programados:")
    logger.info("  - Google Analytics: 2:00 AM (diario)")
    logger.info("  - WooCommerce:      3:00 AM (diario)")
    logger.info("-" * 60)
    
    scheduler = BlockingScheduler()
    
    # Programar Google Analytics - 2:00 AM diario
    scheduler.add_job(
        func=run_analytics_etl,
        trigger=CronTrigger(hour=2, minute=0),
        id='analytics_daily',
        name='Google Analytics ETL (Daily)',
        replace_existing=True
    )
    
    # Programar WooCommerce - 3:00 AM diario
    scheduler.add_job(
        func=run_woocommerce_etl,
        trigger=CronTrigger(hour=3, minute=0),
        id='woocommerce_daily',
        name='WooCommerce ETL (Daily)',
        replace_existing=True
    )
    
    logger.info("✅ Jobs programados correctamente")
    logger.info("   Presiona Ctrl+C para detener el scheduler")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("🛑 Scheduler detenido por el usuario")
    except Exception as e:
        logger.error(f"❌ Error en scheduler: {e}", exc_info=True)


if __name__ == "__main__":
    main()
