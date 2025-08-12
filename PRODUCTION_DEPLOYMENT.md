# 🚀 Umoor Sehhat Production Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the Umoor Sehhat Django application to production with proper security, performance, and monitoring configurations.

## 📋 Prerequisites

### System Requirements
- **OS**: Ubuntu 20.04+ or CentOS 8+
- **Python**: 3.8+
- **PostgreSQL**: 12+
- **Redis**: 6+
- **Nginx**: Latest stable
- **SSL Certificate**: Valid SSL certificate for your domain

### Server Specifications (Recommended)
- **CPU**: 2+ cores
- **RAM**: 4GB+
- **Storage**: 20GB+ SSD
- **Network**: Stable internet connection

## 🔧 Phase 1: Critical Security & Configuration

### Step 1: Environment Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Sehhat_Website
   ```

2. **Create and configure environment file**:
   ```bash
   cp .env.production .env
   nano .env  # Edit with your actual values
   ```

3. **Generate a secure secret key**:
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

### Step 2: Database Setup

1. **Install PostgreSQL**:
   ```bash
   sudo apt update
   sudo apt install postgresql postgresql-contrib
   ```

2. **Create database and user**:
   ```sql
   sudo -u postgres psql
   CREATE DATABASE umoor_sehhat_db;
   CREATE USER umoor_sehhat_user WITH PASSWORD 'your-secure-password';
   GRANT ALL PRIVILEGES ON DATABASE umoor_sehhat_db TO umoor_sehhat_user;
   ALTER USER umoor_sehhat_user CREATEDB;
   \q
   ```

3. **Test database connection**:
   ```bash
   psql -h localhost -U umoor_sehhat_user -d umoor_sehhat_db
   ```

### Step 3: Redis Setup

1. **Install Redis**:
   ```bash
   sudo apt install redis-server
   ```

2. **Configure Redis for production**:
   ```bash
   sudo nano /etc/redis/redis.conf
   ```
   
   Add/modify these settings:
   ```conf
   bind 127.0.0.1
   requirepass your-redis-password
   maxmemory 256mb
   maxmemory-policy allkeys-lru
   ```

3. **Restart Redis**:
   ```bash
   sudo systemctl restart redis-server
   sudo systemctl enable redis-server
   ```

### Step 4: Python Environment

1. **Install Python dependencies**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Test the application**:
   ```bash
   python manage.py check --deploy --settings=umoor_sehhat.production
   ```

## 🔒 Phase 2: Security Hardening

### SSL/TLS Configuration

1. **Obtain SSL certificate** (Let's Encrypt recommended):
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
   ```

2. **Configure automatic renewal**:
   ```bash
   sudo crontab -e
   # Add: 0 12 * * * /usr/bin/certbot renew --quiet
   ```

### Firewall Configuration

1. **Configure UFW firewall**:
   ```bash
   sudo ufw allow ssh
   sudo ufw allow 'Nginx Full'
   sudo ufw enable
   ```

2. **Verify firewall status**:
   ```bash
   sudo ufw status
   ```

## 🚀 Phase 3: Deployment

### Automated Deployment

1. **Run the deployment script**:
   ```bash
   ./deploy_production.sh
   ```

2. **Verify deployment**:
   ```bash
   sudo systemctl status umoor-sehhat.service
   sudo nginx -t
   ```

### Manual Deployment (Alternative)

If you prefer manual deployment:

1. **Collect static files**:
   ```bash
   python manage.py collectstatic --noinput --settings=umoor_sehhat.production
   ```

2. **Run migrations**:
   ```bash
   python manage.py migrate --settings=umoor_sehhat.production
   ```

3. **Create superuser**:
   ```bash
   python manage.py createsuperuser --settings=umoor_sehhat.production
   ```

4. **Start Gunicorn**:
   ```bash
   gunicorn --config gunicorn.conf.py umoor_sehhat.wsgi_production:application
   ```

## 📊 Phase 4: Monitoring & Maintenance

### Health Checks

1. **Application health**:
   ```bash
   curl -I https://yourdomain.com/admin/
   ```

2. **Database health**:
   ```bash
   psql -h localhost -U umoor_sehhat_user -d umoor_sehhat_db -c "SELECT version();"
   ```

3. **Redis health**:
   ```bash
   redis-cli ping
   ```

### Monitoring Setup

1. **System monitoring**:
   ```bash
   ./monitor.sh
   ```

2. **Log monitoring**:
   ```bash
   tail -f logs/django.log
   sudo journalctl -u umoor-sehhat.service -f
   ```

### Backup Strategy

1. **Automated backups**:
   ```bash
   ./backup.sh
   ```

2. **Setup cron job for daily backups**:
   ```bash
   crontab -e
   # Add: 0 2 * * * /path/to/your/app/backup.sh
   ```

## 🔧 Configuration Files

### Environment Variables (.env)

```bash
# Django Settings
DJANGO_SECRET_KEY=your-super-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_NAME=umoor_sehhat_db
DB_USER=umoor_sehhat_user
DB_PASSWORD=your-secure-password
DB_HOST=localhost
DB_PORT=5432
DB_SSL=true

# Redis
REDIS_URL=redis://:your-redis-password@localhost:6379/1

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### Gunicorn Configuration (gunicorn.conf.py)

Key settings:
- **Workers**: CPU cores × 2 + 1
- **Timeout**: 30 seconds
- **Max requests**: 1000 per worker
- **Preload app**: True for better performance

### Nginx Configuration

Features:
- **SSL/TLS termination**
- **Static file serving**
- **Security headers**
- **Gzip compression**
- **Proxy to Gunicorn**

## 🛠️ Troubleshooting

### Common Issues

1. **Database connection errors**:
   ```bash
   # Check PostgreSQL status
   sudo systemctl status postgresql
   
   # Test connection
   psql -h localhost -U umoor_sehhat_user -d umoor_sehhat_db
   ```

2. **Redis connection errors**:
   ```bash
   # Check Redis status
   sudo systemctl status redis-server
   
   # Test connection
   redis-cli ping
   ```

3. **Permission errors**:
   ```bash
   # Fix file permissions
   sudo chown -R www-data:www-data /path/to/your/app
   sudo chmod -R 755 /path/to/your/app
   ```

4. **SSL certificate issues**:
   ```bash
   # Check certificate validity
   sudo certbot certificates
   
   # Renew certificate
   sudo certbot renew
   ```

### Log Analysis

1. **Application logs**:
   ```bash
   tail -f logs/django.log
   ```

2. **System logs**:
   ```bash
   sudo journalctl -u umoor-sehhat.service -f
   sudo journalctl -u nginx -f
   ```

3. **Error monitoring**:
   ```bash
   grep ERROR logs/django.log
   grep CRITICAL logs/django.log
   ```

## 🔄 Maintenance Procedures

### Regular Maintenance

1. **Daily**:
   - Check application status
   - Monitor logs for errors
   - Verify backup completion

2. **Weekly**:
   - Review performance metrics
   - Check disk space
   - Update security packages

3. **Monthly**:
   - Review and rotate logs
   - Update application dependencies
   - Security audit

### Update Procedures

1. **Application updates**:
   ```bash
   git pull origin main
   pip install -r requirements.txt --upgrade
   python manage.py migrate --settings=umoor_sehhat.production
   python manage.py collectstatic --noinput --settings=umoor_sehhat.production
   sudo systemctl restart umoor-sehhat.service
   ```

2. **System updates**:
   ```bash
   sudo apt update && sudo apt upgrade
   sudo systemctl restart nginx
   sudo systemctl restart postgresql
   sudo systemctl restart redis-server
   ```

## 📈 Performance Optimization

### Database Optimization

1. **PostgreSQL tuning**:
   ```bash
   sudo nano /etc/postgresql/*/main/postgresql.conf
   ```

   Recommended settings:
   ```conf
   shared_buffers = 256MB
   effective_cache_size = 1GB
   maintenance_work_mem = 64MB
   checkpoint_completion_target = 0.9
   wal_buffers = 16MB
   default_statistics_target = 100
   ```

2. **Database indexing**:
   ```bash
   python manage.py dbshell --settings=umoor_sehhat.production
   ```

### Caching Strategy

1. **Redis optimization**:
   ```conf
   maxmemory 512mb
   maxmemory-policy allkeys-lru
   save 900 1
   save 300 10
   save 60 10000
   ```

2. **Application caching**:
   - Session storage in Redis
   - API response caching
   - Static file caching

## 🔐 Security Checklist

- [ ] DEBUG = False
- [ ] SECRET_KEY is secure and unique
- [ ] ALLOWED_HOSTS is properly configured
- [ ] SSL/TLS is enabled
- [ ] Security headers are set
- [ ] Rate limiting is configured
- [ ] Database uses SSL
- [ ] Firewall is configured
- [ ] Regular backups are scheduled
- [ ] Monitoring is set up
- [ ] Logs are rotated
- [ ] Dependencies are up to date

## 📞 Support

For issues and support:
1. Check the troubleshooting section
2. Review application logs
3. Contact the development team
4. Create an issue in the repository

---

**Last Updated**: August 12, 2025  
**Version**: 1.0  
**Status**: Production Ready ✅