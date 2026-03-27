
import os
import matplotlib
matplotlib.use('Agg') # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.units import inch
from datetime import datetime

# --- CONFIGURACIÓN DE ESTILOS DE GRÁFICOS ---
COLOR_PRIMARY = '#4318FF'
COLOR_SECONDARY = '#6AD2FF'
COLOR_SUCCESS = '#05CD99'
COLOR_WARNING = '#FFB547'

def generate_mock_images():
    """Genera imágenes sintéticas que simulan las vistas del dashboard."""
    print("Generando visualizaciones...")
    
    # 1. KPI Cards Row (Simulado con matplotlib para mantener coherencia visual)
    fig_kpi, ax = plt.subplots(figsize=(10, 2.5))
    ax.axis('off')
    
    # Datos de ejemplo
    kpis = [
        {'title': 'Ingresos Totales', 'val': '$12.450.000', 'delta': '+15.2%', 'color': COLOR_PRIMARY},
        {'title': 'Pedidos Totales', 'val': '342', 'delta': '+5.8%', 'color': COLOR_WARNING},
        {'title': 'Ticket Promedio', 'val': '$36.400', 'delta': '+1.2%', 'color': COLOR_SUCCESS},
        {'title': 'Tasa Conversión', 'val': '2.8%', 'delta': '-0.5%', 'color': '#EE5D50'}
    ]
    
    # Dibujar "Tarjetas"
    for i, item in enumerate(kpis):
        x_offset = i * 2.6
        # Fondo tarjeta
        rect = plt.Rectangle((x_offset, 0), 2.4, 2, facecolor='#F4F7FE', edgecolor='#E0E5F2', linewidth=1, zorder=1)
        ax.add_patch(rect)
        # Contenido
        ax.text(x_offset + 0.2, 1.5, item['title'].upper(), fontsize=9, color='gray', zorder=2)
        ax.text(x_offset + 0.2, 0.9, item['val'], fontsize=18, fontweight='bold', color='#1B2559', zorder=2)
        
        delta_color = 'green' if '+' in item['delta'] else 'red'
        icon = '▲' if '+' in item['delta'] else '▼'
        ax.text(x_offset + 0.2, 0.4, f"{icon} {item['delta']} vs mes ant.", fontsize=8, color=delta_color, zorder=2)

    ax.set_xlim(-0.1, 10.5)
    ax.set_ylim(0, 2.2)
    plt.tight_layout()
    plt.savefig('viz_kpis.png', dpi=150, bbox_inches='tight')
    plt.close()

    # 2. Gráfico de Ventas (Bar + Line)
    plt.style.use('bmh')
    fig_sales, ax1 = plt.subplots(figsize=(10, 4))
    
    months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    sales_2024 = [3.5, 3.8, 4.2, 4.0, 3.9, 4.5, 4.8, 5.2, 6.0, 7.5, 8.2, 9.5] # Millones
    sales_2025 = [4.5, 5.0, 5.5, 5.1, 4.9, 6.2, 6.8, 7.5, 8.2, 9.1, 10.5, 12.4]
    
    # Barras 2025
    bars = ax1.bar(months, sales_2025, color=COLOR_PRIMARY, alpha=0.8, label='Ventas 2025')
    
    # Línea 2024
    ax1.plot(months, sales_2024, color='gray', linestyle='--', linewidth=2, marker='o', label='Ventas 2024')
    
    ax1.set_ylabel('Ventas (Millones CLP)')
    ax1.set_title('Evolución de Ventas: Comparativa Anual', pad=15)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Añadir valores sobre las barras
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'${height}M', ha='center', va='bottom', fontsize=8)

    plt.tight_layout()
    plt.savefig('viz_sales.png', dpi=150)
    plt.close()

    # 3. Grífico de Inventario / Categorías (Pie)
    fig_pie, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    
    # Pie Chart
    labels = ['Frutos Secos', 'Harinas', 'Semillas', 'Mixes', 'Otros']
    sizes = [45, 20, 15, 12, 8]
    colors_pie = [COLOR_PRIMARY, COLOR_SECONDARY, COLOR_SUCCESS, COLOR_WARNING, '#A3AED0']
    
    ax1.pie(sizes, labels=labels, colors=colors_pie, autopct='%1.1f%%', startangle=90, 
            wedgeprops=dict(width=0.4, edgecolor='white'))
    ax1.set_title('Distribución por Categoría')
    
    # Horizontal Bar (Top Products)
    products = ['Almendra Non Pareil', 'Nuez Mariposa', 'Maní Sin Sal', 'Harina Almendra', 'Mix Energético']
    values = [1450, 1200, 980, 850, 620] # Unidades
    
    y_pos = np.arange(len(products))
    ax2.barh(y_pos, values, color=colors_pie, align='center')
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(products)
    ax2.invert_yaxis()  # labels read top-to-bottom
    ax2.set_xlabel('Unidades Vendidas')
    ax2.set_title('Top 5 Productos')
    
    plt.tight_layout()
    plt.savefig('viz_products.png', dpi=150)
    plt.close()

def create_pdf(filename):
    # Generar imágenes primero
    try:
        generate_mock_images()
    except Exception as e:
        print(f"Error generando imágenes: {e}")
    
    doc = SimpleDocTemplate(filename, pagesize=A4,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=50)
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=4))
    styles.add(ParagraphStyle(name='MainTitle', parent=styles['Heading1'], alignment=1, fontSize=24, spaceAfter=20, textColor=colors.HexColor(COLOR_PRIMARY)))
    styles.add(ParagraphStyle(name='SubTitle', parent=styles['Heading2'], alignment=1, fontSize=14, spaceAfter=30, textColor=colors.grey))
    styles.add(ParagraphStyle(name='ChapterTitle', parent=styles['Heading1'], fontSize=18, spaceBefore=20, spaceAfter=15, color=colors.HexColor('#1B2559')))
    styles.add(ParagraphStyle(name='SectionTitle', parent=styles['Heading2'], fontSize=14, spaceBefore=15, spaceAfter=10, color=colors.HexColor('#2B3674')))
    styles.add(ParagraphStyle(name='BodyTextCustom', parent=styles['BodyText'], fontSize=11, leading=14, spaceAfter=10))
    styles.add(ParagraphStyle(name='PriceTag', parent=styles['BodyText'], fontSize=12, leading=16, spaceAfter=6, textColor=colors.HexColor('#05CD99'), fontName='Helvetica-Bold'))

    story = []

    # --- PORTADA ---
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("Documentación Técnica y Valoración", styles['MainTitle']))
    story.append(Paragraph("Dashboard de Inteligencia de Negocios v2.0", styles['SubTitle']))
    story.append(Paragraph(f"Fecha: {datetime.now().strftime('%d de %B, %Y')}", styles['BodyTextCustom']))
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph("Este documento incluye:", styles['BodyTextCustom']))
    
    list_items = [
        "Visualizaciones del Dashboard (Simulación)",
        "Documentación Técnica de Funcionalidades",
        "Análisis de Valoración en Mercado Chileno"
    ]
    for item in list_items:
        story.append(Paragraph(f"• {item}", styles['BodyTextCustom']))
    
    story.append(PageBreak())

    # --- CAPÍTULO 1: VISUALIZACIÓN ---
    story.append(Paragraph("1. Visualización del Dashboard", styles['ChapterTitle']))
    story.append(Paragraph("A continuación se presentan capturas representativas de las principales funcionalidades analíticas del sistema.", styles['BodyTextCustom']))
    
    story.append(Paragraph("Panel de Control Principal (Resumen Ejecutivo)", styles['SectionTitle']))
    if os.path.exists('viz_kpis.png'):
        story.append(Image('viz_kpis.png', width=6*inch, height=1.5*inch))
    story.append(Paragraph("Indicadores clave de rendimiento (KPIs) en tiempo real con comparativas automáticas vs periodos anteriores.", styles['BodyTextCustom']))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Análisis de Ventas (Tendencias)", styles['SectionTitle']))
    if os.path.exists('viz_sales.png'):
        story.append(Image('viz_sales.png', width=6*inch, height=2.4*inch))
    story.append(Paragraph("Gráficos interactivos de ventas diarias con proyección y contraste 'Year over Year' (YoY) para detectar estacionalidad.", styles['BodyTextCustom']))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Distribución de Inventario", styles['SectionTitle']))
    if os.path.exists('viz_products.png'):
        story.append(Image('viz_products.png', width=6*inch, height=2.4*inch))
    story.append(Paragraph("Desglose del catálogo por categorías y ranking de productos más vendidos para optimización de stock.", styles['BodyTextCustom']))
    story.append(PageBreak())

    # --- CAPÍTULO 2: VALORACIÓN ---
    story.append(Paragraph("2. Valoración de Mercado (Chile 2025)", styles['ChapterTitle']))
    story.append(Paragraph("Análisis estimativo del costo de desarrollo de un software de inteligencia de negocios a medida en el mercado chileno actual.", styles['BodyTextCustom']))

    story.append(Paragraph("2.1 Desglose de Costos de Desarrollo", styles['SectionTitle']))
    story.append(Paragraph("El desarrollo de un dashboard personalizado que integre múltiples fuentes de datos (WooCommerce, Google Analytics, Facebook Ads) requiere perfiles especializados:", styles['BodyTextCustom']))

    # Tabla de Costos
    cost_data = [
        ['Fase / Actividad', 'Horas Est.', 'Valor Hora (UF)', 'Valor Total (CLP)'],
        ['Ingeniería de Datos (ETL)', '50 hrs', '2.0 UF', '$3.800.000'],
        ['Desarrollo Backend/API', '40 hrs', '2.0 UF', '$3.040.000'],
        ['Frontend / Visualización', '40 hrs', '1.8 UF', '$2.736.000'],
        ['Infraestructura & QA', '20 hrs', '1.8 UF', '$1.368.000'],
        ['Gestión de Proyecto', '15 hrs', '2.5 UF', '$1.425.000'],
        ['TOTAL ESTIMADO', '165 hrs', '-', '$12.369.000']
    ]
    
    t_costs = Table(cost_data, colWidths=[180, 60, 90, 100])
    t_costs.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1B2559')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (0,1), (0,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('GRID', (0,0), (-1,-1), 1, colors.grey),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#E0E5F2')),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
    ]))
    story.append(t_costs)
    story.append(Spacer(1, 8))
    story.append(Paragraph("* Valor UF referencial: $38.000 CLP. Tarifas de mercado para perfiles Senior/Semi-Senior.", styles['BodyTextCustom']))
    
    story.append(Paragraph("2.2 Valoración Comercial del Producto", styles['SectionTitle']))
    story.append(Paragraph("Considerando márgenes de agencia y licenciamiento, el valor comercial de una solución 'Lleve en Mano' de estas características oscila entre:", styles['BodyTextCustom']))
    
    story.append(Paragraph("Rango Conservador (Freelance): $4.500.000 - $6.000.000 CLP", styles['PriceTag']))
    story.append(Paragraph("Rango Mercado Agencia: $9.000.000 - $15.000.000 CLP", styles['PriceTag']))
    
    story.append(Paragraph("2.3 Costos Recurrentes (Mantención)", styles['SectionTitle']))
    story.append(Paragraph("Para garantizar la operatividad y actualización de conectores:", styles['BodyTextCustom']))
    story.append(Paragraph("• Hosting & Base de Datos: 2.0 - 4.0 UF / mes", styles['BodyTextCustom']))
    story.append(Paragraph("• Soporte & Actualizaciones: 5.0 - 10.0 UF / mes", styles['BodyTextCustom']))
    story.append(PageBreak())

    # --- CAPÍTULO 3: DOCUMENTACIÓN TÉCNICA ---
    # (Resumen de lo anterior)
    story.append(Paragraph("3. Resumen Funcional", styles['ChapterTitle']))
    story.append(Paragraph("Este dashboard resuelve problemáticas críticas de la gestión de comercio electrónico mediante la centralización de datos.", styles['BodyTextCustom']))
    
    features = [
        "Unificación de Data: Elimina la necesidad de revisar 3 plataformas distintas.",
        "Alertas de Inventario: Reduce quiebres de stock y sobre-stock.",
        "Georeferenciación: Identifica zonas de calor de ventas para focalizar marketing.",
        "Auditoría Fiscal: Facilita el cálculo de IVA y proyecciones de Renta."
    ]
    for feat in features:
        story.append(Paragraph(f"✔ {feat}", styles['BodyTextCustom']))

    doc.build(story)
    print(f"PDF generado: {os.path.abspath(filename)}")

if __name__ == "__main__":
    create_pdf("Informe_Valoracion_y_Dashboard.pdf")
