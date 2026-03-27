"""
ACTUALIZADOR DE CAMPOS FALTANTES
=================================
Este script actualiza los campos payment_method, payment_method_title y date_paid
que estan faltantes en la BD, consultando directamente la API de WooCommerce.
"""
import sqlite3
import time
from woocommerce import API

# Config
URL = "https://tayen.cl"
CK = "ck_5409f28b110a1dd51d930ea0fdcd48ad11706192"
CS = "cs_b8cb8f93124f41fc7165f0ea235fe82e932f09d9"
DATABASE = "data/woocommerce.db"

wcapi = API(
    url=URL,
    consumer_key=CK,
    consumer_secret=CS,
    version="wc/v3",
    timeout=30
)

def get_orders_missing_payment():
    """Obtiene pedidos sin payment_method"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    query = """
    SELECT order_id 
    FROM wc_orders 
    WHERE (payment_method IS NULL OR payment_method = '')
    AND strftime('%Y', date_created) >= '2024'
    ORDER BY order_id DESC
    """
    
    cursor.execute(query)
    orders = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    return orders

def update_order_from_api(order_id):
    """Actualiza un pedido desde la API"""
    try:
        response = wcapi.get(f"orders/{order_id}")
        if response.status_code == 200:
            order = response.json()
            return {
                'payment_method': order.get('payment_method', ''),
                'payment_method_title': order.get('payment_method_title', ''),
                'date_paid': order.get('date_paid')
            }
    except Exception as e:
        print(f"Error para #{order_id}: {e}")
    return None

def update_db(order_id, data):
    """Actualiza la BD con los datos"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE wc_orders 
        SET payment_method = ?,
            payment_method_title = ?,
            date_paid = ?
        WHERE order_id = ?
    """, (data['payment_method'], data['payment_method_title'], data['date_paid'], order_id))
    
    conn.commit()
    conn.close()

def main():
    print("="*70)
    print("ACTUALIZADOR DE CAMPOS FALTANTES")
    print("="*70)
    
    # Obtener pedidos sin payment_method
    orders = get_orders_missing_payment()
    print(f"\nPedidos a actualizar: {len(orders)}")
    
    if not orders:
        print("No hay pedidos para actualizar")
        return
    
    updated = 0
    errors = 0
    
    for i, order_id in enumerate(orders):
        if i % 50 == 0:
            print(f"\nProcesando {i}/{len(orders)}...")
        
        data = update_order_from_api(order_id)
        if data:
            update_db(order_id, data)
            updated += 1
            if i < 5:  # Mostrar primeros 5
                print(f"  #{order_id}: PM={data['payment_method']}, DP={data['date_paid']}")
        else:
            errors += 1
        
        # Rate limiting
        if i % 10 == 0:
            time.sleep(0.5)
    
    print(f"\n" + "="*70)
    print(f"COMPLETADO: {updated} actualizados, {errors} errores")
    print("="*70)

if __name__ == "__main__":
    main()
