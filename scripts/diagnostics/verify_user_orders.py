import sqlite3

conn = sqlite3.connect('data/woocommerce.db')
cur = conn.cursor()

# IDs que el usuario menciona
wc_orders = [17409, 17408, 17407, 17406]

print("="*70)
print("VERIFICACIÓN DE PEDIDOS MENCIONADOS POR EL USUARIO:")
print("="*70)

found = []
missing = []

for order_id in wc_orders:
    cur.execute('SELECT order_id, date_created, status, total FROM wc_orders WHERE order_id = ?', (order_id,))
    row = cur.fetchone()
    
    if row:
        print(f"✅ #{row[0]}: {row[1]} | {row[2]} | ${row[3]:,.0f}")
        found.append(row)
    else:
        print(f"❌ #{order_id}: NO ENCONTRADO")
        missing.append(order_id)

if found:
    total_found = sum([r[3] for r in found])
    print(f"\n💰 Total pedidos encontrados: ${total_found:,.0f}")

if missing:
    print(f"\n⚠️ Faltan {len(missing)} pedidos: {missing}")

# Ver todos los pedidos de Ene 30-31
print("\n" + "="*70)
print("TODOS LOS PEDIDOS 30-31 ENERO EN BD:")
print("="*70)

cur.execute('''
    SELECT order_id, DATE(date_created), status, total
    FROM wc_orders  
    WHERE DATE(date_created) IN ('2025-01-30', '2025-01-31')
    ORDER BY date_created DESC, order_id DESC
''')

all_orders = cur.fetchall()
total_all = 0

for r in all_orders:
    print(f"#{r[0]:5d} | {r[1]} | {r[2]:20s} | ${r[3]:10,.0f}")
    total_all += r[3]

print("="*70)
print(f"TOTAL 30-31 Ene: ${total_all:,.0f}")

# Calcular lo que debería ser según WooCommerce
wc_total = 100510 + 20000 + 26150 + 72780
print(f"\nSegún pedidos del usuario: ${wc_total:,.0f}")
print(f"Diferencia: ${abs(total_all - wc_total):,.0f}")

conn.close()
