"""
Diagnostic script to trace exactly what happens with GA data in the dashboard.
"""
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

# Paths
db_path = Path(__file__).parent / 'data' / 'analytics.db'

print(f"=== DIAGNÓSTICO COMPLETO DE VISITAS DIARIAS ===")
print(f"Fecha actual: {datetime.now()}")
print(f"DB Path: {db_path}")
print(f"DB Existe: {db_path.exists()}")

if not db_path.exists():
    print("❌ Base de datos no encontrada!")
    exit(1)

# 1. Load raw data (como lo hace load_data)
conn = sqlite3.connect(db_path)
df_ga = pd.read_sql("SELECT * FROM ga4_ecommerce", conn)
conn.close()

print(f"\n--- PASO 1: Datos RAW ---")
print(f"Registros: {len(df_ga)}")
if df_ga.empty:
    print("❌ Tabla ga4_ecommerce está VACÍA!")
    exit(1)
print(f"Columnas: {df_ga.columns.tolist()}")
print(f"Muestra Fecha raw: {df_ga['Fecha'].head()}")
print(f"Tipo Fecha: {df_ga['Fecha'].dtype}")

# 2. Parse dates (como lo hace main())
print(f"\n--- PASO 2: Parsing de fechas (como main()) ---")
df_ga['Fecha'] = pd.to_datetime(df_ga['Fecha'].astype(str), format='%Y%m%d', errors='coerce')
df_ga['date_only'] = df_ga['Fecha'].dt.date
print(f"Muestra Fecha parsed: {df_ga['Fecha'].head()}")
print(f"Tipo Fecha: {df_ga['Fecha'].dtype}")
print(f"Muestra date_only: {df_ga['date_only'].head()}")
print(f"Min Fecha: {df_ga['Fecha'].min()}")
print(f"Max Fecha: {df_ga['Fecha'].max()}")

# 3. Simulate show_time_selector() - default is last year
print(f"\n--- PASO 3: Rango de fechas (show_time_selector) ---")
today = datetime.now()
start_date = datetime.combine((today - timedelta(days=365)).date(), datetime.min.time())
end_date = datetime.combine(today.date(), datetime.max.time())
print(f"start_date: {start_date}")
print(f"end_date: {end_date}")

# 4. Apply filter (como view_traffic())
print(f"\n--- PASO 4: Filtrado ---")
print(f"Tipo start_date: {type(start_date)}")
print(f"Tipo df_ga['Fecha'].iloc[0]: {type(df_ga['Fecha'].iloc[0])}")

# Check if already datetime (como el fix)
print(f"Es datetime64?: {pd.api.types.is_datetime64_any_dtype(df_ga['Fecha'])}")

# Apply filter
mask = (df_ga['Fecha'] >= start_date) & (df_ga['Fecha'] <= end_date)
print(f"Mask: {mask.values}")
df_filtered = df_ga[mask]
print(f"Registros después del filtro: {len(df_filtered)}")

if df_filtered.empty:
    print("❌ NO HAY DATOS DESPUÉS DEL FILTRO!")
    print(f"   Datos en DB: {df_ga['Fecha'].min()} a {df_ga['Fecha'].max()}")
    print(f"   Filtro: {start_date} a {end_date}")
else:
    print(f"✅ Datos filtrados correctamente")
    print(df_filtered[['Fecha', 'UsuariosActivos']])

# 5. Create daily_ga (como view_traffic())
print(f"\n--- PASO 5: Agrupación diaria ---")
if not df_filtered.empty:
    daily_ga = df_filtered.groupby('date_only').agg(Visitas=('UsuariosActivos','sum')).reset_index()
    daily_ga['date_only'] = pd.to_datetime(daily_ga['date_only'])
    print(f"Registros daily_ga: {len(daily_ga)}")
    print(daily_ga)
    
    if daily_ga['Visitas'].sum() == 0:
        print("⚠️ Visitas sum = 0. Verificando UsuariosActivos:")
        print(df_filtered['UsuariosActivos'])
else:
    print("❌ No hay datos para agrupar")

print("\n=== FIN DEL DIAGNÓSTICO ===")
