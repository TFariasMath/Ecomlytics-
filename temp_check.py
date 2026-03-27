import sqlite3

conn = sqlite3.connect('data/woocommerce.db')
cursor = conn.cursor()

# Check all statuses
cursor.execute("SELECT status, COUNT(*) FROM wc_orders GROUP BY status")
print("Estados en la base de datos:")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]} pedidos")

# Check specifically for on-hold
cursor.execute("SELECT COUNT(*) FROM wc_orders WHERE status = 'on-hold'")
count = cursor.fetchone()[0]
print(f"\nPedidos 'on-hold' (En espera): {count}")

conn.close()
