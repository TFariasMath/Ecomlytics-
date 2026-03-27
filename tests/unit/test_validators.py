"""
Tests unitarios para el módulo utils/validators.py

Valida las funciones de validación de datos y configuración.
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta

# Import validators module
try:
    from utils.validators import (
        validate_dataframe,
        validate_date_format,
        validate_config,
        sanitize_string
    )
except ImportError:
    pytest.skip("validators module not found", allow_module_level=True)


class TestDataFrameValidation:
    """Tests para validación de DataFrames."""
    
    def test_validate_empty_dataframe(self):
        """Test que detecta DataFrames vacíos."""
        empty_df = pd.DataFrame()
        result = validate_dataframe(empty_df, required_columns=['id', 'name'])
        assert result['valid'] == False
        assert 'empty' in result['error'].lower()
    
    def test_validate_missing_columns(self):
        """Test que detecta columnas faltantes."""
        df = pd.DataFrame({'id': [1, 2], 'value': [100, 200]})
        result = validate_dataframe(df, required_columns=['id', 'name', 'date'])
        assert result['valid'] == False
        assert 'name' in result['error'] or 'date' in result['error']
    
    def test_validate_correct_dataframe(self):
        """Test que acepta DataFrame válido."""
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['A', 'B', 'C'],
            'value': [100, 200, 300]
        })
        result = validate_dataframe(df, required_columns=['id', 'name', 'value'])
        assert result['valid'] == True
    
    @pytest.mark.parametrize("invalid_input", [None, [], {}, "string", 123])
    def test_validate_invalid_types(self, invalid_input):
        """Test que rechaza tipos inválidos."""
        result = validate_dataframe(invalid_input, required_columns=['id'])
        assert result['valid'] == False


class TestDateValidation:
    """Tests para validación de fechas."""
    
    def test_validate_correct_date_format(self):
        """Test que acepta formato de fecha correcto."""
        result = validate_date_format('2025-01-15', format='%Y-%m-%d')
        assert result['valid'] == True
    
    def test_validate_incorrect_date_format(self):
        """Test que rechaza formato incorrecto."""
        result = validate_date_format('15/01/2025', format='%Y-%m-%d')
        assert result['valid'] == False
    
    def test_validate_invalid_date(self):
        """Test que detecta fechas inválidas."""
        result = validate_date_format('2025-13-45', format='%Y-%m-%d')
        assert result['valid'] == False
    
    @pytest.mark.parametrize("date_string", [
        '2025-01-01',
        '2025-12-31',
        '2000-02-29',  # Año bisiesto
    ])
    def test_validate_various_valid_dates(self, date_string):
        """Test varias fechas válidas."""
        result = validate_date_format(date_string, format='%Y-%m-%d')
        assert result['valid'] == True


class TestStringFormat:
    """Tests para sanitización de strings."""
    
    def test_sanitize_removes_special_chars(self):
        """Test que elimina caracteres especiales."""
        result = sanitize_string("Hello<script>alert('xss')</script>")
        assert '<script>' not in result
        assert 'Hello' in result
    
    def test_sanitize_preserves_safe_chars(self):
        """Test que preserva caracteres seguros."""
        safe_text = "Hello World 123!?"
        result = sanitize_string(safe_text)
        assert 'Hello' in result
        assert 'World' in result
    
    def test_sanitize_handles_empty_string(self):
        """Test que maneja strings vacíos."""
        result = sanitize_string("")
        assert result == ""
    
    def test_sanitize_handles_none(self):
        """Test que maneja None apropiadamente."""
        result = sanitize_string(None)
        assert result == "" or result is None


class TestConfigValidation:
    """Tests para validación de configuración."""
    
    def test_validate_complete_config(self):
        """Test que acepta configuración completa."""
        config = {
            'WC_URL': 'https://example.com',
            'WC_CONSUMER_KEY': 'ck_test',
            'WC_CONSUMER_SECRET': 'cs_test',
            'GA4_PROPERTY_ID': '123456789'
        }
        result = validate_config(config, required_keys=['WC_URL', 'WC_CONSUMER_KEY'])
        assert result['valid'] == True
    
    def test_validate_missing_keys(self):
        """Test que detecta keys faltantes."""
        config = {'WC_URL': 'https://example.com'}
        result = validate_config(config, required_keys=['WC_URL', 'WC_CONSUMER_KEY'])
        assert result['valid'] == False
        assert 'WC_CONSUMER_KEY' in result['error']
    
    def test_validate_empty_values(self):
        """Test que detecta valores vacíos."""
        config = {
            'WC_URL': '',
            'WC_CONSUMER_KEY': 'ck_test'
        }
        result = validate_config(config, required_keys=['WC_URL'], allow_empty=False)
        assert result['valid'] == False
