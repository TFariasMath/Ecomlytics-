import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path('.env')
try:
    load_dotenv(env_path, encoding='utf-8')
except UnicodeDecodeError:
    load_dotenv(env_path, encoding='latin-1')

print(f"TICKETS_ENABLED: {os.getenv('TICKETS_ENABLED')}")
print(f"WC_URL: {os.getenv('WC_URL')}")
