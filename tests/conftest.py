"""
Fixtures compartidos para pytest.

Provee fixtures reutilizables para tests unitarios e integración.
"""

import pytest
import sqlite3
import os
import tempfile
import pandas as pd
from unittest.mock import MagicMock


@pytest.fixture
def temp_db():
    """
    Crea una base de datos temporal para tests.
    
    Yields:
        Path a la base de datos temporal
    """
    # Crear archivo temporal
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    yield path
    
    # Cleanup
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def sample_ga4_data():
    """
    Datos de ejemplo de GA4.
    
    Returns:
        DataFrame con datos de prueba
    """
    return pd.DataFrame({
        'Fecha': ['20231201', '20231202', '20231203'],
        'Sesiones': [100, 150, 200],
        'UsuariosActivos': [80, 120, 160]
    })


@pytest.fixture
def sample_wc_orders():
    """
    Órdenes de ejemplo de WooCommerce.
    
    Returns:
        Lista de diccionarios con órdenes
    """
    return [
        {
            'id': 1,
            'status': 'completed',
            'total': '100.00',
            'date_created': '2023-12-01T10:00:00',
            'shipping_total': '10.00',
            'discount_total': '0.00',
            'total_tax': '19.00',
            'cart_tax': '19.00',
            'shipping_tax': '0.00',
            'currency': 'CLP',
            'line_items': [
                {
                    'product_id': 101,
                    'name': 'Producto Test',
                    'quantity': 2,
                    'total': '90.00'
                }
            ]
        },
        {
            'id': 2,
            'status': 'processing',
            'total': '200.00',
            'date_created': '2023-12-02T15:30:00',
            'shipping_total': '15.00',
            'discount_total': '5.00',
            'total_tax': '38.00',
            'cart_tax': '38.00',
            'shipping_tax': '0.00',
            'currency': 'CLP',
            'line_items': [
                {
                    'product_id': 102,
                    'name': 'Producto Test 2',
                    'quantity': 1,
                    'total': '185.00'
                }
            ]
        }
    ]


@pytest.fixture
def mock_wc_api(mocker, sample_wc_orders):
    """
    Mock del cliente WooCommerce API.
    
    Returns:
        Mock configurado del API
    """
    mock_api = MagicMock()
    mock_response = MagicMock()
    mock_response.json.return_value = sample_wc_orders
    mock_api.get.return_value = mock_response
    return mock_api


@pytest.fixture
def mock_ga4_client(mocker):
    """
    Mock del cliente de Google Analytics.
    
    Returns:
        Mock configurado del cliente GA4
    """
    mock_client = mocker.patch('google.analytics.data_v1beta.BetaAnalyticsDataClient')
    return mock_client
