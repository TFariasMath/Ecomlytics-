"""
Script para verificar qué estados de pedidos hay en la base de datos
y cuánto suman por estado.
"""

import sys
import os
import sqlite3
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config.logging_config import setup_logger

logger = setup_logger(__name__)

DATABASE = os.path.join(os.path.dirname(__file__), '..', 'data', 'woocommerce.db')

def main():
    logger.info("="*70)
    logger.info("🔍 Análisis de Estados de Pedidos en BD")
    logger.info("="*70)
    
    conn = sqlite3.connect(DATABASE)
    
    # Obtener todos los pedidos del año actual
    query = """
    SELECT 
        status,
        COUNT(*) as cantidad,
        SUM(total) as total_ventas
    FROM wc_orders
    WHERE strftime('%Y', date_created) = '2025'
    GROUP BY status
    ORDER BY total_ventas DESC
    """
    
    df = pd.read_sql(query, conn)
    
    print("\n" + "="*70)
    print("PEDIDOS 2025 POR ESTADO:")
    print("="*70)
    
    total_general = 0
    for idx, row in df.iterrows():
        print(f"\n{row['status']}:")
        print(f"   Cantidad: {row['cantidad']:,} pedidos")
        print(f"   Total: ${row['total_ventas']:,.0f}")
        total_general += row['total_ventas']
    
    print("\n" + "="*70)
    print(f"TOTAL GENERAL (TODOS LOS ESTADOS): ${total_general:,.0f}")
    print("="*70)
    
    # Calcular solo estados válidos
    valid_statuses = ['completed', 'completoenviado', 'processing', 'porsalir', 'on-hold']
    df_valid = df[df['status'].isin(valid_statuses)]
    total_valid = df_valid['total_ventas'].sum()
    
    print(f"\n{'='*70}")
    print(f"TOTAL ESTADOS VÁLIDOS: ${total_valid:,.0f}")
    print(f"Estados incluidos: {', '.join(valid_statuses)}")
    print("="*70)
    
    print(f"\n⚠️ DIFERENCIA: ${(total_general - total_valid):,.0f}")
    print(f"   ({((total_general - total_valid) / total_general * 100):.1f}% del total)")
    
    # Mostrar estados no válidos
    df_invalid = df[~df['status'].isin(valid_statuses)]
    if not df_invalid.empty:
        print(f"\n{'='*70}")
        print("ESTADOS NO VÁLIDOS (que se están incluyendo incorrectamente):")
        print("="*70)
        for idx, row in df_invalid.iterrows():
            print(f"  {row['status']}: {row['cantidad']} pedidos = ${row['total_ventas']:,.0f}")
    
    conn.close()

if __name__ == "__main__":
    main()
