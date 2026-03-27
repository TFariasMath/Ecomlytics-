"""
Script de diagnóstico para ver TODOS los pedidos del 16 de diciembre
sin filtro de estado.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from etl.extract_woocommerce import get_wc_api, init_db_if_needed
from config.logging_config import setup_logger

logger = setup_logger(__name__)

def main():
    logger.info("="*70)
    logger.info("DIAGNÓSTICO: Pedidos del 16 de diciembre (TODOS LOS ESTADOS)")
    logger.info("="*70)
    
    # Get WooCommerce API client
    wcapi = get_wc_api()
    
    # Obtener TODOS los pedidos del 16 de diciembre SIN filtro de estado
    logger.info("\nObteniendo pedidos del 16 de diciembre...")
    
    page = 1
    all_orders = []
    
    while True:
        try:
            orders = wcapi.get("orders", params={
                "per_page": 100,
                "page": page,
                "after": "2025-12-16T00:00:00",
                "before": "2025-12-17T00:00:00"
                # SIN filtro de status
            }).json()
            
            if not orders or not isinstance(orders, list) or len(orders) == 0:
                break
            
            all_orders.extend(orders)
            page += 1
            
        except Exception as e:
            logger.error(f"Error: {e}")
            break
    
    logger.info(f"\n✅ Total pedidos encontrados: {len(all_orders)}")
    logger.info("\n" + "="*70)
    logger.info("DETALLE DE PEDIDOS:")
    logger.info("="*70)
    
    total_sum = 0
    
    for order in all_orders:
        order_id = order.get('id')
        date = order.get('date_created', 'N/A')
        status = order.get('status', 'N/A')
        total = float(order.get('total', 0))
        customer = f"{order.get('billing', {}).get('first_name', '')} {order.get('billing', {}).get('last_name', '')}"
        
        total_sum += total
        
        print(f"\n📦 Pedido #{order_id}")
        print(f"   Fecha: {date}")
        print(f"   Estado: {status}")
        print(f"   Total: ${total:,.0f}")
        print(f"   Cliente: {customer}")
    
    logger.info("\n" + "="*70)
    logger.info(f"TOTAL VENTAS 16 DIC: ${total_sum:,.0f}")
    logger.info("="*70)
    
    # Resumen por estado
    from collections import Counter
    status_count = Counter([o.get('status') for o in all_orders])
    
    logger.info("\nRESUMEN POR ESTADO:")
    for status, count in status_count.items():
        logger.info(f"  {status}: {count} pedidos")

if __name__ == "__main__":
    main()
