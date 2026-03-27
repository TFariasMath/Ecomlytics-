# ========================================
# CÓDIGO DE INTEGRACIÓN v1.2 PARA SIDEBAR
# ========================================
#
# Copia este código en app_woo_v2.py en el sidebar,
# después de la sección de "Actualización de Datos"
# (alrededor de la línea 2786)
#
# ========================================

        st.markdown("---")
        
        # ===== v1.2 FEATURE #1: LANGUAGE SELECTOR =====
        from config.i18n import get_language_display_name, get_available_languages
        
        st.markdown("### 🌐 Idioma / Language")
        lang = st.selectbox(
            "Seleccionar idioma",
            options=get_available_languages(),
            format_func=get_language_display_name,
            key='language_selector',
            label_visibility="collapsed"
        )
        
        # Store in session state
        if 'language' not in st.session_state:
            st.session_state.language = lang
        elif st.session_state.language != lang:
            st.session_state.language = lang
            st.rerun()  # Reload to apply language
        
        st.markdown("---")
        
        # ===== v1.2 FEATURE #2: EXPORT TO PDF/EXCEL =====
        from utils.export import ReportExporter, create_summary_export
        
        st.markdown("### 📥 Exportar Reporte")
        
        export_format = st.selectbox(
            "Formato",
            ["Excel (.xlsx)", "PDF (.pdf)"],
            key='export_format',
            label_visibility="collapsed"
        )
        
        if st.button("📥 Generar Reporte", use_container_width=True):
            try:
                # Load current data
                df_orders = load_data('wc_orders', filter_valid_statuses=True)
                
                if df_orders.empty:
                    st.warning("⚠️ No hay datos para exportar")
                else:
                    with st.spinner("Generando reporte..."):
                        
                        if export_format == "Excel (.xlsx)":
                            # Prepare data for Excel export
                            data_dict = create_summary_export(
                                df_orders,
                                start_date=df_orders['date_created'].min().strftime('%Y-%m-%d'),
                                end_date=df_orders['date_created'].max().strftime('%Y-%m-%d')
                            )
                            
                            filename = ReportExporter.export_to_excel(data_dict)
                            
                            # Offer download
                            with open(filename, 'rb') as f:
                                st.download_button(
                                    label="💾 Descargar Excel",
                                    data=f,
                                    file_name=filename,
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    use_container_width=True
                                )
                        
                        elif export_format == "PDF (.pdf)":
                            # Prepare metrics for PDF
                            metrics = {
                                'Ventas Totales': f"${df_orders['total'].sum():,.0f}",
                                'Total Órdenes': f"{len(df_orders):,}",
                                'Ticket Promedio': f"${df_orders['total'].mean():,.0f}"
                            }
                            
                            # Prepare data tables (first 20 rows)
                            data_tables = {
                                'Últimas Órdenes': df_orders[['date_created', 'order_id', 'customer_name', 'total']].head(20)
                            }
                            
                            filename = ReportExporter.export_to_pdf(metrics, data_tables)
                            
                            # Offer download
                            with open(filename, 'rb') as f:
                                st.download_button(
                                    label="💾 Descargar PDF",
                                    data=f,
                                    file_name=filename,
                                    mime="application/pdf",
                                    use_container_width=True
                                )
                        
                        st.success(f"✅ Reporte generado exitosamente: {filename}")
                        
            except Exception as e:
                st.error(f"❌ Error generando reporte: {str(e)}")
        
        st.markdown("---")
        
        # ===== v1.2 FEATURE #3: PERIOD COMPARISON =====
        from utils.comparisons import get_comparison_period, calculate_comparison_metrics
        
        st.markdown("### 📈 Comparar Períodos")
        
        comparison_mode = st.selectbox(
            "Comparar con:",
            [
                "Sin comparación",
                "Período anterior (mismo tamaño)",
                "Mismo período año pasado"
            ],
            key='comparison_mode',
            label_visibility="collapsed"
        )
        
        # Store in session state for use in metrics
        if 'comparison_mode' not in st.session_state:
            st.session_state.comparison_mode = comparison_mode
        else:
            st.session_state.comparison_mode = comparison_mode
        
        if comparison_mode != "Sin comparación":
            st.info(f"ℹ️ Modo activo: {comparison_mode}")
        
        st.markdown("---")


# ========================================
# CÓMO USAR LAS COMPARACIONES EN MÉTRICAS
# ========================================
#
# En las funciones de vista (view_summary, view_sales, etc.),
# puedes usar el comparison_mode para mostrar deltas:
#

def example_usage_in_view_function(df_orders):
    """Ejemplo de cómo usar las comparaciones en las vistas"""
    import streamlit as st
    from utils.comparisons import get_comparison_period, calculate_comparison_metrics
    from datetime import datetime
    
    # Obtener modo de comparación desde session state
    comparison_mode = st.session_state.get('comparison_mode', 'Sin comparación')
    
    # Si hay comparación activa
    if comparison_mode != "Sin comparación":
        # Determinar tipo de comparación
        comp_type = 'previous' if 'anterior' in comparison_mode else 'year_ago'
        
        # Obtener rango de fechas actual (del filtro de fecha)
        start_date = datetime(2025, 12, 1)  # Ejemplo
        end_date = datetime(2025, 12, 21)   # Ejemplo
        
        # Calcular período de comparación
        comp_start, comp_end = get_comparison_period(start_date, end_date, comp_type)
        
        # Filtrar datos del período de comparación
        df_comparison = df_orders[
            (df_orders['date_created'].dt.date >= comp_start.date()) &
            (df_orders['date_created'].dt.date <= comp_end.date())
        ]
        
        # Calcular métricas
        metrics = calculate_comparison_metrics(df_orders, df_comparison, metric_column='total')
        
        # Mostrar con delta
        st.metric(
            label="Ventas Totales",
            value=f"${metrics['current_value']:,.0f}",
            delta=f"{metrics['change_percentage']:+.1f}%",
            help=f"vs {comp_start.date()} - {comp_end.date()}"
        )
    
    else:
        # Sin comparación, mostrar métrica normal
        st.metric(
            label="Ventas Totales",
            value=f"${df_orders['total'].sum():,.0f}"
        )
