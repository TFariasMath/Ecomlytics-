"""
Data Quality Validators.

Sistema de validación de calidad de datos para detectar problemas
antes de guardar en la base de datos.
"""

import pandas as pd
from typing import Tuple, List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ValidationResult:
    """Resultado de una validación."""
    
    def __init__(self, is_valid: bool, errors: List[str], warnings: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors
        self.warnings = warnings or []
    
    def __bool__(self) -> bool:
        return self.is_valid
    
    def __repr__(self) -> str:
        status = "✅ VALID" if self.is_valid else "❌ INVALID"
        msg = f"{status}"
        if self.errors:
            msg += f" | Errors: {len(self.errors)}"
        if self.warnings:
            msg += f" | Warnings: {len(self.warnings)}"
        return msg
    
    def get_summary(self) -> str:
        """Retorna un resumen detallado de la validación."""
        lines = [repr(self)]
        if self.errors:
            lines.append("\nErrores:")
            lines.extend(f"  - {e}" for e in self.errors)
        if self.warnings:
            lines.append("\nAdvertencias:")
            lines.extend(f"  - {w}" for w in self.warnings)
        return "\n".join(lines)


class DataQualityValidator:
    """
    Validador de calidad de datos.
    
    Proporciona validaciones comunes para DataFrames.
    """
    
    @staticmethod
    def validate_not_empty(df: pd.DataFrame, name: str = "DataFrame") -> ValidationResult:
        """Valida que el DataFrame no esté vacío."""
        if df.empty:
            return ValidationResult(False, [f"{name} está vacío"])
        return ValidationResult(True, [])
    
    @staticmethod
    def validate_required_columns(
        df: pd.DataFrame,
        required_columns: List[str],
        name: str = "DataFrame"
    ) -> ValidationResult:
        """Valida que existan las columnas requeridas."""
        missing = set(required_columns) - set(df.columns)
        if missing:
            return ValidationResult(
                False,
                [f"{name} le faltan columnas: {', '.join(missing)}"]
            )
        return ValidationResult(True, [])
    
    @staticmethod
    def validate_no_nulls(
        df: pd.DataFrame,
        columns: List[str],
        name: str = "DataFrame"
    ) -> ValidationResult:
        """Valida que no haya valores nulos en columnas específicas."""
        errors = []
        for col in columns:
            if col in df.columns:
                null_count = df[col].isna().sum()
                if null_count > 0:
                    errors.append(f"{name}.{col} tiene {null_count} valores nulos")
        
        return ValidationResult(len(errors) == 0, errors)
    
    @staticmethod
    def validate_date_column(
        df: pd.DataFrame,
        date_column: str,
        name: str = "DataFrame",
        min_date: Optional[str] = None,
        max_date: Optional[str] = None
    ) -> ValidationResult:
        """
        Valida que una columna de fecha sea válida.
        
        Args:
            df: DataFrame a validar
            date_column: Nombre de la columna de fecha
            name: Nombre descriptivo del DataFrame
            min_date: Fecha mínima permitida (YYYY-MM-DD)
            max_date: Fecha máxima permitida (YYYY-MM-DD)
        """
        errors = []
        warnings = []
        
        if date_column not in df.columns:
            return ValidationResult(False, [f"Columna {date_column} no existe"])
        
        # Validar formato de fecha
        try:
            dates = pd.to_datetime(df[date_column], errors='coerce')
            invalid_count = dates.isna().sum()
            
            if invalid_count > 0:
                errors.append(
                    f"{name}.{date_column} tiene {invalid_count} fechas inválidas"
                )
            
            # Validar rango de fechas
            if min_date and not dates.empty:
                min_allowed = pd.to_datetime(min_date)
                below_min = (dates < min_allowed).sum()
                if below_min > 0:
                    warnings.append(
                        f"{below_min} fechas son anteriores a {min_date}"
                    )
            
            if max_date and not dates.empty:
                max_allowed = pd.to_datetime(max_date)
                above_max = (dates > max_allowed).sum()
                if above_max > 0:
                    warnings.append(
                        f"{above_max} fechas son posteriores a {max_date}"
                    )
                    
        except Exception as e:
            errors.append(f"Error validando fechas: {str(e)}")
        
        return ValidationResult(len(errors) == 0, errors, warnings)
    
    @staticmethod
    def validate_numeric_positive(
        df: pd.DataFrame,
        columns: List[str],
        name: str = "DataFrame",
        allow_zero: bool = True
    ) -> ValidationResult:
        """Valida que columnas numéricas tengan valores positivos."""
        errors = []
        warnings = []
        
        for col in columns:
            if col not in df.columns:
                continue
            
            if not pd.api.types.is_numeric_dtype(df[col]):
                warnings.append(f"{col} no es numérica")
                continue
            
            if allow_zero:
                negative_count = (df[col] < 0).sum()
                if negative_count > 0:
                    errors.append(f"{name}.{col} tiene {negative_count} valores negativos")
            else:
                non_positive_count = (df[col] <= 0).sum()
                if non_positive_count > 0:
                    errors.append(
                        f"{name}.{col} tiene {non_positive_count} valores ≤ 0"
                    )
        
        return ValidationResult(len(errors) == 0, errors, warnings)
    
    @staticmethod
    def validate_no_duplicates(
        df: pd.DataFrame,
        subset: List[str],
        name: str = "DataFrame"
    ) -> ValidationResult:
        """Valida que no haya duplicados en un subset de columnas."""
        duplicate_count = df.duplicated(subset=subset).sum()
        
        if duplicate_count > 0:
            return ValidationResult(
                False,
                [f"{name} tiene {duplicate_count} filas duplicadas en {subset}"],
                []
            )
        
        return ValidationResult(True, [])
    
    @staticmethod
    def detect_outliers(
        df: pd.DataFrame,
        column: str,
        threshold: float = 3.0,
        name: str = "DataFrame"
    ) -> ValidationResult:
        """
        Detecta outliers usando z-score.
        
        Args:
            df: DataFrame
            column: Columna a analizar
            threshold: Número de desviaciones estándar
            name: Nombre descriptivo
        """
        warnings = []
        
        if column not in df.columns:
            return ValidationResult(True, [], [])
        
        if not pd.api.types.is_numeric_dtype(df[column]):
            return ValidationResult(True, [], [])
        
        mean = df[column].mean()
        std = df[column].std()
        
        if std == 0:
            return ValidationResult(True, [], [])
        
        z_scores = ((df[column] - mean) / std).abs()
        outliers_count = (z_scores > threshold).sum()
        
        if outliers_count > 0:
            warnings.append(
                f"{name}.{column} tiene {outliers_count} valores atípicos "
                f"(>{threshold} std deviations)"
            )
        
        return ValidationResult(True, [], warnings)


class GA4DataValidator:
    """Validador específico para datos de Google Analytics 4."""
    
    @staticmethod
    def validate_report(df: pd.DataFrame, report_name: str) -> ValidationResult:
        """
        Valida un reporte de GA4.
        
        Args:
            df: DataFrame con datos de GA4
            report_name: Nombre del reporte
        """
        validator = DataQualityValidator()
        all_errors = []
        all_warnings = []
        
        # 1. No vacío
        result = validator.validate_not_empty(df, report_name)
        all_errors.extend(result.errors)
        
        if not result.is_valid:
            return ValidationResult(False, all_errors, all_warnings)
        
        # 2. Fecha válida
        if 'Fecha' in df.columns:
            result = validator.validate_date_column(
                df, 'Fecha', report_name,
                min_date='2020-01-01',
                max_date=datetime.now().strftime('%Y-%m-%d')
            )
            all_errors.extend(result.errors)
            all_warnings.extend(result.warnings)
        
        # 3. Métricas positivas
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        if numeric_cols:
            result = validator.validate_numeric_positive(
                df, numeric_cols, report_name, allow_zero=True
            )
            all_errors.extend(result.errors)
            all_warnings.extend(result.warnings)
        
        # 4. Detectar outliers en métricas principales
        if 'Sesiones' in df.columns:
            result = validator.detect_outliers(df, 'Sesiones', threshold=3.0, name=report_name)
            all_warnings.extend(result.warnings)
        
        return ValidationResult(len(all_errors) == 0, all_errors, all_warnings)


class WooCommerceDataValidator:
    """Validador específico para datos de WooCommerce."""
    
    @staticmethod
    def validate_orders(df: pd.DataFrame) -> ValidationResult:
        """Valida datos de órdenes de WooCommerce."""
        validator = DataQualityValidator()
        all_errors = []
        all_warnings = []
        
        # 1. No vacío
        result = validator.validate_not_empty(df, "WooCommerce Orders")
        all_errors.extend(result.errors)
        
        if not result.is_valid:
            return ValidationResult(False, all_errors, all_warnings)
        
        # 2. Columnas requeridas
        required = ['order_id', 'date_created', 'total', 'status']
        result = validator.validate_required_columns(df, required, "WooCommerce Orders")
        all_errors.extend(result.errors)
        
        # 3. No nulos en campos críticos
        result = validator.validate_no_nulls(df, ['order_id', 'total'], "WooCommerce Orders")
        all_errors.extend(result.errors)
        
        # 4. Total positivo
        if 'total' in df.columns:
            result = validator.validate_numeric_positive(
                df, ['total'], "WooCommerce Orders", allow_zero=False
            )
            all_errors.extend(result.errors)
        
        # 5. No duplicados por order_id
        if 'order_id' in df.columns:
            result = validator.validate_no_duplicates(df, ['order_id'], "WooCommerce Orders")
            all_errors.extend(result.errors)
        
        # 6. Fecha válida
        if 'date_created' in df.columns:
            result = validator.validate_date_column(
                df, 'date_created', "WooCommerce Orders",
                min_date='2020-01-01'
            )
            all_errors.extend(result.errors)
            all_warnings.extend(result.warnings)
        
        return ValidationResult(len(all_errors) == 0, all_errors, all_warnings)
    
    @staticmethod
    def validate_order_items(df: pd.DataFrame) -> ValidationResult:
        """Valida datos de items de órdenes."""
        validator = DataQualityValidator()
        all_errors = []
        all_warnings = []
        
        # 1. No vacío
        result = validator.validate_not_empty(df, "WooCommerce Order Items")
        all_errors.extend(result.errors)
        
        if not result.is_valid:
            return ValidationResult(False, all_errors, all_warnings)
        
        # 2. Columnas requeridas
        required = ['order_id', 'product_id', 'product_name', 'quantity']
        result = validator.validate_required_columns(df, required, "WooCommerce Order Items")
        all_errors.extend(result.errors)
        
        # 3. Cantidad positiva
        if 'quantity' in df.columns:
            result = validator.validate_numeric_positive(
                df, ['quantity'], "WooCommerce Order Items", allow_zero=False
            )
            all_errors.extend(result.errors)
        
        return ValidationResult(len(all_errors) == 0, all_errors, all_warnings)


def validate_and_log(df: pd.DataFrame, validator_func, name: str) -> bool:
    """
    Helper para validar y loggear resultados.
    
    Args:
        df: DataFrame a validar
        validator_func: Función validadora
        name: Nombre descriptivo
    
    Returns:
        True si es válido, False en caso contrario
    """
    result = validator_func(df)
    
    if result.is_valid:
        logger.info(f"✅ {name}: Validación exitosa")
        if result.warnings:
            for warning in result.warnings:
                logger.warning(f"⚠️ {name}: {warning}")
    else:
        logger.error(f"❌ {name}: Validación FALLIDA")
        for error in result.errors:
            logger.error(f"   {error}")
        for warning in result.warnings:
            logger.warning(f"⚠️ {warning}")
    
    return result.is_valid


class FacebookDataValidator:
    """Validador específico para datos de Facebook."""
    
    @staticmethod
    def validate_insights(df: pd.DataFrame) -> ValidationResult:
        """Valida datos de insights de Facebook."""
        validator = DataQualityValidator()
        all_errors = []
        all_warnings = []
        
        # 1. No vacío
        result = validator.validate_not_empty(df, "Facebook Insights")
        all_errors.extend(result.errors)
        
        if not result.is_valid:
            return ValidationResult(False, all_errors, all_warnings)
        
        # 2. Columnas requeridas
        required = ['date', 'metric', 'value', 'period']
        result = validator.validate_required_columns(df, required, "Facebook Insights")
        all_errors.extend(result.errors)
        
        # 3. Fecha válida
        if 'date' in df.columns:
            result = validator.validate_date_column(
                df, 'date', "Facebook Insights",
                min_date='2020-01-01'
            )
            all_errors.extend(result.errors)
            all_warnings.extend(result.warnings)
            
        # 4. Valor positivo
        if 'value' in df.columns:
            # Algunas métricas podrían ser negativas teóricamente (ej. net likes), pero la mayoría son positivas
            result = validator.validate_numeric_positive(
                df, ['value'], "Facebook Insights", allow_zero=True
            )
            all_warnings.extend(result.errors) # Treat as warning just in case
            
        return ValidationResult(len(all_errors) == 0, all_errors, all_warnings)
