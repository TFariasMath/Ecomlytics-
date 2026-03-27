"""
Script de diagnóstico para verificar datos en la BD después de la extracción.
"""

import sys
import os
import sqlite3
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

DATABASE = os.path.join(os.path.dirname(__file__), '..', 'data', 'woocommerce.db')

def main():
    print("="*70)
    print("🔍 DIAGNÓSTICO DE DATOS EN BD")
    print("="*70)
    
    conn = sqlite3.connect(DATABASE)
    
    # Verificar si la tabla existe
    tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
    print(f"\nTablas en BD: {tables['name'].tolist()}")
    
    if 'wc_orders' not in tables['name'].values:
        print("\n❌ Tabla wc_orders NO EXISTE")
        print("La extracción aún no ha completado.")
        conn.close()
        return
    
    # Estados válidos según el filtro del ETL
    VALID_STATUSES = ['completed', 'completoenviado', 'processing', 'porsalir', 'on-hold']
    
    # 1. Total de pedidos por año
    query_year = """
    SELECT 
        strftime('%Y', date_created) as year,
        COUNT(*) as total_pedidos,
        SUM(total) as total_ventas
    FROM wc_orders
    GROUP BY year
    ORDER BY year
    """
    df_year = pd.read_sql(query_year, conn)
    
    print("\n" + "="*70)
    print("TOTALES POR AÑO (TODOS LOS ESTADOS):")
    print("="*70)
    for _, row in df_year.iterrows():
        print(f"{row['year']}: {row['total_pedidos']} pedidos = ${row['total_ventas']:,.0f}")
    
    # 2. Total 2025 con filtro de estados válidos
    query_2025_valid = f"""
    SELECT 
        COUNT(*) as total_pedidos,
        SUM(total) as total_ventas
    FROM wc_orders
    WHERE strftime('%Y', date_created) = '2025'
    AND status IN ({','.join(['?' for _ in VALID_STATUSES])})
    """
    df_2025_valid = pd.read_sql(query_2025_valid, conn, params=VALID_STATUSES)
    
    print("\n" + "="*70)
    print(f"2025 CON ESTADOS VÁLIDOS: ${df_2025_valid['total_ventas'].iloc[0]:,.0f}")
    print(f"Estados: {', '.join(VALID_STATUSES)}")
    print("="*70)
    
    # 3. Desglose por estado en 2025
    query_status = """
    SELECT 
        status,
        COUNT(*) as cantidad,
        SUM(total) as total
    FROM wc_orders
    WHERE strftime('%Y', date_created) = '2025'
    GROUP BY status
    ORDER BY total DESC
    """
    df_status = pd.read_sql(query_status, conn)
    
    print("\n" + "="*70)
    print("DESGLOSE POR ESTADO EN 2025:")
    print("="*70)
    for _, row in df_status.iterrows():
        is_valid = "✅" if row['status'] in VALID_STATUSES else "❌"
        print(f"{is_valid} {row['status']}: {row['cantidad']} pedidos = ${row['total']:,.0f}")
    
    conn.close()
    
    print("\n" + "="*70)
    print("✅ Diagnóstico completado")
    print("="*70)

if __name__ == "__main__":
    main()
