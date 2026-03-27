"""Investigar por que hay $11M de diferencia"""
import sqlite3
import pandas as pd

conn = sqlite3.connect('data/woocommerce.db')

# La diferencia es $11.2M
# WC dice 53.29M, BD dice 64.55M
# Posibles causas:
# 1. Estados: WC solo cuenta ciertos estados
# 2. Periodo: WC empieza desde una fecha diferente
# 3. El campo 'total' incluye algo que WC no cuenta

print("="*80)
print("INVESTIGACION PROFUNDA: Donde estan los $11M extra?")
print("="*80)

# WC reporta ventas brutas de $52.97M
# Ventas brutas = subtotal de productos (antes de descuentos, sin envio)
# Verificar si tenemos esa columna

# Primero ver estructura de una orden
print("\nEJEMPLO DE UNA ORDEN:")
query_sample = """
SELECT order_id, date_created, status, total, shipping_total, discount_total
FROM wc_orders
WHERE strftime('%Y', date_created) = '2025'
AND status = 'completoenviado'
LIMIT 3
"""
df_sample = pd.read_sql(query_sample, conn)
print(df_sample.to_string())

# Hipotesis: El 'total' en WC ya incluye shipping?
# Verificar: total = subtotal + shipping - discount + tax
print("\n" + "="*80)
print("VERIFICACION: Que es 'total' en la BD?")
print("="*80)

query_verify = """
SELECT 
    order_id,
    total,
    shipping_total,
    discount_total,
    (total - shipping_total + discount_total) as subtotal_calculado
FROM wc_orders
WHERE strftime('%Y', date_created) = '2025'
AND status IN ('completed', 'completoenviado')
LIMIT 5
"""
df_verify = pd.read_sql(query_verify, conn)
print(df_verify.to_string())

# Ahora calcular: Si total YA INCLUYE shipping...
# Entonces Ventas brutas = total - shipping + discount
print("\n" + "="*80)
print("HIPOTESIS: total = subtotal + shipping - discount")
print("Si es asi, Ventas brutas = SUM(total - shipping + discount)")
print("="*80)

query_brutas = """
SELECT 
    SUM(total) as total_bd,
    SUM(shipping_total) as envio_bd,
    SUM(discount_total) as descuento_bd,
    SUM(total - shipping_total + discount_total) as ventas_brutas_calc
FROM wc_orders
WHERE strftime('%Y', date_created) = '2025'
AND status IN ('completed', 'completoenviado', 'processing', 'porsalir')
"""
df_brutas = pd.read_sql(query_brutas, conn)
print(f"Total BD:         ${df_brutas['total_bd'].iloc[0]:>15,.0f}")
print(f"Envio BD:         ${df_brutas['envio_bd'].iloc[0]:>15,.0f}")
print(f"Descuento BD:     ${df_brutas['descuento_bd'].iloc[0]:>15,.0f}")
print(f"Ventas brutas calc: ${df_brutas['ventas_brutas_calc'].iloc[0]:>15,.0f}")
print(f"WC Ventas brutas:   ${52971536:>15,}")
print(f"Diferencia:         ${df_brutas['ventas_brutas_calc'].iloc[0] - 52971536:>+15,.0f}")

# Verificar conteo de pedidos
print("\n" + "="*80)
print("CONTEO DE PEDIDOS 2025")
print("="*80)

query_count = """
SELECT COUNT(*) as pedidos
FROM wc_orders
WHERE strftime('%Y', date_created) = '2025'
AND status IN ('completed', 'completoenviado', 'processing', 'porsalir')
"""
df_count = pd.read_sql(query_count, conn)
print(f"Pedidos en BD (estados validos): {df_count['pedidos'].iloc[0]}")

# Ver distribucion de totales para detectar outliers
print("\n" + "="*80)
print("TOP 20 PEDIDOS MAS GRANDES (posibles outliers)")
print("="*80)

query_top = """
SELECT order_id, date_created, status, total, shipping_total, discount_total
FROM wc_orders
WHERE strftime('%Y', date_created) = '2025'
AND status IN ('completed', 'completoenviado', 'processing', 'porsalir')
ORDER BY total DESC
LIMIT 20
"""
df_top = pd.read_sql(query_top, conn)
for _, row in df_top.iterrows():
    print(f"#{row['order_id']} | {row['date_created'][:10]} | {row['status']:<15} | ${row['total']:>12,.0f}")

conn.close()
