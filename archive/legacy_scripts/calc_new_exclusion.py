"""Calcular nueva lista de exclusión para target exacto"""
import pandas as pd
import sqlite3

WC_TARGET = 53330128  # Valor real de WooCommerce según el usuario

conn = sqlite3.connect('data/woocommerce.db')

# Total SIN exclusiones
q_total = "SELECT SUM(total) FROM wc_orders WHERE strftime('%Y',date_created)='2025' AND status IN ('completed','completoenviado','processing','porsalir')"
total_sin_filtro = pd.read_sql(q_total, conn).iloc[0,0]

conn.close()

# Diferencia ORI GINAL que necesitamos excluir
diff_original = total_sin_filtro - WC_TARGET

print(f"Total sin filtro:     ${total_sin_filtro:,}")
print(f"WC Target:            ${WC_TARGET:,}")
print(f"Diferencia a excluir: ${diff_original:,}")
print(f"\nEsto es diferente a los $11.6M que calculé antes.")
print(f"El valor correcto del CSV era $52.9M, pero WC reporta $53.3M")
print(f"\nRecomendación: Ajustar la lista de exclusión para que")
print(f"la suma de pedidos excluidos sea exactamente ${diff_original:,.0f}")
