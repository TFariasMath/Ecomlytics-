"""
Script para obtener un Page Access Token permanente de Facebook.

Este script convierte un User Access Token de corta duración en un 
Page Access Token permanente que nunca expira.
"""

import requests
import json
import os

def get_long_lived_token(user_token, app_id, app_secret):
    """Convierte un short-lived user token en long-lived token (60 días)."""
    url = "https://graph.facebook.com/v19.0/oauth/access_token"
    params = {
        'grant_type': 'fb_exchange_token',
        'client_id': app_id,
        'client_secret': app_secret,
        'fb_exchange_token': user_token
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if 'access_token' in data:
        print("✅ Long-lived User Token obtenido")
        return data['access_token']
    else:
        print("❌ Error al obtener long-lived token:")
        print(json.dumps(data, indent=2))
        return None

def get_page_token(long_lived_user_token):
    """Obtiene el Page Access Token permanente usando el long-lived user token."""
    url = "https://graph.facebook.com/v19.0/me/accounts"
    params = {'access_token': long_lived_user_token}
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if 'data' in data and len(data['data']) > 0:
        pages = data['data']
        print(f"\n✅ Encontradas {len(pages)} página(s):")
        
        for i, page in enumerate(pages, 1):
            print(f"\n{i}. {page['name']} (ID: {page['id']})")
            print(f"   Permisos: {', '.join(page.get('tasks', []))}")
        
        # Si hay solo una página, devolverla automáticamente
        if len(pages) == 1:
            selected_page = pages[0]
        else:
            # Solicitar selección al usuario
            choice = int(input("\nSelecciona el número de página: ")) - 1
            selected_page = pages[choice]
        
        print(f"\n✅ Page Access Token permanente obtenido para: {selected_page['name']}")
        return selected_page['access_token'], selected_page['id'], selected_page['name']
    else:
        print("❌ Error al obtener páginas:")
        print(json.dumps(data, indent=2))
        return None, None, None

def verify_token(token):
    """Verifica que el token funcione."""
    url = f"https://graph.facebook.com/v19.0/me?access_token={token}"
    response = requests.get(url)
    data = response.json()
    print("\n=== Verificación del Token ===")
    print(json.dumps(data, indent=2))
    return 'error' not in data

def update_config_file(page_token, page_id, page_name):
    """Actualiza el archivo de configuración con el nuevo token."""
    config_content = f'''"""
Configuración de Facebook API.
"""

# Page Access Token permanente
# Generado usando scripts/get_permanent_facebook_token.py
PAGE_ACCESS_TOKEN = "{page_token}"

# Facebook Page ID
PAGE_ID = "{page_id}"

# Nombre de la página
PAGE_NAME = "{page_name}"

# API Version
API_VERSION = "v19.0"
BASE_URL = f"https://graph.facebook.com/{{API_VERSION}}"
'''
    
    config_dir = os.path.join(os.path.dirname(__file__), '..', 'config')
    os.makedirs(config_dir, exist_ok=True)
    
    config_path = os.path.join(config_dir, 'facebook_config.py')
    
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print(f"\n✅ Configuración guardada en: {config_path}")

def main():
    print("=" * 60)
    print("🔑 Obtener Token Permanente de Facebook")
    print("=" * 60)
    print("\nEste script te ayudará a obtener un Page Access Token permanente.")
    print("\n📋 Necesitarás:")
    print("1. User Access Token (del Graph API Explorer)")
    print("2. App ID (de tu aplicación de Facebook)")
    print("3. App Secret (de tu aplicación de Facebook)")
    print("\n🔗 Graph API Explorer: https://developers.facebook.com/tools/explorer/")
    print("🔗 Tus Apps: https://developers.facebook.com/apps/")
    print("\n" + "=" * 60)
    
    # Solicitar datos al usuario
    user_token = input("\n1. User Access Token: ").strip()
    app_id = input("2. App ID: ").strip()
    app_secret = input("3. App Secret: ").strip()
    
    if not all([user_token, app_id, app_secret]):
        print("\n❌ Error: Todos los campos son requeridos")
        return
    
    # Paso 1: Obtener long-lived user token
    print("\n" + "-" * 60)
    print("Paso 1: Obteniendo Long-Lived User Token...")
    print("-" * 60)
    long_lived_token = get_long_lived_token(user_token, app_id, app_secret)
    
    if not long_lived_token:
        return
    
    # Paso 2: Obtener Page Token permanente
    print("\n" + "-" * 60)
    print("Paso 2: Obteniendo Page Access Token Permanente...")
    print("-" * 60)
    page_token, page_id, page_name = get_page_token(long_lived_token)
    
    if not page_token:
        return
    
    # Paso 3: Verificar el token
    print("\n" + "-" * 60)
    print("Paso 3: Verificando el token...")
    print("-" * 60)
    if not verify_token(page_token):
        print("❌ El token no es válido")
        return
    
    # Paso 4: Guardar configuración
    print("\n" + "-" * 60)
    print("Paso 4: Guardando configuración...")
    print("-" * 60)
    update_config_file(page_token, page_id, page_name)
    
    # Resumen
    print("\n" + "=" * 60)
    print("✅ ¡COMPLETADO!")
    print("=" * 60)
    print(f"\n📝 Página: {page_name}")
    print(f"🆔 Page ID: {page_id}")
    print(f"🔑 Token guardado en: config/facebook_config.py")
    print("\n🚀 Próximo paso:")
    print("   python etl/extract_facebook.py")
    print("=" * 60)

if __name__ == "__main__":
    main()
