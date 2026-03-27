import sqlite3
import pandas as pd

# Check backup
backup_path = 'backups/analytics_20251221_104235.db'
print(f"=== Checking backup: {backup_path} ===")

try:
    conn = sqlite3.connect(backup_path)
    
    # List tables
    tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
    print(f"Tables: {tables['name'].tolist()}")
    
    # Check ga4_ecommerce
    if 'ga4_ecommerce' in tables['name'].tolist():
        df = pd.read_sql("SELECT MIN(Fecha) as min_fecha, MAX(Fecha) as max_fecha, COUNT(*) as total FROM ga4_ecommerce", conn)
        print(f"ga4_ecommerce range: {df.iloc[0]['min_fecha']} to {df.iloc[0]['max_fecha']}, total: {df.iloc[0]['total']} rows")
        
        # Show sample
        sample = pd.read_sql("SELECT * FROM ga4_ecommerce ORDER BY Fecha LIMIT 5", conn)
        print(f"Sample:\n{sample}")
    
    conn.close()
except Exception as e:
    print(f"Error: {e}")

# Check current DB
print(f"\n=== Checking current: data/analytics.db ===")
try:
    conn = sqlite3.connect('data/analytics.db')
    tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
    print(f"Tables: {tables['name'].tolist()}")
    
    if 'ga4_ecommerce' in tables['name'].tolist():
        df = pd.read_sql("SELECT MIN(Fecha) as min_fecha, MAX(Fecha) as max_fecha, COUNT(*) as total FROM ga4_ecommerce", conn)
        print(f"ga4_ecommerce range: {df.iloc[0]['min_fecha']} to {df.iloc[0]['max_fecha']}, total: {df.iloc[0]['total']} rows")
    else:
        print("ga4_ecommerce table NOT FOUND!")
    
    conn.close()
except Exception as e:
    print(f"Error: {e}")
