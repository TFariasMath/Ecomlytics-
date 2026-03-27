import sqlite3
import pandas as pd

conn = sqlite3.connect('data/woocommerce.db')

print("="*70)
print("31 ENERO 2025 - ANÁLISIS COMPLETO:")
print("="*70)

# Ver TODOS los pedidos del 31 de enero
query = """
SELECT 
    order_id,
    DATE(date_created) as fecha,
    status,
    total
FROM wc_orders
WHERE DATE(date_created) = '2025-01-31'
ORDER BY total DESC
"""

df = pd.read_sql(query, conn)

if df.empty:
    print("\n❌ No hay pedidos del 31 de enero en la BD")
else:
    print(f"\n📊 Total pedidos encontrados: {len(df)}")
    print(f"💰 Suma total: ${df['total'].sum():,.0f}")
    
    print("\n" + "-"*70)
    print("DESGLOSE POR ESTADO:")
    print("-"*70)
    
    VALID = ['completed', 'completoenviado', 'processing', 'porsalir']
    
    by_status = df.groupby('status').agg({
        'order_id': 'count',
        'total': 'sum'
    }).reset_index()
    
    total_valid = 0
    total_invalid = 0
    
    for _, row in by_status.iterrows():
        is_valid = row['status'] in VALID
        mark = "✅ INCLUIDO" if is_valid else "❌ EXCLUIDO"
        print(f"\n{mark} - {row['status']}:")
        print(f"  Pedidos: {row['order_id']}")
        print(f"  Total: ${row['total']:,.0f}")
        
        if is_valid:
            total_valid += row['total']
        else:
            total_invalid += row['total']
    
    print("\n" + "="*70)
    print(f"INCLUIDOS (estados válidos):  ${total_valid:,.0f}")
    print(f"EXCLUIDOS (estados no válidos): ${total_invalid:,.0f}")
    print(f"TOTAL EN BD:                   ${df['total'].sum():,.0f}")
    print("="*70)
    print(f"\nWooCommerce muestra: $193,290")
    print(f"Dashboard muestra:   $127,490")
    print(f"BD con filtro actual: ${total_valid:,.0f}")
    
    # Ver detalle de pedidos
    print("\n" + "="*70)
    print("DETALLE DE TODOS LOS PEDIDOS DEL 31 ENE:")
    print("="*70)
    for _, row in df.iterrows():
        mark = "✅" if row['status'] in VALID else "❌"
        print(f"{mark} #{row['order_id']} | {row['status']:20s} | ${row['total']:,.0f}")

conn.close()
