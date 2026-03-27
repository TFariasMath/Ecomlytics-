# System Reset Utility

Utilidad para resetear el sistema de Analytics Dashboard, limpiando bases de datos y credenciales.

## Descripción

Esta utilidad permite limpiar completamente el dashboard para:
- Cambiar a una nueva tienda WooCommerce
- Eliminar datos de prueba
- Configurar nuevas credenciales de API
- Solucionar problemas comenzando desde cero

## Características

- ✅ **Backup Automático**: Crea copias de seguridad antes de eliminar
- ✅ **Reset Selectivo**: Elige qué componentes resetear
- ✅ **Modo Dry-Run**: Preview sin eliminar archivos
- ✅ **Interfaz CLI y Web**: Disponible en línea de comandos y Streamlit
- ✅ **Confirmaciones de Seguridad**: Previene eliminaciones accidentales

## Uso desde Línea de Comandos

```bash
# Ver qué se eliminará (recomendado primero)
python utils/reset_system.py --dry-run

# Reset completo con backup (opción más segura)
python utils/reset_system.py

# Solo bases de datos (mantiene credenciales)
python utils/reset_system.py --databases-only --confirm

# Solo credenciales (mantiene bases de datos)
python utils/reset_system.py --credentials-only --confirm

# Sin backup (no recomendado)
python utils/reset_system.py --no-backup --confirm
```

## Uso desde Streamlit

1. Navega a la página **⚙️ System Reset** en el dashboard
2. Selecciona qué componentes resetear:
   - 📊 Bases de datos individuales
   - 🔑 Archivo .env (credenciales)
   - 📄 Archivos JSON de Google Analytics
3. Asegúrate que "Crear backup antes de eliminar" esté marcado
4. Haz clic en "RESETEAR SISTEMA"
5. Confirma la acción en el diálogo de confirmación
6. Espera a que se complete el proceso
7. Ve a **Configuración Inicial** para configurar nuevas credenciales

## Componentes que se pueden Resetear

### Bases de Datos
- `woocommerce.db` - Datos de órdenes, productos y clientes
- `analytics.db` - Datos de Google Analytics
- `facebook.db` - Datos de Facebook Insights
- `monitoring.db` - Logs de ETL y monitoreo

### Credenciales
- `.env` - Archivo con claves de API y configuración

### Archivos JSON
- Archivos de credenciales de Google Cloud Service Account

## Backups

### Ubicación
Los backups se crean en:
```
backups/reset_YYYYMMDD_HHMMSS/
```

Donde `YYYYMMDD_HHMMSS` es la fecha y hora del backup.

### Contenido
Cada backup incluye:
- Todas las bases de datos (.db)
- Archivo .env
- Archivos JSON de credenciales

### Restauración Manual

Si necesitas restaurar desde un backup:

1. Ve a la carpeta `backups/reset_YYYYMMDD_HHMMSS/`
2. Copia los archivos `.db` a la carpeta `data/`
3. Copia el archivo `.env` a la raíz del proyecto
4. Copia los archivos `.json` a la raíz del proyecto
5. Reinicia el dashboard

## Opciones de Línea de Comandos

| Opción | Descripción |
|--------|-------------|
| `--dry-run` | Preview sin eliminar archivos |
| `--databases-only` | Solo resetea bases de datos |
| `--credentials-only` | Solo resetea credenciales |
| `--no-backup` | Omite creación de backup |
| `--confirm` | Omite confirmaciones interactivas |
| `--quiet` | Suprime salida no-error |

## Casos de Uso

### Cambiar de Tienda WooCommerce
```bash
python utils/reset_system.py
```
Luego configura las nuevas credenciales en **Configuración Inicial**.

### Limpiar Solo Datos (Mantener Credenciales)
```bash
python utils/reset_system.py --databases-only --confirm
```

### Actualizar Solo Credenciales de API
```bash
python utils/reset_system.py --credentials-only --confirm
```

### Preview Antes de Resetear
```bash
python utils/reset_system.py --dry-run
```

## Seguridad

- ⚠️ **Siempre se recomienda crear backup** antes de resetear
- ⚠️ **La eliminación es permanente** sin backup
- ✅ **Backups automáticos** están habilitados por defecto
- ✅ **Doble confirmación** requerida en interfaz web

## Gestión de Backups

### Ver Backups Disponibles
En el dashboard, ve a **⚙️ System Reset > Tab: Backups Disponibles**

### Eliminar Backups Antiguos
Puedes eliminar backups antiguos desde la interfaz web o manualmente desde la carpeta `backups/`.

## Solución de Problemas

### Error: "No se encontraron archivos"
- Verifica que estás en el directorio correcto del proyecto
- Asegúrate que existen bases de datos o credenciales para resetear

### Error al crear backup
- Verifica permisos de escritura en la carpeta `backups/`
- Asegúrate que hay suficiente espacio en disco

### Error en Windows con caracteres especiales
- La utilidad maneja automáticamente problemas de codificación
- Si persiste, usa `--quiet` para salida simplificada

## Archivos Relacionados

- `utils/reset_system.py` - Utilidad CLI
- `dashboard/pages/03_⚙️_System_Reset.py` - Interfaz Streamlit
- `config/settings.py` - Funciones helper para reset

## Autor

Analytics Dashboard Team

## Versión

1.0.0
