"""
PRUEBA OPCION 2: Usar date_paid en lugar de date_created
Verificar si nos acerca a los valores de WC CSV
"""
import pandas as pd
import sqlite3

# Cargar WC CSV para referencia
df_wc = pd.read_csv("wc-revenue-report-export-17661192702824.csv")
df_wc['Fecha'] = pd.to_datetime(df_wc['Fecha'])
df_wc['Ventas totales'] = pd.to_numeric(df_wc['Ventas totales'], errors='coerce').fillna(0)
df_wc['Pedidos'] = pd.to_numeric(df_wc['Pedidos'], errors='coerce').fillna(0)

df_2025_wc = df_wc[(df_wc['Fecha'] >= '2025-01-01') & (df_wc['Fecha'] < '2026-01-01')]
df_2024_wc = df_wc[(df_wc['Fecha'] >= '2024-01-01') & (df_wc['Fecha'] < '2025-01-01')]

wc_2025 = df_2025_wc['Ventas totales'].sum()
wc_2024 = df_2024_wc['Ventas totales'].sum()
wc_2025_ped = int(df_2025_wc['Pedidos'].sum())
wc_2024_ped = int(df_2024_wc['Pedidos'].sum())

print("="*80)
print("COMPARACION: date_created VS date_paid VS WC CSV")
print("="*80)

conn = sqlite3.connect('data/woocommerce.db')

# METODO ACTUAL (date_created)
print("\n1. METODO ACTUAL (date_created):")
print("-"*80)

for year in [2024, 2025]:
    q = f"""
    SELECT COUNT(*) as pedidos, SUM(total) as ventas
    FROM wc_orders
    WHERE strftime('%Y', date_created) = '{year}'
    AND status IN ('completed', 'completoenviado', 'processing', 'porsalir')
    """
    r = pd.read_sql(q, conn).iloc[0]
    
    wc_val = wc_2024 if year == 2024 else wc_2025
    wc_ped = wc_2024_ped if year == 2024 else wc_2025_ped
    diff_v = r['ventas'] - wc_val
    diff_p = r['pedidos'] - wc_ped
    
    print(f"{year}: ${r['ventas']:>15,.0f} ({r['pedidos']:>3} ped) | Diff: ${diff_v:>+15,.0f} ({diff_p:+d} ped)")

# METODO PROPUESTO (date_paid)
print("\n2. METODO PROPUESTO (date_paid):")
print("-"*80)

for year in [2024, 2025]:
    q = f"""
    SELECT COUNT(*) as pedidos, COALESCE(SUM(total), 0) as ventas
    FROM wc_orders
    WHERE strftime('%Y', date_paid) = '{year}'
    AND date_paid IS NOT NULL
    AND status IN ('completed', 'completoenviado', 'processing', 'porsalir')
    """
    r = pd.read_sql(q, conn).iloc[0]
    
    wc_val = wc_2024 if year == 2024 else wc_2025
    wc_ped = wc_2024_ped if year == 2024 else wc_2025_ped
    ventas = r['ventas'] if r['ventas'] else 0
    pedidos = r['pedidos'] if r['pedidos'] else 0
    diff_v = ventas - wc_val
    diff_p = pedidos - wc_ped
    
    print(f"{year}: ${ventas:>15,.0f} ({pedidos:>3} ped) | Diff: ${diff_v:>+15,.0f} ({diff_p:+d} ped)")

# WC CSV (REFERENCIA)
print("\n3. WC CSV (FUENTE DE VERDAD):")
print("-"*80)
print(f"2024: ${wc_2024:>15,.0f} ({wc_2024_ped:>3} ped)")
print(f"2025: ${wc_2025:>15,.0f} ({wc_2025_ped:>3} ped)")

# RESUMEN
print("\n" + "="*80)
print("RESUMEN DE DIFERENCIAS")
print("="*80)

# Calcular para 2025
q_created = """
SELECT SUM(total) as v FROM wc_orders 
WHERE strftime('%Y', date_created) = '2025'
AND status IN ('completed', 'completoenviado', 'processing', 'porsalir')
"""
created_2025 = pd.read_sql(q_created, conn).iloc[0]['v']

q_paid = """
SELECT SUM(total) as v FROM wc_orders 
WHERE strftime('%Y', date_paid) = '2025'
AND date_paid IS NOT NULL
AND status IN ('completed', 'completoenviado', 'processing', 'porsalir')
"""
paid_2025 = pd.read_sql(q_paid, conn).iloc[0]['v']
paid_2025 = paid_2025 if paid_2025 else 0

diff_created = abs(created_2025 - wc_2025)
diff_paid = abs(paid_2025 - wc_2025)

print(f"\n2025:")
print(f"  date_created diferencia: ${diff_created:>15,.0f}")
print(f"  date_paid diferencia:    ${diff_paid:>15,.0f}")

if diff_paid < diff_created:
    mejora = diff_created - diff_paid
    porcentaje = (mejora / diff_created) * 100
    print(f"\n  ✅ date_paid es MEJOR por: ${mejora:>15,.0f} ({porcentaje:.1f}% mejor)")
else:
    print(f"\n  ❌ date_paid es PEOR")

# Calcular para 2024
q_created = """
SELECT SUM(total) as v FROM wc_orders 
WHERE strftime('%Y', date_created) = '2024'
AND status IN ('completed', 'completoenviado', 'processing', 'porsalir')
"""
created_2024 = pd.read_sql(q_created, conn).iloc[0]['v']

q_paid = """
SELECT SUM(total) as v FROM wc_orders 
WHERE strftime('%Y', date_paid) = '2024'
AND date_paid IS NOT NULL  
AND status IN ('completed', 'completoenviado', 'processing', 'porsalir')
"""
paid_2024 = pd.read_sql(q_paid, conn).iloc[0]['v']
paid_2024 = paid_2024 if paid_2024 else 0

diff_created_2024 = abs(created_2024 - wc_2024)
diff_paid_2024 = abs(paid_2024 - wc_2024)

print(f"\n2024:")
print(f"  date_created diferencia: ${diff_created_2024:>15,.0f}")
print(f"  date_paid diferencia:    ${diff_paid_2024:>15,.0f}")

if diff_paid_2024 < diff_created_2024:
    mejora = diff_created_2024 - diff_paid_2024
    porcentaje = (mejora / diff_created_2024) * 100 if diff_created_2024 > 0 else 0
    print(f"\n  ✅ date_paid es MEJOR por: ${mejora:>15,.0f} ({porcentaje:.1f}% mejor)")
else:
    print(f"\n  ❌ date_paid es PEOR")

print("\n" + "="*80)
print("CONCLUSION")
print("="*80)
if diff_paid < diff_created and diff_paid_2024 < diff_created_2024:
    print("✅ USAR date_paid nos acerca MAS a los valores de WC CSV")
    print("   RECOMENDACION: Cambiar el dashboard para usar date_paid")
elif paid_2025 == 0:
    print("⚠️  date_paid tiene muy pocos datos (posiblemente solo 1 pedido)")
    print("   Esto sugiere que la mayoría de pedidos NO tienen date_paid registrado")
    print("   WC CSV debe estar usando otro criterio, no solo date_paid")
else:
    print("❌ date_paid NO mejora la precisión")
    print("   El problema es otro, no el campo de fecha")

conn.close()
