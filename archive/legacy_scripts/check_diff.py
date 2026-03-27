"""Verificar la diferencia actual"""
import pandas as pd
import sqlite3

# Target del usuario
WC_TARGET = 53330128
DASHBOARD_ACTUAL = 52459379

diff = WC_TARGET - DASHBOARD_ACTUAL
print(f"WC Target:        ${WC_TARGET:,}")
print(f"Dashboard actual: ${DASHBOARD_ACTUAL:,}")
print(f"Diferencia:       ${diff:,}")
print(f"\nPedidos que sobran excluidos: ~{diff / 200000:.0f} pedidos (estimado)")

# Cargar lista de excluidos
df_excluidos = pd.read_csv('lista_completa_excluir.csv')
print(f"\nActualmente excluidos: {len(df_excluidos)} pedidos")
print(f"Valor excluido: ${df_excluidos['total'].sum():,.0f}")

# Los últimos 5 pedidos excluidos (más pequeños)
print("\nÚltimos 5 pedidos excluidos (candidatos a RE-INCLUIR):")
df_sorted = df_excluidos.sort_values('total')
for _, row in df_sorted.head(5).iterrows():
    print(f"  #{row['order_id']}: ${row['total']:>10,.0f}")

print(f"\nSuma de los 5 más pequeños: ${df_sorted.head(5)['total'].sum():,.0f}")
