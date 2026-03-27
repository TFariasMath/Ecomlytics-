"""
Order Tickets Service Module

Este módulo maneja los tickets de órdenes pendientes de contactar por WhatsApp.
Cada nueva orden crea un ticket pendiente que aparece en el dashboard.

Funcionalidades:
- Detección automática de nuevas órdenes sin ticket
- Generación de links WhatsApp click-to-chat
- Gestión de estado de tickets (pendiente/cerrado)
- Plantilla de mensaje configurable
"""

import sqlite3
import json
import os
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
WOOCOMMERCE_DB = DATA_DIR / 'woocommerce.db'
TICKET_CONFIG_FILE = DATA_DIR / 'ticket_config.json'


# ============================================
# DATABASE FUNCTIONS
# ============================================

def init_tickets_table() -> None:
    """
    Crea la tabla order_tickets si no existe.
    Se llama automáticamente al usar otras funciones.
    """
    conn = sqlite3.connect(str(WOOCOMMERCE_DB))
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER UNIQUE NOT NULL,
            order_number TEXT,
            customer_name TEXT,
            customer_phone TEXT,
            customer_email TEXT,
            order_total REAL,
            order_date DATETIME,
            products_summary TEXT,
            status TEXT DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            closed_at DATETIME,
            notes TEXT
        )
    """)
    
    conn.commit()
    conn.close()


def detect_new_orders() -> int:
    """
    Detecta órdenes que no tienen ticket y crea tickets pendientes.
    
    Returns:
        Número de nuevos tickets creados
    """
    init_tickets_table()
    
    conn = sqlite3.connect(str(WOOCOMMERCE_DB))
    cursor = conn.cursor()
    
    # Obtener órdenes de hoy y ayer que no tienen ticket
    # Solo estados válidos (procesando, completado, etc.)
    cursor.execute("""
        SELECT 
            o.order_id,
            o.order_id AS order_number,
            COALESCE(o.shipping_first_name || ' ' || o.shipping_last_name, 'Cliente') AS customer_name,
            COALESCE(o.billing_phone, '') AS customer_phone,
            '' AS customer_email,
            o.total,
            o.date_created
        FROM wc_orders o
        LEFT JOIN order_tickets t ON o.order_id = t.order_id
        WHERE t.order_id IS NULL
        AND o.status IN ('processing', 'completed', 'completoenviado', 'porsalir')
        AND o.date_created >= date('now', '-2 days')
        ORDER BY o.date_created DESC
    """)
    
    new_orders = cursor.fetchall()
    new_count = 0
    
    for order in new_orders:
        order_id, order_number, customer_name, phone, email, total, order_date = order
        
        # Obtener resumen de productos para esta orden
        cursor.execute("""
            SELECT product_name, quantity
            FROM wc_order_items
            WHERE order_id = ?
            LIMIT 5
        """, (order_id,))
        items = cursor.fetchall()
        products_summary = ", ".join([f"{qty}x {name[:30]}" for name, qty in items])
        
        # Insertar nuevo ticket
        try:
            cursor.execute("""
                INSERT INTO order_tickets 
                (order_id, order_number, customer_name, customer_phone, customer_email, 
                 order_total, order_date, products_summary, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending')
            """, (order_id, order_number, customer_name, phone, email, total, order_date, products_summary))
            new_count += 1
        except sqlite3.IntegrityError:
            # Ya existe ticket para esta orden
            pass
    
    conn.commit()
    conn.close()
    
    return new_count


def get_pending_tickets() -> List[Dict[str, Any]]:
    """
    Obtiene todos los tickets pendientes.
    
    Returns:
        Lista de diccionarios con información del ticket
    """
    init_tickets_table()
    
    conn = sqlite3.connect(str(WOOCOMMERCE_DB))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            id, order_id, order_number, customer_name, customer_phone,
            customer_email, order_total, order_date, products_summary,
            created_at
        FROM order_tickets
        WHERE status = 'pending'
        ORDER BY order_date DESC
    """)
    
    tickets = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return tickets


def close_ticket(order_id: int, notes: str = "") -> bool:
    """
    Marca un ticket como cerrado (mensaje enviado).
    
    Args:
        order_id: ID de la orden
        notes: Notas opcionales
        
    Returns:
        True si se cerró correctamente
    """
    conn = sqlite3.connect(str(WOOCOMMERCE_DB))
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE order_tickets
        SET status = 'closed',
            closed_at = datetime('now'),
            notes = ?
        WHERE order_id = ? AND status = 'pending'
    """, (notes, order_id))
    
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    
    return updated


def get_pending_count() -> int:
    """
    Obtiene el número de tickets pendientes.
    
    Returns:
        Número de tickets pendientes
    """
    init_tickets_table()
    
    conn = sqlite3.connect(str(WOOCOMMERCE_DB))
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM order_tickets WHERE status = 'pending'")
    count = cursor.fetchone()[0]
    conn.close()
    
    return count


# ============================================
# MESSAGE TEMPLATE FUNCTIONS
# ============================================

def get_default_template() -> str:
    """Retorna la plantilla de mensaje por defecto."""
    return (
        "Hola {nombre}, gracias por tu pedido #{orden}. "
        "Tu total es ${total}. "
        "Te contactamos para coordinar el envío. 🚚"
    )


def load_message_template() -> str:
    """
    Carga la plantilla de mensaje desde el archivo de configuración.
    
    Returns:
        Plantilla de mensaje
    """
    if TICKET_CONFIG_FILE.exists():
        try:
            with open(TICKET_CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('message_template', get_default_template())
        except (json.JSONDecodeError, IOError):
            pass
    
    return get_default_template()


def save_message_template(template: str) -> bool:
    """
    Guarda la plantilla de mensaje en el archivo de configuración.
    
    Args:
        template: Plantilla de mensaje
        
    Returns:
        True si se guardó correctamente
    """
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        config = {}
        if TICKET_CONFIG_FILE.exists():
            try:
                with open(TICKET_CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except Exception:
                pass
        
        config['message_template'] = template
        config['updated_at'] = datetime.now().isoformat()
        
        with open(TICKET_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        return True
    except IOError:
        return False


# ============================================
# WHATSAPP LINK GENERATOR
# ============================================

def format_phone_number(phone: str) -> str:
    """
    Formatea un número de teléfono para WhatsApp.
    Remueve espacios, guiones y agrega código de país si falta.
    
    Args:
        phone: Número de teléfono sin formato
        
    Returns:
        Número formateado para wa.me (solo dígitos con código país)
    """
    if not phone:
        return ""
    
    # Remover todo excepto dígitos y +
    cleaned = ''.join(c for c in phone if c.isdigit() or c == '+')
    
    # Si empieza con +, remover el +
    if cleaned.startswith('+'):
        cleaned = cleaned[1:]
    
    # Si es número chileno sin código país (9 dígitos empezando con 9)
    if len(cleaned) == 9 and cleaned.startswith('9'):
        cleaned = '56' + cleaned
    
    # Si tiene 8 dígitos (sin el 9 inicial para Chile)
    if len(cleaned) == 8:
        cleaned = '569' + cleaned
    
    return cleaned


def generate_whatsapp_link(ticket: Dict[str, Any], template: str = None) -> str:
    """
    Genera un link de WhatsApp click-to-chat para un ticket.
    
    Args:
        ticket: Diccionario con datos del ticket
        template: Plantilla de mensaje (opcional, usa guardada si no se pasa)
        
    Returns:
        URL de WhatsApp lista para abrir
    """
    if template is None:
        template = load_message_template()
    
    # Formatear número
    phone = format_phone_number(ticket.get('customer_phone', ''))
    
    if not phone:
        # Si no hay teléfono, retornar link vacío
        return ""
    
    # Reemplazar variables en la plantilla
    message = template.replace('{nombre}', ticket.get('customer_name', 'Cliente'))
    message = message.replace('{orden}', str(ticket.get('order_number', ticket.get('order_id', ''))))
    message = message.replace('{total}', f"{ticket.get('order_total', 0):,.0f}")
    message = message.replace('{productos}', ticket.get('products_summary', ''))
    message = message.replace('{fecha}', str(ticket.get('order_date', ''))[:10])
    
    # Codificar mensaje para URL
    encoded_message = urllib.parse.quote(message)
    
    # Generar link
    return f"https://wa.me/{phone}?text={encoded_message}"


def get_available_variables() -> List[Dict[str, str]]:
    """
    Retorna las variables disponibles para la plantilla.
    
    Returns:
        Lista de diccionarios con nombre y descripción
    """
    return [
        {'var': '{nombre}', 'desc': 'Nombre del cliente'},
        {'var': '{orden}', 'desc': 'Número de orden'},
        {'var': '{total}', 'desc': 'Total del pedido'},
        {'var': '{productos}', 'desc': 'Resumen de productos'},
        {'var': '{fecha}', 'desc': 'Fecha del pedido'},
    ]


# ============================================
# HELPER FUNCTIONS
# ============================================

def refresh_tickets() -> Dict[str, int]:
    """
    Detecta nuevas órdenes y retorna estadísticas.
    
    Returns:
        Diccionario con 'new_tickets' y 'total_pending'
    """
    new_count = detect_new_orders()
    pending_count = get_pending_count()
    
    return {
        'new_tickets': new_count,
        'total_pending': pending_count
    }
