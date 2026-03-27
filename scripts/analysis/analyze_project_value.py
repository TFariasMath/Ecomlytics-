"""
Análisis Completo del Valor Monetario del Proyecto
Genera un reporte detallado de todo el revenue generado por Frutos Tayen
"""

import sqlite3
import pandas as pd
from datetime import datetime
import json

def format_currency(value):
    """Formatea valores monetarios en formato chileno"""
    return f"${value:,.0f}".replace(",", ".")

def analyze_project_value():
    """Realiza un análisis completo del valor monetario del proyecto"""
    
    print("=" * 80)
    print("💰 ANÁLISIS DE VALOR MONETARIO DEL PROYECTO - FRUTOS TAYEN")
    print("=" * 80)
    print(f"Fecha del análisis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Conectar a la base de datos
    db_path = 'data/woocommerce.db'
    conn = sqlite3.connect(db_path)
    
    try:
        # ========================================
        # 1. REVENUE TOTAL DEL PROYECTO
        # ========================================
        print("\n" + "=" * 80)
        print("📊 1. REVENUE TOTAL DEL PROYECTO")
        print("=" * 80)
        
        query_total = """
        SELECT 
            COUNT(DISTINCT order_id) as total_orders,
            SUM(total) as revenue_total,
            SUM(total_tax) as tax_total,
            SUM(shipping_total) as shipping_total,
            MIN(date_created) as fecha_primera_orden,
            MAX(date_created) as fecha_ultima_orden
        FROM wc_orders
        WHERE status IN ('completed', 'processing', 'on-hold')
        """
        
        df_total = pd.read_sql_query(query_total, conn)
        
        revenue_total = df_total['revenue_total'].iloc[0] or 0
        total_orders = df_total['total_orders'].iloc[0] or 0
        tax_total = df_total['tax_total'].iloc[0] or 0
        shipping_total = df_total['shipping_total'].iloc[0] or 0
        
        print(f"\n🎯 MÉTRICAS PRINCIPALES:")
        print(f"   • Revenue Total:        {format_currency(revenue_total)} CLP")
        print(f"   • Total de Órdenes:     {total_orders:,} órdenes")
        print(f"   • Impuestos Totales:    {format_currency(tax_total)} CLP")
        print(f"   • Envíos Totales:       {format_currency(shipping_total)} CLP")
        
        if total_orders > 0:
            aov = revenue_total / total_orders
            print(f"   • Ticket Promedio (AOV): {format_currency(aov)} CLP")
        
        fecha_primera = df_total['fecha_primera_orden'].iloc[0]
        fecha_ultima = df_total['fecha_ultima_orden'].iloc[0]
        print(f"\n📅 PERÍODO DE ANÁLISIS:")
        print(f"   • Primera orden: {fecha_primera}")
        print(f"   • Última orden:  {fecha_ultima}")
        
        # ========================================
        # 2. REVENUE POR AÑO
        # ========================================
        print("\n" + "=" * 80)
        print("📈 2. REVENUE POR AÑO")
        print("=" * 80)
        
        query_anual = """
        SELECT 
            strftime('%Y', date_created) as year,
            COUNT(DISTINCT order_id) as orders,
            SUM(total) as revenue,
            ROUND(AVG(total), 2) as avg_order_value
        FROM wc_orders
        WHERE status IN ('completed', 'processing', 'on-hold')
        GROUP BY year
        ORDER BY year
        """
        
        df_anual = pd.read_sql_query(query_anual, conn)
        
        for _, row in df_anual.iterrows():
            pct = (row['revenue'] / revenue_total * 100) if revenue_total > 0 else 0
            print(f"\n{row['year']}:")
            print(f"   • Revenue:    {format_currency(row['revenue'])} CLP ({pct:.1f}%)")
            print(f"   • Órdenes:    {int(row['orders']):,}")
            print(f"   • AOV:        {format_currency(row['avg_order_value'])} CLP")
        
        # ========================================
        # 3. REVENUE POR MES (ÚLTIMOS 12 MESES)
        # ========================================
        print("\n" + "=" * 80)
        print("📅 3. REVENUE POR MES (ÚLTIMOS 12 MESES)")
        print("=" * 80)
        
        query_mensual = """
        SELECT 
            strftime('%Y-%m', date_created) as month,
            COUNT(DISTINCT order_id) as orders,
            SUM(total) as revenue,
            ROUND(AVG(total), 2) as avg_order_value
        FROM wc_orders
        WHERE status IN ('completed', 'processing', 'on-hold')
            AND date_created >= date('now', '-12 months')
        GROUP BY month
        ORDER BY month DESC
        """
        
        df_mensual = pd.read_sql_query(query_mensual, conn)
        
        for _, row in df_mensual.iterrows():
            print(f"\n{row['month']}:")
            print(f"   • Revenue:    {format_currency(row['revenue'])} CLP")
            print(f"   • Órdenes:    {int(row['orders']):,}")
            print(f"   • AOV:        {format_currency(row['avg_order_value'])} CLP")
        
        # ========================================
        # 4. TOP 10 PRODUCTOS POR REVENUE
        # ========================================
        print("\n" + "=" * 80)
        print("🏆 4. TOP 10 PRODUCTOS POR REVENUE")
        print("=" * 80)
        
        query_productos = """
        SELECT 
            product_name,
            SUM(quantity) as units_sold,
            SUM(total) as revenue,
            COUNT(DISTINCT order_id) as num_orders
        FROM wc_order_items
        WHERE order_id IN (
            SELECT order_id FROM wc_orders 
            WHERE status IN ('completed', 'processing', 'on-hold')
        )
        GROUP BY product_name
        ORDER BY revenue DESC
        LIMIT 10
        """
        
        df_productos = pd.read_sql_query(query_productos, conn)
        
        for idx, row in df_productos.iterrows():
            pct = (row['revenue'] / revenue_total * 100) if revenue_total > 0 else 0
            print(f"\n{idx + 1}. {row['product_name']}")
            print(f"   • Revenue:       {format_currency(row['revenue'])} CLP ({pct:.1f}%)")
            print(f"   • Unidades:      {int(row['units_sold']):,}")
            print(f"   • Órdenes:       {int(row['num_orders']):,}")
        
        # ========================================
        # 5. REVENUE POR REGIÓN
        # ========================================
        print("\n" + "=" * 80)
        print("🗺️  5. REVENUE POR REGIÓN")
        print("=" * 80)
        
        query_regiones = """
        SELECT 
            COALESCE(billing_state, 'Sin Región') as region,
            COUNT(DISTINCT order_id) as orders,
            SUM(total) as revenue,
            ROUND(AVG(total), 2) as avg_order_value
        FROM wc_orders
        WHERE status IN ('completed', 'processing', 'on-hold')
        GROUP BY region
        ORDER BY revenue DESC
        LIMIT 15
        """
        
        df_regiones = pd.read_sql_query(query_regiones, conn)
        
        for _, row in df_regiones.iterrows():
            pct = (row['revenue'] / revenue_total * 100) if revenue_total > 0 else 0
            print(f"\n{row['region']}:")
            print(f"   • Revenue:    {format_currency(row['revenue'])} CLP ({pct:.1f}%)")
            print(f"   • Órdenes:    {int(row['orders']):,}")
            print(f"   • AOV:        {format_currency(row['avg_order_value'])} CLP")
        
        # ========================================
        # 6. ANÁLISIS DE CLIENTES
        # ========================================
        print("\n" + "=" * 80)
        print("👥 6. ANÁLISIS DE CLIENTES")
        print("=" * 80)
        
        query_clientes = """
        SELECT 
            COUNT(DISTINCT customer_id) as total_clientes,
            COUNT(DISTINCT CASE WHEN customer_id = 0 THEN order_id END) as guest_orders,
            COUNT(DISTINCT CASE WHEN customer_id > 0 THEN order_id END) as registered_orders
        FROM wc_orders
        WHERE status IN ('completed', 'processing', 'on-hold')
        """
        
        df_clientes = pd.read_sql_query(query_clientes, conn)
        
        total_clientes = df_clientes['total_clientes'].iloc[0]
        guest_orders = df_clientes['guest_orders'].iloc[0]
        registered_orders = df_clientes['registered_orders'].iloc[0]
        
        print(f"\n📊 DISTRIBUCIÓN DE CLIENTES:")
        print(f"   • Total Clientes Únicos:    {total_clientes:,}")
        print(f"   • Órdenes de Invitados:     {guest_orders:,} ({guest_orders/total_orders*100:.1f}%)")
        print(f"   • Órdenes Registradas:      {registered_orders:,} ({registered_orders/total_orders*100:.1f}%)")
        
        # Top clientes
        query_top_clientes = """
        SELECT 
            CASE 
                WHEN customer_id = 0 THEN 'Cliente Invitado (' || customer_email || ')'
                ELSE customer_name
            END as cliente,
            COUNT(DISTINCT order_id) as num_orders,
            SUM(total) as total_revenue,
            ROUND(AVG(total), 2) as avg_order_value
        FROM wc_orders
        WHERE status IN ('completed', 'processing', 'on-hold')
        GROUP BY customer_id, customer_email, customer_name
        ORDER BY total_revenue DESC
        LIMIT 10
        """
        
        df_top_clientes = pd.read_sql_query(query_top_clientes, conn)
        
        print(f"\n🌟 TOP 10 CLIENTES POR REVENUE:")
        for idx, row in df_top_clientes.iterrows():
            pct = (row['total_revenue'] / revenue_total * 100) if revenue_total > 0 else 0
            print(f"\n{idx + 1}. {row['cliente'][:50]}")
            print(f"   • Revenue:       {format_currency(row['total_revenue'])} CLP ({pct:.1f}%)")
            print(f"   • Órdenes:       {int(row['num_orders']):,}")
            print(f"   • AOV:           {format_currency(row['avg_order_value'])} CLP")
        
        # ========================================
        # 7. ANÁLISIS DE ESTADOS DE ORDEN
        # ========================================
        print("\n" + "=" * 80)
        print("📋 7. ANÁLISIS POR ESTADO DE ORDEN")
        print("=" * 80)
        
        query_estados = """
        SELECT 
            status,
            COUNT(DISTINCT order_id) as orders,
            SUM(total) as revenue
        FROM wc_orders
        GROUP BY status
        ORDER BY revenue DESC
        """
        
        df_estados = pd.read_sql_query(query_estados, conn)
        
        # Calcular revenue total incluyendo todos los estados
        revenue_todos_estados = df_estados['revenue'].sum()
        
        for _, row in df_estados.iterrows():
            pct = (row['revenue'] / revenue_todos_estados * 100) if revenue_todos_estados > 0 else 0
            print(f"\n{row['status']}:")
            print(f"   • Revenue:    {format_currency(row['revenue'])} CLP ({pct:.1f}%)")
            print(f"   • Órdenes:    {int(row['orders']):,}")
        
        # ========================================
        # 8. RESUMEN EJECUTIVO
        # ========================================
        print("\n" + "=" * 80)
        print("📊 8. RESUMEN EJECUTIVO")
        print("=" * 80)
        
        print(f"\n🎯 VALOR TOTAL DEL PROYECTO:")
        print(f"   ┌─────────────────────────────────────────────────┐")
        print(f"   │  REVENUE TOTAL: {format_currency(revenue_total):>28} CLP  │")
        print(f"   └─────────────────────────────────────────────────┘")
        
        print(f"\n📈 MÉTRICAS CLAVE:")
        print(f"   • Total de Órdenes:              {total_orders:>10,}")
        print(f"   • Ticket Promedio (AOV):         {format_currency(aov):>15} CLP")
        print(f"   • Clientes Únicos:               {total_clientes:>10,}")
        
        if total_orders > 0 and total_clientes > 0:
            orders_per_customer = total_orders / total_clientes
            clv = revenue_total / total_clientes
            print(f"   • Órdenes por Cliente:           {orders_per_customer:>15.2f}")
            print(f"   • Customer Lifetime Value (CLV): {format_currency(clv):>15} CLP")
        
        print("\n" + "=" * 80)
        print("✅ Análisis completado exitosamente")
        print("=" * 80)
        
        # Guardar resumen en JSON
        resumen = {
            "fecha_analisis": datetime.now().isoformat(),
            "revenue_total": float(revenue_total),
            "total_orders": int(total_orders),
            "aov": float(aov) if total_orders > 0 else 0,
            "total_clientes": int(total_clientes),
            "periodo": {
                "primera_orden": fecha_primera,
                "ultima_orden": fecha_ultima
            }
        }
        
        with open('data/project_value_summary.json', 'w', encoding='utf-8') as f:
            json.dump(resumen, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resumen guardado en: data/project_value_summary.json")
        
    except Exception as e:
        print(f"\n❌ Error durante el análisis: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        conn.close()

if __name__ == "__main__":
    analyze_project_value()
