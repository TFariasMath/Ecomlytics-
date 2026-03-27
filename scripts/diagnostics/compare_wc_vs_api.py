"""
COMPARACIÓN DEFINITIVA: WC Revenue vs API Extraction
"""

import pandas as pd
import sqlite3

print("="*80)
print("COMPARACIÓN: WC REVENUE vs API EXTRACTION - ENERO 2025")
print("="*80)

# 1. Cargar WC Revenue
df_wc = pd.read_csv('wc-revenue-report-export-17660892507145.csv')
df_wc['date_created'] = pd.to_datetime(df_wc['date_created'])
df_wc['month'] = df_wc['date_created'].dt.month
df_wc['day'] = df_wc['date_created'].dt.day

# Filtrar solo Enero 2025 y excluir cancelados
df_wc_jan = df_wc[(df_wc['date_created'].dt.year == 2025) & (df_wc['month'] == 1)]

# Excluir estados no válidos (cancelados, failed, etc.)
INVALID_STATUSES = ['cancelled', 'failed', 'refunded', 'trash']
df_wc_jan_valid = df_wc_jan[~df_wc_jan['status'].isin(INVALID_STATUSES)]

print(f"\n📊 WC REVENUE - ENERO 2025:")
print(f"   Total filas: {len(df_wc_jan)}")
print(f"   Excluyendo cancelados/failed: {len(df_wc_jan_valid)}")
print(f"   💰 Total WC Revenue: ${df_wc_jan_valid['net_total'].sum():,.0f}")

# Ver estados en WC Revenue
print(f"\n📋 Estados en WC Revenue (Enero):")
status_counts = df_wc_jan_valid['status'].value_counts()
for status, count in status_counts.items():
    status_total = df_wc_jan_valid[df_wc_jan_valid['status'] == status]['net_total'].sum()
    print(f"   {status}: {count} pedidos = ${status_total:,.0f}")

# 2. Cargar datos de API (BD)
conn = sqlite3.connect('data/woocommerce.db')
df_api = pd.read_sql("""
    SELECT 
        order_id,
        DATE(date_created) as fecha,
        status,
        total
    FROM wc_orders
    WHERE strftime('%Y-%m', date_created) = '2025-01'
""", conn)
conn.close()

print(f"\n📊 API EXTRACTION (BD) - ENERO 2025:")
print(f"   Total pedidos: {len(df_api)}")
print(f"   💰 Total API: ${df_api['total'].sum():,.0f}")

# Ver estados en API
print(f"\n📋 Estados en API (Enero):")
api_status_counts = df_api['status'].value_counts()
for status, count in api_status_counts.items():
    status_total = df_api[df_api['status'] == status]['total'].sum()
    print(f"   {status}: {count} pedidos = ${status_total:,.0f}")

# 3. Comparar estados
print("\n" + "="*80)
print("ANÁLISIS DE DISCREPANCIAS:")
print("="*80)

wc_estados = set(df_wc_jan_valid['status'].unique())
api_estados = set(df_api['status'].unique())

print(f"\n🔍 Estados en WC Revenue pero NO en API:")
missing_in_api = wc_estados - api_estados
if missing_in_api:
    for status in missing_in_api:
        count = len(df_wc_jan_valid[df_wc_jan_valid['status'] == status])
        total = df_wc_jan_valid[df_wc_jan_valid['status'] == status]['net_total'].sum()
        print(f"   ⚠️ {status}: {count} pedidos = ${total:,.0f}")
else:
    print("   ✅ Ninguno")

print(f"\n🔍 Estados en API pero NO en WC Revenue:")
extra_in_api = api_estados - wc_estados
if extra_in_api:
    for status in extra_in_api:
        count = len(df_api[df_api['status'] == status])
        total = df_api[df_api['status'] == status]['total'].sum()
        print(f"   ℹ️ {status}: {count} pedidos = ${total:,.0f}")
else:
    print("   ✅ Ninguno")

# 4. Resumen final
print("\n" + "="*80)
print("RESUMEN:")
print("="*80)
print(f"WC Revenue (válidos): ${df_wc_jan_valid['net_total'].sum():,.0f}")
print(f"API Total:            ${df_api['total'].sum():,.0f}")
diff = df_wc_jan_valid['net_total'].sum() - df_api['total'].sum()
print(f"Diferencia:           ${diff:,.0f}")

if abs(diff) < 1000:
    print("\n✅ LOS DATOS COINCIDEN!")
else:
    print(f"\n❌ HAY DISCREPANCIA DE ${abs(diff):,.0f}")
    print("\n💡 Estados que deberían estar en el filtro de la API:")
    print(f"   {sorted(wc_estados)}")
