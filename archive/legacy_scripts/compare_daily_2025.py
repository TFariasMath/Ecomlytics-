"""
PASO 1: Comparación Día por Día - 2025
Identifica días donde BD tiene más pedidos/ventas que WC CSV
"""
import pandas as pd
import sqlite3

print("="*80)
print("COMPARACION DIA POR DIA - 2025")
print("="*80)

# 1. Cargar WC CSV y agrupar por día
df_wc = pd.read_csv("wc-revenue-report-export-17661192702824.csv")
df_wc['Fecha'] = pd.to_datetime(df_wc['Fecha'])
df_wc['Ventas totales'] = pd.to_numeric(df_wc['Ventas totales'], errors='coerce').fillna(0)
df_wc['Pedidos'] = pd.to_numeric(df_wc['Pedidos'], errors='coerce').fillna(0)

# Filtrar 2025
df_wc_2025 = df_wc[(df_wc['Fecha'] >= '2025-01-01') & (df_wc['Fecha'] < '2026-01-01')].copy()
df_wc_2025['date_str'] = df_wc_2025['Fecha'].dt.strftime('%Y-%m-%d')

# 2. Cargar BD y agrupar por día
conn = sqlite3.connect('data/woocommerce.db')
query = """
SELECT 
    date_only as fecha,
    COUNT(*) as pedidos,
    SUM(total) as ventas
FROM wc_orders
WHERE strftime('%Y', date_created) = '2025'
AND status IN ('completed', 'completoenviado', 'processing', 'porsalir')
GROUP BY date_only
ORDER BY date_only
"""
df_bd = pd.read_sql(query, conn)
df_bd['fecha'] = pd.to_datetime(df_bd['fecha']).dt.strftime('%Y-%m-%d')

# 3. Merge para comparar
df_comp = pd.merge(
    df_wc_2025[['date_str', 'Pedidos', 'Ventas totales']],
    df_bd,
    left_on='date_str',
    right_on='fecha',
    how='outer',
    suffixes=('_wc', '_bd')
).fillna(0)

df_comp['Pedidos'] = df_comp['Pedidos'].astype(int)
df_comp['pedidos'] = df_comp['pedidos'].astype(int)
df_comp['diff_ped'] = df_comp['pedidos'] - df_comp['Pedidos']
df_comp['diff_ventas'] = df_comp['ventas'] - df_comp['Ventas totales']

# 4. Identificar días con discrepancia
discrepancias = df_comp[
    (df_comp['diff_ped'] != 0) | (abs(df_comp['diff_ventas']) > 100)
].copy()

print(f"\nTotal díascon pedidos en WC CSV: {len(df_wc_2025[df_wc_2025['Pedidos'] > 0])}")
print(f"Total días con pedidos en BD: {len(df_bd[df_bd['pedidos'] > 0])}")
print(f"Días con discrepancias: {len(discrepancias)}")

# 5. Mostrar discrepancias
if len(discrepancias) > 0:
    print("\n" + "="*80)
    print("DIAS CON DISCREPANCIAS:")
    print("="*80)
    print(f"{'Fecha':<12} | {'WC Ped':>7} | {'BD Ped':>7} | {'Diff':>6} | {'WC $':>12} | {'BD $':>12} | {'Diff $':>12}")
    print("-"*80)
    
    total_diff_ped = 0
    total_diff_ventas = 0
    
    for _, row in discrepancias.head(50).iterrows():  # Primeros 50
        fecha = row['date_str'] if pd.notna(row['date_str']) else row['fecha']
        wc_ped = int(row['Pedidos'])
        bd_ped = int(row['pedidos'])
        diff_ped = int(row['diff_ped'])
        wc_v = row['Ventas totales']
        bd_v = row['ventas']
        diff_v = row['diff_ventas']
        
        total_diff_ped += diff_ped
        total_diff_ventas += diff_v
        
        marker = "⚠️ " if abs(diff_ped) > 0 else "  "
        print(f"{marker}{fecha:<10} | {wc_ped:>7} | {bd_ped:>7} | {diff_ped:>+6} | ${wc_v:>11,.0f} | ${bd_v:>11,.0f} | ${diff_v:>+11,.0f}")
    
    if len(discrepancias) > 50:
        print(f"\n... y {len(discrepancias) - 50} días más con discrepancias")
    
    print("-"*80)
    print(f"{'TOTAL DIFERENCIA':<39} | {total_diff_ped:>+6} |                    | ${total_diff_ventas:>+11,.0f}")

# 6. Resumen de totales
print("\n" + "="*80)
print("RESUMEN TOTAL 2025")
print("="*80)
wc_total_ped = int(df_wc_2025['Pedidos'].sum())
wc_total_ventas = df_wc_2025['Ventas totales'].sum()
bd_total_ped = int(df_bd['pedidos'].sum())
bd_total_ventas = df_bd['ventas'].sum()

print(f"WC CSV:  {wc_total_ped:>4} pedidos | ${wc_total_ventas:>15,.0f}")
print(f"BD:      {bd_total_ped:>4} pedidos | ${bd_total_ventas:>15,.0f}")
print(f"Diff:    {bd_total_ped - wc_total_ped:>+4} pedidos | ${bd_total_ventas - wc_total_ventas:>+15,.0f}")

# 7. Guardar días con discrepancias para análisis posterior
discrepancias.to_csv('dias_con_discrepancias_2025.csv', index=False)
print(f"\n✅ Guardado: dias_con_discrepancias_2025.csv ({len(discrepancias)} días)")

conn.close()
