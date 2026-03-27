"""
Internationalization (i18n) Module

Provides multi-language support for the dashboard.
Currently supports: Spanish (es) and English (en)
"""

TRANSLATIONS = {
    'es': {
        # Navigation
        'nav_dashboard': '📊 Dashboard KPIs',
        'nav_sales': '💰 Análisis de Ventas',
        'nav_history': '📋 Historial de Ventas',
        'nav_products': '📦 Productos Top',
        'nav_inventory': '🏪 Gestión de Inventario',
        'nav_customers': '👥 Segmentación de Clientes',
        'nav_traffic': '🌐 Tráfico y Redes Sociales',
        'nav_taxes': '🏛️ Impuestos y Declaraciones',
        'nav_monitoring': '📊 Monitoreo ETL',
        
        # Dashboard Metrics
        'total_sales': 'Ingresos Totales',
        'total_orders': 'Pedidos',
        'avg_ticket': 'Ticket Promedio',
        'total_customers': 'Clientes',
        'conversion_rate': 'Tasa de Conversión',
        
        # Actions
        'refresh_data': 'Actualizar Datos',
        'export_pdf': 'Exportar a PDF',
        'export_excel': 'Exportar a Excel',
        'download': 'Descargar',
        'save': 'Guardar',
        'cancel': 'Cancelar',
        'test_connection': 'Probar Conexión',
        
        # Time Periods
        'today': 'Hoy',
        'yesterday': 'Ayer',
        'last_7_days': 'Últimos 7 días',
        'last_30_days': 'Últimos 30 días',
        'this_month': 'Este mes',
        'last_month': 'Mes pasado',
        'this_year': 'Este año',
        'custom': 'Personalizado',
        
        # Status
        'loading': 'Cargando...',
        'success': 'Éxito',
        'error': 'Error',
        'warning': 'Advertencia',
        'no_data': 'No hay datos disponibles',
        'configured': 'Configurado',
        'not_configured': 'No configurado',
        
        # Setup
        'setup_title': 'Configuración de Credenciales',
        'woocommerce_section': 'WooCommerce',
        'analytics_section': 'Google Analytics 4',
        'facebook_section': 'Facebook Page Insights',
        'save_config': 'Guardar Configuración',
        
        # Monitoring
        'last_execution': 'Última Ejecución',
        'success_rate': 'Tasa de Éxito',
        'avg_duration': 'Duración Promedio',
        'total_records': 'Total Registros',
        'recent_errors': 'Errores Recientes',
        
        # Misc
        'language': 'Idioma',
        'support': 'Soporte',
        'documentation': 'Documentación',
    },
    
    'en': {
        # Navigation
        'nav_dashboard': '📊 Dashboard KPIs',
        'nav_sales': '💰 Sales Analysis',
        'nav_history': '📋 Sales History',
        'nav_products': '📦 Top Products',
        'nav_inventory': '🏪 Inventory Management',
        'nav_customers': '👥 Customer Segmentation',
        'nav_traffic': '🌐 Traffic & Social Media',
        'nav_taxes': '🏛️ Taxes & Declarations',
        'nav_monitoring': '📊 ETL Monitoring',
        
        # Dashboard Metrics
        'total_sales': 'Total Revenue',
        'total_orders': 'Orders',
        'avg_ticket': 'Average Ticket',
        'total_customers': 'Customers',
        'conversion_rate': 'Conversion Rate',
        
        # Actions
        'refresh_data': 'Refresh Data',
        'export_pdf': 'Export to PDF',
        'export_excel': 'Export to Excel',
        'download': 'Download',
        'save': 'Save',
        'cancel': 'Cancel',
        'test_connection': 'Test Connection',
        
        # Time Periods
        'today': 'Today',
        'yesterday': 'Yesterday',
        'last_7_days': 'Last 7 days',
        'last_30_days': 'Last 30 days',
        'this_month': 'This month',
        'last_month': 'Last month',
        'this_year': 'This year',
        'custom': 'Custom',
        
        # Status
        'loading': 'Loading...',
        'success': 'Success',
        'error': 'Error',
        'warning': 'Warning',
        'no_data': 'No data available',
        'configured': 'Configured',
        'not_configured': 'Not configured',
        
        # Setup
        'setup_title': 'Credentials Setup',
        'woocommerce_section': 'WooCommerce',
        'analytics_section': 'Google Analytics 4',
        'facebook_section': 'Facebook Page Insights',
        'save_config': 'Save Configuration',
        
        # Monitoring
        'last_execution': 'Last Execution',
        'success_rate': 'Success Rate',
        'avg_duration': 'Average Duration',
        'total_records': 'Total Records',
        'recent_errors': 'Recent Errors',
        
        # Misc
        'language': 'Language',
        'support': 'Support',
        'documentation': 'Documentation',
    }
}


def t(key: str, lang: str = 'es') -> str:
    """
    Translate a key to the specified language
    
    Args:
        key: Translation key
        lang: Language code ('es' or 'en'), defaults to 'es'
    
    Returns:
        Translated string, or the key itself if not found
    
    Example:
        >>> t('total_sales', 'en')
        'Total Revenue'
        >>> t('total_sales', 'es')
        'Ingresos Totales'
    """
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS['es'])
    return lang_dict.get(key, key)


def get_available_languages() -> list:
    """
    Get list of available language codes
    
    Returns:
        List of language codes
    """
    return list(TRANSLATIONS.keys())


def get_language_display_name(lang_code: str) -> str:
    """
    Get display name for a language code
    
    Args:
        lang_code: Language code ('es' or 'en')
    
    Returns:
        Display name with flag
    """
    names = {
        'es': '🇪🇸 Español',
        'en': '🇺🇸 English'
    }
    return names.get(lang_code, lang_code)
