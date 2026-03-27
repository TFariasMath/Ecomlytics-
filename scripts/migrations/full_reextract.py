"""
RE-EXTRACCION COMPLETA DE WOOCOMMERCE
=====================================
Este script elimina la tabla wc_orders y la recrea con todos los datos
correctos desde la API de WooCommerce.
"""
import os
import sys
import sqlite3
import pandas as pd
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from woocommerce import API

# Configuration
URL = "https://tayen.cl"
CK = "ck_5409f28b110a1dd51d930ea0fdcd48ad11706192"
CS = "cs_b8cb8f93124f41fc7165f0ea235fe82e932f09d9"
DATABASE_NAME = os.path.join(os.path.dirname(__file__), '..', 'data', 'woocommerce.db')

# Estados validos
VALID_STATUSES = ['completed', 'completoenviado', 'processing', 'porsalir']

def get_api():
    return API(
        url=URL,
        consumer_key=CK,
        consumer_secret=CS,
        version="wc/v3",
        timeout=60
    )

def backup_table():
    """Crear backup de la tabla antes de eliminar"""
    print("📦 Creando backup de wc_orders...")
    conn = sqlite3.connect(DATABASE_NAME)
    try:
        # Verificar si existe
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='wc_orders'")
        if cursor.fetchone():
            cursor.execute("DROP TABLE IF EXISTS wc_orders_backup_old")
            cursor.execute("ALTER TABLE wc_orders RENAME TO wc_orders_backup_old")
            conn.commit()
            print("   Backup creado: wc_orders_backup_old")
        else:
            print("   No existe tabla wc_orders para backup")
    except Exception as e:
        print(f"   Error en backup: {e}")
    finally:
        conn.close()

def extract_all_orders():
    """Extrae TODOS los pedidos desde WooCommerce"""
    print("\n🔄 Extrayendo TODOS los pedidos desde WooCommerce...")
    
    wcapi = get_api()
    page = 1
    all_orders = []
    
    # Extraer SIN filtro de status para obtener todo
    # Luego filtramos localmente
    while True:
        print(f"   Página {page}...", end=" ")
        try:
            response = wcapi.get("orders", params={
                "per_page": 100,
                "page": page,
                "status": ",".join(VALID_STATUSES),
                "after": "2017-01-01T00:00:00"  # Desde el inicio
            })
            
            if response.status_code != 200:
                print(f"Error: {response.status_code}")
                break
                
            orders = response.json()
            
            if not orders or len(orders) == 0:
                print("fin")
                break
                
            all_orders.extend(orders)
            print(f"{len(orders)} pedidos")
            page += 1
            
        except Exception as e:
            print(f"Error: {e}")
            break
    
    print(f"\n✅ Total extraído: {len(all_orders)} pedidos")
    return all_orders

def process_orders(orders):
    """Procesa los pedidos en DataFrame"""
    print("\n🔧 Procesando pedidos...")
    
    order_data = []
    
    for order in orders:
        # Get shipping method
        shipping_lines = order.get('shipping_lines', [])
        shipping_method = shipping_lines[0].get('method_title') if shipping_lines else ''
        
        item = {
            'order_id': order.get('id'),
            'date_created': order.get('date_created'),
            'status': order.get('status'),
            'total': float(order.get('total', 0)),
            'currency': order.get('currency'),
            'shipping_total': float(order.get('shipping_total', 0)),
            'discount_total': float(order.get('discount_total', 0)),
            'total_tax': float(order.get('total_tax', 0)),
            'cart_tax': float(order.get('cart_tax', 0)),
            'shipping_tax': float(order.get('shipping_tax', 0)),
            'customer_id': order.get('customer_id', 0),
            'customer_email': order.get('billing', {}).get('email', ''),
            'customer_name': f"{order.get('billing', {}).get('first_name', '')} {order.get('billing', {}).get('last_name', '')}".strip(),
            'billing_city': order.get('billing', {}).get('city', ''),
            'billing_state': order.get('billing', {}).get('state', ''),
            'billing_postcode': order.get('billing', {}).get('postcode', ''),
            'billing_country': order.get('billing', {}).get('country', 'CL'),
            'billing_phone': order.get('billing', {}).get('phone', ''),
            'shipping_city': order.get('shipping', {}).get('city', ''),
            'shipping_state': order.get('shipping', {}).get('state', ''),
            'shipping_postcode': order.get('shipping', {}).get('postcode', ''),
            # CAMPOS CRITICOS - ANTES FALTABAN
            'payment_method': order.get('payment_method', ''),
            'payment_method_title': order.get('payment_method_title', ''),
            'date_paid': order.get('date_paid'),
            'date_completed': order.get('date_completed'),
            'date_modified': order.get('date_modified'),
            'shipping_method': shipping_method,
            'coupons_used': ",".join([c.get('code', '') for c in (order.get('coupon_lines') or [])])
        }
        order_data.append(item)
    
    df = pd.DataFrame(order_data)
    
    # Normalizar fechas
    if not df.empty:
        df['date_created'] = pd.to_datetime(df['date_created']).dt.tz_localize(None)
        df['date_only'] = df['date_created'].dt.date
        
        # Convertir date_paid a datetime (puede ser None)
        df['date_paid'] = pd.to_datetime(df['date_paid'], errors='coerce').dt.tz_localize(None)
    
    print(f"   Procesados: {len(df)} pedidos")
    return df

def save_to_db(df):
    """Guarda el DataFrame en la base de datos"""
    print("\n💾 Guardando en base de datos...")
    
    conn = sqlite3.connect(DATABASE_NAME)
    
    # Crear tabla nueva
    df.to_sql('wc_orders', conn, if_exists='replace', index=False)
    
    # Verificar
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM wc_orders")
    count = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(total) FROM wc_orders WHERE strftime('%Y', date_created) = '2025'")
    total_2025 = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"   ✅ {count} pedidos guardados")
    print(f"   ✅ Total 2025: ${total_2025:,.0f}")

def verify_data():
    """Verifica que los datos se guardaron correctamente"""
    print("\n🔍 VERIFICACION DE DATOS")
    print("="*60)
    
    conn = sqlite3.connect(DATABASE_NAME)
    
    # Verificar payment_method
    query = """
    SELECT 
        CASE WHEN payment_method IS NULL OR payment_method = '' THEN 'SIN_METODO' ELSE 'CON_METODO' END as tiene_metodo,
        COUNT(*) as pedidos,
        SUM(total) as ventas
    FROM wc_orders
    WHERE strftime('%Y', date_created) = '2025'
    GROUP BY tiene_metodo
    """
    df = pd.read_sql(query, conn)
    print("\nPayment Method:")
    for _, row in df.iterrows():
        print(f"  {row['tiene_metodo']}: {row['pedidos']} pedidos, ${row['ventas']:,.0f}")
    
    # Verificar date_paid
    query = """
    SELECT 
        CASE WHEN date_paid IS NULL THEN 'SIN_FECHA_PAGO' ELSE 'CON_FECHA_PAGO' END as tiene_fecha,
        COUNT(*) as pedidos,
        SUM(total) as ventas
    FROM wc_orders
    WHERE strftime('%Y', date_created) = '2025'
    GROUP BY tiene_fecha
    """
    df = pd.read_sql(query, conn)
    print("\nDate Paid:")
    for _, row in df.iterrows():
        print(f"  {row['tiene_fecha']}: {row['pedidos']} pedidos, ${row['ventas']:,.0f}")
    
    # Comparar con WC
    query = """
    SELECT SUM(total) as total
    FROM wc_orders
    WHERE strftime('%Y', date_created) = '2025'
    AND status IN ('completed', 'completoenviado', 'processing', 'porsalir')
    """
    df = pd.read_sql(query, conn)
    total_bd = df['total'].iloc[0]
    
    print(f"\n📊 COMPARACION CON WOOCOMMERCE:")
    print(f"   BD (date_created 2025):  ${total_bd:,.0f}")
    print(f"   WC reporta:               $53,290,436")
    print(f"   Diferencia:               ${total_bd - 53290436:+,.0f}")
    
    conn.close()

def main():
    print("="*60)
    print("🚀 RE-EXTRACCION COMPLETA DE WOOCOMMERCE")
    print(f"   Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # 1. Backup
    backup_table()
    
    # 2. Extraer todo
    orders = extract_all_orders()
    
    if not orders:
        print("❌ No se obtuvieron pedidos. Abortando.")
        return
    
    # 3. Procesar
    df = process_orders(orders)
    
    # 4. Guardar
    save_to_db(df)
    
    # 5. Verificar
    verify_data()
    
    print("\n" + "="*60)
    print("✅ RE-EXTRACCION COMPLETADA")
    print("="*60)

if __name__ == "__main__":
    main()
