"""Verificacion usando SOLO total (sin shipping)"""
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

# Estados validos
VALID_STATUSES = ['completed', 'completoenviado', 'processing', 'porsalir']

print("="*90)
print("VERIFICACION USANDO 'total' (NO shipping)")
print("="*90)
print(f"{'Fecha':<12} | {'WC Ped':>7} | {'BD Ped':>7} | {'WC Total':>12} | {'BD Total':>12} | {'Estado':>8}")
print("-"*90)

total_wc = 0
total_bd = 0
ok_count = 0
diff_count = 0

for fecha, wc_data in sorted(wc_report.items()):
    query = f"""
    SELECT 
        COUNT(*) as pedidos,
        COALESCE(SUM(total), 0) as ventas_totales
    FROM wc_orders
    WHERE DATE(date_created) = '{fecha}'
    AND status IN ('completed', 'completoenviado', 'processing', 'porsalir')
    """
    
    df = pd.read_sql(query, conn)
    bd_pedidos = df['pedidos'].iloc[0]
    bd_ventas = df['ventas_totales'].iloc[0]
    wc_pedidos = wc_data['pedidos']
    wc_ventas = wc_data['ventas_totales']
    
    diff = abs(wc_ventas - bd_ventas)
    if diff < 1000:
        status = "OK"
        ok_count += 1
    else:
        status = "DIFF"
        diff_count += 1
    
    print(f"{fecha:<12} | {wc_pedidos:>7} | {bd_pedidos:>7} | ${wc_ventas:>10,} | ${bd_ventas:>10,.0f} | {status:>8}")
    
    total_wc += wc_ventas
    total_bd += bd_ventas

print("="*90)
print(f"TOTALES      |         |         | ${total_wc:>10,} | ${total_bd:>10,.0f} |")
print("="*90)
print(f"\nResultado: {ok_count} dias OK, {diff_count} dias con diferencia")
print(f"Diferencia total: ${abs(total_wc - total_bd):,.0f}")

if diff_count > 0:
    print("\nPosibles causas de diferencias:")
    print("1. Faltan pedidos en la extraccion (ejecutar ETL nuevamente)")
    print("2. Estados diferentes en WooCommerce")
    print("3. Zona horaria de Chile vs UTC")

conn.close()
