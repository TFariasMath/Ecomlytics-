"""
COMPARACIÓN DEFINITIVA CORREGIDA: WC Revenue vs API Extraction
"""

import pandas as pd
import sqlite3

print("="*80)
print("COMPARACIÓN: WC REVENUE vs API EXTRACTION - ENERO 2025")
print("="*80)

# 1. Cargar WC Revenue
df_wc = pd.read_csv('wc-revenue-report-export-17660892507145.csv')
print(f"\nColumnas WC Revenue: {df_wc.columns.tolist()}")

# Parsear fecha
df_wc['Fecha'] = pd.to_datetime(df_wc['Fecha'])

# Filtrar solo Enero 2025
df_wc_jan = df_wc[
    (df_wc['Fecha'].dt.year == 2025) & 
    (df_wc['Fecha'].dt.month == 1)
].copy()

print(f"\n📊 WC REVENUE - ENERO 2025:")
print(f"   Total pedidos: {len(df_wc_jan)}")

# Identificar columna de total (puede ser 'Total neto' o similar)
total_col = None
for col in df_wc_jan.columns:
    if 'total' in col.lower() or 'neto' in col.lower():
        total_col = col
        break

if total_col:
    # Excluir cancelados si hay columna de estado
    status_col = None
    for col in df_wc_jan.columns:
        if 'estado' in col.lower() or 'status' in col.lower():
            status_col = col
            break
    
    if status_col:
        print(f"\n📋 Columna de estado: {status_col}")
        print(f"Estados únicos: {df_wc_jan[status_col].unique()}")
        
        # Excluir cancelados, failed, refunded
        INVALID = ['Cancelado', 'Fallido', 'Reembolsado', 'Anulado']
        df_wc_valid = df_wc_jan[~df_wc_jan[status_col].isin(INVALID)]
        
        print(f"\n   Excluyendo estados inválidos: {len(df_wc_valid)} pedidos")
        total_wc = df_wc_valid[total_col].sum()
    else:
        df_wc_valid = df_wc_jan
        total_wc = df_wc_jan[total_col].sum()
    
    print(f"   💰 Total WC Revenue: ${total_wc:,.0f}")
    
    # Ver estados y totales
    if status_col:
        print(f"\n📋 Desglose por estado (WC Revenue):")
        for status in df_wc_valid[status_col].unique():
            df_status = df_wc_valid[df_wc_valid[status_col] == status]
            count = len(df_status)
            status_total = df_status[total_col].sum()
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
print(f"   Total pedidos extraídos: {len(df_api)}")
print(f"   💰 Total API (todos): ${df_api['total'].sum():,.0f}")

# Aplicar filtro actual de la API
VALID_API = ['completed', 'completoenviado', 'processing', 'porsalir']
df_api_filtered = df_api[df_api['status'].isin(VALID_API)]
print(f"   Con filtro actual ({', '.join(VALID_API)}): {len(df_api_filtered)} pedidos")
print(f"   💰 Total API (filtrado): ${df_api_filtered['total'].sum():,.0f}")

# Ver estados en API
print(f"\n📋 Desglose por estado (API - todos):")
for status in df_api['status'].unique():
    df_status = df_api[df_api['status'] == status]
    count = len(df_status)
    status_total = df_status['total'].sum()
    in_filter = "✅" if status in VALID_API else "❌"
    print(f"   {in_filter} {status}: {count} pedidos = ${status_total:,.0f}")

# 3. Comparación
print("\n" + "="*80)
print("RESULTADO:")
print("="*80)
if total_col:
    print(f"WC Revenue (válidos): ${total_wc:,.0f}")
    print(f"API (filtrado actual): ${df_api_filtered['total'].sum():,.0f}")
    diff = total_wc - df_api_filtered['total'].sum()
    print(f"DIFERENCIA:           ${diff:,.0f}")
    
    if abs(diff) < 1000:
        print("\n✅ ¡LOS DATOS COINCIDEN!")
    else:
        print(f"\n❌ DISCREPANCIA DE ${abs(diff):,.0f}")
        print("\n💡 Revisar qué estados usa WooCommerce vs nuestro filtro API")
