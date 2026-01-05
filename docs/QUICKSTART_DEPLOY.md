# =============================================================================
# QUICK START GUIDE - PRODUCTION DEPLOYMENT
# =============================================================================

## 🚀 5-Minute Local Deployment

### 1. Prerequisites
- Docker Desktop running
- Port 80 available

### 2. Quick Setup
```bash
# Clone repository
git clone <repo-url>
cd kp-real-estate-llm-prototype

# Configure environment
cp .env.example .env
nano .env  # Set SECRET_KEY, POSTGRES_PASSWORD, OPENAI_API_KEY

# Generate SECRET_KEY:
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Deploy
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

### 3. Access
- Frontend: http://localhost
- Admin: http://localhost/admin
- API: http://localhost/api/

**Login**: Use credentials from `.env` (DJANGO_SUPERUSER_USERNAME/PASSWORD)

---

## 🌊 Digital Ocean Deployment (10 minutes)

### 1. Create Droplet
- Ubuntu 22.04 LTS
- 2GB RAM / 2 vCPUs
- Add SSH key

### 2. Connect & Setup
```bash
# SSH to droplet
ssh root@YOUR_DROPLET_IP

# Install Docker
curl -fsSL https://get.docker.com | sh
apt install docker-compose -y

# Clone repository
cd /opt
git clone <repo-url>
cd kp-real-estate-llm-prototype

# Configure
cp .env.example .env
nano .env  # Update ALLOWED_HOSTS, set production passwords
```

### 3. Deploy
```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

### 4. Configure Firewall
```bash
ufw allow 22
ufw allow 80
ufw allow 443
ufw enable
```

### 5. Access
Visit: `http://YOUR_DROPLET_IP`

---

## 🔒 Enable HTTPS (Optional, +15 minutes)

### Requirements
- Domain name pointing to droplet IP

### Steps
```bash
# Stop nginx
docker-compose -f docker-compose.production.yml stop nginx

# Get SSL certificate
apt install certbot -y
certbot certonly --standalone -d yourdomain.com

# Update nginx config (see DEPLOYMENT.md for details)
nano nginx/conf.d/app.conf

# Update .env
nano .env
# Set: SECURE_SSL_REDIRECT=True, ALLOWED_HOSTS=yourdomain.com

# Restart
./scripts/deploy.sh
```

---

## 📋 Essential Commands

```bash
# View logs
docker-compose -f docker-compose.production.yml logs -f

# Restart services
docker-compose -f docker-compose.production.yml restart

# Backup database
./scripts/backup.sh

# Restore database
./scripts/restore.sh YYYYMMDD_HHMMSS

# Stop everything
docker-compose -f docker-compose.production.yml down
```

---

## 🐛 Quick Troubleshooting

### Can't access application
```bash
# Check services
docker-compose -f docker-compose.production.yml ps

# Check logs
docker-compose -f docker-compose.production.yml logs nginx
docker-compose -f docker-compose.production.yml logs web
```

### Database errors
```bash
# Check database
docker-compose -f docker-compose.production.yml logs db

# Reset database (WARNING: deletes data)
docker-compose -f docker-compose.production.yml down -v
./scripts/deploy.sh
```

### Out of memory
```bash
# Reduce workers in Dockerfile.production
# Change: --workers 4 --threads 2
# To:     --workers 2 --threads 2
./scripts/deploy.sh
```

---

## 📚 Full Documentation

See **DEPLOYMENT.md** for:
- Complete SSL setup guide
- Security hardening
- Monitoring & scaling
- Advanced troubleshooting
- Production best practices

---

## ✅ Checklist

Before going live:
- [ ] Change `SECRET_KEY`
- [ ] Strong `POSTGRES_PASSWORD`
- [ ] Valid `OPENAI_API_KEY`
- [ ] `DEBUG=False`
- [ ] `ALLOWED_HOSTS` configured
- [ ] Firewall enabled
- [ ] SSL certificate (for production)
- [ ] Backup script scheduled
- [ ] Health check working: `curl http://localhost/api/health/`

---

## 🆘 Need Help?

1. Check logs: `docker-compose -f docker-compose.production.yml logs -f`
2. Health check: `curl http://localhost/api/health/`
3. Review DEPLOYMENT.md
4. Check environment variables: `.env`
