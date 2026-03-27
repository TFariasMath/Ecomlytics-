import sqlite3
import pandas as pd

def analyze_database(db_path, db_name):
    print(f"\n{'='*80}")
    print(f"DATABASE: {db_name}")
    print(f"{'='*80}\n")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    for table_name in tables:
        table_name = table_name[0]
        print(f"\n📊 TABLE: {table_name}")
        print("-" * 80)
        
        # Get column info
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        
        print("\nColumns:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"\nRow count: {count:,}")
        
        # Get sample data
        if count > 0:
            print("\nSample data (first 3 rows):")
            df = pd.read_sql(f"SELECT * FROM {table_name} LIMIT 3", conn)
            print(df.to_string(index=False))
    
    conn.close()

# Analyze all databases
analyze_database('data/woocommerce.db', 'WooCommerce')
analyze_database('data/analytics.db', 'Google Analytics')
analyze_database('data/facebook.db', 'Facebook')

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)
