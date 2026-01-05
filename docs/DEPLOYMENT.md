# =============================================================================
# DEPLOYMENT GUIDE - LOCAL & DIGITAL OCEAN
# =============================================================================

## 📋 Prerequisites

### Local Development
- Docker Desktop installed
- Docker Compose installed
- Git (optional, for version control)

### Digital Ocean Deployment
- Digital Ocean account
- Domain name (optional, but recommended)
- SSH access to droplet

---

## 🚀 LOCAL DEPLOYMENT

### 1. Clone Repository (if needed)
```bash
git clone <your-repo-url>
cd kp-real-estate-llm-prototype
```

### 2. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your values
nano .env
```

**Required Environment Variables:**
- `SECRET_KEY` - Generate with: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- `POSTGRES_PASSWORD` - Strong database password
- `OPENAI_API_KEY` - Your OpenAI API key
- `DJANGO_SUPERUSER_PASSWORD` - Admin password

### 3. Deploy
```bash
# Make scripts executable
chmod +x scripts/*.sh

# Deploy
./scripts/deploy.sh
```

The script will:
- Build Docker images
- Start all services (PostgreSQL, Redis, Django, Nginx, Celery)
- Run database migrations
- Collect static files
- Create superuser

### 4. Access Application
- **Frontend**: http://localhost
- **Admin**: http://localhost/admin
- **API**: http://localhost/api/

### 5. Verify Deployment
```bash
# Check all services are running
docker-compose -f docker-compose.production.yml ps

# Check logs
docker-compose -f docker-compose.production.yml logs -f

# Test health endpoint
curl http://localhost/api/health/
```

---

## 🌊 DIGITAL OCEAN DEPLOYMENT

### 1. Create Droplet
1. Go to Digital Ocean console
2. Create Droplet:
   - **Distribution**: Ubuntu 22.04 LTS
   - **Plan**: Basic ($12/month minimum recommended)
   - **CPU**: 2 vCPUs, 2GB RAM
   - **Storage**: 50GB SSD
3. Add your SSH key
4. Choose datacenter region (closest to users)

### 2. Connect to Droplet
```bash
ssh root@your_droplet_ip
```

### 3. Install Docker
```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose -y

# Verify installation
docker --version
docker-compose --version
```

### 4. Clone Repository
```bash
# Install Git if needed
apt install git -y

# Clone your repository
cd /opt
git clone <your-repo-url>
cd kp-real-estate-llm-prototype
```

### 5. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit with production values
nano .env
```

**Production-Specific Settings:**
```bash
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com,your_droplet_ip
SECURE_SSL_REDIRECT=False  # Set to True after SSL setup
SECRET_KEY=<generate-strong-key>
POSTGRES_PASSWORD=<strong-password>
OPENAI_API_KEY=<your-key>
```

### 6. Deploy
```bash
# Make scripts executable
chmod +x scripts/*.sh

# Deploy
./scripts/deploy.sh
```

### 7. Configure Firewall
```bash
# Allow SSH, HTTP, HTTPS
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable

# Verify
ufw status
```

### 8. Access Application
Visit: `http://your_droplet_ip`

---

## 🔒 SSL SETUP (HTTPS)

### 1. Point Domain to Droplet
Add A record in your DNS provider:
```
Type: A
Name: @
Value: your_droplet_ip
TTL: 3600
```

Wait for DNS propagation (5-30 minutes).

### 2. Install Certbot
```bash
apt install certbot python3-certbot-nginx -y
```

### 3. Stop Nginx
```bash
docker-compose -f docker-compose.production.yml stop nginx
```

### 4. Get SSL Certificate
```bash
certbot certonly --standalone -d your-domain.com -d www.your-domain.com
```

Certificates will be saved to:
- `/etc/letsencrypt/live/your-domain.com/fullchain.pem`
- `/etc/letsencrypt/live/your-domain.com/privkey.pem`

### 5. Update Nginx Configuration
Edit `nginx/conf.d/app.conf`:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # ... rest of configuration
}
```

### 6. Update docker-compose.production.yml
Add SSL certificate volumes to nginx service:

```yaml
nginx:
  volumes:
    - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    - ./nginx/conf.d:/etc/nginx/conf.d:ro
    - static_volume:/app/staticfiles:ro
    - media_volume:/app/media:ro
    - /etc/letsencrypt:/etc/letsencrypt:ro  # Add this
```

### 7. Update Environment Variables
```bash
nano .env
```

Set:
```bash
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
```

### 8. Restart Services
```bash
./scripts/deploy.sh
```

### 9. Setup Auto-Renewal
```bash
# Test renewal
certbot renew --dry-run

# Add cron job
crontab -e

# Add this line (renew at 3am daily)
0 3 * * * certbot renew --quiet && docker-compose -f /opt/kp-real-estate-llm-prototype/docker-compose.production.yml restart nginx
```

---

## 🔧 MAINTENANCE COMMANDS

### View Logs
```bash
# All services
docker-compose -f docker-compose.production.yml logs -f

# Specific service
docker-compose -f docker-compose.production.yml logs -f web
docker-compose -f docker-compose.production.yml logs -f nginx
docker-compose -f docker-compose.production.yml logs -f celery_worker
```

### Restart Services
```bash
# All services
docker-compose -f docker-compose.production.yml restart

# Specific service
docker-compose -f docker-compose.production.yml restart web
```

### Stop Services
```bash
docker-compose -f docker-compose.production.yml down
```

### Backup Database
```bash
./scripts/backup.sh
```

Backups saved to `backups/` directory.

### Restore Database
```bash
# List available backups
ls -lh backups/

# Restore specific backup
./scripts/restore.sh 20240115_143000
```

### Shell Access
```bash
# Django shell
docker-compose -f docker-compose.production.yml exec web python manage.py shell

# Database shell
docker-compose -f docker-compose.production.yml exec db psql -U postgres -d real_estate

# Bash shell
docker-compose -f docker-compose.production.yml exec web bash
```

### Update Code
```bash
# Pull latest changes
git pull

# Rebuild and restart
./scripts/deploy.sh
```

---

## 🐛 TROUBLESHOOTING

### Services Won't Start
```bash
# Check logs
docker-compose -f docker-compose.production.yml logs

# Check if ports are in use
netstat -tulpn | grep :80
netstat -tulpn | grep :443

# Remove old containers
docker-compose -f docker-compose.production.yml down -v
```

### Database Connection Error
```bash
# Check database is running
docker-compose -f docker-compose.production.yml ps

# Check database logs
docker-compose -f docker-compose.production.yml logs db

# Verify environment variables
docker-compose -f docker-compose.production.yml exec web env | grep DATABASE
```

### Static Files Not Loading
```bash
# Collect static files
docker-compose -f docker-compose.production.yml exec web python manage.py collectstatic --noinput

# Restart nginx
docker-compose -f docker-compose.production.yml restart nginx
```

### Out of Memory
```bash
# Check memory usage
docker stats

# Reduce Gunicorn workers in Dockerfile.production:
# Change: --workers 4 --threads 2
# To:     --workers 2 --threads 2
```

### SSL Certificate Issues
```bash
# Check certificate expiry
certbot certificates

# Force renewal
certbot renew --force-renewal

# Restart nginx
docker-compose -f docker-compose.production.yml restart nginx
```

---

## 📊 MONITORING

### Health Check
```bash
curl http://localhost/api/health/
```

Expected response:
```json
{
    "status": "healthy",
    "database": "ok",
    "cache": "ok",
    "celery": "ok"
}
```

### Resource Usage
```bash
# Docker stats
docker stats

# System resources
htop

# Disk usage
df -h
```

### Application Metrics
- Admin panel: `/admin/`
- Check logs: `docker-compose -f docker-compose.production.yml logs -f`

---

## 🔐 SECURITY CHECKLIST

- [ ] Change default `SECRET_KEY`
- [ ] Use strong `POSTGRES_PASSWORD`
- [ ] Change `DJANGO_SUPERUSER_PASSWORD`
- [ ] Set `DEBUG=False` in production
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Enable SSL/HTTPS
- [ ] Set `SECURE_SSL_REDIRECT=True` after SSL setup
- [ ] Configure firewall (UFW)
- [ ] Regular backups (cron job)
- [ ] Keep Docker images updated
- [ ] Monitor logs for suspicious activity
- [ ] Use environment variables (never commit `.env`)

---

## 📈 SCALING

### Increase Workers
Edit `Dockerfile.production`:
```dockerfile
CMD ["gunicorn", "--workers", "8", "--threads", "4", ...]
```

### Add More Celery Workers
Edit `docker-compose.production.yml`:
```yaml
celery_worker_2:
  <<: *celery_worker
  container_name: celery_worker_2
```

### Upgrade Droplet
Digital Ocean → Droplets → Your droplet → Resize
- Choose larger plan
- Restart droplet

---

## 📞 SUPPORT

For issues:
1. Check logs: `docker-compose -f docker-compose.production.yml logs -f`
2. Verify health: `curl http://localhost/api/health/`
3. Check environment variables
4. Review troubleshooting section above

---

## 📝 NOTES

- **Database backups**: Run `./scripts/backup.sh` regularly (recommended: daily cron job)
- **SSL certificates**: Auto-renew via cron job
- **Updates**: Pull latest code and run `./scripts/deploy.sh`
- **Monitoring**: Check `/api/health/` endpoint for service status
- **Logs**: Stored in `logs/` directory inside containers
