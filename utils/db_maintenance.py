"""
Script de Mantenimiento de Base de Datos.

Realiza tareas de mantenimiento en las bases de datos SQLite:
- Vacuum para recuperar espacio
- Análisis de estadísticas
- Verificación de integridad
- Backup
"""

import sqlite3
import os
import shutil
from datetime import datetime
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config.logging_config import setup_logger

logger = setup_logger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
BACKUP_DIR = os.path.join(BASE_DIR, 'backups')

# Asegurar que existe el directorio de backups
os.makedirs(BACKUP_DIR, exist_ok=True)


def get_db_size(db_path: str) -> float:
    """
    Obtiene el tamaño de una base de datos en MB.
    
    Args:
        db_path: Ruta a la base de datos
    
    Returns:
        Tamaño en MB
    """
    if not os.path.exists(db_path):
        return 0
    return os.path.getsize(db_path) / (1024 * 1024)


def vacuum_database(db_path: str) -> None:
    """
    Ejecuta VACUUM para compactar la base de datos.
    
    Args:
        db_path: Ruta a la base de datos
    """
    if not os.path.exists(db_path):
        logger.warning(f"Base de datos no existe: {db_path}")
        return
    
    logger.info(f"🔧 Ejecutando VACUUM en {os.path.basename(db_path)}...")
    
    size_before = get_db_size(db_path)
    logger.info(f"   Tamaño antes: {size_before:.2f} MB")
    
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("VACUUM")
        conn.close()
        
        size_after = get_db_size(db_path)
        space_saved = size_before - size_after
        
        logger.info(f"   Tamaño después: {size_after:.2f} MB")
        logger.info(f"✅ Espacio recuperado: {space_saved:.2f} MB")
        
    except Exception as e:
        logger.error(f"❌ Error en VACUUM: {e}", exc_info=True)


def analyze_database(db_path: str) -> None:
    """
    Ejecuta ANALYZE para actualizar estadísticas del query optimizer.
    
    Args:
        db_path: Ruta a la base de datos
    """
    if not os.path.exists(db_path):
        logger.warning(f"Base de datos no existe: {db_path}")
        return
    
    logger.info(f"📊 Ejecutando ANALYZE en {os.path.basename(db_path)}...")
    
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("ANALYZE")
        conn.close()
        
        logger.info("✅ Estadísticas actualizadas")
        
    except Exception as e:
        logger.error(f"❌ Error en ANALYZE: {e}", exc_info=True)


def check_integrity(db_path: str) -> bool:
    """
    Verifica la integridad de la base de datos.
    
    Args:
        db_path: Ruta a la base de datos
    
    Returns:
        True si la integridad es OK
    """
    if not os.path.exists(db_path):
        logger.warning(f"Base de datos no existe: {db_path}")
        return False
    
    logger.info(f"🔍 Verificando integridad de {os.path.basename(db_path)}...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()[0]
        conn.close()
        
        if result == 'ok':
            logger.info("✅ Integridad OK")
            return True
        else:
            logger.error(f"❌ Problemas de integridad: {result}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error verificando integridad: {e}", exc_info=True)
        return False


def backup_database(db_path: str) -> str:
    """
    Crea un backup de la base de datos.
    
    Args:
        db_path: Ruta a la base de datos
    
    Returns:
        Ruta al archivo de backup
    """
    if not os.path.exists(db_path):
        logger.warning(f"Base de datos no existe: {db_path}")
        return ""
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    db_name = os.path.basename(db_path)
    backup_name = f"{db_name}.{timestamp}.backup"
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    
    logger.info(f"💾 Creando backup de {db_name}...")
    
    try:
        shutil.copy2(db_path, backup_path)
        backup_size = get_db_size(backup_path)
        logger.info(f"✅ Backup creado: {backup_name} ({backup_size:.2f} MB)")
        return backup_path
        
    except Exception as e:
        logger.error(f"❌ Error creando backup: {e}", exc_info=True)
        return ""


def cleanup_old_backups(max_backups: int = 5) -> None:
    """
    Elimina backups antiguos, manteniendo solo los más recientes.
    
    Args:
        max_backups: Número máximo de backups a mantener por BD
    """
    logger.info(f"🧹 Limpiando backups antiguos (manteniendo {max_backups} por BD)...")
    
    try:
        # Agrupar backups por base de datos
        backups = {}
        for filename in os.listdir(BACKUP_DIR):
            if filename.endswith('.backup'):
                # Extraer nombre de BD
                db_name = filename.split('.')[0] + '.db'
                if db_name not in backups:
                    backups[db_name] = []
                backups[db_name].append(filename)
        
        # Para cada BD, mantener solo los últimos max_backups
        total_deleted = 0
        for db_name, backup_list in backups.items():
            backup_list.sort(reverse=True)  # Más recientes primero
            
            if len(backup_list) > max_backups:
                to_delete = backup_list[max_backups:]
                for backup_file in to_delete:
                    backup_path = os.path.join(BACKUP_DIR, backup_file)
                    os.remove(backup_path)
                    total_deleted += 1
                    logger.info(f"   Eliminado: {backup_file}")
        
        if total_deleted > 0:
            logger.info(f"✅ {total_deleted} backups antiguos eliminados")
        else:
            logger.info("✅ No hay backups antiguos para eliminar")
            
    except Exception as e:
        logger.error(f"❌ Error limpiando backups: {e}", exc_info=True)


def main():
    """Ejecuta mantenimiento completo."""
    logger.info("="*60)
    logger.info("🔧 Iniciando Mantenimiento de Bases de Datos")
    logger.info("="*60)
    
    databases = [
        os.path.join(DATA_DIR, 'analytics.db'),
        os.path.join(DATA_DIR, 'woocommerce.db')
    ]
    
    for db_path in databases:
        if not os.path.exists(db_path):
            logger.warning(f"Saltando {os.path.basename(db_path)} (no existe)")
            continue
        
        logger.info("")
        logger.info(f"📁 Procesando {os.path.basename(db_path)}")
        logger.info("-"*60)
        
        # 1. Backup
        backup_database(db_path)
        
        # 2. Verificar integridad
        if not check_integrity(db_path):
            logger.error("⚠️ Problemas de integridad detectados, saltando mantenimiento")
            continue
        
        # 3. VACUUM
        vacuum_database(db_path)
        
        # 4. ANALYZE
        analyze_database(db_path)
    
    # 5. Limpiar backups antiguos
    logger.info("")
    logger.info("-"*60)
    cleanup_old_backups(max_backups=5)
    
    logger.info("")
    logger.info("="*60)
    logger.info("✅ Mantenimiento completado")
    logger.info("="*60)


if __name__ == '__main__':
    main()
