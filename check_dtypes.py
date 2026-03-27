import sqlite3
import pandas as pd

db_path = 'data/analytics.db'
conn = sqlite3.connect(db_path)

print("--- ga4_traffic_sources ---")
try:
    df = pd.read_sql("SELECT * FROM ga4_traffic_sources LIMIT 5", conn)
    print("Dtypes:")
    print(df.dtypes)
    print("\nSample values:")
    print(df.head())
    
    # Test conversion
    print("\nTest pd.to_datetime default behavior:")
    converted = pd.to_datetime(df['Fecha'])
    print(converted.head())
    
    print("\nTest pd.to_datetime with format:")
    converted_fmt = pd.to_datetime(df['Fecha'].astype(str), format='%Y%m%d')
    print(converted_fmt.head())
    
except Exception as e:
    print(e)

print("\n--- ga4_ecommerce ---")
try:
    df = pd.read_sql("SELECT * FROM ga4_ecommerce LIMIT 5", conn)
    print("Dtypes:")
    print(df.dtypes)
    print("\nSample values:")
    print(df.head())
except Exception as e:
    print(e)

conn.close()
