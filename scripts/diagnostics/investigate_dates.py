"""Investigar discrepancia dia por dia"""
import sqlite3
import pandas as pd

conn = sqlite3.connect('data/woocommerce.db')

# Verificar 18 dic (5 pedidos, $200,540)
print("="*90)
print("DETALLE 18 DICIEMBRE 2025")
print("="*90)

query = """
SELECT 
    order_id,
    status,
    total,
    shipping_total,
    (total + shipping_total) as ventas_totales,
    date_created
FROM wc_orders
WHERE DATE(date_created) = '2025-12-18'
ORDER BY order_id
"""

df = pd.read_sql(query, conn)
print(f"Total pedidos en BD: {len(df)}")
print(f"\nDetalle:")
for _, row in df.iterrows():
    print(f"  #{row['order_id']} | Status: {row['status']:15s} | Total: ${row['total']:>10,.0f} | Envio: ${row['shipping_total']:>6,.0f} | VentasT: ${row['ventas_totales']:>10,.0f}")

print(f"\nSuma total BD: ${df['total'].sum():,.0f}")
print(f"Suma total+envio BD: ${df['ventas_totales'].sum():,.0f}")
print(f"WooCommerce reporta: $200,540")

# Ver solo pedidos validos
VALID = ['completed', 'completoenviado', 'processing', 'porsalir']
df_valid = df[df['status'].isin(VALID)]
print(f"\nPedidos validos ({len(df_valid)}):")
print(f"Suma validos (total): ${df_valid['total'].sum():,.0f}")
print(f"Suma validos (total+envio): ${df_valid['ventas_totales'].sum():,.0f}")

# Verificar 19 dic (1 pedido, $382,500)
print("\n" + "="*90)
print("DETALLE 19 DICIEMBRE 2025")
print("="*90)

query = """
SELECT 
    order_id,
    status,
    total,
    shipping_total,
    (total + shipping_total) as ventas_totales,
    date_created
FROM wc_orders
WHERE DATE(date_created) = '2025-12-19'
ORDER BY order_id
"""

df = pd.read_sql(query, conn)
print(f"Total pedidos en BD: {len(df)}")
for _, row in df.iterrows():
    print(f"  #{row['order_id']} | Status: {row['status']:15s} | Total: ${row['total']:>10,.0f} | Envio: ${row['shipping_total']:>6,.0f} | VentasT: ${row['ventas_totales']:>10,.0f}")

print(f"\nWooCommerce reporta: $382,500")

conn.close()
