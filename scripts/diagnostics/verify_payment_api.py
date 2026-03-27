"""Verificar directamente con API si los pedidos tienen payment_method"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from woocommerce import API

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

# Verificar algunos pedidos grandes
test_orders = [56336, 56963, 57600, 57661]

print("="*80)
print("VERIFICAR PAYMENT_METHOD EN API")
print("="*80)

for order_id in test_orders:
    print(f"\nPedido #{order_id}:")
    try:
        response = wcapi.get(f"orders/{order_id}")
        if response.status_code == 200:
            order = response.json()
            print(f"  payment_method: '{order.get('payment_method', 'N/A')}'")
            print(f"  payment_method_title: '{order.get('payment_method_title', 'N/A')}'")
            print(f"  date_paid: '{order.get('date_paid', 'N/A')}'")
            print(f"  date_created: '{order.get('date_created', 'N/A')}'")
            print(f"  status: '{order.get('status', 'N/A')}'")
            print(f"  total: ${float(order.get('total', 0)):,.0f}")
        else:
            print(f"  Error: {response.status_code}")
    except Exception as e:
        print(f"  Error: {e}")

print("\n" + "="*80)
print("OBTENIENDO ULTIMOS 5 PEDIDOS DIRECTAMENTE DE API")
print("="*80)

try:
    response = wcapi.get("orders", params={
        "per_page": 5,
        "order": "desc",
        "status": "completed,completoenviado"
    })
    
    if response.status_code == 200:
        orders = response.json()
        for order in orders:
            print(f"\n#{order.get('id')} - {order.get('status')}")
            print(f"  payment_method: '{order.get('payment_method', 'N/A')}'")
            print(f"  payment_method_title: '{order.get('payment_method_title', 'N/A')}'")
            print(f"  date_paid: '{order.get('date_paid', 'N/A')}'")
            print(f"  total: ${float(order.get('total', 0)):,.0f}")
except Exception as e:
    print(f"Error: {e}")
