"""
Diagnóstico para identificar el slug exacto del estado "En espera".
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from etl.extract_woocommerce import get_wc_api
from config.logging_config import setup_logger

logger = setup_logger(__name__)

def main():
    logger.info("="*70)
    logger.info("🔍 Verificando pedidos del 18 de diciembre 2025")
    logger.info("="*70)
    
    wcapi = get_wc_api()
    
    try:
        # Obtener TODOS los pedidos del 18 dic sin filtro de status
        orders = wcapi.get("orders", params={
            "per_page": 100,
            "after": "2025-12-18T00:00:00",
            "before": "2025-12-19T00:00:00"
        }).json()
        
        logger.info(f"\n✅ Total pedidos encontrados: {len(orders)}")
        
        total_sum = 0
        
        print("\n" + "="*70)
        print("PEDIDOS DEL 18 DE DICIEMBRE 2025:")
        print("="*70)
        
        for order in orders:
            order_id = order.get('id')
            date = order.get('date_created', 'N/A')
            status = order.get('status', 'N/A')
            total = float(order.get('total', 0))
            
            total_sum += total
            
            print(f"\n📦 Pedido #{order_id}")
            print(f"   Fecha: {date}")
            print(f"   Estado: '{status}'")  # Comillas para ver el slug exacto
            print(f"   Total: ${total:,.0f}")
        
        print("\n" + "="*70)
        print(f"TOTAL VENTAS 18 DIC: ${total_sum:,.0f}")
        print("="*70)
        
        # Resumen por estado
        from collections import Counter
        status_count = Counter([o.get('status') for o in orders])
        
        print("\nRESUMEN POR ESTADO:")
        for status, count in status_count.items():
            print(f"  '{status}': {count} pedidos")
            
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)

if __name__ == "__main__":
    main()
