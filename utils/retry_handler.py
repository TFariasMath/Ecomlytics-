"""
Retry Handler con Tenacity.

Este módulo proporciona decoradores y funciones para reintentos automáticos
con backoff exponencial en operaciones que pueden fallar temporalmente.
"""

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    after_log
)
import logging
from typing import Callable, Any
import requests
from google.api_core import exceptions as google_exceptions

logger = logging.getLogger(__name__)


# Exceptions que ameritan retry (errores transitorios)
RETRIABLE_EXCEPTIONS = (
    requests.exceptions.RequestException,
    requests.exceptions.Timeout,
    requests.exceptions.ConnectionError,
    google_exceptions.ServiceUnavailable,
    google_exceptions.DeadlineExceeded,
    google_exceptions.ResourceExhausted,
    TimeoutError,
    ConnectionError
)


def retry_on_api_error(
    max_attempts: int = 3,
    min_wait: int = 4,
    max_wait: int = 60,
    multiplier: int = 2
):
    """
    Decorador para reintentar operaciones de API con backoff exponencial.
    
    Args:
        max_attempts: Número máximo de intentos
        min_wait: Tiempo mínimo de espera (segundos)
        max_wait: Tiempo máximo de espera (segundos)
        multiplier: Multiplicador para backoff exponencial
    
    Example:
        >>> @retry_on_api_error(max_attempts=5)
        ... def fetch_data():
        ...     return api.get_data()
    """
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=multiplier, min=min_wait, max=max_wait),
        retry=retry_if_exception_type(RETRIABLE_EXCEPTIONS),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        after=after_log(logger, logging.INFO)
    )


def retry_on_db_error(
    max_attempts: int = 3,
    min_wait: int = 1,
    max_wait: int = 10
):
    """
    Decorador para reintentar operaciones de base de datos.
    
    Args:
        max_attempts: Número máximo de intentos
        min_wait: Tiempo mínimo de espera (segundos)
        max_wait: Tiempo máximo de espera (segundos)
    
    Example:
        >>> @retry_on_db_error()
        ... def save_to_db(data):
        ...     conn.execute(data)
    """
    import sqlite3
    
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
        retry=retry_if_exception_type((
            sqlite3.OperationalError,
            sqlite3.DatabaseError
        )),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )


class RetryableAPIClient:
    """
    Wrapper para clientes API con retry automático.
    
    Example:
        >>> client = RetryableAPIClient(max_attempts=5)
        >>> result = client.execute(lambda: api.get_report())
    """
    
    def __init__(self, max_attempts: int = 3, min_wait: int = 4, max_wait: int = 60):
        self.max_attempts = max_attempts
        self.min_wait = min_wait
        self.max_wait = max_wait
    
    @property
    def retry_decorator(self):
        """Retorna el decorador retry configurado."""
        return retry_on_api_error(
            max_attempts=self.max_attempts,
            min_wait=self.min_wait,
            max_wait=self.max_wait
        )
    
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        Ejecuta una función con retry automático.
        
        Args:
            func: Función a ejecutar
            *args: Argumentos posicionales
            **kwargs: Argumentos nombrados
        
        Returns:
            Resultado de la función
        """
        @self.retry_decorator
        def wrapped():
            return func(*args, **kwargs)
        
        return wrapped()


# Instancia global para uso rápido
default_retry_client = RetryableAPIClient(max_attempts=3, min_wait=4, max_wait=60)


def execute_with_retry(func: Callable, *args, **kwargs) -> Any:
    """
    Función helper para ejecutar con retry sin decorador.
    
    Args:
        func: Función a ejecutar
        *args: Argumentos posicionales
        **kwargs: Argumentos nombrados
    
    Returns:
        Resultado de la función
    
    Example:
        >>> result = execute_with_retry(api.get_data, param1='value')
    """
    return default_retry_client.execute(func, *args, **kwargs)
