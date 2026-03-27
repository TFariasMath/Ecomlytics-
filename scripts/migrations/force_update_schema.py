
import os
import sys
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etl.extract_woocommerce import get_wc_api, extract_orders, extract_products, DATABASE_NAME
from utils.monitoring import track_etl_execution
from config.logging_config import setup_logger

logger = setup_logger(__name__)

def force_update():
    logger.info("🔧 Force updating schema and recent data...")
    
    # 1. Update Products (always runs fully)
    wcapi = get_wc_api()
    extract_products(wcapi)
    
    # 2. Update Orders (Last 7 days to cover recent schema changes)
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    logger.info(f"Re-extracting orders since {start_date}")
    
    extract_orders(wcapi, start_date=start_date)
    
    logger.info("✅ Force update complete")

if __name__ == "__main__":
    force_update()
