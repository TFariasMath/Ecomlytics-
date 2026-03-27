"""
Analizar CSV de WooCommerce y comparar con Base de Datos
"""
import pandas as pd
import sqlite3

# Cargar CSV de WooCommerce
csv_path = "wc-revenue-report-export-17661192702824.csv"
df_wc = pd.read_csv(csv_path, encoding='utf-8')

# Convertir columnas numericas removiendo comas
numeric_cols = ['Pedidos', 'Ventas brutas', 'Devoluciones', 'Cupones', 'Ventas netas', 'Impuestos', 'Envío', 'Ventas totales']
for col in numeric_cols:
    df_wc[col] = pd.to_numeric(df_wc[col].astype(str).str.replace(',', ''), errors='coerce').fillna(0)

# Limpiar datos
df_wc['Fecha'] = pd.to_datetime(df_wc['Fecha'])
df_wc['year'] = df_wc['Fecha'].dt.year

# Calcular totales por año
print("="*80)
print("ANALISIS DE CSV DE WOOCOMMERCE")
print("="*80)

for year in [2024, 2025]:
    df_year = df_wc[df_wc['year'] == year]
    
    total_pedidos = int(df_year['Pedidos'].sum())
    ventas_brutas = df_year['Ventas brutas'].sum()
    ventas_netas = df_year['Ventas netas'].sum()
    envio = df_year['Envío'].sum()
    ventas_totales = df_year['Ventas totales'].sum()
    devoluciones = df_year['Devoluciones'].sum()
    cupones = df_year['Cupones'].sum()
    
    print(f"\n{year}:")
    print(f"  Pedidos:        {total_pedidos:>8,}")
    print(f"  Ventas brutas:  ${ventas_brutas:>12,.0f}")
    print(f"  Devoluciones:   ${devoluciones:>12,.0f}")
    print(f"  Cupones:        ${cupones:>12,.0f}")
    print(f"  Ventas netas:   ${ventas_netas:>12,.0f}")
    print(f"  Envío:          ${envio:>12,.0f}")  
    print(f"  VENTAS TOTALES: ${ventas_totales:>12,.0f}")

# Comparar con BD
print("\n" + "="*80)
print("COMPARACION CON BASE DE DATOS")
print("="*80)

conn = sqlite3.connect('data/woocommerce.db')

for year in [2024, 2025]:
    query = f"""
    SELECT 
        COUNT(*) as pedidos,
        SUM(total) as total_bd
    FROM wc_orders
    WHERE strftime('%Y', date_created) = '{year}'
    AND status IN ('completed', 'completoenviado', 'processing', 'porsalir')
    """
    df_bd = pd.read_sql(query, conn)
    
    # Del CSV
    df_year = df_wc[df_wc['year'] == year]
    wc_ventas = df_year['Ventas totales'].sum()
    wc_pedidos = int(df_year['Pedidos'].sum())
    
    bd_ventas = df_bd['total_bd'].iloc[0]
    bd_pedidos = df_bd['pedidos'].iloc[0]
    
    print(f"\n{year}:")
    print(f"  WC CSV Ventas:  ${wc_ventas:>15,.0f}  ({wc_pedidos} pedidos)")
    print(f"  BD Ventas:      ${bd_ventas:>15,.0f}  ({bd_pedidos} pedidos)")
    print(f"  Diferencia:     ${bd_ventas - wc_ventas:>+15,.0f}  ({bd_pedidos - wc_pedidos:+d} pedidos)")

conn.close()
