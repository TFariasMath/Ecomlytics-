import sqlite3
import os
from pathlib import Path

db_path = Path('data/woocommerce.db')
if not db_path.exists():
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Check total orders
cursor.execute("SELECT count(*) FROM wc_orders")
total_orders = cursor.fetchone()[0]
print(f"Total orders: {total_orders}")

# Check latest order date
cursor.execute("SELECT max(date_created) FROM wc_orders")
latest_order = cursor.fetchone()[0]
print(f"Latest order date: {latest_order}")

# Check tickets
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='order_tickets'")
if cursor.fetchone():
    cursor.execute("SELECT count(*) FROM order_tickets")
    total_tickets = cursor.fetchone()[0]
    print(f"Total tickets: {total_tickets}")
    
    cursor.execute("SELECT count(*) FROM order_tickets WHERE status='pending'")
    pending_tickets = cursor.fetchone()[0]
    print(f"Pending tickets: {pending_tickets}")
else:
    print("Table 'order_tickets' does not exist.")

conn.close()
