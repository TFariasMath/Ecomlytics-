
import os
import requests
from dotenv import load_dotenv

load_dotenv()

USER_TOKEN = os.getenv('FB_ACCESS_TOKEN')
PAGE_ID = os.getenv('FB_PAGE_ID')
API_VERSION = "v19.0"

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

def test_basic_fields(token):
    # Fetch basic page fields (not insights)
    url = f"https://graph.facebook.com/{API_VERSION}/{PAGE_ID}"
    params = {
        'access_token': token,
        'fields': 'id,name,fan_count,followers_count,verification_status'
    }
    
    try:
        print(f"Querying: {url}")
        resp = requests.get(url, params=params)
        data = resp.json()
        
        if resp.ok:
            print("✅ Basic Fields Request Successful!")
            print(data)
            return True
        else:
            print(f"❌ Basic Fields Failed: {data}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

print("="*30)
print("TESTING BASIC FACEBOOK ACCESS")
print("="*30)

FINAL_TOKEN = get_page_token(USER_TOKEN, PAGE_ID)
test_basic_fields(FINAL_TOKEN)
