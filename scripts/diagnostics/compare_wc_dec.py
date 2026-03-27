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

print("="*90)
print("COMPARACION WOOCOMMERCE vs BASE DE DATOS - DICIEMBRE 2025")
print("="*90)
print(f"{'Fecha':<12} | {'WC Ped':>7} | {'BD Ped':>7} | {'WC Total':>12} | {'BD Total':>12} | {'BD Total+Env':>12} | {'Diff':>10}")
print("-"*90)

# Estados validos actuales
VALID_STATUSES = ['completed', 'completoenviado', 'processing', 'porsalir']

total_wc = 0
total_bd = 0
total_bd_con_envio = 0

for fecha, wc_data in sorted(wc_report.items()):
    # Query BD
    query = f"""
    SELECT 
        COUNT(*) as pedidos,
        COALESCE(SUM(total), 0) as total_ventas,
        COALESCE(SUM(total + shipping_total), 0) as total_con_envio,
        GROUP_CONCAT(DISTINCT status) as estados
    FROM wc_orders
    WHERE DATE(date_created) = '{fecha}'
    AND status IN ('completed', 'completoenviado', 'processing', 'porsalir')
    """
    
    df = pd.read_sql(query, conn)
    bd_pedidos = df['pedidos'].iloc[0]
    bd_total = df['total_ventas'].iloc[0]
    bd_total_con_envio = df['total_con_envio'].iloc[0]
    
    wc_pedidos = wc_data['pedidos']
    wc_total = wc_data['ventas_totales']
    
    diff = wc_total - bd_total_con_envio
    match = "OK" if abs(diff) < 1000 else "DIFF"
    
    print(f"{fecha:<12} | {wc_pedidos:>7} | {bd_pedidos:>7} | ${wc_total:>10,} | ${bd_total:>10,.0f} | ${bd_total_con_envio:>10,.0f} | {match:>4} ${diff:>8,.0f}")
    
    total_wc += wc_total
    total_bd += bd_total
    total_bd_con_envio += bd_total_con_envio

print("="*90)
print(f"{'TOTALES':<12} | {'':<7} | {'':<7} | ${total_wc:>10,} | ${total_bd:>10,.0f} | ${total_bd_con_envio:>10,.0f} | ${(total_wc - total_bd_con_envio):>10,.0f}")
print("="*90)

# Ver todos los estados en diciembre
print("\n" + "="*90)
print("TODOS LOS ESTADOS EN DICIEMBRE 2025 (SIN FILTRO):")
print("="*90)

query_all = """
SELECT 
    status,
    COUNT(*) as qty,
    SUM(total) as total,
    SUM(total + shipping_total) as total_con_envio
FROM wc_orders
WHERE strftime('%Y-%m', date_created) = '2025-12'
GROUP BY status
ORDER BY total DESC
"""

df_all = pd.read_sql(query_all, conn)
for _, row in df_all.iterrows():
    is_valid = "SI" if row['status'] in VALID_STATUSES else "NO"
    print(f"{is_valid} {row['status']:20s} | {row['qty']:4} ped | Total: ${row['total']:>12,.0f} | +Envio: ${row['total_con_envio']:>12,.0f}")

# Analizar que columna usar
print("\n" + "="*90)
print("ANALISIS: Que columna usar para coincidir con WooCommerce?")
print("="*90)
print(f"WooCommerce 'Ventas totales' parece ser: total + shipping_total")
print(f"Diferencia usando 'total': ${total_wc - total_bd:,.0f}")
print(f"Diferencia usando 'total + shipping_total': ${total_wc - total_bd_con_envio:,.0f}")

conn.close()
