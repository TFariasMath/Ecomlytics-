"""
Central Configuration Module

This module loads configuration from environment variables (.env file)
and provides typed configuration classes for all external services.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Load environment variables from .env file
env_path = PROJECT_ROOT / '.env'
if env_path.exists():
    try:
        # Try UTF-8 first
        load_dotenv(env_path, encoding='utf-8')
    except UnicodeDecodeError:
        try:
            # Fallback to latin-1 if UTF-8 fails
            load_dotenv(env_path, encoding='latin-1')
        except Exception as e:
            # If all else fails, try without encoding specification
            print(f"Warning: Could not load .env file with standard encodings: {e}")
            try:
                load_dotenv(env_path, encoding='utf-8', override=False)
            except:
                pass  # Continue without .env file
else:
    # Try to load from environment anyway (useful for production deployments)
    load_dotenv()


class ConfigurationError(Exception):
    """Raised when configuration is missing or invalid."""
    pass


class WooCommerceConfig:
    """WooCommerce API Configuration"""
    
    @staticmethod
    def get_url() -> str:
        """Get WooCommerce store URL."""
        url = os.getenv('WC_URL')
        if not url:
            raise ConfigurationError(
                "WC_URL not found in environment variables. "
                "Please configure it in .env file or setup page."
            )
        return url
    
    @staticmethod
    def get_consumer_key() -> str:
        """Get WooCommerce Consumer Key."""
        key = os.getenv('WC_CONSUMER_KEY')
        if not key:
            raise ConfigurationError(
                "WC_CONSUMER_KEY not found in environment variables. "
                "Please configure it in .env file or setup page."
            )
        return key
    
    @staticmethod
    def get_consumer_secret() -> str:
        """Get WooCommerce Consumer Secret."""
        secret = os.getenv('WC_CONSUMER_SECRET')
        if not secret:
            raise ConfigurationError(
                "WC_CONSUMER_SECRET not found in environment variables. "
                "Please configure it in .env file or setup page."
            )
        return secret
    
    @staticmethod
    def is_configured() -> bool:
        """Check if WooCommerce is configured."""
        try:
            return bool(
                os.getenv('WC_URL') and 
                os.getenv('WC_CONSUMER_KEY') and 
                os.getenv('WC_CONSUMER_SECRET')
            )
        except Exception:
            return False


class GoogleAnalyticsConfig:
    """Google Analytics 4 Configuration"""
    
    @staticmethod
    def get_key_file_path() -> str:
        """Get path to Google Cloud Service Account JSON file."""
        key_file = os.getenv('GA4_KEY_FILE')
        if not key_file:
            raise ConfigurationError(
                "GA4_KEY_FILE not found in environment variables. "
                "Please configure it in .env file or setup page."
            )
        
        # Handle both absolute and relative paths
        key_path = Path(key_file)
        if not key_path.is_absolute():
            key_path = PROJECT_ROOT / key_file
        
        if not key_path.exists():
            raise ConfigurationError(
                f"GA4 key file not found at: {key_path}. "
                f"Please upload the JSON file and update the path in .env"
            )
        
        return str(key_path)
    
    @staticmethod
    def get_property_id() -> str:
        """Get Google Analytics 4 Property ID."""
        property_id = os.getenv('GA4_PROPERTY_ID')
        if not property_id:
            raise ConfigurationError(
                "GA4_PROPERTY_ID not found in environment variables. "
                "Please configure it in .env file or setup page."
            )
        return property_id
    
    @staticmethod
    def is_configured() -> bool:
        """Check if Google Analytics is configured."""
        try:
            key_file = os.getenv('GA4_KEY_FILE')
            if not key_file:
                return False
            
            key_path = Path(key_file)
            if not key_path.is_absolute():
                key_path = PROJECT_ROOT / key_file
            
            return bool(
                os.getenv('GA4_PROPERTY_ID') and 
                key_path.exists()
            )
        except Exception:
            return False


class FacebookConfig:
    """Facebook Page Insights Configuration"""
    
    @staticmethod
    def get_access_token() -> str:
        """Get Facebook Access Token."""
        token = os.getenv('FB_ACCESS_TOKEN')
        if not token:
            raise ConfigurationError(
                "FB_ACCESS_TOKEN not found in environment variables. "
                "Please configure it in .env file or setup page."
            )
        return token
    
    @staticmethod
    def get_page_id() -> str:
        """Get Facebook Page ID."""
        page_id = os.getenv('FB_PAGE_ID')
        if not page_id:
            raise ConfigurationError(
                "FB_PAGE_ID not found in environment variables. "
                "Please configure it in .env file or setup page."
            )
        return page_id
    
    @staticmethod
    def get_api_version() -> str:
        """Get Facebook Graph API version."""
        return os.getenv('FB_API_VERSION', 'v19.0')
    
    @staticmethod
    def is_configured() -> bool:
        """Check if Facebook is configured."""
        try:
            return bool(
                os.getenv('FB_ACCESS_TOKEN') and 
                os.getenv('FB_PAGE_ID')
            )
        except Exception:
            return False


class DatabaseConfig:
    """Database Configuration - Supports SQLite and PostgreSQL"""
    
    @staticmethod
    def get_db_type() -> str:
        """Get database type from environment. Returns 'sqlite' or 'postgresql'."""
        return os.getenv('DATABASE_TYPE', 'sqlite').lower()
    
    @staticmethod
    def get_database_url() -> str:
        """Get PostgreSQL connection URL."""
        return os.getenv('DATABASE_URL', '')
    
    @staticmethod
    def is_postgresql() -> bool:
        """Check if using PostgreSQL."""
        return DatabaseConfig.get_db_type() == 'postgresql'
    
    @staticmethod
    def is_sqlite() -> bool:
        """Check if using SQLite."""
        return DatabaseConfig.get_db_type() == 'sqlite'
    
    @staticmethod
    def get_woocommerce_db_path() -> str:
        """Get WooCommerce database path (SQLite only)."""
        return str(PROJECT_ROOT / 'data' / 'woocommerce.db')
    
    @staticmethod
    def get_analytics_db_path() -> str:
        """Get Analytics database path (SQLite only)."""
        return str(PROJECT_ROOT / 'data' / 'analytics.db')
    
    @staticmethod
    def get_facebook_db_path() -> str:
        """Get Facebook database path (SQLite only)."""
        return str(PROJECT_ROOT / 'data' / 'facebook.db')
    
    @staticmethod
    def get_monitoring_db_path() -> str:
        """Get monitoring database path (SQLite only)."""
        return str(PROJECT_ROOT / 'data' / 'monitoring.db')


class TicketConfig:
    """Order Tickets Configuration for WhatsApp notifications"""
    
    @staticmethod
    def is_enabled() -> bool:
        """Check if order tickets feature is enabled."""
        return os.getenv('TICKETS_ENABLED', 'true').lower() == 'true'
    
    @staticmethod
    def get_ticket_config_path() -> str:
        """Get ticket configuration file path."""
        return str(PROJECT_ROOT / 'data' / 'ticket_config.json')


def check_configuration_status() -> dict:
    """
    Check configuration status for all services.
    
    Returns:
        Dict with service names as keys and boolean status as values
    """
    return {
        'woocommerce': WooCommerceConfig.is_configured(),
        'google_analytics': GoogleAnalyticsConfig.is_configured(),
        'facebook': FacebookConfig.is_configured(),
        'env_file_exists': env_path.exists()
    }


def get_missing_configuration() -> list:
    """
    Get list of services with missing configuration.
    
    Returns:
        List of service names that are not configured
    """
    status = check_configuration_status()
    missing = []
    
    if not status['woocommerce']:
        missing.append('WooCommerce')
    if not status['google_analytics']:
        missing.append('Google Analytics')
    if not status['facebook']:
        missing.append('Facebook')
    
    return missing


def get_view_requirements() -> dict:
    """
    Get API requirements for each dashboard view.
    
    Returns:
        Dict mapping view names to required services and their criticality
    """
    return {
        'Dashboard KPIs': {
            'required': ['woocommerce'],
            'optional': ['google_analytics'],
            'status_without_optional': 'partial'
        },
        'Historial de Órdenes': {
            'required': ['woocommerce'],
            'optional': [],
            'status_without_optional': 'active'
        },
        'Análisis de Ventas': {
            'required': ['woocommerce'],
            'optional': ['google_analytics'],
            'status_without_optional': 'partial'
        },
        'Catálogo de Productos': {
            'required': ['woocommerce'],
            'optional': [],
            'status_without_optional': 'active'
        },
        'Control de Inventario': {
            'required': ['woocommerce'],
            'optional': [],
            'status_without_optional': 'active'
        },
        'Segmentación de Clientes': {
            'required': ['woocommerce'],
            'optional': [],
            'status_without_optional': 'active'
        },
        'Tráfico y Redes Sociales': {
            'required': ['woocommerce'],
            'optional': ['google_analytics', 'facebook'],
            'status_without_optional': 'partial'  # Accessible with limited functionality
        },
        'Impuestos y Declaraciones': {
            'required': ['woocommerce'],
            'optional': [],
            'status_without_optional': 'active'
        }
    }


def get_view_status(view_name: str) -> str:
    """
    Get the status of a specific view based on configured APIs.
    
    Args:
        view_name: Name of the view to check
        
    Returns:
        'active' | 'partial' | 'locked'
    """
    requirements = get_view_requirements().get(view_name, {})
    if not requirements:
        return 'locked'
    
    config_status = check_configuration_status()
    
    # Check if all required services are configured
    required = requirements.get('required', [])
    all_required_met = all(config_status.get(service, False) for service in required)
    
    if not all_required_met:
        return 'locked'
    
    # Check optional services
    optional = requirements.get('optional', [])
    if not optional:
        # No optional services, fully active
        return 'active'
    
    # Check if any optional service is configured
    any_optional_met = any(config_status.get(service, False) for service in optional)
    
    if any_optional_met:
        # All required + at least one optional
        return 'active'
    else:
        # All required but no optional
        # For most views this means 'partial', but for some it could mean 'locked'
        return requirements.get('status_without_optional', 'partial')


def get_all_views_status() -> dict:
    """
    Get status for all dashboard views.
    
    Returns:
        Dict mapping view names to their status ('active' | 'partial' | 'locked')
    """
    return {
        view_name: get_view_status(view_name)
        for view_name in get_view_requirements().keys()
    }


def can_access_view(view_name: str) -> bool:
    """
    Check if user can access a specific view.
    A view is accessible if it's 'active' or 'partial' (not 'locked').
    
    Args:
        view_name: Name of the view to check
        
    Returns:
        True if view is accessible, False if locked
    """
    status = get_view_status(view_name)
    return status in ['active', 'partial']


def get_missing_services_for_view(view_name: str) -> list:
    """
    Get list of missing required services for a specific view.
    
    Args:
        view_name: Name of the view to check
        
    Returns:
        List of service names that are required but not configured
    """
    requirements = get_view_requirements().get(view_name, {})
    if not requirements:
        return []
    
    config_status = check_configuration_status()
    required = requirements.get('required', [])
    
    missing = []
    for service in required:
        if not config_status.get(service, False):
            # Map internal names to user-friendly names
            service_names = {
                'woocommerce': 'WooCommerce',
                'google_analytics': 'Google Analytics',
                'facebook': 'Facebook'
            }
            missing.append(service_names.get(service, service))
    
    return missing


def get_all_database_paths() -> dict:
    """
    Get paths to all database files.
    
    Returns:
        Dict mapping database names to their file paths
    """
    return {
        'woocommerce': DatabaseConfig.get_woocommerce_db_path(),
        'analytics': DatabaseConfig.get_analytics_db_path(),
        'facebook': DatabaseConfig.get_facebook_db_path(),
        'monitoring': DatabaseConfig.get_monitoring_db_path()
    }


def list_service_account_keys() -> list:
    """
    Find all Google Analytics service account JSON files in project root.
    
    Returns:
        List of Path objects for found service account JSON files
    """
    json_files = []
    
    # Look in project root
    for file in PROJECT_ROOT.glob('*.json'):
        # Skip certain files
        if file.name not in ['package.json', 'tsconfig.json']:
            # Basic check if it looks like a service account key
            try:
                import json
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'type' in data and data.get('type') == 'service_account':
                        json_files.append(file)
            except:
                pass
    
    return json_files


def reset_configuration(backup: bool = True) -> bool:
    """
    Reset .env file to template state.
    
    Args:
        backup: Whether to backup current .env before resetting
    
    Returns:
        True if successful, False otherwise
    """
    env_file = PROJECT_ROOT / '.env'
    env_example = PROJECT_ROOT / '.env.example'
    
    try:
        # Backup if requested
        if backup and env_file.exists():
            from datetime import datetime
            backup_name = f'.env.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
            backup_path = PROJECT_ROOT / 'backups' / backup_name
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            import shutil
            shutil.copy2(env_file, backup_path)
        
        # Get template content
        if not env_example.exists():
            # Create basic template
            template_content = """# ========================================
# CONFIGURACIÓN DE CREDENCIALES
# ========================================
# Completa con tus credenciales reales

# WOOCOMMERCE API
WC_URL=https://tu-tienda.com
WC_CONSUMER_KEY=ck_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
WC_CONSUMER_SECRET=cs_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# GOOGLE ANALYTICS 4
GA4_KEY_FILE=your-service-account-key.json
GA4_PROPERTY_ID=123456789

# FACEBOOK PAGE INSIGHTS
FB_ACCESS_TOKEN=EAAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
FB_PAGE_ID=1234567890123456
FB_API_VERSION=v19.0
"""
        else:
            with open(env_example, 'r', encoding='utf-8') as f:
                template_content = f.read()
        
        # Write template to .env
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        return True
        
    except Exception as e:
        print(f"Error resetting configuration: {e}")
        return False
