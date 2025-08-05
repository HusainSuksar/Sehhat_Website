#!/bin/bash

# PythonAnywhere Deployment Script for Umoor Sehhat
# Run this script in PythonAnywhere Bash console after initial setup

set -e  # Exit on any error

echo "🚀 Starting PythonAnywhere deployment for Umoor Sehhat..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Get username
USERNAME=$(whoami)
PROJECT_DIR="/home/$USERNAME/umoor_sehhat"

print_status "Deploying for user: $USERNAME"
print_status "Project directory: $PROJECT_DIR"

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    print_error "manage.py not found. Please run this script from the project root directory."
    exit 1
fi

# Step 1: Install dependencies
print_step "1. Installing Python dependencies..."
pip3.10 install --user -r requirements_pythonanywhere.txt

# Step 2: Check if .env file exists
print_step "2. Checking environment configuration..."
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating from template..."
    cp .env.pythonanywhere.template .env
    print_warning "Please edit .env file with your actual values before continuing!"
    print_warning "Update the following in .env:"
    echo "  - SECRET_KEY (generate a new one)"
    echo "  - DB_PASSWORD (from PythonAnywhere MySQL dashboard)"
    echo "  - Replace 'yourusername' with '$USERNAME'"
    echo ""
    read -p "Press Enter after updating .env file..."
fi

# Step 3: Update .env file with correct username
print_step "3. Updating .env file with correct username..."
sed -i "s/yourusername/$USERNAME/g" .env

# Step 4: Collect static files
print_step "4. Collecting static files..."
mkdir -p staticfiles
python3.10 manage.py collectstatic --noinput --settings=umoor_sehhat.settings_pythonanywhere

# Step 5: Run migrations
print_step "5. Running database migrations..."
python3.10 manage.py migrate --settings=umoor_sehhat.settings_pythonanywhere

# Step 6: Create superuser (if needed)
print_step "6. Checking for superuser..."
SUPERUSER_EXISTS=$(python3.10 manage.py shell --settings=umoor_sehhat.settings_pythonanywhere -c "from django.contrib.auth import get_user_model; User = get_user_model(); print(User.objects.filter(is_superuser=True).exists())")

if [[ "$SUPERUSER_EXISTS" == *"False"* ]]; then
    print_warning "No superuser found. You may want to create one:"
    echo "python3.10 manage.py createsuperuser --settings=umoor_sehhat.settings_pythonanywhere"
fi

# Step 7: Create test users
print_step "7. Creating test users..."
python3.10 create_test_users.py

# Step 8: Check deployment
print_step "8. Running deployment checks..."
python3.10 manage.py check --deploy --settings=umoor_sehhat.settings_pythonanywhere

# Step 9: Set up media directory
print_step "9. Setting up media directory..."
mkdir -p media
chmod 755 media

# Step 10: Display important information
print_step "10. Deployment Summary"
echo ""
echo "✅ Deployment completed successfully!"
echo ""
echo "📋 Next Steps:"
echo "1. Go to PythonAnywhere Web tab"
echo "2. Create a new web app (Manual configuration, Python 3.10)"
echo "3. Set source code: $PROJECT_DIR"
echo "4. Set working directory: $PROJECT_DIR"
echo "5. Edit WSGI file and paste contents from pythonanywhere_wsgi.py"
echo "6. Set virtualenv: /home/$USERNAME/.local"
echo "7. Add static files mapping:"
echo "   URL: /static/"
echo "   Directory: $PROJECT_DIR/staticfiles"
echo "8. Add media files mapping:"
echo "   URL: /media/"
echo "   Directory: $PROJECT_DIR/media"
echo "9. Reload your web app"
echo ""
echo "🔗 Your app will be available at: https://$USERNAME.pythonanywhere.com"
echo ""
echo "🔑 Test Login Credentials (password: test123456):"
echo "   Admin: admin_user1, admin_user2"
echo "   Aamil: aamil_001, aamil_002"
echo "   Student: student_001, student_002, student_003"
echo "   Doctor: doctor_001, doctor_002"
echo ""
echo "📝 Important Files:"
echo "   - Settings: umoor_sehhat/settings_pythonanywhere.py"
echo "   - Environment: .env"
echo "   - WSGI: pythonanywhere_wsgi.py"
echo "   - Test Users: create_test_users.py"
echo ""
print_status "🎉 Ready for PythonAnywhere web app configuration!"