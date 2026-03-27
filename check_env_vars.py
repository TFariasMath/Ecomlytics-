import os
from dotenv import load_dotenv
from pathlib import Path

# Try to load again just to be sure
project_root = Path(__file__).parent
load_dotenv(project_root / '.env')

print(f"TICKETS_ENABLED: {os.getenv('TICKETS_ENABLED')}")
print(f"WC_URL: {os.getenv('WC_URL')}")
