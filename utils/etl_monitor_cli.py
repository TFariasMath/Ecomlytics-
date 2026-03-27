"""
Script de utilidades para monitorear el estado de los ETL.

Proporciona comandos para ver el historial, estadísticas y salud de los procesos ETL.
"""

import os
import sys
import argparse
from datetime import datetime, timedelta

# Agregar path para imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.monitoring import ETLMonitor
from config.logging_config import setup_logger

logger = setup_logger(__name__)

MONITORING_DB = os.path.join(os.path.dirname(__file__), '..', 'data', 'monitoring.db')


def show_history(etl_name=None, limit=10):
    """Muestra el historial de ejecuciones."""
    monitor = ETLMonitor(MONITORING_DB)
    
    print("\n" + "="*70)
    print("📊 HISTORIAL DE EJECUCIONES ETL")
    print("="*70)
    
    df = monitor.get_execution_history(etl_name=etl_name, limit=limit)
    
    if df.empty:
        print("No hay ejecuciones registradas")
        return
    
    # Mostrar en formato tabla
    for idx, row in df.iterrows():
        status_icon = "✅" if row['status'] == 'SUCCESS' else "❌"
        
        print(f"\n{status_icon} {row['etl_name']} - {row['execution_id']}")
        print(f"   Inicio: {row['start_time']}")
        print(f"   Duración: {row['duration_seconds']:.2f}s")
        print(f"   Filas: {row['rows_loaded']:,}")
        
        if row['error_count'] > 0:
            print(f"   ❌ Errores: {row['error_count']}")
            if row['errors']:
                for error in str(row['errors']).split('|')[:3]:
                    print(f"      - {error}")
        
        if row['warning_count'] > 0:
            print(f"   ⚠️ Advertencias: {row['warning_count']}")


def show_stats(etl_name=None, days=7):
    """Muestra estadísticas de ejecuciones."""
    monitor = ETLMonitor(MONITORING_DB)
    
    print("\n" + "="*70)
    print(f"📈 ESTADÍSTICAS ETL - Últimos {days} días")
    if etl_name:
        print(f"   ETL: {etl_name}")
    print("="*70)
    
    stats = monitor.get_stats(etl_name=etl_name, days=days)
    
    if not stats or stats.get('total_executions', 0) == 0:
        print("No hay estadísticas disponibles")
        return
    
    print(f"\n📊 Ejecuciones Totales: {stats['total_executions']}")
    print(f"   ✅ Exitosas: {stats['successful']}")
    print(f"   ❌ Fallidas: {stats['failed']}")
    print(f"   📈 Success Rate: {stats['success_rate']:.1f}%")
    
    print(f"\n⏱️ Duración:")
    print(f"   Promedio: {stats['avg_duration']:.2f}s")
    print(f"   Máxima: {stats['max_duration']:.2f}s")
    
    print(f"\n📦 Filas Procesadas: {stats['total_rows_loaded']:,}")


def check_health(etl_name, max_failures=3):
    """Verifica la salud de un ETL."""
    monitor = ETLMonitor(MONITORING_DB)
    
    print("\n" + "="*70)
    print(f"🏥 HEALTH CHECK - {etl_name}")
    print("="*70)
    
    health = monitor.check_health(etl_name, max_failures=max_failures)
    
    status_icon = "✅" if health['is_healthy'] else "❌"
    print(f"\n{status_icon} Estado: {health['status']}")
    print(f"   Mensaje: {health['message']}")
    
    if 'consecutive_failures' in health:
        print(f"   Fallos consecutivos: {health['consecutive_failures']}/{max_failures}")


def show_all_etls():
    """Muestra resumen de todos los ETL."""
    monitor = ETLMonitor(MONITORING_DB)
    
    print("\n" + "="*70)
    print("🔍 RESUMEN DE TODOS LOS ETL")
    print("="*70)
    
    # Obtener lista de ETLs únicos
    df = monitor.get_execution_history(limit=100)
    
    if df.empty:
        print("No hay ejecuciones registradas")
        return
    
    etl_names = df['etl_name'].unique()
    
    for etl_name in etl_names:
        print(f"\n🔹 {etl_name}")
        
        # Últimas 3 ejecuciones
        recent = df[df['etl_name'] == etl_name].head(3)
        
        for idx, row in recent.iterrows():
            status_icon = "✅" if row['status'] == 'SUCCESS' else "❌"
            print(f"   {status_icon} {row['start_time'][:16]} - {row['duration_seconds']:.1f}s - {row['rows_loaded']:,} filas")
        
        # Health check
        health = monitor.check_health(etl_name)
        health_icon = "🟢" if health['is_healthy'] else "🔴"
        print(f"   {health_icon} Salud: {health['status']}")


def main():
    """CLI principal."""
    parser = argparse.ArgumentParser(description='Monitor de ETL')
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')
    
    # Comando: history
    history_parser = subparsers.add_parser('history', help='Ver historial de ejecuciones')
    history_parser.add_argument('--etl', help='Filtrar por ETL específico')
    history_parser.add_argument('--limit', type=int, default=10, help='Número de registros')
    
    # Comando: stats
    stats_parser = subparsers.add_parser('stats', help='Ver estadísticas')
    stats_parser.add_argument('--etl', help='Filtrar por ETL específico')
    stats_parser.add_argument('--days', type=int, default=7, help='Días a analizar')
    
    # Comando: health
    health_parser = subparsers.add_parser('health', help='Verificar salud de ETL')
    health_parser.add_argument('etl', help='Nombre del ETL')
    health_parser.add_argument('--max-failures', type=int, default=3, help='Fallos consecutivos permitidos')
    
    # Comando: all
    subparsers.add_parser('all', help='Resumen de todos los ETL')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'history':
            show_history(etl_name=args.etl, limit=args.limit)
        elif args.command == 'stats':
            show_stats(etl_name=args.etl, days=args.days)
        elif args.command == 'health':
            check_health(etl_name=args.etl, max_failures=args.max_failures)
        elif args.command == 'all':
            show_all_etls()
    
    except Exception as e:
        logger.error(f"Error ejecutando comando: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
