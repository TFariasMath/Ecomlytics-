"""
PASO 2: Identificar Pedidos Problemáticos
Para cada día con discrepancia, lista los order_ids específicos
"""
import pandas as pd
import sqlite3

# Cargar días con discrepancias
df_disc = pd.read_csv('dias_con_discrepancias_2025.csv')

# Filtrar solo días donde BD > WC (tiene pedidos de más)
df_extra = df_disc[df_disc['diff_ped'] > 0].copy()

print("="*80)
print(f"IDENTIFICAR PEDIDOS PROBLEMATICOS")
print("="*80)
print(f"\nDías donde BD tiene MAS pedidos que WC: {len(df_extra)}")
print(f"Total pedidos extra: {int(df_extra['diff_ped'].sum())}")
print(f"Total ventas extra: ${df_extra['diff_ventas'].sum():,.0f}")

conn = sqlite3.connect('data/woocommerce.db')

# Lista para almacenar todos los pedidos problemáticos
problem_orders = []

print("\n" + "="*80)
print("ANALIZANDO DIAS CON PEDIDOS EXTRA...")
print("="*80)

for idx, row in df_extra.head(20).iterrows():  # Analizar primeros 20 días
    fecha = row['date_str'] if pd.notna(row['date_str']) else row['fecha']
    wc_ped = int(row['Pedidos'])
    bd_ped = int(row['pedidos'])
    extra = int(row['diff_ped'])
    
    # Obtener todos los pedidos de ese día en BD
    query = f"""
    SELECT order_id, total, status, customer_id, customer_name
    FROM wc_orders
    WHERE date_only = '{fecha}'
    AND status IN ('completed', 'completoenviado', 'processing', 'porsalir')
    ORDER BY total DESC
    """
    df_day = pd.read_sql(query, conn)
    
    if len(df_day) > 0:
        print(f"\n{fecha}: WC={wc_ped}, BD={bd_ped}, Extra={extra}")
        print(f"  Pedidos en BD:")
        for _, order in df_day.iterrows():
            print(f"    #{order['order_id']}: ${order['total']:>10,.0f} | {order['status']:<15} | {order['customer_name'][:30]}")
        
        # Si hay pedidos extra, los marcamos como problemáticos
        # Hipótesis: los pedidos con total más alto son los problemáticos
        # (esto es una suposición que necesita validación)
        if extra > 0:
            top_orders = df_day.nlargest(extra, 'total')
            for _, order in top_orders.iterrows():
                problem_orders.append({
                    'order_id': order['order_id'],
                    'fecha': fecha,
                    'total': order['total'],
                    'status': order['status'],
                    'customer_name': order['customer_name'],
                    'reason': 'top_value_on_discrepant_day'
                })

conn.close()

# Guardar pedidos problemáticos
if problem_orders:
    df_problems = pd.DataFrame(problem_orders)
    df_problems.to_csv('pedidos_problematicos.csv', index=False)
    print(f"\n✅ Guardado: pedidos_problematicos.csv ({len(df_problems)} pedidos)")
    
    print("\n" + "="*80)
    print("RESUMEN DE PEDIDOS PROBLEMATICOS")
    print("="*80)
    print(f"Total pedidos identificados: {len(df_problems)}")
    print(f"Total en ventas: ${df_problems['total'].sum():,.0f}")
    
    print("\nTop 10 pedidos por monto:")
    for _, order in df_problems.nlargest(10, 'total').iterrows():
        print(f"  #{order['order_id']}: ${order['total']:>10,.0f} | {order['fecha']} | {order['customer_name' ][:30]}")

print("\n" + "="*80)
print("SIGUIENTE PASO")
print("="*80)
print("""
NOTA: Este análisis asume que los pedidos con MAYOR valor en días
con discrepancia son los problemáticos. Esto es una HIPOTESIS.

Necesitamos validar:
1. ¿Estos pedidos existen realmente en WooCommerce?
2. ¿Por qué WC no los cuenta en sus reportes?

Revisar manualmente algunos de estos pedidos en WooCommerce Admin.""")
