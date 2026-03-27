
import os
import sys
import pandas as pd
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest
from google.oauth2 import service_account

# Setup paths
sys.path.append(os.getcwd())
from dotenv import load_dotenv
load_dotenv()
from config.settings import GoogleAnalyticsConfig

def test_history():
    print("=== Testing Historical Data Availability ===")
    
    # 1. Load Credentials
    key_file_path = GoogleAnalyticsConfig.get_key_file_path()
    if not os.path.exists(key_file_path):
        print(f"❌ Key file not found at: {key_file_path}")
        return

    try:
        creds = service_account.Credentials.from_service_account_file(key_file_path)
        client = BetaAnalyticsDataClient(credentials=creds)
        property_id = GoogleAnalyticsConfig.get_property_id()
        if not property_id.startswith('properties/'):
            property_id = f'properties/{property_id}'
            
        print(f"Property ID: {property_id}")
        
        # 2. Try to fetch Jan 2024
        print("\nAttempting to fetch data for Jan 1, 2024 - Jan 31, 2024...")
        request = RunReportRequest(
            property=property_id,
            dimensions=[Dimension(name='date')],
            metrics=[Metric(name='activeUsers')],
            date_ranges=[DateRange(start_date="2024-01-01", end_date="2024-01-31")],
        )
        
        response = client.run_report(request)
        
        if not response.rows:
            print("❌ No data found for Jan 2024.")
        else:
            print(f"✅ Found {len(response.rows)} days of data for Jan 2024!")
            for row in response.rows[:5]:
                print(f"  Date: {row.dimension_values[0].value}, Users: {row.metric_values[0].value}")

        # 3. Try to fetch Dec 2025 (Known good range)
        print("\nAttempting to fetch data for Dec 1, 2025 - Today...")
        request_recent = RunReportRequest(
            property=property_id,
            dimensions=[Dimension(name='date')],
            metrics=[Metric(name='activeUsers')],
            date_ranges=[DateRange(start_date="2025-12-01", end_date="today")],
        )
        response_recent = client.run_report(request_recent)
        if not response_recent.rows:
             print("❌ No data found for Dec 2025.")
        else:
             print(f"✅ Found {len(response_recent.rows)} days of data for Dec 2025!")
             # Sort by date
             data = []
             for row in response_recent.rows:
                 data.append((row.dimension_values[0].value, int(row.metric_values[0].value)))
             data.sort()
             print(f"  Oldest date found: {data[0]}")
             print(f"  Newest date found: {data[-1]}")

    except Exception as e:
        print(f"❌ Error API: {e}")

if __name__ == "__main__":
    test_history()
