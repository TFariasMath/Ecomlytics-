"""
Script para crear índices en las bases de datos.

Ejecuta el script SQL de creación de índices en las bases de datos
de Analytics y WooCommerce para optimizar las consultas.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config.logging_config import setup_logger
from utils.database import create_indexes

logger = setup_logger(__name__)

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
INDEXES_SQL_PATH = os.path.join(BASE_DIR, 'config', 'create_indexes.sql')
ANALYTICS_DB = os.path.join(BASE_DIR, 'data', 'analytics.db')
WOOCOMMERCE_DB = os.path.join(BASE_DIR, 'data', 'woocommerce.db')


def main():
    """Crea índices en ambas bases de datos."""
    logger.info("🔧 Creando índices de optimización...")
    
    # Leer script SQL
    with open(INDEXES_SQL_PATH, 'r', encoding='utf-8') as f:
        indexes_sql = f.read()
    
    # Aplicar a Analytics DB
    if os.path.exists(ANALYTICS_DB):
        logger.info(f"Aplicando índices a {ANALYTICS_DB}")
        create_indexes(ANALYTICS_DB, indexes_sql)
    else:
        logger.warning(f"Base de datos {ANALYTICS_DB} no existe, saltando...")
    
    # Aplicar a WooCommerce DB
    if os.path.exists(WOOCOMMERCE_DB):
        logger.info(f"Aplicando índices a {WOOCOMMERCE_DB}")
        create_indexes(WOOCOMMERCE_DB, indexes_sql)
    else:
        logger.warning(f"Base de datos {WOOCOMMERCE_DB} no existe, saltando...")
    
    logger.info("✅ Índices creados correctamente")


if __name__ == '__main__':
    main()
