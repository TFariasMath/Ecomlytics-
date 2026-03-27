import sqlite3
import pandas as pd

conn = sqlite3.connect('data/woocommerce.db')

print("date_created 2025:", pd.read_sql("SELECT SUM(total) FROM wc_orders WHERE strftime('%Y',date_created)='2025' AND status IN ('completed','completoenviado','processing','porsalir')", conn).iloc[0,0])
print("date_paid 2025:   ", pd.read_sql("SELECT SUM(total) FROM wc_orders WHERE strftime('%Y',date_paid)='2025' AND date_paid IS NOT NULL AND status IN ('completed','completoenviado','processing','porsalir')", conn).iloc[0,0])
print("WC CSV 2025:      ", 52907936)

print("\ndate_created 2024:", pd.read_sql("SELECT SUM(total) FROM wc_orders WHERE strftime('%Y',date_created)='2024' AND status IN ('completed','completoenviado','processing','porsalir')", conn).iloc[0,0])
print("date_paid 2024:   ", pd.read_sql("SELECT SUM(total) FROM wc_orders WHERE strftime('%Y',date_paid)='2024' AND date_paid IS NOT NULL AND status IN ('completed','completoenviado','processing','porsalir')", conn).iloc[0,0])
print("WC CSV 2024:      ", 78037182)

conn.close()
