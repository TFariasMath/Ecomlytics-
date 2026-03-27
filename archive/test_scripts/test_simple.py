"""Prueba simple de date_paid"""
import pandas as pd
import sqlite3

conn = sqlite3.connect('data/woocommerce.db')

# WC CSV values (hardcoded from previous analysis)
wc_2025 = 52907936
wc_2024 = 78037182

print("COMPARACION date_created vs date_paid")
print("="*70)

# date_created (actual)
print("\n1. ACTUAL (date_created):")
for year in [2024, 2025]:
    q = f"SELECT COUNT(*) as p, SUM(total) as v FROM wc_orders WHERE strftime('%Y',date_created)='{year}' AND status IN ('completed','completoenviado','processing','porsalir')"
    r = pd.read_sql(q, conn).iloc[0]
    wc = wc_2024 if year == 2024 else wc_2025
    diff = r['v'] - wc
    print(f"  {year}: ${r['v']:>12,.0f} | Diff: ${diff:>+12,.0f}")

# date_paid (propuesto)
print("\n2. PROPUESTO (date_paid):")
for year in [2024, 2025]:
    q = f"SELECT COUNT(*) as p, COALESCE(SUM(total),0) as v FROM wc_orders WHERE strftime('%Y',COALESCE(date_paid,''))='{year}' AND date_paid IS NOT NULL AND status IN ('completed','completoenviado','processing','porsalir')"
    r = pd.read_sql(q, conn).iloc[0]
    wc = wc_2024 if year == 2024 else wc_2025
    diff = r['v'] - wc
    print(f"  {year}: ${r['v']:>12,.0f} | Diff: ${diff:>+12,.0f}")

# WC CSV
print("\n3. WC CSV:")
print(f"  2024: ${wc_2024:>12,}")
print(f"  2025: ${wc_2025:>12,}")

conn.close()

print("\nCONCLUSION:")
print("Si date_paid tiene valores cercanos a $0, significa que")
print("la mayoría de pedidos NO tienen date_paid registrado.")
