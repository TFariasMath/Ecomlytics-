#!/bin/bash
# ====================================================================
#  Analytics Pipeline - Instalador Automático
#  Para Linux/macOS
# ====================================================================

echo
echo "========================================"
echo "  Analytics Pipeline - Instalación"
echo "========================================"
echo

# Verificar que Python esté instalado
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 no está instalado"
    echo
    echo "Por favor instala Python 3.10 o superior:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-venv python3-pip"
    echo "  macOS: brew install python@3.10"
    echo
    exit 1
fi

echo "[OK] Python detectado"
python3 --version
echo

# Crear entorno virtual
echo "[1/5] Creando entorno virtual..."
if [ -d "venv" ]; then
    echo "Entorno virtual ya existe, omitiendo..."
else
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "[ERROR] No se pudo crear entorno virtual"
        exit 1
    fi
    echo "[OK] Entorno virtual creado"
fi
echo

# Activar entorno virtual
echo "[2/5] Activando entorno virtual..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "[ERROR] No se pudo activar entorno virtual"
    exit 1
fi
echo "[OK] Entorno virtual activado"
echo

# Instalar dependencias
echo "[3/5] Instalando dependencias..."
echo "Esto puede tomar 2-3 minutos..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
if [ $? -ne 0 ]; then
    echo "[ERROR] Error instalando dependencias"
    exit 1
fi
echo "[OK] Dependencias instaladas"
echo

# Crear archivo .env si no existe
echo "[4/5] Configurando ambiente..."
if [ -f ".env" ]; then
    echo "Archivo .env ya existe, omitiendo..."
else
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "[OK] Archivo .env creado desde .env.example"
        echo "IMPORTANTE: Debes configurar tus credenciales en el dashboard"
    else
        echo "[AVISO] .env.example no encontrado"
    fi
fi
echo

# Crear directorios necesarios
echo "[5/5] Creando directorios..."
mkdir -p data logs backups
echo "[OK] Directorios creados"
echo

echo "========================================"
echo "  Instalación Completada!"
echo "========================================"
echo
echo "Próximos pasos:"
echo
echo "1. Abrir el dashboard:"
echo "   source venv/bin/activate"
echo "   streamlit run dashboard/app_woo_v2.py"
echo
echo "2. Configurar credenciales:"
echo "   - Click en 'Configurar Credenciales'"
echo "   - Ingresa tus datos de WooCommerce / Google Analytics"
echo "   - Prueba las conexiones"
echo "   - Guarda la configuración"
echo
echo "3. Extraer datos:"
echo "   - Click en 'Extraer datos nuevos'"
echo "   - Espera a que complete"
echo "   - Refresca el dashboard"
echo
echo "Ver documentación completa en: docs/SETUP_GUIDE.md"
echo
echo "========================================"
echo

# Preguntar si quiere abrir el dashboard ahora
read -p "¿Quieres abrir el dashboard ahora? (s/n): " OPEN_DASHBOARD
if [ "$OPEN_DASHBOARD" = "s" ] || [ "$OPEN_DASHBOARD" = "S" ]; then
    echo
    echo "Abriendo dashboard..."
    echo "NOTA: Presiona Ctrl+C para detener el servidor"
    echo
    streamlit run dashboard/app_woo_v2.py
else
    echo
    echo "Para abrir el dashboard más tarde, ejecuta:"
    echo "  source venv/bin/activate"
    echo "  streamlit run dashboard/app_woo_v2.py"
    echo
fi
