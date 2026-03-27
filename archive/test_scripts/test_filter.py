"""
PRUEBA: Aplicar filtro customer_id != 0 y comparar con WC CSV
"""
import pandas as pd
import sqlite3

WC_2025 = 52907936
WC_2024 = 78037182

conn = sqlite3.connect('data/woocommerce.db')

print("="*80)
print("PRUEBA DE FILTRO: Excluir customer_id = 0")
print("="*80)

# Original (sin filtro)
print("\n1. SIN FILTRO (actual):")
for year in [2024, 2025]:
    q = f"""
    SELECT COUNT(*) as p, SUM(total) as v
    FROM wc_orders
    WHERE strftime('%Y', date_created) = '{year}'
    AND status IN ('completed', 'completoenviado', 'processing', 'porsalir')
    """
    r = pd.read_sql(q, conn).iloc[0]
    wc = WC_2024 if year == 2024 else WC_2025
    diff = r['v'] - wc
    print(f"  {year}: ${r['v']:>15,.0f} ({r['p']:>3} ped) | Diff: ${diff:>+15,.0f}")

# CON FILTRO customer_id != 0
print("\n2. CON FILTRO (customer_id != 0):")
for year in [2024, 2025]:
    q = f"""
    SELECT COUNT(*) as p, SUM(total) as v
    FROM wc_orders
    WHERE strftime('%Y', date_created) = '{year}'
    AND status IN ('completed', 'completoenviado', 'processing', 'porsalir')
    AND customer_id != 0
    """
    r = pd.read_sql(q, conn).iloc[0]
    wc = WC_2024 if year == 2024 else WC_2025
    diff = r['v'] - wc
    print(f"  {year}: ${r['v']:>15,.0f} ({r['p']:>3} ped) | Diff: ${diff:>+15,.0f}")

# WC CSV
print("\n3. WC CSV (TARGET):")
print(f"  2024: ${WC_2024:>15,} (986 ped)")
print(f"  2025: ${WC_2025:>15,} (637 ped)")

conn.close()

print("\n" + "="*80)
print("ANALISIS")
print("="*80)
print("Si el filtro customer_id != 0 nos acerca significativamente,")
print("entonces podemos aplicarlo en el dashboard.")
