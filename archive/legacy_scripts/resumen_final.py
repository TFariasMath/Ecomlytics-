import pandas as pd
import sqlite3

# Cargar lista de pedidos a excluir
df_exclude = pd.read_csv('pedidos_sobrantes_identificados.csv')
order_ids = df_exclude['order_id'].tolist()

conn = sqlite3.connect('data/woocommerce.db')

# Calcular ventas actuales
q_actual = "SELECT COUNT(*), SUM(total) FROM wc_orders WHERE strftime('%Y',date_created)='2025' AND status IN ('completed','completoenviado','processing','porsalir')"
actual = pd.read_sql(q_actual, conn).iloc[0]

# Calcular SIN los 37 pedidos
ids_str = ','.join([str(x) for x in order_ids])
q_sin = f"SELECT COUNT(*), SUM(total) FROM wc_orders WHERE strftime('%Y',date_created)='2025' AND status IN ('completed','completoenviado','processing','porsalir') AND order_id NOT IN ({ids_str})"
sin_excluir = pd.read_sql(q_sin, conn).iloc[0]

conn.close()

WC_TARGET = 52907936

print("RESUMEN FINAL")
print("="*70)
print(f"\nActual (682 ped):              ${actual[1]:>15,.0f}")
print(f"Excluir 37 ped identificados:  ${df_exclude['total'].sum():>15,.0f}")
print(f"Resultado (645 ped):           ${sin_excluir[1]:>15,.0f}")
print(f"\nWC CSV Target (637 ped):       ${WC_TARGET:>15,}")
print(f"Diferencia remanente:          ${sin_excluir[1] - WC_TARGET:>+15,.0f}")
print(f"\nPedidos faltantes: {int(sin_excluir[0])} - 637 = {int(sin_excluir[0]) - 637}")
print(f"Valor faltante: ~${sin_excluir[1] - WC_TARGET:,.0f}")
