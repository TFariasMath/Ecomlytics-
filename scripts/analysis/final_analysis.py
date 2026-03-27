"""Verificar cuantos pedidos tienen date_paid y como afecta los totales"""
import sqlite3
import pandas as pd

conn = sqlite3.connect('data/woocommerce.db')

print("="*80)
print("ANALISIS: date_paid en pedidos 2025")
print("="*80)

# Cuantos pedidos tienen date_paid
query = """
SELECT 
    CASE 
        WHEN date_paid IS NULL OR date_paid = '' THEN 'SIN_FECHA_PAGO'
        ELSE 'CON_FECHA_PAGO'
    END as tiene_fecha_pago,
    COUNT(*) as pedidos,
    SUM(total) as ventas
FROM wc_orders
WHERE strftime('%Y', date_created) = '2025'
AND status IN ('completed', 'completoenviado', 'processing', 'porsalir')
GROUP BY tiene_fecha_pago
"""

df = pd.read_sql(query, conn)
print("\nPedidos por presencia de date_paid:")
print("-"*60)
for _, row in df.iterrows():
    print(f"{row['tiene_fecha_pago']:<20} | {row['pedidos']:>5} pedidos | ${row['ventas']:>15,.0f}")

# Ver que metodos de pago tienen fecha
print("\n" + "="*80)
print("METODOS DE PAGO Y date_paid")
print("="*80)

query_payment = """
SELECT 
    payment_method_title,
    COUNT(*) as pedidos,
    SUM(CASE WHEN date_paid IS NOT NULL AND date_paid != '' THEN 1 ELSE 0 END) as con_fecha_pago,
    SUM(total) as ventas
FROM wc_orders
WHERE strftime('%Y', date_created) = '2025'
AND status IN ('completed', 'completoenviado', 'processing', 'porsalir')
GROUP BY payment_method_title
ORDER BY ventas DESC
"""

df_pay = pd.read_sql(query_payment, conn)
print(f"\n{'Metodo de Pago':<30} | {'Pedidos':>8} | {'Con Fecha':>10} | {'Ventas':>15}")
print("-"*75)
for _, row in df_pay.iterrows():
    metodo = row['payment_method_title'] if row['payment_method_title'] else "N/A"
    print(f"{metodo[:30]:<30} | {row['pedidos']:>8} | {row['con_fecha_pago']:>10} | ${row['ventas']:>13,.0f}")

# Comparar con lo que WC deberia reportar
print("\n" + "="*80)
print("RESUMEN")
print("="*80)

# Total con date_paid en 2025
query_con_pago = """
SELECT SUM(total) as total
FROM wc_orders
WHERE strftime('%Y', date_paid) = '2025'
AND status IN ('completed', 'completoenviado', 'processing', 'porsalir')
"""
df_con = pd.read_sql(query_con_pago, conn)
total_con_pago = df_con['total'].iloc[0] if df_con['total'].iloc[0] else 0

# Total por date_created
query_created = """
SELECT SUM(total) as total
FROM wc_orders
WHERE strftime('%Y', date_created) = '2025'
AND status IN ('completed', 'completoenviado', 'processing', 'porsalir')
"""
df_created = pd.read_sql(query_created, conn)
total_created = df_created['total'].iloc[0]

print(f"\nVentas por date_created (2025):   ${total_created:>15,.0f}")
print(f"Ventas por date_paid (2025):      ${total_con_pago:>15,.0f}")
print(f"WooCommerce reporta:              ${53290436:>15,}")
print(f"\nDiferencia (WC - date_paid):      ${53290436 - total_con_pago:>+15,.0f}")
print(f"Diferencia (WC - date_created):   ${53290436 - total_created:>+15,.0f}")

conn.close()

print("\n" + "="*80)
print("CONCLUSION:")
print("="*80)
print("""
El problema es que WooCommerce Analytics usa 'date_paid' para sus reportes,
pero la mayoria de los pedidos NO tienen fecha de pago registrada en la BD.

Esto puede deberse a:
1. Metodos de pago manuales (transferencia, efectivo) que no registran fecha
2. Configuracion incorrecta del plugin de pagos
3. Pedidos marcados manualmente como completados sin registrar pago

SOLUCION RECOMENDADA:
1. En WooCommerce, verificar que los metodos de pago registren la fecha
2. Para el dashboard, usar 'date_created' (como ya lo hace) ya que refleja
   todos los pedidos exitosos
3. Los reportes de WC y el dashboard mostraran numeros diferentes porque
   usan fechas diferentes
""")
