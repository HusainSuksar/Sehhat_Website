#!/bin/bash

# Umoor Sehhat Production Deployment Script
# Run with: bash deploy.sh

set -e  # Exit on any error

echo "🚀 Starting Umoor Sehhat Production Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/var/www/umoor_sehhat"
SERVICE_NAME="umoor_sehhat"
BACKUP_DIR="/var/backups/umoor_sehhat"

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

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root for security reasons"
   exit 1
fi

# Check if project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    print_error "Project directory $PROJECT_DIR does not exist!"
    exit 1
fi

cd $PROJECT_DIR

# 1. Create backup
print_status "Creating backup..."
mkdir -p $BACKUP_DIR/$(date +%Y-%m-%d)
sudo -u postgres pg_dump umoor_sehhat_prod > "$BACKUP_DIR/$(date +%Y-%m-%d)/database_backup.sql"

# 2. Pull latest code
print_status "Pulling latest code from repository..."
git fetch origin main
git reset --hard origin/main

# 3. Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# 4. Install/update dependencies
print_status "Installing production dependencies..."
pip install -r requirements_production.txt

# 5. Collect static files
print_status "Collecting static files..."
python manage.py collectstatic --noinput --settings=umoor_sehhat.settings_production

# 6. Run migrations
print_status "Running database migrations..."
python manage.py migrate --settings=umoor_sehhat.settings_production

# 7. Check deployment
print_status "Running deployment checks..."
python manage.py check --deploy --settings=umoor_sehhat.settings_production

# 8. Restart services
print_status "Restarting application services..."
sudo systemctl restart $SERVICE_NAME
sudo systemctl restart nginx

# 9. Wait for services to start
print_status "Waiting for services to start..."
sleep 5

# 10. Health check
print_status "Performing health check..."
if curl -f http://localhost/health/ > /dev/null 2>&1; then
    print_status "✅ Deployment successful! Application is running."
else
    print_error "❌ Health check failed! Check logs for issues."
    print_warning "Rolling back to previous version..."
    # Add rollback logic here if needed
    exit 1
fi

# 11. Clear cache
print_status "Clearing application cache..."
python manage.py clear_cache --settings=umoor_sehhat.settings_production

print_status "🎉 Deployment completed successfully!"
echo ""
echo "📊 Post-deployment checklist:"
echo "1. Check application logs: sudo journalctl -u $SERVICE_NAME -f"
echo "2. Monitor system resources: htop"
echo "3. Verify all dashboards are working"
echo "4. Test user authentication"
echo "5. Verify email functionality"
echo ""
echo "🔗 Application URL: https://your-domain.com"