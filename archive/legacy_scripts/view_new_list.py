import pandas as pd

df = pd.read_csv('lista_exclusion_ajustada.csv')
print(f"Pedidos en nueva lista: {len(df)}")
print(f"Total a excluir: ${df['total'].sum():,.0f}")
print("\nIDs:")
print(df['order_id'].tolist())
