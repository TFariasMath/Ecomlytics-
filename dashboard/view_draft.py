# Customer Analytics Dashboard View
# This file will be inserted into app_woo_v2.py

# === IMPORTACIONES REQUERIDAS ===
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Configuración estática para gráficos Plotly (evita completamente la distorsión)
# Nota: staticPlot=True deshabilita todas las interacciones (zoom, pan, drag, selección)
# pero mantiene la visualización de alta calidad
PLOTLY_CONFIG = {
    'displayModeBar': False, # Oculta la barra de herramientas
    'displaylogo': False,    # Oculta logo de Plotly
    'scrollZoom': False,     # Deshabilita zoom con scroll
    'doubleClick': False,    # Deshabilita doble click
    'editable': False,       # No editable
    'staticPlot': False      # Permite interacciones básicas (hovertips) pero sin zoom/pan
}

def format_empty_cells(df):
    """
    Formatea un DataFrame reemplazando valores vacíos con "Sin información".
    
    Args:
        df: DataFrame de pandas a formatear
        
    Returns:
        DataFrame con valores vacíos reemplazados
    """
    if df is None or df.empty:
        return df
    
    # Crear copia para no modificar el original
    df_formatted = df.copy()
    
    # Reemplazar valores vacíos con "Sin información"
    # Manejar None, NaN, strings vacíos, y strings con solo espacios
    for col in df_formatted.columns:
        # Para columnas de tipo object/string
        if df_formatted[col].dtype == 'object':
            df_formatted[col] = df_formatted[col].apply(
                lambda x: "Sin información" if pd.isna(x) or (isinstance(x, str) and x.strip() == '') else x
            )
    
    return df_formatted


# === DEPENDENCIAS REQUERIDAS DE app_woo_v2.py ===
# Las siguientes funciones deben estar disponibles en el ámbito global:
# - metric_card(title, value, delta=None, icon="fa-chart-line", color="#4318FF", help_text=None, bg_color=None)
# - show_time_selector() -> (start_date, end_date)
# - load_data(table_name, db_path=DATABASE_NAME, filter_valid_statuses=False) -> pd.DataFrame


def view_customer_analytics(df_orders_all):
    """Vista de Customer Analytics con RFM, CLV y Análisis de Cohortes."""
    
    # Mostrar selector de tiempo
    start_date, end_date = show_time_selector()
    
    # Filtrar datos por periodo seleccionado
    mask = (df_orders_all['date_created'] >= start_date) & (df_orders_all['date_created'] <= end_date)
    df_orders = df_orders_all.loc[mask]
    
    st.markdown("### 👥 Customer Analytics Avanzado")
    
    # Cargar datos de clientes
    try:
        df_customers = load_data('wc_customers')
    except:
        st.warning("⚠️ Tabla de clientes no disponible. Ejecuta la extracción de WooCommerce primero.")
        df_customers = pd.DataFrame()
    
    # === KPIs PRINCIPALES ===
    total_customers = len(df_customers) if not df_customers.empty else 0
    
    # Clientes registrados vs guests
    registered_customers = len(df_orders[df_orders['customer_id'] > 0]['customer_id'].unique()) if not df_orders.empty else 0
    guest_orders = len(df_orders[df_orders['customer_id'] == 0]) if not df_orders.empty else 0
    
    # CLV Promedio
    avg_clv = df_customers['total_spent'].mean() if not df_customers.empty else 0
    
    # Tasa de retención (clientes con más de 1 pedido)
    if not df_customers.empty and 'orders_count' in df_customers.columns:
        repeat_customers = len(df_customers[df_customers['orders_count'] > 1])
        retention_rate = (repeat_customers / total_customers * 100) if total_customers > 0 else 0
    else:
        retention_rate = 0
    
    # Mostrar KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("Total Clientes", f"{total_customers:,}", icon="fa-users", color="#4318FF")
    with col2:
        metric_card("CLV Promedio", f"${avg_clv:,.0f}", icon="fa-dollar-sign", color="#05CD99", help_text="Customer Lifetime Value")
    with col3:
        metric_card("Tasa de Retención", f"{retention_rate:.1f}%", icon="fa-repeat", color="#FFB547", help_text="Clientes con >1 pedido")
    with col4:
        metric_card("Pedidos Guest", f"{guest_orders}", icon="fa-user-secret", color="#EE5D50", help_text="Sin cuenta registrada")
    
    st.markdown("---")
    
    # === ANÁLISIS RFM ===
    st.markdown("#### 🎯 Segmentación RFM (Recency, Frequency, Monetary)")
    st.caption("Clasifica clientes según cuándo compraron, cuántas veces y cuánto gastaron")
    
    if not df_orders.empty and not df_customers.empty:
        # Calcular RFM para clientes registrados
        df_rfm_orders = df_orders[df_orders['customer_id'] > 0].copy()
        
        if not df_rfm_orders.empty:
            reference_date = df_orders['date_created'].max()
            
            rfm_data = df_rfm_orders.groupby('customer_id').agg({
                'date_created': lambda x: (reference_date - x.max()).days,  # Recency
                'order_id': 'count',  # Frequency
                'total': 'sum'  # Monetary
            }).reset_index()
            
            rfm_data.columns = ['customer_id', 'recency', 'frequency', 'monetary']
            
            # Scoring RFM (1-5, donde 5 es mejor)
            rfm_data['R_score'] = pd.qcut(rfm_data['recency'], q=5, labels=[5,4,3,2,1], duplicates='drop')
            rfm_data['F_score'] = pd.qcut(rfm_data['frequency'].rank(method='first'), q=5, labels=[1,2,3,4,5], duplicates='drop')
            rfm_data['M_score'] = pd.qcut(rfm_data['monetary'].rank(method='first'), q=5, labels=[1,2,3,4,5], duplicates='drop')
            
            # RFM Score combinado
            rfm_data['RFM_Score'] = rfm_data['R_score'].astype(str) + rfm_data['F_score'].astype(str) + rfm_data['M_score'].astype(str)
            rfm_data['RFM_Sum'] = rfm_data[['R_score', 'F_score', 'M_score']].astype(int).sum(axis=1)
            
            # Segmentación
            def segment_customer(row):
                if row['RFM_Sum'] >= 13:
                    return '🏆 Champions'
                elif row['RFM_Sum'] >= 11:
                    return '⭐ Loyal Customers'
                elif row['R_score'].astype(int) >= 4 and row['F_score'].astype(int) <= 2:
                    return '🌱 Potential Loyalists'
                elif row['R_score'].astype(int) <= 2:
                    return '😴 At Risk'
                elif row['R_score'].astype(int) <= 2 and row['F_score'].astype(int) >= 4:
                    return '💔 Can\'t Lose'
                else:
                    return '📊 Regular'
            
            rfm_data['segment'] = rfm_data.apply(segment_customer, axis=1)
            
            # Merge con datos de clientes para nombres
            rfm_with_names = rfm_data.merge(
                df_customers[['customer_id', 'email', 'first_name', 'last_name']], 
                on='customer_id', 
                how='left'
            )
            rfm_with_names['customer_name'] = rfm_with_names.apply(
                lambda x: f"{x['first_name']} {x['last_name']}".strip() if x['first_name'] else x['email'][:20],
                axis=1
            )
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown("##### 📊 Distribución de Segmentos")
                segment_counts = rfm_data['segment'].value_counts().reset_index()
                segment_counts.columns = ['Segmento', 'Clientes']
                
                colors_seg = {
                    '🏆 Champions': '#05CD99',
                    '⭐ Loyal Customers': '#4318FF',
                    '🌱 Potential Loyalists': '#FFB547',
                    '📊 Regular': '#6AD2FF',
                    '😴 At Risk': '#FFA500',
                    '💔 Can\'t Lose': '#EE5D50'
                }
                
                fig_seg = px.pie(
                    segment_counts,
                    values='Clientes',
                    names='Segmento',
                    hole=0.5,
                    color='Segmento',
                    color_discrete_map=colors_seg
                )
                fig_seg.update_traces(
                    textinfo='label+percent',
                    textfont=dict(size=11)
                )
                fig_seg.update_layout(
                    template='plotly_white',
                    paper_bgcolor='rgba(0,0,0,0)',
                    height=350,
                    showlegend=True,
                    legend=dict(orientation="v", y=0.5),
                    dragmode=False
                )
                st.plotly_chart(fig_seg, use_container_width=True, config=PLOTLY_CONFIG)
            
            with col2:
                st.markdown("##### 💎 Top Clientes por Segmento")
                selected_segment = st.selectbox(
                    "Selecciona un segmento",
                    options=segment_counts['Segmento'].tolist()
                )
                
                seg_customers = rfm_with_names[rfm_with_names['segment'] == selected_segment].sort_values('monetary', ascending=False).head(10)
                
                if not seg_customers.empty:
                    display_seg = seg_customers[['customer_name', 'recency', 'frequency', 'monetary']].copy()
                    display_seg['recency'] = display_seg['recency'].apply(lambda x: f"{x} días")
                    display_seg.columns = ['Cliente', 'Última Compra', 'Pedidos', 'Total Gastado']
                    
                    st.dataframe(format_empty_cells(display_seg), use_container_width=True, height=300)
                else:
                    st.info(f"No hay clientes en {selected_segment}")
        else:
            st.info("No hay suficientes datos de clientes registrados para RFM")
    else:
        st.warning("Datos insuficientes para análisis RFM")
    
    st.markdown("---")
    
    # === ANÁLISIS DE COHORTES ===
    st.markdown("#### 📅 Análisis de Cohortes")
    st.caption("Tracking de retención por mes de primera compra")
    
    if not df_orders_all.empty:
        # Preparar datos para cohortes
        df_cohort = df_orders_all[df_orders_all['customer_id'] > 0].copy()
        
        if not df_cohort.empty and len(df_cohort) > 50:
            # Obtener mes de primera compra por cliente
            df_cohort['order_month'] = df_cohort['date_created'].dt.to_period('M')
            df_cohort['cohort'] = df_cohort.groupby('customer_id')['date_created'].transform('min').dt.to_period('M')
            
            # Calcular períodos desde la primera compra
            def get_period_number(row):
                return (row['order_month'] - row['cohort']).n
            
            df_cohort['period_number'] = df_cohort.apply(get_period_number, axis=1)
            
            # Crear tabla de cohortes
            cohort_data = df_cohort.groupby(['cohort', 'period_number'])['customer_id'].nunique().reset_index()
            cohort_pivot = cohort_data.pivot(index='cohort', columns='period_number', values='customer_id')
            
            # Calcular porcentaje de retención
            cohort_size = cohort_pivot.iloc[:, 0]
            retention = cohort_pivot.divide(cohort_size, axis=0) * 100
            
            # Mostrar solo últimos 12 meses de cohortes
            retention_recent = retention.tail(12)
            
            if not retention_recent.empty:
                # Heatmap de retención
                fig_cohort = go.Figure(data=go.Heatmap(
                    z=retention_recent.values,
                    x=[f"Mes {int(i)}" for i in retention_recent.columns],
                    y=[str(idx) for idx in retention_recent.index],
                    colorscale='Viridis',
                    text=retention_recent.values.round(1),
                    texttemplate='%{text}%',
                    textfont={"size": 10},
                    colorbar=dict(title="Retención %")
                ))
                
                fig_cohort.update_layout(
                    template='plotly_white',
                    paper_bgcolor='rgba(0,0,0,0)',
                    height=400,
                    xaxis=dict(title='Meses desde Primera Compra'),
                    yaxis=dict(title='Cohorte (Mes de Primera Compra)'),
                    dragmode=False
                )
                st.plotly_chart(fig_cohort, use_container_width=True, config=PLOTLY_CONFIG)
                
                st.caption("💡 **Lectura**: Cada fila es un grupo de clientes por mes de primera compra. Las columnas muestran el % que volvió a comprar en cada mes subsecuente.")
            else:
                st.info("No hay suficiente historial para análisis de cohortes")
        else:
            st.info("Se necesitan más datos históricos (>50 órdenes de clientes registrados)")
    
    st.markdown("---")
    
    # === CUSTOMER LIFETIME VALUE ===
    st.markdown("#### 💰 Customer Lifetime Value (CLV)")
    
    if not df_customers.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 📊 Distribución de CLV")
            
            # Crear bins para CLV
            clv_bins = [0, 10000, 50000, 100000, 250000, float('inf')]
            clv_labels = ['$0-10k', '$10k-50k', '$50k-100k', '$100k-250k', '$250k+']
            
            df_customers['clv_category'] = pd.cut(
                df_customers['total_spent'], 
                bins=clv_bins, 
                labels=clv_labels,
                right=False
            )
            
            clv_dist = df_customers['clv_category'].value_counts().sort_index()
            
            fig_clv = px.bar(
                x=clv_dist.index,
                y=clv_dist.values,
                labels={'x': 'Rango CLV', 'y': 'Cantidad de Clientes'},
                text=clv_dist.values
            )
            fig_clv.update_traces(marker_color='#4318FF', textposition='outside')
            fig_clv.update_layout(
                template='plotly_white',
                paper_bgcolor='rgba(0,0,0,0)',
                height=300,
                showlegend=False,
                dragmode=False
            )
            st.plotly_chart(fig_clv, use_container_width=True, config=PLOTLY_CONFIG)
        
        with col2:
            st.markdown("##### 🏆 Top 10 Clientes por CLV")
            
            top_clv = df_customers.nlargest(10, 'total_spent')[['first_name', 'last_name', 'email', 'total_spent', 'orders_count']].copy()
            top_clv['name'] = top_clv.apply(
                lambda x: f"{x['first_name']} {x['last_name']}".strip() if x['first_name'] else x['email'][:20],
                axis=1
            )
            
            display_clv = top_clv[['name', 'total_spent', 'orders_count']].copy()
            display_clv.columns = ['Cliente', 'Total Gastado', 'Pedidos']
            
            st.dataframe(format_empty_cells(display_clv), use_container_width=True, height=350)
    else:
        st.info("Datos de clientes no disponibles")


def view_logistics(df_orders_all):
    """Vista de Logística y Operaciones."""
    # Mostrar selector de tiempo
    start_date, end_date = show_time_selector()
    
    # Filtrar datos por periodo seleccionado
    mask = (df_orders_all['date_created'] >= start_date) & (df_orders_all['date_created'] <= end_date)
    df_orders = df_orders_all.loc[mask]
    
    st.markdown("### 📦 Logística y Operaciones")
    
    if df_orders.empty:
        st.warning("No hay datos de órdenes para el periodo seleccionado")
        return
    
    # === KPIs PRINCIPALES ===
    # Calcular tiempo promedio de procesamiento
    if 'date_paid' in df_orders.columns and 'date_completed' in df_orders.columns:
        df_orders['date_paid_dt'] = pd.to_datetime(df_orders['date_paid'], errors='coerce')
        df_orders['date_completed_dt'] = pd.to_datetime(df_orders['date_completed'], errors='coerce')
        df_orders['processing_time'] = (df_orders['date_completed_dt'] - df_orders['date_paid_dt']).dt.total_seconds() / 3600  # horas
        
        avg_processing = df_orders['processing_time'].mean()
        avg_processing_days = avg_processing / 24 if pd.notna(avg_processing) else 0
    else:
        avg_processing_days = 0
    
    # Método de pago más usado
    top_payment = df_orders['payment_method_title'].mode()[0] if 'payment_method_title' in df_orders.columns and not df_orders.empty else "N/A"
    
    # Método de envío más usado
    top_shipping = df_orders['shipping_method'].mode()[0] if 'shipping_method' in df_orders.columns and not df_orders.empty else "N/A"
    
    # Total costos de envío
    total_shipping_cost = df_orders['shipping_total'].sum() if 'shipping_total' in df_orders.columns else 0
    
    # Mostrar KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("Tiempo Procesamiento", f"{avg_processing_days:.1f} días", icon="fa-clock", color="#4318FF", help_text="Promedio desde pago a completado")
    with col2:
        metric_card("Pago Principal", top_payment[:20], icon="fa-credit-card", color="#05CD99")
    with col3:
        metric_card("Envío Principal", top_shipping[:20], icon="fa-truck", color="#FFB547")
    with col4:
        metric_card("Costo Total Envío", f"${total_shipping_cost:,.0f}", icon="fa-dollar-sign", color="#EE5D50")
    
    st.markdown("---")
    
    # === ANÁLISIS DE MÉTODOS DE PAGO ===
    st.markdown("#### 💳 Análisis de Métodos de Pago")
    
    if 'payment_method_title' in df_orders.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 📊 Distribución por Método")
            payment_dist = df_orders.groupby('payment_method_title').agg(
                Pedidos=('order_id', 'count'),
                Ingresos=('total', 'sum')
            ).reset_index().sort_values('Pedidos', ascending=False)
            
            fig_pay = px.pie(
                payment_dist,
                values='Pedidos',
                names='payment_method_title',
                hole=0.5
            )
            fig_pay.update_layout(
                template='plotly_white',
                paper_bgcolor='rgba(0,0,0,0)',
                height=300,
                dragmode=False
            )
            st.plotly_chart(fig_pay, use_container_width=True, config=PLOTLY_CONFIG)
        
        with col2:
            st.markdown("##### 💰 Ingresos por Método")
            fig_pay_rev = px.bar(
                payment_dist.sort_values('Ingresos', ascending=True),
                x='Ingresos',
                y='payment_method_title',
                orientation='h',
                text='Ingresos'
            )
            fig_pay_rev.update_traces(marker_color='#4318FF', texttemplate='$%{text:,.0f}', textposition='outside')
            fig_pay_rev.update_layout(
                template='plotly_white',
                paper_bgcolor='rgba(0,0,0,0)',
                height=300,
                yaxis=dict(title=''),
                dragmode=False
            )
            st.plotly_chart(fig_pay_rev, use_container_width=True, config=PLOTLY_CONFIG)
    
    st.markdown("---")
    
    # === ANÁLISIS DE MÉTODOS DE ENVÍO ===
    st.markdown("#### 🚚 Análisis de Métodos de Envío")
    
    if 'shipping_method' in df_orders.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 📦 Pedidos por Método")
            shipping_dist = df_orders.groupby('shipping_method').agg(
                Pedidos=('order_id', 'count'),
                Costo_Promedio=('shipping_total', 'mean')
            ).reset_index().sort_values('Pedidos', ascending=False)
            
            fig_ship = px.bar(
                shipping_dist.head(10).sort_values('Pedidos', ascending=True),
                x='Pedidos',
                y='shipping_method',
                orientation='h',
                text='Pedidos'
            )
            fig_ship.update_traces(marker_color='#FFB547', textposition='outside')
            fig_ship.update_layout(
                template='plotly_white',
                paper_bgcolor='rgba(0,0,0,0)',
                height=300,
                yaxis=dict(title=''),
                dragmode=False
            )
            st.plotly_chart(fig_ship, use_container_width=True, config=PLOTLY_CONFIG)
        
        with col2:
            st.markdown("##### 💵 Costo Promedio por Método")
            fig_ship_cost = px.bar(
                shipping_dist.head(10).sort_values('Costo_Promedio', ascending=True),
                x='Costo_Promedio',
                y='shipping_method',
                orientation='h',
                text='Costo_Promedio'
            )
            fig_ship_cost.update_traces(marker_color='#05CD99', texttemplate='$%{text:,.0f}', textposition='outside')
            fig_ship_cost.update_layout(
                template='plotly_white',
                paper_bgcolor='rgba(0,0,0,0)',
                height=300,
                yaxis=dict(title=''),
                dragmode=False
            )
            st.plotly_chart(fig_ship_cost, use_container_width=True, config=PLOTLY_CONFIG)
    
    st.markdown("---")
    
    # === TIEMPOS DE PROCESAMIENTO ===
    st.markdown("#### ⏱️ Tiempos de Procesamiento")
    
    if 'processing_time' in df_orders.columns:
        df_proc = df_orders[df_orders['processing_time'].notna()].copy()
        
        if not df_proc.empty:
            df_proc['processing_days'] = df_proc['processing_time'] / 24
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("##### 📊 Distribución de Tiempos")
                fig_proc = px.histogram(
                    df_proc,
                    x='processing_days',
                    nbins=30,
                    labels={'processing_days': 'Días de Procesamiento'}
                )
                fig_proc.update_traces(marker_color='#4318FF')
                fig_proc.update_layout(
                    template='plotly_white',
                    paper_bgcolor='rgba(0,0,0,0)',
                    height=300,
                    dragmode=False
                )
                st.plotly_chart(fig_proc, use_container_width=True, config=PLOTLY_CONFIG)
            
            with col2:
                st.markdown("##### 📈 Tendencia Mensual")
                df_proc['month'] = df_proc['date_created'].dt.to_period('M').astype(str)
                monthly_proc = df_proc.groupby('month')['processing_days'].mean().reset_index()
                
                fig_trend = px.line(
                    monthly_proc,
                    x='month',
                    y='processing_days',
                    markers=True
                )
                fig_trend.update_traces(line_color='#FFB547', line_width=3)
                fig_trend.update_layout(
                    template='plotly_white',
                    paper_bgcolor='rgba(0,0,0,0)',
                    height=300,
                    yaxis=dict(title='Días Promedio'),
                    dragmode=False
                )
                st.plotly_chart(fig_trend, use_container_width=True, config=PLOTLY_CONFIG)
        else:
            st.info("No hay datos suficientes de tiempos de procesamiento")
    
    st.markdown("---")
    
    # === ANÁLISIS DE PESO/DIMENSIONES ===
    st.markdown("#### 📏 Análisis de Peso y Dimensiones")
    st.caption("Basado en información de productos vendidos")
    
    try:
        df_products = load_data('wc_products')
        df_items = load_data('wc_order_items')
        
        if not df_products.empty and not df_items.empty and 'weight' in df_products.columns:
            # Join items con products
            df_items_weight = df_items.merge(
                df_products[['product_id', 'weight', 'length', 'width', 'height']],
                on='product_id',
                how='left'
            )
            
            # Filtrar por periodo
            df_items_period = df_items_weight[df_items_weight['order_id'].isin(df_orders['order_id'].unique())]
            
            if not df_items_period.empty:
                # Peso total enviado
                df_items_period['weight_num'] = pd.to_numeric(df_items_period['weight'], errors='coerce')
                total_weight = (df_items_period['weight_num'] * df_items_period['quantity']).sum()
                
                # Productos más pesados
                heavy_products = df_items_period.groupby('product_name').agg(
                    peso_unitario=('weight_num', 'first'),
                    cantidad_vendida=('quantity', 'sum')
                ).reset_index()
                heavy_products['peso_total'] = heavy_products['peso_unitario'] * heavy_products['cantidad_vendida']
                heavy_products = heavy_products.sort_values('peso_total', ascending=False).head(10)
                
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    metric_card("Peso Total Enviado", f"{total_weight:,.1f} kg", icon="fa-weight-hanging", color="#4318FF")
                    
                    avg_weight = df_items_period['weight_num'].mean()
                    metric_card("Peso Promedio/Producto", f"{avg_weight:,.2f} kg", icon="fa-balance-scale", color="#05CD99")
                
                with col2:
                    st.markdown("##### 🏋️ Top 10 Productos Más Pesados")
                    display_weight = heavy_products[['product_name', 'peso_unitario', 'cantidad_vendida', 'peso_total']].copy()
                    display_weight.columns = ['Producto', 'Peso Unit (kg)', 'Cant. Vendida', 'Peso Total (kg)']
                    st.dataframe(format_empty_cells(display_weight), use_container_width=True, height=300)
            else:
                st.info("No hay datos de peso para el periodo seleccionado")
        else:
            st.info("Datos de dimensiones/peso no disponibles. Re-ejecuta el ETL.")
    except:
        st.info("Datos de productos no disponibles")
