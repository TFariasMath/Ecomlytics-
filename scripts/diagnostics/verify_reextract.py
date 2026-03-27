"""Verificar datos post-reextraccion"""
import sqlite3
import pandas as pd

conn = sqlite3.connect('data/woocommerce.db')

print("="*80)
print("VERIFICACION POST-REEXTRACCION")
print("="*80)

# Contar registros
query = "SELECT COUNT(*) FROM wc_orders"
total = pd.read_sql(query, conn)['COUNT(*)'].iloc[0]
print(f"\nTotal pedidos en BD: {total:,}")

# 2025 stats
query = """
SELECT 
    COUNT(*) as pedidos,
    SUM(total) as ventas
FROM wc_orders
WHERE strftime('%Y', date_created) = '2025'
"""
df_2025 = pd.read_sql(query, conn)
print(f"\n2025:")
print(f"  Pedidos: {df_2025['pedidos'].iloc[0]:,}")
print(f"  Ventas:  ${df_2025['ventas'].iloc[0]:,.0f}")

# Payment methods
query = """
SELECT 
    COALESCE(payment_method_title, 'N/A') as metodo,
    COUNT(*) as pedidos,
    SUM(total) as ventas
FROM wc_orders
WHERE strftime('%Y', date_created) = '2025'
GROUP BY payment_method_title
ORDER BY ventas DESC
"""
df_pay = pd.read_sql(query, conn)
print(f"\nMetodos de Pago 2025:")
for _, row in df_pay.iterrows():
    print(f"  {row['metodo'][:35]:<35} | {row['pedidos']:>5} | ${row['ventas']:>12,.0f}")

# Date paid stats
query = """
SELECT 
    CASE WHEN date_paid IS NOT NULL THEN 'CON_PAGO' ELSE 'SIN_PAGO' END as estado,
    COUNT(*) as pedidos,
    SUM(total) as ventas
FROM wc_orders
WHERE strftime('%Y', date_created) = '2025'
GROUP BY estado
"""
df_paid = pd.read_sql(query, conn)
print(f"\nFecha de Pago 2025:")
for _, row in df_paid.iterrows():
    print(f"  {row['estado']}: {row['pedidos']:>5} pedidos | ${row['ventas']:>12,.0f}")

# Comparar con WooCommerce
print("\n" + "="*80)
print("COMPARACION CON WOOCOMMERCE")
print("="*80)

# Solo contar completados con fecha de pago en 2025
query = """
SELECT 
    SUM(total) as ventas,
    COUNT(*) as pedidos
FROM wc_orders 
WHERE strftime('%Y', date_paid) = '2025'
AND status IN ('completed', 'completoenviado', 'processing', 'porsalir')
"""
df_comp = pd.read_sql(query, conn)

print(f"\nVentas por date_paid 2025:    ${df_comp['ventas'].iloc[0]:>15,.0f} ({df_comp['pedidos'].iloc[0]} pedidos)")
print(f"WooCommerce reporta:          ${53290436:>15,}")
print(f"Diferencia:                   ${df_comp['ventas'].iloc[0] - 53290436:>+15,.0f}")

conn.close()
