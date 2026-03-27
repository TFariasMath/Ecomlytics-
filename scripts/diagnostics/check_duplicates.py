import sqlite3
import pandas as pd

conn = sqlite3.connect('data/woocommerce.db')

# Verificar duplicados por order_id
query_duplicates = """
SELECT order_id, COUNT(*) as count
FROM wc_orders
WHERE strftime('%Y', date_created) = '2025'
GROUP BY order_id
HAVING count > 1
ORDER BY count DESC
LIMIT 10
"""

df_dup = pd.read_sql(query_duplicates, conn)

print("="*70)
print("VERIFICACIÓN DE DUPLICADOS EN 2025:")
print("="*70)

if df_dup.empty:
    print("\n✅ NO hay duplicados por order_id")
else:
    print(f"\n❌ DUPLICADOS DETECTADOS: {len(df_dup)} order_ids duplicados")
    print("\nEjemplos:")
    print(df_dup.head())
    
    # Contar total de filas duplicadas
    total_extra = (df_dup['count'] - 1).sum()
    print(f"\n⚠️ Hay {total_extra:,} filas duplicadas que deben eliminarse")

# Verificar total de registros vs pedidos únicos
query_stats = """
SELECT 
    COUNT(*) as total_registros,
    COUNT(DISTINCT order_id) as pedidos_unicos,
    SUM(total) as suma_total
FROM wc_orders  
WHERE strftime('%Y', date_created) = '2025'
AND status IN ('completed', 'completoenviado', 'processing', 'porsalir', 'on-hold')
"""

df_stats = pd.read_sql(query_stats, conn)
print("\n" + "="*70)
print("ESTADÍSTICAS:")
print("="*70)
print(f"Total registros: {df_stats['total_registros'].iloc[0]:,}")
print(f"Pedidos únicos: {df_stats['pedidos_unicos'].iloc[0]:,}")
print(f"Suma total: ${df_stats['suma_total'].iloc[0]:,.0f}")

ratio = df_stats['total_registros'].iloc[0] / df_stats['pedidos_unicos'].iloc[0]
print(f"\nRatio de duplicación: {ratio:.2f}x")

conn.close()
