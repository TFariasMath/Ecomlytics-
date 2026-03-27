"""
Demo Data Generator for Analytics Pipeline

Generates realistic fictional data for demonstration purposes:
- WooCommerce orders (500-700)
- Products (80-100)
- Customers (200-300)
- Google Analytics data
- Facebook metrics

All data is completely fictional and safe for public demonstrations.
"""

import sqlite3
import pandas as pd
import random
from datetime import datetime, timedelta
from pathlib import Path

# Seed for reproducibility
random.seed(42)

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / 'data'

# Demo configuration
DEMO_STORE_NAME = "Demo E-commerce Store"
# Set dates relative to today so they always show up in the dashboard by default
END_DATE = datetime.now()
START_DATE = END_DATE - timedelta(days=365)

# Product categories and names
PRODUCTS = {
    'Electronics': [
        ('Premium Laptop Pro', 189000),
        ('Wireless Headphones Elite', 85000),
        ('Smart Watch Ultra', 145000),
        ('Tablet Professional', 125000),
        ('Gaming Console', 175000),
        ('4K Smart TV', 195000),
        ('Bluetooth Speaker', 65000),
        ('Webcam HD Pro', 55000),
        ('Mechanical Keyboard', 75000),
        ('Ultra Mouse Gaming', 45000),
        ('Portable SSD 1TB', 95000),
        ('Wireless Charger', 35000),
        ('USB-C Hub Pro', 42000),
        ('Noise Cancelling Headphones', 115000),
        ('Action Camera 4K', 135000),
        ('Drone with Camera', 165000),
        ('VR Headset', 185000),
        ('Smart Home Hub', 78000),
        ('Security Camera System', 98000),
        ('Portable Battery Bank', 38000),
    ],
    'Home & Garden': [
        ('Designer Sofa Collection', 285000),
        ('Modern Coffee Table', 85000),
        ('Ergonomic Office Chair', 125000),
        ('Standing Desk Electric', 155000),
        ('King Size Bed Frame', 165000),
        ('Dining Table Set', 195000),
        ('Bookshelf Premium', 75000),
        ('Floor Lamp Modern', 55000),
        ('Area Rug Large', 95000),
        ('Wall Art Canvas Set', 45000),
        ('Garden Furniture Set', 215000),
        ('BBQ Grill Deluxe', 145000),
        ('Outdoor Umbrella', 65000),
        ('Patio Heater', 88000),
        ('Plant Collection Indoor', 42000),
        ('Storage Cabinet', 95000),
        ('Nightstand Pair', 68000),
        ('Dresser Modern', 115000),
        ('Mirror Full Length', 58000),
        ('Decorative Cushions', 32000),
        ('Throw Blanket Set', 38000),
        ('Kitchen Island Cart', 125000),
        ('Bar Stool Set', 98000),
        ('Coat Rack Stand', 45000),
        ('Magazine Holder', 28000),
    ],
    'Fashion': [
        ('Designer Jacket Premium', 145000),
        ('Leather Boots', 95000),
        ('Casual Sneakers', 65000),
        ('Formal Shoes', 85000),
        ('Designer Handbag', 125000),
        ('Luxury Watch', 285000),
        ('Sunglasses Collection', 75000),
        ('Winter Coat', 115000),
        ('Summer Dress', 55000),
        ('Denim Jeans Premium', 68000),
        ('Business Suit', 195000),
        ('Casual Shirt Set', 45000),
        ('Sports Jacket', 88000),
        ('Evening Gown', 165000),
        ('Designer Belt', 42000),
        ('Silk Scarf', 38000),
        ('Leather Wallet', 52000),
        ('Backpack Premium', 78000),
        ('Yoga Pants Set', 48000),
        ('Running Shoes', 72000),
    ],
    'Sports': [
        ('Fitness Equipment Bundle', 185000),
        ('Treadmill Professional', 295000),
        ('Exercise Bike', 165000),
        ('Yoga Mat Premium', 35000),
        ('Dumbbell Set Complete', 125000),
        ('Resistance Bands', 28000),
        ('Kettlebell Set', 85000),
        ('Pull-up Bar', 45000),
        ('Jump Rope Pro', 25000),
        ('Foam Roller', 32000),
        ('Sports Bag', 58000),
        ('Water Bottle Set', 22000),
        ('Gym Gloves', 28000),
        ('Fitness Tracker', 95000),
    ],
}

# Chilean cities and regions
CITIES = [
    ('Santiago', 'CL_329', 'Región Metropolitana'),
    ('Valparaíso', 'CL_408', 'Región de Valparaíso'),
    ('Concepción', 'CL_261', 'Región del Biobío'),
    ('La Serena', 'CL_387', 'Región de Coquimbo'),
    ('Temuco', 'CL_220', 'Región de La Araucanía'),
    ('Rancagua', 'CL_235', 'Región de O\'Higgins'),
    ('Talca', 'CL_350', 'Región del Maule'),
    ('Arica', 'CL_211', 'Región de Arica y Parinacota'),
    ('Puerto Montt', 'CL_313', 'Región de Los Lagos'),
    ('Chillán', 'CL_232', 'Región de Ñuble'),
]

# Sales patterns by month (multiplier)
SEASONAL_PATTERN = {
    1: 0.85, 2: 0.75, 3: 1.05, 4: 0.95,
    5: 1.10, 6: 1.15, 7: 1.22, 8: 1.18,
    9: 1.12, 10: 1.25, 11: 1.32, 12: 1.40
}


def generate_products():
    """Generate product catalog"""
    products = []
    product_id = 1000
    
    for category, items in PRODUCTS.items():
        for name, price in items:
            products.append({
                'product_id': product_id,
                'name': name,
                'sku': f'DEMO-{product_id}',
                'price': price,
                'regular_price': price,
                'sale_price': price * 0.9 if random.random() > 0.7 else 0,
                'status': 'publish',
                'categories': category,
                'stock_quantity': random.randint(5, 100),
                'stock_status': 'instock',
                'manage_stock': 1,
                'backorders': 'no',
                'backorders_allowed': 0,
                'low_stock_amount': 5,
                'sold_individually': 0,
                'weight': random.randint(100, 5000),
                'length': random.randint(10, 100),
                'width': random.randint(10, 100),
                'height': random.randint(5, 50),
                'total_sales': 0,  # Will update after orders
                'rating_count': random.randint(10, 150),
                'average_rating': round(random.uniform(3.5, 5.0), 1),
                'date_modified': datetime.now().isoformat()
            })
            product_id += 1
    
    return pd.DataFrame(products)


def generate_customers():
    """Generate customer database"""
    customers = []
    
    for i in range(1, 301):
        city, state, region = random.choice(CITIES)
        customers.append({
            'customer_id': 10000 + i,
            'email': f'demo{i}@example.com',
            'username': f'demo_user{i}',
            'first_name': f'Cliente',
            'last_name': f'Demo {i}',
            'role': 'customer',
            'date_created': (START_DATE + timedelta(days=random.randint(0, 365))).isoformat(),
            'date_modified': datetime.now().isoformat(),
            'billing_city': city,
            'billing_state': state,
            'billing_postcode': f'{random.randint(1000000, 9999999)}',
            'billing_country': 'CL',
            'billing_phone': f'+569{random.randint(10000000, 99999999)}',
            'orders_count': 0,  # Will update
            'total_spent': 0,  # Will update
            'avatar_url': ''
        })
    
    return pd.DataFrame(customers)


def generate_orders(products_df, customers_df):
    """Generate order history with realistic patterns"""
    orders = []
    order_items = []
    order_id = 50000
    
    # Total orders to generate: ~680
    target_orders = 680
    days = (END_DATE - START_DATE).days
    
    for day in range(days):
        current_date = START_DATE + timedelta(days=day)
        month = current_date.month
        
        # Apply seasonal pattern
        base_orders_per_day = target_orders / days
        daily_orders = int(base_orders_per_day * SEASONAL_PATTERN[month])
        
        # Weekend boost (20% more)
        if current_date.weekday() >= 5:
            daily_orders = int(daily_orders * 1.2)
        
        # Random variation
        daily_orders = max(1, daily_orders + random.randint(-1, 2))
        
        for _ in range(daily_orders):
            # Select random customer
            customer = customers_df.sample(1).iloc[0]
            
            # Order date with random time
            order_date = current_date + timedelta(
                hours=random.randint(8, 22),
                minutes=random.randint(0, 59)
            )
            
            # Select 1-4 products
            num_items = random.choices([1, 2, 3, 4], weights=[0.5, 0.3, 0.15, 0.05])[0]
            selected_products = products_df.sample(n=num_items)
            
            # Calculate totals
            subtotal = 0
            items_for_order = []
            
            for _, product in selected_products.iterrows():
                quantity = random.choices([1, 2, 3], weights=[0.7, 0.2, 0.1])[0]
                price = product['price']
                item_total = price * quantity
                subtotal += item_total
                
                items_for_order.append({
                    'order_id': order_id,
                    'product_id': product['product_id'],
                    'product_name': product['name'],
                    'sku': product['sku'],
                    'quantity': quantity,
                    'price': price,
                    'total': item_total,
                    'subtotal': item_total,
                    'subtotal_tax': item_total * 0.19,
                    'tax_class': 'standard',
                    'variation_id': 0,
                    'date_created': order_date.isoformat()
                })
            
            # Add shipping and tax
            shipping = random.choice([0, 3000, 5000, 8000])
            total_before_tax = subtotal + shipping
            tax = total_before_tax * 0.19
            total = total_before_tax + tax
            
            # Random status (mostly completed)
            status = random.choices(
                ['completed', 'processing', 'on-hold'],
                weights=[0.85, 0.10, 0.05]
            )[0]
            
            # Create order
            city, state, region = random.choice(CITIES)
            orders.append({
                'order_id': order_id,
                'date_created': order_date.isoformat(),
                'status': status,
                'total': total,
                'currency': 'CLP',
                'shipping_total': shipping,
                'discount_total': 0,
                'total_tax': tax,
                'cart_tax': tax,
                'shipping_tax': 0,
                'customer_id': customer['customer_id'],
                'customer_email': customer['email'],
                'customer_name': f"{customer['first_name']} {customer['last_name']}",
                'billing_company': '',
                'billing_address_1': f'Calle Demo {random.randint(100, 9999)}',
                'billing_address_2': f'Depto {random.randint(1, 999)}' if random.random() > 0.7 else '',
                'billing_city': city,
                'billing_state': state,
                'billing_postcode': f'{random.randint(1000000, 9999999)}',
                'billing_country': 'CL',
                'billing_phone': customer['billing_phone'],
                'shipping_first_name': customer['first_name'],
                'shipping_last_name': customer['last_name'],
                'shipping_address_1': f'Calle Demo {random.randint(100, 9999)}',
                'shipping_address_2': f'Depto {random.randint(1, 999)}' if random.random() > 0.7 else '',
                'shipping_city': city,
                'shipping_state': state,
                'shipping_postcode': f'{random.randint(1000000, 9999999)}',
                'shipping_country': 'CL',
                'payment_method': random.choice(['webpay', 'transbank', 'transferencia']),
                'payment_method_title': random.choice(['Webpay Plus', 'Transbank', 'Transferencia Bancaria']),
                'shipping_method': random.choice(['Envío estándar', 'Envío express', 'Retiro en tienda']),
                'customer_note': '',
                'date_completed': order_date.isoformat() if status == 'completed' else None,
                'date_paid': order_date.isoformat() if status in ['completed', 'processing'] else None,
                'date_modified': datetime.now().isoformat(),
                'coupons_used': ''
            })
            
            # Add order items
            order_items.extend(items_for_order)
            
            order_id += 1
    
    return pd.DataFrame(orders), pd.DataFrame(order_items)


def generate_analytics_data(orders_df):
    """Generate Google Analytics data correlated with orders"""
    analytics_data = {
        'sessions_by_channel': [],
        'users_by_country': [],
        'ecommerce_purchases': [],
        'pages': []
    }
    
    # Group orders by date
    orders_df['date_only'] = pd.to_datetime(orders_df['date_created']).dt.date
    daily_orders = orders_df.groupby('date_only')['order_id'].count()
    
    for date, order_count in daily_orders.items():
        # Sessions should be ~10-20x orders
        total_sessions = order_count * random.randint(10, 20)
        
        # Distribute across channels
        channels = {
            'Organic Search': 0.35,
            'Direct': 0.25,
            'Social': 0.20,
            'Paid Search': 0.15,
            'Referral': 0.05
        }
        
        for channel, pct in channels.items():
            sessions = int(total_sessions * pct)
            analytics_data['sessions_by_channel'].append({
                'Fecha': pd.Timestamp(date).isoformat(),
                'date_only': date,
                'Canal': channel,
                'Sesiones': sessions,
                'UsuariosActivos': int(sessions * 0.85)
            })
        
        # Country data (95% Chile)
        analytics_data['users_by_country'].append({
            'Fecha': pd.Timestamp(date).isoformat(),
            'date_only': date,
            'País': 'Chile',
            'UsuariosActivos': int(total_sessions * 0.95)
        })
        
        if random.random() > 0.7:  # Other countries occasionally
            analytics_data['users_by_country'].append({
                'Fecha': pd.Timestamp(date).isoformat(),
                'date_only': date,
                'País': random.choice(['Argentina', 'Perú', 'Colombia']),
                'UsuariosActivos': int(total_sessions * 0.05)
            })
        
        # Page data
        sample_pages = [
            ('/inicio', 'Inicio'),
            ('/productos', 'Productos'),
            ('/categoria/electronica', 'Electrónica'),
            ('/categoria/hogar', 'Hogar y Jardín'),
            ('/carrito', 'Carrito'),
            ('/pago', 'Finalizar Compra'),
            ('/contacto', 'Contacto'),
            ('/blog/tendencias-2025', 'Blog: Tendencias')
        ]
        for path, title in sample_pages:
            vistas = int(total_sessions * random.uniform(0.1, 0.4))
            if vistas > 0:
                analytics_data['pages'].append({
                    'Fecha': pd.Timestamp(date).isoformat(),
                    'Pagina': path,
                    'Titulo': title,
                    'Vistas': vistas,
                    'Usuarios': int(vistas * 0.8)
                })
    
    return analytics_data


def generate_facebook_data(orders_df):
    """Generate Facebook metrics"""
    # Create daily metrics for the last 30 days regardless of orders
    fb_data = []
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=90)
    
    current_date = start_date
    while current_date <= end_date:
        # Randomized growth
        base_fans = 5000 + (current_date - start_date).days * 2
        impressions = random.randint(1000, 5000)
        engagement = int(impressions * random.uniform(0.01, 0.05))
        
        fb_data.append({
            'date': current_date.isoformat(),
            'page_impressions': impressions,
            'page_engaged_users': engagement,
            'page_post_engagements': engagement,
            'page_fans': base_fans,
            'page_followers': base_fans + random.randint(100, 200)
        })
        current_date += timedelta(days=1)
    
    return pd.DataFrame(fb_data)


def generate_tickets(orders_df, order_items_df):
    """Generate pending tickets for recent orders"""
    recent_orders = orders_df[orders_df['status'].isin(['processing', 'completed', 'completoenviado', 'porsalir'])].tail(15)
    
    tickets = []
    for _, order in recent_orders.iterrows():
        order_id = order['order_id']
        
        # Get items summary
        items = order_items_df[order_items_df['order_id'] == order_id].head(3)
        products_summary = ", ".join([f"{int(row['quantity'])}x {row['product_name'][:30]}" for _, row in items.iterrows()])
        
        tickets.append({
            'order_id': order_id,
            'order_number': str(order_id),
            'customer_name': order['customer_name'],
            'customer_phone': order['billing_phone'],
            'customer_email': order['customer_email'],
            'order_total': order['total'],
            'order_date': order['date_created'],
            'products_summary': products_summary,
            'status': 'pending',
            'created_at': order['date_created']
        })
    
    return pd.DataFrame(tickets)


def populate_databases():
    """Main function to populate all databases"""
    print("🎬 Starting demo data generation...")
    
    # Generate data
    print("📦 Generating products...")
    products_df = generate_products()
    print(f"✅ Generated {len(products_df)} products")
    
    print("👥 Generating customers...")
    customers_df = generate_customers()
    print(f"✅ Generated {len(customers_df)} customers")
    
    print("🛒 Generating orders (this may take a minute)...")
    orders_df, order_items_df = generate_orders(products_df, customers_df)
    print(f"✅ Generated {len(orders_df)} orders with {len(order_items_df)} line items")
    
    print("📊 Generating analytics data...")
    analytics_data = generate_analytics_data(orders_df)
    print(f"✅ Generated {len(analytics_data['sessions_by_channel'])} GA session records")
    
    print("📱 Generating Facebook data...")
    fb_df = generate_facebook_data(orders_df)
    print(f"✅ Generated {len(fb_df)} Facebook records")
    
    print("🎫 Generating WhatsApp tickets...")
    tickets_df = generate_tickets(orders_df, order_items_df)
    print(f"✅ Generated {len(tickets_df)} pending tickets")
    
    # Add date_only columns
    orders_df['date_only'] = pd.to_datetime(orders_df['date_created']).dt.date
    
    # Populate databases
    print("\n💾 Populating databases...")
    
    # WooCommerce DB
    wc_db = DATA_DIR / 'woocommerce.db'
    if wc_db.exists():
        wc_db.unlink()
    
    conn_wc = sqlite3.connect(wc_db)
    products_df.to_sql('wc_products', conn_wc, index=False, if_exists='replace')
    customers_df.to_sql('wc_customers', conn_wc, index=False, if_exists='replace')
    orders_df.to_sql('wc_orders', conn_wc, index=False, if_exists='replace')
    order_items_df.to_sql('wc_order_items', conn_wc, index=False, if_exists='replace')
    
    # Add tickets table - correctly matching utils/order_tickets.py schema
    conn_wc.execute("""
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
    
    for _, row in tickets_df.iterrows():
        conn_wc.execute("""
            INSERT OR IGNORE INTO order_tickets 
            (order_id, order_number, customer_name, customer_phone, customer_email, 
             order_total, order_date, products_summary, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (row['order_id'], row['order_number'], row['customer_name'], 
              row['customer_phone'], row['customer_email'], row['order_total'], 
              row['order_date'], row['products_summary'], row['status'], row['created_at']))
    
    conn_wc.close()
    print(f"✅ WooCommerce DB populated with orders and tickets: {wc_db}")
    
    # Analytics DB
    analytics_db = DATA_DIR / 'analytics.db'
    if analytics_db.exists():
        analytics_db.unlink()
    
    conn_ga = sqlite3.connect(analytics_db)
    pd.DataFrame(analytics_data['sessions_by_channel']).to_sql(
        'ga_sessions_by_channel', conn_ga, index=False, if_exists='replace'
    )
    pd.DataFrame(analytics_data['users_by_country']).to_sql(
        'ga_users_by_country', conn_ga, index=False, if_exists='replace'
    )
    pd.DataFrame(analytics_data['pages']).to_sql(
        'ga4_pages', conn_ga, index=False, if_exists='replace'
    )
    conn_ga.close()
    print(f"✅ Analytics DB populated: {analytics_db}")
    
    # Facebook DB
    fb_db = DATA_DIR / 'facebook.db'
    if fb_db.exists():
        fb_db.unlink()
    
    conn_fb = sqlite3.connect(fb_db)
    fb_df.to_sql('fb_page_insights', conn_fb, index=False, if_exists='replace')
    conn_fb.close()
    print(f"✅ Facebook DB populated: {fb_db}")
    
    # Summary stats
    total_revenue = orders_df['total'].sum()
    avg_ticket = orders_df['total'].mean()
    
    print("\n" + "="*60)
    print("🎉 DEMO DATA GENERATION COMPLETE!")
    print("="*60)
    print(f"📊 Orders: {len(orders_df):,}")
    print(f"💰 Total Revenue: ${total_revenue:,.0f} CLP")
    print(f"🎫 Avg Ticket: ${avg_ticket:,.0f} CLP")
    print(f"📦 Products: {len(products_df)}")
    print(f"👥 Customers: {len(customers_df)}")
    print(f"📈 GA Records: {len(analytics_data['sessions_by_channel'])}")
    print(f"📱 FB Records: {len(fb_df)}")
    print("="*60)
    print("\n✅ You can now launch the dashboard with: LAUNCH.bat")
    print("📍 Dashboard will be available at: http://localhost:8501\n")


if __name__ == '__main__':
    populate_databases()
