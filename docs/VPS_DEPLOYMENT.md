# Guía de Despliegue en VPS

## Resumen
Desplegar el dashboard en un VPS propio usando Docker. El dashboard será accesible desde cualquier navegador (PC, celular, tablet).

---

## Requisitos del VPS

- **OS**: Ubuntu 22.04 LTS (recomendado)
- **RAM**: 2 GB mínimo
- **CPU**: 1 vCPU
- **Disco**: 20 GB
- **Puerto 80/443** abierto

---

## Paso 1: Preparar el VPS

```bash
# Conectar al VPS
ssh usuario@IP_DEL_VPS

# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo apt install docker-compose-plugin -y

# Cerrar sesión y volver a entrar para aplicar grupo docker
exit
```

---

## Paso 2: Subir el Proyecto

### Opción A: Desde tu PC con Git
```bash
# En tu PC, sube a GitHub (si no lo has hecho)
git init
git add .
git commit -m "Deploy to VPS"
git remote add origin https://github.com/tu-usuario/tu-repo.git
git push -u origin main

# En el VPS, clonar
cd /opt
sudo git clone https://github.com/tu-usuario/tu-repo.git analytics-dashboard
sudo chown -R $USER:$USER analytics-dashboard
cd analytics-dashboard
```

### Opción B: Subir directo con SCP
```bash
# Desde tu PC Windows (PowerShell)
scp -r "C:\Users\USER\Documents\Maquina de produccion masiva\ExtraerDatosGoogleAnalitics_Generic\*" usuario@IP_VPS:/opt/analytics-dashboard/
```

---

## Paso 3: Configurar Variables de Entorno

```bash
cd /opt/analytics-dashboard

# Crear archivo .env
nano .env
```

Contenido del archivo `.env`:
```env
# WooCommerce
WC_URL=https://tu-tienda.com
WC_CONSUMER_KEY=ck_xxxxx
WC_CONSUMER_SECRET=cs_xxxxx

# Google Analytics
GA4_KEY_FILE=/app/config/credentials/tu-service-account.json
GA4_PROPERTY_ID=123456789

# Facebook (opcional)
FB_ACCESS_TOKEN=EAAxxxxx
FB_PAGE_ID=123456789
```

---

## Paso 4: Subir los Datos Existentes

```bash
# Desde tu PC, subir las bases de datos SQLite
scp data/*.db usuario@IP_VPS:/opt/analytics-dashboard/data/

# Verificar
ls -la data/
```

---

## Paso 5: Levantar el Dashboard

```bash
cd /opt/analytics-dashboard

# Construir y ejecutar
docker compose up -d

# Verificar que está corriendo
docker compose ps

# Ver logs
docker compose logs -f app
```

---

## Paso 6: Acceder al Dashboard

Abre en cualquier navegador:
```
http://IP_DEL_VPS:8501
```

✅ **Funciona desde PC, celular, tablet** - cualquier dispositivo con navegador.

---

## Paso 7 (Opcional): Configurar Dominio y HTTPS

### 7a. Instalar Nginx como Reverse Proxy

```bash
sudo apt install nginx -y

sudo nano /etc/nginx/sites-available/analytics
```

Contenido:
```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 86400;
    }

    location /_stcore/stream {
        proxy_pass http://localhost:8501/_stcore/stream;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }
}
```

Activar:
```bash
sudo ln -s /etc/nginx/sites-available/analytics /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 7b. Agregar HTTPS con Let's Encrypt (gratis)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d tu-dominio.com
```

Ahora accedes con: `https://tu-dominio.com`

---

## Comandos Útiles

```bash
# Ver logs
docker compose logs -f

# Reiniciar
docker compose restart

# Reconstruir (después de cambios)
docker compose up -d --build

# Detener
docker compose down

# Actualizar desde Git
git pull && docker compose up -d --build
```

---

## Proteger con Contraseña (Opcional)

Agregar autenticación básica con Nginx:

```bash
# Crear archivo de contraseñas
sudo apt install apache2-utils -y
sudo htpasswd -c /etc/nginx/.htpasswd admin

# Agregar al bloque location en nginx config:
# auth_basic "Dashboard Analytics";
# auth_basic_user_file /etc/nginx/.htpasswd;
```

---

## Actualización Automática de Datos

Para que el ETL corra automáticamente, descomenta el servicio `scheduler` en `docker-compose.yml`:

```yaml
scheduler:
  build:
    context: .
    dockerfile: Dockerfile
  container_name: analytics-scheduler
  command: python scheduler_daemon.py
  # ... resto de configuración
```

---

## Arquitectura Final

```
┌─────────────────────────────────────────────┐
│                    VPS                      │
│  ┌─────────────────────────────────────┐   │
│  │           Docker Compose            │   │
│  │  ┌─────────────┐  ┌──────────────┐ │   │
│  │  │  Streamlit  │  │  SQLite DBs  │ │   │
│  │  │  Dashboard  │  │  (data/*.db) │ │   │
│  │  │  :8501      │  │              │ │   │
│  │  └─────────────┘  └──────────────┘ │   │
│  └─────────────────────────────────────┘   │
│                    │                       │
│               ┌────┴────┐                  │
│               │  Nginx  │                  │
│               │  :80/443│                  │
│               └────┬────┘                  │
└────────────────────┼───────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
    📱 Celular   💻 PC     🖥️ Tablet
```
