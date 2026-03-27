
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
    
    # Check ga4_ecommerce
    print("\nChecking ga4_ecommerce table...")
    try:
        count = pd.read_sql_query('SELECT COUNT(*) as count FROM ga4_ecommerce', conn)['count'].iloc[0]
        print(f"Registros: {count}")
        
        if count > 0:
            sample = pd.read_sql_query('SELECT * FROM ga4_ecommerce ORDER BY Fecha DESC LIMIT 5', conn)
            print("\nMuestra (últimos 5):")
            print(sample)
            print("\nColumnas:", sample.columns.tolist())
            
            if 'UsuariosActivos' in sample.columns:
                print("\nUsuariosActivos stats:")
                stats = pd.read_sql_query('SELECT min(UsuariosActivos), max(UsuariosActivos), avg(UsuariosActivos), sum(UsuariosActivos) FROM ga4_ecommerce', conn)
                print(stats)
            else:
                print("\n❌ Columna 'UsuariosActivos' NO encontrada!")
        else:
            print("⚠️ La tabla está vacía.")
            
    except Exception as e:
        print(f"Error querying ga4_ecommerce: {e}")

    conn.close()

except Exception as e:
    print(f"\n❌ Error connecting to DB: {e}")
