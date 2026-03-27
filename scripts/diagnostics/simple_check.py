import sqlite3

conn = sqlite3.connect('data/woocommerce.db')
cursor = conn.cursor()

print("\n" + "="*70)
print("ENERO 2025 - BREAKDOWN POR ESTADO:")
print("="*70)

cursor.execute("""
SELECT status, COUNT(*) as qty, SUM(total) as sum_total
FROM wc_orders
WHERE strftime('%Y-%m', date_created) = '2025-01'
GROUP BY status
ORDER BY sum_total DESC
""")

VALID = ['completed', 'completoenviado', 'processing', 'porsalir', 'on-hold']
valid_sum = 0
invalid_sum = 0

for row in cursor.fetchall():
    status, qty, total = row
    mark = "SI" if status in VALID else "NO"
    print(f"{mark} | {status:20s} | {qty:4d} pedidos | ${total:12,.0f}")
    if status in VALID:
        valid_sum += total
    else:
        invalid_sum += total

print("="*70)
print(f"VALIDO (debe aparecer):  ${valid_sum:,.0f}")
print(f"NO VALIDO (no debe):     ${invalid_sum:,.0f}")
print(f"TOTAL EN BD:             ${valid_sum + invalid_sum:,.0f}")
print("="*70)

conn.close()
