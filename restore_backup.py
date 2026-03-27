import sqlite3
import pandas as pd

backup_path = 'backups/analytics_20251221_104235.db'
current_path = 'data/analytics.db'

print("Restoring ga4_ecommerce from backup...")

# Read from backup
conn_backup = sqlite3.connect(backup_path)
df = pd.read_sql("SELECT * FROM ga4_ecommerce", conn_backup)
conn_backup.close()
print(f"Read {len(df)} rows from backup")

# Write to current DB
conn_current = sqlite3.connect(current_path)
df.to_sql('ga4_ecommerce', conn_current, if_exists='replace', index=False)
conn_current.close()
print(f"Restored {len(df)} rows to current database!")

# Verify
conn_verify = sqlite3.connect(current_path)
result = pd.read_sql("SELECT MIN(Fecha), MAX(Fecha), COUNT(*) as total FROM ga4_ecommerce", conn_verify)
conn_verify.close()
print(f"Verification: {result.iloc[0].to_dict()}")
