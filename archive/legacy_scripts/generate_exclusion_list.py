"""
SOLUCION: Identificar TODOS los pedidos problemáticos y crear filtro
"""
import pandas as pd
import sqlite3

# Cargar días con discrepancias
df_disc = pd.read_csv('dias_con_discrepancias_2025.csv')

# Solo días donde BD tiene MAS pedidos que WC
df_extra = df_disc[df_disc['diff_ped'] > 0].copy()

print("="*80)
print(f"GENERANDO LISTA COMPLETA DE PEDIDOS PROBLEMATICOS")
print("="*80)
print(f"\nDías con pedidos extra: {len(df_extra)}")
print(f"Total pedidos extra estimados: {int(df_extra['diff_ped'].sum())}")

conn = sqlite3.connect('data/woocommerce.db')

# Lista de TODOS los pedidos de días con discrepancia
all_problem_orders = []
total_value = 0

for idx, row in df_extra.iterrows():
    fecha = row['date_str'] if pd.notna(row['date_str']) else row['fecha']
    wc_ped = int(row['Pedidos'])
    bd_ped = int(row['pedidos'])
    extra = int(row['diff_ped'])
    
    # Obtener TODOS los pedidos de ese día
    query = f"""
    SELECT order_id, total, status, customer_id, customer_name, payment_method
    FROM wc_orders
    WHERE date_only = '{fecha}'
    AND status IN ('completed', 'completoenviado', 'processing', 'porsalir')
    ORDER BY total DESC
    """
    df_day = pd.read_sql(query, conn)
    
    if len(df_day) > 0 and extra > 0:
        # Hipótesis: Los pedidos con mayor valor son los problemáticos
        # (basado en que pedidos de $740K, $563K fueron confirmados como no existentes)
        problem_orders = df_day.nlargest(extra, 'total')
        
        for _, order in problem_orders.iterrows():
            all_problem_orders.append({
                'order_id': order['order_id'],
                'fecha': fecha,
                'total': order['total'],
                'status': order['status'],
                'customer_id': order['customer_id'],
                'customer_name': order['customer_name'],
                'payment_method': order['payment_method']
            })
            total_value += order['total']

conn.close()

# Guardar lista completa
df_problems = pd.DataFrame(all_problem_orders)
df_problems.to_csv('lista_pedidos_excluir.csv', index=False)

print(f"\n✅ Lista generada: lista_pedidos_excluir.csv")
print(f"   Total pedidos: {len(df_problems)}")
print(f"   Valor total: ${total_value:,.0f}")

# Analizar patrones
print("\n" + "="*80)
print("PATRON 1: Por customer_id")
print("="*80)
guest_orders = df_problems[df_problems['customer_id'] == 0]
registered = df_problems[df_problems['customer_id'] != 0]
print(f"Invitados (customer_id=0): {len(guest_orders)} pedidos (${guest_orders['total'].sum():,.0f})")
print(f"Registrados: {len(registered)} pedidos (${registered['total'].sum():,.0f})")

# Analizar por payment_method
print("\n" + "="*80)
print("PATRON 2: Por payment_method")
print("="*80)
pm_counts = df_problems.groupby('payment_method').agg({
    'order_id': 'count',
    'total': 'sum'
}).sort_values('total', ascending=False)
for pm, row in pm_counts.head(5).iterrows():
    pm_name = pm if pm else 'NULL/Vacío'
    print(f"  {pm_name:<30}: {row['order_id']:>4} pedidos | ${row['total']:>12,.0f}")

# Analizar por cliente
print("\n" + "="*80)
print("PATRON 3: Top clientes problemáticos")
print("="*80)
top_customers = df_problems.groupby('customer_name').agg({
    'order_id': 'count',
    'total': 'sum'
}).sort_values('total', ascending=False).head(10)
for name, row in top_customers.iterrows():
    print(f"  {name[:40]:<40}: {row['order_id']:>3} ped | ${row['total']:>12,.0f}")

print("\n" + "="*80)
print("RECOMENDACION")
print("="*80)

# Si más del 80% son de invitados o tienen payment_method NULL
if len(guest_orders) / len(df_problems) > 0.8:
    print("✅ FILTRO RECOMENDADO: Excluir pedidos con customer_id = 0 (invitados)")
elif df_problems['payment_method'].isna().sum() / len(df_problems) > 0.8:
    print("✅ FILTRO RECOMENDADO: Excluir pedidos con payment_method NULL")
else:
    print("⚠️  No hay patrón claro. Usar lista de order_ids específicos.")
    print(f"   Crear archivo: excluded_order_ids.txt con {len(df_problems)} IDs")
    
    # Guardar lista de IDs
    with open('excluded_order_ids.txt', 'w') as f:
        f.write('\n'.join([str(x) for x in df_problems['order_id'].tolist()]))
    print("   ✅ Guardado: excluded_order_ids.txt")
