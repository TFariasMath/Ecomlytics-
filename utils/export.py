"""
Report Export Module

Exports dashboard data and visualizations to PDF and Excel formats.
Allows users to share reports offline and in meetings.
"""

import pandas as pd
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime
import io
import os


class ReportExporter:
    """Handles PDF and Excel export functionality"""
    
    @staticmethod
    def export_to_excel(data_dict: dict, filename: str = None) -> str:
        """
        Export data to Excel with multiple sheets
        
        Args:
            data_dict: Dictionary of {sheet_name: dataframe}
            filename: Output filename (auto-generated if None)
        
        Returns:
            Path to generated file
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"reporte_analytics_{timestamp}.xlsx"
        
        # Create Excel writer
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            for sheet_name, df in data_dict.items():
                # Write dataframe
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Auto-adjust column widths
                worksheet = writer.sheets[sheet_name]
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    
                    for cell in column:
                        try:
                            cell_length = len(str(cell.value))
                            if cell_length > max_length:
                                max_length = cell_length
                        except Exception:
                            pass
                    
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
        
        return filename
    
    @staticmethod
    def export_to_pdf(metrics: dict, data_tables: dict = None, filename: str = None) -> str:
        """
        Export dashboard to PDF report
        
        Args:
            metrics: Dictionary of key metrics {name: value}
            data_tables: Optional dict of {table_name: dataframe}
            filename: Output filename (auto-generated if None)
        
        Returns:
            Path to generated file
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"dashboard_analytics_{timestamp}.pdf"
        
        # Create PDF
        doc = SimpleDocTemplate(filename, pagesize=letter,
                               rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=18)
        
        # Container for PDF elements
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#4318FF'),
            spaceAfter=30,
            alignment=1  # Center
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2B3674'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Title
        title = Paragraph("Reporte de Analytics", title_style)
        story.append(title)
        
        # Date
        date_str = datetime.now().strftime('%d de %B de %Y, %H:%M')
        date_para = Paragraph(f"Generado: {date_str}", styles['Normal'])
        story.append(date_para)
        story.append(Spacer(1, 20))
        
        # Metrics Section
        if metrics:
            metrics_heading = Paragraph("Métricas Principales", heading_style)
            story.append(metrics_heading)
            
            # Create metrics table
            metrics_data = [['Métrica', 'Valor']]
            for key, value in metrics.items():
                # Format large numbers
                if isinstance(value, (int, float)) and abs(value) >= 1000:
                    formatted_value = f"${value:,.0f}" if 'ventas' in key.lower() or 'ingresos' in key.lower() else f"{value:,.0f}"
                else:
                    formatted_value = str(value)
                metrics_data.append([key, formatted_value])
            
            metrics_table = Table(metrics_data, colWidths=[3*inch, 2*inch])
            metrics_table.setStyle(TableStyle([
                # Header
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4318FF')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                
                # Body
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F4F7FE')]),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ]))
            
            story.append(metrics_table)
            story.append(Spacer(1, 20))
        
        # Data Tables Section
        if data_tables:
            for table_name, df in data_tables.items():
                # Add page break between large tables
                if len(story) > 5:
                    story.append(PageBreak())
                
                table_heading = Paragraph(table_name, heading_style)
                story.append(table_heading)
                
                # Limit rows for PDF
                df_limited = df.head(20)  # First 20 rows only
                
                # Convert dataframe to list
                table_data = [df_limited.columns.tolist()] + df_limited.values.tolist()
                
                # Create table
                col_count = len(df_limited.columns)
                col_width = 6.5*inch / col_count
                
                data_table = Table(table_data, colWidths=[col_width] * col_count)
                data_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2B3674')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F4F7FE')]),
                ]))
                
                story.append(data_table)
                
                # Note if data was truncated
                if len(df) > 20:
                    note = Paragraph(
                        f"<i>Mostrando 20 de {len(df)} registros. Exporta a Excel para ver todos.</i>",
                        styles['Normal']
                    )
                    story.append(Spacer(1, 6))
                    story.append(note)
                
                story.append(Spacer(1, 15))
        
        # Footer info
        story.append(Spacer(1, 20))
        footer = Paragraph(
            "<i>Generado por Analytics Pipeline - www.analytics.com</i>",
            styles['Normal']
        )
        story.append(footer)
        
        # Build PDF
        doc.build(story)
        
        return filename
    
    @staticmethod
    def create_summary_export(df_orders: pd.DataFrame, start_date: str, end_date: str) -> dict:
        """
        Create pre-formatted data dict for export
        
        Args:
            df_orders: Orders dataframe
            start_date: Period start
            end_date: Period end
        
        Returns:
            Dictionary ready for export_to_excel()
        """
        # Summary metrics
        summary_df = pd.DataFrame([{
            'Período': f"{start_date} - {end_date}",
            'Total Ventas': f"${df_orders['total'].sum():,.2f}",
            'Total Órdenes': len(df_orders),
            'Ticket Promedio': f"${df_orders['total'].mean():,.2f}",
            'Generado': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }])
        
        # Orders detail
        orders_df = df_orders[['date_created', 'order_id', 'customer_name', 'total', 'status']].copy()
        orders_df['total'] = orders_df['total'].apply(lambda x: f"${x:,.2f}")
        
        # Daily aggregation
        df_daily = df_orders.groupby(df_orders['date_created'].dt.date).agg({
            'total': 'sum',
            'order_id': 'count'
        }).reset_index()
        df_daily.columns = ['Fecha', 'Ventas', 'Cantidad Órdenes']
        df_daily['Ventas'] = df_daily['Ventas'].apply(lambda x: f"${x:,.2f}")
        
        return {
            'Resumen': summary_df,
            'Ventas Diarias': df_daily,
            'Detalle Órdenes': orders_df
        }
    
    @staticmethod
    def export_daily_orders_pdf(df_orders: pd.DataFrame, df_items: pd.DataFrame, 
                                 selected_date: str, company_name: str = "Analytics Pipeline") -> bytes:
        """
        Export detailed daily orders report to PDF for delivery control.
        
        Args:
            df_orders: Orders dataframe for the selected date
            df_items: Order items dataframe with product details
            selected_date: Date string in format 'YYYY-MM-DD'
            company_name: Company name for the header
        
        Returns:
            PDF bytes for download
        """
        from io import BytesIO
        
        # Create PDF buffer
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                               rightMargin=40, leftMargin=40,
                               topMargin=40, bottomMargin=30)
        
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#4318FF'),
            spaceAfter=10,
            alignment=1  # Center
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2B3674'),
            spaceAfter=8,
            spaceBefore=12
        )
        
        subheading_style = ParagraphStyle(
            'SubHeading',
            parent=styles['Heading3'],
            fontSize=11,
            textColor=colors.HexColor('#4318FF'),
            spaceAfter=4,
            spaceBefore=8
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=9,
            spaceAfter=4
        )
        
        small_style = ParagraphStyle(
            'Small',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey
        )
        
        # === HEADER ===
        title = Paragraph(f"📋 Reporte de Entregas - {company_name}", title_style)
        story.append(title)
        
        # Format date nicely
        try:
            date_obj = datetime.strptime(selected_date, '%Y-%m-%d')
            date_formatted = date_obj.strftime('%A %d de %B de %Y').title()
        except ValueError:
            date_formatted = selected_date
        
        date_para = Paragraph(f"<b>Fecha:</b> {date_formatted}", normal_style)
        story.append(date_para)
        
        generated_para = Paragraph(f"<i>Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}</i>", small_style)
        story.append(generated_para)
        story.append(Spacer(1, 15))
        
        # === SUMMARY SECTION ===
        story.append(Paragraph("📊 Resumen del Día", heading_style))
        
        total_orders = len(df_orders)
        total_revenue = df_orders['total'].sum()
        avg_ticket = total_revenue / total_orders if total_orders > 0 else 0
        total_shipping = df_orders['shipping_total'].sum() if 'shipping_total' in df_orders.columns else 0
        
        summary_data = [
            ['Total Pedidos', 'Ventas Totales', 'Ticket Promedio', 'Costo Envío'],
            [f"{total_orders}", f"${total_revenue:,.0f}", f"${avg_ticket:,.0f}", f"${total_shipping:,.0f}"]
        ]
        
        summary_table = Table(summary_data, colWidths=[1.8*inch, 1.8*inch, 1.8*inch, 1.8*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4318FF')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F4F7FE')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E0E5F2')),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # === ORDERS DETAIL ===
        story.append(Paragraph("📦 Detalle de Pedidos para Entrega", heading_style))
        story.append(Spacer(1, 10))
        
        # Sort orders by order_id
        df_orders_sorted = df_orders.sort_values('order_id')
        
        for idx, (_, order) in enumerate(df_orders_sorted.iterrows()):
            if idx > 0:
                story.append(Spacer(1, 10))
                # Separator line
                story.append(Paragraph("<hr/>", normal_style))
            
            order_id = order.get('order_id', 'N/A')
            
            # Customer info header
            story.append(Paragraph(f"<b>Pedido #{order_id}</b>", subheading_style))
            
            # Order time
            order_date = order.get('date_created', '')
            if pd.notna(order_date):
                try:
                    if isinstance(order_date, str):
                        order_time = order_date
                    else:
                        order_time = order_date.strftime('%H:%M')
                except Exception:
                    order_time = 'N/A'
            else:
                order_time = 'N/A'
            story.append(Paragraph(f"<b>🕐 Hora:</b> {order_time}", normal_style))
            
            # Customer details
            customer_name = order.get('customer_name', 'Guest') or 'Guest'
            customer_email = order.get('customer_email', '') or ''
            customer_phone = order.get('billing_phone', '') or 'Sin teléfono'
            
            story.append(Paragraph(f"<b>👤 Cliente:</b> {customer_name}", normal_style))
            story.append(Paragraph(f"<b>📱 Teléfono:</b> {customer_phone}", normal_style))
            if customer_email:
                story.append(Paragraph(f"<b>📧 Email:</b> {customer_email}", normal_style))
            
            # Billing Address (where the customer is located)
            billing_city = order.get('billing_city', '') or ''
            billing_state = order.get('billing_state', '') or ''
            billing_location = f"{billing_city}, {billing_state}" if billing_city and billing_state else billing_city or billing_state or 'N/A'
            story.append(Paragraph(f"<b>📍 Ubicación Cliente:</b> {billing_location}", normal_style))
            
            # Shipping/Delivery Address (where to deliver)
            # First try shipping address, then fall back to billing if shipping is empty
            shipping_name = f"{order.get('shipping_first_name', '') or ''} {order.get('shipping_last_name', '') or ''}".strip()
            shipping_address_1 = order.get('shipping_address_1', '') or ''
            shipping_address_2 = order.get('shipping_address_2', '') or ''
            shipping_city = order.get('shipping_city', '') or ''
            shipping_state = order.get('shipping_state', '') or ''
            shipping_postcode = order.get('shipping_postcode', '') or ''
            
            # If no shipping address, use billing address as fallback
            if not shipping_address_1 and not shipping_city:
                shipping_address_1 = order.get('billing_address_1', '') or ''
                shipping_address_2 = order.get('billing_address_2', '') or ''
                shipping_city = order.get('billing_city', '') or ''
                shipping_state = order.get('billing_state', '') or ''
                shipping_postcode = order.get('billing_postcode', '') or ''
                # Include company name if available (like "PASTELERÍA NOBITA")
                billing_company = order.get('billing_company', '') or ''
                if billing_company:
                    shipping_name = billing_company
            
            # Build full delivery address
            delivery_parts = []
            if shipping_name and shipping_name != customer_name:
                delivery_parts.append(shipping_name)
            if shipping_address_1:
                full_address = shipping_address_1
                if shipping_address_2:
                    full_address += f", {shipping_address_2}"
                delivery_parts.append(full_address)
            if shipping_city or shipping_state:
                city_state = f"{shipping_city}, {shipping_state}" if shipping_city and shipping_state else shipping_city or shipping_state
                if shipping_postcode:
                    city_state += f" ({shipping_postcode})"
                delivery_parts.append(city_state)
            
            if delivery_parts:
                delivery_address = " | ".join(delivery_parts)
                story.append(Paragraph(f"<b>📦 Dirección Entrega:</b> {delivery_address}", normal_style))
            
            # Customer Note (delivery instructions like "ENVIO POR TVP")
            customer_note = order.get('customer_note', '') or ''
            if customer_note:
                story.append(Paragraph(f"<b>📝 Nota Cliente:</b> {customer_note}", normal_style))
            
            # Shipping method
            shipping_method = order.get('shipping_method', '') or 'N/A'
            story.append(Paragraph(f"<b>🚚 Envío:</b> {shipping_method}", normal_style))
            
            # Payment method
            payment_method = order.get('payment_method_title', '') or 'N/A'
            story.append(Paragraph(f"<b>💳 Pago:</b> {payment_method}", normal_style))
            
            # Coupons
            coupons = order.get('coupons_used', '') or ''
            if coupons:
                story.append(Paragraph(f"<b>🎟️ Cupones:</b> {coupons}", normal_style))
            
            # Products for this order
            order_items = df_items[df_items['order_id'] == order_id] if not df_items.empty else pd.DataFrame()
            
            if not order_items.empty:
                story.append(Spacer(1, 5))
                story.append(Paragraph("<b>Productos:</b>", normal_style))
                
                products_data = [['Producto', 'Cant.', 'Precio', 'Total']]
                for _, item in order_items.iterrows():
                    product_name = str(item.get('product_name', 'Producto'))[:40]
                    quantity = int(item.get('quantity', 1))
                    price = float(item.get('price', 0))
                    item_total = float(item.get('total', quantity * price))
                    products_data.append([
                        product_name,
                        str(quantity),
                        f"${price:,.0f}",
                        f"${item_total:,.0f}"
                    ])
                
                products_table = Table(products_data, colWidths=[3*inch, 0.6*inch, 1*inch, 1*inch])
                products_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E8E8E8')),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ]))
                story.append(products_table)
            
            # Order totals
            story.append(Spacer(1, 5))
            subtotal = float(order.get('total', 0)) - float(order.get('shipping_total', 0) or 0)
            shipping = float(order.get('shipping_total', 0) or 0)
            discount = float(order.get('discount_total', 0) or 0)
            total = float(order.get('total', 0))
            
            totals_text = f"<b>Subtotal:</b> ${subtotal:,.0f}"
            if shipping > 0:
                totals_text += f" | <b>Envío:</b> ${shipping:,.0f}"
            if discount > 0:
                totals_text += f" | <b>Descuento:</b> -${discount:,.0f}"
            totals_text += f" | <b>TOTAL: ${total:,.0f}</b>"
            
            story.append(Paragraph(totals_text, normal_style))
            
            # Status
            status_map = {
                'completed': '✅ Completado',
                'completoenviado': '📦 Completo-Enviado', 
                'processing': '⏳ Procesando',
                'porsalir': '🚚 Por Salir',
                'on-hold': '⏸️ En Espera',
                'pending': '⏰ Pendiente'
            }
            status = order.get('status', 'unknown')
            status_text = status_map.get(status, status)
            story.append(Paragraph(f"<b>Estado:</b> {status_text}", normal_style))
            
            # Page break every 3-4 orders to keep readable
            if (idx + 1) % 3 == 0 and idx < len(df_orders_sorted) - 1:
                story.append(PageBreak())
                story.append(Paragraph(f"📋 Reporte de Entregas - {date_formatted} (continuación)", title_style))
                story.append(Spacer(1, 10))
        
        # === QUICK REFERENCE TABLE ===
        story.append(PageBreak())
        story.append(Paragraph("📋 Tabla Resumen de Entregas", heading_style))
        story.append(Paragraph("<i>Lista rápida para control de entregas</i>", small_style))
        story.append(Spacer(1, 10))
        
        quick_ref_data = [['#', 'Cliente', 'Teléfono', 'Ubicación', 'Total', '✓']]
        for _, order in df_orders_sorted.iterrows():
            order_id = str(order.get('order_id', ''))
            customer = str(order.get('customer_name', 'Guest') or 'Guest')[:20]
            phone = str(order.get('billing_phone', '') or 'N/A')[:15]
            city = order.get('billing_city', '') or ''
            location = city[:15] if city else 'N/A'
            total = f"${float(order.get('total', 0)):,.0f}"
            quick_ref_data.append([order_id, customer, phone, location, total, '☐'])
        
        quick_ref_table = Table(quick_ref_data, 
                                colWidths=[0.5*inch, 1.8*inch, 1.3*inch, 1.2*inch, 0.9*inch, 0.4*inch])
        quick_ref_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2B3674')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F4F7FE')]),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(quick_ref_table)
        
        # Footer
        story.append(Spacer(1, 20))
        story.append(Paragraph(
            f"<i>Total: {total_orders} entregas | Monto total: ${total_revenue:,.0f} | Generado por {company_name}</i>",
            small_style
        ))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes

    @staticmethod
    def export_single_order_pdf(order: dict, df_items: pd.DataFrame, company_name: str = "Mi Empresa") -> bytes:
        """
        Generate a compact professional PDF for a single order (invoice style)
        """
        import os
        
        # Get company data from environment
        company_name = os.getenv('COMPANY_NAME', company_name)
        company_rut = os.getenv('COMPANY_RUT', '')
        company_address = os.getenv('COMPANY_ADDRESS', '')
        company_city = os.getenv('COMPANY_CITY', '')
        company_phone = os.getenv('COMPANY_PHONE', '')
        company_email = os.getenv('COMPANY_EMAIL', '')
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=letter, 
            topMargin=0.4*inch, 
            bottomMargin=0.4*inch,
            leftMargin=0.5*inch,
            rightMargin=0.5*inch
        )
        story = []
        
        # Color scheme
        primary_color = colors.HexColor('#1a365d')  # Dark blue
        accent_color = colors.HexColor('#3182ce')   # Light blue
        light_gray = colors.HexColor('#f7fafc')
        border_gray = colors.HexColor('#e2e8f0')
        text_gray = colors.HexColor('#4a5568')
        
        # Styles
        styles = getSampleStyleSheet()
        
        company_style = ParagraphStyle(
            'CompanyName', parent=styles['Heading1'],
            fontSize=18, textColor=primary_color, spaceAfter=2
        )
        subtitle_style = ParagraphStyle(
            'Subtitle', parent=styles['Normal'],
            fontSize=9, textColor=accent_color, spaceAfter=0
        )
        order_num_style = ParagraphStyle(
            'OrderNum', parent=styles['Normal'],
            fontSize=14, textColor=primary_color, alignment=2, spaceAfter=2
        )
        date_style = ParagraphStyle(
            'DateStyle', parent=styles['Normal'],
            fontSize=9, textColor=text_gray, alignment=2
        )
        label_style = ParagraphStyle(
            'Label', parent=styles['Normal'],
            fontSize=8, textColor=accent_color, spaceAfter=2
        )
        info_style = ParagraphStyle(
            'Info', parent=styles['Normal'],
            fontSize=9, textColor=colors.black, spaceAfter=1
        )
        small_info_style = ParagraphStyle(
            'SmallInfo', parent=styles['Normal'],
            fontSize=8, textColor=text_gray, spaceAfter=1
        )
        
        order_id = order.get('order_id', 'N/A')
        
        # Format date
        date_created = order.get('date_created')
        if date_created:
            if hasattr(date_created, 'strftime'):
                date_str = date_created.strftime('%Y-%m-%d')
            else:
                date_str = str(date_created)[:10]
        else:
            date_str = datetime.now().strftime('%Y-%m-%d')
        
        # === HEADER: Company left, Order # right ===
        header_data = [
            [
                Paragraph(company_name, company_style),
                Paragraph(f"<b>PEDIDO</b><br/><font size='16'>#{order_id}</font>", order_num_style)
            ],
            [
                Paragraph("ORDEN DE ENTREGA", subtitle_style),
                Paragraph(f"FECHA: {date_str}", date_style)
            ]
        ]
        header_table = Table(header_data, colWidths=[4*inch, 3*inch])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 15))
        
        # === THREE COLUMNS: EMISOR | FACTURAR A | ENVÍO ===
        # Get customer info
        customer_name = order.get('customer_name', 'Cliente') or 'Cliente'
        customer_phone_billing = order.get('billing_phone', '') or ''
        customer_email = order.get('customer_email', '') or ''
        
        # Billing address
        billing_address = order.get('billing_address_1', '') or ''
        billing_city = order.get('billing_city', '') or ''
        billing_company = order.get('billing_company', '') or ''
        
        # Shipping address (with billing fallback)
        shipping_address = order.get('shipping_address_1', '') or order.get('billing_address_1', '') or ''
        shipping_city = order.get('shipping_city', '') or order.get('billing_city', '') or ''
        shipping_state = order.get('shipping_state', '') or order.get('billing_state', '') or ''
        
        # Build address strings (compact)
        billing_location = f"{billing_city}, {shipping_state}" if billing_city else ''
        shipping_location = f"{shipping_city}, {shipping_state}" if shipping_city else ''
        
        shipping_method = order.get('shipping_method', '') or ''
        payment_method = order.get('payment_method_title', '') or ''
        
        # Column 1: EMISOR (Company) - Now with full details
        emisor_lines = [f"<b>{company_name}</b>"]
        if company_rut:
            emisor_lines.append(f"<font size='8'>RUT: {company_rut}</font>")
        if company_address:
            emisor_lines.append(f"<font size='8'>{company_address}</font>")
        if company_city:
            emisor_lines.append(f"<font size='8'>{company_city}</font>")
        if company_phone:
            emisor_lines.append(f"<font size='8'>📞 {company_phone}</font>")
        if company_email:
            emisor_lines.append(f"<font size='8'>✉ {company_email}</font>")
        
        emisor_content = Paragraph("<br/>".join(emisor_lines), info_style)
        
        # Column 2: FACTURAR A
        facturar_content = [
            Paragraph(f"<b>{customer_name}</b>", info_style)
        ]
        if billing_company:
            facturar_content.append(Paragraph(billing_company, small_info_style))
        if billing_address:
            facturar_content.append(Paragraph(billing_address, small_info_style))
        if billing_location:
            facturar_content.append(Paragraph(billing_location, small_info_style))
        if customer_email:
            facturar_content.append(Paragraph(f"✉ {customer_email}", small_info_style))
        if customer_phone_billing:
            facturar_content.append(Paragraph(f"📞 {customer_phone_billing}", small_info_style))
        
        # Column 3: ENVÍO
        envio_content = [
            Paragraph(f"<b>{customer_name}</b>", info_style)
        ]
        if shipping_address:
            envio_content.append(Paragraph(shipping_address, small_info_style))
        if shipping_location:
            envio_content.append(Paragraph(shipping_location, small_info_style))
        
        # Customer note
        customer_note = order.get('customer_note', '') or ''
        
        # Method info
        method_content = []
        if shipping_method:
            method_content.append(Paragraph(f"<b>MÉTODO</b>: {shipping_method}", small_info_style))
        if payment_method:
            method_content.append(Paragraph(f"<b>PAGO</b>: {payment_method}", small_info_style))
        
        # Build 3-column table
        col_data = [
            [
                Paragraph("<b>EMISOR</b>", label_style),
                Paragraph("<b>FACTURAR A</b>", label_style),
                Paragraph("<b>ENVÍO</b>", label_style)
            ],
            [emisor_content, facturar_content, envio_content + method_content]
        ]
        
        col_table = Table(col_data, colWidths=[2.2*inch, 2.4*inch, 2.4*inch])
        col_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LINEBELOW', (0, 0), (-1, 0), 0.5, border_gray),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(col_table)
        
        # Customer note if exists
        if customer_note:
            story.append(Spacer(1, 5))
            note_style = ParagraphStyle('Note', parent=styles['Normal'], fontSize=8, textColor=accent_color)
            story.append(Paragraph(f"📝 <b>Nota:</b> {customer_note}", note_style))
        
        story.append(Spacer(1, 15))
        
        # === PRODUCTS TABLE ===
        product_data = [['DESCRIPCIÓN', 'CANT.', 'PRECIO UNIT.', 'TOTAL']]
        
        if not df_items.empty:
            for _, item in df_items.iterrows():
                product_name = str(item.get('product_name', 'Producto'))[:45]
                quantity = int(item.get('quantity', 1))
                price = float(item.get('price', 0))
                item_total = float(item.get('total', quantity * price))
                product_data.append([
                    product_name,
                    str(quantity),
                    f"${price:,.0f}",
                    f"${item_total:,.0f}"
                ])
        else:
            product_data.append(['Sin productos', '', '', ''])
        
        products_table = Table(product_data, colWidths=[3.5*inch, 0.7*inch, 1.1*inch, 1.1*inch])
        products_table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), light_gray),
            ('TEXTCOLOR', (0, 0), (-1, 0), text_gray),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            # Data
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            # Lines
            ('LINEBELOW', (0, 0), (-1, 0), 1, border_gray),
            ('LINEBELOW', (0, 1), (-1, -2), 0.5, border_gray),
            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(products_table)
        
        story.append(Spacer(1, 15))
        
        # === TOTALS (right-aligned) ===
        shipping_cost = float(order.get('shipping_total', 0) or 0)
        discount = float(order.get('discount_total', 0) or 0)
        total = float(order.get('total', 0))
        
        # Calculate Net and VAT (Chile 19%)
        total_iva = total * 0.19 / 1.19
        neto = total - total_iva - shipping_cost + discount
        
        totals_data = []
        totals_data.append(['SUBTOTAL (NETO)', f"${neto:,.0f}"])
        totals_data.append(['IVA (19%)', f"${total_iva:,.0f}"])
        if discount > 0:
            totals_data.append(['DESCUENTO', f"- ${discount:,.0f}"])
        if shipping_cost > 0:
            totals_data.append(['ENVÍO', f"${shipping_cost:,.0f}"])
        totals_data.append(['TOTAL A PAGAR', f"${total:,.0f}"])
        
        totals_table = Table(totals_data, colWidths=[1.5*inch, 1.5*inch])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTSIZE', (0, 0), (-1, -2), 9),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (1, 0), (1, -2), text_gray),
            ('TEXTCOLOR', (1, -1), (1, -1), primary_color),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LINEABOVE', (0, -1), (-1, -1), 1, border_gray),
        ]))
        
        # Wrap totals in a table to right-align
        wrapper = Table([[None, totals_table]], colWidths=[4*inch, 3*inch])
        story.append(wrapper)
        
        # Build PDF
        doc.build(story)
        
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
