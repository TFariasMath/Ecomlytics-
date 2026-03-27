# 📁 Archive Directory

Este directorio contiene archivos legacy y datos de análisis histórico que no son necesarios para la operación del proyecto pero se conservan por referencia.

## Estructura

### `/legacy_scripts`
Scripts de análisis y debugging utilizados durante el desarrollo inicial del proyecto. Estos scripts fueron herramientas temporales para:
- Análisis exhaustivo de discrepancias en datos
- Cálculos de verificación
- Comparaciones con datos de WooCommerce
- Identificación de pedidos problemáticos

**Nota**: Estos scripts NO son parte del pipeline de producción.

### `/analysis_data`
Datos históricos de análisis en formatos CSV, TXT y JSON:
- Listas de exclusión de pedidos
- Reportes de análisis
- Datos de comparación con WooCommerce

### `/test_scripts`
Scripts de testing adhoc y experimentales utilizados durante el desarrollo.

---

## ⚠️ Importante

Los archivos en este directorio:
- NO se usan en producción
- NO son parte del ETL pipeline
- Pueden ser eliminados si el espacio en disco es un problema
- Se mantienen por si se necesita referencia histórica

## Mantenimiento

Se recomienda revisar y limpiar este directorio cada 6 meses, conservando solo lo absolutamente necesario para auditoría o referencia.

---

**Fecha de archivo**: 22 de diciembre de 2025
**Razón**: Limpieza y organización del proyecto
