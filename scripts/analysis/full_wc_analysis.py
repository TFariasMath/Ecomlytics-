"""
Análisis completo del WC Revenue Export
"""

import pandas as pd
import sqlite3

print("="*70)
print("1. ANÁLISIS WC REVENUE EXPORT")
print("="*70)

# Cargar WC Revenue
df_wc = pd.read_csv('wc-revenue-report-export-17660892507145.csv')

print(f"\n📊 Total filas: {len(df_wc)}")
print(f"\n📋 Columnas:")
for i, col in enumerate(df_wc.columns, 1):
    print(f"  {i}. {col}")

# Mostrar primeras filas
print("\n" + "="*70)
print("PRIMERAS 10 FILAS:")
print("="*70)
print(df_wc.head(10))

# Verificar 31 enero
print("\n" + "="*70)
print("ENERO 31, 2025:")
print("="*70)

# Intentar encontrar la columna de fecha
date_col = None
for col in df_wc.columns:
    if 'date' in col.lower() or 'fecha' in col.lower():
        date_col = col
        break

if date_col:
    df_wc[date_col] = pd.to_datetime(df_wc[date_col], errors='coerce')
    df_jan31 = df_wc[df_wc[date_col].dt.date == pd.to_datetime('2025-01-31').date()]
    
    print(f"\n📦 Pedidos del 31 enero: {len(df_jan31)}")
    if not df_jan31.empty:
        # Buscar columna de total/revenue
        for col in ['total', 'revenue', 'net', 'Total', 'Revenue']:
            if col in df_jan31.columns:
                total = df_jan31[col].astype(float).sum()
                print(f"💰 Total {col}: ${total:,.0f}")
        
        print("\nDetalle:")
        print(df_jan31.to_string())
else:
    print("\n⚠️ No se encontró columna de fecha")

# Ver resumen de estados si existe
if 'status' in df_wc.columns or 'Status' in df_wc.columns:
    status_col = 'status' if 'status' in df_wc.columns else 'Status'
    print("\n" + "="*70)
    print("RESUMEN POR ESTADO:")
    print("="*70)
    print(df_wc[status_col].value_counts())
