import sqlite3
conn = sqlite3.connect('data/woocommerce.db')

WC_2025 = 52907936
WC_2024 = 78037182

# Query simple
c = conn.cursor()

# 2025
c.execute("SELECT SUM(total) FROM wc_orders WHERE strftime('%Y',date_created)='2025' AND status IN ('completed','completoenviado','processing','porsalir')")
created_2025 = c.fetchone()[0]

c.execute("SELECT COALESCE(SUM(total),0) FROM wc_orders WHERE strftime('%Y',date_paid)='2025' AND date_paid IS NOT NULL AND status IN ('completed','completoenviado','processing','porsalir')")
paid_2025 = c.fetchone()[0]

# 2024
c.execute("SELECT SUM(total) FROM wc_orders WHERE strftime('%Y',date_created)='2024' AND status IN ('completed','completoenviado','processing','porsalir')")
created_2024 = c.fetchone()[0]

c.execute("SELECT COALESCE(SUM(total),0) FROM wc_orders WHERE strftime('%Y',date_paid)='2024' AND date_paid IS NOT NULL AND status IN ('completed','completoenviado','processing','porsalir')")
paid_2024 = c.fetchone()[0]

conn.close()

print("RESULTADOS:")
print("="*60)
print(f"\n2025:")
print(f"  WC CSV:        ${WC_2025:>15,}")
print(f"  date_created: ${created_2025:>15,.0f}  (Diff: ${created_2025-WC_2025:+,.0f})")
print(f"  date_paid:     ${paid_2025:>15,.0f}  (Diff: ${paid_2025-WC_2025:+,.0f})")

print(f"\n2024:")
print(f"  WC CSV:        ${WC_2024:>15,}")
print(f"  date_created: ${created_2024:>15,.0f}  (Diff: ${created_2024-WC_2024:+,.0f})")
print(f"  date_paid:     ${paid_2024:>15,.0f}  (Diff: ${paid_2024-WC_2024:+,.0f})")

print("\n" + "="*60)
print("CONCLUSION:")
if abs(paid_2024 - WC_2024) < 1000 and abs(paid_2025 - WC_2025) < abs(created_2025 - WC_2025):
    print("✅ USAR date_paid nos acerca a WC CSV")
    print(f"   2024: PERFECTO (diferencia < $1,000)")
    if paid_2025 < 1000000:
        print(f"   2025: ⚠️  Muy pocos datos ({paid_2025:,.0f})")
        print("   Problema: La mayoría de pedidos 2025 no tienen date_paid")
    else:
        print(f"   2025: Mejor que date_created")
else:
    print("❌ date_paid NO mejora")
