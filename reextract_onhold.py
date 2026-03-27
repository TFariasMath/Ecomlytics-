"""
Script para re-extraer órdenes on-hold desde el 18 de diciembre.
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from etl.extract_woocommerce import get_wc_api, extract_orders, extract_products, extract_customers

if __name__ == "__main__":
    print("🔄 Re-extrayendo pedidos desde 2025-12-18 (incluyendo on-hold)...")
    wcapi = get_wc_api()
    
    # Extract desde el 18 de diciembre
    extract_orders(wcapi, start_date="2025-12-18")
    
    print("✅ Extracción completada")
