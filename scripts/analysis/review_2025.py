"""Revision completa del ano 2025 - Pedidos y Ventas por mes"""
import sqlite3
import pandas as pd

conn = sqlite3.connect('data/woocommerce.db')

VALID_STATUSES = ['completed', 'completoenviado', 'processing', 'porsalir']

print("="*80)
print("REVISION COMPLETA 2025 - BASE DE DATOS")
print("="*80)

# Query mensual
query = """
SELECT 
    strftime('%Y-%m', date_created) as mes,
    COUNT(*) as pedidos,
    SUM(total) as ventas,
    SUM(shipping_total) as envio,
    COUNT(DISTINCT customer_id) as clientes
FROM wc_orders
WHERE strftime('%Y', date_created) = '2025'
AND status IN ('completed', 'completoenviado', 'processing', 'porsalir')
GROUP BY mes
ORDER BY mes
"""

df = pd.read_sql(query, conn)

print(f"\n{'Mes':<10} | {'Pedidos':>8} | {'Ventas ($)':>15} | {'Envio ($)':>12} | {'Clientes':>10}")
print("-"*80)

total_pedidos = 0
total_ventas = 0
total_envio = 0

meses_nombres = {
    '01': 'Enero', '02': 'Febrero', '03': 'Marzo', '04': 'Abril',
    '05': 'Mayo', '06': 'Junio', '07': 'Julio', '08': 'Agosto',
    '09': 'Septiembre', '10': 'Octubre', '11': 'Noviembre', '12': 'Diciembre'
}

for _, row in df.iterrows():
    mes_num = row['mes'].split('-')[1]
    mes_nombre = meses_nombres.get(mes_num, row['mes'])
    print(f"{mes_nombre:<10} | {row['pedidos']:>8} | ${row['ventas']:>13,.0f} | ${row['envio']:>10,.0f} | {row['clientes']:>10}")
    total_pedidos += row['pedidos']
    total_ventas += row['ventas']
    total_envio += row['envio']

print("-"*80)
print(f"{'TOTAL':<10} | {total_pedidos:>8} | ${total_ventas:>13,.0f} | ${total_envio:>10,.0f} |")
print("="*80)

# Resumen por estado
print("\n" + "="*80)
print("DESGLOSE POR ESTADO (2025)")
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

print(f"\n{'Estado':<20} | {'Pedidos':>8} | {'Ventas ($)':>15} | {'En filtro?':>10}")
print("-"*80)

for _, row in df_status.iterrows():
    en_filtro = "SI" if row['status'] in VALID_STATUSES else "NO"
    print(f"{row['status']:<20} | {row['pedidos']:>8} | ${row['ventas']:>13,.0f} | {en_filtro:>10}")

# Verificar rango de fechas
print("\n" + "="*80)
print("RANGO DE DATOS EN BD")
print("="*80)

query_range = """
SELECT 
    MIN(date_created) as primera_orden,
    MAX(date_created) as ultima_orden,
    COUNT(*) as total_registros
FROM wc_orders
"""

df_range = pd.read_sql(query_range, conn)
print(f"Primera orden: {df_range['primera_orden'].iloc[0]}")
print(f"Ultima orden:  {df_range['ultima_orden'].iloc[0]}")
print(f"Total registros (todos los estados): {df_range['total_registros'].iloc[0]}")

conn.close()
