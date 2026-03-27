"""
Análisis comparativo entre WC Revenue Export y datos extraídos por API.
"""

import pandas as pd
import sqlite3
from datetime import datetime

print("="*70)
print("ANÁLISIS COMPARATIVO: WC REVENUE vs API EXTRACTION")
print("="*70)

# 1. Cargar WC Revenue Export
try:
    # Buscar el archivo
    import glob
    wc_files = glob.glob('**/wc-revenue*.csv', recursive=True)
    
    if not wc_files:
        print("\n❌ No se encontró archivo WC Revenue")
        exit(1)
    
    wc_file = wc_files[0]
    print(f"\n📂 Archivo WC Revenue: {wc_file}")
    
    df_wc = pd.read_csv(wc_file)
    print(f"✅ Cargado: {len(df_wc)} filas")
    print(f"\nColumnas: {df_wc.columns.tolist()}")
    
    # Mostrar primeras filas
    print("\n" + "="*70)
    print("MUESTRA DE DATOS WC REVENUE:")
    print("="*70)
    print(df_wc.head(10).to_string())
    
    # Intentar identificar columnas clave
    print("\n" + "="*70)
    print("ESTRUCTURA DEL ARCHIVO:")
    print("="*70)
    print(df_wc.info())
    
except Exception as e:
    print(f"\n❌ Error cargando WC Revenue: {e}")
    import traceback
    traceback.print_exc()
