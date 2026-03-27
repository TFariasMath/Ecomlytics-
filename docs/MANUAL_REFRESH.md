# 🔄 Manual Data Refresh Feature

## Overview

The dashboard now includes a **manual data refresh button** that allows you to extract fresh data from your APIs without leaving the dashboard interface.

---

## How It Works

### Location

The refresh functionality is in the **sidebar** of the dashboard, at the bottom after the configuration section.

### Two Refresh Options

```
┌─────────────────────────────┐
│ 🔄 Actualización de Datos   │
├─────────────────────────────┤
│ ○ Solo recargar vista       │
│ ● Extraer datos nuevos      │
├─────────────────────────────┤
│  [🔄 Actualizar Datos]      │
└─────────────────────────────┘
```

#### Option 1: Solo recargar vista (Quick Refresh)
- **What it does**: Clears Streamlit cache and reloads the current view
- **When to use**: When you've made changes to filters or want to refresh visualizations
- **Time**: Instant (< 1 second)
- **Data**: Uses existing database data

#### Option 2: Extraer datos nuevos (Full ETL Refresh)
- **What it does**: Runs all configured ETL extractors to fetch new data from APIs
- **When to use**: When you want the latest data from your sources
- **Time**: 30 seconds to 5 minutes (depending on data volume)
- **Data**: Fetches fresh data from WooCommerce, Google Analytics, Facebook

---

## Step-by-Step Usage

### Quick Refresh (Default)

1. Click on **"Solo recargar vista"** radio button (selected by default)
2. Click **"🔄 Actualizar Datos"** button
3. Dashboard reloads with fresh visualizations
4. ✅ Done! (instant)

### Full Data Refresh

1. Click on **"Extraer datos nuevos"** radio button
2. Click **"🔄 Actualizar Datos"** button
3. See execution progress:

```
┌──────────────────────────────────────────┐
│ 🚀 Ejecutando extractores ETL...         │
├──────────────────────────────────────────┤
│ #### Progreso de Extracción              │
│                                          │
│ 📊 Extractores a ejecutar:               │
│    WooCommerce, Google Analytics         │
│                                          │
│ [⏳ Extrayendo datos...]                 │
└──────────────────────────────────────────┘
```

4. Wait for completion (spinner shows progress)

5. See results for each extractor:

```
┌──────────────────────────────────────────┐
│ #### Resultados                          │
│                                          │
│ ✅ Woocommerce: Completado exitosamente  │
│ ✅ Analytics: Completado exitosamente    │
│ ⚪ Facebook: Not configured               │
│                                          │
│ ✅ Todos los extractores completados     │
│                                          │
│ [🔄 Recargar Dashboard]                  │
└──────────────────────────────────────────┘
```

6. Click **"🔄 Recargar Dashboard"** to see new data
7. 🎉 Dashboard shows updated data!

---

## What Happens Behind the Scenes

### Architecture

```
User clicks button
      ↓
Dashboard (app_woo_v2.py)
      ↓
ETL Runner (utils/etl_runner.py)
      ↓
Checks configuration status
      ↓
Runs configured extractors in sequence:
  1. extract_woocommerce.py (if configured)
  2. extract_analytics.py (if configured)
  3. extract_facebook.py (if configured)
      ↓
Each extractor:
  - Reads .env credentials
  - Connects to API
  - Fetches new data (incremental)
  - Saves to SQLite database
      ↓
Results returned to dashboard
      ↓
User sees success/error messages
```

### Execution Details

**ETL Runner** (`utils/etl_runner.py`):
- Uses `subprocess` to run each extractor script
- Captures stdout and stderr for debugging
- 5-minute timeout per extractor
- Only runs configured extractors (skips unconfigured ones)
- Returns detailed results for each

**Dashboard Integration** (`dashboard/app_woo_v2.py`):
- Radio button to select refresh type
- Progress spinner during execution
- Color-coded results (✅ success, ❌ error, ⚪ skipped)
- Error details in expandable sections
- Suggestions if extraction fails

---

## Error Handling

### If an Extractor Fails

```
┌──────────────────────────────────────────┐
│ ❌ Woocommerce: Connection timeout       │
│                                          │
│ ▼ Ver detalles de error - woocommerce   │
│   Error: Failed to connect to API       │
│   Status code: 503                       │
│   Timeout after 30 seconds               │
│                                          │
│ ⚠️ Algunos extractores fallaron          │
│                                          │
│ Sugerencias:                             │
│ - Verifica tu conexión a internet        │
│ - Revisa las credenciales                │
│ - Consulta logs/etl.log                  │
└──────────────────────────────────────────┘
```

### Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| "Not configured" | Service not set up | Go to Setup page and configure credentials |
| "Connection timeout" | Network issue or API down | Check internet, try again later |
| "Authentication failed" | Invalid credentials | Update credentials in Setup page |
| "No new data" | All data already extracted | This is normal! Incremental extraction working |
| "Timeout: 5 minutes" | Very large data extraction | Run extractor manually via command line |

---

## Benefits

### Before (Manual Process)

```
1. Open terminal
2. Activate virtual environment
3. cd to project directory
4. Run: python etl/extract_woocommerce.py
5. Run: python etl/extract_analytics.py
6. Run: python etl/extract_facebook.py
7. Wait for each to complete
8. Go back to browser
9. Refresh dashboard
```

**Time**: 5-10 minutes with manual intervention

### After (One-Click Refresh)

```
1. Click "Extraer datos nuevos"
2. Click "🔄 Actualizar Datos"
3. Wait (automatic)
4. Click "🔄 Recargar Dashboard"
```

**Time**: Same data extraction time, but ZERO manual intervention!

---

## Use Cases

### Daily Morning Routine

```
9:00 AM: Arrive at office
9:01 AM: Open dashboard
9:02 AM: Click "Extraer datos nuevos" → "Actualizar"
9:05 AM: Get coffee ☕
9:07 AM: Dashboard ready with fresh data!
```

### Mid-Day Check

```
2:00 PM: Want to see latest sales
2:01 PM: Quick refresh → "Solo recargar vista"
2:02 PM: See updated visualizations (from this morning's data)
```

### After Making Big Changes

```
Boss: "We just got a huge order!"
You: Click "Extraer datos nuevos"
3 minutes later: "Here it is on the dashboard! 🎉"
```

---

## Technical Notes

### Incremental Extraction

The extractors automatically fetch **only new data** since the last run:

```python
# Inside each extractor
last_date = get_last_extraction_date('wc_orders')
# Fetches only orders after last_date
```

This means:
- ✅ Fast execution (only new data)
- ✅ No duplicate data
- ✅ Efficient API usage

### Timeout Protection

Each extractor has a 5-minute timeout:
- Prevents hanging processes
- Returns control to user
- Can be safely re-run

### Configuration-Aware

Only runs configured extractors:
```python
if config_status['woocommerce']:
    run_extractor('woocommerce')
else:
    skip_extractor('woocommerce')
```

---

## Future Enhancements

Possible improvements:

- [ ] Scheduled automatic refresh (every hour/day)
- [ ] Progress bar showing which extractor is running
- [ ] Email notification when extraction completes
- [ ] Selective extraction (choose which extractors to run)
- [ ] Show last extraction timestamp
- [ ] Estimate time remaining during extraction

---

## Troubleshooting

### "Module not found: etl_runner"

**Solution**: Make sure `utils/etl_runner.py` exists in your project

### Extractor hangs/freezes

**Solution**: 
1. Wait up to 5 minutes (timeout)
2. If persists, run extractor manually in terminal to see full error
3. Check `logs/etl.log` for details

### "No new data" message

**This is normal!** It means:
- Incremental extraction is working
- No new orders/data since last run
- Your data is up-to-date

### Still seeing old data after refresh

**Solution**:
1. Make sure extraction completed successfully (check ✅ marks)
2. Click "🔄 Recargar Dashboard" button
3. Hard refresh browser (Ctrl + F5)
4. Clear Streamlit cache: `st.cache_data.clear()`

---

## Summary

The manual refresh feature provides a **one-click solution** to update your dashboard data without leaving the interface or using the command line.

**Key Points**:
- ✅ Two refresh modes: Quick (cache) and Full (ETL)
- ✅ Runs only configured extractors automatically
- ✅ Shows detailed progress and results
- ✅ Error handling with helpful suggestions
- ✅ No technical knowledge required

**Perfect for**:
- Non-technical users
- Quick daily updates
- Demonstrating real-time data to clients
- Avoiding command line complexity

---

**Last Updated**: December 21, 2025
