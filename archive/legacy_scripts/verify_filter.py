import sqlite3

conn = sqlite3.connect('data/woocommerce.db')
c = conn.cursor()

WC_2025 = 52907936

# Sin filtro
c.execute("SELECT SUM(total) FROM wc_orders WHERE strftime('%Y',date_created)='2025' AND status IN ('completed','completoenviado','processing','porsalir')")
sin_filtro = c.fetchone()[0]

# Con filtro customer_id != 0
c.execute("SELECT SUM(total) FROM wc_orders WHERE strftime('%Y',date_created)='2025' AND status IN ('completed','completoenviado','processing','porsalir') AND customer_id != 0")
con_filtro = c.fetchone()[0]

conn.close()

print(f"Sin filtro:     ${sin_filtro:,}")
print(f"Con filtro:     ${con_filtro:,}")
print(f"WC CSV target:  ${WC_2025:,}")
print(f"\nDiff sin filtro: ${abs(sin_filtro - WC_2025):,}")
print(f"Diff con filtro: ${abs(con_filtro - WC_2025):,}")

if abs(con_filtro - WC_2025) < abs(sin_filtro - WC_2025):
    mejora = abs(sin_filtro - WC_2025) - abs(con_filtro - WC_2025)
    print(f"\n✅ MEJORA: ${mejora:,}")
else:
    print("\n❌ NO MEJORA")
