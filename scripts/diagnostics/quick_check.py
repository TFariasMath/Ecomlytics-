import sqlite3

conn = sqlite3.connect('data/woocommerce.db')
cursor = conn.cursor()

try:
    cursor.execute('SELECT COUNT(*) FROM wc_orders WHERE strftime("%Y", date_created) = "2025"')
    count_2025 = cursor.fetchone()[0]
    print(f'Pedidos 2025: {count_2025}')
    
    cursor.execute('SELECT SUM(total) FROM wc_orders WHERE strftime("%Y", date_created) = "2025" AND status IN ("completed", "completoenviado", "processing", "porsalir", "on-hold")')
    total_2025 = cursor.fetchone()[0]
    if total_2025:
        print(f'Total 2025 válido: ${total_2025:,.0f}')
    else:
        print('Total 2025 válido: $0')
except Exception as e:
    print(f'Error: {e}')
finally:
    conn.close()
