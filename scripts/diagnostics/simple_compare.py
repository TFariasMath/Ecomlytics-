import pandas as pd
import sqlite3

# Cargar WC Revenue
df_wc = pd.read_csv('wc-revenue-report-export-17660892507145.csv')

# Identificar columnas print("COLUMNAS:", df_wc.columns.tolist())
print("\nPRIMERAS 5 FILAS:")
print(df_wc.head())

# Enero 2025
df_jan = df_wc[df_wc['Fecha'].str.contains('2025-01', na=False)]
print(f"\nENERO 2025: {len(df_jan)} pedidos")

# Encontrar columna de total
total_col = [c for c in df_wc.columns if 'total' in c.lower() or 'neto' in c.lower()][0]
print(f"Columna de total: {total_col}")
print(f"TOTAL WC: ${df_jan[total_col].sum():,.0f}")

# API
conn = sqlite3.connect('data/woocommerce.db')
df_api = pd.read_sql("SELECT * FROM wc_orders WHERE strftime('%Y-%m', date_created) = '2025-01'", conn)
conn.close()

VALID = ['completed', 'completoenviado', 'processing', 'porsalir']
df_api_valid = df_api[df_api['status'].isin(VALID)]

print(f"\nAPI Total: ${df_api['total'].sum():,.0f}")
print(f"API Filtrado: ${df_api_valid['total'].sum():,.0f}")
print(f"\nDIFERENCIA: ${df_jan[total_col].sum() - df_api_valid['total'].sum():,.0f}")
