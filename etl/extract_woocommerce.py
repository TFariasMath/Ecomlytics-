"""
Extractor de datos de WooCommerce.

Este módulo extrae datos de WooCommerce y los almacena en SQLite con:
- Logging estructurado
- Carga incremental
- Retry logic automático
- Type hints
"""

import os
import sys
import pandas as pd
from woocommerce import API
from datetime import datetime
from typing import Tuple, List, Dict, Any

# Agregar paths para imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config.logging_config import setup_logger, log_execution_time
from config.settings import WooCommerceConfig, DatabaseConfig
from utils.database import save_dataframe_to_db, get_last_extraction_date, get_db_connection, upsert_dataframe
from utils.retry_handler import retry_on_api_error
from utils.data_quality import WooCommerceDataValidator, validate_and_log
from utils.monitoring import track_etl_execution
from utils.database import ensure_schema_match

# Setup logger
logger = setup_logger(__name__)

# Database configuration
DATABASE_NAME = DatabaseConfig.get_woocommerce_db_path()
MONITORING_DB = DatabaseConfig.get_monitoring_db_path()

# Batch size for processing
BATCH_SIZE = 500


@retry_on_api_error(max_attempts=3, min_wait=4, max_wait=60)
def get_wc_api() -> API:
    """
    Initializes WooCommerce API connection using configuration.
    
    Returns:
        WooCommerce API client
    """
    url = WooCommerceConfig.get_url()
    consumer_key = WooCommerceConfig.get_consumer_key()
    consumer_secret = WooCommerceConfig.get_consumer_secret()
    
    logger.info(f"Conectando a WooCommerce API: {url}")
    api = API(
        url=url,
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        version="wc/v3",
        timeout=30
    )
    logger.info("✅ Conexión WooCommerce establecida")
    return api


def extract_orders(wcapi: API, start_date: str = "2023-01-01", metrics=None) -> None:
    """
    Extracts orders from WooCommerce incrementally.
    
    Args:
        wcapi: WooCommerce API client
        start_date: Start date for extraction (format: YYYY-MM-DD)
        metrics: ETLMetrics object for tracking (optional)
    """
    logger.info(f"📦 Extrayendo órdenes desde WooCommerce (desde {start_date})...")
    
    page = 1
    total_extracted = 0
    batch_orders = []
    
    # Status filter para coincidir con reportes de revenue de WooCommerce
    # Incluye todos los estados que representan ventas/pedidos activos:
    # - completed: Pedido completado y enviado
    # - completoenviado: Estado custom (completado enviado)
    # - processing: Pedido en procesamiento (pago recibido)
    # - porsalir: Estado custom (listo para salir/enviar)
    # - on-hold: Pedido en espera (pendiente de pago/confirmación)
    valid_statuses = "completed,completoenviado,processing,porsalir,on-hold"
    logger.info(f"Filtrando por status: {valid_statuses}")
    
    while True:
        try:
            logger.info(f"📄 Fetching page {page}...")
            
            # Extrae todas las órdenes que WooCommerce considera ventas
            orders = wcapi.get("orders", params={
                "per_page": 100,
                "page": page,
                "status": valid_statuses,
                "after": f"{start_date}T00:00:00"  # Filtrar por fecha
            }).json()
            
            if not orders or not isinstance(orders, list):
                logger.info("No más órdenes disponibles")
                break
            
            if len(orders) == 0:
                break
                
            batch_orders.extend(orders)
            total_extracted += len(orders)
            logger.debug(f"Añadidas {len(orders)} órdenes al batch actual")
            
            # Save every BATCH_SIZE items
            if len(batch_orders) >= BATCH_SIZE:
                logger.info(f"💾 Guardando batch de {len(batch_orders)} órdenes...")
                df_orders, df_items = process_data(batch_orders)
                
                # Validar datos
                is_valid_orders = validate_and_log(
                    df_orders,
                    WooCommerceDataValidator.validate_orders,
                    "WooCommerce Orders"
                )
                
                is_valid_items = validate_and_log(
                    df_items,
                    WooCommerceDataValidator.validate_order_items,
                    "WooCommerce Order Items"
                )
                
                if not is_valid_orders and metrics:
                    metrics.add_warning("Validación fallida en orders")
                
                if not is_valid_items and metrics:
                    metrics.add_warning("Validación fallida en order items")
                
                # Usar upsert para prevenir duplicados
                # Ensure schema matches before upserting
                ensure_schema_match('wc_orders', df_orders, DATABASE_NAME)
                ensure_schema_match('wc_order_items', df_items, DATABASE_NAME)
                
                upsert_dataframe(df_orders, 'wc_orders', DATABASE_NAME, unique_keys=['order_id'])
                upsert_dataframe(df_items, 'wc_order_items', DATABASE_NAME, 
                               unique_keys=['order_id', 'product_id', 'variation_id'])
                
                batch_orders = []  # Clear batch

            page += 1
            
        except Exception as e:
            error_msg = f"Error extrayendo órdenes en página {page}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            if metrics:
                metrics.add_error(error_msg)
            break
    
    # Save remaining orders
    if batch_orders:
        logger.info(f"💾 Guardando batch final de {len(batch_orders)} órdenes...")
        df_orders, df_items = process_data(batch_orders)
        
        # Validar
        validate_and_log(df_orders, WooCommerceDataValidator.validate_orders, "WooCommerce Orders")
        validate_and_log(df_items, WooCommerceDataValidator.validate_order_items, "WooCommerce Order Items")
        
        # Upsert
        ensure_schema_match('wc_orders', df_orders, DATABASE_NAME)
        ensure_schema_match('wc_order_items', df_items, DATABASE_NAME)
        
        upsert_dataframe(df_orders, 'wc_orders', DATABASE_NAME, unique_keys=['order_id'])
        upsert_dataframe(df_items, 'wc_order_items', DATABASE_NAME, 
                       unique_keys=['order_id', 'product_id', 'variation_id'])

    logger.info(f"✅ Total orders extracted: {total_extracted}")
    logger.info(f"   Status filter: {valid_statuses}")
    
    if metrics:
        metrics.add_rows(total_extracted)
        metrics.set_metadata('orders_extracted', total_extracted)
        metrics.add_rows(total_extracted)
        metrics.set_metadata('orders_extracted', total_extracted)


def extract_products(wcapi: API, metrics=None) -> None:
    """
    Extracts all products from WooCommerce.
    
    Args:
        wcapi: WooCommerce API client
        metrics: ETLMetrics object
    """
    logger.info("📦 Extrayendo productos desde WooCommerce...")
    
    page = 1
    all_products = []
    
    while True:
        try:
            logger.info(f"📄 Fetching products page {page}...")
            products = wcapi.get("products", params={"per_page": 100, "page": page}).json()
            
            if not products or not isinstance(products, list):
                break
            
            if len(products) == 0:
                break
                
            all_products.extend(products)
            logger.debug(f"Añadidos {len(products)} productos")
            
            page += 1
            
        except Exception as e:
            logger.error(f"Error extrayendo productos: {e}")
            break
            
    if all_products:
        logger.info(f"💾 Procesando {len(all_products)} productos...")
        
        product_data = []
        for p in all_products:
            # Extract categories as comma-separated string
            categories = [c.get('name') for c in p.get('categories', [])]
            cat_str = ",".join(categories)
            
            # Get dimensions
            dims = p.get('dimensions', {})
            
            item = {
                'product_id': p.get('id'),
                'name': p.get('name'),
                'sku': p.get('sku'),
                'price': float(p.get('price') or 0),
                'regular_price': float(p.get('regular_price') or 0),
                'sale_price': float(p.get('sale_price') or 0),
                'status': p.get('status'),
                'categories': cat_str,
                # Inventory Management Fields
                'stock_quantity': p.get('stock_quantity'),
                'stock_status': p.get('stock_status', 'instock'),  # instock, outofstock, onbackorder
                'manage_stock': 1 if p.get('manage_stock') else 0,  # Boolean as int
                'backorders': p.get('backorders', 'no'),  # no, notify, yes
                'backorders_allowed': 1 if p.get('backorders_allowed') else 0,
                'low_stock_amount': p.get('low_stock_amount'),  # Threshold for low stock
                'sold_individually': 1 if p.get('sold_individually') else 0,  # Only 1 per order
                # Logistics Fields
                'weight': p.get('weight'),
                'length': dims.get('length') if dims else None,
                'width': dims.get('width') if dims else None,
                'height': dims.get('height') if dims else None,
                # Performance Fields
                'total_sales': p.get('total_sales', 0),  # Historical sales count
                'rating_count': p.get('rating_count', 0),
                'average_rating': float(p.get('average_rating') or 0),
                'date_modified': p.get('date_modified')
            }
            product_data.append(item)
            
        df_products = pd.DataFrame(product_data)
        
        # Ensure schema match
        ensure_schema_match('wc_products', df_products, DATABASE_NAME)
        
        # Upsert
        upsert_dataframe(
            df_products, 
            'wc_products', 
            DATABASE_NAME, 
            unique_keys=['product_id']
        )
        
        if metrics:
            metrics.set_metadata('products_extracted', len(df_products))
        
        logger.info(f"✅ {len(df_products)} productos actualizados")

def extract_customers(wcapi: API, metrics=None) -> None:
    """
    Extracts all customers from WooCommerce.
    
    Args:
        wcapi: WooCommerce API client
        metrics: ETLMetrics object
    """
    logger.info("👥 Extrayendo clientes desde WooCommerce...")
    
    page = 1
    all_customers = []
    
    while True:
        try:
            logger.info(f"📄 Fetching customers page {page}...")
            customers = wcapi.get("customers", params={"per_page": 100, "page": page}).json()
            
            if not customers or not isinstance(customers, list):
                break
            
            if len(customers) == 0:
                break
                
            all_customers.extend(customers)
            logger.debug(f"Añadidos {len(customers)} clientes")
            
            page += 1
            
        except Exception as e:
            logger.error(f"Error extrayendo clientes: {e}")
            break
            
    if all_customers:
        logger.info(f"💾 Procesando {len(all_customers)} clientes...")
        
        customer_data = []
        for c in all_customers:
            # Get billing info
            billing = c.get('billing', {})
            
            item = {
                'customer_id': c.get('id'),
                'email': c.get('email', ''),
                'username': c.get('username', ''),
                'first_name': c.get('first_name', ''),
                'last_name': c.get('last_name', ''),
                'role': c.get('role', 'customer'),
                'date_created': c.get('date_created'),
                'date_modified': c.get('date_modified'),
                # Billing address
                'billing_city': billing.get('city', ''),
                'billing_state': billing.get('state', ''),
                'billing_postcode': billing.get('postcode', ''),
                'billing_country': billing.get('country', ''),
                'billing_phone': billing.get('phone', ''),
                # Customer metrics from WooCommerce
                'orders_count': c.get('orders_count', 0),
                'total_spent': float(c.get('total_spent', 0)),
                'avatar_url': c.get('avatar_url', '')
            }
            customer_data.append(item)
            
        df_customers = pd.DataFrame(customer_data)
        
        # Ensure schema match
        ensure_schema_match('wc_customers', df_customers, DATABASE_NAME)
        
        # Upsert
        upsert_dataframe(
            df_customers, 
            'wc_customers', 
            DATABASE_NAME, 
            unique_keys=['customer_id']
        )
        
        if metrics:
            metrics.set_metadata('customers_extracted', len(df_customers))
        
        logger.info(f"✅ {len(df_customers)} clientes actualizados")

def process_data(orders: List[Dict[str, Any]]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Processes raw orders into structured DataFrames.
    
    Args:
        orders: List of order dictionaries from WooCommerce API
    
    Returns:
        Tuple of (orders_df, items_df)
    """
    logger.debug(f"Procesando {len(orders)} órdenes...")
    
    order_data = []
    order_items_data = []
    orders_without_items = []
    
    for order in orders:
        # Filter for active orders (incluye todos los estados de pedidos activos)
        # Incluye on-hold para mostrar pedidos pendientes de pago/confirmación
        if order.get('status') in ['completed', 'completoenviado', 'processing', 'porsalir', 'on-hold']:
            # Main Order Data with enhanced fields
            # Get payment and shipping info
            shipping_lines = order.get('shipping_lines', [])
            shipping_method = shipping_lines[0].get('method_title') if shipping_lines else ''
            
            item = {
                'order_id': order.get('id'),
                'date_created': order.get('date_created'),
                'status': order.get('status'),
                'total': float(order.get('total', 0)),
                'currency': order.get('currency'),
                # Breakdown fields
                'shipping_total': float(order.get('shipping_total', 0)),
                'discount_total': float(order.get('discount_total', 0)),
                'total_tax': float(order.get('total_tax', 0)),
                'cart_tax': float(order.get('cart_tax', 0)),
                'shipping_tax': float(order.get('shipping_tax', 0)),
                # Customer tracking
                'customer_id': order.get('customer_id', 0),  # 0 = guest checkout
                'customer_email': (order.get('billing', {}).get('email', '') if order.get('billing') else ''),
                'customer_name': (
                    f"{order.get('billing', {}).get('first_name', '')} {order.get('billing', {}).get('last_name', '')}".strip()
                    if order.get('billing') else ''
                ),
                # Billing Address (complete for fallback when shipping is empty)
                'billing_company': order.get('billing', {}).get('company', ''),
                'billing_address_1': order.get('billing', {}).get('address_1', ''),
                'billing_address_2': order.get('billing', {}).get('address_2', ''),
                'billing_city': order.get('billing', {}).get('city', ''),
                'billing_state': order.get('billing', {}).get('state', ''),
                'billing_postcode': order.get('billing', {}).get('postcode', ''),
                'billing_country': order.get('billing', {}).get('country', 'CL'),
                'billing_phone': order.get('billing', {}).get('phone', ''),
                # Shipping Address (complete for delivery)
                'shipping_first_name': order.get('shipping', {}).get('first_name', ''),
                'shipping_last_name': order.get('shipping', {}).get('last_name', ''),
                'shipping_address_1': order.get('shipping', {}).get('address_1', ''),
                'shipping_address_2': order.get('shipping', {}).get('address_2', ''),
                'shipping_city': order.get('shipping', {}).get('city', ''),
                'shipping_state': order.get('shipping', {}).get('state', ''),
                'shipping_postcode': order.get('shipping', {}).get('postcode', ''),
                'shipping_country': order.get('shipping', {}).get('country', 'CL'),
                # Payment & Shipping Methods
                'payment_method': order.get('payment_method', ''),
                'payment_method_title': order.get('payment_method_title', ''),
                'shipping_method': shipping_method,
                # Customer Note (delivery instructions)
                'customer_note': order.get('customer_note', ''),
                # Timestamps for operational analysis
                'date_completed': order.get('date_completed'),
                'date_paid': order.get('date_paid'),
                'date_modified': order.get('date_modified'),
                # Coupons
                'coupons_used': ",".join([c.get('code', '') for c in (order.get('coupon_lines') or [])])
            }

            order_data.append(item)
            
            # Line Items for Products
            line_items = order.get('line_items', [])
            if not line_items:
                orders_without_items.append(order.get('id'))
                
            for product in line_items:
                p_item = {
                    'order_id': order.get('id'),
                    'product_id': product.get('product_id'),
                    'product_name': product.get('name'),
                    'sku': product.get('sku', ''),
                    'quantity': product.get('quantity'),
                    'price': float(product.get('price', 0)),
                    'total': float(product.get('total', 0)),
                    'subtotal': float(product.get('subtotal', 0)),
                    'subtotal_tax': float(product.get('subtotal_tax', 0)),
                    'tax_class': product.get('tax_class', ''),
                    'variation_id': product.get('variation_id', 0),
                    'date_created': order.get('date_created')
                }
                order_items_data.append(p_item)
    
    # Alert about orders without items
    if orders_without_items:
        logger.warning(f"⚠️ {len(orders_without_items)} órdenes sin items: {orders_without_items[:10]}")
                
    df_orders = pd.DataFrame(order_data)
    df_items = pd.DataFrame(order_items_data)
    
    # Normalize Date
    if not df_orders.empty:
        df_orders['date_created'] = pd.to_datetime(df_orders['date_created']).dt.tz_localize(None)
        df_orders['date_only'] = df_orders['date_created'].dt.date
        logger.debug(f"Procesadas {len(df_orders)} órdenes")
        
    if not df_items.empty:
        df_items['date_created'] = pd.to_datetime(df_items['date_created']).dt.tz_localize(None)
        logger.debug(f"Procesados {len(df_items)} items")
        
    return df_orders, df_items


def init_db_if_needed() -> None:
    """
    Initializes database tables if they don't exist.
    Only drops tables on first run or if explicitly needed.
    """
    if not os.path.exists(DATABASE_NAME):
        logger.info("Base de datos no existe, será creada automáticamente")
        os.makedirs(os.path.dirname(DATABASE_NAME), exist_ok=True)


@log_execution_time(logger)
def main() -> None:
    """Main execution function with monitoring and data quality."""
    
    with track_etl_execution('extract_woocommerce', MONITORING_DB) as metrics:
        try:
            logger.info("="*50)
            logger.info("🚀 Iniciando extracción de WooCommerce")
            logger.info("="*50)
            
            # Validate configuration first
            if not WooCommerceConfig.is_configured():
                error_msg = "WooCommerce no está configurado. Por favor configura las credenciales en .env o via interfaz web."
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # Initialize DB
            init_db_if_needed()
            
            # Get WooCommerce API client
            wcapi = get_wc_api()
            metrics.set_metadata('source', 'WooCommerce')
            metrics.set_metadata('url', WooCommerceConfig.get_url())
            
            # FULL EXTRACTION: Always extract all orders from beginning
            # This ensures no data is missed due to incremental sync issues
            # The upsert logic handles duplicates automatically, so this is safe
            start_date = '2023-01-01'
            
            logger.info(f"📅 Extrayendo TODAS las órdenes desde: {start_date} (extracción completa)")
            metrics.set_metadata('start_date', start_date)
            metrics.set_metadata('extraction_mode', 'full')
            
            # Extract orders (pasa metrics para tracking)
            extract_orders(wcapi, start_date=start_date, metrics=metrics)
            
            # Extract products
            extract_products(wcapi, metrics=metrics)
            
            # Extract customers
            extract_customers(wcapi, metrics=metrics)
            
            logger.info("="*50)
            logger.info("✅ Extracción de WooCommerce completada")
            logger.info("="*50)
            
        except Exception as e:
            logger.error(f"Error crítico en ETL: {e}", exc_info=True)
            raise


if __name__ == "__main__":
    main()
