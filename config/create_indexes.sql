-- ================================================
-- Script SQL para crear índices de optimización
-- ================================================

-- Índices para tabla wc_orders
-- ================================================
CREATE INDEX IF NOT EXISTS idx_orders_date ON wc_orders(date_only);
CREATE INDEX IF NOT EXISTS idx_orders_status ON wc_orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_date_status ON wc_orders(date_only, status);
CREATE INDEX IF NOT EXISTS idx_orders_id ON wc_orders(order_id);

-- Índices para tabla wc_order_items
-- ================================================
CREATE INDEX IF NOT EXISTS idx_items_order_id ON wc_order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_items_product_id ON wc_order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_items_product_name ON wc_order_items(product_name);

-- Índices para tabla ga4_channels
-- ================================================
CREATE INDEX IF NOT EXISTS idx_ga4_channels_date ON ga4_channels(Fecha);
CREATE INDEX IF NOT EXISTS idx_ga4_channels_canal ON ga4_channels(Canal);

-- Índices para tabla ga4_countries
-- ================================================
CREATE INDEX IF NOT EXISTS idx_ga4_countries_date ON ga4_countries(Fecha);
CREATE INDEX IF NOT EXISTS idx_ga4_countries_pais ON ga4_countries(Pais);

-- Índices para tabla ga4_pages
-- ================================================
CREATE INDEX IF NOT EXISTS idx_ga4_pages_date ON ga4_pages(Fecha);
CREATE INDEX IF NOT EXISTS idx_ga4_pages_pagina ON ga4_pages(Pagina);

-- Índices para tabla ga4_ecommerce
-- ================================================
CREATE INDEX IF NOT EXISTS idx_ga4_ecommerce_date ON ga4_ecommerce(Fecha);

-- Índices para tabla ga4_products
-- ================================================
CREATE INDEX IF NOT EXISTS idx_ga4_products_date ON ga4_products(Fecha);
CREATE INDEX IF NOT EXISTS idx_ga4_products_producto ON ga4_products(Producto);

-- Índices para tabla ga4_traffic_sources
-- ================================================
CREATE INDEX IF NOT EXISTS idx_ga4_traffic_date ON ga4_traffic_sources(Fecha);
CREATE INDEX IF NOT EXISTS idx_ga4_traffic_fuente ON ga4_traffic_sources(Fuente);
CREATE INDEX IF NOT EXISTS idx_ga4_traffic_medio ON ga4_traffic_sources(Medio);
