"""Verificar API para pedidos sin datos en BD"""
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

orders_to_check = [57660, 57658, 57657, 57656]

print("="*80)
print("VERIFICACION DE API PARA PEDIDOS SIN DATOS EN BD")
print("="*80)

for order_id in orders_to_check:
    print(f"\nPedido #{order_id}:")
    response = wcapi.get(f"orders/{order_id}")
    if response.status_code == 200:
        order = response.json()
        pm = order.get('payment_method', 'NONE')
        pmt = order.get('payment_method_title', 'NONE')
        dp = order.get('date_paid', 'NONE')
        print(f"  payment_method: '{pm}'")
        print(f"  payment_method_title: '{pmt}'")
        print(f"  date_paid: '{dp}'")
    else:
        print(f"  Error: {response.status_code}")
