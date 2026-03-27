"""
Sistema de Logging Centralizado

Configuración centralizada de logging con rotación de archivos
y niveles configurables.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Directorio de logs
LOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# Formato de logs
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Configura y retorna un logger con handlers tanto para archivo como consola.
    
    Args:
        name: Nombre del logger (usualmente __name__ del módulo)
        level: Nivel de logging (default: INFO)
    
    Returns:
        Logger configurado con rotación de archivos
    
    Example:
        >>> logger = setup_logger(__name__)
        >>> logger.info("ETL iniciado")
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Evitar duplicar handlers si ya existe
    if logger.handlers:
        return logger
    
    # Handler para archivo con rotación (max 10MB, 5 backups)
    log_file = os.path.join(LOG_DIR, 'etl.log')
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    
    # Agregar handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def log_execution_time(logger: logging.Logger):
    """
    Decorador para loggear tiempo de ejecución de funciones.
    
    Args:
        logger: Logger a utilizar
    
    Example:
        >>> logger = setup_logger(__name__)
        >>> @log_execution_time(logger)
        ... def extract_data():
        ...     pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            logger.info(f"Iniciando {func.__name__}")
            try:
                result = func(*args, **kwargs)
                duration = (datetime.now() - start_time).total_seconds()
                logger.info(f"Completado {func.__name__} en {duration:.2f}s")
                return result
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                logger.error(f"Error en {func.__name__} después de {duration:.2f}s: {e}", exc_info=True)
                raise
        return wrapper
    return decorator


# Logger por defecto para uso rápido
default_logger = setup_logger('etl')
