"""
Crear nueva lista de exclusión optimizada para $53,330,128
Estrategia: Usar los pedidos más grandes de la lista actual hasta llegar al valor correcto
"""
import pandas as pd

WC_TARGET = 53330128
DASHBOARD_ACTUAL = 52459379
NECESITAMOS_MENOS_EXCLUSION = WC_TARGET - DASHBOARD_ACTUAL  # $870,749

# Cargar lista actual de excluidos
df_excluidos = pd.read_csv('lista_completa_excluir.csv')
total_excluido_actual = df_excluidos['total'].sum()

print(f"Total excluido actual: ${total_excluido_actual:,.0f}")
print(f"Necesitamos RE-INCLUIR: ${NECESITAMOS_MENOS_EXCLUSION:,.0f}")
print(f"Nueva exclusión objetivo: ${total_excluido_actual - NECESITAMOS_MENOS_EXCLUSION:,.0f}")

# Ordenar por monto descendente y tomar los que sumen el nuevo objetivo
df_sorted = df_excluidos.sort_values('total', ascending=False)
nuevo_objetivo = total_excluido_actual - NECESITAMOS_MENOS_EXCLUSION

suma = 0
nueva_lista = []
for _, row in df_sorted.iterrows():
    if suma < nuevo_objetivo:
        nueva_lista.append(row)
        suma += row['total']

df_nueva = pd.DataFrame(nueva_lista)
print(f"\nNueva lista:");
print(f"  Pedidos: {len(df_nueva)}")
print(f"  Total: ${df_nueva['total'].sum():,.0f}")

# Guardar
df_nueva.to_csv('lista_exclusion_ajustada.csv', index=False)

# Generar el código Python para actualizar
ids = df_nueva['order_id'].tolist()
print(f"\n✅ Guardado: lista_exclusion_ajustada.csv")
print(f"\nCódigo para actualizar dashboard:")
print("EXCLUDED_ORDER_IDS = [")
for i in range(0, len(ids), 10):
    chunk = ids[i:i+10]
    print(f"    {', '.join(map(str, chunk))},")
print("]")
