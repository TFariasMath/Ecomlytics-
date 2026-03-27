"""
Verificar si tenemos los pedidos correctos en la BD
"""

import sqlite3
import pandas as pd

conn = sqlite3.connect('data/woocommerce.db')

print("="*70)
print("VERIFICACIÓN: ¿Tenemos los pedidos de WooCommerce?")
print("="*70)

# Pedidos que el usuario ve en WooCommerce para 31 Ene
wc_orders = [17409, 17408]

print(f"\n🔍 Buscando pedidos #{wc_orders} en la BD...")

for order_id in wc_orders:
    query = f"SELECT * FROM wc_orders WHERE order_id = {order_id}"
    df = pd.read_sql(query, conn)
    
    if df.empty:
        print(f"\n❌ Pedido #{order_id} NO ENCONTRADO en BD")
    else:
        print(f"\n✅ Pedido #{order_id} ENCONTRADO:")
        print(f"   Fecha: {df['date_created'].iloc[0]}")
        print(f"   Estado: {df['status'].iloc[0]}")
        print(f"   Total: ${df['total'].iloc[0]:,.0f}")

# Ver qué pedidos SÍ tenemos para el 31 enero
print("\n" + "="*70)
print("PEDIDOS QUE SÍ TENEMOS PARA 31 ENERO 2025:")
print("="*70)

df_jan31 = pd.read_sql("""
    SELECT order_id, date_created, status, total
    FROM wc_orders
    WHERE DATE(date_created) = '2025-01-31'
    ORDER BY order_id DESC
""", conn)

if df_jan31.empty:
    print("\n❌ NO HAY PEDIDOS del 31 enero en la BD")
else:
    print(f"\n📦 {len(df_jan31)} pedidos encontrados:")
    for _, row in df_jan31.iterrows():
        print(f"   #{row['order_id']} | {row['status']} | ${row['total']:,.0f}")
    print(f"\n💰 Total: ${df_jan31['total'].sum():,.0f}")

# Ver el pedido más reciente en la BD
print("\n" + "="*70)
print("PEDIDO MÁS RECIENTE EN LA BD:")
print("="*70)

df_latest = pd.read_sql("""
    SELECT order_id, date_created, status, total
    FROM wc_orders
    ORDER BY date_created DESC
    LIMIT 5
""", conn)

for _, row in df_latest.iterrows():
    print(f"#{row['order_id']} | {row['date_created']} | {row['status']} | ${row['total']:,.0f}")

conn.close()

print("\n" + "="*70)
print("DIAGNÓSTICO:")
print("="*70)
print("Si los order IDs no coinciden, el problema es que:")
print("1. La extracción de la API no está funcionando correctamente, O")
print("2. Estamos conectados a una BD/tienda diferente, O") 
print("3. Los datos en la BD están desactualizados")
