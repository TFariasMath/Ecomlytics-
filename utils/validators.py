"""
Validadores de Calidad de Datos.

Funciones para validar la calidad e integridad de los datos extraídos.
"""

import pandas as pd
from typing import List, Dict, Any, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config.logging_config import setup_logger

logger = setup_logger(__name__)


class DataValidator:
    """Validador de calidad de datos."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_dataframe(
        self,
        df: pd.DataFrame,
        name: str,
        required_columns: Optional[List[str]] = None,
        min_rows: int = 1
    ) -> bool:
        """
        Valida un DataFrame básico.
        
        Args:
            df: DataFrame a validar
            name: Nombre descriptivo
            required_columns: Columnas requeridas
            min_rows: Mínimo de filas esperadas
        
        Returns:
            True si pasa validación
        """
        logger.info(f"🔍 Validando {name}...")
        valid = True
        
        # Verificar que no esté vacío
        if df.empty:
            self.errors.append(f"{name}: DataFrame vacío")
            logger.error(f"❌ {name}: DataFrame vacío")
            return False
        
        # Verificar mínimo de filas
        if len(df) < min_rows:
            self.warnings.append(f"{name}: Solo {len(df)} filas (esperado >= {min_rows})")
            logger.warning(f"⚠️ {name}: Solo {len(df)} filas")
        
        # Verificar columnas requeridas
        if required_columns:
            missing = set(required_columns) - set(df.columns)
            if missing:
                self.errors.append(f"{name}: Columnas faltantes: {missing}")
                logger.error(f"❌ {name}: Faltan columnas: {missing}")
                valid = False
        
        # Verificar duplicados
        if df.duplicated().any():
            dup_count = df.duplicated().sum()
            self.warnings.append(f"{name}: {dup_count} filas duplicadas")
            logger.warning(f"⚠️ {name}: {dup_count} duplicados")
        
        if valid:
            logger.info(f"✅ {name}: Validación OK ({len(df)} filas)")
        
        return valid
    
    def validate_numeric_column(
        self,
        df: pd.DataFrame,
        column: str,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        allow_null: bool = False
    ) -> bool:
        """
        Valida una columna numérica.
        
        Args:
            df: DataFrame
            column: Nombre de columna
            min_value: Valor mínimo permitido
            max_value: Valor máximo permitido
            allow_null: Si permite valores nulos
        
        Returns:
            True si pasa validación
        """
        valid = True
        
        # Verificar existencia
        if column not in df.columns:
            self.errors.append(f"Columna {column} no existe")
            return False
        
        # Verificar nulos
        null_count = df[column].isna().sum()
        if null_count > 0 and not allow_null:
            self.errors.append(f"{column}: {null_count} valores nulos")
            logger.error(f"❌ {column}: {null_count} nulos")
            valid = False
        
        # Verificar rango
        if min_value is not None:
            below_min = (df[column] < min_value).sum()
            if below_min > 0:
                self.errors.append(f"{column}: {below_min} valores < {min_value}")
                logger.error(f"❌ {column}: {below_min} valores fuera de rango")
                valid = False
        
        if max_value is not None:
            above_max = (df[column] > max_value).sum()
            if above_max > 0:
                self.errors.append(f"{column}: {above_max} valores > {max_value}")
                logger.error(f"❌ {column}: {above_max} valores fuera de rango")
                valid = False
        
        return valid
    
    def validate_date_column(
        self,
        df: pd.DataFrame,
        column: str,
        min_date: Optional[str] = None,
        max_date: Optional[str] = None
    ) -> bool:
        """
        Valida una columna de fecha.
        
        Args:
            df: DataFrame
            column: Nombre de columna
            min_date: Fecha mínima (YYYY-MM-DD)
            max_date: Fecha máxima (YYYY-MM-DD)
        
        Returns:
            True si pasa validación
        """
        valid = True
        
        if column not in df.columns:
            self.errors.append(f"Columna {column} no existe")
            return False
        
        # Convertir a datetime
        try:
            dates = pd.to_datetime(df[column])
        except Exception as e:
            self.errors.append(f"{column}: Error convirtiendo a fecha: {e}")
            return False
        
        # Verificar rango
        if min_date:
            min_dt = pd.to_datetime(min_date)
            below_min = (dates < min_dt).sum()
            if below_min > 0:
                self.warnings.append(f"{column}: {below_min} fechas antes de {min_date}")
        
        if max_date:
            max_dt = pd.to_datetime(max_date)
            above_max = (dates > max_dt).sum()
            if above_max > 0:
                self.warnings.append(f"{column}: {above_max} fechas después de {max_date}")
        
        return valid
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Retorna resumen de validación.
        
        Returns:
            Diccionario con errores y warnings
        """
        return {
            'errors': self.errors,
            'warnings': self.warnings,
            'status': 'PASS' if not self.errors else 'FAIL',
            'total_issues': len(self.errors) + len(self.warnings)
        }


def validate_woocommerce_data(df_orders: pd.DataFrame, df_items: pd.DataFrame) -> DataValidator:
    """
    Valida datos de WooCommerce.
    
    Args:
        df_orders: DataFrame de órdenes
        df_items: DataFrame de items
    
    Returns:
        DataValidator con resultados
    """
    validator = DataValidator()
    
    # Validar órdenes
    validator.validate_dataframe(
        df_orders,
        "wc_orders",
        required_columns=['order_id', 'total', 'status', 'date_created'],
        min_rows=1
    )
    
    validator.validate_numeric_column(df_orders, 'total', min_value=0)
    validator.validate_date_column(df_orders, 'date_created', min_date='2020-01-01')
    
    # Validar items
    validator.validate_dataframe(
        df_items,
        "wc_order_items",
        required_columns=['order_id', 'product_id', 'quantity'],
        min_rows=1
    )
    
    validator.validate_numeric_column(df_items, 'quantity', min_value=1)
    
    return validator


def validate_analytics_data(df: pd.DataFrame, report_name: str) -> DataValidator:
    """
    Valida datos de Google Analytics.
    
    Args:
        df: DataFrame del reporte
        report_name: Nombre del reporte
    
    Returns:
        DataValidator con resultados
    """
    validator = DataValidator()
    
    validator.validate_dataframe(
        df,
        f"ga4_{report_name}",
        required_columns=['Fecha'],
        min_rows=1
    )
    
    validator.validate_date_column(df, 'Fecha', min_date='2023-01-01')
    
    return validator
