
import os
import sys
import argparse
import subprocess
import logging
from datetime import datetime
import importlib

# Add project root to path
sys.path.append(os.path.dirname(__file__))

from config.logging_config import setup_logger

logger = setup_logger("UnifiedPipeline")

def run_step(step_name, module_path):
    """Executes a specific ETL step by importing and running its main function."""
    logger.info("="*60)
    logger.info(f"🚀 Iniciando paso: {step_name}")
    logger.info("="*60)
    
    try:
        # Import dynamically to ensure fresh load
        module = importlib.import_module(module_path)
        importlib.reload(module)
        
        # Execute main
        if hasattr(module, 'main'):
            module.main()
            logger.info(f"✅ Paso {step_name} completado exitosamente.")
            return True
        else:
            logger.error(f"❌ El módulo {module_path} no tiene función main()")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error crítico en {step_name}: {e}", exc_info=True)
        return False

def main():
    parser = argparse.ArgumentParser(description="Unified ETL Pipeline for Frutos Tayen")
    parser.add_argument("--dashboard", action="store_true", help="Launch dashboard after ETL")
    parser.add_argument("--skip-etl", action="store_true", help="Skip ETL and just launch dashboard")
    args = parser.parse_args()

    success = True
    
    if not args.skip_etl:
        print("\n🔵 Iniciando Pipeline de Datos...")
        
        # 1. WooCommerce (Critical)
        if not run_step("WooCommerce ETL", "etl.extract_woocommerce"):
            print("⚠️ Advertencia: Falló carga de WooCommerce")
            success = False
            
        # 2. Google Analytics
        if not run_step("Google Analytics 4 ETL", "etl.extract_analytics"):
             print("⚠️ Advertencia: Falló carga de GA4")
             success = False
             
        # 3. Facebook Insights
        if not run_step("Facebook ETL", "etl.extract_facebook"):
             print("⚠️ Advertencia: Falló carga de Facebook")
             success = False
        
        print("\n" + "="*60)
        if success:
            print("✅ Pipeline completado exitosamente")
        else:
            print("⚠️ Pipeline completado con errores (ver logs)")
        print("="*60 + "\n")

    if args.dashboard:
        print("🚀 Lanzando Dashboard...")
        dashboard_path = os.path.join(os.path.dirname(__file__), "dashboard", "app_woo_v2.py")
        
        # Use subprocess to run streamlit independent of this script
        try:
            # shell=True required on Windows for resolving path
            subprocess.run(["streamlit", "run", dashboard_path], check=True, shell=True)
        except subprocess.CalledProcessError as e:
            print(f"Error lanzando dashboard: {e}")
            # Fallback to python -m streamlit if streamlit is not in PATH
            subprocess.run([sys.executable, "-m", "streamlit", "run", dashboard_path], check=True, shell=True)
        except KeyboardInterrupt:
            print("\nDashboard detenido por el usuario.")

if __name__ == "__main__":
    main()
