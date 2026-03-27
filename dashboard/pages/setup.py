"""
Setup Configuration Page

Streamlit page for configuring API credentials for WooCommerce, 
Google Analytics, and Facebook.
"""

import streamlit as st
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from config.settings import (
    WooCommerceConfig, 
    GoogleAnalyticsConfig, 
    FacebookConfig,
    check_configuration_status
)
from config.config_validator import (
    validate_woocommerce,
    validate_google_analytics,
    validate_facebook
)

# Page configuration
st.set_page_config(
    page_title="Configuration Setup",
    page_icon="⚙️",
    layout="wide"
)

# Title
st.title("⚙️ Configuration Setup")
st.markdown("Configure your API credentials for WooCommerce, Google Analytics, and Facebook.")

# Back to Dashboard button
col_back, col_empty = st.columns([1, 4])
with col_back:
    if st.button("← Back to Dashboard", use_container_width=True):
        st.switch_page("app_woo_v2.py")

st.markdown("---")

# Check current configuration status
config_status = check_configuration_status()

# Helper function to save .env file
def save_to_env(data: dict):
    """Save configuration data to .env file"""
    env_path = project_root / '.env'
    
    # Read existing .env content if it exists
    existing_content = {}
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    existing_content[key] = value
    
    # Update with new data
    existing_content.update(data)
    
    # Write back to .env
    with open(env_path, 'w') as f:
        f.write("# ========================================\n")
        f.write("# CONFIGURACIÓN DE CREDENCIALES\n")
        f.write("# ========================================\n")
        f.write("# Generado automáticamente via interfaz web\n\n")
        
        # WooCommerce section
        if any(k.startswith('WC_') for k in existing_content):
            f.write("# ========================================\n")
            f.write("# WOOCOMMERCE API\n")
            f.write("# ========================================\n")
            for key in ['WC_URL', 'WC_CONSUMER_KEY', 'WC_CONSUMER_SECRET']:
                if key in existing_content:
                    f.write(f"{key}={existing_content[key]}\n")
            f.write("\n")
        
        # Google Analytics section
        if any(k.startswith('GA4_') for k in existing_content):
            f.write("# ========================================\n")
            f.write("# GOOGLE ANALYTICS 4\n")
            f.write("# ========================================\n")
            for key in ['GA4_KEY_FILE', 'GA4_PROPERTY_ID']:
                if key in existing_content:
                    f.write(f"{key}={existing_content[key]}\n")
            f.write("\n")
        
        # Facebook section
        if any(k.startswith('FB_') for k in existing_content):
            f.write("# ========================================\n")
            f.write("# FACEBOOK PAGE INSIGHTS\n")
            f.write("# ========================================\n")
            for key in ['FB_ACCESS_TOKEN', 'FB_PAGE_ID', 'FB_API_VERSION']:
                if key in existing_content:
                    f.write(f"{key}={existing_content[key]}\n")
            f.write("\n")
        
        # Company/Emisor section
        if any(k.startswith('COMPANY_') for k in existing_content):
            f.write("# ========================================\n")
            f.write("# DATOS DE LA EMPRESA (EMISOR PDF)\n")
            f.write("# ========================================\n")
            for key in ['COMPANY_NAME', 'COMPANY_ADDRESS', 'COMPANY_CITY', 'COMPANY_PHONE', 'COMPANY_EMAIL', 'COMPANY_RUT']:
                if key in existing_content:
                    f.write(f"{key}={existing_content[key]}\n")
            f.write("\n")
    
    return True

# Create tabs for each service
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 WooCommerce", "📈 Google Analytics", "📱 Facebook", "🏢 Empresa", "📋 Status"])

# ==================== TAB 1: WOOCOMMERCE ====================
with tab1:
    st.header("WooCommerce Configuration")
    
    # Show current status
    if config_status['woocommerce']:
        st.success("✅ WooCommerce is currently configured")
    else:
        st.warning("⚠️ WooCommerce is not configured")
    
    st.markdown("### Enter your WooCommerce credentials")
    st.markdown("Find these at: **WooCommerce > Settings > Advanced > REST API**")
    
    # Form for WooCommerce
    with st.form("wc_form"):
        wc_url = st.text_input(
            "Store URL",
            value=os.getenv('WC_URL', ''),
            placeholder="https://your-store.com",
            help="Your WooCommerce store URL (e.g., https://example.com)"
        )
        
        wc_ck = st.text_input(
            "Consumer Key",
            value=os.getenv('WC_CONSUMER_KEY', ''),
            type="password",
            placeholder="ck_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            help="WooCommerce Consumer Key"
        )
        
        wc_cs = st.text_input(
            "Consumer Secret",
            value=os.getenv('WC_CONSUMER_SECRET', ''),
            type="password",
            placeholder="cs_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            help="WooCommerce Consumer Secret"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            test_wc = st.form_submit_button("🔍 Test Connection", use_container_width=True)
        with col2:
            save_wc = st.form_submit_button("💾 Save Configuration", type="primary", use_container_width=True)
    
    # Handle WooCommerce test
    if test_wc:
        if wc_url and wc_ck and wc_cs:
            with st.spinner("Testing WooCommerce connection..."):
                success, message = validate_woocommerce(wc_url, wc_ck, wc_cs)
                if success:
                    st.success(message)
                else:
                    st.error(message)
        else:
            st.error("Please fill in all WooCommerce fields")
    
    # Handle WooCommerce save
    if save_wc:
        if wc_url and wc_ck and wc_cs:
            data = {
                'WC_URL': wc_url,
                'WC_CONSUMER_KEY': wc_ck,
                'WC_CONSUMER_SECRET': wc_cs
            }
            if save_to_env(data):
                st.success("✅ WooCommerce configuration saved to .env file!")
                st.info("Please restart the application to use the new configuration")
        else:
            st.error("Please fill in all WooCommerce fields")

# ==================== TAB 2: GOOGLE ANALYTICS ====================
with tab2:
    st.header("Google Analytics 4 Configuration")
    
    # Show current status
    if config_status['google_analytics']:
        st.success("✅ Google Analytics is currently configured")
    else:
        st.warning("⚠️ Google Analytics is not configured")
    
    st.markdown("### Enter your Google Analytics 4 credentials")
    st.markdown("Find these at: **Google Cloud Console > Service Accounts**")
    
    # Form for GA4
    with st.form("ga4_form"):
        # File uploader for JSON key
        uploaded_file = st.file_uploader(
            "Service Account JSON File",
            type=['json'],
            help="Upload your Google Cloud Service Account JSON key file"
        )
        
        # Show current key file if exists
        current_key_file = os.getenv('GA4_KEY_FILE', '')
        if current_key_file and not uploaded_file:
            st.info(f"Current key file: {current_key_file}")
        
        ga4_property = st.text_input(
            "GA4 Property ID",
            value=os.getenv('GA4_PROPERTY_ID', ''),
            placeholder="123456789",
            help="Your Google Analytics 4 Property ID (numbers only)"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            test_ga4 = st.form_submit_button("🔍 Test Connection", use_container_width=True)
        with col2:
            save_ga4 = st.form_submit_button("💾 Save Configuration", type="primary", use_container_width=True)
    
    # Handle GA4 test
    if test_ga4:
        key_file_to_test = current_key_file
        
        # If new file uploaded, save it temporarily
        if uploaded_file:
            temp_key_path = project_root / uploaded_file.name
            with open(temp_key_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            key_file_to_test = str(temp_key_path)
        
        if key_file_to_test and ga4_property:
            with st.spinner("Testing Google Analytics connection..."):
                success, message = validate_google_analytics(key_file_to_test, ga4_property)
                if success:
                    st.success(message)
                else:
                    st.error(message)
        else:
            st.error("Please upload a JSON key file and enter Property ID")
    
    # Handle GA4 save
    if save_ga4:
        if uploaded_file and ga4_property:
            # Save JSON file
            key_file_path = project_root / uploaded_file.name
            with open(key_file_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            # Save to .env
            data = {
                'GA4_KEY_FILE': uploaded_file.name,
                'GA4_PROPERTY_ID': ga4_property
            }
            if save_to_env(data):
                st.success(f"✅ Google Analytics configuration saved!")
                st.success(f"📁 Key file saved as: {uploaded_file.name}")
                st.info("Please restart the application to use the new configuration")
        elif current_key_file and ga4_property:
            # Just update property ID
            data = {
                'GA4_KEY_FILE': current_key_file,
                'GA4_PROPERTY_ID': ga4_property
            }
            if save_to_env(data):
                st.success("✅ Google Analytics configuration saved!")
                st.info("Please restart the application to use the new configuration")
        else:
            st.error("Please upload a JSON key file and enter Property ID")

# ==================== TAB 3: FACEBOOK ====================
with tab3:
    st.header("Facebook Page Insights Configuration")
    
    # Show current status
    if config_status['facebook']:
        st.success("✅ Facebook is currently configured")
    else:
        st.warning("⚠️ Facebook is not configured")
    
    st.markdown("### Enter your Facebook credentials")
    st.markdown("Generate token at: **[Facebook Graph API Explorer](https://developers.facebook.com/tools/explorer/)**")
    
    # Form for Facebook
    with st.form("fb_form"):
        fb_token = st.text_input(
            "Access Token",
            value=os.getenv('FB_ACCESS_TOKEN', ''),
            type="password",
            placeholder="EAAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            help="Facebook User or Page Access Token"
        )
        
        fb_page_id = st.text_input(
            "Page ID",
            value=os.getenv('FB_PAGE_ID', ''),
            placeholder="1234567890123456",
            help="Your Facebook Page ID (find in Page Settings)"
        )
        
        fb_api_version = st.selectbox(
            "API Version",
            options=["v19.0", "v18.0", "v17.0", "v16.0"],
            index=0,
            help="Facebook Graph API version"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            test_fb = st.form_submit_button("🔍 Test Connection", use_container_width=True)
        with col2:
            save_fb = st.form_submit_button("💾 Save Configuration", type="primary", use_container_width=True)
    
    # Handle Facebook test
    if test_fb:
        if fb_token and fb_page_id:
            with st.spinner("Testing Facebook connection..."):
                success, message = validate_facebook(fb_token, fb_page_id, fb_api_version)
                if success:
                    st.success(message)
                else:
                    st.error(message)
        else:
            st.error("Please fill in all Facebook fields")
    
    # Handle Facebook save
    if save_fb:
        if fb_token and fb_page_id:
            data = {
                'FB_ACCESS_TOKEN': fb_token,
                'FB_PAGE_ID': fb_page_id,
                'FB_API_VERSION': fb_api_version
            }
            if save_to_env(data):
                st.success("✅ Facebook configuration saved to .env file!")
                st.info("Please restart the application to use the new configuration")
        else:
            st.error("Please fill in all Facebook fields")

# ==================== TAB 4: EMPRESA/EMISOR ====================
with tab4:
    st.header("🏢 Datos de la Empresa (Emisor)")
    st.markdown("Estos datos aparecerán en los PDFs de pedidos como información del emisor.")
    
    # Show current status
    current_company = os.getenv('COMPANY_NAME', '')
    if current_company:
        st.success(f"✅ Empresa configurada: {current_company}")
    else:
        st.warning("⚠️ Los datos de la empresa no están configurados")
    
    # Form for Company data
    with st.form("company_form"):
        st.markdown("### Información del Emisor")
        
        company_name = st.text_input(
            "Nombre de la Empresa *",
            value=os.getenv('COMPANY_NAME', 'Mi Empresa'),
            placeholder="Tu Empresa S.A.",
            help="Nombre que aparecerá en los PDFs"
        )
        
        company_rut = st.text_input(
            "RUT (opcional)",
            value=os.getenv('COMPANY_RUT', ''),
            placeholder="76.123.456-0",
            help="RUT de la empresa"
        )
        
        company_address = st.text_input(
            "Dirección",
            value=os.getenv('COMPANY_ADDRESS', ''),
            placeholder="Av. Principal 1234, Of. 567",
            help="Dirección de la empresa"
        )
        
        company_city = st.text_input(
            "Ciudad",
            value=os.getenv('COMPANY_CITY', ''),
            placeholder="Santiago, Chile",
            help="Ciudad y país"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            company_phone = st.text_input(
                "Teléfono",
                value=os.getenv('COMPANY_PHONE', ''),
                placeholder="+56 9 1234 5678",
                help="Teléfono de contacto"
            )
        with col2:
            company_email = st.text_input(
                "Email",
                value=os.getenv('COMPANY_EMAIL', ''),
                placeholder="contacto@tuempresa.com",
                help="Email de contacto"
            )
        
        save_company = st.form_submit_button("💾 Guardar Configuración", type="primary", use_container_width=True)
    
    # Handle Company save
    if save_company:
        if company_name:
            data = {
                'COMPANY_NAME': company_name,
            }
            if company_rut:
                data['COMPANY_RUT'] = company_rut
            if company_address:
                data['COMPANY_ADDRESS'] = company_address
            if company_city:
                data['COMPANY_CITY'] = company_city
            if company_phone:
                data['COMPANY_PHONE'] = company_phone
            if company_email:
                data['COMPANY_EMAIL'] = company_email
            
            if save_to_env(data):
                st.success("✅ Configuración de empresa guardada!")
                st.info("Por favor reinicia la aplicación para usar la nueva configuración")
        else:
            st.error("Por favor ingresa al menos el nombre de la empresa")
    
    # Preview
    st.markdown("---")
    st.markdown("### 👁️ Vista previa en PDF")
    st.markdown("Así se verá en los PDFs de pedidos:")
    
    preview_name = os.getenv('COMPANY_NAME', 'Mi Empresa')
    preview_rut = os.getenv('COMPANY_RUT', '')
    preview_address = os.getenv('COMPANY_ADDRESS', '')
    preview_city = os.getenv('COMPANY_CITY', '')
    preview_phone = os.getenv('COMPANY_PHONE', '')
    preview_email = os.getenv('COMPANY_EMAIL', '')
    
    preview_html = f"""
    <div style="background:#f8f9fa; padding:15px; border-radius:8px; border-left:4px solid #3182ce;">
        <div style="color:#1a365d; font-size:18px; font-weight:bold;">{preview_name}</div>
        <div style="color:#3182ce; font-size:12px;">EMISOR</div>
        <div style="color:#4a5568; font-size:12px; margin-top:8px;">
            {f'RUT: {preview_rut}<br/>' if preview_rut else ''}
            {f'{preview_address}<br/>' if preview_address else ''}
            {f'{preview_city}<br/>' if preview_city else ''}
            {f'📞 {preview_phone}<br/>' if preview_phone else ''}
            {f'✉ {preview_email}' if preview_email else ''}
        </div>
    </div>
    """
    st.markdown(preview_html, unsafe_allow_html=True)

# ==================== TAB 5: STATUS ====================
with tab5:
    st.header("Configuration Status")
    
    st.markdown("### Current Configuration")
    
    # WooCommerce status
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("📊 WooCommerce")
    with col2:
        if config_status['woocommerce']:
            st.success("✅ Configured")
        else:
            st.error("❌ Not Configured")
    
    if config_status['woocommerce']:
        st.markdown(f"- **URL**: {os.getenv('WC_URL', 'Not set')}")
        st.markdown(f"- **Consumer Key**: `{'*' * 20}...` (hidden)")
    
    st.markdown("---")
    
    # Google Analytics status
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("📈 Google Analytics 4")
    with col2:
        if config_status['google_analytics']:
            st.success("✅ Configured")
        else:
            st.error("❌ Not Configured")
    
    if config_status['google_analytics']:
        st.markdown(f"- **Property ID**: {os.getenv('GA4_PROPERTY_ID', 'Not set')}")
        st.markdown(f"- **Key File**: {os.getenv('GA4_KEY_FILE', 'Not set')}")
    
    st.markdown("---")
    
    # Facebook status
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("📱 Facebook")
    with col2:
        if config_status['facebook']:
            st.success("✅ Configured")
        else:
            st.error("❌ Not Configured")
    
    if config_status['facebook']:
        st.markdown(f"- **Page ID**: {os.getenv('FB_PAGE_ID', 'Not set')}")
        st.markdown(f"- **API Version**: {os.getenv('FB_API_VERSION', 'v19.0')}")
        st.markdown(f"- **Access Token**: `{'*' * 20}...` (hidden)")
    
    st.markdown("---")
    
    # .env file status
    env_exists = config_status['env_file_exists']
    st.subheader("📄 Configuration File")
    if env_exists:
        st.success("✅ .env file exists")
        env_path = project_root / '.env'
        st.markdown(f"Location: `{env_path}`")
    else:
        st.warning("⚠️ .env file does not exist yet")
        st.markdown("Save any configuration above to create the .env file")

# Footer
st.markdown("---")
st.markdown("### 📚 Help")
with st.expander("Where to find credentials?"):
    st.markdown("""
    **WooCommerce:**
    - Go to your WordPress admin
    - Navigate to WooCommerce > Settings > Advanced > REST API
    - Click "Add key" to create new API credentials
    
    **Google Analytics 4:**
    - Go to [Google Cloud Console](https://console.cloud.google.com/)
    - Create a Service Account under IAM & Admin
    - Download the JSON key file
    - Grant the service account access to your GA4 property
    
    **Facebook:**
    - Go to [Facebook Developers](https://developers.facebook.com/)
    - Use the [Graph API Explorer](https://developers.facebook.com/tools/explorer/) to generate a token
    - Make sure to grant `pages_show_list`, `pages_read_engagement`, and `read_insights` permissions
    """)

with st.expander("Security Notes"):
    st.markdown("""
    - The `.env` file is added to `.gitignore` automatically
    - Never commit your `.env` file to version control
    - API credentials are stored locally on your machine
    - Use environment-specific credentials (don't use production keys for testing)
    """)
