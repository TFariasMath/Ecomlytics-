
import sqlite3
import pandas as pd
import os

db_path = 'data/analytics.db'
if not os.path.exists(db_path):
    print("❌ Database file not found!")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    
    print("\n--- Verifying ga4_ecommerce Date Parsing ---")
    df_ecommerce = pd.read_sql_query('SELECT * FROM ga4_ecommerce', conn)
    
    if not df_ecommerce.empty:
        print(f"Raw first date: {df_ecommerce['Fecha'].iloc[0]} (Type: {type(df_ecommerce['Fecha'].iloc[0])})")
        
        # APPLY FIX LOGIC
        try:
            df_ecommerce['Fecha_Parsed'] = pd.to_datetime(df_ecommerce['Fecha'].astype(str), format='%Y%m%d', errors='coerce')
            print("\nVerification Results:")
            print(f"Min Date: {df_ecommerce['Fecha_Parsed'].min()}")
            print(f"Max Date: {df_ecommerce['Fecha_Parsed'].max()}")
            
            if df_ecommerce['Fecha_Parsed'].dt.year.max() >= 2024:
                print("✅ Date parsing successful! Years are correct.")
            else:
                print("❌ Date parsing failed! Years are incorrect (likely 1970).")
        except Exception as e:
            print(f"❌ Error during parsing: {e}")
    else:
        print("⚠️ ga4_ecommerce is empty.")

    print("\n--- Verifying ga4_traffic_sources Date Parsing ---")
    df_traffic = pd.read_sql_query('SELECT * FROM ga4_traffic_sources', conn)
    
    if not df_traffic.empty:
        print(f"Raw first date: {df_traffic['Fecha'].iloc[0]} (Type: {type(df_traffic['Fecha'].iloc[0])})")
         # APPLY FIX LOGIC
        try:
            df_traffic['Fecha_Parsed'] = pd.to_datetime(df_traffic['Fecha'].astype(str), format='%Y%m%d', errors='coerce')
            print(f"Min Date: {df_traffic['Fecha_Parsed'].min()}")
            print(f"Max Date: {df_traffic['Fecha_Parsed'].max()}")
             
            if df_traffic['Fecha_Parsed'].dt.year.max() >= 2024:
                print("✅ Date parsing successful! Years are correct.")
            else:
                print("❌ Date parsing failed! Years are incorrect.")

        except Exception as e:
             print(f"❌ Error during parsing: {e}")
    else:
        print("⚠️ ga4_traffic_sources is empty.")

    conn.close()

except Exception as e:
    print(f"\n❌ Error connecting to DB: {e}")
