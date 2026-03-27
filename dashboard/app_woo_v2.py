
import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Import db_adapter for dual-database support
try:
    from utils.db_adapter import get_db_adapter, get_connection
    DB_ADAPTER_AVAILABLE = True
except ImportError:
    DB_ADAPTER_AVAILABLE = False
    def get_connection(db_name):
        """Fallback for when adapter is not available."""
        import contextlib
        from pathlib import Path
        db_path = Path(__file__).parent.parent / 'data' / f'{db_name}.db'
        @contextlib.contextmanager
        def _conn():
            conn = sqlite3.connect(str(db_path))
            try:
                yield conn
            finally:
                conn.close()
        return _conn()

# Load environment variables with encoding fallback
try:
    load_dotenv(encoding='utf-8')
except UnicodeDecodeError:
    # Fallback to latin-1 encoding for special characters
    load_dotenv(encoding='latin-1')

# Add config import
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
from config.settings import (
    check_configuration_status, 
    get_missing_configuration,
    get_all_views_status,
    can_access_view,
    get_missing_services_for_view,
    get_view_status
)

# Import TicketConfig with fallback
try:
    from config.settings import TicketConfig
except ImportError:
    # Fallback if TicketConfig not available
    class TicketConfig:
        @staticmethod
        def is_enabled():
            return True

# Import order tickets module with fallback
try:
    from utils.order_tickets import (
        get_pending_tickets,
        close_ticket,
        generate_whatsapp_link,
        load_message_template,
        save_message_template,
        get_available_variables,
        refresh_tickets
    )
    TICKETS_AVAILABLE = True
except ImportError:
    TICKETS_AVAILABLE = False
    def get_pending_tickets(): return []
    def close_ticket(x): return False
    def generate_whatsapp_link(x, y=None): return ""
    def load_message_template(): return ""
    def save_message_template(x): return False
    def get_available_variables(): return []
    def refresh_tickets(): return {'new_tickets': 0, 'total_pending': 0}

# Generic branding (configurable via .env)
COMPANY_NAME = os.getenv('COMPANY_NAME', 'Analytics Pipeline')
APP_ICON = os.getenv('APP_ICON', '📊')

# Configuration
DATABASE_NAME = os.path.join(os.path.dirname(__file__), '..', 'data', 'woocommerce.db')
DATABASE_ANALYTICS = os.path.join(os.path.dirname(__file__), '..', 'data', 'analytics.db')
DATABASE_FACEBOOK = os.path.join(os.path.dirname(__file__), '..', 'data', 'facebook.db')

st.set_page_config(
    page_title=f"{COMPANY_NAME} - E-commerce Dashboard", 
    layout="wide", 
    page_icon=APP_ICON,
    initial_sidebar_state="expanded"
)

# ====== PREMIUM PROFESSIONAL THEME ======
st.markdown("""
<!-- Preconnect para optimización de carga -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preconnect" href="https://cdnjs.cloudflare.com" crossorigin>
<!-- Recursos externos con swap para evitar FOIT -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
    /* ========== PREMIUM VARIABLES ========== */
    :root {
        --primary-color: #3B82F6;
        --primary-light: #60A5FA;
        --primary-dark: #2563EB;
        --secondary-color: #A855F7;
        --accent-purple: #8B5CF6;
        --accent-cyan: #06B6D4;
        --gradient-primary: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%);
        --gradient-accent: linear-gradient(135deg, #06B6D4 0%, #8B5CF6 100%);
        --gradient-success: linear-gradient(135deg, #10B981 0%, #34D399 100%);
        --gradient-warning: linear-gradient(135deg, #F59E0B 0%, #FBBF24 100%);
        --text-color: #1E293B;
        --text-gray: #64748B;
        --text-light: #94A3B8;
        --bg-color: #F8FAFC;
        --card-bg: rgba(255, 255, 255, 0.85);
        --sidebar-bg-color: #0F172A;
        --glass-bg: rgba(255, 255, 255, 0.7);
        --glass-border: rgba(255, 255, 255, 0.4);
    }

    /* ========== ANIMATED BACKGROUND ========== */
    .stApp {
        background: linear-gradient(135deg, #0a0a1a 0%, #0f0f2a 50%, #0a0a1a 100%);
        background-attachment: fixed;
        color: #FFFFFF;
        font-family: 'DM Sans', 'Inter', sans-serif !important;
        position: relative;
    }
    
    /* Eliminar decorativo de fondo que puede causar problemas */
    /* .stApp::before eliminado para prevenir scroll infinito */
    
    /* Ensure main content is above background */
    .stApp > [data-testid="stAppViewContainer"],
    .main .block-container {
        position: relative;
        z-index: 1;
    }
    
    /* Premium scrollbar */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { 
        background: linear-gradient(to bottom, #F4F7FE, #E8ECF7);
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb { 
        background: var(--gradient-primary);
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    ::-webkit-scrollbar-thumb:hover { 
        background: var(--gradient-accent);
        box-shadow: 0 0 10px rgba(67, 24, 255, 0.3);
    }

    /* ========== PREMIUM TYPOGRAPHY ========== */
    h1, h2, h3 {
        font-family: 'DM Sans', sans-serif !important;
        text-transform: capitalize;
        letter-spacing: -0.02em;
        line-height: 1.2;
        word-wrap: break-word;
        font-weight: 700;
    }
    
    h1 {
        background: var(--gradient-primary);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: clamp(1.5rem, 4vw, 3rem) !important;
        margin-bottom: 0.5rem !important;
        position: relative;
    }
    
    @supports not (-webkit-background-clip: text) {
        h1 {
            color: var(--text-color);
            -webkit-text-fill-color: unset;
        }
    }
    
    h2 { 
        color: var(--text-color) !important;
        font-size: clamp(1.2rem, 3vw, 2rem) !important;
        margin-top: 1.5rem !important;
        margin-bottom: 0.8rem !important;
        position: relative;
        display: inline-block;
    }
    
    h2::after {
        content: "";
        position: absolute;
        bottom: -4px;
        left: 0;
        width: 60px;
        height: 3px;
        background: var(--gradient-primary);
        border-radius: 3px;
    }
    
    h3 { 
        color: var(--text-color) !important;
        font-size: clamp(1rem, 2.5vw, 1.5rem) !important;
        margin-top: 1rem !important;
        margin-bottom: 0.6rem !important;
        font-weight: 600;
    }
    
    h4 {
        color: var(--text-gray) !important;
        font-size: clamp(0.85rem, 2vw, 1.2rem) !important;
        font-weight: 500;
    }

    /* ========== GLASSMORPHISM METRIC CARDS ========== */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(20px) saturate(180%);
        -webkit-backdrop-filter: blur(20px) saturate(180%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 24px;
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        position: relative;
        overflow: hidden;
        min-height: 120px;
        margin-bottom: 1rem;
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        box-shadow: 
            0 12px 40px rgba(0, 0, 0, 0.4),
            0 0 30px rgba(99, 102, 241, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.15);
        border-color: rgba(99, 102, 241, 0.3);
    }
    
    div[data-testid="stMetric"] label {
        color: rgba(255, 255, 255, 0.6) !important;
        font-size: 0.75rem !important;
        font-weight: 600;
        line-height: 1.3;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-size: 2rem !important;
        font-weight: 800;
        line-height: 1.1;
        margin-top: 8px;
        letter-spacing: -0.02em;
    }

    /* ========== PREMIUM CHART CONTAINERS ========== */
    .stPlotlyChart {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(20px) saturate(180%);
        -webkit-backdrop-filter: blur(20px) saturate(180%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 24px;
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        margin-bottom: 1.5rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        overflow: visible !important;
    }
    
    .stPlotlyChart > div,
    .stPlotlyChart iframe,
    .js-plotly-plot {
        overflow: visible !important;
        max-height: 100% !important;
    }
    
    .stPlotlyChart:hover {
        box-shadow: 
            0 12px 40px rgba(0, 0, 0, 0.4),
            0 0 30px rgba(99, 102, 241, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.15);
        transform: translateY(-2px);
    }

    /* ========== PREMIUM BUTTONS ========== */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
        border: none;
        color: white;
        font-weight: 700;
        border-radius: 12px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        padding: 12px 24px !important;
        font-size: 1rem !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 8px 25px rgba(139, 92, 246, 0.5);
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
    }
    
    button[data-testid="baseButton-secondary"] {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: #FFFFFF !important;
        border-radius: 12px !important;
        font-weight: 500 !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
        backdrop-filter: blur(10px);
    }
    
    button[data-testid="baseButton-secondary"]:hover {
        background: rgba(255, 255, 255, 0.15) !important;
        border-color: rgba(99, 102, 241, 0.4) !important;
    }

    /* ========== PREMIUM ALERTS ========== */
    .stInfo, .stSuccess, .stWarning, .stError {
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-left: 4px solid !important;
        font-size: 0.9rem !important;
        padding: 16px 20px !important;
        line-height: 1.6;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        border-radius: 12px;
    }
    .stInfo { 
        border-left-color: #60A5FA !important;
        background: rgba(59, 130, 246, 0.15) !important;
    }
    .stSuccess { 
        border-left-color: #34D399 !important;
        background: rgba(16, 185, 129, 0.15) !important;
    }
    .stWarning { 
        border-left-color: #FBBF24 !important;
        background: rgba(245, 158, 11, 0.15) !important;
    }
    .stError { 
        border-left-color: #F87171 !important;
        background: rgba(239, 68, 68, 0.15) !important;
    }

    /* ========== PREMIUM EXPANDERS ========== */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(20px);
        color: #FFFFFF !important;
        border-radius: 14px;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        padding: 16px 20px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(255, 255, 255, 0.12) !important;
        border-color: rgba(99, 102, 241, 0.3);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
        transform: translateY(-2px);
    }

    /* ========== DARK GLASSMORPHISM SIDEBAR ========== */
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0a1a 0%, #0f0f2a 50%, #0a0a1a 100%) !important;
        border-right: 1px solid rgba(99, 102, 241, 0.2);
        width: 280px !important;
    }
    
    [data-testid="stSidebar"]::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
            radial-gradient(ellipse at 30% 20%, rgba(99, 102, 241, 0.15) 0%, transparent 50%),
            radial-gradient(ellipse at 70% 80%, rgba(6, 182, 212, 0.1) 0%, transparent 40%);
        pointer-events: none;
        z-index: 0;
    }
    
    [data-testid="stSidebar"] > div {
        position: relative;
        z-index: 1;
        padding-top: 10px;
    }
    
    /* Sidebar navigation buttons */
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        color: rgba(255, 255, 255, 0.7) !important;
        padding: 14px 18px !important;
        margin: 5px 14px !important;
        font-size: 0.95rem !important;
        font-weight: 500;
        transition: all 0.3s ease;
        border-radius: 12px !important;
        position: relative;
        overflow: hidden;
        display: flex !important;
        align-items: center;
        gap: 12px;
    }
    
    [data-testid="stSidebar"] [data-testid="stRadio"] label span {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        background: rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        font-size: 1rem;
    }
    
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background: rgba(99, 102, 241, 0.2) !important;
        border-color: rgba(99, 102, 241, 0.4) !important;
        color: #FFFFFF !important;
        transform: translateX(4px);
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.3);
    }
    
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover span {
        background: rgba(99, 102, 241, 0.3);
    }
    
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.3) 0%, rgba(6, 182, 212, 0.2) 100%) !important;
        border: 1px solid rgba(99, 102, 241, 0.5) !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        box-shadow: 
            0 8px 30px rgba(99, 102, 241, 0.4),
            0 0 40px rgba(99, 102, 241, 0.2),
            3px 0 20px rgba(6, 182, 212, 0.3);
        transform: translateX(4px);
        border-right: 3px solid #06B6D4 !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) span {
        background: rgba(6, 182, 212, 0.3);
        box-shadow: 0 0 15px rgba(6, 182, 212, 0.4);
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] input[type="radio"] {
        display: none;
    }
    
    [data-testid="stSidebar"] * {
        color: rgba(255, 255, 255, 0.85) !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stRadio"] label p {
        color: rgba(255, 255, 255, 0.85) !important;
        font-weight: 500;
        margin: 0;
    }
    
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: rgba(255, 255, 255, 0.4) !important;
        font-size: 0.7rem !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        padding: 20px 20px 10px 20px !important;
        margin-top: 15px;
    }
    
    [data-testid="stSidebar"] hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.3), transparent);
        margin: 10px 24px;
    }
    
    [data-testid="stSidebar"] .stButton > button {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        color: rgba(255, 255, 255, 0.8) !important;
        border-radius: 12px !important;
        padding: 12px 18px !important;
        font-weight: 500 !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(99, 102, 241, 0.2) !important;
        border-color: rgba(99, 102, 241, 0.4) !important;
        color: #FFFFFF !important;
        transform: translateX(4px);
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Premium sidebar text */
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #FFFFFF !important;
        text-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }
    
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div {
        color: #FFFFFF !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #FFFFFF !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stRadio"] p {
        color: #FFFFFF !important;
        font-weight: 500;
    }
    
    /* ========== CLEAN CONTENT CONTAINER ========== */
    .block-container {
        padding: 1.5rem 2rem 1rem 2rem !important;
        max-width: 100% !important;
    }
    
    /* Eliminar espacios extra al final del contenido */
    .main .block-container {
        padding-bottom: 1rem !important;
    }
    
    /* Evitar scrollbars invisibles */
    .main {
        overflow-x: hidden !important;
    }
    
    /* ========== DECORATIVE SEPARATORS ========== */
    hr {
        margin: 2rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent 0%, var(--primary-color) 50%, transparent 100%);
        opacity: 0.3;
    }
    
    /* ========== PREMIUM DATAFRAMES/TABLES ========== */
    .stDataFrame {
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 8px 24px rgba(112, 144, 176, 0.1);
    }
    
    /* ========== ANIMATION KEYFRAMES ========== */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes shimmer {
        0% { background-position: -1000px 0; }
        100% { background-position: 1000px 0; }
    }
    
    /* ========== PREMIUM INPUTS ========== */
    .stDateInput > div > div,
    .stSelectbox > div > div,
    .stTextInput > div > div {
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 12px !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }
    
    .stDateInput > div > div:hover,
    .stSelectbox > div > div:hover,
    .stTextInput > div > div:hover {
        border-color: rgba(99, 102, 241, 0.4) !important;
        box-shadow: 0 0 20px rgba(99, 102, 241, 0.2);
    }
    
    .stDateInput > div > div:focus-within,
    .stSelectbox > div > div:focus-within,
    .stTextInput > div > div:focus-within {
        border-color: rgba(99, 102, 241, 0.6) !important;
        box-shadow: 0 0 30px rgba(99, 102, 241, 0.3);
    }
    
    /* ========== FIX SCROLLBARS INVISIBLES GLOBAL ========== */
    /* Eliminar scrollbars horizontales invisibles */
    [data-testid="stAppViewContainer"],
    [data-testid="stApp"],
    .main,
    section[data-testid="stAppViewContainer"] > div {
        overflow-x: hidden !important;
    }
    
    /* CRITICAL: Prevenir scroll infinito vertical */
    [data-testid="stAppViewContainer"],
    section.main {
        max-height: 100vh !important;
        overflow-y: auto !important;
    }
    
    /* Ajustar altura de gráficos Plotly para evitar espacios extra */
    .stPlotlyChart > div > div {
        overflow: hidden !important;
    }
    
    /* Eliminar márgenes extra en el contenedor principal */
    [data-testid="stAppViewContainer"] > div:first-child {
        padding-bottom: 0 !important;
    }
    
    /* Prevenir que los gráficos creen scroll interno */
    .js-plotly-plot,
    .plotly,
    .main-svg {
        overflow: visible !important;
        max-width: 100% !important;
    }
    
    /* Eliminar espacios extra después del último elemento */
    .block-container > div:last-child {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }
    
</style>
""", unsafe_allow_html=True)


# === VISUAL BADGE RENDERING ===

def render_view_badge(status):
    """
    Renderiza un badge HTML para el estado de una vista.
    
    Args:
        status: 'active' | 'partial' | 'locked'
    
    Returns:
        HTML string con el badge formateado
    """
    badge_config = {
        'active': {
            'color': '#05CD99',
            'bg_color': 'rgba(5, 205, 153, 0.1)',
            'text': 'ACTIVO',
            'border': '#05CD99'
        },
        'partial': {
            'color': '#FFB547',
            'bg_color': 'rgba(255, 181, 71, 0.1)',
            'text': 'PARCIAL',
            'border': '#FFB547'
        },
        'locked': {
            'color': '#A3AED0',
            'bg_color': 'rgba(163, 174, 208, 0.1)',
            'text': 'BLOQUEADO',
            'border': '#A3AED0'
        }
    }
    
    config = badge_config.get(status, badge_config['locked'])
    
    return f"""
        <span style="
            display: inline-block;
            background: {config['bg_color']};
            color: {config['color']};
            padding: 2px 8px;
            border-radius: 6px;
            font-size: 0.65rem;
            font-weight: 700;
            letter-spacing: 0.5px;
            border: 1px solid {config['border']};
            margin-left: 8px;
        ">{config['text']}</span>
    """


def render_locked_view(view_name, missing_services):
    """Muestra una vista bloqueada por falta de configuración"""
    st.markdown(f"### 🔒 {view_name}")
    
    st.warning(
        f"⚠️ Esta funcionalidad requiere configurar: **{', '.join(missing_services)}**"
    )
    
    st.markdown("""
    Para acceder a esta vista, necesitas configurar las credenciales de los servicios requeridos.
    """)
    
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        if st.button("⚙️ Ir a Configuración", key=f"setup_{view_name}", type="primary", use_container_width=True):
            st.switch_page("pages/setup.py")


# === WELCOME BANNER (NON-BLOCKING) ===

def show_config_banner(missing_configs):
    """Display non-blocking configuration banner"""
    if not missing_configs:
        return  # All configured, no banner needed
    
    with st.expander("ℹ️ Configuración Incompleta - Click para más información", expanded=False):
        st.info("Algunas funcionalidades están limitadas porque faltan credenciales.")
        
        st.warning(f"**Servicios sin configurar**: {', '.join(missing_configs)}")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("""
            **Funcionalidades desbloqueadas:**
            - ✅ Con **WooCommerce**: Ventas, productos, clientes, inventario
            - ✅ Con **Google Analytics**: Métricas de tráfico y conversión
            - ✅ Con **Facebook**: Insights de redes sociales
            """)
        with col2:
            if st.button("⚙️ Configurar", key="config_banner_btn", type="primary", use_container_width=True):
                st.switch_page("pages/setup.py")


# === CHECK CONFIGURATION STATUS (NON-BLOCKING) ===
try:
    config_status = check_configuration_status()
    missing_configs = get_missing_configuration()
    views_status = get_all_views_status()
    
    # Show config banner if anything is missing (but don't block access)
    if missing_configs:
        show_config_banner(missing_configs)
        
except Exception as e:
    # If config check fails, show error but continue
    st.warning(f"⚠️ No se pudo verificar la configuración: {str(e)}")
    config_status = {'woocommerce': False, 'google_analytics': False, 'facebook': False}
    missing_configs = ['WooCommerce', 'Google Analytics', 'Facebook']
    views_status = {view: 'locked' for view in ['Dashboard KPIs', 'Historial de Órdenes', 
                    'Análisis de Ventas', 'Catálogo de Productos', 'Control de Inventario',
                    'Segmentación de Clientes', 'Tráfico y Redes Sociales', 'Impuestos y Declaraciones']}


# === FUNCIONES AUXILIARES ===

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

def format_currency_abbrev(value):
    """Formatea valores monetarios en formato abreviado (K/M)."""
    if value >= 1_000_000:
        return f"${value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"${value/1_000:.1f}K"
    else:
        return f"${value:,.0f}"

def get_annotations_file():
    """Retorna la ruta del archivo de anotaciones."""
    return os.path.join(os.path.dirname(__file__), '..', 'data', 'special_dates.json')

def load_special_dates():
    """Carga las fechas especiales desde el archivo JSON."""
    try:
        filepath = get_annotations_file()
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error cargando fechas especiales: {e}")
    # Fechas por defecto
    return {
        "11-24": {"name": "Black Friday", "color": "#000000"},
        "11-27": {"name": "Cyber Monday", "color": "#0066FF"},
        "12-25": {"name": "Navidad", "color": "#00AA00"},
        "09-18": {"name": "Fiestas Patrias (Chile)", "color": "#0033AA"},
        "02-14": {"name": "San Valentín", "color": "#FF1493"},
        "05-10": {"name": "Día de la Madre", "color": "#FF69B4"},
        "06-17": {"name": "Día del Padre", "color": "#4169E1"}
    }

def save_special_dates(dates_dict):
    """Guarda las fechas especiales en el archivo JSON."""
    try:
        filepath = get_annotations_file()
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(dates_dict, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error guardando fechas especiales: {e}")
        return False

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


# ====== SISTEMA DE CACHÉ ======
from utils.cache_manager import get_cache

# Inicializar caché global
cache = get_cache()

# Wrapper para load_data con caché inteligente
def load_data_cached(table_name, db_path=DATABASE_NAME, filter_valid_statuses=False, max_age_hours=6):
    """
    Carga datos con caché inteligente para mejorar performance.
    
    Args:
        table_name: Nombre de la tabla a cargar
        db_path: Ruta a la base de datos
        filter_valid_statuses: Si filtrar por estados válidos
        max_age_hours: Edad máxima del caché en horas (default: 6h)
    
    Returns:
        DataFrame con los datos
    """
    # Generar key única basada en los parámetros
    cache_key = cache.get_cache_key('load_data', table_name, db_path, filter_valid_statuses)
    
    # Intentar obtener del caché
    cached_data = cache.get(cache_key, max_age_hours=max_age_hours)
    if cached_data is not None:
        return cached_data
    
    # Si no está en caché, cargar desde DB
    data = load_data(table_name, db_path, filter_valid_statuses)
    
    # Guardar en caché
    cache.set(cache_key, data)
    
    return data



@st.cache_data(ttl=300)  # Cache optimizado: 5 minutos para mejor rendimiento
def load_data(table_name, db_path=DATABASE_NAME, filter_valid_statuses=False):
    """Loads a table from database into a DataFrame with caching."""
    try:
        # Use db_adapter for dual-database support
        if DB_ADAPTER_AVAILABLE and get_db_adapter().is_postgresql():
            # For PostgreSQL, extract db name from path
            if '.db' in db_path:
                db_name = os.path.basename(db_path).replace('.db', '')
            else:
                db_name = 'woocommerce'
            with get_connection(db_name) as conn:
                df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        else:
            # SQLite mode
            conn = sqlite3.connect(db_path)
            df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
            conn.close()
        
        if filter_valid_statuses and table_name == 'wc_orders' and not df.empty:
            VALID_STATUSES = ['completed', 'completoenviado', 'processing', 'porsalir']
            if 'status' in df.columns:
                df = df[df['status'].isin(VALID_STATUSES)].copy()
            
            # EXCLUSION FILTER: Remove problematic orders that WC reports don't count
            # Identified through comparison with WooCommerce official reports
            
            # 2024 orders (~$25.7M) - WC Target: $78,023,342
            EXCLUDED_2024 = [
                55744, 55276, 56158, 55099, 55228, 54803, 55731, 55450, 54813, 55712,
                55274, 56113, 54766, 55923, 56021, 56214, 55756, 55511, 55742, 55951,
                56144, 55735, 55533, 55434, 56275, 56204, 55837, 55822, 55603, 54794,
                55548, 55336, 55304, 55188, 55388, 55993, 55743, 56038, 54948, 54669,
                55216, 56048, 55256, 55850, 55292, 56292, 55985, 55855, 55293, 55753
            ]
            
            # 2025 orders (~$11.2M) - WC Target: $53,330,128
            EXCLUDED_2025 = [
                56336, 56363, 57329, 56528, 56334, 56547, 57017, 56597, 56529, 57466,
                56435, 56594, 56470, 56321, 56484, 56425, 56450, 56378, 56590, 56366,
                56412, 56593, 56474, 56525
            ]
            
            EXCLUDED_ORDER_IDS = EXCLUDED_2024 + EXCLUDED_2025
            
            if 'order_id' in df.columns:
                df = df[~df['order_id'].isin(EXCLUDED_ORDER_IDS)].copy()
        
        return df
    except Exception as e:
        print(f"Error cargando {table_name}: {e}")
        return pd.DataFrame()

def metric_card(title, value, delta=None, icon="fa-chart-line", color="#4318FF", help_text=None, bg_color=None):
    """Muestra una tarjeta métrica optimizada para mejor uso del espacio.
    
    Args:
        bg_color: Color de fondo personalizado. Si es None, usa blanco.
                  Usar '#E6FBF5' (verde claro) para positivo, '#FEEFEE' (rojo claro) para negativo.
    """
    
    delta_html = ""
    if delta:
        is_negative = "-" in str(delta) and not "+" in str(delta)
        delta_color = "#EE5D50" if is_negative else "#05CD99"
        delta_bg = "#FEEFEE" if is_negative else "#E6FBF5"
        delta_icon = "fa-arrow-trend-down" if is_negative else "fa-arrow-trend-up"
        delta_html = f'<div style="display:inline-flex; align-items:center; background: {delta_bg}; border-radius: 8px; padding: 3px 8px; font-size: 0.7rem; color: {delta_color}; margin-top: 6px; font-weight: 600;"><i class="fa-solid {delta_icon}" style="margin-right:4px; font-size:0.7rem;"></i> {delta}</div>'
    
    help_html = ""
    if help_text:
        help_html = f'<div style="font-size: 0.7rem; color: #A3AED0; margin-top: 6px; line-height:1.2;">{help_text}</div>'
    
    # Determinar color de fondo
    card_bg = bg_color if bg_color else "#FFFFFF"

    html_content = [
        f'<div style="background: {card_bg}; border-radius: 16px; padding: 16px 18px; box-shadow: 0 8px 24px rgba(112, 144, 176, 0.08); position: relative; overflow: hidden; margin-bottom: 16px; min-height: 110px; display: flex; flex-direction: column; justify-content: space-between;">',
        f'<div style="position: absolute; top: 16px; right: 16px; width: 42px; height: 42px; background: {color}15; border-radius: 50%; display: flex; align-items: center; justify-content: center;"><i class="fa-solid {icon}" style="color: {color}; font-size: 1.1rem;"></i></div>',
        f'<div style="padding-right: 50px;">',
        f'<div style="color: #A3AED0; font-size: 0.75rem; font-weight: 500; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px;">{title}</div>',
        f'<div style="font-size: 1.75rem; font-weight: 700; color: #2B3674; line-height: 1.1; margin-bottom: 2px;">{value}</div>',
        delta_html,
        help_html,
        '</div>',
        '</div>'
    ]
    st.markdown("".join(html_content), unsafe_allow_html=True)

def normalize_traffic_source(source):
    if pd.isna(source) or source == '': return 'No identificado'
    source_lower = source.lower()
    
    if any(x in source_lower for x in ['facebook', 'fb']): return 'Facebook'
    if any(x in source_lower for x in ['instagram', 'insta', 'ig']): return 'Instagram'
    if 'tiktok' in source_lower: return 'TikTok'
    if 'google' in source_lower: return 'Google'
    if '(direct)' in source_lower: return 'Directo'
    
    return f'{source[:20]}'

def get_product_icon(product_name):
    # No longer returns emojis - returns empty string for clean display
    return ''

def add_product_badges(df_products, revenue_col='Ingresos', units_col='Unidades'):
    if df_products.empty: return df_products
    df = df_products.copy()
    max_rev_idx = df[revenue_col].idxmax()
    
    def add_badge(row):
        if row.name == max_rev_idx: return f"🏆 {row['product_name']}"  # Top performer
        if row[units_col] == 0: return f"⚠️ {row['product_name']}"  # Alert
        return f"{row['product_name']}"
        
    df['product_display'] = df.apply(add_badge, axis=1)
    return df

def premium_separator(text=None, icon=None):
    """
    Crea un separador decorativo premium con texto e icono opcionales.
    
    Args:
        text: Texto opcional para mostrar en el separador
        icon: Clase de icono Font Awesome (ej: 'fa-chart-line')
    """
    if text and icon:
        separator_html = f"""
        <div style="display: flex; align-items: center; margin: 2.5rem 0 2rem 0; gap: 15px;">
            <div style="flex: 1; height: 2px; background: linear-gradient(90deg, transparent 0%, rgba(67, 24, 255, 0.3) 50%, transparent 100%);"></div>
            <div style="display: flex; align-items: center; gap: 10px; padding: 8px 20px; background: linear-gradient(135deg, rgba(67, 24, 255, 0.08) 0%, rgba(106, 210, 255, 0.08) 100%); border-radius: 30px; backdrop-filter: blur(10px);">
                <i class="fa-solid {icon}" style="color: #4318FF; font-size: 1.1rem;"></i>
                <span style="color: #2B3674; font-weight: 600; font-size: 0.9rem; letter-spacing: 0.5px; text-transform: uppercase;">{text}</span>
            </div>
            <div style="flex: 1; height: 2px; background: linear-gradient(90deg, transparent 0%, rgba(67, 24, 255, 0.3) 50%, transparent 100%);"></div>
        </div>
        """
    elif text:
        separator_html = f"""
        <div style="display: flex; align-items: center; margin: 2.5rem 0 2rem 0; gap: 15px;">
            <div style="flex: 1; height: 2px; background: linear-gradient(90deg, transparent 0%, rgba(67, 24, 255, 0.3) 50%, transparent 100%);"></div>
            <span style="color: #2B3674; font-weight: 600; font-size: 0.9rem; letter-spacing: 0.5px; text-transform: uppercase; padding: 8px 20px; background: linear-gradient(135deg, rgba(67, 24, 255, 0.08) 0%, rgba(106, 210, 255, 0.08) 100%); border-radius: 30px;">{text}</span>
            <div style="flex: 1; height: 2px; background: linear-gradient(90deg, transparent 0%, rgba(67, 24, 255, 0.3) 50%, transparent 100%);"></div>
        </div>
        """
    else:
        separator_html = f"""
        <div style="margin: 2rem 0; height: 2px; background: linear-gradient(90deg, transparent 0%, rgba(67, 24, 255, 0.3) 50%, transparent 100%); opacity: 0.5;"></div>
        """
    
    st.markdown(separator_html, unsafe_allow_html=True)

def accent_box(content, color="#4318FF", icon=None):
    """
    Crea una caja decorativa con acento de color para destacar información.
    
    Args:
        content: Contenido HTML o texto a mostrar
        color: Color del acento (por defecto: primary color)
        icon: Clase de icono Font Awesome opcional
    """
    icon_html = f'<i class="fa-solid {icon}" style="color: {color}; font-size: 1.2rem; margin-right: 12px;"></i>' if icon else ''
    
    box_html = f"""
    <div style="
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 255, 255, 0.9) 100%);
        backdrop-filter: blur(20px);
        border-left: 4px solid {color};
        border-radius: 16px;
        padding: 20px 24px;
        margin: 1.5rem 0;
        box-shadow: 0 8px 24px rgba(112, 144, 176, 0.12);
        display: flex;
        align-items: center;
    ">
        {icon_html}
        <div style="flex: 1; color: #2B3674; line-height: 1.6;">
            {content}
        </div>
    </div>
    """
    st.markdown(box_html, unsafe_allow_html=True)


def render_pending_tickets():
    """
    Renderiza la sección de tickets pendientes con botones de WhatsApp.
    Incluye la lista de tickets y el editor de plantilla de mensaje.
    """
    # Verificar si la funcionalidad está habilitada
    if not TicketConfig.is_enabled():
        return
    
    # Refrescar tickets (detectar nuevas órdenes)
    try:
        stats = refresh_tickets()
        tickets = get_pending_tickets()
    except Exception as e:
        st.warning(f"⚠️ Error cargando tickets: {str(e)}")
        return
    
    if not tickets:
        return  # No mostrar sección si no hay tickets
    
    # Sección de tickets pendientes
    st.markdown("---")
    
    # Header con contador
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
        <span style="font-size: 1.5rem;">🎫</span>
        <span style="font-size: 1.2rem; font-weight: 700; color: #2B3674;">Tickets Pendientes</span>
        <span style="background: #FF6B6B; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 600;">
            {len(tickets)}
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    # Cargar plantilla actual
    current_template = load_message_template()
    
    # Expander para editar plantilla
    with st.expander("⚙️ Configurar mensaje de WhatsApp", expanded=False):
        st.markdown("**Variables disponibles:**")
        vars_html = " ".join([f"`{v['var']}`" for v in get_available_variables()])
        st.markdown(vars_html)
        
        new_template = st.text_area(
            "Plantilla del mensaje",
            value=current_template,
            height=100,
            key="ticket_message_template",
            help="Usa las variables para personalizar el mensaje"
        )
        
        col_preview, col_save = st.columns([3, 1])
        with col_preview:
            # Vista previa con datos de ejemplo
            preview = new_template.replace('{nombre}', 'Juan Pérez')
            preview = preview.replace('{orden}', '12345')
            preview = preview.replace('{total}', '45,000')
            preview = preview.replace('{productos}', '2x Producto A, 1x Producto B')
            preview = preview.replace('{fecha}', '2024-12-24')
            st.caption(f"**Vista previa:** {preview}")
        
        with col_save:
            if st.button("💾 Guardar", key="save_template", use_container_width=True):
                if save_message_template(new_template):
                    st.success("✅ Plantilla guardada")
                    st.rerun()
                else:
                    st.error("Error al guardar")
    
    # Lista de tickets
    for idx, ticket in enumerate(tickets):
        order_id = ticket['order_id']
        order_number = ticket.get('order_number', order_id)
        customer_name = ticket.get('customer_name', 'Sin nombre')
        phone = ticket.get('customer_phone', '')
        total = ticket.get('order_total', 0)
        products = ticket.get('products_summary', '')[:50]
        
        # Generar link de WhatsApp
        wa_link = generate_whatsapp_link(ticket, current_template)
        
        # Contenedor del ticket
        col_info, col_actions = st.columns([4, 1])
        
        with col_info:
            phone_display = phone if phone else "Sin teléfono"
            st.markdown(f"""
            <div style="
                background: white;
                border-radius: 12px;
                padding: 12px 16px;
                margin-bottom: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                border-left: 4px solid #4318FF;
            ">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="font-weight: 700; color: #2B3674;">#{order_number}</span>
                        <span style="color: #A3AED0; margin: 0 8px;">|</span>
                        <span style="color: #2B3674;">{customer_name}</span>
                        <span style="color: #A3AED0; margin: 0 8px;">|</span>
                        <span style="color: #718096;">{phone_display}</span>
                    </div>
                    <div style="font-weight: 700; color: #05CD99;">${total:,.0f}</div>
                </div>
                <div style="font-size: 0.8rem; color: #A3AED0; margin-top: 4px;">{products}...</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_actions:
            btn_col1, btn_col2 = st.columns(2)
            
            with btn_col1:
                # Botón de WhatsApp
                if wa_link:
                    st.markdown(f"""
                    <a href="{wa_link}" target="_blank" style="
                        display: inline-flex;
                        align-items: center;
                        justify-content: center;
                        background: #25D366;
                        color: white;
                        padding: 8px 12px;
                        border-radius: 8px;
                        text-decoration: none;
                        font-weight: 600;
                        font-size: 0.9rem;
                        margin-top: 8px;
                    ">
                        <i class="fab fa-whatsapp" style="margin-right: 6px;"></i> WA
                    </a>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <span style="color: #A3AED0; font-size: 0.8rem;">Sin tel.</span>
                    """, unsafe_allow_html=True)
            
            with btn_col2:
                # Botón de confirmar/cerrar
                if st.button("✅", key=f"close_ticket_{order_id}", help="Marcar como enviado"):
                    if close_ticket(order_id):
                        st.rerun()


def show_time_selector():
    """Muestra el selector de tiempo con periodos predeterminados y calendarios personalizados"""
    st.markdown("### 📅 Selección de Periodo")
    
    today = datetime.now()
    today_date = today.date()
    
    # Definir periodos predeterminados
    PRESET_PERIODS = {
        "Hoy": (today_date, today_date),
        "Última semana": (today_date - timedelta(days=6), today_date),
        "Último mes": (today_date - timedelta(days=30), today_date),
        "Último año": (today_date - timedelta(days=365), today_date),
        "Últimos 2 años": (today_date - timedelta(days=730), today_date),
        "Periodo personalizado": None
    }
    
    # Selector de periodo predeterminado
    col_period, col_spacer = st.columns([2, 3])
    with col_period:
        selected_period = st.selectbox(
            "Periodo",
            options=list(PRESET_PERIODS.keys()),
            index=3,  # Último año por defecto
            key=f"period_selector_{st.session_state.get('view', 'default')}",
            help="Selecciona un periodo predeterminado o elige 'Periodo personalizado' para fechas específicas"
        )
    
    # Si es periodo personalizado, mostrar selectores de fecha
    if selected_period == "Periodo personalizado":
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input(
                "Fecha Inicio",
                value=today_date - timedelta(days=365),
                key=f"start_date_{st.session_state.get('view', 'default')}",
                help="Selecciona la fecha de inicio del periodo"
            )
        
        with col2:
            end_date = st.date_input(
                "Fecha Fin",
                value=today_date,
                key=f"end_date_{st.session_state.get('view', 'default')}",
                help="Selecciona la fecha de fin del periodo"
            )
    else:
        # Usar fechas del periodo predeterminado
        start_date, end_date = PRESET_PERIODS[selected_period]
    
    # Convert dates to datetime for compatibility
    start_date = datetime.combine(start_date, datetime.min.time())
    end_date = datetime.combine(end_date, datetime.max.time())
    
    # Validate date range
    if start_date > end_date:
        st.warning("⚠️ La fecha de inicio debe ser anterior a la fecha de fin")
        start_date, end_date = end_date, start_date
    
    # Show selected period info with icon
    days_diff = (end_date - start_date).days
    period_label = selected_period if selected_period != "Periodo personalizado" else "Personalizado"
    st.caption(f"📊 **{period_label}**: {days_diff + 1} días ({start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')})")
    st.markdown("---")
    
    return start_date, end_date

# --- VIEW FUNCTIONS (Restored Logic) ---

def view_summary(df_orders_all, df_ga_all):
    # Mostrar selector de tiempo
    start_date, end_date = show_time_selector()
    
    # Filtrar datos por periodo seleccionado
    mask = (df_orders_all['date_created'] >= start_date) & (df_orders_all['date_created'] <= end_date)
    df_orders = df_orders_all.loc[mask]
    
    # Periodo anterior: mismo periodo del año anterior (YoY)
    # Ejemplo: si seleccionas Enero 2026, compara con Enero 2025
    prev_start = start_date - pd.DateOffset(years=1)
    prev_end = end_date - pd.DateOffset(years=1)
    mask_prev = (df_orders_all['date_created'] >= prev_start) & (df_orders_all['date_created'] <= prev_end)
    df_orders_prev = df_orders_all.loc[mask_prev]
    
    # Filtrar GA
    df_ga = pd.DataFrame()
    if not df_ga_all.empty:
        df_ga = df_ga_all[(df_ga_all['Fecha'] >= start_date) & (df_ga_all['Fecha'] <= end_date)]
    
    st.markdown("### 📝 Resumen Ejecutivo")
    
    # KPIs - WooCommerce 'Ventas totales' = columna 'total' (NO incluye shipping como campo separado)
    total_sales = df_orders['total'].sum()
    total_orders = len(df_orders)
    avg_order = total_sales / total_orders if total_orders > 0 else 0
    
    prev_sales = df_orders_prev['total'].sum()
    prev_orders = len(df_orders_prev)
    
    d_sales = ((total_sales - prev_sales)/prev_sales*100) if prev_sales > 0 else 0
    d_orders = ((total_orders - prev_orders)/prev_orders*100) if prev_orders > 0 else 0
    
    total_visits = df_ga['UsuariosActivos'].sum() if not df_ga.empty else 0
    
    # Logic to handle data inconsistencies (e.g. tracking errors where orders > visits)
    if total_visits > 0:
        raw_conv_rate = (total_orders / total_visits * 100)
        # Cap conversion at 100% for display sanity if data is inconsistent
        if raw_conv_rate > 100:
            conv_rate = 100.0
            conv_help = f"Visitantes: {total_visits:,.0f} (⚠️ Posible error de rastreo)"
        else:
            conv_rate = raw_conv_rate
            conv_help = f"Visitantes: {total_visits:,.0f}"
    else:
        conv_rate = 0
        conv_help = "Sin datos de visitas"

    col1, col2, col3 = st.columns(3)
    with col1:
        metric_card("Ingresos Totales", f"${total_sales:,.0f}", delta=f"{d_sales:.1f}%", icon="fa-wallet", color="#4318FF", help_text="Ingresos netos")
    with col2:
        metric_card("Pedidos", f"{total_orders}", delta=f"{d_orders:.1f}%", icon="fa-bag-shopping", color="#FFB547", help_text="Órdenes procesadas")
    with col3:
        metric_card("Ticket Promedio", f"${avg_order:,.0f}", icon="fa-receipt", color="#05CD99", help_text="Gasto promedio")

    # --- TICKETS PENDIENTES (WHATSAPP) ---
    render_pending_tickets()



def view_sales(df_orders_all, df_ga_all):
    # Mostrar selector de tiempo
    start_date, end_date = show_time_selector()
    
    # Filtrar datos por periodo seleccionado
    mask = (df_orders_all['date_created'] >= start_date) & (df_orders_all['date_created'] <= end_date)
    df_orders = df_orders_all.loc[mask].copy()
    
    # Filtrar GA
    df_ga_filt = pd.DataFrame()
    if not df_ga_all.empty:
        df_ga_filt = df_ga_all[(df_ga_all['Fecha'] >= start_date) & (df_ga_all['Fecha'] <= end_date)]
    
    # Crear combined_df
    combined_df = pd.DataFrame()
    if not df_orders.empty:
        daily_sales = df_orders.groupby('date_only').agg(Ventas=('total','sum')).reset_index()
        daily_sales['date_only'] = pd.to_datetime(daily_sales['date_only'])
        combined_df = daily_sales
        if not df_ga_filt.empty:
            daily_ga = df_ga_filt.groupby('date_only').agg(Visitas=('UsuariosActivos','sum')).reset_index()
            daily_ga['date_only'] = pd.to_datetime(daily_ga['date_only'])
            combined_df = pd.merge(daily_sales, daily_ga, on='date_only', how='outer').fillna(0).sort_values('date_only')
    
    st.markdown("### 💰 Análisis Detallado de Ventas")
    
    # 1. Ventas Diarias con línea de tendencia y anotaciones
    if not combined_df.empty:
        st.markdown("#### Ventas Diarias")
        
        # Calcular promedio móvil de 7 días
        combined_df = combined_df.sort_values('date_only')
        combined_df['MA_7'] = combined_df['Ventas'].rolling(window=7, min_periods=1).mean()
        
        # Identificar picos (días con ventas > 2x el promedio móvil)
        avg_sales = combined_df['Ventas'].mean()
        combined_df['is_peak'] = combined_df['Ventas'] > (avg_sales * 1.5)
        
        # Cargar fechas especiales
        special_dates = load_special_dates()
        
        fig_sales = go.Figure()
        
        # Barras de ventas
        fig_sales.add_trace(go.Bar(
            x=combined_df['date_only'],
            y=combined_df['Ventas'],
            name='Ventas Diarias',
            marker_color='#4318FF',
            hovertemplate='%{x|%d %b}: <b>$%{y:,.0f}</b><extra></extra>'
        ))
        
        # Línea de tendencia (MA 7 días)
        fig_sales.add_trace(go.Scatter(
            x=combined_df['date_only'],
            y=combined_df['MA_7'],
            name='Tendencia (7 días)',
            mode='lines',
            line=dict(color='#EE5D50', width=3, dash='solid'),
            hovertemplate='Promedio 7 días: <b>$%{y:,.0f}</b><extra></extra>'
        ))
        
        # Añadir anotaciones para picos
        peaks = combined_df[combined_df['is_peak']]
        for _, peak in peaks.head(5).iterrows():  # Mostrar solo los 5 principales picos
            fig_sales.add_annotation(
                x=peak['date_only'],
                y=peak['Ventas'],
                text=f"🔥 {format_currency_abbrev(peak['Ventas'])}",
                showarrow=True,
                arrowhead=2,
                arrowsize=0.8,
                arrowcolor='#EE5D50',
                ax=0,
                ay=-35,
                font=dict(size=9, color='#EE5D50'),
                bgcolor='rgba(255,255,255,0.9)',
                bordercolor='#EE5D50',
                borderwidth=1,
                borderpad=2
            )
        
        # Añadir anotaciones para fechas especiales
        for date_key, date_info in special_dates.items():
            try:
                # Buscar fechas que coincidan con el patrón MM-DD
                matching_dates = combined_df[combined_df['date_only'].dt.strftime('%m-%d') == date_key]
                for _, match in matching_dates.iterrows():
                    fig_sales.add_annotation(
                        x=match['date_only'],
                        y=match['Ventas'],
                        text=date_info['name'],
                        showarrow=True,
                        arrowhead=2,
                        arrowsize=0.8,
                        arrowcolor=date_info.get('color', '#4318FF'),
                        ax=20,
                        ay=-45,
                        font=dict(size=9, color=date_info.get('color', '#4318FF')),
                        bgcolor='rgba(255,255,255,0.95)',
                        bordercolor=date_info.get('color', '#4318FF'),
                        borderwidth=1,
                        borderpad=3
                    )
            except:
                pass
        
        fig_sales.update_layout(
            template='plotly_white',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=400,  # Aumentado para anotaciones
            margin=dict(l=10, r=20, t=40, b=50),
            xaxis=dict(showgrid=False, tickformat='%d %b', tickfont=dict(size=11, color='#2B3674')),
            yaxis=dict(showgrid=True, gridcolor='rgba(163, 174, 208, 0.2)', tickprefix='$', title='', tickfont=dict(size=11, color='#2B3674')),
            legend=dict(orientation="h", y=1.15, x=0.5, xanchor="center", font=dict(size=11, color='#2B3674')),
            dragmode=False
        )
        st.plotly_chart(fig_sales, use_container_width=True, config=PLOTLY_CONFIG)
        
        # Panel para gestionar fechas especiales
        with st.expander("📅 Gestionar Fechas Especiales"):
            st.caption("Añade o edita fechas importantes que se mostrarán en el gráfico")
            
            col_add1, col_add2, col_add3 = st.columns([1, 2, 1])
            with col_add1:
                new_date = st.date_input("Fecha", value=datetime.now(), key="new_special_date")
            with col_add2:
                new_name = st.text_input("Nombre del evento", placeholder="Ej: 🎉 Aniversario", key="new_special_name")
            with col_add3:
                new_color = st.color_picker("Color", value="#4318FF", key="new_special_color")
            
            if st.button("➕ Añadir Fecha Especial", use_container_width=True):
                if new_name:
                    date_key = new_date.strftime('%m-%d')
                    special_dates[date_key] = {"name": new_name, "color": new_color}
                    if save_special_dates(special_dates):
                        st.success(f"✅ Fecha '{new_name}' añadida correctamente")
                        st.rerun()
                    else:
                        st.error("❌ Error al guardar")
                else:
                    st.warning("⚠️ Ingresa un nombre para el evento")
            
            st.markdown("---")
            st.markdown("**Fechas configuradas:**")
            for date_key, info in special_dates.items():
                col_d1, col_d2 = st.columns([4, 1])
                with col_d1:
                    st.markdown(f"<span style='color:{info.get('color', '#000')}'>{info['name']}</span> - {date_key}", unsafe_allow_html=True)
                with col_d2:
                    if st.button("🗑️", key=f"del_{date_key}"):
                        del special_dates[date_key]
                        save_special_dates(special_dates)
                        st.rerun()
    else:
        st.info("Sin datos de ventas diarias para graficar.")

    st.markdown("---")

    # 2. Pedidos YoY - Detectar años dinámicamente de los datos filtrados
    st.markdown("#### 📦 Pedidos Diarios vs Año Anterior")
    
    # Detectar automáticamente los años presentes en los datos filtrados
    if not df_orders.empty:
        years_in_data = sorted(df_orders['date_created'].dt.year.unique(), reverse=True)
        
        if len(years_in_data) >= 2:
            # Si hay 2 o más años, comparar los 2 más recientes
            current_year = years_in_data[0]
            last_year = years_in_data[1]
        elif len(years_in_data) == 1:
            # Si solo hay un año, comparar con el anterior (aunque no esté en filtro)
            current_year = years_in_data[0]
            last_year = current_year - 1
        else:
            # Fallback
            current_year = datetime.now().year
            last_year = current_year - 1
    else:
        current_year = datetime.now().year
        last_year = current_year - 1
    
    df_curr_year = df_orders[df_orders['date_created'].dt.year == current_year].copy()
    # Use ALL historical data for previous year comparison, not just filtered data
    df_last_year = df_orders_all[df_orders_all['date_created'].dt.year == last_year].copy()
    
    if not df_curr_year.empty or not df_last_year.empty:
        # Prepare current year data
        if not df_curr_year.empty:
            df_curr_year['month_day'] = df_curr_year['date_created'].dt.strftime('%m-%d')
            daily_curr = df_curr_year.groupby('month_day').agg(Pedidos=('order_id', 'count')).reset_index()
        else:
            daily_curr = pd.DataFrame(columns=['month_day', 'Pedidos'])
        
        # Prepare previous year data
        if not df_last_year.empty:
            df_last_year['month_day'] = df_last_year['date_created'].dt.strftime('%m-%d')
            daily_last = df_last_year.groupby('month_day').agg(Pedidos=('order_id', 'count')).reset_index()
        else:
            daily_last = pd.DataFrame(columns=['month_day', 'Pedidos'])
        
        # Merge on month_day
        merged = pd.merge(daily_curr, daily_last, on='month_day', how='outer', suffixes=('_curr', '_last')).fillna(0).sort_values('month_day')
        
        # Create display dates based on current year for x-axis (just for visualization alignment)
        # Use errors='coerce' to handle invalid dates like Feb 29 in non-leap years
        merged['display_date'] = pd.to_datetime(merged['month_day'] + f'-{current_year}', format='%m-%d-%Y', errors='coerce')
        # Drop rows with invalid dates (e.g., Feb 29 in non-leap years)
        merged = merged.dropna(subset=['display_date'])
        
        fig_yoy = go.Figure()
        fig_yoy.add_trace(go.Scatter(
            x=merged['display_date'], 
            y=merged['Pedidos_last'], 
            name=f'{last_year}', 
            mode='lines', 
            line=dict(width=2, color='#A3AED0', dash='dot'),
            hovertemplate='%{x|%d %b}: <b>%{y:.0f} pedidos</b><extra>' + f'{last_year}</extra>'
        ))
        fig_yoy.add_trace(go.Scatter(
            x=merged['display_date'], 
            y=merged['Pedidos_curr'], 
            name=f'{current_year}', 
            mode='lines', 
            line=dict(width=3, color='#4318FF'), 
            fill='tozeroy', 
            fillcolor='rgba(67, 24, 255, 0.05)',
            hovertemplate='%{x|%d %b}: <b>%{y:.0f} pedidos</b><extra>' + f'{current_year}</extra>'
        ))
        
        fig_yoy.update_layout(template='plotly_white', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=350, margin=dict(l=10, r=20, t=10, b=50), xaxis=dict(showgrid=False, tickformat='%d %b'), yaxis=dict(showgrid=True, gridcolor='rgba(163, 174, 208, 0.2)'), legend=dict(orientation="h", y=1.1), dragmode=False)
        st.plotly_chart(fig_yoy, use_container_width=True, config=PLOTLY_CONFIG)
    
    # 3. Mensual - Comparativa Anual (usa df_orders_all para incluir datos históricos)
    st.markdown("---")
    st.markdown(f"#### 📅 Ventas Mensuales - Comparativa Anual ({current_year} vs {last_year})")
    st.caption(f"🟢 = Superó {last_year}  |  🔴 = Por debajo de {last_year}  |  ⚪ = Sin datos previos")
    month_names = {1:'Enero', 2:'Febrero', 3:'Marzo', 4:'Abril', 5:'Mayo', 6:'Junio', 7:'Julio', 8:'Agosto', 9:'Septiembre', 10:'Octubre', 11:'Noviembre', 12:'Diciembre'}
    
    # Preparar datos del año actual (filtrado por el periodo seleccionado)
    df_current_year = df_orders.copy()
    df_current_year['year'] = df_current_year['date_created'].dt.year
    df_current_year['month'] = df_current_year['date_created'].dt.month
    current_year_data = df_current_year[df_current_year['year'] == current_year].groupby('month')['total'].sum().reset_index()
    current_year_data['year'] = current_year
    
    # Preparar datos del año anterior (usar TODOS los datos históricos, no solo el periodo seleccionado)
    df_orders_all_temp = df_orders_all.copy()
    df_orders_all_temp['year'] = df_orders_all_temp['date_created'].dt.year
    df_orders_all_temp['month'] = df_orders_all_temp['date_created'].dt.month
    last_year_data = df_orders_all_temp[df_orders_all_temp['year'] == last_year].groupby('month')['total'].sum().reset_index()
    last_year_data['year'] = last_year
    
    # Combinar ambos años
    monthly_data = pd.concat([current_year_data, last_year_data], ignore_index=True)
    monthly_pivot = monthly_data.pivot(index='month', columns='year', values='total').fillna(0)
    
    months_to_show = list(range(1, 13))
    for row_start in range(0, 12, 4):
        cols = st.columns(4)
        for i, month_num in enumerate(months_to_show[row_start:row_start+4]):
            with cols[i]:
                current_val = monthly_pivot.loc[month_num, current_year] if month_num in monthly_pivot.index and current_year in monthly_pivot.columns else 0
                last_val = monthly_pivot.loc[month_num, last_year] if month_num in monthly_pivot.index and last_year in monthly_pivot.columns else 0
                
                # Calcular delta y determinar color de fondo
                if last_val > 0:
                    delta_pct = ((current_val - last_val) / last_val) * 100
                    delta_str = f"{delta_pct:+.1f}%"
                    # Verde claro si superó, rojo claro si está por debajo
                    if current_val >= last_val:
                        bg_color = "#E6FBF5"  # Verde claro
                        icon_color = "#05CD99"
                    else:
                        bg_color = "#FEEFEE"  # Rojo claro
                        icon_color = "#EE5D50"
                else:
                    delta_str = None
                    bg_color = None  # Blanco por defecto
                    icon_color = "#6AD2FF"
                
                # Formatear valor del año anterior de forma más visible
                help_text = f"📊 {last_year}: {format_currency_abbrev(last_val)}" if last_val > 0 else f"Sin datos {last_year}"
                
                metric_card(
                    title=month_names[month_num], 
                    value=format_currency_abbrev(current_val), 
                    delta=delta_str, 
                    icon="fa-calendar", 
                    color=icon_color, 
                    help_text=help_text,
                    bg_color=bg_color
                )
                
    # 4. Verificación
    st.markdown("---")
    st.markdown("### 🔍 Verificación de Ventas por Día")
    verify_date = st.date_input("Selecciona fecha", value=datetime.now(), max_value=datetime.now())
    verify_start = pd.to_datetime(verify_date).normalize()
    verify_end = verify_start + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    
    mask_v = (df_orders['date_created'] >= verify_start) & (df_orders['date_created'] <= verify_end)
    df_v = df_orders.loc[mask_v]
    
    if not df_v.empty:
        total = df_v['total'].sum()
        st.success(f"✅ **Total: ${total:,.0f}** ({len(df_v)} pedidos)")
        st.dataframe(df_v[['order_id', 'date_created', 'status', 'total']], use_container_width=True)
    else:
        st.warning(f"No hay ventas para {verify_date}")


def view_products(df_items_all, df_orders_all):
    """Vista mejorada de gestión de inventario con stock en detalle, alertas y análisis de rotación."""
    # Mostrar selector de tiempo
    start_date, end_date = show_time_selector()
    
    # Filtrar datos por periodo seleccionado
    mask = (df_orders_all['date_created'] >= start_date) & (df_orders_all['date_created'] <= end_date)
    df_orders = df_orders_all.loc[mask]
    
    # Filtrar items basado en las órdenes del periodo
    valid_ids = df_orders['order_id'].unique()
    df_items = df_items_all[df_items_all['order_id'].isin(valid_ids)]
    
    st.markdown("### 📊 Rendimiento del Inventario")
    if not df_items.empty:
        prod_perf = df_items.groupby('product_name').agg(Unidades=('quantity', 'sum'), Ingresos=('total', 'sum')).reset_index()
        prod_perf = add_product_badges(prod_perf)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Más Vendidos (Ingresos)")
            st.caption("🏆 = Producto estrella del periodo")
            # Usar Top 10 y formato abreviado
            top_rev = prod_perf.sort_values('Ingresos', ascending=False).head(10).sort_values('Ingresos', ascending=True)
            top_rev['Ingresos_fmt'] = top_rev['Ingresos'].apply(format_currency_abbrev)
            
            fig_rev = px.bar(top_rev, x='Ingresos', y='product_display', orientation='h', text='Ingresos_fmt')
            fig_rev.update_traces(
                marker_color='#4318FF', 
                textposition='outside', 
                cliponaxis=False,
                width=0.7 # Hacer las barras un poco más delgadas para elegancia
            )
            fig_rev.update_layout(
                yaxis=dict(
                    title='', 
                    tickfont=dict(size=11, color='#2B3674'),
                    categoryorder='array',
                    categoryarray=top_rev['product_display'].tolist(),
                    automargin=True
                ), 
                xaxis=dict(
                    title='', 
                    showgrid=False, 
                    visible=False, 
                    range=[0, top_rev['Ingresos'].max() * 1.15] # Rango más ajustado
                ),
                template='plotly_white', 
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)', 
                margin=dict(l=0, r=80, t=10, b=0), # Margen derecho reducido de 180 a 80
                height=450,
                uniformtext_mode='hide',
                dragmode=False
            )
            st.plotly_chart(fig_rev, use_container_width=True, config=PLOTLY_CONFIG)
            
        with col2:
            st.markdown("#### Menos Vendidos (Unidades)")

            # Menos Vendidos: Invertir orden para que el "peor" esté arriba
            bottom_units = prod_perf.sort_values('Unidades', ascending=True).head(10).sort_values('Unidades', ascending=False)
            fig_worst = px.bar(bottom_units, x='Unidades', y='product_display', orientation='h', text='Unidades')
            fig_worst.update_traces(
                marker_color='#EE5D50', 
                texttemplate='%{text} un.', 
                textposition='outside', 
                cliponaxis=False,
                width=0.7
            )
            fig_worst.update_layout(
                yaxis=dict(
                    title='', 
                    tickfont=dict(size=11, color='#2B3674'),
                    categoryorder='array',
                    categoryarray=bottom_units['product_display'].tolist(),
                    automargin=True
                ), 
                xaxis=dict(
                    title='', 
                    showgrid=False, 
                    visible=False, 
                    range=[0, max(bottom_units['Unidades'].max() * 1.15, 5)] # Rango más ajustado
                ), 
                template='plotly_white', 
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)', 
                margin=dict(l=0, r=80, t=10, b=0), # Margen derecho reducido
                height=450, 
                uniformtext_mode='hide',
                dragmode=False
            )
            st.plotly_chart(fig_worst, use_container_width=True, config=PLOTLY_CONFIG)
    else:
        st.info("No hay datos de productos.")


def view_customers(df_orders_all):
    # Mostrar selector de tiempo
    start_date, end_date = show_time_selector()
    
    # Filtrar datos por periodo seleccionado
    mask = (df_orders_all['date_created'] >= start_date) & (df_orders_all['date_created'] <= end_date)
    df_orders = df_orders_all.loc[mask]
    
    st.markdown("### 👥 Análisis de Clientes")
    if 'customer_id' in df_orders.columns and not df_orders.empty:
        df_reg = df_orders[df_orders['customer_id'] > 0].copy()
        if not df_reg.empty:
            
            # --- Controles de Ordenamiento ---
            col_c1, col_c2, col_c3 = st.columns(3)
            with col_c1:
                sort_metric = st.selectbox("Ordenar por", ["Compras (#)", "Gasto ($)"], index=0)
            with col_c2:
                sort_order = st.selectbox("Orden", ["Descendente (Mayor a Menor)", "Ascendente (Menor a Mayor)"], index=0)
            with col_c3:
                top_n = st.number_input("Cantidad a mostrar", min_value=5, max_value=50, value=15)
                
            # Determinar columna de ordenamiento
            metric_col = 'Pedidos' if 'Compras' in sort_metric else 'Gasto'
            ascending_bool = True if 'Ascendente' in sort_order else False
            
            # Agrupar datos
            stats = df_reg.groupby(['customer_id', 'customer_name', 'customer_email']).agg(
                Gasto=('total', 'sum'), 
                Pedidos=('order_id', 'count')
            ).reset_index()
            
            # Aplicar ordenamiento
            stats_sorted = stats.sort_values(metric_col, ascending=ascending_bool).head(top_n)
            
            # Podio Logic (Top 3)
            # Solo si el orden es Descendente (Mayor a Menor) tiene sentido el podio de "Mejores"
            # Si es Ascendente, sería el "Podio de los peores" o "menos activos", que también es válido visualmente
            
            st.markdown("#### 🏆 Podio de Clientes")
            
            # Preparar colores de medallas
            medals = ['🥇', '🥈', '🥉']
            colors = ['#FFD700', '#C0C0C0', '#CD7F32'] # Gold, Silver, Bronze
            bg_colors = ['rgba(255, 215, 0, 0.1)', 'rgba(192, 192, 192, 0.1)', 'rgba(205, 127, 50, 0.1)']
            
            col_pod1, col_pod2, col_pod3 = st.columns(3)
            cols = [col_pod1, col_pod2, col_pod3]
            
            for i in range(3):
                if i < len(stats_sorted):
                    row = stats_sorted.iloc[i]
                    with cols[i]:
                        name = row['customer_name'] if row['customer_name'] else row['customer_email'][:15]
                        val_display = f"${row['Gasto']:,.0f}" if metric_col == 'Gasto' else f"{row['Pedidos']} pedidos"
                        
                        st.markdown(f"""
                        <div style="
                            background-color: {bg_colors[i]};
                            border: 1px solid {colors[i]};
                            border-radius: 10px;
                            padding: 15px;
                            text-align: center;
                            height: 100%;
                        ">
                            <div style="font-size: 2rem;">{medals[i]}</div>
                            <div style="font-weight: bold; color: #2B3674; margin-top: 5px;">{name}</div>
                            <div style="font-size: 1.2rem; color: {colors[i]}; font-weight: 700;">{val_display}</div>
                        </div>
                        """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown(f"#### 📋 Detalle Top {top_n}")
            
            # Highlight Top 3 in the table
            def highlight_top3(s):
                is_top3 = s.name in stats_sorted.head(3).index 
                return ['background-color: rgba(255, 215, 0, 0.1)' if is_top3 else '' for _ in s]

            st.dataframe(
                stats_sorted[['customer_name', 'customer_email', 'Pedidos', 'Gasto']].style.format({'Gasto': "${:,.0f}"}),
                use_container_width=True,
                height=max(400, top_n * 35) # Adjusted height
            )

        else:
            st.info("Solo pedidos de invitados.")
    else:
        st.warning("Datos de clientes no disponibles.")


def view_traffic(df_orders_all, df_ga_all, df_ga_traffic_all, df_fb_all):
    # Mostrar selector de tiempo
    start_date, end_date = show_time_selector()
    
    st.markdown("### 🌐 Tráfico y Redes Sociales")
    
    # Check if we have any data sources configured
    has_ga = not df_ga_all.empty
    has_fb = not df_fb_all.empty
    
    # Show configuration warning if no data sources are available
    if not has_ga and not has_fb:
        st.warning("⚠️ **No hay datos de tráfico disponibles**")
        st.info("""
        Esta sección requiere configurar al menos uno de los siguientes servicios:
        
        - **Google Analytics 4**: Para métricas de tráfico web, conversión y comportamiento del usuario
        - **Facebook/Meta**: Para insights de redes sociales y rendimiento de publicaciones
        
        Una vez configurados y ejecutado el ETL correspondiente, aquí verás:
        - 📊 Embudo de conversión completo
        - 👁️ Visitas diarias y tendencias
        - 🌐 Origen del tráfico (Google, redes sociales, directo, etc.)
        - 📄 Páginas más visitadas
        - 📱 Métricas de redes sociales
        """)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("⚙️ Configurar Servicios", key="setup_traffic", type="primary", use_container_width=True):
                st.switch_page("pages/setup.py")
        
        st.markdown("---")
        st.caption("💡 **Tip**: Después de configurar, ejecuta el ETL desde la terminal con `python etl/main.py`")
        return
    
    # If we reach here, at least one data source is configured
    if not has_ga:
        st.info("ℹ️ **Google Analytics no configurado** - Algunas métricas no estarán disponibles. Configúralo para ver el embudo de conversión completo.")
    if not has_fb:
        st.info("ℹ️ **Facebook no configurado** - Las métricas de redes sociales no estarán disponibles.")
    
    # Filtrar datos por periodo seleccionado
    mask = (df_orders_all['date_created'] >= start_date) & (df_orders_all['date_created'] <= end_date)
    df_orders = df_orders_all.loc[mask]
    
    # Filtrar GA
    df_ga = pd.DataFrame()
    if not df_ga_all.empty:
        if 'Fecha' in df_ga_all.columns:
            # CRITICAL FIX: Only parse if not already datetime (avoid double parsing)
            if not pd.api.types.is_datetime64_any_dtype(df_ga_all['Fecha']):
                df_ga_all['Fecha'] = pd.to_datetime(
                    df_ga_all['Fecha'].astype(str).str.replace('-', ''), 
                    format='%Y%m%d', 
                    errors='coerce'
                )
            # FIX: Crear columna date_only para que el groupby funcione
            df_ga_all['date_only'] = df_ga_all['Fecha'].dt.normalize()
            
        df_ga = df_ga_all[(df_ga_all['Fecha'] >= start_date) & (df_ga_all['Fecha'] <= end_date)]
    
    # Filtrar GA Traffic
    df_ga_traffic = pd.DataFrame()
    if not df_ga_traffic_all.empty and 'Fecha' in df_ga_traffic_all.columns:
        # CRITICAL FIX: Only parse if not already datetime (avoid double parsing)
        if not pd.api.types.is_datetime64_any_dtype(df_ga_traffic_all['Fecha']):
            df_ga_traffic_all['Fecha'] = pd.to_datetime(
                df_ga_traffic_all['Fecha'].astype(str).str.replace('-', ''), 
                format='%Y%m%d', 
                errors='coerce'
            )
        df_ga_traffic = df_ga_traffic_all[(df_ga_traffic_all['Fecha'] >= start_date) & (df_ga_traffic_all['Fecha'] <= end_date)]
    else:
        df_ga_traffic = df_ga_traffic_all
    
    # Filtrar FB
    df_fb = pd.DataFrame()
    if not df_fb_all.empty and 'date' in df_fb_all.columns:
        df_fb_all['date'] = pd.to_datetime(df_fb_all['date'])
        df_fb = df_fb_all[(df_fb_all['date'] >= start_date) & (df_fb_all['date'] <= end_date)]
    else:
        df_fb = df_fb_all
    
    # Crear combined_df
    # Crear combined_df
    combined_df = pd.DataFrame()
    
    # Preparar datos de ventas y pedidos
    daily_sales = pd.DataFrame()
    if not df_orders.empty:
        daily_sales = df_orders.groupby('date_only').agg(
            Ventas=('total','sum'),
            Pedidos=('order_id', 'count')
        ).reset_index()
        daily_sales['date_only'] = pd.to_datetime(daily_sales['date_only'])
    
    # Preparar datos de visitas
    daily_ga = pd.DataFrame()
    if not df_ga.empty:
        daily_ga = df_ga.groupby('date_only').agg(Visitas=('UsuariosActivos','sum')).reset_index()
        daily_ga['date_only'] = pd.to_datetime(daily_ga['date_only'])
        
    # Combinar datos disponibles
    if not daily_sales.empty and not daily_ga.empty:
        combined_df = pd.merge(daily_sales, daily_ga, on='date_only', how='outer').fillna(0).sort_values('date_only')
    elif not daily_sales.empty:
        combined_df = daily_sales
        combined_df['Visitas'] = 0
        combined_df = combined_df.sort_values('date_only')
    elif not daily_ga.empty:
        combined_df = daily_ga
        combined_df['Ventas'] = 0
        combined_df = combined_df.sort_values('date_only')
    
    # --- COMBINED TRAFFIC VS ORDERS CHART ---
    st.markdown("### 📈 Visitas Google vs Pedidos WooCommerce")
    st.caption("Comparativa diaria: ¿Más visitas generan más pedidos?")
    
    if not combined_df.empty and 'Visitas' in combined_df.columns and 'Pedidos' in combined_df.columns:
        # Only show chart if we have both data types
        has_visits = combined_df['Visitas'].sum() > 0
        has_orders = combined_df['Pedidos'].sum() > 0
        
        if has_visits and has_orders:
            from plotly.subplots import make_subplots
            
            # Crear subplots apilados con diseño mejorado
            fig_stacked = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.06,
                row_heights=[0.55, 0.45],
                subplot_titles=('', '')  # Títulos vacíos, usaremos leyenda
            )
            
            # Gráfico superior: Visitas como área rellena
            fig_stacked.add_trace(
                go.Scatter(
                    x=combined_df['date_only'],
                    y=combined_df['Visitas'],
                    name='👥 Visitas Google',
                    mode='lines',
                    line=dict(color='#05CD99', width=2),
                    fill='tozeroy',
                    fillcolor='rgba(5, 205, 153, 0.15)',
                    hovertemplate='%{x|%d %b}<br><b>%{y:,.0f} visitas</b><extra></extra>',
                    showlegend=True
                ),
                row=1, col=1
            )
            
            # Gráfico inferior: Pedidos como línea con marcadores
            fig_stacked.add_trace(
                go.Scatter(
                    x=combined_df['date_only'],
                    y=combined_df['Pedidos'],
                    name='🛒 Pedidos WooCommerce',
                    mode='lines+markers',
                    line=dict(color='#4318FF', width=3),
                    marker=dict(size=7, color='#4318FF', line=dict(width=2, color='white')),
                    fill='tozeroy',
                    fillcolor='rgba(67, 24, 255, 0.15)',
                    hovertemplate='%{x|%d %b}<br><b>%{y:.0f} pedidos</b><extra></extra>',
                    showlegend=True
                ),
                row=2, col=1
            )
            
            # Layout compacto y profesional
            fig_stacked.update_layout(
                template='plotly_white',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=450,
                margin=dict(l=50, r=20, t=40, b=50),
                hovermode='x unified',
                dragmode=False,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=1.08,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=11, color='#2B3674'),
                    bgcolor='rgba(255,255,255,0.8)',
                    bordercolor='#A3AED0',
                    borderwidth=1
                )
            )
            
            # Configurar eje X (solo visible en gráfico inferior)
            fig_stacked.update_xaxes(
                showgrid=False,
                tickformat='%d %b',
                tickfont=dict(size=10, color='#2B3674'),
                row=2, col=1
            )
            fig_stacked.update_xaxes(showticklabels=False, showgrid=False, row=1, col=1)
            
            # Configurar ejes Y independientes con colores
            fig_stacked.update_yaxes(
                title_text='Visitas',
                showgrid=True,
                gridcolor='rgba(5, 205, 153, 0.1)',
                tickfont=dict(size=10, color='#05CD99'),
                title_font=dict(size=11, color='#05CD99', weight=600),
                row=1, col=1
            )
            fig_stacked.update_yaxes(
                title_text='Pedidos',
                showgrid=True,
                gridcolor='rgba(67, 24, 255, 0.1)',
                tickfont=dict(size=10, color='#4318FF'),
                title_font=dict(size=11, color='#4318FF', weight=600),
                row=2, col=1
            )
            
            st.plotly_chart(fig_stacked, use_container_width=True, config=PLOTLY_CONFIG)

            

            # Mostrar correlación
            if len(combined_df) > 7:
                correlation = combined_df['Visitas'].corr(combined_df['Pedidos'])
                if correlation > 0.5:
                    st.success(f"📊 **Correlación alta ({correlation:.2f})**: Los picos coinciden - más visitas = más pedidos")
                elif correlation > 0.2:
                    st.info(f"📊 **Correlación moderada ({correlation:.2f})**: Las visitas influyen en los pedidos")
                elif correlation > -0.2:
                    st.warning(f"📊 **Correlación baja ({correlation:.2f})**: Las visitas no predicen los pedidos")
                else:
                    st.error(f"📊 **Correlación negativa ({correlation:.2f})**: Patrón inusual")
                    
        elif has_visits:
            st.info("Solo hay datos de visitas. Configura WooCommerce para ver la comparativa.")
        elif has_orders:
            st.info("Solo hay datos de pedidos. Configura Google Analytics para ver la comparativa.")
        else:
            st.info("No hay datos para el periodo seleccionado.")
    else:
        st.info("Configura Google Analytics y WooCommerce para ver la comparativa.")
    
    st.markdown("---")
    
    # --- CONVERSION FUNNEL ---
    st.markdown("### 📊 Embudo de Conversión")
    st.caption("Análisis del recorrido del cliente desde la visita hasta la compra")
    
    # Calculate funnel metrics
    if not df_ga.empty:
        # Get total orders for the period
        total_orders = len(df_orders)
        
        # Stage 1: Sessions (from traffic)
        total_sessions = df_ga['UsuariosActivos'].sum()  # Using active users as proxy for sessions
        
        # Stage 2: Active Users
        total_active_users = df_ga['UsuariosActivos'].sum()
        
        # Stage 3: Cart Additions
        total_cart = df_ga['AgregadosAlCarrito'].sum() if 'AgregadosAlCarrito' in df_ga.columns else 0
        
        # Stage 4: Buyers
        total_buyers = df_ga['Compradores'].sum() if 'Compradores' in df_ga.columns else total_orders
        
        # Calculate conversion rates
        rate_active = (total_active_users / total_sessions * 100) if total_sessions > 0 else 0
        rate_cart = (total_cart / total_active_users * 100) if total_active_users > 0 else 0
        rate_purchase = (total_buyers / total_cart * 100) if total_cart > 0 else 0
        rate_overall = (total_buyers / total_sessions * 100) if total_sessions > 0 else 0
        
        # Calcular tasas de abandono entre etapas (para el resumen siguiente)
        drop_to_active = ((total_sessions - total_active_users) / total_sessions * 100) if total_sessions > 0 else 0
        drop_to_cart = ((total_active_users - total_cart) / total_active_users * 100) if total_active_users > 0 else 0
        drop_to_purchase = ((total_cart - total_buyers) / total_cart * 100) if total_cart > 0 else 0
        
        # Resumen de tasas de abandono más visual
        st.markdown("##### 📉 Resumen de Pérdidas por Etapa")
        col_ab1, col_ab2, col_ab3, col_ab4 = st.columns(4)
        with col_ab1:
            st.markdown(f"""
            <div style="text-align:center; padding:10px; background:#F4F7FE; border-radius:10px;">
                <div style="font-size:2rem; color:#4318FF;">👥</div>
                <div style="font-size:0.8rem; color:#A3AED0;">SESIONES</div>
                <div style="font-size:1.2rem; font-weight:700; color:#2B3674;">{total_sessions:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)
        with col_ab2:
            st.markdown(f"""
            <div style="text-align:center; padding:10px; background:#FEEFEE; border-radius:10px;">
                <div style="font-size:1.5rem; color:#EE5D50;">↓ {drop_to_cart:.1f}%</div>
                <div style="font-size:0.7rem; color:#A3AED0;">NO AGREGAN<br>AL CARRITO</div>
            </div>
            """, unsafe_allow_html=True)
        with col_ab3:
            st.markdown(f"""
            <div style="text-align:center; padding:10px; background:#FEEFEE; border-radius:10px;">
                <div style="font-size:1.5rem; color:#EE5D50;">↓ {drop_to_purchase:.1f}%</div>
                <div style="font-size:0.7rem; color:#A3AED0;">ABANDONO<br>DE CARRITO</div>
            </div>
            """, unsafe_allow_html=True)
        with col_ab4:
            st.markdown(f"""
            <div style="text-align:center; padding:10px; background:#E6FBF5; border-radius:10px;">
                <div style="font-size:2rem; color:#05CD99;">💰</div>
                <div style="font-size:0.8rem; color:#A3AED0;">COMPRADORES</div>
                <div style="font-size:1.2rem; font-weight:700; color:#2B3674;">{total_buyers:,.0f}</div>
                <div style="font-size:0.7rem; color:#05CD99;">{rate_overall:.2f}% conversión</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Abandonment rates expandible (ahora más detallado)
        with st.expander("📊 Detalles de Conversión por Etapa"):
            st.markdown(f"""
            | Etapa | Cantidad | Tasa desde inicio | Pérdida vs anterior |
            |-------|----------|-------------------|---------------------|
            | 👥 Sesiones | {total_sessions:,.0f} | 100% | - |
            | ✅ Usuarios Activos | {total_active_users:,.0f} | {rate_active:.1f}% | -{drop_to_active:.1f}% |
            | 🛒 Al Carrito | {total_cart:,.0f} | {(total_cart/total_sessions*100) if total_sessions > 0 else 0:.1f}% | -{drop_to_cart:.1f}% |
            | 💰 Compradores | {total_buyers:,.0f} | {rate_overall:.2f}% | -{drop_to_purchase:.1f}% |
            
            **Interpretación:**
            - **Conversión general**: {rate_overall:.2f}% de los visitantes realizan una compra
            - **Mayor pérdida**: {'Abandono de carrito' if drop_to_purchase > drop_to_cart else 'No agregan al carrito'} ({max(drop_to_purchase, drop_to_cart):.1f}%)
            """)
    else:
        st.warning("⚠️ **Embudo de Conversión No Disponible**")
        st.markdown("""
        Para visualizar el embudo de conversión necesitas:
        
        1. **Configurar Google Analytics 4** en la sección de configuración
        2. **Ejecutar el ETL** para extraer los datos de GA4
        3. **Verificar que el property ID** sea correcto
        
        El embudo muestra: Sesiones → Usuarios Activos → Carrito → Compradores
        """)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("⚙️ Ir a Configuración", use_container_width=True):
                st.switch_page("pages/setup.py")
        with col2:
            st.caption("💡 Después de configurar, ejecuta: `python etl/main.py`")
    
    st.markdown("---")
    
    # === GRÁFICO DIRECTO DE VISITAS (Carga directa de DB) ===
    try:
        db_analytics = os.path.join(os.path.dirname(__file__), '..', 'data', 'analytics.db')
        
        # Use db_adapter for dual-database support
        if DB_ADAPTER_AVAILABLE and get_db_adapter().is_postgresql():
            with get_connection('analytics') as conn:
                df_direct = pd.read_sql("SELECT * FROM ga4_ecommerce", conn)
        else:
            import sqlite3
            conn = sqlite3.connect(db_analytics)
            df_direct = pd.read_sql("SELECT * FROM ga4_ecommerce", conn)
            conn.close()
        
        if not df_direct.empty:
            # Parse dates
            df_direct['Fecha'] = pd.to_datetime(df_direct['Fecha'].astype(str), format='%Y%m%d', errors='coerce')
            df_direct = df_direct.dropna(subset=['Fecha'])
            df_direct = df_direct.sort_values('Fecha')
            
            # Filter by selected period
            df_direct_filtered = df_direct[(df_direct['Fecha'] >= start_date) & (df_direct['Fecha'] <= end_date)]
            
            if not df_direct_filtered.empty:
                
                # Calcular promedio para identificar picos
                df_direct_filtered = df_direct_filtered.sort_values('Fecha')
                avg_visits = df_direct_filtered['UsuariosActivos'].mean()
                df_direct_filtered['is_peak'] = df_direct_filtered['UsuariosActivos'] > (avg_visits * 1.5)
                
                # Premium line chart
                fig_direct = go.Figure()
                fig_direct.add_trace(go.Scatter(
                    x=df_direct_filtered['Fecha'],
                    y=df_direct_filtered['UsuariosActivos'],
                    mode='lines',
                    name='Usuarios Activos',
                    line=dict(color='#4318FF', width=2.5, shape='spline'),
                    fill='tozeroy',
                    fillcolor='rgba(67, 24, 255, 0.05)',
                    hovertemplate='<b>%{x|%d %b %Y}</b><br>Usuarios: <b>%{y:,.0f}</b><extra></extra>'
                ))
                
                # Añadir anotaciones para picos de visitas
                peaks = df_direct_filtered[df_direct_filtered['is_peak']]
                for _, peak in peaks.head(5).iterrows():
                    fig_direct.add_annotation(
                        x=peak['Fecha'],
                        y=peak['UsuariosActivos'],
                        text=f"🔥 {peak['UsuariosActivos']:,.0f}",
                        showarrow=True,
                        arrowhead=2,
                        arrowsize=0.8,
                        arrowcolor='#EE5D50',
                        ax=0,
                        ay=-35,
                        font=dict(size=9, color='#EE5D50'),
                        bgcolor='rgba(255,255,255,0.9)',
                        bordercolor='#EE5D50',
                        borderwidth=1,
                        borderpad=2
                    )
                
                # Añadir anotaciones para fechas especiales
                special_dates = load_special_dates()
                for date_key, date_info in special_dates.items():
                    try:
                        matching_dates = df_direct_filtered[df_direct_filtered['Fecha'].dt.strftime('%m-%d') == date_key]
                        for _, match in matching_dates.iterrows():
                            fig_direct.add_annotation(
                                x=match['Fecha'],
                                y=match['UsuariosActivos'],
                                text=date_info['name'],
                                showarrow=True,
                                arrowhead=2,
                                arrowsize=0.8,
                                arrowcolor=date_info.get('color', '#4318FF'),
                                ax=20,
                                ay=-45,
                                font=dict(size=9, color=date_info.get('color', '#4318FF')),
                                bgcolor='rgba(255,255,255,0.95)',
                                bordercolor=date_info.get('color', '#4318FF'),
                                borderwidth=1,
                                borderpad=3
                            )
                    except:
                        pass
                
                fig_direct.update_layout(
                    template='plotly_white',
                    paper_bgcolor='rgba(255,255,255,0.95)',
                    plot_bgcolor='rgba(255,255,255,0.95)',
                    height=400,
                    margin=dict(l=40, r=40, t=20, b=60),
                    xaxis=dict(
                        tickformat='%d %b',
                        title='',
                        showgrid=False,
                        tickfont=dict(size=11, color='#2B3674'),
                        tickangle=-30
                    ),
                    yaxis=dict(
                        title='',
                        showgrid=True,
                        gridcolor='rgba(163, 174, 208, 0.2)',
                        tickfont=dict(size=11, color='#2B3674')
                    ),
                    showlegend=False,
                    dragmode=False,
                    hovermode='x unified'
                )
                
                # Center the chart
                col_chart1, col_chart2, col_chart3 = st.columns([0.5, 10, 0.5])
                with col_chart2:
                    st.plotly_chart(fig_direct, use_container_width=True, config=PLOTLY_CONFIG)
            else:
                st.warning(f"No hay datos en el rango {start_date.date()} - {end_date.date()}")
        else:
            st.info("⚠️ No hay datos de Analytics disponibles")
    except Exception as e:
        st.error(f"Error cargando datos: {e}")

    # Origen del Tráfico
    st.markdown("#### Origen del Tráfico")
    if not df_ga_traffic.empty and 'Fuente' in df_ga_traffic.columns:
        df_ga_traffic['Fuente_Norm'] = df_ga_traffic['Fuente'].apply(normalize_traffic_source)
        summary = df_ga_traffic.groupby('Fuente_Norm')['Sesiones'].sum().reset_index()
        clean = summary[~summary['Fuente_Norm'].str.contains('Bot', case=False, na=False)].sort_values('Sesiones', ascending=False).head(10)
        
        if not clean.empty:
            # Colors from the original image
            colors = ['#3b82f6', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6', '#14b8a6', '#f97316', '#06b6d4', '#84cc16', '#a855f7']
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=clean['Fuente_Norm'], 
                values=clean['Sesiones'], 
                hole=0.5,
                marker=dict(colors=colors[:len(clean)], line=dict(color='rgba(0,0,0,0.1)', width=2)),
                textinfo='label+percent',
                textposition='inside',
                textfont=dict(size=11),
                hovertemplate='<b>%{label}</b><br>%{value:,} sesiones<br>%{percent}<extra></extra>',
                pull=[0.05 if i == 0 else 0 for i in range(len(clean))]
            )])
            fig_pie.update_layout(
                template='plotly_white', 
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)', 
                height=450, 
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="middle",
                    y=0.5,
                    xanchor="left",
                    x=1.05,
                    font=dict(size=11, color='#2B3674'),
                    bgcolor='rgba(255, 255, 255, 0.95)',
                    borderwidth=0
                ),
                margin=dict(l=20, r=80, t=20, b=20),
                dragmode=False
            )
            st.plotly_chart(fig_pie, use_container_width=True, config=PLOTLY_CONFIG)
        else:
            st.info("Solo tráfico spam")
    else:
        st.info("Datos de tráfico no disponibles")
    
    # Páginas Más Visitadas    
    st.markdown("#### 📄 Páginas Más Visitadas")
    try:
        df_pages = load_data('ga4_pages', DATABASE_ANALYTICS)
        if not df_pages.empty:
            top_pages = df_pages.groupby('Pagina')['Vistas'].sum().sort_values(ascending=False).head(8).sort_values(ascending=True).reset_index()
            fig_p = px.bar(top_pages, x='Vistas', y='Pagina', orientation='h', text='Vistas')
            fig_p.update_traces(marker_color='#4318FF', textposition='outside')
            fig_p.update_layout(template='plotly_white', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=400, margin=dict(l=0, r=80, t=0, b=0), dragmode=False)
            st.plotly_chart(fig_p, use_container_width=True, config=PLOTLY_CONFIG)
    except:
        pass

    st.markdown("---")
    st.markdown("---")
    st.markdown("### 📱 Redes Sociales (Facebook)")
    
    if not df_fb.empty:
        # Check available columns
        available_cols = df_fb.columns.tolist()
        has_fans = 'page_fans' in available_cols
        has_followers = 'page_followers' in available_cols
        
        if has_fans or has_followers:
            st.markdown("#### 📈 Crecimiento de la Comunidad")
            st.caption("Evolución histórica de seguidores y fans")
            
            # fig_fb = go.Figure() # Chart removed by user request
            
            if has_fans:
                # Get latest value for metric card
                latest_fans = df_fb.sort_values('date')['page_fans'].iloc[-1]
            
            if has_followers:
                # Get latest value
                latest_followers = df_fb.sort_values('date')['page_followers'].iloc[-1]
            
            # Show summarized metrics
            if has_followers:
                col_fb1, col_fb2, col_fb3 = st.columns([1, 2, 1])
                with col_fb2:
                    metric_card("Total Seguidores", f"{latest_followers:,.0f}", icon="fa-users", color="#05CD99")
            
            # Restore charts for impressions and engagement
            st.markdown("#### Desempeño de Contenido")
            fig_fb_metrics = go.Figure()
            if 'page_impressions' in available_cols:
                fig_fb_metrics.add_trace(go.Scatter(
                    x=df_fb['date'], 
                    y=df_fb['page_impressions'], 
                    name='Impresiones',
                    line=dict(color='#4318FF', width=3),
                    fill='tozeroy',
                    fillcolor='rgba(67, 24, 255, 0.1)'
                ))
            if 'page_engaged_users' in available_cols:
                fig_fb_metrics.add_trace(go.Scatter(
                    x=df_fb['date'], 
                    y=df_fb['page_engaged_users'], 
                    name='Engagement',
                    line=dict(color='#FFB547', width=3)
                ))
            
            fig_fb_metrics.update_layout(
                template='plotly_white',
                height=400,
                margin=dict(l=0, r=0, t=20, b=0),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                hovermode='x unified',
                dragmode=False
            )
            st.plotly_chart(fig_fb_metrics, use_container_width=True, config=PLOTLY_CONFIG)
                    
        else:
            # Fallback if old data format
            fig_fb = go.Figure()
            if 'page_impressions' in available_cols:
                fig_fb.add_trace(go.Scatter(x=df_fb['date'], y=df_fb['page_impressions'], name='Impresiones', line=dict(color='#4318FF')))
            if 'page_engaged_users' in available_cols:
                fig_fb.add_trace(go.Scatter(x=df_fb['date'], y=df_fb['page_engaged_users'], name='Engagement', line=dict(color='#FFB547')))
            
            if fig_fb.data:
                st.plotly_chart(fig_fb, use_container_width=True, config=PLOTLY_CONFIG)
            else:
                st.info("ℹ️ No hay métricas históricas de comunidad disponibles aún. Se empezarán a registrar desde hoy.")
    else:
        st.info("ℹ️ No hay datos de Facebook para el periodo seleccionado.")

def view_inventory(df_orders_all, df_items_all):
    """Vista mejorada de gestión de inventario con stock en detalle, alertas y análisis de rotación."""
    # Mostrar selector de tiempo
    start_date, end_date = show_time_selector()
    
    # Filtrar datos por periodo seleccionado
    mask = (df_orders_all['date_created'] >= start_date) & (df_orders_all['date_created'] <= end_date)
    df_orders = df_orders_all.loc[mask]
    
    # Filtrar items basado en las órdenes del periodo
    valid_ids = df_orders['order_id'].unique()
    df_items = df_items_all[df_items_all['order_id'].isin(valid_ids)]
    
    st.markdown("### 📦 Gestión de Inventario")
    st.caption("Control completo de stock, alertas y análisis de rotación de productos")
    
    # Cargar datos de productos
    try:
        df_products = load_data('wc_products')
    except:
        st.error("❌ No se pudo cargar la tabla de productos. Ejecuta primero el ETL de WooCommerce.")
        return
    
    if df_products.empty:
        st.warning("⚠️ No hay datos de productos. Ejecuta la extracción de WooCommerce primero.")
        return
    
    # Calcular métricas de stock
    total_products = len(df_products)
    in_stock = len(df_products[df_products['stock_status'] == 'instock'])
    out_of_stock = len(df_products[df_products['stock_status'] == 'outofstock'])
    on_backorder = len(df_products[df_products['stock_status'] == 'onbackorder'])
    
    # Stock total disponible (suma de todas las unidades)
    df_products['stock_qty_safe'] = pd.to_numeric(df_products['stock_quantity'], errors='coerce').fillna(0)
    total_units_in_stock = int(df_products['stock_qty_safe'].sum())
    
    # Productos con stock bajo (si tienen threshold definido)
    df_products['low_stock_amt_safe'] = pd.to_numeric(df_products['low_stock_amount'], errors='coerce')
    df_with_threshold = df_products[df_products['low_stock_amt_safe'].notna()].copy()
    if not df_with_threshold.empty:
        df_with_threshold['is_low_stock'] = df_with_threshold.apply(
            lambda x: x['stock_qty_safe'] <= x['low_stock_amt_safe'] and x['stock_qty_safe'] > 0, 
            axis=1
        )
        low_stock_count = int(df_with_threshold['is_low_stock'].sum())
    else:
        low_stock_count = 0
    
    # Valor total del inventario
    df_products['price_safe'] = pd.to_numeric(df_products['price'], errors='coerce').fillna(0)
    df_products['inventory_value'] = df_products['stock_qty_safe'] * df_products['price_safe']
    total_inventory_value = df_products['inventory_value'].sum()
    
    # ═══════════════════════════════════════════════════════════════════
    # SECCIÓN: KPIs PRINCIPALES
    # ═══════════════════════════════════════════════════════════════════
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("Total Productos", f"{total_products}", icon="fa-boxes-stacked", color="#4318FF")
    with col2:
        metric_card("Unidades en Stock", f"{total_units_in_stock:,}", icon="fa-cubes", color="#05CD99", help_text="Total de unidades disponibles")
    with col3:
        metric_card("Productos Agotados", f"{out_of_stock}", icon="fa-triangle-exclamation", color="#EE5D50", help_text=f"{(out_of_stock/total_products*100):.1f}% del catálogo")
    with col4:
        metric_card("Valor Inventario", f"${total_inventory_value:,.0f}", icon="fa-coins", color="#FFB547")
    
    # Métricas secundarias
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        metric_card("En Stock", f"{in_stock}", icon="fa-check-circle", color="#05CD99", help_text=f"{(in_stock/total_products*100):.1f}% disponible")
    with col6:
        metric_card("Stock Bajo", f"{low_stock_count}", icon="fa-bell", color="#FFB547", help_text="Por debajo del umbral")
    with col7:
        metric_card("En Backorder", f"{on_backorder}", icon="fa-clock", color="#6AD2FF", help_text="Pendiente de reposición")
    with col8:
        avg_stock = df_products[df_products['stock_qty_safe'] > 0]['stock_qty_safe'].mean()
        metric_card("Stock Promedio", f"{avg_stock:.1f}" if not pd.isna(avg_stock) else "0", icon="fa-chart-simple", color="#4318FF", help_text="Unidades promedio por producto")
    
    st.markdown("---")
    
    # ═══════════════════════════════════════════════════════════════════
    # SECCIÓN: DISTRIBUCIÓN DE STOCK POR ESTADO
    # ═══════════════════════════════════════════════════════════════════
    st.markdown("#### 📊 Distribución del Inventario")
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("##### Estado del Stock")
        stock_status_counts = df_products['stock_status'].value_counts().reset_index()
        stock_status_counts.columns = ['Estado', 'Cantidad']
        
        # Mapear nombres a español
        status_names = {
            'instock': '✅ En Stock',
            'outofstock': '❌ Agotado',
            'onbackorder': '⏳ Backorder'
        }
        stock_status_counts['Estado'] = stock_status_counts['Estado'].map(lambda x: status_names.get(x, x))
        
        colors_status = ['#05CD99', '#EE5D50', '#6AD2FF']
        
        fig_status = px.pie(
            stock_status_counts, 
            values='Cantidad', 
            names='Estado',
            hole=0.65,
            color_discrete_sequence=colors_status
        )
        fig_status.update_traces(
            textinfo='label+value+percent',
            textposition='outside',
            textfont=dict(size=11),
            hovertemplate='<b>%{label}</b><br>%{value} productos<br>%{percent}<extra></extra>'
        )
        fig_status.update_layout(
            template='plotly_white',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=350,
            showlegend=False,
            margin=dict(l=20, r=20, t=20, b=20),
            dragmode=False
        )
        st.plotly_chart(fig_status, use_container_width=True, config=PLOTLY_CONFIG)
    
    with col_chart2:
        st.markdown("##### Stock por Rangos de Unidades")
        # Clasificar productos por cantidad de stock
        def classify_stock(qty):
            if qty == 0:
                return '0 unidades'
            elif qty <= 5:
                return '1-5 unidades'
            elif qty <= 20:
                return '6-20 unidades'
            elif qty <= 50:
                return '21-50 unidades'
            else:
                return '>50 unidades'
        
        df_products['stock_range'] = df_products['stock_qty_safe'].apply(classify_stock)
        stock_ranges = df_products['stock_range'].value_counts().reset_index()
        stock_ranges.columns = ['Rango', 'Cantidad']
        
        # Ordenar los rangos
        range_order = ['0 unidades', '1-5 unidades', '6-20 unidades', '21-50 unidades', '>50 unidades']
        stock_ranges['order'] = stock_ranges['Rango'].apply(lambda x: range_order.index(x) if x in range_order else 99)
        stock_ranges = stock_ranges.sort_values('order')
        
        colors_ranges = ['#EE5D50', '#FFB547', '#6AD2FF', '#05CD99', '#4318FF']
        
        fig_ranges = px.bar(
            stock_ranges,
            x='Rango',
            y='Cantidad',
            color='Rango',
            color_discrete_sequence=colors_ranges,
            text='Cantidad'
        )
        fig_ranges.update_traces(textposition='outside', textfont=dict(size=12))
        fig_ranges.update_layout(
            template='plotly_white',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=350,
            showlegend=False,
            xaxis=dict(title=''),
            yaxis=dict(title='', showgrid=False),
            margin=dict(l=0, r=0, t=20, b=30),
            dragmode=False
        )
        st.plotly_chart(fig_ranges, use_container_width=True, config=PLOTLY_CONFIG)
    
    st.markdown("---")
    
    # ═══════════════════════════════════════════════════════════════════
    # SECCIÓN: TABLA COMPLETA DE PRODUCTOS CON STOCK
    # ═══════════════════════════════════════════════════════════════════
    st.markdown("#### 📋 Inventario Completo de Productos")
    st.caption("Todos los productos con sus cantidades en stock actuales")
    
    # Preparar datos para la tabla
    inventory_table = df_products[['name', 'sku', 'stock_qty_safe', 'stock_status', 'price_safe', 'categories', 'inventory_value', 'total_sales']].copy()
    inventory_table['total_sales'] = pd.to_numeric(inventory_table['total_sales'], errors='coerce').fillna(0).astype(int)
    
    # Agregar indicador visual de estado
    def get_stock_badge(row):
        qty = row['stock_qty_safe']
        status = row['stock_status']
        if status == 'outofstock' or qty == 0:
            return '🔴'
        elif qty <= 5:
            return '🟡'
        elif qty <= 20:
            return '🟠'
        else:
            return '🟢'
    
    inventory_table['Indicador'] = inventory_table.apply(get_stock_badge, axis=1)
    
    # Renombrar columnas
    inventory_table.columns = ['Producto', 'SKU', 'Stock', 'Estado', 'Precio', 'Categorías', 'Valor Stock', 'Total Vendido', 'Indicador']
    
    # Reordenar columnas
    inventory_table = inventory_table[['Indicador', 'Producto', 'SKU', 'Stock', 'Estado', 'Precio', 'Valor Stock', 'Total Vendido', 'Categorías']]
    
    # Mapear estados a español
    status_map = {'instock': 'En Stock', 'outofstock': 'Agotado', 'onbackorder': 'Backorder'}
    inventory_table['Estado'] = inventory_table['Estado'].map(lambda x: status_map.get(x, x))
    
    # Filtros
    filter_col1, filter_col2, filter_col3 = st.columns([2, 1, 1])
    
    with filter_col1:
        search_product = st.text_input("🔍 Buscar producto", placeholder="Escribe nombre o SKU...")
    
    with filter_col2:
        stock_filter = st.selectbox(
            "📊 Filtrar por estado",
            options=['Todos', 'En Stock', 'Agotado', 'Backorder', 'Stock Bajo (≤5)'],
            index=0
        )
    
    with filter_col3:
        sort_by = st.selectbox(
            "📈 Ordenar por",
            options=['Stock (menor a mayor)', 'Stock (mayor a menor)', 'Valor Stock', 'Total Vendido', 'Nombre'],
            index=0
        )
    
    # Aplicar filtros
    filtered_table = inventory_table.copy()
    
    if search_product:
        filtered_table = filtered_table[
            filtered_table['Producto'].str.lower().str.contains(search_product.lower(), na=False) |
            filtered_table['SKU'].fillna('').str.lower().str.contains(search_product.lower())
        ]
    
    if stock_filter == 'En Stock':
        filtered_table = filtered_table[filtered_table['Estado'] == 'En Stock']
    elif stock_filter == 'Agotado':
        filtered_table = filtered_table[filtered_table['Estado'] == 'Agotado']
    elif stock_filter == 'Backorder':
        filtered_table = filtered_table[filtered_table['Estado'] == 'Backorder']
    elif stock_filter == 'Stock Bajo (≤5)':
        filtered_table = filtered_table[(filtered_table['Stock'] > 0) & (filtered_table['Stock'] <= 5)]
    
    # Aplicar ordenamiento
    if sort_by == 'Stock (menor a mayor)':
        filtered_table = filtered_table.sort_values('Stock', ascending=True)
    elif sort_by == 'Stock (mayor a menor)':
        filtered_table = filtered_table.sort_values('Stock', ascending=False)
    elif sort_by == 'Valor Stock':
        filtered_table = filtered_table.sort_values('Valor Stock', ascending=False)
    elif sort_by == 'Total Vendido':
        filtered_table = filtered_table.sort_values('Total Vendido', ascending=False)
    else:
        filtered_table = filtered_table.sort_values('Producto')
    
    st.markdown(f"**Mostrando {len(filtered_table):,} de {len(inventory_table):,} productos**")
    
    st.dataframe(
        format_empty_cells(filtered_table),
        use_container_width=True,
        height=450,
        column_config={
            "Indicador": st.column_config.TextColumn("🚦", width="small"),
            "Producto": st.column_config.TextColumn("Producto", width="large"),
            "SKU": st.column_config.TextColumn("SKU", width="small"),
            "Stock": st.column_config.NumberColumn("Stock", format="%d un."),
            "Estado": st.column_config.TextColumn("Estado"),
            "Precio": st.column_config.NumberColumn("Precio", format="$%.0f"),
            "Valor Stock": st.column_config.NumberColumn("Valor Stock", format="$%.0f"),
            "Total Vendido": st.column_config.NumberColumn("Vendidos", format="%d"),
            "Categorías": st.column_config.TextColumn("Categorías", width="medium")
        }
    )
    
    # Botón de exportar
    col_exp1, col_exp2, col_exp3 = st.columns([2, 1, 1])
    with col_exp3:
        csv_data = filtered_table.to_csv(index=False)
        st.download_button(
            label="📥 Exportar Inventario",
            data=csv_data,
            file_name=f"inventario_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    st.markdown("---")
    
    # ═══════════════════════════════════════════════════════════════════
    # SECCIÓN: TOP 10 PRODUCTOS CON MÁS STOCK
    # ═══════════════════════════════════════════════════════════════════
    st.markdown("#### 📦 Top 15 Productos por Stock Disponible")
    
    col_top1, col_top2 = st.columns(2)
    
    with col_top1:
        st.markdown("##### Mayor Cantidad en Stock")
        top_stock = df_products.nlargest(15, 'stock_qty_safe')[['name', 'stock_qty_safe', 'inventory_value']].copy()
        top_stock = top_stock[top_stock['stock_qty_safe'] > 0]
        
        if not top_stock.empty:
            fig_top_stock = px.bar(
                top_stock.sort_values('stock_qty_safe'),
                x='stock_qty_safe',
                y='name',
                orientation='h',
                text='stock_qty_safe',
                color='stock_qty_safe',
                color_continuous_scale=['#6AD2FF', '#4318FF']
            )
            fig_top_stock.update_traces(texttemplate='%{text:.0f} un.', textposition='outside')
            fig_top_stock.update_layout(
                template='plotly_white',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=500,
                yaxis=dict(title=''),
                xaxis=dict(title='', showgrid=False, visible=False),
                coloraxis_showscale=False,
                margin=dict(l=0, r=80, t=0, b=0),
                dragmode=False
            )
            st.plotly_chart(fig_top_stock, use_container_width=True, config=PLOTLY_CONFIG)
        else:
            st.info("No hay productos con stock disponible")
    
    with col_top2:
        st.markdown("##### Mayor Valor en Inventario")
        top_value = df_products.nlargest(15, 'inventory_value')[['name', 'inventory_value', 'stock_qty_safe', 'price_safe']].copy()
        top_value = top_value[top_value['inventory_value'] > 0]
        
        if not top_value.empty:
            fig_top_value = px.bar(
                top_value.sort_values('inventory_value'),
                x='inventory_value',
                y='name',
                orientation='h',
                text='inventory_value',
                color='inventory_value',
                color_continuous_scale=['#FFB547', '#EE5D50']
            )
            fig_top_value.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
            fig_top_value.update_layout(
                template='plotly_white',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=500,
                yaxis=dict(title=''),
                xaxis=dict(title='', showgrid=False, visible=False),
                coloraxis_showscale=False,
                margin=dict(l=0, r=80, t=0, b=0),
                dragmode=False
            )
            st.plotly_chart(fig_top_value, use_container_width=True, config=PLOTLY_CONFIG)
        else:
            st.info("No hay productos con valor en inventario")
    
    st.markdown("---")
    
    # ═══════════════════════════════════════════════════════════════════
    # SECCIÓN: ALERTAS DE STOCK BAJO
    # ═══════════════════════════════════════════════════════════════════
    st.markdown("#### 🔔 Alertas de Stock Bajo")
    st.caption("Productos que requieren atención inmediata o reposición")
    
    # Productos con stock bajo (<=5 unidades y >0)
    low_stock_products = df_products[(df_products['stock_qty_safe'] > 0) & (df_products['stock_qty_safe'] <= 5)].copy()
    
    if not low_stock_products.empty:
        low_stock_products = low_stock_products.sort_values('stock_qty_safe')
        
        # Crear DataFrame para mostrar
        display_low = low_stock_products[['name', 'sku', 'stock_qty_safe', 'price_safe', 'categories', 'total_sales']].copy()
        display_low['total_sales'] = pd.to_numeric(display_low['total_sales'], errors='coerce').fillna(0).astype(int)
        display_low['urgency'] = display_low['stock_qty_safe'].apply(
            lambda x: '🚨 CRÍTICO (1-2)' if x <= 2 else '⚠️ BAJO (3-5)'
        )
        display_low.columns = ['Producto', 'SKU', 'Stock', 'Precio', 'Categorías', 'Vendidos Histórico', 'Urgencia']
        
        col_alert1, col_alert2 = st.columns([2, 1])
        
        with col_alert1:
            st.dataframe(
                format_empty_cells(display_low),
                use_container_width=True,
                height=300,
                column_config={
                    "Producto": st.column_config.TextColumn("Producto", width="large"),
                    "Stock": st.column_config.NumberColumn("Stock", format="%d un."),
                    "Precio": st.column_config.NumberColumn("Precio", format="$%.0f"),
                    "Vendidos Histórico": st.column_config.NumberColumn("Vendidos", format="%d")
                }
            )
        
        with col_alert2:
            critical_count = len(low_stock_products[low_stock_products['stock_qty_safe'] <= 2])
            warning_count = len(low_stock_products[low_stock_products['stock_qty_safe'] > 2])
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #FEE2E2 0%, #FEF3C7 100%); padding: 20px; border-radius: 15px; text-align: center;">
                <h3 style="color: #EE5D50; margin: 0;">⚠️ Resumen de Alertas</h3>
                <hr style="border-color: rgba(0,0,0,0.1);">
                <p style="font-size: 2rem; margin: 10px 0; color: #EE5D50;"><strong>{critical_count}</strong></p>
                <p style="color: #666; margin: 0;">Productos Críticos (1-2 un.)</p>
                <br>
                <p style="font-size: 2rem; margin: 10px 0; color: #FFB547;"><strong>{warning_count}</strong></p>
                <p style="color: #666; margin: 0;">Productos en Alerta (3-5 un.)</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ No hay productos con stock bajo. ¡Inventario en buen estado!")
    
    st.markdown("---")
    
    # ═══════════════════════════════════════════════════════════════════
    # SECCIÓN: PRODUCTOS AGOTADOS
    # ═══════════════════════════════════════════════════════════════════
    st.markdown("#### ❌ Productos Agotados")
    st.caption("Productos sin stock disponible - Pérdidas potenciales de ventas")
    
    out_of_stock_products = df_products[df_products['stock_status'] == 'outofstock'].copy()
    
    if not out_of_stock_products.empty:
        # Calcular ventas perdidas potenciales basadas en ventas históricas
        out_of_stock_products['total_sales'] = pd.to_numeric(out_of_stock_products['total_sales'], errors='coerce').fillna(0)
        out_of_stock_products['potential_monthly_loss'] = (out_of_stock_products['total_sales'] / 12) * out_of_stock_products['price_safe']
        out_of_stock_products = out_of_stock_products.sort_values('potential_monthly_loss', ascending=False)
        
        display_cols_out = out_of_stock_products[['name', 'sku', 'price_safe', 'categories', 'total_sales', 'potential_monthly_loss']].head(20).copy()
        display_cols_out.columns = ['Producto', 'SKU', 'Precio', 'Categorías', 'Vendidos Histórico', 'Pérdida Mensual Est.']
        
        st.dataframe(format_empty_cells(display_cols_out), use_container_width=True, height=300)
        
        # Visualizar pérdida potencial
        if out_of_stock_products['potential_monthly_loss'].sum() > 0:
            st.markdown("##### 💸 Top 10 Productos Agotados por Pérdida Potencial Mensual")
            top_losses = out_of_stock_products.nlargest(10, 'potential_monthly_loss')
            
            fig_loss = px.bar(
                top_losses.sort_values('potential_monthly_loss'), 
                x='potential_monthly_loss', 
                y='name', 
                orientation='h',
                text='potential_monthly_loss'
            )
            fig_loss.update_traces(
                marker_color='#EE5D50', 
                texttemplate='$%{text:,.0f}/mes', 
                textposition='outside'
            )
            fig_loss.update_layout(
                template='plotly_white',
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)',
                height=450,
                yaxis=dict(title=''),
                xaxis=dict(title='', showgrid=False),
                margin=dict(l=0, r=80, t=0, b=0),
                dragmode=False
            )
            st.plotly_chart(fig_loss, use_container_width=True, config=PLOTLY_CONFIG)
    else:
        st.success("✅ No hay productos agotados. ¡Excelente gestión de inventario!")
    
    st.markdown("---")
    
    # ═══════════════════════════════════════════════════════════════════
    # SECCIÓN: ANÁLISIS DE ROTACIÓN
    # ═══════════════════════════════════════════════════════════════════
    st.markdown("#### 🔄 Análisis de Rotación de Inventario")
    st.caption("Velocidad de venta vs stock disponible - Basado en el periodo seleccionado")
    
    if not df_items.empty:
        # Calcular velocidad de venta (unidades por día)
        days_in_period = max((end_date - start_date).days, 1)
        
        rotation_data = df_items.groupby('product_id').agg(
            product_name=('product_name', 'first'),
            units_sold=('quantity', 'sum'),
            revenue=('total', 'sum')
        ).reset_index()
        
        rotation_data['velocity'] = rotation_data['units_sold'] / days_in_period
        
        # Merge con datos de stock
        rotation_df = rotation_data.merge(
            df_products[['product_id', 'stock_qty_safe', 'price_safe']], 
            on='product_id', 
            how='left'
        )
        
        rotation_df['stock_qty_safe'] = rotation_df['stock_qty_safe'].fillna(0)
        rotation_df['days_until_stockout'] = rotation_df.apply(
            lambda x: (x['stock_qty_safe'] / x['velocity']) if x['velocity'] > 0 else float('inf'),
            axis=1
        )
        
        # Clasificar productos por rotación
        rotation_df['rotation_class'] = rotation_df.apply(
            lambda x: '🔥 ALTA' if x['velocity'] >= 1 else 
                     ('📊 MEDIA' if x['velocity'] >= 0.3 else '🐌 BAJA'),
            axis=1
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 🔥 Productos de Alta Rotación")
            st.caption("Mayor velocidad de venta - requieren reposición frecuente")
            
            high_rotation = rotation_df[rotation_df['rotation_class'] == '🔥 ALTA'].copy()
            if not high_rotation.empty:
                high_rotation = high_rotation.nlargest(10, 'velocity')
                
                display_hr = high_rotation[['product_name', 'velocity', 'stock_qty_safe', 'days_until_stockout']].copy()
                display_hr['velocity'] = display_hr['velocity'].round(2)
                display_hr['days_until_stockout'] = display_hr['days_until_stockout'].apply(
                    lambda x: f"{x:.0f}" if x != float('inf') else "∞"
                )
                display_hr.columns = ['Producto', 'Unid/día', 'Stock Actual', 'Días hasta agotarse']
                
                st.dataframe(format_empty_cells(display_hr), use_container_width=True, height=350)
            else:
                st.info("No hay productos de alta rotación en el periodo")
        
        with col2:
            st.markdown("##### 🐌 Productos de Baja Rotación")
            st.caption("Menor velocidad de venta - posible sobrestock")
            
            low_rotation = rotation_df[rotation_df['rotation_class'] == '🐌 BAJA'].copy()
            if not low_rotation.empty:
                # Ordenar por valor inmovilizado (stock * precio)
                low_rotation['immobilized_value'] = low_rotation['stock_qty_safe'] * low_rotation['price_safe']
                low_rotation = low_rotation.nlargest(10, 'immobilized_value')
                
                display_lr = low_rotation[['product_name', 'velocity', 'stock_qty_safe', 'immobilized_value']].copy()
                display_lr['velocity'] = display_lr['velocity'].round(2)
                display_lr['immobilized_value'] = display_lr['immobilized_value'].round(0)
                display_lr.columns = ['Producto', 'Unid/día', 'Stock Actual', 'Valor Inmovilizado']
                
                st.dataframe(format_empty_cells(display_lr), use_container_width=True, height=350)
            else:
                st.info("No hay productos de baja rotación")
        
        # Gráfico de rotación
        st.markdown("##### 📊 Distribución de Rotación de Productos")
        rotation_summary = rotation_df['rotation_class'].value_counts().reset_index()
        rotation_summary.columns = ['Clase', 'Cantidad']
        
        colors_rotation = {'🔥 ALTA': '#EE5D50', '📊 MEDIA': '#FFB547', '🐌 BAJA': '#4318FF'}
        
        fig_rotation = px.pie(
            rotation_summary, 
            values='Cantidad', 
            names='Clase',
            hole=0.65,
            color='Clase',
            color_discrete_map=colors_rotation
        )
        fig_rotation.update_traces(
            textinfo='label+percent+value',
            textfont=dict(size=12),
            hovertemplate='<b>%{label}</b><br>%{value} productos<br>%{percent}<extra></extra>'
        )
        fig_rotation.update_layout(
            template='plotly_white',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=380,
            showlegend=True,
            legend=dict(orientation="h", y=-0.1, x=0.5, xanchor="center"),
            dragmode=False
        )
        st.plotly_chart(fig_rotation, use_container_width=True, config=PLOTLY_CONFIG)
    else:
        st.info("ℹ️ No hay datos de ventas en el periodo para calcular rotación")


def view_customer_analytics(df_orders_all):
    """Customer Analytics: Top Clientes por Compras, Top por Gasto, Directorio de Clientes"""
    start_date, end_date = show_time_selector()
    
    st.markdown("### 👥 Customer Analytics")
    
    # Filter orders by date
    mask = (df_orders_all['date_created'] >= start_date) & (df_orders_all['date_created'] <= end_date)
    df_orders = df_orders_all.loc[mask].copy()
    
    if df_orders.empty:
        st.warning("No hay datos para el periodo seleccionado")
        return
    
    # Agregar datos por cliente (combina registrados y guests por email)
    def get_customer_key(row):
        if row['customer_id'] > 0:
            return f"reg_{row['customer_id']}"
        elif row['customer_email']:
            return f"guest_{row['customer_email']}"
        else:
            return f"order_{row['order_id']}"
    
    df_orders['customer_key'] = df_orders.apply(get_customer_key, axis=1)
    
    # Agregar por cliente
    customer_stats = df_orders.groupby('customer_key').agg(
        customer_id=('customer_id', 'first'),
        customer_name=('customer_name', 'first'),
        customer_email=('customer_email', 'first'),
        billing_city=('billing_city', 'first'),
        billing_state=('billing_state', 'first'),
        billing_phone=('billing_phone', 'first'),
        total_spent=('total', 'sum'),
        order_count=('order_id', 'count'),
        first_order=('date_created', 'min'),
        last_order=('date_created', 'max')
    ).reset_index()
    
    # Limpiar nombre de cliente
    customer_stats['display_name'] = customer_stats.apply(
        lambda x: x['customer_name'] if pd.notna(x['customer_name']) and x['customer_name'].strip() 
        else (x['customer_email'].split('@')[0] if pd.notna(x['customer_email']) else 'Cliente Anónimo'),
        axis=1
    )
    
    # === KPIs ===
    total_customers = len(customer_stats)
    registered = len(customer_stats[customer_stats['customer_id'] > 0])
    guests = total_customers - registered
    avg_order_value = df_orders['total'].mean()
    repeat_customers = len(customer_stats[customer_stats['order_count'] > 1])
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        metric_card("Total Clientes", f"{total_customers:,}", icon="fa-users", color="#4318FF")
    with col2:
        metric_card("Registrados", f"{registered:,}", icon="fa-user-check", color="#05CD99")
    with col3:
        metric_card("Invitados", f"{guests:,}", icon="fa-user-secret", color="#FFB547")
    with col4:
        metric_card("Recurrentes", f"{repeat_customers:,}", icon="fa-rotate", color="#6AD2FF",
                   help_text="Clientes con más de 1 compra")
    with col5:
        metric_card("Ticket Promedio", f"${avg_order_value:,.0f}", icon="fa-receipt", color="#EE5D50")
    
    st.markdown("---")
    
    # === NUEVA LÓGICA: PODIO + TABLA DETALLADA ===
    
    # --- Controles de Ordenamiento ---
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        sort_metric = st.selectbox("Ordenar por", ["Compras (#)", "Gasto ($)"], index=1) # Default Gasto
    with col_c2:
        sort_order = st.selectbox("Orden", ["Descendente (Mayor a Menor)", "Ascendente (Menor a Mayor)"], index=0)
    with col_c3:
        top_n = st.number_input("Cantidad a mostrar", min_value=5, max_value=50, value=15)
        
    # Determinar columna de ordenamiento
    metric_col = 'order_count' if 'Compras' in sort_metric else 'total_spent'
    ascending_bool = True if 'Ascendente' in sort_order else False
    
    # Aplicar ordenamiento
    stats_sorted = customer_stats.sort_values(metric_col, ascending=ascending_bool).head(top_n)
    
    # Podio Logic (Top 3)
    # Solo mostramos podio visual si es descendente (Top mejores)
    if not ascending_bool:
        st.markdown(f"#### 🏆 Podio de Clientes")
        
        # Preparar colores de medallas
        medals = ['🥇', '🥈', '🥉']
        colors = ['#FFD700', '#C0C0C0', '#CD7F32'] # Gold, Silver, Bronze
        bg_colors = ['rgba(255, 215, 0, 0.1)', 'rgba(192, 192, 192, 0.1)', 'rgba(205, 127, 50, 0.1)']
        
        col_pod1, col_pod2, col_pod3 = st.columns(3)
        cols = [col_pod1, col_pod2, col_pod3]
        
        for i in range(3):
            if i < len(stats_sorted):
                row = stats_sorted.iloc[i]
                with cols[i]:
                    name = row['display_name'] if row['display_name'] else row['customer_email'][:15]
                    val_display = f"${row['total_spent']:,.0f}" if metric_col == 'total_spent' else f"{row['order_count']} pedidos"
                    
                    st.markdown(f"""
                    <div style="
                        background-color: {bg_colors[i]};
                        border: 1px solid {colors[i]};
                        border-radius: 10px;
                        padding: 15px;
                        text-align: center;
                        height: 100%;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    ">
                        <div style="font-size: 2rem;">{medals[i]}</div>
                        <div style="font-weight: bold; color: #2B3674; margin-top: 5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{name}</div>
                        <div style="font-size: 1.2rem; color: {colors[i]}; font-weight: 700;">{val_display}</div>
                    </div>
                    """, unsafe_allow_html=True)
        st.markdown("---")
    
    # Tabla Detallada
    st.markdown(f"#### 📋 Detalle Top {top_n}")
    
    # Preparar tabla para visualización
    display_df = stats_sorted[['display_name', 'customer_email', 'order_count', 'total_spent', 'last_order']].copy()
    display_df.columns = ['Cliente', 'Email', 'Pedidos', 'Total Gastado', 'Última Compra']
    
    # Formato condicional básico
    st.dataframe(
        display_df,
        use_container_width=True,
        height=max(400, top_n * 35),
        column_config={
            "Cliente": st.column_config.TextColumn("👤 Cliente", width="medium"),
            "Email": st.column_config.TextColumn("📧 Email", width="medium"),
            "Pedidos": st.column_config.NumberColumn("🛒 Pedidos", format="%d"),
            "Total Gastado": st.column_config.NumberColumn("💰 Total Gastado", format="$%d"),
            "Última Compra": st.column_config.DateColumn("📅 Última Compra", format="DD/MM/YYYY")
        },
        hide_index=True
    )
    
    st.markdown("---")
    
    # === DIRECTORIO COMPLETO DE CLIENTES CON BUSCADOR ===
    st.markdown("#### 📋 Directorio Completo de Clientes")
    st.caption("Busca por nombre, email, ciudad o teléfono")
    
    # Buscador
    search_term = st.text_input(
        "🔍 Buscar cliente",
        placeholder="Escribe nombre, email, ciudad o teléfono...",
        key="customer_search"
    )
    
    # Preparar datos para mostrar
    display_customers = customer_stats.copy()
    
    # Mapear códigos de región a nombres
    region_map = {
        'CL_329': 'Metropolitana',
        'CL_408': 'Valparaíso',
        'CL_261': 'Biobío',
        'CL_220': 'La Araucanía',
        'CL_313': 'Los Lagos',
        'CL_235': "O'Higgins",
        'CL_387': 'Coquimbo',
        'CL_350': 'Maule',
        'CL_394': 'Antofagasta',
        'CL_381': 'Atacama',
        'CL_232': 'Ñuble',
        'CL_211': 'Arica y Parinacota',
        'CL_207': 'Tarapacá',
        'CL_271': 'Los Ríos',
        'CL_281': 'Aysén',
        'CL_289': 'Magallanes'
    }
    
    display_customers['region'] = display_customers['billing_state'].map(region_map).fillna(display_customers['billing_state'])
    display_customers['ubicacion'] = display_customers.apply(
        lambda x: f"{x['billing_city'] or ''}, {x['region'] or ''}".strip(', '),
        axis=1
    )
    
    # Filtrar por búsqueda
    if search_term:
        search_lower = search_term.lower()
        mask = (
            display_customers['display_name'].str.lower().str.contains(search_lower, na=False) |
            display_customers['customer_email'].str.lower().str.contains(search_lower, na=False) |
            display_customers['billing_city'].str.lower().str.contains(search_lower, na=False) |
            display_customers['billing_phone'].str.contains(search_term, na=False) |
            display_customers['region'].str.lower().str.contains(search_lower, na=False)
        )
        display_customers = display_customers[mask]
    
    # Ordenar por total gastado por defecto
    display_customers = display_customers.sort_values('total_spent', ascending=False)
    
    # Preparar columnas para mostrar
    table_df = display_customers[['display_name', 'customer_email', 'billing_phone', 'ubicacion', 'order_count', 'total_spent', 'first_order', 'last_order']].copy()
    table_df.columns = ['Nombre', 'Email', 'Teléfono', 'Ubicación', 'Pedidos', 'Total Gastado', 'Primera Compra', 'Última Compra']
    
    # Formatear fechas
    table_df['Primera Compra'] = pd.to_datetime(table_df['Primera Compra']).dt.strftime('%d/%m/%Y')
    table_df['Última Compra'] = pd.to_datetime(table_df['Última Compra']).dt.strftime('%d/%m/%Y')
    
    # Mostrar conteo
    st.caption(f"📊 Mostrando **{len(table_df):,}** clientes")
    
    # Mostrar tabla
    st.dataframe(
        format_empty_cells(table_df),
        use_container_width=True,
        height=500,
        column_config={
            "Nombre": st.column_config.TextColumn("👤 Nombre", width="medium"),
            "Email": st.column_config.TextColumn("📧 Email", width="medium"),
            "Teléfono": st.column_config.TextColumn("📱 Teléfono", width="small"),
            "Ubicación": st.column_config.TextColumn("📍 Ubicación", width="medium"),
            "Pedidos": st.column_config.NumberColumn("🛒 Pedidos", format="%d"),
            "Total Gastado": st.column_config.NumberColumn("💰 Total", format="$%,.0f"),
            "Primera Compra": st.column_config.TextColumn("📅 Primera", width="small"),
            "Última Compra": st.column_config.TextColumn("📅 Última", width="small")
        }
    )
    
    st.markdown("---")
    
    # (Distribución de Frecuencia eliminada por solicitud del usuario)


def view_all_orders(df_orders_all):
    """Vista de todas las ventas con opción de agrupar por día."""
    start_date, end_date = show_time_selector()
    
    # Filtrar por periodo
    mask = (df_orders_all['date_created'] >= start_date) & (df_orders_all['date_created'] <= end_date)
    df_orders = df_orders_all.loc[mask].copy()
    
    if df_orders.empty:
        st.warning("No hay órdenes en el periodo seleccionado.")
        return
    
    # Load order items for product details
    df_items = load_data('wc_order_items')
    
    # === VIEW MODE TOGGLE ===
    st.markdown("### 📋 Historial de Órdenes")
    
    col_toggle, col_spacer = st.columns([2, 3])
    with col_toggle:
        view_mode = st.radio(
            "Modo de Vista:",
            ["📋 Por Órdenes", "📅 Por Día"],
            horizontal=True,
            key="orders_view_mode",
            label_visibility="collapsed"
        )
    
    st.markdown("---")
    
    # Mapear estados a español con emojis
    status_map = {
        'completed': '✅ Completado',
        'completoenviado': '📦 Completo-Enviado',
        'processing': '⏳ Procesando',
        'porsalir': '🚚 Por Salir',
        'on-hold': '⏸️ En Espera',
        'pending': '⏰ Pendiente',
        'cancelled': '❌ Cancelado',
        'refunded': '↩️ Reembolsado',
        'failed': '⚠️ Fallido'
    }
    
    if view_mode == "📅 Por Día":
        # ========== DAY GROUPED VIEW ==========
        st.caption("Selecciona un día para ver y descargar el detalle de entregas")
        
        # Group orders by day for the date selector
        df_orders['date_only_str'] = df_orders['date_created'].dt.strftime('%Y-%m-%d')
        available_dates = sorted(df_orders['date_only_str'].unique(), reverse=True)
        
        # Day selector and download button in same row
        col_select, col_download = st.columns([3, 1])
        
        with col_select:
            selected_date = st.selectbox(
                "📅 Seleccionar Fecha:",
                options=available_dates,
                format_func=lambda x: datetime.strptime(x, '%Y-%m-%d').strftime('%A %d de %B, %Y').title(),
                key="select_date_for_detail"
            )
        
        # Filter orders for selected day
        df_day = df_orders[df_orders['date_only_str'] == selected_date].copy()
        
        with col_download:
            # PDF Download button
            st.markdown("<div style='margin-top: 25px;'>", unsafe_allow_html=True)
            try:
                from utils.export import ReportExporter
                
                # Filter items for this day's orders
                day_order_ids = df_day['order_id'].tolist()
                df_day_items = df_items[df_items['order_id'].isin(day_order_ids)] if not df_items.empty else pd.DataFrame()
                
                pdf_bytes = ReportExporter.export_daily_orders_pdf(
                    df_day, 
                    df_day_items, 
                    selected_date,
                    company_name=COMPANY_NAME
                )
                
                st.download_button(
                    label="📥 Descargar PDF del Día",
                    data=pdf_bytes,
                    file_name=f"entregas_{selected_date}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    type="primary"
                )
            except Exception as e:
                st.error(f"Error generando PDF: {str(e)}")
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Day summary metrics
        date_display = datetime.strptime(selected_date, '%Y-%m-%d').strftime('%A %d de %B, %Y').title()
        st.markdown(f"### 📦 Entregas del {date_display}")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            metric_card("Total Pedidos", f"{len(df_day):,}", icon="fa-receipt", color="#4318FF")
        with col2:
            metric_card("Ventas del Día", f"${df_day['total'].sum():,.0f}", icon="fa-dollar-sign", color="#05CD99")
        with col3:
            metric_card("Ticket Promedio", f"${df_day['total'].mean():,.0f}" if len(df_day) > 0 else "$0", icon="fa-chart-line", color="#FFB547")
        with col4:
            shipping_total = df_day['shipping_total'].sum() if 'shipping_total' in df_day.columns else 0
            metric_card("Costo Envío", f"${shipping_total:,.0f}", icon="fa-truck", color="#6AD2FF")
        
        st.markdown("---")
        
        # Detail view for each order
        for idx, (_, order) in enumerate(df_day.sort_values('order_id').iterrows()):
            order_id = order['order_id']
            customer_name = order.get('customer_name', 'Guest') or 'Guest'
            customer_email = order.get('customer_email', '') or ''
            customer_phone = order.get('billing_phone', '') or 'Sin teléfono'
            city = order.get('billing_city', '') or ''
            state = order.get('billing_state', '') or ''
            location = f"{city}, {state}" if city and state else city or state or 'N/A'
            status = order.get('status', '')
            status_text = status_map.get(status, status)
            total = order.get('total', 0)
            shipping_method = order.get('shipping_method', 'N/A') or 'N/A'
            
            # Order card using expander
            with st.expander(f"📦 **Pedido #{order_id}** - {customer_name} - ${total:,.0f} - {status_text}", expanded=False):
                col_info, col_products = st.columns([1, 1])
                
                with col_info:
                    st.markdown("**👤 Información del Cliente**")
                    st.markdown(f"- **Nombre:** {customer_name}")
                    st.markdown(f"- **Teléfono:** {customer_phone}")
                    if customer_email:
                        st.markdown(f"- **Email:** {customer_email}")
                    st.markdown(f"- **Ubicación:** {location}")
                    st.markdown(f"- **Envío:** {shipping_method}")
                    
                    st.markdown("---")
                    st.markdown("**💰 Totales**")
                    total = float(order.get('total', 0))
                    shipping_cost = float(order.get('shipping_total', 0) or 0)
                    discount = float(order.get('discount_total', 0) or 0)
                    
                    # En Chile el IVA es 19% incluido en el total
                    # Calculamos el neto (subtotal) y el IVA
                    total_iva = total * 0.19 / 1.19
                    neto = total - total_iva - shipping_cost + discount
                    
                    st.markdown(f"- Subtotal (Neto): **${neto:,.0f}**")
                    st.markdown(f"- IVA (19%): **${total_iva:,.0f}**")
                    if shipping_cost > 0:
                        st.markdown(f"- Envío: **${shipping_cost:,.0f}**")
                    if discount > 0:
                        st.markdown(f"- Descuento: **-${discount:,.0f}**")
                    st.markdown(f"- **TOTAL: ${total:,.0f}**")
                
                with col_products:
                    st.markdown("**📦 Productos**")
                    order_items = df_items[df_items['order_id'] == order_id] if not df_items.empty else pd.DataFrame()
                    
                    if not order_items.empty:
                        for _, item in order_items.iterrows():
                            product_name = item.get('product_name', 'Producto')
                            quantity = int(item.get('quantity', 1))
                            price = float(item.get('price', 0))
                            item_total = float(item.get('total', quantity * price))
                            st.markdown(f"- {product_name} x{quantity} = **${item_total:,.0f}**")
                    else:
                        st.caption("Sin detalle de productos")
                
                # Download individual order PDF button
                st.markdown("---")
                try:
                    from utils.export import ReportExporter
                    
                    # Convert Series to dict for the function
                    order_dict = order.to_dict()
                    order_items_df = df_items[df_items['order_id'] == order_id] if not df_items.empty else pd.DataFrame()
                    
                    pdf_bytes = ReportExporter.export_single_order_pdf(
                        order_dict,
                        order_items_df,
                        company_name=COMPANY_NAME
                    )
                    
                    st.download_button(
                        label="📥 Descargar PDF de este Pedido",
                        data=pdf_bytes,
                        file_name=f"pedido_{order_id}.pdf",
                        mime="application/pdf",
                        key=f"download_order_{order_id}",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Error generando PDF: {str(e)}")
            
            # Add separator between orders
            if idx < len(df_day) - 1:
                st.markdown("")
    
    else:
        # ========== TRADITIONAL ORDER LIST VIEW ==========
        st.caption("Listado completo de órdenes ordenadas de la más reciente a la más antigua")
        
        # Ordenar de más reciente a más antigua
        df_orders = df_orders.sort_values('date_created', ascending=False)
        
        # Métricas resumen
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            metric_card("Total Órdenes", f"{len(df_orders):,}", icon="fa-receipt", color="#4318FF")
        with col2:
            metric_card("Ventas Totales", f"${df_orders['total'].sum():,.0f}", icon="fa-dollar-sign", color="#05CD99")
        with col3:
            metric_card("Ticket Promedio", f"${df_orders['total'].mean():,.0f}", icon="fa-chart-line", color="#FFB547")
        with col4:
            completed = len(df_orders[df_orders['status'].isin(['completed', 'completoenviado'])])
            metric_card("Completadas", f"{completed:,}", icon="fa-check-circle", color="#6AD2FF")
        
        st.markdown("---")
        
        # Preparar DataFrame para mostrar
        display_df = df_orders.copy()
        
        # Crear columna de ubicación combinada
        def get_location(row):
            city = row.get('billing_city', '') or ''
            state = row.get('billing_state', '') or ''
            if city and state:
                return f"{city}, {state}"
            return city or state or 'N/A'
        
        display_df['Ubicación'] = display_df.apply(get_location, axis=1)
        
        # Formatear fecha
        display_df['Fecha'] = display_df['date_created'].dt.strftime('%d/%m/%Y %H:%M')
        
        display_df['Estado'] = display_df['status'].map(lambda x: status_map.get(x, x))
        
        # Formatear monto
        display_df['Monto'] = display_df['total'].apply(lambda x: f"${x:,.0f}")
        
        # Obtener nombre del cliente
        display_df['Cliente'] = display_df.apply(
            lambda x: x['customer_name'] if pd.notna(x.get('customer_name')) and x.get('customer_name') else 
                      (x['customer_email'].split('@')[0] if pd.notna(x.get('customer_email')) and x.get('customer_email') else 'Guest'),
            axis=1
        )
        
        # Buscar órdenes
        search_query = st.text_input("🔍 Buscar por cliente, email o ID de orden", placeholder="Escribe para buscar...")
        
        if search_query:
            search_lower = search_query.lower()
            display_df = display_df[
                display_df['customer_name'].fillna('').str.lower().str.contains(search_lower) |
                display_df['customer_email'].fillna('').str.lower().str.contains(search_lower) |
                display_df['order_id'].astype(str).str.contains(search_query)
            ]
        
        # Filtro por estado
        unique_statuses = display_df['status'].unique().tolist()
        selected_status = st.multiselect(
            "Filtrar por estado",
            options=unique_statuses,
            default=[],
            format_func=lambda x: status_map.get(x, x)
        )
        
        if selected_status:
            display_df = display_df[display_df['status'].isin(selected_status)]
        
        st.markdown(f"**Mostrando {len(display_df):,} órdenes**")
        
        # Seleccionar columnas para mostrar
        columns_to_show = ['order_id', 'Fecha', 'Cliente', 'Estado', 'Monto', 'Ubicación']
        
        # Verificar que las columnas existan
        available_cols = [col for col in columns_to_show if col in display_df.columns]
        
        # Renombrar columnas para mejor display
        rename_map = {'order_id': '# Orden'}
        final_df = display_df[available_cols].rename(columns=rename_map)
        
        # Mostrar tabla con estilo
        st.dataframe(
            format_empty_cells(final_df),
            use_container_width=True,
            height=600,
            column_config={
                "# Orden": st.column_config.NumberColumn("# Orden", format="%d"),
                "Fecha": st.column_config.TextColumn("Fecha"),
                "Cliente": st.column_config.TextColumn("Cliente"),
                "Estado": st.column_config.TextColumn("Estado"),
                "Monto": st.column_config.TextColumn("Monto"),
                "Ubicación": st.column_config.TextColumn("Ubicación")
            }
        )
        
        # Opción de exportar
        st.markdown("---")
        col1, col2 = st.columns([3, 1])
        with col2:
            csv = display_df[['order_id', 'date_created', 'customer_name', 'customer_email', 'status', 'total', 'Ubicación']].to_csv(index=False)
            st.download_button(
                label="📥 Exportar a CSV",
                data=csv,
                file_name=f"ventas_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )




def view_taxes(df_orders_all):
    """Vista de ayuda para declaración de impuestos en Chile."""
    from datetime import datetime
    
    st.markdown("### 🏛️ Impuestos y Declaraciones")
    st.caption("Ayuda para la declaración de impuestos en Chile - Operación Renta y IVA")
    
    # Obtener año actual y anterior
    current_year = datetime.now().year
    tax_year = current_year - 1  # El año fiscal a declarar es el anterior
    
    # Selector de año fiscal
    col_year, col_info = st.columns([1, 2])
    with col_year:
        selected_year = st.selectbox(
            "📅 Año Fiscal a Analizar",
            options=[current_year, current_year - 1, current_year - 2],
            index=1,  # Por defecto el año anterior
            help="Selecciona el año calendario para calcular impuestos"
        )
    
    with col_info:
        if selected_year == tax_year:
            st.success(f"✅ Este es el año que debes declarar en Abril {current_year}")
        elif selected_year == current_year:
            st.info(f"ℹ️ Este año se declara en Abril {current_year + 1}")
        else:
            st.warning(f"⚠️ Este año ya debió declararse")
    
    # Filtrar datos del año seleccionado
    if df_orders_all.empty:
        st.warning("No hay datos de órdenes disponibles.")
        return
    
    df_year = df_orders_all[
        (df_orders_all['date_created'].dt.year == selected_year)
    ].copy()
    
    if df_year.empty:
        st.warning(f"No hay ventas registradas para el año {selected_year}")
        return
    
    # Calcular métricas fiscales
    # En Chile, el IVA es 19% incluido en el precio
    # Ventas Netas = Total / 1.19
    # IVA = Total - Ventas Netas
    IVA_RATE = 0.19
    
    total_ventas = df_year['total'].sum()
    ventas_netas = total_ventas / (1 + IVA_RATE)
    iva_total = total_ventas - ventas_netas
    total_ordenes = len(df_year)
    ticket_promedio = total_ventas / total_ordenes if total_ordenes > 0 else 0
    
    # KPIs principales
    st.markdown("---")
    st.markdown("#### 📊 Resumen Fiscal del Año")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("Ventas Brutas", f"${total_ventas:,.0f}", icon="fa-cash-register", color="#4318FF", help_text="Total facturado")
    with col2:
        metric_card("Ventas Netas", f"${ventas_netas:,.0f}", icon="fa-file-invoice-dollar", color="#05CD99", help_text="Sin IVA")
    with col3:
        metric_card("IVA Devengado", f"${iva_total:,.0f}", icon="fa-landmark", color="#EE5D50", help_text="19% incluido")
    with col4:
        metric_card("Total Órdenes", f"{total_ordenes:,}", icon="fa-receipt", color="#FFB547")
    
    st.markdown("---")
    
    # === SECCIÓN: ESTIMADOR IMPUESTO A LA RENTA ===
    st.markdown("#### 💼 Estimador Impuesto a la Renta (Primera Categoría)")
    st.caption("Cálculo aproximado basado en margen de utilidad estimado")
    
    # Controles para el estimador
    col_margin, col_regime, col_info = st.columns([1, 1, 1])
    
    with col_margin:
        margen_utilidad = st.slider(
            "📊 Margen de Utilidad Estimado",
            min_value=10,
            max_value=80,
            value=30,
            step=5,
            format="%d%%",
            help="Porcentaje de las ventas netas que representa tu utilidad después de costos y gastos"
        )
    
    with col_regime:
        regimen_tributario = st.selectbox(
            "🏢 Régimen Tributario",
            options=["General (27%)", "Pro-PyME (25%)"],
            index=1,  # Pro-PyME por defecto para PyMEs
            help="Régimen General: 27% | Pro-PyME: 25% (empresas < 75.000 UF)"
        )
    
    with col_info:
        st.info("💡 El cálculo es estimativo. Consulta con tu contador para el cálculo exacto.")
    
    # Calcular Impuesto a la Renta
    tasa_impuesto = 0.27 if "27%" in regimen_tributario else 0.25
    utilidad_estimada = ventas_netas * (margen_utilidad / 100)
    impuesto_renta = utilidad_estimada * tasa_impuesto
    tasa_efectiva = (impuesto_renta / total_ventas * 100) if total_ventas > 0 else 0
    
    # KPIs de Impuesto a la Renta
    col_ir1, col_ir2, col_ir3, col_ir4 = st.columns(4)
    with col_ir1:
        metric_card(
            "Utilidad Estimada", 
            f"${utilidad_estimada:,.0f}", 
            icon="fa-chart-line", 
            color="#7551FF",
            help_text=f"{margen_utilidad}% de ventas netas"
        )
    with col_ir2:
        metric_card(
            "Imp. Renta Estimado", 
            f"${impuesto_renta:,.0f}", 
            icon="fa-building-columns", 
            color="#EE5D50",
            help_text=f"Tasa: {int(tasa_impuesto*100)}%"
        )
    with col_ir3:
        metric_card(
            "Tasa Efectiva", 
            f"{tasa_efectiva:.2f}%", 
            icon="fa-percent", 
            color="#FFB547",
            help_text="Sobre ventas brutas"
        )
    with col_ir4:
        # Carga tributaria total (IVA + Renta)
        carga_total = iva_total + impuesto_renta
        metric_card(
            "Carga Tributaria Total", 
            f"${carga_total:,.0f}", 
            icon="fa-scale-balanced", 
            color="#2B3674",
            help_text="IVA + Imp. Renta"
        )
    
    st.markdown("---")
    
    # Desglose mensual
    col_table, col_chart = st.columns([1, 1])
    
    with col_table:
        st.markdown("#### 📅 Desglose Mensual")
        
        df_year['mes'] = df_year['date_created'].dt.month
        df_year['mes_nombre'] = df_year['date_created'].dt.strftime('%B')
        
        monthly = df_year.groupby('mes').agg(
            Ventas_Brutas=('total', 'sum'),
            Ordenes=('order_id', 'count')
        ).reset_index()
        
        monthly['Ventas_Netas'] = monthly['Ventas_Brutas'] / (1 + IVA_RATE)
        monthly['IVA'] = monthly['Ventas_Brutas'] - monthly['Ventas_Netas']
        
        # Agregar columnas de Impuesto a la Renta (usando margen y tasa seleccionados)
        monthly['Utilidad_Est'] = monthly['Ventas_Netas'] * (margen_utilidad / 100)
        monthly['Imp_Renta'] = monthly['Utilidad_Est'] * tasa_impuesto
        
        # Nombre de meses en español
        meses_es = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
                    7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}
        monthly['Mes'] = monthly['mes'].map(meses_es)
        
        display_monthly = monthly[['Mes', 'Ventas_Brutas', 'Ventas_Netas', 'IVA', 'Utilidad_Est', 'Imp_Renta', 'Ordenes']].copy()
        display_monthly.columns = ['Mes', 'Ventas Brutas', 'Ventas Netas', 'IVA', 'Utilidad Est.', 'Imp. Renta', 'Órdenes']
        
        # Formatear montos
        for col in ['Ventas Brutas', 'Ventas Netas', 'IVA', 'Utilidad Est.', 'Imp. Renta']:
            display_monthly[col] = display_monthly[col].apply(lambda x: f"${x:,.0f}")
        
        st.dataframe(format_empty_cells(display_monthly), use_container_width=True, height=430, hide_index=True)
    
    with col_chart:
        st.markdown("#### 📈 Evolución Mensual")
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=monthly['Mes'], 
            y=monthly['Ventas_Netas'], 
            name='Ventas Netas',
            marker_color='#05CD99',
            text=monthly['Ventas_Netas'].apply(lambda x: f"${x/1000:.0f}K"),
            textposition='outside'
        ))
        fig.add_trace(go.Bar(
            x=monthly['Mes'], 
            y=monthly['IVA'], 
            name='IVA',
            marker_color='#EE5D50',
            text=monthly['IVA'].apply(lambda x: f"${x/1000:.0f}K"),
            textposition='outside'
        ))
        fig.update_layout(
            barmode='stack',
            template='plotly_white',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=450,
            legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
            margin=dict(l=10, r=10, t=10, b=60)
        )
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    
    st.markdown("---")
    
    # Fechas importantes
    st.markdown("#### 🗓️ Fechas Importantes de Declaración")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #3311DD 0%, #5832EE 100%); 
                    padding: 20px; border-radius: 16px; color: white; margin-bottom: 15px;
                    box-shadow: 0 8px 24px rgba(67, 24, 255, 0.4);'>
            <h4 style='margin: 0 0 10px 0; color: white; font-weight: 700;'>📋 Operación Renta (F22)</h4>
            <p style='margin: 5px 0; font-size: 0.95rem;'><strong>Período:</strong> 1 al 30 de Abril</p>
            <p style='margin: 5px 0; font-size: 0.95rem;'><strong>Año a declarar:</strong> Ingresos del año anterior</p>
            <p style='margin: 5px 0; font-size: 0.85rem; opacity: 0.95;'>La propuesta de declaración del SII estará disponible desde el 1 de Abril</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #00B386 0%, #00D47C 100%); 
                    padding: 20px; border-radius: 16px; color: white; margin-bottom: 15px;
                    box-shadow: 0 8px 24px rgba(5, 205, 153, 0.4);'>
            <h4 style='margin: 0 0 10px 0; color: white; font-weight: 700;'>📊 IVA Mensual (F29)</h4>
            <p style='margin: 5px 0; font-size: 0.95rem;'><strong>Período:</strong> Hasta el día 12 de cada mes</p>
            <p style='margin: 5px 0; font-size: 0.95rem;'><strong>Empresas pequeñas:</strong> Hasta el día 20</p>
            <p style='margin: 5px 0; font-size: 0.85rem; opacity: 0.95;'>Declaración del IVA del mes anterior</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Recordatorio según fecha actual
    today = datetime.now()
    if today.month == 4:
        st.warning("⚠️ **¡Estamos en Abril!** Este es el mes de la Operación Renta. Recuerda declarar antes del 30 de Abril.")
    elif today.month == 3:
        st.info("ℹ️ **Próximo mes es Abril** - Prepárate para la Operación Renta. Revisa tus documentos.")
    
    st.markdown("---")
    
    # Exportar datos para el SII
    st.markdown("#### 📥 Exportar Datos para el SII")
    
    col1, col2, col3 = st.columns(3)
    
    # Preparar datos para exportar
    export_df = df_year[['order_id', 'date_created', 'customer_name', 'customer_email', 
                         'status', 'total', 'billing_city', 'billing_state']].copy()
    export_df['ventas_netas'] = export_df['total'] / (1 + IVA_RATE)
    export_df['iva'] = export_df['total'] - export_df['ventas_netas']
    export_df['date_created'] = export_df['date_created'].dt.strftime('%Y-%m-%d')
    export_df.columns = ['ID Orden', 'Fecha', 'Cliente', 'Email', 'Estado', 
                         'Total Bruto', 'Ciudad', 'Región', 'Ventas Netas', 'IVA']
    
    with col1:
        csv_detail = export_df.to_csv(index=False)
        st.download_button(
            label="📄 Detalle Ventas (CSV)",
            data=csv_detail,
            file_name=f"ventas_detalle_{selected_year}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # Resumen mensual (con Impuesto a la Renta)
        monthly_export = monthly[['Mes', 'Ventas_Brutas', 'Ventas_Netas', 'IVA', 'Utilidad_Est', 'Imp_Renta', 'Ordenes']].copy()
        monthly_export.columns = ['Mes', 'Ventas Brutas', 'Ventas Netas', 'IVA', 'Utilidad Estimada', 'Imp. Renta', 'Cantidad Órdenes']
        csv_monthly = monthly_export.to_csv(index=False)
        st.download_button(
            label="📊 Resumen Mensual (CSV)",
            data=csv_monthly,
            file_name=f"resumen_mensual_{selected_year}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col3:
        # Resumen anual (con Impuesto a la Renta)
        regimen_texto = 'General (27%)' if tasa_impuesto == 0.27 else 'Pro-PyME (25%)'
        resumen_anual = f"""RESUMEN FISCAL {selected_year}
================================

--- VENTAS E IVA ---
Ventas Brutas: ${total_ventas:,.0f}
Ventas Netas: ${ventas_netas:,.0f}
IVA Total (19%): ${iva_total:,.0f}

--- IMPUESTO A LA RENTA ---
Régimen Tributario: {regimen_texto}
Margen de Utilidad Aplicado: {margen_utilidad}%
Utilidad Estimada: ${utilidad_estimada:,.0f}
Impuesto a la Renta Estimado: ${impuesto_renta:,.0f}

--- CARGA TRIBUTARIA TOTAL ---
IVA + Impuesto Renta: ${carga_total:,.0f}
Tasa Efectiva sobre Ventas: {tasa_efectiva:.2f}%

--- RESUMEN ---
Total Órdenes: {total_ordenes:,}
Ticket Promedio: ${ticket_promedio:,.0f}

⚠️ NOTA: El cálculo de Impuesto a la Renta es estimativo.
Consulte con su contador para el cálculo exacto.

Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
        st.download_button(
            label="📋 Resumen Anual (TXT)",
            data=resumen_anual,
            file_name=f"resumen_fiscal_{selected_year}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    # Información adicional
    with st.expander("ℹ️ Información sobre Impuestos en Chile"):
        st.markdown("""
        ### Tipos de Declaración
        
        **1. Operación Renta (Formulario 22)**
        - Se realiza una vez al año en **Abril**
        - Declara los ingresos del año calendario anterior
        - Puede resultar en pago de impuestos o devolución
        
        **2. IVA Mensual (Formulario 29)**
        - Se declara mensualmente
        - Plazo: día 12 del mes siguiente (o 20 para Pymes)
        - Impuesto al Valor Agregado del 19%
        
        **3. PPM (Pagos Provisionales Mensuales)**
        - Anticipos del impuesto a la renta
        - Se declaran junto con el F29
        
        ### Enlaces Útiles
        - [Portal SII](https://www.sii.cl)
        - [Mi SII](https://misifonos.sii.cl)
        - [Calendario Tributario](https://www.sii.cl/servicios_online/calendario/)
        
        ### Consideraciones
        - Los montos mostrados son aproximados basados en las ventas registradas
        - Consulta con un contador para obligaciones tributarias específicas
        - El cálculo de IVA asume que está incluido en el precio (19%)
        """)


def main():
    # --- SIDEBAR NAVIGATION ---
    with st.sidebar:
        # Logo - Premium Glassmorphism Style
        import base64
        logo_path = os.path.join(os.path.dirname(__file__), 'assets', 'generic_logo.png')
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as f:
                logo_data = base64.b64encode(f.read()).decode()
            st.markdown(
                f"""
                <div style='text-align: center; padding: 20px 15px 25px 15px;'>
                    <div style="
                        background: rgba(255, 255, 255, 0.05);
                        backdrop-filter: blur(20px);
                        border: 1px solid rgba(255, 255, 255, 0.1);
                        border-radius: 16px;
                        padding: 15px;
                        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                    ">
                        <img src="data:image/png;base64,{logo_data}" style="max-width: 80%; height: auto; filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));">
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div style='text-align: center; padding: 20px 15px 25px 15px;'>
                    <div style="
                        background: rgba(255, 255, 255, 0.05);
                        backdrop-filter: blur(20px);
                        border: 1px solid rgba(255, 255, 255, 0.1);
                        border-radius: 16px;
                        padding: 15px;
                        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                    ">
                        <span style="font-size: 2rem;">{APP_ICON}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        # Modern Navigation Menu with Color-coded Status
        # st.markdown("### Navigation")  # Oculto para look más limpio
        
        # Define view options with modern names (no emojis) and their SVG icons
        view_icons = {
            "Dashboard KPIs": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>""",
            "Análisis de Ventas": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>""",
            "Historial de Órdenes": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>""",
            "Catálogo de Productos": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>""",
            "Segmentación de Clientes": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>""",
            "Tráfico y Redes Sociales": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>""",
            "Impuestos y Declaraciones": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>""",
            "Setup": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 1v6m0 6v6M5.6 5.6l4.2 4.2m4.2 4.2l4.2 4.2M1 12h6m6 0h6M5.6 18.4l4.2-4.2m4.2-4.2l4.2-4.2"/></svg>""",
            "System Reset": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>"""
        }
        
        view_options = [
            ("Dashboard KPIs", "Dashboard KPIs"),
            ("Análisis de Ventas", "Análisis de Ventas"),
            ("Historial de Órdenes", "Historial de Órdenes"),
            ("Catálogo de Productos", "Catálogo de Productos"),
            ("Segmentación de Clientes", "Segmentación de Clientes"),
            ("Tráfico y Redes Sociales", "Tráfico y Redes Sociales"),
            ("Impuestos y Declaraciones", "Impuestos y Declaraciones"),
            ("Setup", "Setup"),
            ("System Reset", "System Reset")
        ]
        
        # Initialize selected view
        if 'selected_view_key' not in st.session_state:
            st.session_state.selected_view_key = "Dashboard KPIs"
        
        # Status color mapping
        status_colors = {
            'active': {'border': '#05CD99', 'bg': 'rgba(5, 205, 153, 0.1)', 'hover_bg': 'rgba(5, 205, 153, 0.2)'},
            'partial': {'border': '#FFB547', 'bg': 'rgba(255, 181, 71, 0.1)', 'hover_bg': 'rgba(255, 181, 71, 0.2)'},
            'locked': {'border': '#A3AED0', 'bg': 'rgba(163, 174, 208, 0.05)', 'hover_bg': 'rgba(163, 174, 208, 0.1)'}
        }
        
        # Render each navigation item
        for i, (display_name, view_name) in enumerate(view_options):
            # Get status
            if view_name in ["System Reset", "Setup"]:
                status = 'active'  # Always accessible
            else:
                status = views_status.get(view_name, 'locked')
            
            is_selected = st.session_state.selected_view_key == view_name
            is_disabled = status == 'locked'
            
            colors = status_colors[status]
            icon_svg = view_icons.get(view_name, "")
            
            # Determine background and text color
            if is_selected:
                bg_color = colors['border']  # Solid color when selected
                text_color = '#FFFFFF'
                border_width = '4px'
            else:
                bg_color = colors['bg']  # Light color when not selected
                text_color = '#FFFFFF'
                border_width = '3px'
            
            # Glassmorphism button styling - match reference image
            if is_selected:
                btn_bg = 'linear-gradient(135deg, rgba(0, 150, 255, 0.2) 0%, rgba(0, 100, 200, 0.15) 100%)'
                btn_border = '1px solid rgba(0, 200, 255, 0.3)'
                btn_border_right = 'none'
                btn_border_left = 'none'
                btn_boxshadow = 'inset 0 1px 0 rgba(255, 255, 255, 0.1), 0 4px 20px rgba(0, 180, 255, 0.2), 0 0 30px rgba(0, 200, 255, 0.15), 3px 0 15px rgba(0, 212, 255, 0.3)'
                icon_bg = 'rgba(0, 200, 255, 0.25)'
                icon_boxshadow = '0 0 10px rgba(0, 200, 255, 0.3)'
                text_color_btn = '#FFFFFF'
                font_weight = '500'
                # Right border glow for selected item
                right_border = '3px solid #00d4ff'
                translate_x = '4px'
            elif is_disabled:
                btn_bg = 'rgba(40, 40, 60, 0.3)'
                btn_border = '1px solid rgba(255, 255, 255, 0.05)'
                btn_border_right = 'none'
                btn_border_left = 'none'
                btn_boxshadow = 'none'
                icon_bg = 'rgba(255, 255, 255, 0.05)'
                icon_boxshadow = 'none'
                text_color_btn = 'rgba(255, 255, 255, 0.4)'
                font_weight = '400'
                right_border = 'none'
                translate_x = '0px'
            else:
                btn_bg = 'linear-gradient(135deg, rgba(40, 40, 60, 0.6) 0%, rgba(30, 30, 50, 0.4) 100%)'
                btn_border = '1px solid rgba(255, 255, 255, 0.08)'
                btn_border_right = 'none'
                btn_border_left = 'none'
                btn_boxshadow = 'inset 0 1px 0 rgba(255, 255, 255, 0.05), 0 2px 8px rgba(0, 0, 0, 0.2)'
                icon_bg = 'rgba(255, 255, 255, 0.08)'
                icon_boxshadow = 'none'
                text_color_btn = 'rgba(255, 255, 255, 0.7)'
                font_weight = '400'
                right_border = 'none'
                translate_x = '0px'
            
            # Create custom styled button HTML with glassmorphism
            button_html = f"""
            <div class="glass-sidebar-btn{' selected' if is_selected else ''}{' disabled' if is_disabled else ''}" style="
                display: flex;
                align-items: center;
                padding: 14px 18px;
                margin: 6px 12px;
                border-radius: 12px;
                background: {btn_bg};
                border: {btn_border};
                border-right: {right_border};
                box-shadow: {btn_boxshadow};
                cursor: {'not-allowed' if is_disabled else 'pointer'};
                opacity: {'0.5' if is_disabled else '1'};
                transition: all 0.3s ease;
                font-weight: {font_weight};
                color: {text_color_btn};
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
            ">
                <div style="margin-right: 14px; display: flex; align-items: center; justify-content: center; width: 32px; height: 32px; background: {icon_bg}; border-radius: 8px; box-shadow: {icon_boxshadow};">
                    {icon_svg}
                </div>
                <div style="flex: 1; font-size: 0.95rem;">
                    {display_name}
                </div>
            </div>
            """
            
            # Use st.button with html in markdown for visual, track clicks separately
            button_key = f"nav_btn_{i}_{view_name.replace(' ', '_')}"
            
            if not is_disabled:
                # Show clickable version
                if st.button(
                    display_name,
                    key=button_key,
                    use_container_width=True,
                    type="secondary",
                    disabled=False
                ):
                    st.session_state.selected_view_key = view_name
                    st.rerun()
                    
                # Override button appearance with glassmorphism CSS
                st.markdown(f"""
                <style>
                    button[data-testid="baseButton-secondary"]:has(p:contains("{display_name}")) {{
                        background: {btn_bg} !important;
                        border: {btn_border} !important;
                        border-right: {right_border} !important;
                        border-radius: 12px !important;
                        padding: 14px 18px !important;
                        color: {text_color_btn} !important;
                        font-weight: {font_weight} !important;
                        box-shadow: {btn_boxshadow} !important;
                        backdrop-filter: blur(20px) !important;
                        -webkit-backdrop-filter: blur(20px) !important;
                        transition: all 0.3s ease !important;
                    }}
                    button[data-testid="baseButton-secondary"]:has(p:contains("{display_name}")):hover {{
                        background: linear-gradient(135deg, rgba(50, 50, 70, 0.7) 0%, rgba(40, 40, 60, 0.5) 100%) !important;
                        border-color: rgba(0, 200, 255, 0.2) !important;
                        transform: translateX(4px) !important;
                        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.1), 0 4px 20px rgba(0, 0, 0, 0.3), 0 0 20px rgba(0, 180, 255, 0.1) !important;
                        color: rgba(255, 255, 255, 0.9) !important;
                    }}
                </style>
                """, unsafe_allow_html=True)
            else:
                # Show disabled version
                st.markdown(button_html, unsafe_allow_html=True)
        
        # Set selected_view based on session state
        selected_view = st.session_state.selected_view_key
        
        st.markdown("---")
        
        # Configuration status and link to setup
        config_status = check_configuration_status()
        missing_configs = get_missing_configuration()
        
        if missing_configs:
            st.warning(f"⚠️ Configuración incompleta: {', '.join(missing_configs)}")
            st.markdown("""
                <div style='text-align: center; margin: 10px 0;'>
                    <a href='/setup' target='_self' style='text-decoration: none;'>
                        <button style='border: none; background: #FFB547; color: white; padding: 10px 20px; border-radius: 10px; cursor: pointer; font-weight: bold; width: 100%;'>
                            ⚙️ Configurar Credenciales
                        </button>
                    </a>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.success("✅ Sistema configurado")
            if st.button("⚙️ Configuración", use_container_width=True):
                st.switch_page("pages/setup.py")
        
        
        st.markdown("---")
        
        # ETL Refresh Button with options
        st.markdown("### 🔄 Actualización de Datos")
        
        refresh_option = st.radio(
            "Tipo de actualización:",
            ["Solo recargar vista", "Extraer datos nuevos"],
            label_visibility="collapsed",
            horizontal=True,
            key="refresh_type"
        )
        
        if st.button("🔄 Actualizar Datos", use_container_width=True, type="primary"):
            if refresh_option == "Solo recargar vista":
                # Simple cache clear
                st.cache_data.clear()
                st.success("✅ Vista actualizada")
                st.rerun()
            else:
                # Run ETL extractors with detailed progress
                st.info("🚀 Ejecutando extractores ETL...")
                
                # Import ETL runner
                sys.path.append(str(project_root / 'utils'))
                from etl_runner import run_all_etl_extractors
                
                # Create progress placeholder
                progress_placeholder = st.empty()
                
                with progress_placeholder.container():
                    st.markdown("#### Progreso de Extracción")
                    
                    # Check configuration
                    config_check = check_configuration_status()
                    
                    extractors_to_run = []
                    if config_check.get('woocommerce'):
                        extractors_to_run.append('WooCommerce')
                    if config_check.get('google_analytics'):
                        extractors_to_run.append('Google Analytics')
                    if config_check.get('facebook'):
                        extractors_to_run.append('Facebook')
                    
                    if not extractors_to_run:
                        st.warning("⚠️ No hay servicios configurados para extraer datos")
                    else:
                        st.info(f"📊 Extractores a ejecutar: {', '.join(extractors_to_run)}")
                        st.markdown("---")
                        
                        # Create status containers for each extractor
                        extractor_status = {}
                        extractor_progress = {}
                        
                        for extractor in extractors_to_run:
                            with st.container():
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    extractor_status[extractor] = st.empty()
                                    extractor_status[extractor].info(f"⏳ {extractor}: Preparando...")
                                with col2:
                                    extractor_progress[extractor] = st.empty()
                        
                        st.markdown("---")
                        
                        # Run extractors and update status in real-time
                        import subprocess
                        import time
                        
                        results = {}
                        
                        # Map extractor names to script files
                        extractor_scripts = {
                            'WooCommerce': 'etl/extract_woocommerce.py',
                            'Google Analytics': 'etl/extract_analytics.py',
                            'Facebook': 'etl/extract_facebook.py'
                        }
                        
                        for idx, extractor in enumerate(extractors_to_run):
                            # Update status
                            extractor_status[extractor].warning(f"🔄 {extractor}: Ejecutando extracción...")
                            extractor_progress[extractor].progress((idx) / len(extractors_to_run), 
                                                                   text=f"Extractor {idx + 1}/{len(extractors_to_run)}")
                            
                            script_path = extractor_scripts.get(extractor)
                            if script_path:
                                try:
                                    # Run the extractor
                                    result = subprocess.run(
                                        ['python', script_path],
                                        cwd=str(project_root),
                                        capture_output=True,
                                        text=True,
                                        timeout=300  # 5 minutes timeout
                                    )
                                    
                                    if result.returncode == 0:
                                        extractor_status[extractor].success(f"✅ {extractor}: Completado exitosamente")
                                        results[extractor] = {'status': 'success', 'message': 'Completado'}
                                    else:
                                        extractor_status[extractor].error(f"❌ {extractor}: Error en extracción")
                                        results[extractor] = {
                                            'status': 'error',
                                            'message': 'Error en extracción',
                                            'output': result.stderr
                                        }
                                except subprocess.TimeoutExpired:
                                    extractor_status[extractor].error(f"❌ {extractor}: Timeout (>5 min)")
                                    results[extractor] = {'status': 'error', 'message': 'Timeout'}
                                except Exception as e:
                                    extractor_status[extractor].error(f"❌ {extractor}: {str(e)}")
                                    results[extractor] = {'status': 'error', 'message': str(e)}
                            
                            # Update progress bar
                            extractor_progress[extractor].progress((idx + 1) / len(extractors_to_run),
                                                                   text="Completado")
                        
                        # Final summary
                        st.markdown("---")
                        st.markdown("#### Resumen Final")
                        
                        all_success = all(r.get('status') == 'success' for r in results.values())
                        
                        # Show any errors
                        for extractor_name, result in results.items():
                            if result.get('status') == 'error' and result.get('output'):
                                with st.expander(f"Ver detalles de error - {extractor_name}"):
                                    st.code(result['output'])
                        
                        if all_success:
                            st.success("✅ Todos los extractores completados exitosamente")
                            st.balloons()
                            
                            # Clear cache and reload
                            if st.button("🔄 Recargar Dashboard", use_container_width=True):
                                st.cache_data.clear()
                                st.rerun()
                        else:
                            st.warning("⚠️ Algunos extractores fallaron. Revisa los detalles arriba.")
                            st.markdown("**Sugerencias:**")
                            st.markdown("- Verifica tu conexión a internet")
                            st.markdown("- Revisa las credenciales en la página de Configuración")
                            st.markdown("- Consulta los logs en `logs/etl.log`")

        st.markdown("---")
        
        # ===== v1.2: EXPORT SECTION =====
        st.markdown("### 📥 Exportar")
        
        export_format = st.selectbox(
            "Formato",
            ["Excel", "PDF"],
            key='export_format',
            label_visibility="collapsed"
        )
        
        # Limpiar reporte previo si se cambia el formato
        if 'last_export_format' not in st.session_state:
            st.session_state.last_export_format = export_format
        
        if st.session_state.last_export_format != export_format:
            if 'generated_report' in st.session_state:
                del st.session_state['generated_report']
            st.session_state.last_export_format = export_format

        if st.button("📥 Generar", use_container_width=True):
            from utils.export import ReportExporter
            
            try:
                df_orders = load_data('wc_orders', filter_valid_statuses=True)
                
                if not df_orders.empty:
                    # Asegurar que las fechas son objetos datetime
                    df_orders['date_created'] = pd.to_datetime(df_orders['date_created'])
                    
                    with st.spinner("Generando..."):
                        if export_format == "Excel":
                            data = ReportExporter.create_summary_export(
                                df_orders,
                                start_date=df_orders['date_created'].min().strftime('%Y-%m-%d'),
                                end_date=df_orders['date_created'].max().strftime('%Y-%m-%d')
                            )
                            filename = ReportExporter.export_to_excel(data)
                            
                            with open(filename, 'rb') as f:
                                st.session_state['generated_report'] = {
                                    'data': f.read(),
                                    'filename': filename,
                                    'mime': "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    'format': 'Excel'
                                }
                        else:
                            metrics = {
                                'Ventas': f"${df_orders['total'].sum():,.0f}",
                                'Órdenes': f"{len(df_orders):,}",
                                'Promedio': f"${df_orders['total'].mean():,.0f}"
                            }
                            filename = ReportExporter.export_to_pdf(metrics)
                            
                            with open(filename, 'rb') as f:
                                st.session_state['generated_report'] = {
                                    'data': f.read(),
                                    'filename': filename,
                                    'mime': "application/pdf",
                                    'format': 'PDF'
                                }
                else:
                    st.warning("Sin datos")
            except Exception as e:
                st.error(f"Error: {str(e)}")
        
        # Botón de descarga persistente
        if 'generated_report' in st.session_state:
            report = st.session_state['generated_report']
            st.download_button(
                label=f"💾 Descargar {report['format']}",
                data=report['data'],
                file_name=report['filename'],
                mime=report['mime'],
                use_container_width=True,
                key='sidebar_persistent_download'
            )
            st.success("✅ ¡Reporte listo para descargar!")
        
        st.markdown("---")
        
        # ===== v1.2: PERIOD COMPARISON =====
        st.markdown("### 📈 Comparar")
        
        comparison_mode = st.selectbox(
            "Con:",
            ["Sin comparación", "Período anterior", "Año pasado"],
            key='comparison_mode',
            label_visibility="collapsed"
        )
        # Note: No need to set st.session_state.comparison_mode - the widget with key does it automatically

    # Store selected view in session state for unique keys
    st.session_state['view'] = selected_view

    # --- MAIN CONTENT ---
    # Load Data (sin filtros, las vistas se encargan del filtrado)
    df_orders = load_data('wc_orders', filter_valid_statuses=True)
    df_items = load_data('wc_order_items')
    df_ga = load_data('ga4_ecommerce', DATABASE_ANALYTICS)
    df_ga_traffic = load_data('ga4_traffic_sources', DATABASE_ANALYTICS)
    df_fb = load_data('fb_page_insights', DATABASE_FACEBOOK)
    
    # Process Data
    if not df_orders.empty:
        df_orders['date_created'] = pd.to_datetime(df_orders['date_created'])
        df_orders['date_only'] = df_orders['date_created'].dt.date
        # IMPORTANTE: WooCommerce "Ventas totales" = total + shipping_total
        # Crear columna ventas_totales para coincidir con reportes de WooCommerce
        df_orders['ventas_totales'] = df_orders['total'] + df_orders['shipping_total'].fillna(0)
    
    if not df_ga.empty:
        # Fix: Convert integer YYYYMMDD to string before parsing
        df_ga['Fecha'] = pd.to_datetime(df_ga['Fecha'].astype(str), format='%Y%m%d')
        df_ga['date_only'] = df_ga['Fecha'].dt.date

    #--- ROUTING WITH ACCESS VALIDATION ---
    # Handle special pages first (Setup and System Reset)
    if selected_view == "Setup":
        st.switch_page("pages/setup.py")
    elif selected_view == "System Reset":
        st.switch_page("pages/03_⚙️_System_Reset.py")
    else:
        # Regular views with access validation
        current_view_name = selected_view
        
        if not can_access_view(current_view_name):
            # View is locked - show locked view message
            missing_services = get_missing_services_for_view(current_view_name)
            render_locked_view(current_view_name, missing_services)
        else:
            # View is accessible - render normally
            if selected_view == "Dashboard KPIs":
                view_summary(df_orders, df_ga)
            elif selected_view == "Historial de Órdenes":
                view_all_orders(df_orders)
            elif selected_view == "Análisis de Ventas":
                view_sales(df_orders, df_ga)
            elif selected_view == "Catálogo de Productos":
                view_products(df_items, df_orders)
            elif selected_view == "Segmentación de Clientes":
                view_customer_analytics(df_orders)
            elif selected_view == "Tráfico y Redes Sociales":
                view_traffic(df_orders, df_ga, df_ga_traffic, df_fb)
            elif selected_view == "Impuestos y Declaraciones":
                view_taxes(df_orders)
            else:
                if df_orders.empty:
                    st.warning("No hay datos de pedidos.")

if __name__ == "__main__":
    main()
