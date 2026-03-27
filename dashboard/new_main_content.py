# Configuración optimizada para gráficos Plotly
# Permite hover tooltips pero deshabilita zoom/pan/drag que distorsionan
PLOTLY_CONFIG = {
    'displayModeBar': False,  # Oculta la barra de herramientas
    'displaylogo': False,     # Oculta logo de Plotly
    'scrollZoom': False,      # Deshabilita zoom con scroll
    'doubleClick': False,     # Deshabilita doble click
    'editable': False,        # No editable
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

def main():
    st.markdown("<h1><i class='fa-solid fa-rocket' style='color:#00f2ff'></i> Dashboard v2 <span style='font-size:0.7em; opacity:0.8'>Analytics Pipeline (Mobile-Responsive)</span></h1>", unsafe_allow_html=True)
    st.markdown("### <i class='fa-solid fa-mobile-screen-button' style='color:#ff00ff'></i> Centro de Control Optimizado", unsafe_allow_html=True)

    # 1. LOAD DATA
    # Load Data - WITH STATUS FILTER FOR WC_ORDERS
    df_orders = load_data('wc_orders', filter_valid_statuses=True)
    df_items = load_data('wc_order_items')
    
    # Load GA Data
    df_ga_ecommerce = load_data('ga4_ecommerce', DATABASE_ANALYTICS)
    df_ga_traffic = load_data('ga4_traffic_sources', DATABASE_ANALYTICS)
    
    # Load Facebook Data
    df_facebook = load_data('fb_page_insights', DATABASE_FACEBOOK)

    if df_orders.empty:
        st.error("❌ No se encontraron datos de WooCommerce. Ejecuta primero el script de extracción ETL.")
        st.info("💡 **Sugerencia**: Ejecuta `python etl/extract_woocommerce.py` para cargar los datos.")
        return

    # Process Dates
    df_orders['date_created'] = pd.to_datetime(df_orders['date_created'])
    df_orders['date_only'] = df_orders['date_created'].dt.date
    
    if not df_ga_ecommerce.empty:
        # Fix: Convert to string first to handle integer YYYYMMDD format
        df_ga_ecommerce['Fecha'] = pd.to_datetime(df_ga_ecommerce['Fecha'].astype(str), format='%Y%m%d', errors='coerce')
        df_ga_ecommerce['date_only'] = df_ga_ecommerce['Fecha'].dt.date
        
    if not df_ga_traffic.empty:
        # Fix: Convert to string first to handle integer YYYYMMDD format
        df_ga_traffic['Fecha'] = pd.to_datetime(df_ga_traffic['Fecha'].astype(str), format='%Y%m%d', errors='coerce')
        
    if not df_facebook.empty:
        df_facebook['date'] = pd.to_datetime(df_facebook['date'])

    # 2. CONFIGURATION & FILTERS (Moved from Sidebar)
    with st.expander("⚙️ Configuración y Filtros", expanded=True):
        col_filters1, col_filters2 = st.columns([1, 2])
        
        with col_filters1:
            # Botón de actualización
            if st.button("🔄 Actualizar Datos", use_container_width=True):
                st.cache_data.clear()
                st.rerun()
        
        with col_filters2:
            st.markdown("### 📅 Periodo de Análisis")
            today = datetime.now()
            
            # Selector de granularidad mejorado
            period_option = st.selectbox(
                "Selecciona período",
                [
                    "📆 Últimos 7 días",
                    "📆 Últimos 30 días",
                    "📆 Últimos 90 días",
                    "📆 Este año",
                    "📆 Año pasado",
                    "🗓️ Personalizado"
                ],
                index=1,  # Por defecto: Últimos 30 días
                label_visibility="collapsed"
            )
            
            # Calcular fechas según la selección
            if period_option == "📆 Últimos 7 días":
                default_start = today - pd.Timedelta(days=7)
                default_end = today
                show_custom = False
            elif period_option == "📆 Últimos 30 días":
                default_start = today - pd.Timedelta(days=30)
                default_end = today
                show_custom = False
            elif period_option == "📆 Últimos 90 días":
                default_start = today - pd.Timedelta(days=90)
                default_end = today
                show_custom = False
            elif period_option == "📆 Este año":
                default_start = datetime(today.year, 1, 1)
                default_end = today
                show_custom = False
            elif period_option == "📆 Año pasado":
                default_start = datetime(today.year - 1, 1, 1)
                default_end = datetime(today.year - 1, 12, 31)
                show_custom = False
            else:  # Personalizado
                default_start = today - pd.Timedelta(days=30)
                default_end = today
                show_custom = True
            
            # Mostrar selector de rango solo si es personalizado
            if show_custom:
                # Configurar formato chileno (día/mes/año)
                date_range = st.date_input(
                    "Selecciona rango personalizado",
                    value=(default_start, default_end),
                    max_value=today,
                    format="DD/MM/YYYY"  # Formato chileno
                )
                
                if len(date_range) == 2:
                    start_date, end_date = date_range
                else:
                    start_date = default_start
                    end_date = default_end
            else:
                start_date = default_start
                end_date = default_end
            
            # Normalizar a inicio y fin del día para consistencia
            start_date = pd.to_datetime(start_date).normalize()  # 00:00:00
            end_date = pd.to_datetime(end_date).normalize() + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)  # 23:59:59
            
            # Mostrar período seleccionado en formato chileno
            st.info(
                f"📊 **Analizando:** {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}"
            )

    # 3. SET FIXED VARIABLES (Removed Interactive Widgets)
    comparison_option = "Periodo anterior (mismo rango)"
    product_filter = "Todos los productos"

    # Filter Data (Current Period)
    mask = (df_orders['date_created'] >= start_date) & (df_orders['date_created'] <= end_date)
    df_orders_filtered = df_orders.loc[mask]
    
    # Filter items
    valid_order_ids = df_orders_filtered['order_id'].unique()
    df_items_filtered = df_items[df_items['order_id'].isin(valid_order_ids)]
    
    # Filter GA Data (Current Period)
    df_ga_filtered = pd.DataFrame()
    if not df_ga_ecommerce.empty:
        mask_ga = (df_ga_ecommerce['Fecha'] >= start_date) & (df_ga_ecommerce['Fecha'] <= end_date)
        df_ga_filtered = df_ga_ecommerce.loc[mask_ga]
        
    # Previous Period Logic (for Deltas)
    duration = end_date - start_date
    
    if comparison_option == "Periodo anterior (mismo rango)":
        prev_end = start_date - pd.Timedelta(seconds=1)
        prev_start = prev_end - duration
    elif comparison_option == "Mes anterior":
        prev_start = start_date - pd.Timedelta(days=30)
        prev_end = end_date - pd.Timedelta(days=30)
    else:  # Mismo periodo año pasado
        prev_start = start_date - pd.Timedelta(days=365)
        prev_end = end_date - pd.Timedelta(days=365)
    
    mask_prev = (df_orders['date_created'] >= prev_start) & (df_orders['date_created'] <= prev_end)
    df_orders_prev = df_orders.loc[mask_prev]
    
    # Previous GA data
    df_ga_prev = pd.DataFrame()
    if not df_ga_ecommerce.empty:
        mask_ga_prev = (df_ga_ecommerce['Fecha'] >= prev_start) & (df_ga_ecommerce['Fecha'] <= prev_end)
        df_ga_prev = df_ga_ecommerce.loc[mask_ga_prev]

    # 4. TABS LAYOUT
    st.markdown("---")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Resumen", "💰 Ventas", "📦 Productos", "👥 Clientes", "🌐 Tráfico y Redes"])

    # DATA PREPARATION (Shared for Charts)
    combined_df = pd.DataFrame()
    daily_sales = pd.DataFrame()
    daily_ga = pd.DataFrame()

    if not df_orders_filtered.empty:
        daily_sales = df_orders_filtered.groupby('date_only').agg(
            Ventas=('total', 'sum'),
            Ordenes=('order_id', 'count')
        ).reset_index()
        daily_sales['date_only'] = pd.to_datetime(daily_sales['date_only'])
        
    if not df_ga_filtered.empty:
        daily_ga = df_ga_filtered.groupby('date_only').agg(
            Visitas=('UsuariosActivos', 'sum')
        ).reset_index()
        daily_ga['date_only'] = pd.to_datetime(daily_ga['date_only'])

    if not daily_sales.empty and not daily_ga.empty:
        combined_df = pd.merge(daily_sales, daily_ga, on='date_only', how='outer').fillna(0)
    elif not daily_sales.empty:
        combined_df = daily_sales.copy()
        combined_df['Visitas'] = 0
    elif not daily_ga.empty:
        combined_df = daily_ga.copy()
        combined_df['Ventas'] = 0
        combined_df['Ordenes'] = 0

    if not combined_df.empty:
        combined_df = combined_df.sort_values('date_only')

    # ================= TAB 1: RESUMEN =================
    with tab1:
        st.markdown("### 📝 Resumen del Periodo")
        
        insights = generate_insights(
            df_orders_filtered, 
            df_orders_prev, 
            df_items_filtered, 
            df_ga_filtered, 
            df_ga_prev, 
            df_ga_traffic
        )
        display_insights_panel(insights)
        
        st.markdown("---")

        total_sales = df_orders_filtered['total'].sum()
        total_orders = len(df_orders_filtered)
        avg_order_value = total_sales / total_orders if total_orders > 0 else 0
        
        prev_sales = df_orders_prev['total'].sum()
        prev_orders = len(df_orders_prev)
        
        delta_sales = ((total_sales - prev_sales) / prev_sales * 100) if prev_sales > 0 else 0
        delta_orders = ((total_orders - prev_orders) / prev_orders * 100) if prev_orders > 0 else 0
        
        total_visits = df_ga_filtered['UsuariosActivos'].sum() if not df_ga_filtered.empty else 0
        conv_rate = (total_orders / total_visits * 100) if total_visits > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            metric_card("Ingresos Totales", f"${total_sales:,.0f}", delta=f"{delta_sales:.1f}%", icon="fa-money-bill-wave", color="#00f2ff", help_text="Ingresos netos tras descuentos")
        with col2:
            metric_card("Pedidos", f"{total_orders}", delta=f"{delta_orders:.1f}%", icon="fa-cart-shopping", color="#ff00ff", help_text="Órdenes procesadas")
        with col3:
            metric_card("Ticket Promedio", f"${avg_order_value:,.0f}", icon="fa-receipt", color="#39ff14", help_text="Gasto promedio por cliente")
        with col4:
            metric_card("Conversión", f"{conv_rate:.2f}%", icon="fa-percent", color="#ffaa00", help_text="Visitantes que compran")

        st.markdown("---")

        status = create_business_status(df_orders_filtered, df_orders_prev, df_ga_filtered, df_items_filtered, df_ga_traffic)
        display_business_status(status)

    # ================= TAB 2: VENTAS =================
    with tab2:
        st.markdown("### 📈 Análisis Detallado de Ventas")
        
        if not combined_df.empty:
            st.markdown("#### Ventas Diarias")
            fig_sales = go.Figure()
            fig_sales.add_trace(go.Bar(
                x=combined_df['date_only'],
                y=combined_df['Ventas'],
                name='Ventas Reales',
                marker_color='#ff00ff',
                hovertemplate='%{x|%d %b}: <b>$%{y:,.0f}</b><extra></extra>'
            ))
            fig_sales.update_layout(
                template='plotly_white',  # Template claro para mejor visibilidad
                paper_bgcolor='rgba(255,255,255,0.95)',
                plot_bgcolor='rgba(255,255,255,0.95)',
                height=320,  # Más alto para dar espacio
                margin=dict(l=40, r=40, t=20, b=70),  # Margen inferior muy grande
                dragmode=False, # Deshabilita zoom/pan
                xaxis=dict(
                    showgrid=False, 
                    tickformat='%d %b',
                    tickfont=dict(size=13, color='#000000', family='Arial'),
                    tickangle=-45,
                    showticklabels=True,
                    tickmode='auto',
                    nticks=15
                ),
                yaxis=dict(
                    showgrid=True, 
                    gridcolor='rgba(0,0,0,0.1)', 
                    tickprefix='$', 
                    title='', 
                    tickfont=dict(size=11, color='#000000')
                ),
                legend=dict(
                    orientation="h", 
                    y=1.05, 
                    x=0.5, 
                    xanchor="center", 
                    font=dict(size=11, color='#000000')
                )
            )
            st.plotly_chart(fig_sales, use_container_width=True, config=PLOTLY_CONFIG)
        else:
             st.info("Sin datos de ventas diarias para graficar.")

        st.markdown("#### 📦 Pedidos Diarios vs Año Anterior")
        current_year = datetime.now().year
        last_year = current_year - 1
        
        df_orders_curr_year = df_orders[df_orders['date_created'].dt.year == current_year].copy()
        df_orders_last_year = df_orders[df_orders['date_created'].dt.year == last_year].copy()
        
        if not df_orders_curr_year.empty or not df_orders_last_year.empty:
            df_orders_curr_year['month_day'] = df_orders_curr_year['date_created'].dt.strftime('%m-%d')
            df_orders_curr_year['date_display'] = df_orders_curr_year['date_created'].dt.date
            df_orders_last_year['month_day'] = df_orders_last_year['date_created'].dt.strftime('%m-%d')
            
            daily_orders_curr = df_orders_curr_year.groupby('month_day').agg(Pedidos=('order_id', 'count'), Fecha=('date_display', 'first')).reset_index().sort_values('month_day')
            daily_orders_last = df_orders_last_year.groupby('month_day').agg(Pedidos=('order_id', 'count')).reset_index().sort_values('month_day')
            
            merged_orders = pd.merge(daily_orders_curr[['month_day', 'Pedidos', 'Fecha']], daily_orders_last[['month_day', 'Pedidos']], on='month_day', how='outer', suffixes=('_curr', '_last')).fillna(0).sort_values('month_day')
            
            fig_orders_yoy = go.Figure()
            fig_orders_yoy.add_trace(go.Scatter(
                x=merged_orders['Fecha'], 
                y=merged_orders['Pedidos_last'], 
                name=f'{last_year}', 
                mode='lines', 
                line=dict(width=3, color='#A0AEC0', dash='dot'),  # Línea más gruesa y visible
                hovertemplate=f'%{{x|%d %b}} {last_year}: <b>%{{y}}</b> pedidos<extra></extra>'
            ))
            fig_orders_yoy.add_trace(go.Scatter(
                x=merged_orders['Fecha'], 
                y=merged_orders['Pedidos_curr'], 
                name=f'{current_year}', 
                mode='lines', 
                line=dict(width=3, color='#ff00ff'), 
                fill='tozeroy', 
                fillcolor='rgba(255, 0, 255, 0.1)', 
                hovertemplate=f'%{{x|%d %b}} {current_year}: <b>%{{y}}</b> pedidos<extra></extra>'
            ))
            
            fig_orders_yoy.update_layout(
                template='plotly_dark', 
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)', 
                height=280, 
                margin=dict(l=10, r=10, t=10, b=40),  # Más margen abajo para fechas
                dragmode=False, # Deshabilita zoom/pan
                xaxis=dict(
                    showgrid=False, 
                    tickformat='%d %b',
                    tickfont=dict(size=11, color='#000000'),  # Texto negro visible
                    tickangle=-45,  # Ángulo para mejor legibilidad
                    showticklabels=True
                ), 
                yaxis=dict(
                    showgrid=True, 
                    gridcolor='rgba(255,255,255,0.05)', 
                    title='', 
                    tickfont=dict(size=11, color='#000000')
                ), 
                legend=dict(
                    orientation="h", 
                    y=1.1, 
                    x=0.5, 
                    xanchor="center", 
                    font=dict(size=11, color='#000000')
                ),
                hovermode='x unified'  # Hover unificado para ver ambas líneas
            )
            st.plotly_chart(fig_orders_yoy, use_container_width=True, config=PLOTLY_CONFIG)
        else:
            st.info("No hay datos suficientes para la comparación de pedidos.")

        st.markdown("---")
        st.markdown("#### 📅 Ventas Mensuales - Comparativa Anual")
        st.caption("Compara las ventas totales de cada mes con el año anterior")
        
        month_names = {1:'Enero', 2:'Febrero', 3:'Marzo', 4:'Abril', 5:'Mayo', 6:'Junio', 7:'Julio', 8:'Agosto', 9:'Septiembre', 10:'Octubre', 11:'Noviembre', 12:'Diciembre'}
        df_orders['year'] = df_orders['date_created'].dt.year
        df_orders['month'] = df_orders['date_created'].dt.month
        monthly_data = df_orders[df_orders['year'].isin([current_year, last_year])].groupby(['year', 'month'])['total'].sum().reset_index()
        monthly_pivot = monthly_data.pivot(index='month', columns='year', values='total').fillna(0)
        
        months_to_show = list(range(1, 13))
        for row_start in range(0, 12, 4):
            cols = st.columns(4)
            for i, month_num in enumerate(months_to_show[row_start:row_start+4]):
                with cols[i]:
                    month_name = month_names[month_num]
                    current_val = monthly_pivot.loc[month_num, current_year] if month_num in monthly_pivot.index and current_year in monthly_pivot.columns else 0
                    last_val = monthly_pivot.loc[month_num, last_year] if month_num in monthly_pivot.index and last_year in monthly_pivot.columns else 0
                    
                    delta_str = f"{((current_val - last_val) / last_val) * 100:+.1f}%" if last_val > 0 else None
                    metric_card(title=f"{month_name}", value=f"${current_val:,.0f}", delta=delta_str, icon="fa-calendar-days", color="#00f2ff", help_text=f"vs {last_year}: ${last_val:,.0f}")

        st.markdown("---")
        st.markdown("### 🔍 Verificación de Ventas por Día")
        st.caption("Verifica las ventas de un día específico comparando con WooCommerce")
        
        verification_date = st.date_input("📅 Selecciona fecha a verificar", value=datetime.now(), max_value=datetime.now(), key="verification_date", format="DD/MM/YYYY")
        verification_date_start = pd.to_datetime(verification_date).normalize()
        verification_date_end = verification_date_start + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        
        mask_verification = (df_orders['date_created'] >= verification_date_start) & (df_orders['date_created'] <= verification_date_end)
        df_verification = df_orders.loc[mask_verification]
        
        if not df_verification.empty:
            total_sales_day = df_verification['total'].sum()
            total_orders_day = len(df_verification)
            avg_ticket_day = total_sales_day / total_orders_day if total_orders_day > 0 else 0
            
            vcol1, vcol2, vcol3 = st.columns(3)
            with vcol1: metric_card("Ventas del Día", f"${total_sales_day:,.0f}", icon="fa-money-bill-wave", color="#00ff00", help_text=f"Total: {verification_date.strftime('%d/%m/%Y')}")
            with vcol2: metric_card("Pedidos", f"{total_orders_day}", icon="fa-shopping-cart", color="#00f2ff", help_text="Número de pedidos")
            with vcol3: metric_card("Ticket Promedio", f"${avg_ticket_day:,.0f}", icon="fa-receipt", color="#ff00ff", help_text="Valor promedio")
            
            st.markdown("#### 📋 Desglose de Pedidos")
            verification_table = df_verification[['order_id', 'date_created', 'status', 'total']].copy()
            verification_table['date_created'] = verification_table['date_created'].dt.strftime('%d/%m/%Y %H:%M')
            verification_table = verification_table.rename(columns={'order_id': 'ID Pedido', 'date_created': 'Fecha y Hora', 'status': 'Estado', 'total': 'Total'})
            verification_table['Total'] = verification_table['Total'].apply(lambda x: f"${x:,.0f}")
            st.dataframe(format_empty_cells(verification_table.sort_values('Fecha y Hora', ascending=False)), use_container_width=True, hide_index=True)
            st.success(f"✅ **Total: ${total_sales_day:,.0f}**")
        else:
            st.warning(f"⚠️ No hay ventas para {verification_date.strftime('%d/%m/%Y')}")

    # ================= TAB 3: PRODUCTOS =================
    with tab3:
        st.markdown("### 📊 Rendimiento del Inventario")
        if not df_items_filtered.empty:
            prod_perf = df_items_filtered.groupby('product_name').agg(Unidades=('quantity', 'sum'), Ingresos=('total', 'sum')).reset_index()
            prod_perf = add_product_badges(prod_perf)
            
            col_prod1, col_prod2 = st.columns(2)
            with col_prod1:
                st.markdown("#### Más Vendidos (Ingresos)")
                st.caption("🏆 = Producto estrella del periodo")
                top_rev = prod_perf.sort_values('Ingresos', ascending=False).head(8).sort_values('Ingresos', ascending=True)
                fig_rev = px.bar(top_rev, x='Ingresos', y='product_display', orientation='h', text='Ingresos')
                fig_rev.update_traces(marker_color='#3b82f6', texttemplate='$%{text:,.0f}', textposition='outside', cliponaxis=False)
                fig_rev.update_layout(yaxis=dict(title='', tickfont=dict(family='Arial Black', size=11, color='#000000')), xaxis=dict(title='', showgrid=False, showticklabels=False), template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=150, t=0, b=0), height=330, uniformtext_minsize=9, uniformtext_mode='hide', dragmode=False)
                st.plotly_chart(fig_rev, use_container_width=True, config=PLOTLY_CONFIG)
            with col_prod2:
                st.markdown("#### Menos Vendidos (Unidades)")
                st.caption("⚠️ = Sin ventas  |  📦 = Pocas ventas (≤3)")
                bottom_units = prod_perf.sort_values('Unidades', ascending=True).head(8).sort_values('Unidades', ascending=True)
                fig_worst = px.bar(bottom_units, x='Unidades', y='product_display', orientation='h', text='Unidades')
                fig_worst.update_traces(marker_color='#ef4444', texttemplate='%{text} un.', textposition='outside', cliponaxis=False)
                fig_worst.update_layout(yaxis=dict(title='', tickfont=dict(family='Arial Black', size=11, color='#000000')), xaxis=dict(title='', showgrid=False, showticklabels=False), template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=150, t=0, b=0), height=330, uniformtext_minsize=9, uniformtext_mode='hide')
                st.plotly_chart(fig_worst, use_container_width=True, config=PLOTLY_CONFIG)
        else:
            st.info("No hay datos de productos.")

    # ================= TAB 4: CLIENTES =================
    with tab4:
        st.markdown("### 👥 Análisis de Clientes")
        has_customer_data = 'customer_id' in df_orders.columns
        if has_customer_data and not df_orders.empty:
            df_registered = df_orders[df_orders['customer_id'] > 0].copy()
            if not df_registered.empty:
                col_cust1, col_cust2 = st.columns(2)
                with col_cust1:
                    st.markdown("#### 🏆 Top Clientes Históricos")
                    customer_stats = df_registered.groupby(['customer_id', 'customer_name', 'customer_email']).agg(Total_Gastado=('total', 'sum'), Num_Pedidos=('order_id', 'count'), Primera_Compra=('date_created', 'min'), Ultima_Compra=('date_created', 'max')).reset_index()
                    top_customers = customer_stats.sort_values('Total_Gastado', ascending=False).head(10)
                    top_customers['Ranking'] = range(1, len(top_customers) + 1)
                    top_customers['Cliente'] = top_customers.apply(lambda x: f"{'🥇' if x['Ranking']==1 else '🥈' if x['Ranking']==2 else '🥉' if x['Ranking']==3 else '👤'} {x['customer_name'] if x['customer_name'] else x['customer_email'][:20]}", axis=1)
                    fig_top_cust = px.bar(top_customers.sort_values('Total_Gastado'), x='Total_Gastado', y='Cliente', orientation='h', text=top_customers.sort_values('Total_Gastado')['Total_Gastado'].apply(lambda x: f"${x:,.0f}"))
                    fig_top_cust.update_traces(marker_color='#10b981', textposition='outside', cliponaxis=False)
                    fig_top_cust.update_layout(yaxis=dict(title='', tickfont=dict(family='Arial Black', size=10, color='#000000')), xaxis=dict(title='', showgrid=False, showticklabels=False), template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=150, t=0, b=0), height=400, uniformtext_minsize=8, uniformtext_mode='hide')
                    st.plotly_chart(fig_top_cust, use_container_width=True, config=PLOTLY_CONFIG)
                with col_cust2:
                    st.markdown("#### ⭐ Clientes Nuevos Frecuentes")
                    new_customers = customer_stats[(customer_stats['Primera_Compra'] >= start_date) & (customer_stats['Primera_Compra'] <= end_date)].copy()
                    frequent_new = new_customers[new_customers['Num_Pedidos'] >= 2].copy().sort_values('Num_Pedidos', ascending=False).head(10)
                    if not frequent_new.empty:
                        frequent_new['Cliente'] = frequent_new.apply(lambda x: f"⭐ {x['customer_name'] if x['customer_name'] else x['customer_email'][:20]}", axis=1)
                        fig_new_freq = px.bar(frequent_new.sort_values('Num_Pedidos'), x='Num_Pedidos', y='Cliente', orientation='h', text=frequent_new.sort_values('Num_Pedidos')['Num_Pedidos'].apply(lambda x: f"{x} pedidos"))
                        fig_new_freq.update_traces(marker_color='#f59e0b', textposition='outside', cliponaxis=False)
                        fig_new_freq.update_layout(yaxis=dict(title='', tickfont=dict(family='Arial Black', size=10, color='#000000')), xaxis=dict(title='', showgrid=False, showticklabels=False), template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=150, t=0, b=0), height=400, uniformtext_minsize=8, uniformtext_mode='hide')
                        st.plotly_chart(fig_new_freq, use_container_width=True, config=PLOTLY_CONFIG)
                    else:
                        st.info("No hay clientes nuevos frecuentes.")
            else:
                st.info("⚠️ Solo pedidos de invitados.")
        else:
            st.warning("⚠️ Datos de clientes no disponibles.")

    # ================= TAB 5: TRÁFICO Y REDES =================
    with tab5:
        st.markdown("### 🌐 Tráfico y Audiencia")
        if not combined_df.empty and 'Visitas' in combined_df.columns:
            st.markdown("#### 👁️ Visitas Diarias")
            fig_visits = go.Figure()
            fig_visits.add_trace(go.Scatter(x=combined_df['date_only'], y=combined_df['Visitas'], name='Visitas', mode='lines', fill='tozeroy', line=dict(width=3, color='#00f2ff'), fillcolor='rgba(0, 242, 255, 0.1)', hovertemplate='%{x|%d %b}: <b>%{y}</b> Visitas<extra></extra>'))
            fig_visits.update_layout(
                template='plotly_dark', 
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)', 
                height=280, 
                margin=dict(l=10, r=10, t=10, b=40), 
                xaxis=dict(
                    showgrid=False, 
                    tickformat='%d %b', 
                    tickfont=dict(size=12, color='#000000'),
                    tickangle=-45,
                    showticklabels=True
                ), 
                yaxis=dict(
                    showgrid=True, 
                    gridcolor='rgba(255,255,255,0.05)', 
                    title='', 
                    tickfont=dict(size=11, color='#000000')
                )
            )
            st.plotly_chart(fig_visits, use_container_width=True, config=PLOTLY_CONFIG)

        # Gráfico 1: Origen del Tráfico (full width)
        st.markdown("#### Origen del Tráfico")
        if not df_ga_traffic.empty:
            mask_tr = (df_ga_traffic['Fecha'] >= start_date) & (df_ga_traffic['Fecha'] <= end_date)
            df_traffic_filt = df_ga_traffic.loc[mask_tr].copy()
            if not df_traffic_filt.empty:
                df_traffic_filt['Fuente_Normalizada'] = df_traffic_filt['Fuente'].apply(normalize_traffic_source)
                traffic_summary = df_traffic_filt.groupby('Fuente_Normalizada').agg(Sesiones=('Sesiones', 'sum')).reset_index()
                clean_traffic = traffic_summary[~traffic_summary['Fuente_Normalizada'].str.contains('Bot/Spam', case=False, na=False)]
                if not clean_traffic.empty:
                    clean_traffic = clean_traffic.sort_values('Sesiones', ascending=False).head(10)
                    colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316', '#06b6d4', '#84cc16']
                    fig_traffic = go.Figure(data=[go.Pie(labels=clean_traffic['Fuente_Normalizada'], values=clean_traffic['Sesiones'], hole=0.5, marker=dict(colors=colors[:len(clean_traffic)], line=dict(color='rgba(255,255,255,0.3)', width=2)), textinfo='label+percent', textposition='inside', textfont=dict(size=11), hovertemplate='<b>%{label}</b><br>%{value:,} sesiones<br>%{percent}<extra></extra>', pull=[0.05 if i == 0 else 0 for i in range(len(clean_traffic))])])
                    fig_traffic.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=True, legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05, font=dict(size=11, color='#ffffff'), bgcolor='rgba(16, 16, 37, 0.95)', bordercolor='#00f2ff', borderwidth=2), margin=dict(l=0, r=150, t=0, b=0), height=400, dragmode=False)
                    st.plotly_chart(fig_traffic, use_container_width=True, config=PLOTLY_CONFIG)
                else:
                    st.info("Solo tráfico spam.")
            else:
                st.info("No hay datos de tráfico.")
        else:
            st.info("Datos GA no disponibles.")

        # Gráfico 2: Páginas Más Visitadas (full width)
        st.markdown("#### 📄 Páginas Más Visitadas")
        try:
            df_pages = load_data('ga4_pages', DATABASE_ANALYTICS)
            if not df_pages.empty:
                df_pages['Fecha'] = pd.to_datetime(df_pages['Fecha'])
                mask_ga = (df_pages['Fecha'] >= start_date) & (df_pages['Fecha'] <= end_date)
                df_pages_filtered = df_pages.loc[mask_ga]
                if not df_pages_filtered.empty:
                    top_pages = df_pages_filtered.groupby('Pagina', as_index=False)['Vistas'].sum().sort_values(by='Vistas', ascending=False).head(8).sort_values(by='Vistas', ascending=True)
                    fig_pages = px.bar(top_pages, x='Vistas', y='Pagina', orientation='h', text='Vistas')
                    fig_pages.update_traces(marker_color='#ec4899', texttemplate='%{text}', textposition='outside', cliponaxis=False)
                    fig_pages.update_layout(yaxis=dict(title='', tickfont=dict(family='Arial Black', size=11, color='#000000')), xaxis=dict(title='', showgrid=False, showticklabels=False), template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=150, t=0, b=0), height=400, dragmode=False)
                    st.plotly_chart(fig_pages, use_container_width=True, config=PLOTLY_CONFIG)
                else:
                    st.info("Sin visitas.")
        except:
            pass

        st.markdown("---")
        st.markdown("### 📱 Redes Sociales (Facebook)")
        if not df_facebook.empty:
            mask_fb = (df_facebook['date'] >= start_date) & (df_facebook['date'] <= end_date)
            df_fb_filtered = df_facebook.loc[mask_fb]
            if not df_fb_filtered.empty:
                impressions = df_fb_filtered['page_impressions'].sum() if 'page_impressions' in df_fb_filtered else 0
                engagement = df_fb_filtered['page_engaged_users'].sum() if 'page_engaged_users' in df_fb_filtered else 0
                col_fb1, col_fb2 = st.columns(2)
                with col_fb1: metric_card("Impresiones", f"{impressions:,.0f}", icon="fa-eye", color="#1877F2", help_text="Total Vistas")
                with col_fb2: metric_card("Engagement", f"{engagement:,.0f}", icon="fa-thumbs-up", color="#4267B2", help_text="Total Interacciones")
                
                fig_fb = go.Figure()
                fig_fb.add_trace(go.Scatter(x=df_fb_filtered['date'], y=df_fb_filtered['page_impressions'], name='Impresiones', mode='lines', fill='tozeroy', line=dict(color='#1877F2', width=2), fillcolor='rgba(24, 119, 242, 0.1)'))
                fig_fb.add_trace(go.Scatter(x=df_fb_filtered['date'], y=df_fb_filtered['page_engaged_users'], name='Engagement', mode='lines', line=dict(color='#34D399', width=2)))
                fig_fb.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=300, margin=dict(l=10, r=10, t=10, b=10), xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'), legend=dict(orientation="h", y=1.1), dragmode=False)
                st.plotly_chart(fig_fb, use_container_width=True, config=PLOTLY_CONFIG)
            else:
                st.info("Sin datos FB en periodo.")

    st.markdown("---")
    st.caption(f"🔄 Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
