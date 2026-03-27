"""Comparar TOTAL de pedidos WC vs BD en diciembre"""
import sqlite3
import pandas as pd

conn = sqlite3.connect('data/woocommerce.db')

# Datos de WooCommerce (del reporte del usuario)
wc_report = {
    '2025-12-19': {'pedidos': 1, 'ventas_totales': 382500},
    '2025-12-18': {'pedidos': 5, 'ventas_totales': 200540},
    '2025-12-17': {'pedidos': 2, 'ventas_totales': 95903},
    '2025-12-16': {'pedidos': 4, 'ventas_totales': 222687},
    '2025-12-15': {'pedidos': 5, 'ventas_totales': 411209},
    '2025-12-11': {'pedidos': 5, 'ventas_totales': 619890},
    '2025-12-10': {'pedidos': 2, 'ventas_totales': 121700},
    '2025-12-09': {'pedidos': 2, 'ventas_totales': 62680},
    '2025-12-08': {'pedidos': 1, 'ventas_totales': 8480},
    '2025-12-07': {'pedidos': 1, 'ventas_totales': 61300},
    '2025-12-05': {'pedidos': 1, 'ventas_totales': 42240},
    '2025-12-04': {'pedidos': 3, 'ventas_totales': 624260},
    '2025-12-03': {'pedidos': 2, 'ventas_totales': 97564},
    '2025-12-02': {'pedidos': 2, 'ventas_totales': 717270},
    '2025-12-01': {'pedidos': 1, 'ventas_totales': 58930},
}

# Sumar totales de WooCommerce
total_wc_pedidos = sum(d['pedidos'] for d in wc_report.values())
total_wc_ventas = sum(d['ventas_totales'] for d in wc_report.values())

# Obtener totales de BD (mismos dias)
VALID_STATUSES = ['completed', 'completoenviado', 'processing', 'porsalir']

# Query para el mismo rango de fechas
query = """
SELECT 
    COUNT(*) as total_pedidos,
    SUM(total) as total_ventas
FROM wc_orders
WHERE DATE(date_created) BETWEEN '2025-12-01' AND '2025-12-19'
AND status IN ('completed', 'completoenviado', 'processing', 'porsalir')
"""

df = pd.read_sql(query, conn)
total_bd_pedidos = df['total_pedidos'].iloc[0]
total_bd_ventas = df['total_ventas'].iloc[0]

print("="*70)
print("COMPARACION TOTAL DICIEMBRE 2025 (01 al 19)")
print("="*70)
print(f"\n{'Metrica':<20} {'WooCommerce':>15} {'Base de Datos':>15} {'Diferencia':>15}")
print("-"*70)
print(f"{'Pedidos':<20} {total_wc_pedidos:>15} {total_bd_pedidos:>15} {total_bd_pedidos - total_wc_pedidos:>+15}")
print(f"{'Ventas ($)':<20} {total_wc_ventas:>15,} {total_bd_ventas:>15,.0f} {total_bd_ventas - total_wc_ventas:>+15,.0f}")
print("-"*70)

if total_wc_pedidos == total_bd_pedidos:
    print("\n CANTIDAD DE PEDIDOS COINCIDE!")
    print("La diferencia diaria es probablemente por ZONA HORARIA (Chile vs UTC)")
else:
    print(f"\n DIFERENCIA DE {abs(total_bd_pedidos - total_wc_pedidos)} PEDIDOS")
    if total_bd_pedidos > total_wc_pedidos:
        print("BD tiene MAS pedidos que WC - posible duplicados o estados diferentes")
    else:
        print("BD tiene MENOS pedidos que WC - faltan extraer algunos pedidos")

# Verificar por dia
print("\n" + "="*70)
print("DETALLE POR DIA (donde hay diferencia)")
print("="*70)

for fecha, wc_data in sorted(wc_report.items()):
    query_day = f"""
    SELECT COUNT(*) as pedidos, SUM(total) as ventas
    FROM wc_orders
    WHERE DATE(date_created) = '{fecha}'
    AND status IN ('completed', 'completoenviado', 'processing', 'porsalir')
    """
    df_day = pd.read_sql(query_day, conn)
    bd_pedidos = df_day['pedidos'].iloc[0]
    
    if wc_data['pedidos'] != bd_pedidos:
        diff_ped = bd_pedidos - wc_data['pedidos']
        print(f"{fecha}: WC={wc_data['pedidos']} pedidos, BD={bd_pedidos} pedidos (diff: {diff_ped:+d})")

conn.close()
