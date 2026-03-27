# 🚀 Docker Deployment Guide

## Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed (20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) installed (v2.0+)
- `.env` file configured (see [Setup Guide](SETUP_GUIDE.md))

### One-Command Start

**Windows:**
```bash
docker-start.bat
```

**Linux/Mac:**
```bash
chmod +x docker-start.sh
./docker-start.sh
```

**Manual:**
```bash
docker-compose up -d
```

Access dashboard at: **http://localhost:8501**

---

## Docker Commands Reference

### Building

```bash
# Build image
docker-compose build

# Build without cache
docker-compose build --no-cache

# Build specific service
docker-compose build app
```

### Running

```bash
# Start in background
docker-compose up -d

# Start with logs visible
docker-compose up

# Start specific service
docker-compose up -d app
```

### Monitoring

```bash
# View logs
docker-compose logs -f

# View app logs only
docker-compose logs -f app

# Check container status
docker-compose ps

# Check resource usage
docker stats
```

### Stopping

```bash
# Stop containers
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove everything (including volumes)
docker-compose down -v
```

### Maintenance

```bash
# Restart services
docker-compose restart

# Rebuild and restart
docker-compose up -d --build

# Execute command in container
docker-compose exec app bash

# View container resource limits
docker-compose exec app top
```

---

## Configuration

### Environment Variables

Create `.env` file from template:

```bash
cp .env.example .env
```

Required variables:
```bash
WC_URL=https://your-store.com
WC_CONSUMER_KEY=ck_xxxxx
WC_CONSUMER_SECRET=cs_xxxxx
GA4_PROPERTY_ID=123456789
```

### Volume Mounts

Data is persisted in:
- `./data` - Database files
- `./logs` - Application logs
- `./backups` - Database backups
- `./exports` - Generated reports

### Port Configuration

Default port: `8501`

To change port, edit `docker-compose.yml`:
```yaml
ports:
  - "8080:8501"  # External:Internal
```

---

## Production Deployment

### Option 1: Docker Compose (Simple)

1. **Clone repository on server:**
   ```bash
   git clone <your-repo>
   cd ExtraerDatosGoogleAnalitics_Generic
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   nano .env  # Edit with production credentials
   ```

3. **Start services:**
   ```bash
   docker-compose up -d
   ```

4. **Setup reverse proxy (Nginx):**
   ```nginx
   server {
       listen 80;
       server_name analytics.yourdomain.com;
       
       location / {
           proxy_pass http://localhost:8501;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
       }
   }
   ```

### Option 2: Docker Hub

1. **Push to Docker Hub:**
   ```bash
   docker tag analytics-pipeline:latest username/analytics-pipeline:latest
   docker push username/analytics-pipeline:latest
   ```

2. **Pull and run on server:**
   ```bash
   docker pull username/analytics-pipeline:latest
   docker run -d -p 8501:8501 --env-file .env username/analytics-pipeline:latest
   ```

### Option 3: Cloud Platforms

**AWS ECS:**
```bash
# Create ECR repository
aws ecr create-repository --repository-name analytics-pipeline

# Build and push
docker build -t analytics-pipeline .
docker tag analytics-pipeline:latest <account>.dkr.ecr.us-east-1.amazonaws.com/analytics-pipeline:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/analytics-pipeline:latest

# Deploy via ECS console or CLI
```

**Google Cloud Run:**
```bash
# Build and push
gcloud builds submit --tag gcr.io/<project>/analytics-pipeline

# Deploy
gcloud run deploy analytics-pipeline \
  --image gcr.io/<project>/analytics-pipeline \
  --platform managed \
  --port 8501 \
  --allow-unauthenticated
```

**Azure Container Instances:**
```bash
# Push to ACR
az acr build --registry <registry> --image analytics-pipeline .

# Deploy
az container create \
  --resource-group myResourceGroup \
  --name analytics-pipeline \
  --image <registry>.azurecr.io/analytics-pipeline \
  --ports 8501 \
  --environment-variables $(cat .env)
```

---

## Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs app

# Check if port is already in use
netstat -ano | findstr :8501  # Windows
lsof -i :8501                 # Linux/Mac

# Remove and recreate
docker-compose down
docker-compose up -d
```

### Connection refused

```bash
# Check if container is running
docker-compose ps

# Check health status
docker inspect analytics-pipeline | grep -A 10 Health

# Restart container
docker-compose restart app
```

### Database errors

```bash
# Access container shell
docker-compose exec app bash

# Check database files
ls -lh data/

# Check permissions
chmod 755 data/
```

### Out of memory

Edit `docker-compose.yml`:
```yaml
services:
  app:
    mem_limit: 2g
    mem_reservation: 1g
```

### Network issues

```bash
# Check network
docker network ls

# Inspect network
docker network inspect <network-name>

# Recreate network
docker-compose down
docker network prune
docker-compose up -d
```

---

## Advanced Configuration

### Using PostgreSQL

Uncomment PostgreSQL service in `docker-compose.yml`:

```yaml
postgres:
  image: postgres:15-alpine
  environment:
    - POSTGRES_DB=analytics
    - POSTGRES_USER=analytics_user
    - POSTGRES_PASSWORD=${DB_PASSWORD}
  volumes:
    - postgres_data:/var/lib/postgresql/data
```

Update `.env`:
```bash
DB_TYPE=postgresql
DB_HOST=postgres
DB_PORT=5432
DB_NAME=analytics
DB_USER=analytics_user
DB_PASSWORD=your-secure-password
```

### Enabling Scheduler

Uncomment scheduler service in `docker-compose.yml`:

```yaml
scheduler:
  build: .
  command: python scheduler_daemon.py
  depends_on:
    - app
```

### Custom Healthcheck

Edit `Dockerfile`:
```dockerfile
HEALTHCHECK --interval=60s --timeout=30s --start-period=5s --retries=5 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1
```

---

## Security Best Practices

1. **Never commit .env file**
   - Already in `.gitignore`
   - Use secrets management in production

2. **Use non-root user**
   ```dockerfile
   RUN useradd -m -u 1000 appuser
   USER appuser
   ```

3. **Scan for vulnerabilities**
   ```bash
   docker scan analytics-pipeline:latest
   ```

4. **Keep images updated**
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

5. **Limit container resources**
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '2'
         memory: 2G
   ```

---

## CI/CD Integration

GitHub Actions automatically:
- ✅ Builds and tests on every push
- ✅ Builds Docker image
- ✅ Pushes to Docker Hub (on main branch)
- ✅ Runs security scans

See `.github/workflows/` for configuration.

---

## Monitoring

### Container Metrics

```bash
# Resource usage
docker stats analytics-pipeline

# Container inspect
docker inspect analytics-pipeline

# Process list
docker top analytics-pipeline
```

### Application Logs

```bash
# All logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Since timestamp
docker-compose logs --since 2024-01-01T00:00:00
```

---

## Backup and Restore

### Backup

```bash
# Backup data volume
docker run --rm -v $(pwd)/data:/data -v $(pwd)/backup:/backup \
  alpine tar czf /backup/data-backup-$(date +%Y%m%d).tar.gz /data

# Or use script
./scripts/backup.sh
```

### Restore

```bash
# Restore from backup
docker run --rm -v $(pwd)/data:/data -v $(pwd)/backup:/backup \
  alpine tar xzf /backup/data-backup-20241221.tar.gz -C /
```

---

## Support

For issues with Docker deployment:
1. Check logs: `docker-compose logs -f`
2. Verify configuration: `docker-compose config`
3. Review [Troubleshooting](#troubleshooting) section
4. Check [DEPLOYMENT.md](DEPLOYMENT.md) for general deployment info
