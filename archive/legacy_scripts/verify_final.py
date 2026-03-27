"""Verificar resultado final con la lista completa"""
import pandas as pd
import sqlite3

# Cargar lista completa
df_excluir = pd.read_csv('lista_completa_excluir.csv')
order_ids = df_excluir['order_id'].tolist()

conn = sqlite3.connect('data/woocommerce.db')

# Sin exclusión
q1 = "SELECT COUNT(*), SUM(total) FROM wc_orders WHERE strftime('%Y',date_created)='2025' AND status IN ('completed','completoenviado','processing','porsalir')"
sin_excluir = pd.read_sql(q1, conn).iloc[0]

# Con exclusión
ids_str = ','.join([str(x) for x in order_ids])
q2 = f"SELECT COUNT(*), SUM(total) FROM wc_orders WHERE strftime('%Y',date_created)='2025' AND status IN ('completed','completoenviado','processing','porsalir') AND order_id NOT IN ({ids_str})"
con_excluir = pd.read_sql(q2, conn).iloc[0]

conn.close()

WC = 52907936

print("VERIFICACION FINAL")
print("="*70)
print(f"\nSIN exclusión:  ${sin_excluir[1]:>15,.0f} ({int(sin_excluir[0])} ped)")
print(f"Pedidos excluir: {len(order_ids)} (${df_excluir['total'].sum():,.0f})")
print(f"CON exclusión:  ${con_excluir[1]:>15,.0f} ({int(con_excluir[0])} ped)")
print(f"\nWC CSV:         ${WC:>15,} (637 ped)")
print(f"Diferencia:     ${con_excluir[1] - WC:>+15,.0f} ({int(con_excluir[0]) - 637:+d} ped)")

if abs(con_excluir[1] - WC) < 100000:  # Menos de $100K de diferencia
    print("\n✅ EXCELENTE! Muy cerca del target WC CSV")
elif abs(con_excluir[1] - WC) < 500000:  # Menos de $500K
    print("\n✓ BUENO! Razonablemente cerca del target")
else:
    print("\n⚠️ Todavía hay diferencia significativa")
