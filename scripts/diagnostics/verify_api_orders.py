"""Verificar pedidos fantasma directamente con la API de WooCommerce"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from woocommerce import API

# WC API Config
URL = "https://tayen.cl"
CK = "ck_5409f28b110a1dd51d930ea0fdcd48ad11706192"
CS = "cs_b8cb8f93124f41fc7165f0ea235fe82e932f09d9"

wcapi = API(
    url=URL,
    consumer_key=CK,
    consumer_secret=CS,
    version="wc/v3",
    timeout=30
)

# Pedidos sospechosos
GHOST_ORDERS = [56336, 56963, 56363, 57067, 57600]

print("="*80)
print("VERIFICACION DIRECTA CON API DE WOOCOMMERCE")
print("="*80)

for order_id in GHOST_ORDERS:
    print(f"\nBuscando pedido #{order_id}...")
    try:
        response = wcapi.get(f"orders/{order_id}")
        
        if response.status_code == 200:
            order = response.json()
            print(f"  EXISTE en WooCommerce:")
            print(f"    Status: {order.get('status')}")
            print(f"    Fecha: {order.get('date_created')}")
            print(f"    Total: ${float(order.get('total', 0)):,.0f}")
            print(f"    Cliente: {order.get('billing', {}).get('first_name')} {order.get('billing', {}).get('last_name')}")
        elif response.status_code == 404:
            print(f"  NO EXISTE (404)")
        else:
            print(f"  Error: Status {response.status_code}")
            print(f"    {response.text[:200]}")
            
    except Exception as e:
        print(f"  Error: {e}")

print("\n" + "="*80)
print("VERIFICACION COMPLETA")
print("="*80)
