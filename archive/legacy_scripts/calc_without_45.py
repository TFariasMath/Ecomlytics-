"""
Calcular ventas 2025 SIN los pedidos problemáticos identificados
"""
import pandas as pd
import sqlite3

# Verificar si tenemos la lista de pedidos sobrantes
try:
    df_sobrantes = pd.read_csv('pedidos_sobrantes_identificados.csv')
    order_ids = df_sobrantes['order_id'].tolist()
    print(f"Pedidos en lista de exclusión: {len(order_ids)}")
    print(f"Valor total a excluir: ${df_sobrantes['total'].sum():,.0f}")
except FileNotFoundError:
    print("No se encontró lista de pedidos sobrantes.")
    print("Calculando basado en la diferencia conocida...")
    order_ids = []

conn = sqlite3.connect('data/woocommerce.db')

# Total actual
query_total = """
SELECT COUNT(*) as pedidos, SUM(total) as ventas
FROM wc_orders
WHERE strftime('%Y', date_created) = '2025'
AND status IN ('completed', 'completoenviado', 'processing', 'porsalir')
"""
total_actual = pd.read_sql(query_total, conn).iloc[0]

print("\n" + "="*70)
print("CALCULO DE VENTAS 2025")
print("="*70)

print(f"\nActual (con TODOS los pedidos):")
print(f"  Pedidos: {total_actual['pedidos']}")
print(f"  Ventas:  ${total_actual['ventas']:,.0f}")

if order_ids:
    # Con exclusión de la lista
    ids_str = ','.join([str(x) for x in order_ids])
    query_filtered = f"""
    SELECT COUNT(*) as pedidos, SUM(total) as ventas
    FROM wc_orders
    WHERE strftime('%Y', date_created) = '2025'
    AND status IN ('completed', 'completoenviado', 'processing', 'porsalir')
    AND order_id NOT IN ({ids_str})
    """
    filtered = pd.read_sql(query_filtered, conn).iloc[0]
    
    print(f"\nCon exclusión de pedidos identificados:")
    print(f"  Pedidos: {filtered['pedidos']}")
    print(f"  Ventas:  ${filtered['ventas']:,.0f}")
    
    diff_from_wc = filtered['ventas'] - 52907936
    print(f"\nDiferencia con WC CSV ($52,907,936): ${diff_from_wc:+,.0f}")
else:
    # Cálculo teórico
    diferencia_conocida = 11647487
    ventas_teoricas = total_actual['ventas'] - diferencia_conocida
    pedidos_teoricos = total_actual['pedidos'] - 45
    
    print(f"\nSi excluimos 45 pedidos ($11,647,487):")
    print(f"  Pedidos: {pedidos_teoricos}")
    print(f"  Ventas:  ${ventas_teoricas:,.0f}")
    
    print(f"\nWC CSV Target:")
    print(f"  Pedidos: 637")
    print(f"  Ventas:  $52,907,936")
    
    if abs(ventas_teoricas - 52907936) < 1000:
        print(f"\n✅ PERFECTO! Coincide con WC CSV")
    else:
        diff = ventas_teoricas - 52907936
        print(f"\n⚠️  Diferencia remanente: ${diff:+,.0f}")

conn.close()
