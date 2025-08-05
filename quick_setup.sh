#!/bin/bash

# Quick Setup Script for Umoor Sehhat on PythonAnywhere
# This script handles the most common setup tasks automatically

set -e

echo "🚀 UMOOR SEHHAT - QUICK SETUP FOR PYTHONANYWHERE"
echo "=================================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Get username automatically
USERNAME=$(whoami)
PROJECT_DIR="/home/$USERNAME/umoor_sehhat"

echo -e "${GREEN}Setting up for user: $USERNAME${NC}"
echo -e "${GREEN}Project directory: $PROJECT_DIR${NC}"
echo ""

# Function to prompt for input with default
prompt_with_default() {
    local prompt="$1"
    local default="$2"
    local result
    
    read -p "$prompt [$default]: " result
    echo "${result:-$default}"
}

# Function to generate secret key
generate_secret_key() {
    python3.10 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
}

echo "📋 CONFIGURATION SETUP"
echo "======================"

# Get database password
echo -e "${YELLOW}Please provide your MySQL database password from PythonAnywhere dashboard:${NC}"
DB_PASSWORD=$(prompt_with_default "MySQL Password" "")

if [ -z "$DB_PASSWORD" ]; then
    echo -e "${RED}Database password is required!${NC}"
    exit 1
fi

# Generate secret key
echo -e "${YELLOW}Generating Django secret key...${NC}"
SECRET_KEY=$(generate_secret_key)

# Create .env file
echo -e "${GREEN}Creating .env configuration file...${NC}"
cat > .env << EOF
# PythonAnywhere Environment Configuration
# Generated on $(date)

# Django Configuration
DEBUG=False
SECRET_KEY=$SECRET_KEY
DJANGO_SETTINGS_MODULE=umoor_sehhat.settings_pythonanywhere

# Database Configuration
DB_NAME=${USERNAME}\$umoor_sehhat
DB_USER=$USERNAME
DB_PASSWORD=$DB_PASSWORD
DB_HOST=${USERNAME}.mysql.pythonanywhere-services.com
DB_PORT=3306

# Allowed Hosts
ALLOWED_HOSTS=${USERNAME}.pythonanywhere.com,localhost,127.0.0.1

# Static and Media Files
STATIC_ROOT=/home/$USERNAME/umoor_sehhat/staticfiles
MEDIA_ROOT=/home/$USERNAME/umoor_sehhat/media

# Email Configuration (Optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=noreply@${USERNAME}.pythonanywhere.com

# Security Settings
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False

# Time Zone
TIME_ZONE=Asia/Karachi

# Application Settings
TEST_MODE=False
EOF

echo -e "${GREEN}✅ Environment file created successfully!${NC}"

# Install dependencies
echo ""
echo "📦 INSTALLING DEPENDENCIES"
echo "=========================="
pip3.10 install --user -r requirements_pythonanywhere.txt

# Create directories
echo ""
echo "📁 CREATING DIRECTORIES"
echo "======================="
mkdir -p staticfiles
mkdir -p media
chmod 755 media

# Collect static files
echo ""
echo "📄 COLLECTING STATIC FILES"
echo "=========================="
python3.10 manage.py collectstatic --noinput --settings=umoor_sehhat.settings_pythonanywhere

# Run migrations
echo ""
echo "🗄️  RUNNING DATABASE MIGRATIONS"
echo "==============================="
python3.10 manage.py migrate --settings=umoor_sehhat.settings_pythonanywhere

# Create test users
echo ""
echo "👥 CREATING TEST USERS"
echo "===================="
python3.10 create_test_users.py

# Run health check
echo ""
echo "🏥 RUNNING HEALTH CHECK"
echo "======================"
python3.10 health_check.py

# Final instructions
echo ""
echo "🎉 SETUP COMPLETE!"
echo "=================="
echo ""
echo -e "${GREEN}Your Umoor Sehhat application is ready for PythonAnywhere!${NC}"
echo ""
echo "📋 NEXT STEPS:"
echo "1. Go to PythonAnywhere Web tab"
echo "2. Create new web app (Manual configuration, Python 3.10)"
echo "3. Set Source code: $PROJECT_DIR"
echo "4. Set Working directory: $PROJECT_DIR"
echo "5. Set Virtualenv: /home/$USERNAME/.local"
echo "6. Edit WSGI configuration file:"
echo ""
echo "   Replace the contents with:"
echo "   ----------------------------------------"
cat << 'EOF'
   import os
   import sys
   
   # Replace 'yourusername' with your actual username
   path = '/home/yourusername/umoor_sehhat'
   if path not in sys.path:
       sys.path.insert(0, path)
   
   os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings_pythonanywhere')
   
   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
EOF
echo "   ----------------------------------------"
echo ""
echo "7. Add Static files mapping:"
echo "   URL: /static/"
echo "   Directory: $PROJECT_DIR/staticfiles"
echo ""
echo "8. Add Media files mapping:"
echo "   URL: /media/"
echo "   Directory: $PROJECT_DIR/media"
echo ""
echo "9. Click 'Reload' button"
echo ""
echo "🔗 Your app will be available at: https://$USERNAME.pythonanywhere.com"
echo ""
echo "🔑 TEST CREDENTIALS (password: test123456):"
echo "   Admin: admin_user1, admin_user2"
echo "   Aamil: aamil_001, aamil_002"
echo "   Student: student_001, student_002, student_003"
echo "   Doctor: doctor_001, doctor_002"
echo ""
echo "🛠️  USEFUL COMMANDS:"
echo "   Health check: python3.10 health_check.py --web --username $USERNAME"
echo "   Database management: python3.10 manage_database.py"
echo "   Reset test users: python3.10 create_test_users.py"
echo ""
echo -e "${GREEN}Happy testing! 🚀${NC}"