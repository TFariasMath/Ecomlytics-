"""
Configuration Validator

This module provides functions to validate API credentials
by testing actual connections to each service.
"""

import os
import requests
from typing import Dict, Tuple
from pathlib import Path

# Lazy imports to avoid circular dependencies
def _get_config_module():
    """Lazy load config settings to avoid circular imports."""
    from config import settings
    return settings


def validate_woocommerce(url: str, consumer_key: str, consumer_secret: str) -> Tuple[bool, str]:
    """
    Validate WooCommerce API credentials by attempting a connection.
    
    Args:
        url: WooCommerce store URL
        consumer_key: Consumer Key
        consumer_secret: Consumer Secret
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        from woocommerce import API
        
        # Create API instance
        wcapi = API(
            url=url,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            version="wc/v3",
            timeout=10
        )
        
        # Try to get system status (lightweight endpoint)
        response = wcapi.get("system_status")
        
        if response.status_code == 200:
            return True, "✅ WooCommerce connection successful!"
        else:
            return False, f"❌ WooCommerce API returned status {response.status_code}"
            
    except Exception as e:
        return False, f"❌ WooCommerce validation failed: {str(e)}"


def validate_google_analytics(key_file_path: str, property_id: str) -> Tuple[bool, str]:
    """
    Validate Google Analytics 4 credentials.
    
    Args:
        key_file_path: Path to service account JSON file
        property_id: GA4 Property ID
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric
        from google.oauth2 import service_account
        
        # Check if file exists
        if not Path(key_file_path).exists():
            return False, f"❌ Key file not found at: {key_file_path}"
        
        # Load credentials
        try:
            creds = service_account.Credentials.from_service_account_file(key_file_path)
        except Exception as e:
            return False, f"❌ Invalid service account file: {str(e)}"
        
        # Try to create client and run a simple query
        client = BetaAnalyticsDataClient(credentials=creds)
        
        # Ensure property ID has correct format
        if not property_id.startswith('properties/'):
            property_id = f'properties/{property_id}'
        
        # Run minimal report request (last 7 days, sessions metric)
        request = RunReportRequest(
            property=property_id,
            date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
            metrics=[Metric(name="sessions")],
        )
        
        response = client.run_report(request)
        
        return True, f"✅ Google Analytics connection successful! (Retrieved {len(response.rows)} data points)"
        
    except Exception as e:
        error_msg = str(e)
        if "403" in error_msg or "permission" in error_msg.lower():
            return False, "❌ Permission denied. Ensure the service account has access to this GA4 property."
        elif "404" in error_msg or "not found" in error_msg.lower():
            return False, f"❌ Property ID {property_id} not found. Please verify the ID."
        else:
            return False, f"❌ Google Analytics validation failed: {error_msg}"


def validate_facebook(access_token: str, page_id: str, api_version: str = "v19.0") -> Tuple[bool, str]:
    """
    Validate Facebook API credentials.
    
    Args:
        access_token: Facebook Access Token
        page_id: Facebook Page ID
        api_version: Graph API version (default: v19.0)
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        base_url = f"https://graph.facebook.com/{api_version}"
        
        # First, check token validity
        debug_url = f"{base_url}/debug_token"
        debug_params = {
            'input_token': access_token,
            'access_token': access_token
        }
        
        debug_response = requests.get(debug_url, params=debug_params, timeout=10)
        
        if not debug_response.ok:
            return False, f"❌ Invalid access token (Status {debug_response.status_code})"
        
        debug_data = debug_response.json()
        if not debug_data.get('data', {}).get('is_valid'):
            return False, "❌ Access token is not valid or has expired"
        
        # Try to access the page
        page_url = f"{base_url}/{page_id}"
        page_params = {
            'access_token': access_token,
            'fields': 'name,id'
        }
        
        page_response = requests.get(page_url, params=page_params, timeout=10)
        
        if not page_response.ok:
            return False, f"❌ Cannot access page {page_id} (Status {page_response.status_code})"
        
        page_data = page_response.json()
        page_name = page_data.get('name', 'Unknown')
        
        return True, f"✅ Facebook connection successful! Connected to page: {page_name}"
        
    except requests.exceptions.Timeout:
        return False, "❌ Facebook API request timed out"
    except Exception as e:
        return False, f"❌ Facebook validation failed: {str(e)}"


def validate_all_configured_services() -> Dict[str, Dict[str, any]]:
    """
    Validate all configured services.
    
    Returns:
        Dict with service names as keys and validation results as values
        Each result contains: {'configured': bool, 'valid': bool, 'message': str}
    """
    settings = _get_config_module()
    results = {}
    
    # WooCommerce
    if settings.WooCommerceConfig.is_configured():
        try:
            url = settings.WooCommerceConfig.get_url()
            key = settings.WooCommerceConfig.get_consumer_key()
            secret = settings.WooCommerceConfig.get_consumer_secret()
            valid, message = validate_woocommerce(url, key, secret)
            results['woocommerce'] = {'configured': True, 'valid': valid, 'message': message}
        except Exception as e:
            results['woocommerce'] = {'configured': True, 'valid': False, 'message': str(e)}
    else:
        results['woocommerce'] = {'configured': False, 'valid': False, 'message': 'Not configured'}
    
    # Google Analytics
    if settings.GoogleAnalyticsConfig.is_configured():
        try:
            key_file = settings.GoogleAnalyticsConfig.get_key_file_path()
            property_id = settings.GoogleAnalyticsConfig.get_property_id()
            valid, message = validate_google_analytics(key_file, property_id)
            results['google_analytics'] = {'configured': True, 'valid': valid, 'message': message}
        except Exception as e:
            results['google_analytics'] = {'configured': True, 'valid': False, 'message': str(e)}
    else:
        results['google_analytics'] = {'configured': False, 'valid': False, 'message': 'Not configured'}
    
    # Facebook
    if settings.FacebookConfig.is_configured():
        try:
            token = settings.FacebookConfig.get_access_token()
            page_id = settings.FacebookConfig.get_page_id()
            api_version = settings.FacebookConfig.get_api_version()
            valid, message = validate_facebook(token, page_id, api_version)
            results['facebook'] = {'configured': True, 'valid': valid, 'message': message}
        except Exception as e:
            results['facebook'] = {'configured': True, 'valid': False, 'message': str(e)}
    else:
        results['facebook'] = {'configured': False, 'valid': False, 'message': 'Not configured'}
    
    return results
