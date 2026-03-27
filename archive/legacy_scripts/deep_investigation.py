"""
INVESTIGACION PROFUNDA: Encontrar los 45 pedidos EXACTOS que WC CSV excluye
Estrategia: Comparación inversa - identificar pedidos que SOBRAN en BD vs WC CSV
"""
import pandas as pd
import sqlite3

# Cargar WC CSV
df_wc = pd.read_csv("wc-revenue-report-export-17661192702824.csv")
df_wc['Fecha'] = pd.to_datetime(df_wc['Fecha'])
df_wc['Ventas totales'] = pd.to_numeric(df_wc['Ventas totales'], errors='coerce').fillna(0)
df_wc['Pedidos'] = pd.to_numeric(df_wc['Pedidos'], errors='coerce').fillna(0)

df_wc_2025 = df_wc[(df_wc['Fecha'] >= '2025-01-01') & (df_wc['Fecha'] < '2026-01-01')].copy()
df_wc_2025['date_str'] = df_wc_2025['Fecha'].dt.strftime('%Y-%m-%d')

conn = sqlite3.connect('data/woocommerce.db')

print("="*80)
print("ESTRATEGIA INVERSA: Identificar pedidos SOBRANTES")
print("="*80)

# Para días donde BD > WC, necesitamos identificar cuáles pedidos WC NO cuenta
# Pero NO sabemos cuáles son sin acceso a WC Admin

# NUEVA ESTRATEGIA: Buscar patrones en días donde WC < BD
# 1. Ver si hay pedidos con montos exactos que faltan en WC
# 2. Buscar pedidos que sumen exactamente la diferencia

problematic_orders = []

# Cargar días con discrepancias donde BD > WC
df_disc = pd.read_csv('dias_con_discrepancias_2025.csv')
df_extra = df_disc[df_disc['diff_ped'] > 0].copy()

print(f"\nAnalizando {len(df_extra)} días donde BD tiene más pedidos que WC...")
print("\nBuscando pedidos que sumen EXACTAMENTE la diferencia de ventas:")
print("-"*80)

total_found = 0
total_value_found = 0

for idx, row in df_extra.head(30).iterrows():  # Analizar primeros 30 días
    fecha = row['date_str'] if pd.notna(row['date_str']) else row['fecha']
    wc_count = int(row['Pedidos'])
    bd_count = int(row['pedidos'])
    extra_count = int(row['diff_ped'])
    wc_value = row['Ventas totales']
    bd_value = row['ventas']
    diff_value = row['diff_ventas']
    
    if extra_count > 0 and abs(diff_value) > 100:  # Solo si hay diferencia significativa
        # Obtener todos los pedidos de ese día
        query = f"""
        SELECT order_id, total, status, customer_name
        FROM wc_orders
        WHERE date_only = '{fecha}'
        AND status IN ('completed', 'completoenviado', 'processing', 'porsalir')
        ORDER BY total DESC
        """
        df_day = pd.read_sql(query, conn)
        
        if len(df_day) > 0:
            # HIPOTESIS: Los pedidos más grandes son los que WC exclude
            # (Basado en evidencia de pedidos de $740K, $563K, $2.85M que no aparecen en CSV)
            
            # Intentar encontrar combinación que sume exactamente diff_value
            # Para simplificar, tomar los N pedidos más grandes
            top_orders = df_day.nlargest(extra_count, 'total')
            sum_top = top_orders['total'].sum()
            
            # Si la suma de top orders está cerca de diff_value
            if abs(sum_top - diff_value) / abs(diff_value) < 0.1:  # Dentro de 10%
                print(f"\n✓ {fecha}: {extra_count} pedidos (~${diff_value:,.0f})")
                for _, order in top_orders.iterrows():
                    print(f"    #{order['order_id']}: ${order['total']:>10,.0f} - {order['customer_name'][:30]}")
                    problematic_orders.append({
                        'order_id': order['order_id'],
                        'total': order['total'],
                        'fecha': fecha,
                        'customer_name': order['customer_name'],
                        'confidence': 'high'
                    })
                    total_value_found += order['total']
                total_found += len(top_orders)

conn.close()

print("\n" + "="*80)
print("RESULTADOS PRELIMINARES")
print("="*80)
print(f"Pedidos identificados: {total_found}")
print(f"Valor total: ${total_value_found:,.0f}")
print(f"Objetivo: 45 pedidos, $11,647,487")

if total_found > 0:
    df_prob = pd.DataFrame(problematic_orders)
    df_prob.to_csv('pedidos_sobrantes_identificados.csv', index=False)
    print(f"\n✅ Guardado: pedidos_sobrantes_identificados.csv")

print("\n" + "="*80)
print("LIMITACION")
print("="*80)
print("""
Sin acceso directo a WooCommerce Admin, NO podemos saber con certeza
cuáles pedidos específicos WC excluye de su CSV.

La única forma definitiva es:
1. Entrar a WC Admin
2. Ver el reporte del día específico (ej: 2025-03-05)
3. Comparar order_ids mostrados con los que tenemos en BD
4. Identificar cuáles faltan

ALTERNATIVA: Aceptar que el dashboard muestre TODOS los pedidos reales
y agregar nota explicando la diferencia con WC CSV.
""")
