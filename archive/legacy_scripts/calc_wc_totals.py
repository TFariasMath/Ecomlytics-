import pandas as pd

# Calcular EXACTAMENTE el total 2025 del CSV
df = pd.read_csv("wc-revenue-report-export-17661192702824.csv")
df['Fecha'] = pd.to_datetime(df['Fecha'])
df['Ventas totales'] = pd.to_numeric(df['Ventas totales'], errors='coerce').fillna(0)
df['Ped'] = pd.to_numeric(df['Pedidos'], errors='coerce').fillna(0)

df_2025 = df[(df['Fecha'] >= '2025-01-01') & (df['Fecha'] < '2026-01-01')]
df_2024 = df[(df['Fecha'] >= '2024-01-01') & (df['Fecha'] < '2025-01-01')]

print("WC CSV TOTALES:")
print(f"2024: ${df_2024['Ventas totales'].sum():.0f} ({int(df_2024['Ped'].sum())} ped)")
print(f"2025: ${df_2025['Ventas totales'].sum():.0f} ({int(df_2025['Ped'].sum())} ped)")

# Guardar a archivo para poder leerlo
with open("wc_totals.txt", "w") as f:
    f.write(f"2024: {df_2024['Ventas totales'].sum():.0f}\n")
    f.write(f"2025: {df_2025['Ventas totales'].sum():.0f}\n")
