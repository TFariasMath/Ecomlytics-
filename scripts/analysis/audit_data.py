"""
Script de Auditoría de Datos Mejorado.

Validación completa de integridad y calidad de datos del ETL con:
- Logging estructurado
- Alertas automáticas
- Métricas detalladas
- Exportación de reportes
"""

import sqlite3
import pandas as pd
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any
import json

sys.path.append(os.path.dirname(__file__))
from config.logging_config import setup_logger
from utils.notifications import default_notifier
from utils.database import get_db_connection

logger = setup_logger(__name__)

DATABASE_WC = os.path.join(os.path.dirname(__file__), 'data', 'woocommerce.db')
DATABASE_GA = os.path.join(os.path.dirname(__file__), 'data', 'analytics.db')


class DataAuditor:
    """Clase para auditar datos del ETL."""
    
    def __init__(self):
        self.results = {}
        self.issues = []
        
    def audit_woocommerce(self) -> Dict[str, Any]:
        """
        Audita datos de WooCommerce.
        
        Returns:
            Diccionario con resultados de auditoría
        """
        logger.info("="*60)
        logger.info("🔍 Iniciando auditoría de WooCommerce")
        logger.info("="*60)
        
        try:
            with get_db_connection(DATABASE_WC) as conn:
                # Cargar datos
                df_orders = pd.read_sql("SELECT * FROM wc_orders", conn)
                df_items = pd.read_sql("SELECT * FROM wc_order_items", conn)
            
            if df_orders.empty:
                self.issues.append("❌ No hay datos en wc_orders")
                return {}
            
            # Análisis de órdenes
            total_orders = len(df_orders)
            total_revenue = df_orders['total'].sum()
            avg_ticket = total_revenue / total_orders if total_orders > 0 else 0
            
            status_dist = df_orders['status'].value_counts().to_dict()
            
            logger.info(f"✓ Total órdenes: {total_orders}")
            logger.info(f"✓ Ingresos totales: ${total_revenue:,.0f}")
            logger.info(f"✓ Ticket promedio: ${avg_ticket:,.0f}")
            logger.info(f"✓ Distribución por estado: {status_dist}")
            
            # Análisis de items
            total_items = len(df_items)
            unique_products = df_items['product_name'].nunique()
            total_units = df_items['quantity'].sum()
            revenue_items = df_items['total'].sum()
            
            logger.info(f"✓ Total items: {total_items}")
            logger.info(f"✓ Productos únicos: {unique_products}")
            logger.info(f"✓ Unidades vendidas: {total_units}")
            
            # Validación cruzada
            difference = total_revenue - revenue_items
            difference_pct = abs(difference / total_revenue * 100) if total_revenue > 0 else 0
            
            logger.info(f"🔍 Diferencia órdenes vs items: ${abs(difference):,.0f} ({difference_pct:.2f}%)")
            
            if difference_pct > 5:
                issue = f"Diferencia significativa detectada: {difference_pct:.2f}%"
                self.issues.append(f"⚠️ {issue}")
                logger.warning(issue)
            else:
                logger.info("✅ Datos consistentes")
            
            # Verificación de integridad referencial
            orders_in_orders = set(df_orders['order_id'].unique())
            orders_in_items = set(df_items['order_id'].unique())
            
            orphan_items = orders_in_items - orders_in_orders
            orders_without_items = orders_in_orders - orders_in_items
            
            if orphan_items:
                issue = f"Items huérfanos detectados: {len(orphan_items)}"
                self.issues.append(f"⚠️ {issue}")
                logger.warning(issue)
            
            if orders_without_items:
                logger.warning(f"⚠️ Órdenes sin items: {len(orders_without_items)}")
            
            # Análisis temporal (últimos 30 días)
            df_orders['date_created'] = pd.to_datetime(df_orders['date_created'])
            last_30_days = datetime.now() - timedelta(days=30)
            recent_orders = df_orders[df_orders['date_created'] >= last_30_days]
            recent_revenue = recent_orders['total'].sum()
            
            logger.info(f"📅 Últimos 30 días: {len(recent_orders)} órdenes, ${recent_revenue:,.0f}")
            
            # Preparar resultados
            results = {
                'total_orders': total_orders,
                'total_revenue': float(total_revenue),
                'avg_ticket': float(avg_ticket),
                'status_distribution': status_dist,
                'total_items': total_items,
                'unique_products': unique_products,
                'total_units': int(total_units),
                'difference_pct': float(difference_pct),
                'orphan_items': len(orphan_items),
                'orders_without_items': len(orders_without_items),
                'recent_orders_30d': len(recent_orders),
                'recent_revenue_30d': float(recent_revenue)
            }
            
            self.results['woocommerce'] = results
            return results
            
        except Exception as e:
            logger.error(f"Error en auditoría de WooCommerce: {e}", exc_info=True)
            self.issues.append(f"❌ Error: {str(e)}")
            return {}
    
    def audit_analytics(self) -> Dict[str, Any]:
        """
        Audita datos de Google Analytics.
        
        Returns:
            Diccionario con resultados de auditoría
        """
        logger.info("="*60)
        logger.info("🔍 Iniciando auditoría de Google Analytics")
        logger.info("="*60)
        
        try:
            with get_db_connection(DATABASE_GA) as conn:
                # Verificar existencia de tablas
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                if not tables:
                    self.issues.append("❌ No hay tablas en analytics.db")
                    return {}
                
                logger.info(f"✓ Tablas encontradas: {len(tables)}")
                
                results = {}
                
                # Analizar cada tabla
                for table in tables:
                    df = pd.read_sql(f"SELECT * FROM {table}", conn)
                    results[table] = {
                        'rows': len(df),
                        'columns': list(df.columns),
                        'date_range': None
                    }
                    
                    # Obtener rango de fechas si tiene columna Fecha
                    if 'Fecha' in df.columns and not df.empty:
                        date_col = pd.to_datetime(df['Fecha'], format='%Y%m%d', errors='coerce')
                        if date_col.notna().any():
                            results[table]['date_range'] = {
                                'min': str(date_col.min().date()),
                                'max': str(date_col.max().date())
                            }
                    
                    logger.info(f"✓ {table}: {len(df)} filas")
                
                self.results['analytics'] = results
                return results
                
        except Exception as e:
            logger.error(f"Error en auditoría de Analytics: {e}", exc_info=True)
            self.issues.append(f"❌ Error: {str(e)}")
            return {}
    
    def generate_report(self, output_file: str = None) -> None:
        """
        Genera reporte de auditoría.
        
        Args:
            output_file: Path para exportar reporte JSON (opcional)
        """
        logger.info("="*60)
        logger.info("📋 RESUMEN DE AUDITORÍA")
        logger.info("="*60)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'results': self.results,
            'issues': self.issues,
            'status': 'PASS' if not self.issues else 'WARNINGS' if len(self.issues) < 3 else 'FAIL'
        }
        
        # Log resumen
        logger.info(f"Estado: {report['status']}")
        logger.info(f"Issues detectados: {len(self.issues)}")
        
        if self.issues:
            logger.warning("⚠️ Problemas encontrados:")
            for issue in self.issues:
                logger.warning(f"  {issue}")
        else:
            logger.info("✅ No se detectaron problemas")
        
        # Exportar a archivo
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"📄 Reporte exportado a: {output_file}")
        
        # Enviar notificación si hay problemas críticos
        if len(self.issues) >= 3:
            default_notifier.send_data_quality_alert(
                issue="Múltiples problemas detectados en auditoría",
                details="\n".join(self.issues)
            )


def main():
    """Ejecuta auditoría completa."""
    auditor = DataAuditor()
    
    # Auditar ambas bases de datos
    auditor.audit_woocommerce()
    auditor.audit_analytics()
    
    # Generar reporte
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"logs/audit_report_{timestamp}.json"
    auditor.generate_report(output_file)
    
    logger.info("="*60)
    logger.info("✅ Auditoría completada")
    logger.info("="*60)


if __name__ == "__main__":
    main()
