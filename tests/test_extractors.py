"""
Tests unitarios para extractores de datos.

Prueba las funciones de extracción de GA4 y WooCommerce.
"""

import pytest
import sys
import os
import pandas as pd

# Agregar path para imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.database import save_dataframe_to_db, get_last_extraction_date


class TestDatabaseUtils:
    """Tests para utilidades de base de datos."""
    
    def test_save_dataframe_to_db(self, temp_db, sample_ga4_data):
        """
        Test guardar DataFrame en base de datos.
        """
        # Save data
        save_dataframe_to_db(
            df=sample_ga4_data,
            table_name='test_table',
            db_path=temp_db,
            if_exists='replace'
        )
        
        # Verify
        import sqlite3
        conn = sqlite3.connect(temp_db)
        df_loaded = pd.read_sql('SELECT * FROM test_table', conn)
        conn.close()
        
        assert len(df_loaded) == len(sample_ga4_data)
        assert 'Fecha' in df_loaded.columns
    
    def test_save_empty_dataframe(self, temp_db):
        """
        Test que DataFrame vacío no falla.
        """
        empty_df = pd.DataFrame()
        # Should not raise exception
        save_dataframe_to_db(
            df=empty_df,
            table_name='empty_table',
            db_path=temp_db
        )
    
    def test_get_last_extraction_date_default(self, temp_db):
        """
        Test obtener fecha por defecto cuando tabla no existe.
        """
        last_date = get_last_extraction_date(
            table_name='nonexistent',
            date_column='Fecha',
            db_path=temp_db,
            default_date='2023-01-01'
        )
        
        assert last_date == '2023-01-01'
    
    def test_get_last_extraction_date_with_data(self, temp_db):
        """
        Test obtener última fecha de extracción con datos.
        """
        # Create test data
        df = pd.DataFrame({
            'Fecha': ['2023-12-01', '2023-12-15', '2023-12-10']
        })
        
        save_dataframe_to_db(df, 'test_dates', temp_db)
        
        last_date = get_last_extraction_date(
            table_name='test_dates',
            date_column='Fecha',
            db_path=temp_db
        )
        
        assert last_date == '2023-12-15'


class TestWooCommerceExtractor:
    """Tests para extractor de WooCommerce."""
    
    def test_process_data(self, sample_wc_orders):
        """
        Test procesamiento de órdenes de WooCommerce.
        """
        from etl.extract_woocommerce import process_data
        
        df_orders, df_items = process_data(sample_wc_orders)
        
        # Verify orders
        assert len(df_orders) == 2
        assert 'order_id' in df_orders.columns
        assert 'total' in df_orders.columns
        assert df_orders['total'].sum() == 300.0  # 100 + 200
        
        # Verify items
        assert len(df_items) == 2
        assert 'product_id' in df_items.columns
        assert 'quantity' in df_items.columns
    
    def test_process_data_with_invalid_status(self):
        """
        Test que órdenes con status inválido son filtradas.
        """
        from etl.extract_woocommerce import process_data
        
        invalid_orders = [
            {
                'id': 1,
                'status': 'cancelled',  # Status inválido
                'total': '100.00',
                'date_created': '2023-12-01T10:00:00',
                'line_items': []
            }
        ]
        
        df_orders, df_items = process_data(invalid_orders)
        
        # Should be empty
        assert len(df_orders) == 0
        assert len(df_items) == 0


class TestAPIClient:
    """Tests para cliente API."""
    
    def test_get_usd_clp_rate_fallback(self, mocker):
        """
        Test fallback de tasa de cambio cuando API falla.
        """
        from utils.api_client import get_usd_clp_rate
        
        # Mock requests to raise exception
        mocker.patch('utils.api_client.make_api_request', side_effect=Exception("API Error"))
        
        rate = get_usd_clp_rate(fallback_rate=950.0)
        
        assert rate == 950.0


# ===== Tests de Integración Básicos =====

@pytest.mark.integration
class TestIntegration:
    """Tests de integración básicos."""
    
    def test_full_wc_extraction_flow(self, temp_db, mock_wc_api):
        """
        Test flujo completo de extracción de WooCommerce.
        """
        from etl.extract_woocommerce import extract_orders
        
        # Setup: configurar DB temporal
        import etl.extract_woocommerce as wc_module
        original_db = wc_module.DATABASE_NAME
        wc_module.DATABASE_NAME = temp_db
        
        try:
            # Execute extraction
            extract_orders(mock_wc_api, start_date='2023-01-01')
            
            # Verify data was saved
            import sqlite3
            conn = sqlite3.connect(temp_db)
            
            orders = pd.read_sql('SELECT * FROM wc_orders', conn)
            items = pd.read_sql('SELECT * FROM wc_order_items', conn)
            
            conn.close()
            
            assert len(orders) > 0
            assert len(items) > 0
            
        finally:
            # Restore original DB path
            wc_module.DATABASE_NAME = original_db
