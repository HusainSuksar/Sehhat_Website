#!/bin/bash

# Production Deployment Script for Umoor Sehhat
# Usage: ./deploy_production.sh

set -e  # Exit on any error

echo "🚀 Starting Umoor Sehhat Production Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env file exists
if [ ! -f .env ]; then
    print_error ".env file not found. Please copy .env.production to .env and configure it."
    exit 1
fi

# Load environment variables
print_status "Loading environment variables..."
source .env

# Check required environment variables
required_vars=("DJANGO_SECRET_KEY" "DB_PASSWORD" "EMAIL_HOST_USER" "EMAIL_HOST_PASSWORD")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        print_error "Required environment variable $var is not set."
        exit 1
    fi
done

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs
mkdir -p staticfiles
mkdir -p media
mkdir -p /var/log/umoor_sehhat 2>/dev/null || print_warning "Could not create /var/log/umoor_sehhat (may need sudo)"

# Install/upgrade dependencies
print_status "Installing/upgrading Python dependencies..."
pip install -r requirements.txt --upgrade

# Run database migrations
print_status "Running database migrations..."
python manage.py migrate --settings=umoor_sehhat.production

# Collect static files
print_status "Collecting static files..."
python manage.py collectstatic --noinput --settings=umoor_sehhat.production

# Create superuser if it doesn't exist
print_status "Checking for superuser..."
python manage.py shell --settings=umoor_sehhat.production << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print("Creating superuser...")
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("Superuser created: admin/admin123")
else:
    print("Superuser already exists")
EOF

# Test the application
print_status "Testing the application..."
python manage.py check --deploy --settings=umoor_sehhat.production

# Create systemd service file
print_status "Creating systemd service file..."
sudo tee /etc/systemd/system/umoor-sehhat.service > /dev/null << EOF
[Unit]
Description=Umoor Sehhat Django Application
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=$(pwd)
Environment=DJANGO_SETTINGS_MODULE=umoor_sehhat.production
EnvironmentFile=$(pwd)/.env
ExecStart=$(which gunicorn) --config gunicorn.conf.py umoor_sehhat.wsgi_production:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
print_status "Reloading systemd and enabling service..."
sudo systemctl daemon-reload
sudo systemctl enable umoor-sehhat.service

# Start the service
print_status "Starting Umoor Sehhat service..."
sudo systemctl start umoor-sehhat.service

# Check service status
print_status "Checking service status..."
sudo systemctl status umoor-sehhat.service --no-pager

# Create Nginx configuration
print_status "Creating Nginx configuration..."
sudo tee /etc/nginx/sites-available/umoor-sehhat > /dev/null << EOF
server {
    listen 80;
    server_name ${DJANGO_ALLOWED_HOSTS//,/ };

    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name ${DJANGO_ALLOWED_HOSTS//,/ };

    # SSL Configuration (replace with your certificate paths)
    ssl_certificate /etc/ssl/certs/umoor-sehhat.crt;
    ssl_certificate_key /etc/ssl/private/umoor-sehhat.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload";

    # Static files
    location /static/ {
        alias $(pwd)/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias $(pwd)/media/;
        expires 1y;
        add_header Cache-Control "public";
    }

    # Proxy to Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
}
EOF

# Enable Nginx site
print_status "Enabling Nginx site..."
sudo ln -sf /etc/nginx/sites-available/umoor-sehhat /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Setup log rotation
print_status "Setting up log rotation..."
sudo tee /etc/logrotate.d/umoor-sehhat > /dev/null << EOF
$(pwd)/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload umoor-sehhat.service
    endscript
}
EOF

# Create backup script
print_status "Creating backup script..."
tee backup.sh > /dev/null << EOF
#!/bin/bash
# Backup script for Umoor Sehhat

BACKUP_DIR="/var/backups/umoor-sehhat"
DATE=\$(date +%Y%m%d_%H%M%S)

mkdir -p \$BACKUP_DIR

# Backup database
pg_dump -h \$DB_HOST -U \$DB_USER -d \$DB_NAME > \$BACKUP_DIR/db_backup_\$DATE.sql

# Backup media files
tar -czf \$BACKUP_DIR/media_backup_\$DATE.tar.gz media/

# Backup logs
tar -czf \$BACKUP_DIR/logs_backup_\$DATE.tar.gz logs/

# Keep only last 7 days of backups
find \$BACKUP_DIR -name "*.sql" -mtime +7 -delete
find \$BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: \$DATE"
EOF

chmod +x backup.sh

# Create monitoring script
print_status "Creating monitoring script..."
tee monitor.sh > /dev/null << EOF
#!/bin/bash
# Monitoring script for Umoor Sehhat

echo "=== Umoor Sehhat System Status ==="
echo "Service Status:"
systemctl is-active umoor-sehhat.service
echo ""

echo "Memory Usage:"
free -h
echo ""

echo "Disk Usage:"
df -h
echo ""

echo "Recent Logs:"
tail -n 20 logs/django.log
echo ""

echo "Database Connections:"
psql -h \$DB_HOST -U \$DB_USER -d \$DB_NAME -c "SELECT count(*) FROM pg_stat_activity;"
EOF

chmod +x monitor.sh

print_status "🎉 Production deployment completed successfully!"
print_status "Application is running at: https://${DJANGO_ALLOWED_HOSTS%%,*}"
print_status "Admin interface: https://${DJANGO_ALLOWED_HOSTS%%,*}/admin/"
print_status ""
print_status "Useful commands:"
print_status "  sudo systemctl status umoor-sehhat.service  # Check service status"
print_status "  sudo systemctl restart umoor-sehhat.service # Restart service"
print_status "  ./backup.sh                                 # Run backup"
print_status "  ./monitor.sh                                # Check system status"
print_status ""
print_warning "Don't forget to:"
print_warning "  1. Configure SSL certificates"
print_warning "  2. Set up regular backups"
print_warning "  3. Configure monitoring and alerting"
print_warning "  4. Change default admin password"