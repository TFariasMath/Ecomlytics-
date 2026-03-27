
import sqlite3
import os

db_path = os.path.join('data', 'analytics.db')

if os.path.exists(db_path):
    print(f"Connecting to {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Drop table to force full reload
    print("Dropping ga4_ecommerce table...")
    try:
        cursor.execute("DROP TABLE IF EXISTS ga4_ecommerce")
        conn.commit()
        print("✅ Table dropped successfully. Next ETL run will fetch full history (default from 2023-01-01).")
    except Exception as e:
        print(f"❌ Error dropping table: {e}")
    finally:
        conn.close()
else:
    print(f"❌ Database not found at {db_path}")
