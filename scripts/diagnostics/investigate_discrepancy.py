"""Investigar discrepancia anual 2025: WC=$53,290,436 vs BD=$64,555,423"""
import sqlite3
import pandas as pd

conn = sqlite3.connect('data/woocommerce.db')

# Datos de WooCommerce segun el usuario
WC_VENTAS_BRUTAS = 52971536
WC_VENTAS_NETAS = 52519736
WC_VENTAS_TOTALES = 53290436
WC_ENVIO = 770700
WC_CUPONES = 380100
WC_DEVOLUCIONES = 71700

print("="*80)
print("INVESTIGACION: DISCREPANCIA ANUAL 2025")
print("="*80)
print(f"\nWooCommerce reporta (1 Ene - 20 Dic 2025):")
print(f"  Ventas brutas:  ${WC_VENTAS_BRUTAS:>12,}")
print(f"  Devoluciones:   ${WC_DEVOLUCIONES:>12,}")
print(f"  Cupones:        ${WC_CUPONES:>12,}")
print(f"  Ventas netas:   ${WC_VENTAS_NETAS:>12,}")
print(f"  Envio:          ${WC_ENVIO:>12,}")
print(f"  VENTAS TOTALES: ${WC_VENTAS_TOTALES:>12,}")

# Verificar que columnas tenemos
print("\n" + "="*80)
print("COLUMNAS DISPONIBLES EN wc_orders:")
print("="*80)
query_cols = "SELECT * FROM wc_orders LIMIT 1"
df_sample = pd.read_sql(query_cols, conn)
print(df_sample.columns.tolist())

# Calcular totales de BD con diferentes combinaciones
print("\n" + "="*80)
print("PRUEBAS DE CALCULO BD (2025)")
print("="*80)

# Estados validos actuales
VALID_STATUSES = ['completed', 'completoenviado', 'processing', 'porsalir']

# Test 1: Solo total (estados validos)
query1 = """
SELECT SUM(total) as ventas FROM wc_orders
WHERE strftime('%Y', date_created) = '2025'
AND status IN ('completed', 'completoenviado', 'processing', 'porsalir')
"""
result1 = pd.read_sql(query1, conn)['ventas'].iloc[0]

# Test 2: total - discount_total (ventas netas)
query2 = """
SELECT SUM(total - discount_total) as ventas FROM wc_orders
WHERE strftime('%Y', date_created) = '2025'
AND status IN ('completed', 'completoenviado', 'processing', 'porsalir')
"""
result2 = pd.read_sql(query2, conn)['ventas'].iloc[0]

# Test 3: total + shipping_total
query3 = """
SELECT SUM(total + shipping_total) as ventas FROM wc_orders
WHERE strftime('%Y', date_created) = '2025'
AND status IN ('completed', 'completoenviado', 'processing', 'porsalir')
"""
result3 = pd.read_sql(query3, conn)['ventas'].iloc[0]

# Test 4: Verificar suma de shipping
query4 = """
SELECT SUM(shipping_total) as envio FROM wc_orders
WHERE strftime('%Y', date_created) = '2025'
AND status IN ('completed', 'completoenviado', 'processing', 'porsalir')
"""
result4 = pd.read_sql(query4, conn)['envio'].iloc[0]

# Test 5: Verificar suma de descuentos
query5 = """
SELECT SUM(discount_total) as descuentos FROM wc_orders
WHERE strftime('%Y', date_created) = '2025'
AND status IN ('completed', 'completoenviado', 'processing', 'porsalir')
"""
result5 = pd.read_sql(query5, conn)['descuentos'].iloc[0]

print(f"\n{'Calculo':<40} | {'BD':>15} | {'WC':>15} | {'Diff':>15}")
print("-"*95)
print(f"{'SUM(total) [estados validos]':<40} | ${result1:>13,.0f} | ${WC_VENTAS_TOTALES:>13,} | ${result1-WC_VENTAS_TOTALES:>+13,.0f}")
print(f"{'SUM(total - discount_total)':<40} | ${result2:>13,.0f} | ${WC_VENTAS_NETAS:>13,} | ${result2-WC_VENTAS_NETAS:>+13,.0f}")
print(f"{'SUM(total + shipping_total)':<40} | ${result3:>13,.0f} | ${WC_VENTAS_TOTALES:>13,} | ${result3-WC_VENTAS_TOTALES:>+13,.0f}")
print(f"{'SUM(shipping_total)':<40} | ${result4:>13,.0f} | ${WC_ENVIO:>13,} | ${result4-WC_ENVIO:>+13,.0f}")
print(f"{'SUM(discount_total)':<40} | ${result5:>13,.0f} | ${WC_CUPONES:>13,} | ${result5-WC_CUPONES:>+13,.0f}")

# Verificar si hay duplicados
print("\n" + "="*80)
print("VERIFICAR DUPLICADOS")
print("="*80)

query_dup = """
SELECT order_id, COUNT(*) as veces
FROM wc_orders
WHERE strftime('%Y', date_created) = '2025'
GROUP BY order_id
HAVING veces > 1
"""
df_dup = pd.read_sql(query_dup, conn)
if df_dup.empty:
    print("No hay duplicados de order_id")
else:
    print(f"HAY {len(df_dup)} order_id duplicados!")
    print(df_dup.head(10))

# Ver conteo por estado
print("\n" + "="*80)
print("CONTEO POR ESTADO (2025)")
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
for _, row in df_status.iterrows():
    en_filtro = "SI" if row['status'] in VALID_STATUSES else "NO"
    print(f"{en_filtro:>3} | {row['status']:<20} | {row['pedidos']:>5} ped | ${row['ventas']:>12,.0f}")

# Hipotesis: WC probablemente usa total - discount_total
print("\n" + "="*80)
print("HIPOTESIS: WC 'Ventas totales' = total - discount + shipping?")
print("="*80)

# Ventas totales WC = Ventas netas + Envio = 52,519,736 + 770,700 = 53,290,436
ventas_netas_calc = WC_VENTAS_BRUTAS - WC_DEVOLUCIONES - WC_CUPONES
print(f"WC Ventas netas = Brutas - Devoluciones - Cupones")
print(f"               = {WC_VENTAS_BRUTAS:,} - {WC_DEVOLUCIONES:,} - {WC_CUPONES:,} = {ventas_netas_calc:,}")
print(f"WC Ventas totales = Ventas netas + Envio")
print(f"                  = {WC_VENTAS_NETAS:,} + {WC_ENVIO:,} = {WC_VENTAS_NETAS + WC_ENVIO:,}")

conn.close()
