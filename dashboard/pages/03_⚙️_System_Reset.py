"""
System Reset Page

This page allows users to reset the analytics dashboard system by cleaning
databases, removing credentials, and creating backups. It provides a user-friendly
interface for system maintenance and fresh starts.
"""

import streamlit as st
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime
import sqlite3

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import (
    get_all_database_paths,
    list_service_account_keys,
    reset_configuration
)


def get_file_size_mb(file_path: Path) -> float:
    """Get file size in MB"""
    if file_path.exists():
        return file_path.stat().st_size / (1024 * 1024)
    return 0.0


def create_backup() -> tuple[bool, str]:
    """
    Create backup of all databases and credentials
    
    Returns:
        Tuple of (success, backup_path or error_message)
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = PROJECT_ROOT / 'backups' / f'reset_{timestamp}'
    
    try:
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup databases
        db_paths = get_all_database_paths()
        for name, db_path in db_paths.items():
            db_file = Path(db_path)
            if db_file.exists():
                backup_path = backup_dir / db_file.name
                shutil.copy2(db_file, backup_path)
        
        # Backup .env file
        env_file = PROJECT_ROOT / '.env'
        if env_file.exists():
            backup_env = backup_dir / '.env'
            shutil.copy2(env_file, backup_env)
        
        # Backup Google Analytics JSON keys
        json_files = list_service_account_keys()
        for json_file in json_files:
            backup_path = backup_dir / json_file.name
            shutil.copy2(json_file, backup_path)
        
        return True, str(backup_dir)
        
    except Exception as e:
        return False, str(e)


def delete_databases(selected_dbs: list) -> tuple[int, list]:
    """
    Delete selected databases
    
    Args:
        selected_dbs: List of database names to delete
    
    Returns:
        Tuple of (count_deleted, errors)
    """
    db_paths = get_all_database_paths()
    count = 0
    errors = []
    
    for db_name in selected_dbs:
        db_path = Path(db_paths.get(db_name.lower()))
        if db_path.exists():
            try:
                db_path.unlink()
                count += 1
            except Exception as e:
                errors.append(f"Error deleting {db_name}: {e}")
    
    return count, errors


def delete_json_keys() -> tuple[int, list]:
    """
    Delete Google Analytics service account JSON files
    
    Returns:
        Tuple of (count_deleted, errors)
    """
    json_files = list_service_account_keys()
    count = 0
    errors = []
    
    for json_file in json_files:
        try:
            json_file.unlink()
            count += 1
        except Exception as e:
            errors.append(f"Error deleting {json_file.name}: {e}")
    
    return count, errors


def list_available_backups() -> list:
    """List all available backup directories"""
    backups_root = PROJECT_ROOT / 'backups'
    if not backups_root.exists():
        return []
    
    backups = []
    for backup_dir in backups_root.glob('reset_*'):
        if backup_dir.is_dir():
            # Get timestamp from directory name
            try:
                timestamp_str = backup_dir.name.replace('reset_', '')
                timestamp = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                backups.append({
                    'path': backup_dir,
                    'name': backup_dir.name,
                    'timestamp': timestamp,
                    'formatted_date': timestamp.strftime('%Y-%m-%d %H:%M:%S')
                })
            except:
                pass
    
    # Sort by timestamp (newest first)
    backups.sort(key=lambda x: x['timestamp'], reverse=True)
    return backups


def main():
    st.set_page_config(
        page_title="System Reset",
        page_icon="⚙️",
        layout="wide"
    )
    
    st.title("⚙️ System Reset")
    
    # Back to Dashboard button
    col_back, col_empty = st.columns([1, 4])
    with col_back:
        if st.button("← Back to Dashboard", use_container_width=True):
            st.switch_page("app_woo_v2.py")
    
    st.markdown("---")
    
    # Warning banner
    st.warning("""
    **⚠️ ADVERTENCIA:** Esta herramienta elimina datos de forma permanente.
    
    Usa esta página para:
    - Limpiar las bases de datos y empezar desde cero
    - Cambiar a una nueva tienda WooCommerce
    - Resetear las credenciales de API
    - Solucionar problemas comenzando de nuevo
    """)
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs([
        "🗑️ Resetear Sistema",
        "💾 Backups Disponibles",
        "ℹ️ Información"
    ])
    
    # ===========================
    # TAB 1: RESET SYSTEM
    # ===========================
    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Selecciona qué resetear")
            
            # Database section
            st.markdown("### 📊 Bases de Datos")
            
            db_paths = get_all_database_paths()
            db_options = {}
            
            for name, path in db_paths.items():
                db_file = Path(path)
                if db_file.exists():
                    size_mb = get_file_size_mb(db_file)
                    label = f"{name.capitalize()} ({size_mb:.2f} MB)"
                    db_options[name.capitalize()] = st.checkbox(
                        label,
                        key=f"db_{name}",
                        help=f"Base de datos de {name}"
                    )
                else:
                    st.info(f"✓ {name.capitalize()} - No existe")
            
            # Credentials section
            st.markdown("### 🔑 Credenciales")
            
            env_file = PROJECT_ROOT / '.env'
            reset_env = False
            if env_file.exists():
                reset_env = st.checkbox(
                    "Resetear archivo .env (credenciales de API)",
                    help="Elimina todas las credenciales y restaura el archivo a su estado inicial"
                )
            else:
                st.info("✓ Archivo .env - No existe")
            
            # JSON keys section
            st.markdown("### 📄 Archivos JSON de Google Analytics")
            
            json_files = list_service_account_keys()
            remove_json = False
            if json_files:
                json_names = [f.name for f in json_files]
                st.write("Archivos encontrados:")
                for name in json_names:
                    st.text(f"  • {name}")
                remove_json = st.checkbox(
                    f"Eliminar {len(json_files)} archivo(s) JSON",
                    help="Elimina los archivos de credenciales de Google Analytics"
                )
            else:
                st.info("✓ No se encontraron archivos JSON de service account")
            
            st.markdown("---")
            
            # Backup option
            create_backup_before = st.checkbox(
                "✅ Crear backup antes de eliminar",
                value=True,
                help="Recomendado: Crea una copia de seguridad de todos los archivos antes de eliminarlos"
            )
        
        with col2:
            st.subheader("Resumen")
            
            # Count items to be reset
            db_count = sum(1 for v in db_options.values() if v)
            cred_count = 1 if reset_env else 0
            json_count = len(json_files) if remove_json else 0
            total = db_count + cred_count + json_count
            
            if total == 0:
                st.info("No hay nada seleccionado para resetear")
            else:
                st.metric("Items a resetear", total)
                
                if db_count > 0:
                    st.metric("Bases de datos", db_count)
                if cred_count > 0:
                    st.metric("Archivos de credenciales", cred_count)
                if json_count > 0:
                    st.metric("Archivos JSON", json_count)
                
                st.markdown("---")
                
                # Reset button
                if st.button("🗑️ RESETEAR SISTEMA", type="primary", use_container_width=True):
                    # Show confirmation dialog
                    st.session_state.confirm_reset = True
        
        # Confirmation dialog
        if st.session_state.get('confirm_reset', False):
            st.markdown("---")
            st.error("### ⚠️ CONFIRMACIÓN FINAL")
            st.write("Esta acción **NO SE PUEDE DESHACER**. ¿Estás seguro?")
            
            col_yes, col_no = st.columns(2)
            with col_yes:
                if st.button("✅ Sí, resetear", type="primary", use_container_width=True):
                    with st.spinner("Ejecutando reset..."):
                        # Create backup if requested
                        backup_success = True
                        backup_path = None
                        
                        if create_backup_before:
                            backup_success, backup_path = create_backup()
                            if backup_success:
                                st.success(f"✓ Backup creado en: `{Path(backup_path).name}`")
                            else:
                                st.error(f"❌ Error creando backup: {backup_path}")
                                st.stop()
                        
                        # Delete databases
                        if db_count > 0:
                            selected_dbs = [k for k, v in db_options.items() if v]
                            deleted_count, errors = delete_databases(selected_dbs)
                            if errors:
                                for error in errors:
                                    st.error(error)
                            else:
                                st.success(f"✓ {deleted_count} base(s) de datos eliminada(s)")
                        
                        # Reset credentials
                        if reset_env:
                            if reset_configuration(backup=False):  # Already backed up
                                st.success("✓ Archivo .env reseteado")
                            else:
                                st.error("❌ Error reseteando .env")
                        
                        # Delete JSON keys
                        if remove_json:
                            deleted_count, errors = delete_json_keys()
                            if errors:
                                for error in errors:
                                    st.error(error)
                            else:
                                st.success(f"✓ {deleted_count} archivo(s) JSON eliminado(s)")
                        
                        st.success("### ✅ Reset completado!")
                        st.info("Ahora puedes ir a **Configuración Inicial** para configurar nuevas credenciales.")
                        
                        # Clear confirmation state
                        st.session_state.confirm_reset = False
                        st.rerun()
            
            with col_no:
                if st.button("❌ No, cancelar", use_container_width=True):
                    st.session_state.confirm_reset = False
                    st.rerun()
    
    # ===========================
    # TAB 2: AVAILABLE BACKUPS
    # ===========================
    with tab2:
        st.subheader("💾 Backups Disponibles")
        
        backups = list_available_backups()
        
        if not backups:
            st.info("No hay backups disponibles. Los backups se crean automáticamente cuando reseteas el sistema.")
        else:
            st.write(f"Se encontraron **{len(backups)}** backup(s):")
            
            for backup in backups:
                with st.expander(f"📦 {backup['formatted_date']} - {backup['name']}"):
                    backup_path = backup['path']
                    
                    # List files in backup
                    files = list(backup_path.glob('*'))
                    
                    st.write("**Archivos en este backup:**")
                    for file in files:
                        if file.is_file():
                            size_mb = get_file_size_mb(file)
                            st.text(f"  • {file.name} ({size_mb:.2f} MB)")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.code(str(backup_path), language="text")
                    with col2:
                        if st.button("🗑️ Eliminar este backup", key=f"del_{backup['name']}"):
                            try:
                                shutil.rmtree(backup_path)
                                st.success("Backup eliminado")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
    
    # ===========================
    # TAB 3: INFORMATION
    # ===========================
    with tab3:
        st.subheader("ℹ️ Información sobre el Reset del Sistema")
        
        st.markdown("""
        ### ¿Qué hace esta herramienta?
        
        Esta herramienta te permite resetear el dashboard a un estado limpio, eliminando:
        
        - **Bases de Datos**: Elimina todos los datos extraídos de WooCommerce, Google Analytics y Facebook
        - **Credenciales**: Resetea el archivo `.env` con las claves de API a su estado inicial
        - **Archivos JSON**: Elimina los archivos de credenciales de Google Cloud Service Account
        
        ### ¿Cuándo usar esta herramienta?
        
        - 🔄 **Cambiar de tienda**: Cuando quieres configurar el dashboard para otra tienda WooCommerce
        - 🧹 **Limpiar datos de prueba**: Para eliminar datos de testing y empezar con datos reales
        - 🔧 **Solucionar problemas**: Cuando hay errores en los datos y quieres empezar de cero
        - 🔐 **Cambiar credenciales**: Para configurar nuevas claves de API de forma limpia
        
        ### Proceso de Reset
        
        1. **Selección**: Elige qué componentes quieres resetear
        2. **Backup**: Se crea automáticamente un backup de seguridad (recomendado)
        3. **Confirmación**: Se te pedirá confirmar la acción
        4. **Ejecución**: Se eliminan los archivos seleccionados
        5. **Reconfiguración**: Ve a "Configuración Inicial" para configurar nuevas credenciales
        
        ### Seguridad
        
        - ✅ Los backups se crean automáticamente antes de eliminar
        - ✅ Se requiere confirmación explícita antes de eliminar
        - ✅ Los backups se almacenan en `backups/reset_YYYYMMDD_HHMMSS/`
        - ✅ Puedes restaurar manualmente desde los backups si es necesario
        
        ### Uso desde línea de comandos
        
        También puedes usar la utilidad CLI para más control:
        
        ```bash
        # Ver qué se eliminará sin eliminar nada (dry run)
        python utils/reset_system.py --dry-run
        
        # Resetear solo las bases de datos
        python utils/reset_system.py --databases-only --confirm
        
        # Resetear solo las credenciales
        python utils/reset_system.py --credentials-only --confirm
        
        # Reset completo sin backup (no recomendado)
        python utils/reset_system.py --no-backup --confirm
        ```
        
        ### Restauración Manual
        
        Si necesitas restaurar desde un backup:
        
        1. Ve a la carpeta `backups/reset_YYYYMMDD_HHMMSS/`
        2. Copia los archivos `.db` a la carpeta `data/`
        3. Copia el archivo `.env` a la raíz del proyecto
        4. Si hay archivos `.json`, cópialos a la raíz del proyecto
        5. Reinicia el dashboard
        """)
        
        st.markdown("---")
        st.info("💡 **Tip**: Mantén siempre backups de tus credenciales en un lugar seguro fuera del proyecto.")


if __name__ == "__main__":
    main()
