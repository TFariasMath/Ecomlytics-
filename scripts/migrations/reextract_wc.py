
import os
import sys
import pandas as pd
from woocommerce import API
from typing import List, Dict, Any, Tuple
import sqlite3

# Define Database Path directly
DATABASE_NAME = os.path.join(os.path.dirname(__file__), 'data', 'woocommerce.db')

# Config
URL = "https://tayen.cl"
CK = "ck_5409f28b110a1dd51d930ea0fdcd48ad11706192"
CS = "cs_b8cb8f93124f41fc7165f0ea235fe82e932f09d9"
BATCH_SIZE = 500

def get_wc_api() -> API:
    print(f"🔌 Conectando a WooCommerce API: {URL}")
    return API(url=URL, consumer_key=CK, consumer_secret=CS, version="wc/v3", timeout=30)

def upsert_dataframe(df, table_name, db_path, unique_keys):
    if df.empty: return
    
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    
    # Create valid columns for insert
    cols = df.columns.tolist()
    placeholders = ', '.join(['?' for _ in cols])
    
    # We need to rely on existing table structure, or create if not exists
    # For backfill we assume table exists and has unique index
    
    sql = f"INSERT OR REPLACE INTO {table_name} ({', '.join(cols)}) VALUES ({placeholders})"
    
    # Convert dates/objects to str
    df_copy = df.copy()
    for col in df_copy.select_dtypes(include=['datetime64', 'datetime']):
        df_copy[col] = df_copy[col].astype(str)
        
    values = [tuple(x) for x in df_copy.values]
    with conn:
        conn.executemany(sql, values)
    print(f"💾 Guardadas {len(df)} filas en {table_name}")
    conn.close()

def process_data(orders: List[Dict[str, Any]]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    order_data = []
    order_items_data = []
    
    for order in orders:
        if order.get('status') in ['completed', 'completoenviado', 'processing', 'porsalir']:
            # Safe extraction of customer name
            billing = order.get('billing') or {}
            first = billing.get('first_name') or ''
            last = billing.get('last_name') or ''
            email = billing.get('email') or ''
            full_name = f"{first} {last}".strip()
            
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
                # Customer tracking
                'customer_id': order.get('customer_id', 0),
                'customer_email': email,
                'customer_name': full_name
            }
            order_data.append(item)
            
            for product in order.get('line_items', []):
                p_item = {
                    'order_id': order.get('id'),
                    'product_id': product.get('product_id'),
                    'product_name': product.get('name'),
                    'quantity': product.get('quantity'),
                    'total': float(product.get('total', 0)),
                    'date_created': order.get('date_created')
                }
                order_items_data.append(p_item)
                
    df_orders = pd.DataFrame(order_data)
    df_items = pd.DataFrame(order_items_data)
    
    if not df_orders.empty:
        df_orders['date_created'] = pd.to_datetime(df_orders['date_created']).dt.tz_localize(None)
        df_orders['date_only'] = df_orders['date_created'].dt.date
        
    if not df_items.empty:
        df_items['date_created'] = pd.to_datetime(df_items['date_created']).dt.tz_localize(None)
        
    return df_orders, df_items

def main():
    print("="*50)
    print("🔄 RE-EXTRACCIÓN DE CLIENTES (Standalone)")
    print("="*50)
    
    wcapi = get_wc_api()
    page = 1
    valid_statuses = "completed,completoenviado,processing,porsalir"
    
    while True:
        try:
            print(f"📄 Fetching page {page}...")
            orders = wcapi.get("orders", params={
                "per_page": 100,
                "page": page,
                "status": valid_statuses,
                "after": "2023-01-01T00:00:00"
            }).json()
            
            if not orders or len(orders) == 0:
                print("✅ Fin de órdenes.")
                break
                
            df_orders, df_items = process_data(orders)
            
            upsert_dataframe(df_orders, 'wc_orders', DATABASE_NAME, unique_keys=['order_id'])
            # Note: We update items too just in case, though usually not needed for customer fix
            upsert_dataframe(df_items, 'wc_order_items', DATABASE_NAME, unique_keys=['order_id', 'product_id'])
            
            page += 1
            
        except Exception as e:
            print(f"❌ Error: {e}")
            break

if __name__ == "__main__":
    main()
