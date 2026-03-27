import sqlite3
import pandas as pd

conn = sqlite3.connect('data/woocommerce.db')
df = pd.read_sql('SELECT DISTINCT billing_state FROM wc_orders WHERE billing_state IS NOT NULL AND billing_state != ""', conn)
conn.close()

print("Unique regions in database:")
print(df['billing_state'].tolist())
