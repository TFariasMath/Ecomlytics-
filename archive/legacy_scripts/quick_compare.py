import pandas as pd
import sqlite3

# Cargar y procesar CSV
df_wc = pd.read_csv("wc-revenue-report-export-17661192702824.csv")
df_wc['Fecha'] = pd.to_datetime(df_wc['Fecha'])
df_wc['year'] = df_wc['Fecha'].dt.year

# Convertir columnas numéricas
for col in ['Pedidos', 'Ventas totales']:
    df_wc[col] = pd.to_numeric(df_wc[col], errors='coerce').fillna(0)

# Totales por año
print("WC CSV:")
for year in [2024, 2025]:
    df_y = df_wc[df_wc['year'] == year]
    print(f"{year}: ${df_y['Ventas totales'].sum():.0f} ({int(df_y['Pedidos'].sum())} ped)")

# BD
conn = sqlite3.connect('data/woocommerce.db')
print("\nBD:")
for year in [2024, 2025]:
    q = f"SELECT COUNT(*) as p, SUM(total) as v FROM wc_orders WHERE strftime('%Y',date_created)='{year}' AND status IN ('completed','completoenviado','processing','porsalir')"
    r = pd.read_sql(q, conn).iloc[0]
    print(f"{year}: ${r['v']:.0f} ({r['p']} ped)")
conn.close()
