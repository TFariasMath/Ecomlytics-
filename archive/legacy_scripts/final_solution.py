"""
SOLUCION FINAL - Identificar pedidos que NO están en WC CSV
"""
import pandas as pd
import sqlite3

#  1. Cargar CSV de WC
df_wc = pd.read_csv("wc-revenue-report-export-17661192702824.csv")
df_wc['Fecha'] = pd.to_datetime(df_wc['Fecha'])
df_wc['Ventas totales'] = pd.to_numeric(df_wc['Ventas totales'], errors='coerce').fillna(0)
df_wc['Pedidos'] = pd.to_numeric(df_wc['Pedidos'], errors='coerce').fillna(0)

# Totales WC
df_2025 = df_wc[(df_wc['Fecha'] >= '2025-01-01') & (df_wc['Fecha'] < '2026-01-01')]
wc_2025_total = df_2025['Ventas totales'].sum()
wc_2025_ped = int(df_2025['Pedidos'].sum())

df_2024 = df_wc[(df_wc['Fecha'] >= '2024-01-01') & (df_wc['Fecha'] < '2025-01-01')]
wc_2024_total = df_2024['Ventas totales'].sum()
wc_2024_ped = int(df_2024['Pedidos'].sum())

print("="*80)
print("SOLUCION FINAL")
print("="*80)

print("\nWOOCOMMERCE CSV (FUENTE DE VERDAD):")
print(f"  2024: ${wc_2024_total:>15,.0f}  ({wc_2024_ped} pedidos)")
print(f"  2025: ${wc_2025_total:>15,.0f}  ({wc_2025_ped} pedidos)")

# 2. Comparar con BD
conn = sqlite3.connect('data/woocommerce.db')

print("\nBASE DE DATOS (ACTUAL):")
for year, wc_total, wc_ped in [(2024, wc_2024_total, wc_2024_ped), (2025, wc_2025_total, wc_2025_ped)]:
    q = f"""
    SELECT COUNT(*) as p, SUM(total) as v 
    FROM wc_orders 
    WHERE strftime('%Y',date_created)='{year}' 
    AND status IN ('completed','completoenviado','processing','porsalir')
    """
    r = pd.read_sql(q, conn).iloc[0]
    diff_v = r['v'] - wc_total
    diff_p = r['p'] - wc_ped
    print(f"  {year}: ${r['v']:>15,.0f}  ({r['p']} pedidos)")
    print(f"         Diferencia: ${diff_v:>+15,.0f}  ({diff_p:+d} pedidos)")

# 3. El problema: WC CSV agrupa por FECHA (dia completo), nuestra BD tiene TIMESTAMP
# Necesitamos agrupar nuestra BD por date_only y comparar con WC day by day

print("\n" + "="*80)
print("HIPOTESIS DEL PROBLEMA")
print("="*80)
print("""
El CSV de WooCommerce agrupa las ventas por DÍA (fecha completa).
Nuestra BD tiene pedidos con timestamps, y estamos sumando el campo 'total'.

Pero el 'total' en nuestra BD podría estar INCLUYENDO pedidos que WC NO cuenta:
  - Pedidos cancelados/reembolsados después de ser completados
  - Pedidos con estados que WC filtra en sus reportes
  - Pedidos duplicados en la BD

Vamos a identificar  exactamente qué pedidos tenemos de MÁS.
""")

#  La clave: WC CSV solo muestra días con ventas, mientras nuestra BD tiene TODOS los pedidos
# Necesitamos hacer matching día por día

conn.close()

print("\nPROXIMO PASO:")
print("  1. Comparar conteos de pedidos día por día 2025")
print("  2. Identificar días donde BD > WC CSV")
print("  3. Ver qué pedidos específicos causan la diferencia")
