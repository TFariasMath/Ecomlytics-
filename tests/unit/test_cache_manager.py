"""
Tests unitarios para el módulo cache_manager.

Valida que el sistema de caché funcione correctamente:
- Almacenamiento y recuperación de datos
- Expiración por TTL
- Invalidación manual
- Métricas de hit/miss
"""

import pytest
import time
import tempfile
import shutil
import os
from pathlib import Path
from datetime import datetime, timedelta

from utils.cache_manager import CacheManager


@pytest.fixture
def temp_cache_dir():
    """Crea un directorio temporal para tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def cache_manager(temp_cache_dir):
    """Fixture que proporciona un CacheManager limpio para cada test."""
    return CacheManager(cache_dir=temp_cache_dir)


class TestCacheManager:
    """Suite de tests para el CacheManager."""
    
    def test_initialization(self, temp_cache_dir):
        """Test que el cache manager se inicializa correctamente."""
        cache = CacheManager(cache_dir=temp_cache_dir)
        assert cache.cache_dir.exists()
        assert cache.enable_compression == True
        assert cache.stats == {'hits': 0, 'misses': 0, 'invalidations': 0}
    
    def test_get_cache_key_generates_unique_keys(self, cache_manager):
        """Test que diferentes parámetros generan diferentes keys."""
        key1 = cache_manager.get_cache_key('table1', 'param1')
        key2 = cache_manager.get_cache_key('table1', 'param2')
        key3 = cache_manager.get_cache_key('table2', 'param1')
        
        assert key1 != key2
        assert key1 != key3
        assert key2 != key3
    
    def test_get_cache_key_is_deterministic(self, cache_manager):
        """Test que los mismos parámetros generan la misma key."""
        key1 = cache_manager.get_cache_key('table', 'param')
        key2 = cache_manager.get_cache_key('table', 'param')
        
        assert key1 == key2
    
    def test_set_and_get_value(self, cache_manager):
        """Test que se puede guardar y recuperar un valor."""
        test_data = {'key': 'value', 'number': 42}
        cache_manager.set('test_key', test_data)
        
        retrieved = cache_manager.get('test_key')
        assert retrieved == test_data
    
    def test_get_nonexistent_key_returns_none(self, cache_manager):
        """Test que una key inexistente retorna None."""
        result = cache_manager.get('nonexistent_key')
        assert result is None
    
    def test_cache_expiration(self, cache_manager, temp_cache_dir):
        """Test que las entradas expiradas retornan None."""
        cache_manager.set('expired_key', 'test_value')
        
        # Modificar el timestamp del archivo para simular expiración
        cache_file = list(Path(temp_cache_dir).glob('*.pkl*'))[0]
        old_time = datetime.now() - timedelta(hours=25)
        timestamp = old_time.timestamp()
        cache_file.touch()
        
        # Configurar tiempo modificado manualmente
        import os
        os.utime(cache_file, (timestamp, timestamp))
        
        # Verificar que ha expirado
        result = cache_manager.get('expired_key', max_age_hours=24)
        assert result is None
    
    def test_invalidate_existing_key(self, cache_manager):
        """Test que se puede invalidar una key existente."""
        cache_manager.set('key_to_delete', 'value')
        assert cache_manager.get('key_to_delete') is not None
        
        result = cache_manager.invalidate('key_to_delete')
        assert result == True
        assert cache_manager.get('key_to_delete') is None
    
    def test_invalidate_nonexistent_key(self, cache_manager):
        """Test que invalidar una key inexistente retorna False."""
        result = cache_manager.invalidate('nonexistent_key')
        assert result == False
    
    def test_invalidate_all(self, cache_manager):
        """Test que se pueden eliminar todas las entradas del caché."""
        # Guardar varias entradas
        for i in range(5):
            cache_manager.set(f'key_{i}', f'value_{i}')
        
        # Verificar que existen
        assert cache_manager.get('key_0') is not None
        
        # Invalidar todo
        count = cache_manager.invalidate_all()
        assert count == 5
        
        # Verificar que ya no existen
        assert cache_manager.get('key_0') is None
    
    def test_stats_tracking_hits_and_misses(self, cache_manager):
        """Test que las estadísticas de hits/misses son correctas."""
        # Reset stats
        cache_manager.reset_stats()
        
        # Miss
        cache_manager.get('nonexistent')
        assert cache_manager.stats['misses'] == 1
        assert cache_manager.stats['hits'] == 0
        
        # Set y Hit
        cache_manager.set('test_key', 'value')
        cache_manager.get('test_key')
        assert cache_manager.stats['hits'] == 1
        assert cache_manager.stats['misses'] == 1
    
    def test_get_stats_returns_correct_data(self, cache_manager):
        """Test que get_stats retorna información correcta."""
        cache_manager.reset_stats()
        
        # Generar actividad
        cache_manager.set('key1', 'value1')
        cache_manager.set('key2', 'value2')
        cache_manager.get('key1')  # hit
        cache_manager.get('nonexistent')  # miss
        
        stats = cache_manager.get_stats()
        
        assert stats['hits'] == 1
        assert stats['misses'] == 1
        assert stats['hit_rate'] == 50.0
        assert stats['total_files'] == 2
        assert stats['total_size_mb'] > 0
    
    def test_compression_enabled(self, temp_cache_dir):
        """Test que la compresión funciona cuando está habilitada."""
        cache = CacheManager(cache_dir=temp_cache_dir, enable_compression=True)
        cache.set('test_key', 'x' * 1000)  # Datos comprimibles
        
        # Verificar que el archivo tiene extensión .gz
        cache_files = list(Path(temp_cache_dir).glob('*.pkl.gz'))
        assert len(cache_files) == 1
    
    def test_compression_disabled(self, temp_cache_dir):
        """Test que funciona sin compresión."""
        cache = CacheManager(cache_dir=temp_cache_dir, enable_compression=False)
        cache.set('test_key', 'test_value')
        
        # Verificar que el archivo NO tiene extensión .gz
        cache_files = list(Path(temp_cache_dir).glob('*.pkl'))
        assert len(cache_files) == 1
        
        # Verificar que se puede recuperar
        assert cache.get('test_key') == 'test_value'
    
    def test_cleanup_expired(self, cache_manager, temp_cache_dir):
        """Test que cleanup_expired elimina archivos viejos."""
        # Crear varias entradas
        for i in range(3):
            cache_manager.set(f'key_{i}', f'value_{i}')
        
        # Hacer que una sea "vieja"
        cache_files = list(Path(temp_cache_dir).glob('*.pkl*'))
        old_time = (datetime.now() - timedelta(hours=200)).timestamp()
        os.utime(cache_files[0], (old_time, old_time))
        
        # Limpiar archivos >168 horas (7 días)
        count = cache_manager.cleanup_expired(max_age_hours=168)
        assert count == 1
        
        # Verificar que quedan 2 archivos
        remaining = list(Path(temp_cache_dir).glob('*.pkl*'))
        assert len(remaining) == 2
    
    def test_large_data_handling(self, cache_manager):
        """Test que el caché maneja datos grandes correctamente."""
        import pandas as pd
        
        # Crear un DataFrame grande
        large_df = pd.DataFrame({
            'col1': range(10000),
            'col2': ['text'] * 10000,
            'col3': [3.14] * 10000
        })
        
        cache_manager.set('large_data', large_df)
        retrieved = cache_manager.get('large_data')
        
        assert retrieved is not None
        assert len(retrieved) == 10000
        assert retrieved.equals(large_df)


@pytest.mark.parametrize("max_age_hours", [1, 6, 24, 168])
def test_different_ttl_values(cache_manager, max_age_hours):
    """Test que diferentes valores de TTL funcionan correctamente."""
    cache_manager.set('ttl_test', 'value')
    result = cache_manager.get('ttl_test', max_age_hours=max_age_hours)
    assert result == 'value'
