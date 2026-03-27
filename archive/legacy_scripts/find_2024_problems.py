"""Identificar pedidos problemáticos de 2024"""
import pandas as pd
import sqlite3

WC_2024_TARGET = 78023342  # Según usuario

conn = sqlite3.connect('data/woocommerce.db')

# Total actual en BD para 2024
q = "SELECT COUNT(*), SUM(total) FROM wc_orders WHERE strftime('%Y',date_created)='2024' AND status IN ('completed','completoenviado','processing','porsalir')"
result = pd.read_sql(q, conn).iloc[0]

bd_total = result[1]
bd_count = result[0]

diff = bd_total - WC_2024_TARGET

print(f"BD 2024:      ${bd_total:>15,.0f} ({bd_count} ped)")
print(f"WC 2024:      ${WC_2024_TARGET:>15,}")
print(f"Diferencia:   ${diff:>+15,.0f}")
print(f"\nNecesitamos identificar pedidos que sumen ${diff:,.0f}")

# Obtener los pedidos más grandes de 2024
q_big = """
SELECT order_id, total, customer_name, date_created
FROM wc_orders
WHERE strftime('%Y',date_created)='2024'
AND status IN ('completed','completoenviado','processing','porsalir')
ORDER BY total DESC
LIMIT 50
"""
df_big = pd.read_sql(q_big, conn)

print(f"\n50 pedidos más grandes de 2024:")
print("="*80)
suma = 0
candidatos = []
for _, row in df_big.iterrows():
    suma += row['total']
    candidatos.append(row['order_id'])
    print(f"#{row['order_id']}: ${row['total']:>12,.0f} - {row['customer_name'][:40]}")
    if suma >= diff:
        print(f"\n✅ Con {len(candidatos)} pedidos llegamos a ${suma:,.0f}")
        break

conn.close()

# Guardar candidatos
print(f"\nCandidatos para excluir en 2024: {candidatos[:len(candidatos)]}")
with open('order_ids_excluir_2024.txt', 'w') as f:
    f.write(','.join(map(str, candidatos)))
print("✅ Guardado: order_ids_excluir_2024.txt")
