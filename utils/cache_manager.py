"""
Sistema de Caché Inteligente para el Dashboard Analytics Pipeline.

Este módulo proporciona un sistema de caché con las siguientes características:
- TTL (Time To Live) configurable por entrada
- Invalidación manual y automática
- Métricas de hit/miss rate
- Almacenamiento en disco para persistencia
- Compresión automática para ahorrar espacio

Uso:
    from utils.cache_manager import CacheManager
    
    cache = CacheManager()
    
    # Obtener con caché
    data = cache.get('ventas_2025', max_age_hours=6)
    if data is None:
        data = expensive_calculation()
        cache.set('ventas_2025', data)
"""

import hashlib
import pickle
import gzip
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """Gestor de caché con TTL y métricas."""
    
    def __init__(self, cache_dir='data/cache', enable_compression=True):
        """
        Inicializa el gestor de caché.
        
        Args:
            cache_dir: Directorio donde almacenar archivos de caché
            enable_compression: Si True, comprimir datos con gzip
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.enable_compression = enable_compression
        
        # Métricas
        self.stats = {
            'hits': 0,
            'misses': 0,
            'invalidations': 0
        }
        
        logger.info(f"CacheManager initialized: dir={cache_dir}, compression={enable_compression}")
    
    def get_cache_key(self, *args, **kwargs) -> str:
        """
        Genera una clave única de caché basada en los parámetros.
        
        Args:
            *args: Argumentos posicionales
            **kwargs: Argumentos nombrados
            
        Returns:
            String MD5 hash de los parámetros
        """
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_cache_file(self, key: str) -> Path:
        """Retorna la ruta del archivo de caché para una key."""
        extension = '.pkl.gz' if self.enable_compression else '.pkl'
        return self.cache_dir / f"{key}{extension}"
    
    def get(self, key: str, max_age_hours: int = 24) -> Optional[Any]:
        """
        Obtiene un valor del caché si existe y no ha expirado.
        
        Args:
            key: Clave del caché
            max_age_hours: Edad máxima en horas antes de considerar expirado
            
        Returns:
            Valor almacenado o None si no existe/expiró
        """
        cache_file = self._get_cache_file(key)
        
        if not cache_file.exists():
            self.stats['misses'] += 1
            logger.debug(f"Cache MISS: {key}")
            return None
        
        # Verificar edad del archivo
        file_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
        max_age = timedelta(hours=max_age_hours)
        
        if file_age > max_age:
            self.stats['misses'] += 1
            logger.debug(f"Cache EXPIRED: {key} (age={file_age.total_seconds()/3600:.1f}h)")
            # Limpiar archivo expirado
            cache_file.unlink()
            return None
        
        # Cargar datos
        try:
            if self.enable_compression:
                with gzip.open(cache_file, 'rb') as f:
                    data = pickle.load(f)
            else:
                with open(cache_file, 'rb') as f:
                    data = pickle.load(f)
            
            self.stats['hits'] += 1
            logger.debug(f"Cache HIT: {key} (age={file_age.total_seconds()/3600:.1f}h)")
            return data
            
        except Exception as e:
            logger.error(f"Error loading cache {key}: {e}")
            # Si hay error, eliminar archivo corrupto
            cache_file.unlink()
            self.stats['misses'] += 1
            return None
    
    def set(self, key: str, value: Any) -> bool:
        """
        Guarda un valor en el caché.
        
        Args:
            key: Clave del caché
            value: Valor a almacenar (debe ser serializable con pickle)
            
        Returns:
            True si se guardó exitosamente, False en caso contrario
        """
        cache_file = self._get_cache_file(key)
        
        try:
            if self.enable_compression:
                with gzip.open(cache_file, 'wb') as f:
                    pickle.dump(value, f, protocol=pickle.HIGHEST_PROTOCOL)
            else:
                with open(cache_file, 'wb') as f:
                    pickle.dump(value, f, protocol=pickle.HIGHEST_PROTOCOL)
            
            # Obtener tamaño del archivo
            size_kb = cache_file.stat().st_size / 1024
            logger.debug(f"Cache SET: {key} ({size_kb:.1f} KB)")
            return True
            
        except Exception as e:
            logger.error(f"Error saving cache {key}: {e}")
            return False
    
    def invalidate(self, key: str) -> bool:
        """
        Invalida (elimina) una entrada específica del caché.
        
        Args:
            key: Clave a invalidar
            
        Returns:
            True si se eliminó, False si no existía
        """
        cache_file = self._get_cache_file(key)
        
        if cache_file.exists():
            cache_file.unlink()
            self.stats['invalidations'] += 1
            logger.debug(f"Cache INVALIDATED: {key}")
            return True
        
        return False
    
    def invalidate_all(self) -> int:
        """
        Invalida TODO el caché.
        
        Returns:
            Número de archivos eliminados
        """
        count = 0
        for cache_file in self.cache_dir.glob('*.pkl*'):
            cache_file.unlink()
            count += 1
        
        self.stats['invalidations'] += count
        logger.info(f"Cache CLEARED: {count} files deleted")
        return count
    
    def cleanup_expired(self, max_age_hours: int = 168) -> int:
        """
        Limpia archivos de caché expirados (por defecto >7 días).
        
        Args:
            max_age_hours: Edad máxima en horas
            
        Returns:
            Número de archivos eliminados
        """
        count = 0
        max_age = timedelta(hours=max_age_hours)
        now = datetime.now()
        
        for cache_file in self.cache_dir.glob('*.pkl*'):
            file_age = now - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if file_age > max_age:
                cache_file.unlink()
                count += 1
        
        if count > 0:
            logger.info(f"Cleaned {count} expired cache files (>{max_age_hours}h)")
        
        return count
    
    def get_stats(self) -> dict:
        """
        Obtiene estadísticas del caché.
        
        Returns:
            Dict con hits, misses, hit_rate, total_files, total_size_mb
        """
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        # Calcular tamaño total
        total_size = sum(f.stat().st_size for f in self.cache_dir.glob('*.pkl*'))
        total_files = len(list(self.cache_dir.glob('*.pkl*')))
        
        return {
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'invalidations': self.stats['invalidations'],
            'hit_rate': hit_rate,
            'total_files': total_files,
            'total_size_mb': total_size / (1024 * 1024)
        }
    
    def reset_stats(self):
        """Reinicia las estadísticas de métricas."""
        self.stats = {'hits': 0, 'misses': 0, 'invalidations': 0}
        logger.debug("Cache stats reset")


# Singleton global para uso en toda la aplicación
_cache_instance = None

def get_cache() -> CacheManager:
    """
    Obtiene la instancia singleton del CacheManager.
    
    Returns:
        Instancia compartida de CacheManager
    """
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = CacheManager()
    return _cache_instance
