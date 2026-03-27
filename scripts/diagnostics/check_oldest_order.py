"""
Script para verificar la fecha más antigua disponible en WooCommerce.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from etl.extract_woocommerce import get_wc_api
from config.logging_config import setup_logger

logger = setup_logger(__name__)

def main():
    logger.info("="*70)
    logger.info("🔍 Verificando datos históricos más antiguos en WooCommerce")
    logger.info("="*70)
    
    wcapi = get_wc_api()
    
    # Obtener la orden más antigua
    logger.info("\n📅 Buscando la orden más antigua...")
    
    try:
        # Ordenar por fecha ascendente para obtener la más vieja
        oldest_orders = wcapi.get("orders", params={
            "per_page": 5,
            "orderby": "date",
            "order": "asc",
            "status": "completed,completoenviado,processing,porsalir"
        }).json()
        
        if oldest_orders and isinstance(oldest_orders, list) and len(oldest_orders) > 0:
            oldest = oldest_orders[0]
            order_id = oldest.get('id')
            date_created = oldest.get('date_created')
            status = oldest.get('status')
            total = float(oldest.get('total', 0))
            
            print(f"\n📦 Orden más antigua encontrada:")
            print(f"   ID: #{order_id}")
            print(f"   Fecha: {date_created}")
            print(f"   Estado: {status}")
            print(f"   Total: ${total:,.0f}")
            
            # Extraer solo la fecha
            fecha_str = date_created.split('T')[0] if 'T' in date_created else date_created
            
            logger.info(f"\n✅ Primera orden: {fecha_str}")
            
            # Verificar si hay datos antes de 2023-01-01
            if fecha_str < "2023-01-01":
                logger.warning(f"\n⚠️ HAY DATOS MÁS ANTIGUOS!")
                logger.warning(f"   La re-extracción desde 2023-01-01 NO capturó todo el histórico")
                logger.warning(f"   Se recomienda re-extraer desde: {fecha_str}")
                
                # Contar cuántas órdenes hay antes de 2023
                logger.info(f"\n📊 Contando órdenes antes de 2023-01-01...")
                pre_2023_orders = wcapi.get("orders", params={
                    "per_page": 1,
                    "before": "2023-01-01T00:00:00",
                    "status": "completed,completoenviado,processing,porsalir"
                }).json()
                
                # La API incluye el header X-WP-Total con el total
                logger.info(f"   (Nota: para saber el total exacto, se necesitaría paginar)")
                
            else:
                logger.info(f"\n✅ NO hay datos más antiguos que 2023-01-01")
                logger.info(f"   La re-extracción capturó TODO el histórico disponible")
            
            print(f"\n{'='*70}")
            print("Resumen de las 5 órdenes más antiguas:")
            print('='*70)
            
            for i, order in enumerate(oldest_orders[:5], 1):
                date = order.get('date_created', '').split('T')[0]
                total = float(order.get('total', 0))
                print(f"{i}. ID #{order.get('id')} - {date} - ${total:,.0f}")
        
        else:
            logger.warning("No se encontraron órdenes")
            
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)

if __name__ == "__main__":
    main()
