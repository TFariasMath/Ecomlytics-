import pandas as pd
import sqlite3

conn = sqlite3.connect('data/woocommerce.db')

# Ver totals 2025 por diferentes combinaciones
print("2025 - DIFERENTES CALCULOS:")
print("="*60)

queries = [
    ("Total SIN filtro", "SELECT SUM(total) as v, COUNT(*) as p FROM wc_orders WHERE strftime('%Y',date_created)='2025'"),
    ("Estados válidos", "SELECT SUM(total) as v, COUNT(*) as p FROM wc_orders WHERE strftime('%Y',date_created)='2025' AND status IN ('completed','completoenviado','processing','porsalir')"),
    ("Solo completed", "SELECT SUM(total) as v, COUNT(*) as p FROM wc_orders WHERE strftime('%Y',date_created)='2025' AND status='completed'"),
    ("Solo completoenviado", "SELECT SUM(total) as v, COUNT(*) as p FROM wc_orders WHERE strftime('%Y',date_created)='2025' AND status='completoenviado'"),
]

for name, q in queries:
    r = pd.read_sql(q, conn).iloc[0]
    print(f"{name:<25}: ${r['v']:>12,.0f} ({r['p']:>3} ped)")

# Ver que otros estados hay
print("\n2025 - TODOS LOS ESTADOS:")
print("="*60)
q = "SELECT status, COUNT(*) as p, SUM(total) as v FROM wc_orders WHERE strftime('%Y',date_created)='2025' GROUP BY status ORDER BY v DESC"
df = pd.read_sql(q, conn)
for _, r in df.iterrows():
    print(f"{r['status']:<20}: ${r['v']:>12,.0f} ({r['p']:>3} ped)")

conn.close()

# Cargar CSV y comparar
df_wc = pd.read_csv("wc-revenue-report-export-17661192702824.csv")
df_wc['Fecha'] = pd.to_datetime(df_wc['Fecha'])
df_wc['year'] = df_wc['Fecha'].dt.year
df_wc['Ventas totales'] = pd.to_numeric(df_wc['Ventas totales'], errors='coerce').fillna(0)
df_wc['Pedidos'] = pd.to_numeric(df_wc['Pedidos'], errors='coerce').fillna(0)

df_2025 = df_wc[df_wc['year'] == 2025]
wc_total = df_2025['Ventas totales'].sum()
wc_pedidos = int(df_2025['Pedidos'].sum())

print(f"\nWC CSV 2025: ${wc_total:>12,.0f} ({wc_pedidos:>3} ped)")
