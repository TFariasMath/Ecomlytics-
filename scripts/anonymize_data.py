import sqlite3
import random
import os
import json
from pathlib import Path

# Configuración de Randomización
FIRST_NAMES = ["Diego", "Valentina", "Matías", "Javiera", "Nicolás", "Isidora", "Sebastián", "Antonia", "Felipe", "Camila", "Cristian", "Fernanda", "Gonzalo", "Ignacia", "Jose", "Loreto"]
LAST_NAMES = ["González", "Muñoz", "Rojas", "Díaz", "Pérez", "Soto", "Contreras", "Silva", "Martínez", "Sepúlveda", "Morales", "Rodríguez", "López", "Fuentes", "Hernández"]
DOMAINS = ["gmail.com", "yahoo.cl", "outlook.com", "icloud.com", "vtr.net"]

PRODUCTS = {
    "Electrónica": ["Audífonos Bluetooth Pro", "Reloj Inteligente V2", "Cargador Carga Rápida", "Parlante Portátil", "Tableta 10 pulgadas", "Mouse Gamer RGB", "Teclado Mecánico"],
    "Hogar": ["Cafetera Espresso", "Lámpara LED Escritorio", "Set de Cuchillos Cocina", "Humidificador Ultrasónico", "Mesa de Centro Roble", "Perchero Vintage", "Silla Ergonómica"],
    "Moda": ["Polera Algodón Orgánico", "Jeans Slim Fit", "Zapatillas Urbanas", "Chaqueta Cortaviento", "Bolso de Cuero Vegano", "Gorro de Lana", "Bufanda de Lino"],
    "Bienestar": ["Yoga Mat Premium", "Botella de Agua Inoxidable", "Masajeador Cervical", "Kit de Aceites Esenciales", "Pesas de 2kg", "Cuerda para Saltar"]
}

STREETS = ["Av. Providencia", "Alameda", "Grandes Avenidas", "Calle Larga", "Av. Vitacura", "Paseo Ahumada", "Viña del Mar 123", "Valparaíso 456"]

def anonymize_woocommerce(db_path):
    if not os.path.exists(db_path):
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Anonymize Customers
    cursor.execute("SELECT customer_id, first_name, last_name, email FROM wc_customers")
    rows = cursor.fetchall()
    
    for cid, old_fn, old_ln, old_email in rows:
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        email = f"{fn.lower()}.{ln.lower()}{random.randint(10,99)}@{random.choice(DOMAINS)}"
        
        # WooCommerce stores phone and address in 'billing' and 'shipping' JSON usually if extracted via API
        # We'll just set them to empty or simple dummy strings if they are plain text, 
        # or update them if they are JSON.
        dummy_billing = json.dumps({
            "first_name": fn, "last_name": ln, "company": "", 
            "address_1": f"{random.choice(STREETS)} #{random.randint(100, 999)}",
            "city": "Santiago", "state": "RM", "postcode": "1234567", "country": "CL",
            "email": email, "phone": f"+569{random.randint(10000000, 99999999)}"
        })
        
        cursor.execute("""
            UPDATE wc_customers 
            SET first_name=?, last_name=?, email=?, username=?, billing=?, shipping=?
            WHERE customer_id=?
        """, (fn, ln, email, f"user_{cid}", dummy_billing, dummy_billing, cid))
    
    # 2. Anonymize Products
    cursor.execute("SELECT id FROM wc_products")
    product_ids = [r[0] for r in cursor.fetchall()]
    all_prod_names = [p for cat in PRODUCTS.values() for p in cat]
    
    for pid in product_ids:
        new_name = random.choice(all_prod_names)
        cursor.execute("UPDATE wc_products SET name=?, description=?, short_description=? WHERE id=?", 
                      (new_name, f"Descripción de {new_name}", f"Short {new_name}", pid))
        
    # 3. Anonymize Order Items
    cursor.execute("SELECT id FROM wc_order_items")
    item_ids = [r[0] for r in cursor.fetchall()]
    for iid in item_ids:
        cursor.execute("UPDATE wc_order_items SET name=? WHERE id=?", (random.choice(all_prod_names), iid))
        
    conn.commit()
    conn.close()
    print(f"Anonymized {db_path}")

def anonymize_analytics(db_path):
    if not os.path.exists(db_path):
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    pages = ["/inicio", "/tienda", "/carrito", "/contacto", "/blog/articulo-1", "/productos/electronica"]
    titles = ["Inicio - Demo Store", "Tienda Online", "Tu Carrito", "Contáctanos", "Blog de Noticias", "Categoría Electrónica"]
    
    cursor.execute("SELECT rowid FROM ga4_pages")
    row_ids = [r[0] for r in cursor.fetchall()]
    
    for rid in row_ids:
        idx = random.randint(0, len(pages)-1)
        cursor.execute("UPDATE ga4_pages SET Pagina=?, Titulo=? WHERE rowid=?", (pages[idx], titles[idx], rid))
        
    conn.commit()
    conn.close()
    print(f"Anonymized {db_path}")

if __name__ == "__main__":
    anonymize_woocommerce("data/woocommerce.db")
    anonymize_analytics("data/analytics.db")
    
    summary_path = Path("data/project_value_summary.json")
    if summary_path.exists():
        with open(summary_path, 'r') as f:
            data = json.load(f)
        data["revenue_total"] = round(data["revenue_total"] * 0.85, -3) 
        data["total_clientes"] = len(FIRST_NAMES) * 2
        with open(summary_path, 'w') as f:
            json.dump(data, f, indent=2)
        print("Updated project_value_summary.json")
