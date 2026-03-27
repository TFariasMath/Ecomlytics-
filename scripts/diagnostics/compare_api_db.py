"""Comparar un pedido en API vs BD"""
import sqlite3
import pandas as pd
from woocommerce import API

URL = "https://tayen.cl"
CK = "ck_5409f28b110a1dd51d930ea0fdcd48ad11706192"
CS = "cs_b8cb8f93124f41fc7165f0ea235fe82e932f09d9"

wcapi = API(
    url=URL,
    consumer_key=CK,
    consumer_secret=CS,
    version="wc/v3",
    timeout=30
)

conn = sqlite3.connect('data/woocommerce.db')

order_id = 57661

print("="*80)
print(f"COMPARACION PEDIDO #{order_id}")
print("="*80)

# Datos de API
print("\nDESDE API:")
response = wcapi.get(f"orders/{order_id}")
if response.status_code == 200:
    order = response.json()
    print(f"  payment_method: '{order.get('payment_method')}'")
    print(f"  payment_method_title: '{order.get('payment_method_title')}'")
    print(f"  date_paid: '{order.get('date_paid')}'")
    print(f"  total: ${float(order.get('total', 0)):,.0f}")
else:
    print(f"  Error: {response.status_code}")

# Datos de BD
print("\nDESDE BD:")
query = f"""
SELECT order_id, payment_method, payment_method_title, date_paid, total
FROM wc_orders
WHERE order_id = {order_id}
"""
df = pd.read_sql(query, conn)
if not df.empty:
    row = df.iloc[0]
    print(f"  payment_method: '{row['payment_method']}'")
    print(f"  payment_method_title: '{row['payment_method_title']}'")
    print(f"  date_paid: '{row['date_paid']}'")
    print(f"  total: ${row['total']:,.0f}")
else:
    print("  No encontrado en BD")

# Ver muestra de pedidos en BD
print("\n" + "="*80)
print("MUESTRA DE 5 PEDIDOS EN BD (2025)")
print("="*80)

query = """
SELECT order_id, payment_method, payment_method_title, date_paid, total
FROM wc_orders
WHERE strftime('%Y', date_created) = '2025'
ORDER BY order_id DESC
LIMIT 5
"""
df = pd.read_sql(query, conn)
for _, row in df.iterrows():
    pm = row['payment_method'] if row['payment_method'] else 'NULL'
    dp = row['date_paid'] if row['date_paid'] else 'NULL'
    print(f"#{row['order_id']} | PM: {pm[:20]:<20} | Date Paid: {str(dp)[:20]}")

conn.close()
