import sqlite3

conn = sqlite3.connect('data/woocommerce.db')
cur = conn.cursor()

print("31 ENERO 2025 - PEDIDOS EN BD:")
print("="*70)

cur.execute('''
    SELECT order_id, date_created, status, total
    FROM wc_orders
    WHERE DATE(date_created) = "2025-01-31" 
    ORDER BY total DESC
''')

rows = cur.fetchall()
total = 0

for r in rows:
    print(f"#{r[0]:5d} | {r[1]} | {r[2]:20s} | ${r[3]:10,.0f}")
    total += r[3]

print("="*70)
print(f"TOTAL BD:        ${total:,.0f}")
print(f"WooCommerce:     $193,290")
print(f"DIFERENCIA:      ${abs(total - 193290):,.0f}")

if abs(total - 193290) > 1000:
    print("\n⚠️ FALTA UN PEDIDO!")
    print("Según WooCommerce hay:")
    print("  #17409: $100,510")
    print("  #17408: $20,000")
    print("  (Posiblemente hay más)")

conn.close()
