import sqlite3
import pandas as pd
import os

db_path = 'data/analytics.db'

print(f"Checking database at: {os.path.abspath(db_path)}")

if not os.path.exists(db_path):
    print("❌ Database file not found!")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    
    # Check tables
    tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)
    print("\nTablas encontradas:")
    print(tables)
    
    # Check ga4_traffic_sources
    if 'ga4_traffic_sources' in tables['name'].values:
        count_traffic = pd.read_sql_query('SELECT COUNT(*) as count FROM ga4_traffic_sources', conn)
        print(f"\nRegistros en ga4_traffic_sources: {count_traffic['count'].iloc[0]}")
        
        if count_traffic['count'].iloc[0] > 0:
            sample = pd.read_sql_query('SELECT * FROM ga4_traffic_sources LIMIT 3', conn)
            print("\nMuestra ga4_traffic_sources:")
            print(sample)
            print("\nColumnas:", sample.columns.tolist())
    else:
        print("\n❌ Tabla ga4_traffic_sources NO encontrada")

    # Check ga4_ecommerce
    if 'ga4_ecommerce' in tables['name'].values:
        count_ecom = pd.read_sql_query('SELECT COUNT(*) as count FROM ga4_ecommerce', conn)
        print(f"\nRegistros en ga4_ecommerce: {count_ecom['count'].iloc[0]}")
    else:
        print("\n❌ Tabla ga4_ecommerce NO encontrada")

    conn.close()

except Exception as e:
    print(f"\n❌ Error accediendo a la BD: {e}")
