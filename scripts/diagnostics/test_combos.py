import sqlite3

conn = sqlite3.connect('data/woocommerce.db')
cursor = conn.cursor()

# Test diferentes combinaciones
print("="*70)
print("ENERO 2025 - PRUEBA DE COMBINACIONES:")
print("="*70)

tests = [
    ("Solo completed + completoenviado", 
     "completed,completoenviado"),
    ("completed + completoenviado + processing", 
     "completed,completoenviado,processing"),
    ("completed + completoenviado + processing + porsalir",
     "completed,completoenviado,processing,porsalir"),
]

target = 4583859

for name, statuses in tests:
    cursor.execute(f"""
    SELECT SUM(total) FROM wc_orders
    WHERE strftime('%Y-%m', date_created) = '2025-01'
    AND status IN ({','.join(['?' for _ in statuses.split(',')])})
    """, statuses.split(','))
    
    total = cursor.fetchone()[0] or 0
    diff = abs(total - target)
    match = "✅ MATCH!" if diff < 1000 else f"Diff: ${diff:,.0f}"
    
    print(f"\n{name}:")
    print(f"  ${total:,.0f} - {match}")

print("\n" + "="*70)
print(f"Objetivo WooCommerce: ${target:,.0f}")
print("="*70)

conn.close()
