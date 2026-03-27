"""
Cliente API reutilizable con retry logic.

Implementa reintentos automáticos y manejo de errores para llamadas a APIs externas.
"""

import requests
from typing import Optional, Dict, Any
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config.logging_config import setup_logger

logger = setup_logger(__name__)


class APIError(Exception):
    """Excepción personalizada para errores de API."""
    pass


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((requests.exceptions.RequestException, APIError)),
    reraise=True
)
def make_api_request(
    url: str,
    method: str = 'GET',
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    timeout: int = 30
) -> requests.Response:
    """
    Realiza una petición HTTP con retry automático.
    
    Args:
        url: URL del endpoint
        method: Método HTTP (GET, POST, etc.)
        headers: Headers HTTP
        params: Query parameters
        json_data: Datos JSON para el body
        timeout: Timeout en segundos
    
    Returns:
        Response object de requests
    
    Raises:
        APIError: Si la petición falla después de los reintentos
    
    Example:
        >>> response = make_api_request('https://api.example.com/data')
        >>> data = response.json()
    """
    try:
        logger.debug(f"API Request: {method} {url}")
        
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json_data,
            timeout=timeout
        )
        
        response.raise_for_status()
        logger.debug(f"API Response: {response.status_code}")
        
        return response
        
    except requests.exceptions.Timeout as e:
        logger.warning(f"Timeout en {url}: {e}")
        raise APIError(f"Timeout: {e}")
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response else 'N/A'
        logger.error(f"HTTP Error {status_code} en {url}: {e}")
        raise APIError(f"HTTP {status_code}: {e}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error de conexión en {url}: {e}")
        raise APIError(f"Request failed: {e}")


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def get_usd_clp_rate(fallback_rate: float = 950.0) -> float:
    """
    Obtiene la tasa de cambio USD a CLP con retry automático.
    
    Args:
        fallback_rate: Tasa por defecto si falla la API
    
    Returns:
        Tasa de cambio USD/CLP
    
    Example:
        >>> rate = get_usd_clp_rate()
        >>> print(f"1 USD = {rate} CLP")
    """
    try:
        logger.info("Obteniendo tasa de cambio USD/CLP de mindicador.cl...")
        
        response = make_api_request(
            url='https://mindicador.cl/api/dolar',
            timeout=5
        )
        
        data = response.json()
        
        if 'serie' in data and len(data['serie']) > 0:
            rate = float(data['serie'][0]['valor'])
            logger.info(f"✅ Tasa de cambio: 1 USD = {rate} CLP")
            return rate
        else:
            logger.warning("Formato de respuesta inesperado de mindicador.cl")
            raise APIError("Formato de respuesta inválido")
            
    except Exception as e:
        logger.error(f"Error obteniendo tasa de cambio: {e}")
        logger.info(f"Usando tasa fallback: {fallback_rate} CLP")
        return fallback_rate
