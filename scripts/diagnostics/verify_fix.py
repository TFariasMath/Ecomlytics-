"""Verificacion final: Dashboard ahora usa ventas_totales = total + shipping_total"""
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
print("VERIFICACION: Dashboard ahora usa ventas_totales = total + shipping_total")
print("="*90)

total_wc = 0
total_dashboard = 0
errores = 0

for fecha, wc_data in sorted(wc_report.items()):
    query = f"""
    SELECT 
        COUNT(*) as pedidos,
        COALESCE(SUM(total + shipping_total), 0) as ventas_totales
    FROM wc_orders
    WHERE DATE(date_created) = '{fecha}'
    AND status IN ('completed', 'completoenviado', 'processing', 'porsalir')
    """
    
    df = pd.read_sql(query, conn)
    bd_ventas = df['ventas_totales'].iloc[0]
    wc_ventas = wc_data['ventas_totales']
    
    diff = abs(wc_ventas - bd_ventas)
    match = "OK" if diff < 1000 else "ERROR"
    if diff >= 1000:
        errores += 1
    
    print(f"{fecha} | WC: ${wc_ventas:>10,} | Dashboard: ${bd_ventas:>10,.0f} | {match}")
    
    total_wc += wc_ventas
    total_dashboard += bd_ventas

print("="*90)
print(f"TOTAL WC:        ${total_wc:>12,}")
print(f"TOTAL Dashboard: ${total_dashboard:>12,.0f}")
print(f"Diferencia:      ${abs(total_wc - total_dashboard):>12,.0f}")
print("="*90)

if errores == 0:
    print("RESULTADO: CORRECTO - Los datos coinciden!")
else:
    print(f"RESULTADO: {errores} dias con diferencias")

conn.close()
