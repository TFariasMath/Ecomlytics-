import sqlite3

conn = sqlite3.connect('data/woocommerce.db')
cur = conn.cursor()

# Verificar si tenemos los pedidos específicos de WooCommerce
print("="*70)
print("VERIFICACIÓN POST-ETL:")
print("="*70)

cur.execute('SELECT order_id, date_created, status, total FROM wc_orders WHERE order_id IN (17409, 17408)')
rows = cur.fetchall()

if rows:
    print("\n✅ ¡PEDIDOS ENCONTRADOS!")
    for r in rows:
        print(f"   #{r[0]} | {r[1]} | {r[2]} | ${r[3]:,.0f}")
else:
    print("\n❌ Pedidos #17409 y #17408 NO encontrados")

# Ver Enero 31
cur.execute('SELECT order_id, status, total FROM wc_orders WHERE DATE(date_created) = "2025-01-31" ORDER BY order_id DESC')
jan31 = cur.fetchall()

print(f"\n31 ENERO 2025: {len(jan31)} pedidos")
for r in jan31:
    print(f"   #{r[0]} | {r[1]} | ${r[2]:,.0f}")

if jan31:
    total_31 = sum([r[2] for r in jan31])
    print(f"\n💰 Total 31 Ene: ${total_31:,.0f}")
    print(f"   WooCommerce: $193,290")
    if abs(total_31 - 193290) < 1000:
        print("   ✅ ¡COINCIDE!")
    else:
        print(f"   ❌ Diferencia: ${abs(total_31 - 193290):,.0f}")

conn.close()
