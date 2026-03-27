import sqlite3

conn = sqlite3.connect('data/woocommerce.db')
cursor = conn.cursor()

# Test SIN on-hold
cursor.execute("""
SELECT SUM(total) as total
FROM wc_orders
WHERE strftime('%Y-%m', date_created) = '2025-01'
AND status IN ('completed', 'completoenviado', 'processing', 'porsalir')
""")

total_sin_onhold = cursor.fetchone()[0]

print("="*70)
print("ENERO 2025 - TEST SIN ON-HOLD:")
print("="*70)
print(f"Total SIN on-hold: ${total_sin_onhold:,.0f}")
print(f"WooCommerce:       $4,583,859")
print(f"Diferencia:        ${abs(total_sin_onhold - 4583859):,.0f}")
print("="*70)

if abs(total_sin_onhold - 4583859) < 1000:
    print("✅ COINCIDE! El problema ERA on-hold")
else:
    print("❌ AÚN NO COINCIDE - hay otro problema")

conn.close()
