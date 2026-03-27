"""
Script para verificar el esquema de la base de datos woocommerce
"""
import sqlite3

db_path = 'data/woocommerce.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 80)
print("ESQUEMA DE BASE DE DATOS: woocommerce.db")
print("=" * 80)

# Obtener todas las tablas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print(f"\n📊 Tablas encontradas ({len(tables)}):\n")
for table in tables:
    table_name = table[0]
    print(f"  • {table_name}")
    
    # Contar registros
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"    Registros: {count:,}")
    
    # Mostrar esquema
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    print(f"    Columnas ({len(columns)}):")
    for col in columns:
        print(f"      - {col[1]} ({col[2]})")
    print()

conn.close()
