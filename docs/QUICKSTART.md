# 🚀 Guía de Inicio Rápido

## Primeros Pasos Después de la Implementación

### 1. Instalar Dependencias (Si aún no lo hizo)

```powershell
pip install -r requirements.txt
```

Esto instalará:
- `tenacity` - Retry logic
- `pytest`, `pytest-cov`, `pytest-mock` - Testing
- `APScheduler` - Scheduling

---

### 2. Aplicar Índices a las Bases de Datos

```powershell
python config/apply_indexes.py
```

Esto creará índices en ambas bases de datos para optimizar las consultas del dashboard.

---

### 3. Ejecutar Tests

```powershell
# Tests básicos
pytest tests/ -v

# Con coverage
pytest tests/ --cov=etl --cov=utils --cov-report=html
```

---

### 4. Ejecutar Mantenimiento de DB (Opcional pero recomendado)

```powershell
python utils/db_maintenance.py
```

Esto hará:
- Backup de las bases de datos
- VACUUM para recuperar espacio
- ANALYZE para optimizar queries
- Verificación de integridad

---

### 5. Probar los ETLs Refactorizados

**Google Analytics:**
```powershell
python etl/extract_analytics.py
```

**WooCommerce:**
```powershell
python etl/extract_woocommerce.py
```

Verificar que:
- ✅ Los logs aparecen en `logs/etl.log`
- ✅ Solo extrae datos nuevos (carga incremental)
- ✅ Muestra tiempos de ejecución

---

### 6. Ejecutar Auditoría

```powershell
python audit_data.py
```

Esto generará:
- Reporte en consola con logging estructurado
- Archivo JSON en `logs/audit_report_YYYYMMDD_HHMMSS.json`
- Alerta por email si detecta problemas críticos (si está configurado)

---

### 7. Configurar Notificaciones por Email (Opcional)

Si desea recibir alertas por email:

1. Crear variables de entorno (o agregarlas al código):
   - `EMAIL_FROM` - Email remitente (ej: alertas@miempresa.com)
   - `EMAIL_PASSWORD` - Contraseña del email
   - `EMAIL_TO` - Emails destino separados por coma

2. Para Gmail, necesita crear una "App Password":
   - Ir a: https://myaccount.google.com/apppasswords
   - Crear contraseña para "Mail"
   - Usar esa contraseña en `EMAIL_PASSWORD`

---

### 8. Configurar Scheduler (Opcional)

Para ejecuciones automáticas diarias:

```powershell
python scheduler.py
```

Presionar Ctrl+C para detener.

**Horarios programados:**
- 2:00 AM - Google Analytics
- 3:00 AM - WooCommerce

---

## 📊 Comandos Útiles

### Ver Logs en Tiempo Real
```powershell
Get-Content logs/etl.log -Wait -Tail 50
```

### Ejecutar Solo Tests Unitarios
```powershell
pytest tests/test_extractors.py::TestDatabaseUtils -v
```

### Crear Backup Manual
```powershell
python -c "from utils.db_maintenance import backup_database; backup_database('data/woocommerce.db')"
```

---

## ⚠️ Problemas Comunes

### Error: `ModuleNotFoundError: No module named 'tenacity'`
**Solución:** `pip install tenacity`

### Error: `Permission denied` en logs
**Solución:** Cerrar cualquier programa que esté abriendo `logs/etl.log`

### Error: `Database is locked`
**Solución:** Cerrar dashboards de Streamlit antes de ejecutar ETLs

### Notificaciones no se envían
**Solución:** Verificar variables de entorno `EMAIL_FROM`, `EMAIL_PASSWORD`, `EMAIL_TO`

---

## 📈 Monitoreo

### Verificar Última Extracción
```python
from utils.database import get_last_extraction_date

last_wc = get_last_extraction_date('wc_orders', 'date_only', 'data/woocommerce.db')
print(f"Última extracción WooCommerce: {last_wc}")

last_ga = get_last_extraction_date('ga4_channels', 'Fecha', 'data/analytics.db')
print(f"Última extracción Analytics: {last_ga}")
```

### Ver Tamaño de Bases de Datos
```powershell
Get-ChildItem data/*.db | Select-Object Name, @{Name="Size(MB)";Expression={[math]::Round($_.Length / 1MB, 2)}}
```

---

## 🎯 Próximos Pasos Recomendados

1. ✅ **Ejecutar todo manualmente** para verificar funcionamiento
2. ✅ **Revisar logs** en `logs/etl.log`
3. ✅ **Ejecutar auditoría** para validar datos
4. ✅ **Configurar scheduler** para automatización
5. 🔮 **Configurar emails** para alertas (opcional)
6. 🔮 **Documentar** cualquier ajuste específico para tu entorno

---

**Última actualización**: 18 de diciembre de 2025
