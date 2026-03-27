import sqlite3
import pandas as pd

conn = sqlite3.connect('data/woocommerce.db')

# Estados usados en el dashboard
VALID_STATUSES = ['completed', 'completoenviado', 'processing', 'porsalir']

# Verificar diciembre 2025 (mes actual)
print('='*70)
print('VERIFICACIÓN DICIEMBRE 2025')
print('='*70)

query = """
SELECT status, COUNT(*) as qty, SUM(total) as total
FROM wc_orders
WHERE strftime('%Y-%m', date_created) = '2025-12'
GROUP BY status
ORDER BY total DESC
"""

df = pd.read_sql(query, conn)

total_valid = 0
total_all = 0

for _, row in df.iterrows():
    is_valid = 'OK' if row['status'] in VALID_STATUSES else 'NO'
    print(f"{is_valid} {row['status']:20s} | {row['qty']:4d} pedidos | ${row['total']:12,.0f}")
    total_all += row['total']
    if row['status'] in VALID_STATUSES:
        total_valid += row['total']

print('='*70)
print(f"Total VÁLIDO (dashboard):  ${total_valid:,.0f}")
print(f"Total TODOS los estados:   ${total_all:,.0f}")
print(f"Diferencia:                ${(total_all - total_valid):,.0f}")
print('='*70)

conn.close()
