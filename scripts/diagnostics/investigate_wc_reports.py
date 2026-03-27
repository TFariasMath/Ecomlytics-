"""
INVESTIGACION: Por que WooCommerce reporta menos ventas que la BD?

HALLAZGO CLAVE: Los pedidos EXISTEN en WooCommerce API pero NO aparecen en reportes.

Hipotesis:
1. WooCommerce Analytics usa diferentes estados para calcular ventas
2. Los pedidos con customer_id=0 (invitados) podrian ser excluidos
3. WC usa fecha diferente (date_paid vs date_created)
4. Problema con estados custom como 'completoenviado'
"""
import sqlite3
import pandas as pd

conn = sqlite3.connect('data/woocommerce.db')

print("="*80)
print("ANALISIS: Por que WooCommerce excluye pedidos?")
print("="*80)

# Verificar pedidos grandes
print("\nPEDIDOS > $500K - Verificar customer_id y date_paid:")
query = """
SELECT 
    order_id,
    date_created,
    date_paid,
    status,
    total,
    customer_id,
    customer_email
FROM wc_orders
WHERE total > 500000
AND strftime('%Y', date_created) = '2025'
ORDER BY total DESC
LIMIT 20
"""

df = pd.read_sql(query, conn)
for _, row in df.iterrows():
    cust = "GUEST" if row['customer_id'] == 0 else f"#{row['customer_id']}"
    paid = row['date_paid'][:10] if row['date_paid'] else "NO PAGADO"
    created = row['date_created'][:10] if row['date_created'] else "N/A"
    print(f"#{row['order_id']} | Creado: {created} | Pagado: {paid} | {row['status']:<15} | ${row['total']:>12,.0f} | {cust}")

# Analisis por customer_id
print("\n" + "="*80)
print("VENTAS POR TIPO DE CLIENTE (2025)")
print("="*80)

query_cust = """
SELECT 
    CASE WHEN customer_id = 0 THEN 'INVITADO' ELSE 'REGISTRADO' END as tipo_cliente,
    COUNT(*) as pedidos,
    SUM(total) as ventas
FROM wc_orders
WHERE strftime('%Y', date_created) = '2025'
AND status IN ('completed', 'completoenviado', 'processing', 'porsalir')
GROUP BY tipo_cliente
"""

df_cust = pd.read_sql(query_cust, conn)
for _, row in df_cust.iterrows():
    print(f"{row['tipo_cliente']:<15} | {row['pedidos']:>5} pedidos | ${row['ventas']:>15,.0f}")

# Analisis por estado
print("\n" + "="*80)
print("VENTAS POR ESTADO (2025) - Verificar que estados usa WC")
print("="*80)

query_status = """
SELECT 
    status,
    COUNT(*) as pedidos,
    SUM(total) as ventas
FROM wc_orders
WHERE strftime('%Y', date_created) = '2025'
GROUP BY status
ORDER BY ventas DESC
"""

df_status = pd.read_sql(query_status, conn)
print(f"\n{'Estado':<20} | {'Pedidos':>8} | {'Ventas':>15}")
print("-"*50)
for _, row in df_status.iterrows():
    print(f"{row['status']:<20} | {row['pedidos']:>8} | ${row['ventas']:>13,.0f}")

# Verificar si WC podria usar solo 'completed'
print("\n" + "="*80)
print("HIPOTESIS: WC solo cuenta 'completed' (no completoenviado)?")
print("="*80)

query_completed = """
SELECT SUM(total) as total_completed
FROM wc_orders
WHERE strftime('%Y', date_created) = '2025'
AND status = 'completed'
"""

df_comp = pd.read_sql(query_completed, conn)
print(f"Total solo 'completed': ${df_comp['total_completed'].iloc[0]:,.0f}")
print(f"WC reporta:             $53,290,436")

# Verificar fecha de pago vs fecha creacion
print("\n" + "="*80)
print("VERIFICAR: Pedidos por fecha de pago vs fecha creacion")
print("="*80)

query_paid = """
SELECT 
    strftime('%Y-%m', date_paid) as mes_pago,
    COUNT(*) as pedidos,
    SUM(total) as ventas
FROM wc_orders
WHERE strftime('%Y', date_paid) = '2025'
AND status IN ('completed', 'completoenviado', 'processing', 'porsalir')
GROUP BY mes_pago
ORDER BY mes_pago
"""

df_paid = pd.read_sql(query_paid, conn)
if not df_paid.empty:
    print("\nPor fecha de PAGO:")
    for _, row in df_paid.iterrows():
        print(f"{row['mes_pago']} | {row['pedidos']:>5} pedidos | ${row['ventas']:>13,.0f}")

conn.close()
