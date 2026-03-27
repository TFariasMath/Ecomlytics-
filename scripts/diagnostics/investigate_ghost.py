"""CRITICO: Investigar pedidos fantasma en la BD"""
import sqlite3
import pandas as pd

conn = sqlite3.connect('data/woocommerce.db')

# Pedidos que NO existen en WooCommerce segun el usuario
GHOST_ORDERS = [56336, 56963, 56363]

print("="*80)
print("INVESTIGACION: PEDIDOS FANTASMA")
print("="*80)

for order_id in GHOST_ORDERS:
    query = f"""
    SELECT *
    FROM wc_orders
    WHERE order_id = {order_id}
    """
    df = pd.read_sql(query, conn)
    
    if not df.empty:
        print(f"\n{'='*40}")
        print(f"PEDIDO #{order_id}")
        print(f"{'='*40}")
        for col in df.columns:
            val = df[col].iloc[0]
            if val is not None and str(val).strip() != '':
                print(f"  {col}: {val}")

# Verificar patron de order_id
print("\n" + "="*80)
print("PATRON DE ORDER_ID EN 2025")
print("="*80)

query_pattern = """
SELECT 
    MIN(order_id) as min_id,
    MAX(order_id) as max_id,
    COUNT(*) as total,
    COUNT(DISTINCT order_id) as unicos
FROM wc_orders
WHERE strftime('%Y', date_created) = '2025'
"""
df_pattern = pd.read_sql(query_pattern, conn)
print(f"Order ID minimo: {df_pattern['min_id'].iloc[0]}")
print(f"Order ID maximo: {df_pattern['max_id'].iloc[0]}")
print(f"Total registros: {df_pattern['total'].iloc[0]}")
print(f"IDs unicos: {df_pattern['unicos'].iloc[0]}")

# Verificar si hay gaps en los order_id
print("\n" + "="*80)
print("VERIFICAR GAPS EN ORDER_ID")
print("="*80)

query_ids = """
SELECT order_id
FROM wc_orders
WHERE strftime('%Y', date_created) = '2025'
ORDER BY order_id
"""
df_ids = pd.read_sql(query_ids, conn)
ids = df_ids['order_id'].tolist()

if len(ids) > 1:
    expected_total = ids[-1] - ids[0] + 1
    actual = len(ids)
    gaps = expected_total - actual
    print(f"Rango de IDs: {ids[0]} a {ids[-1]}")
    print(f"IDs esperados (secuencial): {expected_total}")
    print(f"IDs reales: {actual}")
    print(f"Gaps (faltan): {gaps}")

# Ver de donde vino el pedido fantasma - verificar fechas
print("\n" + "="*80)
print("VERIFICAR INTEGRIDAD: Pedidos alrededor de #56336 (5 Mar)")
print("="*80)

query_around = """
SELECT order_id, date_created, status, total
FROM wc_orders
WHERE order_id BETWEEN 56330 AND 56340
ORDER BY order_id
"""
df_around = pd.read_sql(query_around, conn)
for _, row in df_around.iterrows():
    marker = " <<< FANTASMA" if row['order_id'] in GHOST_ORDERS else ""
    print(f"#{row['order_id']} | {row['date_created']} | {row['status']:<15} | ${row['total']:>12,.0f}{marker}")

# Verificar si hay datos duplicados o mal importados
print("\n" + "="*80)
print("VERIFICAR: Pedidos con totales mayores a $500K")
print("="*80)

query_big = """
SELECT order_id, date_created, status, total, customer_email
FROM wc_orders
WHERE total > 500000
AND strftime('%Y', date_created) = '2025'
ORDER BY total DESC
"""
df_big = pd.read_sql(query_big, conn)
print(f"Pedidos > $500K: {len(df_big)}")
print(f"Suma total: ${df_big['total'].sum():,.0f}")
print("\nDetalle:")
for _, row in df_big.iterrows():
    email = row['customer_email'][:30] if row['customer_email'] else "N/A"
    print(f"#{row['order_id']} | {row['date_created'][:10]} | ${row['total']:>12,.0f} | {email}")

conn.close()
