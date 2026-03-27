import sqlite3
import pandas as pd

conn = sqlite3.connect('data/woocommerce.db')

print("="*70)
print("ENERO 2025 - ANÁLISIS DETALLADO POR ESTADO:")
print("="*70)

# Ver TODOS los estados con sus totales
query = """
SELECT 
    status,
    COUNT(*) as cantidad,
    SUM(total) as total,
    GROUP_CONCAT(order_id) as order_ids
FROM wc_orders
WHERE strftime('%Y-%m', date_created) = '2025-01'
GROUP BY status
ORDER BY total DESC
"""

df = pd.read_sql(query, conn)

total_acumulado = 0
estados_probados = []

print("\nEstado               | Cantidad | Total        | Acumulado")
print("-"*70)

for _, row in df.iterrows():
    total_acumulado += row['total']
    estados_probados.append(row['status'])
    
    match_wc = "✅ MATCH!" if abs(total_acumulado - 4583859) < 1000 else ""
    
    print(f"{row['status']:20s} | {row['cantidad']:8d} | ${row['total']:11,.0f} | ${total_acumulado:11,.0f} {match_wc}")
    
    # Si encontramos el match, mostrar qué estados son
    if match_wc:
        print("\n" + "="*70)
        print(f"✅ ENCONTRADO! WooCommerce cuenta estos {len(estados_probados)} estados:")
        print(f"   {', '.join(estados_probados)}")
        print("="*70)
        break

print(f"\nWooCommerce objetivo: $4,583,859")

conn.close()
