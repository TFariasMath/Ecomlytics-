import sqlite3
import pandas as pd

conn = sqlite3.connect('data/woocommerce.db')

# Ver todos los estados y sus sumas para enero 2025
query = """
SELECT 
    status,
    COUNT(*) as cantidad,
    SUM(total) as total_ventas
FROM wc_orders
WHERE strftime('%Y-%m', date_created) = '2025-01'
GROUP BY status
ORDER BY total_ventas DESC
"""

df = pd.read_sql(query, conn)

print("="*70)
print("VENTAS ENERO 2025 POR ESTADO:")
print("="*70)

VALID_STATUSES = ['completed', 'completoenviado', 'processing', 'porsalir', 'on-hold']

total_valid = 0
total_invalid = 0

for _, row in df.iterrows():
    is_valid = "✅" if row['status'] in VALID_STATUSES else "❌"
    print(f"\n{is_valid} {row['status']}:")
    print(f"   Cantidad: {row['cantidad']} pedidos")
    print(f"   Total: ${row['total_ventas']:,.0f}")
    
    if row['status'] in VALID_STATUSES:
        total_valid += row['total_ventas']
    else:
        total_invalid += row['total_ventas']

print("\n" + "="*70)
print(f"TOTAL ESTADOS VÁLIDOS (lo que SI debe aparecer): ${total_valid:,.0f}")
print(f"TOTAL ESTADOS NO VÁLIDOS (lo que NO debe aparecer): ${total_invalid:,.0f}")
print(f"TOTAL GENERAL EN BD: ${total_valid + total_invalid:,.0f}")
print("="*70)

conn.close()
