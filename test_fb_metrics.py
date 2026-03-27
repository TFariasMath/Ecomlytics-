
import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load .env manually to be sure
load_dotenv()

USER_TOKEN = os.getenv('FB_ACCESS_TOKEN')
PAGE_ID = os.getenv('FB_PAGE_ID')
API_VERSION = "v19.0"

CANDIDATE_METRICS = [
    'page_impressions',
    'page_engaged_users',
    'page_fan_adds',
    'page_views_total',
    'page_post_engagements',
    'page_fans'
]

def get_page_token(user_token, page_id):
    url = f"https://graph.facebook.com/{API_VERSION}/me/accounts"
    params = {'access_token': user_token}
    try:
        resp = requests.get(url, params=params)
        data = resp.json().get('data', [])
        for page in data:
            if page.get('id') == page_id:
                print(f"✅ Found Page Token for {page.get('name')}")
                return page.get('access_token')
        print(f"⚠️ Page {page_id} not found in user accounts. Using original token.")
        return user_token
    except Exception as e:
        print(f"Error getting page token: {e}")
        return user_token

def test_metric(metric, token):
    url = f"https://graph.facebook.com/{API_VERSION}/{PAGE_ID}/insights"
    
    # Test for yesterday
    until = datetime.now()
    since = until - timedelta(days=2)
    
    params = {
        'access_token': token,
        'metric': metric,
        'period': 'day',
        'since': since.strftime('%Y-%m-%d'),
        'until': until.strftime('%Y-%m-%d')
    }
    
    try:
        resp = requests.get(url, params=params)
        data = resp.json()
        
        if resp.ok:
            print(f"✅ {metric}: OK")
            return True
        else:
            err = data.get('error', {}).get('message', 'Unknown error')
            print(f"❌ {metric}: FAIL - {err}")
            return False
            
    except Exception as e:
        print(f"❌ {metric}: EXCEPTION - {e}")
        return False

print("="*30)
print("TESTING FACEBOOK METRICS")
print("="*30)

FINAL_TOKEN = get_page_token(USER_TOKEN, PAGE_ID)

success_count = 0
for m in CANDIDATE_METRICS:
    if test_metric(m, FINAL_TOKEN):
        success_count += 1

print("="*30)
print(f"Valid Metrics: {success_count}/{len(CANDIDATE_METRICS)}")
