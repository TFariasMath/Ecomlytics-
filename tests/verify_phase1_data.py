import os
import sys
import pandas as pd
import sqlite3

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.database import get_db_connection

DATABASE_NAME = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'woocommerce.db')

def verify_phase1():
    print("🚀 Verifying Phase 1 Data Enrichment...")
    
    if not os.path.exists(DATABASE_NAME):
        print(f"❌ Database not found at {DATABASE_NAME}")
        return

    try:
        with get_db_connection(DATABASE_NAME) as conn:
            # 1. Verify wc_orders schema
            print("\n1️⃣  Checking wc_orders schema...")
            df_orders = pd.read_sql("SELECT * FROM wc_orders LIMIT 5", conn)
            columns = df_orders.columns.tolist()
            
            required_columns = ['billing_city', 'billing_state', 'billing_postcode', 'coupons_used', 'customer_name']
            missing = [col for col in required_columns if col not in columns]
            
            if missing:
                print(f"❌ Missing columns in wc_orders: {missing}")
            else:
                print(f"✅ All required columns present in wc_orders: {required_columns}")
                print("\n   Sample Data:")
                print(df_orders[required_columns].head().to_string())

            # 2. Verify wc_products
            print("\n2️⃣  Checking wc_products table...")
            try:
                df_products = pd.read_sql("SELECT * FROM wc_products LIMIT 5", conn)
                print(f"✅ wc_products table exists with {len(df_products)} rows (limit 5)")
                print("   Columns:", df_products.columns.tolist())
                print("\n   Sample Data (Categories):")
                if 'categories' in df_products.columns:
                    print(df_products[['product_id', 'name', 'categories']].head().to_string())
                else:
                    print("❌ 'categories' column missing in wc_products")
            except Exception as e:
                print(f"❌ wc_products table error: {e}")

    except Exception as e:
        print(f"❌ Verification failed: {e}")

if __name__ == "__main__":
    verify_phase1()
