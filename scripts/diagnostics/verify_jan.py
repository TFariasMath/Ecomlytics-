import sqlite3
import pandas as pd

conn = sqlite3.connect('data/woocommerce.db')

# Verificar enero 2025 directamente
query_all = """
SELECT SUM(total) as total_all
FROM wc_orders
WHERE strftime('%Y-%m', date_created) = '2025-01'
"""

query_valid = """
SELECT SUM(total) as total_valid
FROM wc_orders
WHERE strftime('%Y-%m', date_created) = '2025-01'
AND status IN ('completed', 'completoenviado', 'processing', 'porsalir', 'on-hold')
"""

total_all = pd.read_sql(query_all, conn).iloc[0]['total_all']
total_valid = pd.read_sql(query_valid, conn).iloc[0]['total_valid']

print("="*70)
print("ENERO 2025 - VERIFICACIÓN:")
print("="*70)
print(f"Total SIN filtro:  ${total_all:,.0f}")
print(f"Total CON filtro:  ${total_valid:,.0f}")
print(f"Diferencia:        ${(total_all - total_valid):,.0f}")
print("="*70)
print(f"\nWooCommerce muestra: $4,583,859")
print(f"Dashboard muestra:   $6,589,944")
print(f"BD con filtro:       ${total_valid:,.0f}")

# Ver los estados que existen
query_states = """
SELECT status, COUNT(*) as qty, SUM(total) as sum_total
FROM wc_orders
WHERE strftime('%Y-%m', date_created) = '2025-01'
GROUP BY status
"""

df_states = pd.read_sql(query_states, conn)
print("\n" + "="*70)
print("ESTADOS EN ENERO 2025:")
print("="*70)

VALID = ['completed', 'completoenviado', 'processing', 'porsalir', 'on-hold']
for _, row in df_states.iterrows():
    mark = "✅" if row['status'] in VALID else "❌"
    print(f"{mark} {row['status']:20s} | ${row['sum_total']:12,.0f} ({row['qty']} pedidos)")

conn.close()
