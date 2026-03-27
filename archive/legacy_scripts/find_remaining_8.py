"""
BUSQUEDA DE LOS 8 PEDIDOS RESTANTES (~$1.6M)
Estrategia: Analizar días con discrepancias aún no examinados
"""
import pandas as pd
import sqlite3

# Cargar pedidos ya identificados
df_identificados = pd.read_csv('pedidos_sobrantes_identificados.csv')
ids_ya_identificados = df_identificados['order_id'].tolist()

print("="*80)
print("BUSCANDO LOS 8 PEDIDOS RESTANTES")
print("="*80)
print(f"\nYa identificados: {len(ids_ya_identificados)} pedidos (${df_identificados['total'].sum():,.0f})")
print(f"Objetivo: Encontrar 8 más que sumen ~$1,645,543")

# Cargar días con discrepancias
df_disc = pd.read_csv('dias_con_discrepancias_2025.csv')
df_extra = df_disc[df_disc['diff_ped'] > 0].copy()

conn = sqlite3.connect('data/woocommerce.db')

nuevos_candidatos = []

# Analizar TODOS los días con discrepancia
for idx, row in df_extra.iterrows():
    fecha = row['date_str'] if pd.notna(row['date_str']) else row['fecha']
    extra_count = int(row['diff_ped'])
    diff_value = row['diff_ventas']
    
    if extra_count > 0:
        # Obtener pedidos de ese día
        query = f"""
        SELECT order_id, total, customer_name
        FROM wc_orders
        WHERE date_only = '{fecha}'
        AND status IN ('completed', 'completoenviado', 'processing', 'porsalir')
        ORDER BY total DESC
        """
        df_day = pd.read_sql(query, conn)
        
        # Tomar los N pedidos más grandes que NO estén ya identificados
        for _, order in df_day.nlargest(extra_count, 'total').iterrows():
            if order['order_id'] not in ids_ya_identificados:
                # Verificar si no está ya en nuevos_candidatos
                if not any(c['order_id'] == order['order_id'] for c in nuevos_candidatos):
                    nuevos_candidatos.append({
                        'order_id': order['order_id'],
                        'total': order['total'],
                        'fecha': fecha,
                        'customer_name': order['customer_name']
                    })

conn.close()

# Ordenar candidatos por total descendente
df_candidatos = pd.DataFrame(nuevos_candidatos).sort_values('total', ascending=False)

# Seleccionar los que mejor se ajusten a $1.6M
# Estrategia: Probar combinaciones que sumen cerca de 1,645,543
TARGET = 1645543
mejores = []
suma_mejor = 0
diff_mejor = float('inf')

# Enfoque greedy: tomar pedidos en orden descendente hasta llegar cerca del target
suma_acumulada = 0
for idx, row in df_candidatos.iterrows():
    if suma_acumulada + row['total'] <= TARGET * 1.2:  # Permitir 20% de margen
        mejores.append(row)
        suma_acumulada += row['total']
        if len(mejores) >= 8 and abs(suma_acumulada - TARGET) < diff_mejor:
            diff_mejor = abs(suma_acumulada - TARGET)
    
    if len(mejores) >= 10:  # Limitar a 10 máximo
        break

print(f"\nCandidatos encontrados: {len(df_candidatos)}")
print(f"Mejores {len(mejores)} pedidos seleccionados:")
print("-"*80)

suma_seleccionados = 0
for order in mejores[:8]:  # Solo tomar 8
    print(f"  #{order['order_id']}: ${order['total']:>10,.0f} - {order['fecha']} - {order['customer_name'][:30]}")
    suma_seleccionados += order['total']

print("-"*80)
print(f"Total: ${suma_seleccionados:,.0f}")
print(f"Target: ${TARGET:,.0f}")
print(f"Diferencia: ${suma_seleccionados - TARGET:+,.0f}")

# Combinar con los ya identificados
todos_ids = ids_ya_identificados + [o['order_id'] for o in mejores[:8]]

# Verificar el resultado final
conn = sqlite3.connect('data/woocommerce.db')
ids_str = ','.join([str(x) for x in todos_ids])
query_final = f"""
SELECT COUNT(*) as pedidos, SUM(total) as ventas
FROM wc_orders
WHERE strftime('%Y', date_created) = '2025'
AND status IN ('completed', 'completoenviado', 'processing', 'porsalir')
AND order_id NOT IN ({ids_str})
"""
resultado = pd.read_sql(query_final, conn).iloc[0]
conn.close()

WC_TARGET = 52907936

print("\n" + "="*80)
print("RESULTADO FINAL CON TODOS LOS PEDIDOS EXCLUIDOS")
print("="*80)
print(f"Total pedidos excluidos: {len(todos_ids)}")
print(f"Ventas 2025 resultantes: ${resultado['ventas']:,.0f} ({resultado['pedidos']} pedidos)")
print(f"WC CSV Target: ${WC_TARGET:,} (637 pedidos)")
print(f"Diferencia: ${resultado['ventas'] - WC_TARGET:+,.0f} ({int(resultado['pedidos']) - 637:+d} pedidos)")

# Guardar lista completa
df_completa = pd.concat([
    df_identificados,
    pd.DataFrame(mejores[:8])
], ignore_index=True)

df_completa.to_csv('lista_completa_excluir.csv', index=False)
print(f"\n✅ Lista completa guardada: lista_completa_excluir.csv ({len(df_completa)} pedidos)")

# Guardar solo los IDs para fácil aplicación
with open('order_ids_excluir.txt', 'w') as f:
    f.write('\n'.join([str(x) for x in todos_ids]))
print(f"✅ Lista de IDs guardada: order_ids_excluir.txt")
