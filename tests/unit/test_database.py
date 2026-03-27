"""
Tests unitarios para el módulo utils/database.py

Valida las operaciones de base de datos:
- Creación y conexión a databases
- Guardado de DataFrames
- Lectura de datos
- Manejo de errores
"""

import pytest
import sqlite3
import pandas as pd
import tempfile
import os
from pathlib import Path

from utils.database import (
    get_last_extraction_date,
    save_to_db,
    query_db
)


@pytest.fixture
def temp_db():
    """Crea una base de datos temporal para tests."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def sample_dataframe():
    """Crea un DataFrame de ejemplo para tests."""
    return pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['Alice', 'Bob', 'Charlie'],
        'value': [100, 200, 300],
        'date': pd.to_datetime(['2025-01-01', '2025-01-02', '2025-01-03'])
    })


class TestDatabaseOperations:
    """Tests para operaciones de base de datos."""
    
    def test_save_to_db_creates_table(self, temp_db, sample_dataframe):
        """Test que save_to_db crea una nueva tabla."""
        save_to_db(sample_dataframe, 'test_table', temp_db)
        
        # Verificar que la tabla existe
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='test_table'")
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None
        assert result[0] == 'test_table'
    
    def test_save_to_db_preserves_data(self, temp_db, sample_dataframe):
        """Test que los datos se guardan correctamente."""
        save_to_db(sample_dataframe, 'test_table', temp_db)
        
        # Leer los datos de vuelta
        conn = sqlite3.connect(temp_db)
        df_read = pd.read_sql('SELECT * FROM test_table', conn)
        conn.close()
        
        assert len(df_read) == len(sample_dataframe)
        assert list(df_read['name']) == list(sample_dataframe['name'])
    
    def test_save_to_db_append_mode(self, temp_db, sample_dataframe):
        """Test que append mode agrega datos sin borrar existentes."""
        # Guardar primera vez
        save_to_db(sample_dataframe, 'test_table', temp_db, if_exists='replace')
        
        # Guardar segunda vez con append
        additional_data = pd.DataFrame({
            'id': [4, 5],
            'name': ['David', 'Eve'],
            'value': [400, 500],
            'date': pd.to_datetime(['2025-01-04', '2025-01-05'])
        })
        save_to_db(additional_data, 'test_table', temp_db, if_exists='append')
        
        # Verificar que hay 5 registros
        conn = sqlite3.connect(temp_db)
        df_read = pd.read_sql('SELECT * FROM test_table', conn)
        conn.close()
        
        assert len(df_read) == 5
    
    def test_get_last_extraction_date_empty_table(self, temp_db):
        """Test que retorna None si la tabla está vacía."""
        # Crear tabla vacía
        conn = sqlite3.connect(temp_db)
        conn.execute('CREATE TABLE empty_table (id INTEGER, date TEXT)')
        conn.close()
        
        result = get_last_extraction_date('empty_table', 'date', temp_db)
        assert result is None
    
    def test_get_last_extraction_date_returns_max_date(self, temp_db, sample_dataframe):
        """Test que retorna la fecha más reciente."""
        save_to_db(sample_dataframe, 'test_table', temp_db)
        
        result = get_last_extraction_date('test_table', 'date', temp_db)
        assert result is not None
        # La fecha más reciente debería ser 2025-01-03
        assert '2025-01-03' in str(result)
    
    def test_query_db_returns_dataframe(self, temp_db, sample_dataframe):
        """Test que query_db retorna un DataFrame."""
        save_to_db(sample_dataframe, 'test_table', temp_db)
        
        result = query_db('SELECT * FROM test_table WHERE value > 150', temp_db)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2  # Bob y Charlie
    
    def test_query_db_with_invalid_query_raises_error(self, temp_db):
        """Test que una query inválida lanza error."""
        with pytest.raises(Exception):
            query_db('SELECT * FROM nonexistent_table', temp_db)
    
    def test_save_empty_dataframe_creates_table(self, temp_db):
        """Test que guardar DataFrame vacío crea la tabla con estructura."""
        empty_df = pd.DataFrame(columns=['id', 'name', 'value'])
        save_to_db(empty_df, 'empty_table', temp_db)
        
        # Verificar que la tabla existe
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='empty_table'")
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None
    
    @pytest.mark.parametrize("invalid_input", [None, [], {}, "string", 123])
    def test_save_to_db_rejects_invalid_input(self, temp_db, invalid_input):
        """Test que save_to_db rechaza inputs inválidos."""
        with pytest.raises((ValueError, TypeError, AttributeError)):
            save_to_db(invalid_input, 'test_table', temp_db)
    
    def test_database_connection_error_handling(self):
        """Test que se manejan errores de conexión apropiadamente."""
        with pytest.raises(Exception):
            query_db('SELECT * FROM test', '/invalid/path/database.db')
    
    def test_special_characters_in_data(self, temp_db):
        """Test que se manejan caracteres especiales correctamente."""
        df_special = pd.DataFrame({
            'text': ["O'Brien", "Quote: \"test\"", "Backslash: \\", "Emoji: 🚀"],
            'value': [1, 2, 3, 4]
        })
        
        save_to_db(df_special, 'special_table', temp_db)
        
        conn = sqlite3.connect(temp_db)
        df_read = pd.read_sql('SELECT * FROM special_table', conn)
        conn.close()
        
        assert len(df_read) == 4
        assert "O'Brien" in df_read['text'].values
    
    def test_large_dataframe_handling(self, temp_db):
        """Test que se manejan DataFrames grandes eficientemente."""
        large_df = pd.DataFrame({
            'id': range(100000),
            'value': range(100000),
            'text': ['test'] * 100000
        })
        
        # Esto no debería lanzar error ni tomar demasiado tiempo
        save_to_db(large_df, 'large_table', temp_db)
        
        conn = sqlite3.connect(temp_db)
        count = pd.read_sql('SELECT COUNT(*) as cnt FROM large_table', conn)['cnt'][0]
        conn.close()
        
        assert count == 100000


class TestDatabaseEdgeCases:
    """Tests para casos edge y manejo de errores."""
    
    def test_null_values_handling(self, temp_db):
        """Test que se manejan valores NULL correctamente."""
        df_with_nulls = pd.DataFrame({
            'id': [1, 2, 3],
            'value': [100, None, 300],
            'text': ['a', 'b', None]
        })
        
        save_to_db(df_with_nulls, 'null_table', temp_db)
        
        conn = sqlite3.connect(temp_db)
        df_read = pd.read_sql('SELECT * FROM null_table', conn)
        conn.close()
        
        assert pd.isna(df_read.iloc[1]['value'])
        assert pd.isna(df_read.iloc[2]['text'])
    
    def test_duplicate_keys_handling(self, temp_db):
        """Test manejo de keys duplicadas."""
        df1 = pd.DataFrame({'id': [1, 2], 'value': [100, 200]})
        df2 = pd.DataFrame({'id': [2, 3], 'value': [250, 300]})
        
        save_to_db(df1, 'dup_table', temp_db, if_exists='replace')
        save_to_db(df2, 'dup_table', temp_db, if_exists='append')
        
        conn = sqlite3.connect(temp_db)
        df_read = pd.read_sql('SELECT * FROM dup_table', conn)
        conn.close()
        
        # Debería tener 4 registros (con id=2 duplicado)
        assert len(df_read) == 4
