#!/bin/bash

# PythonAnywhere Deployment Script for Umoor Sehhat
# Run this in PythonAnywhere Bash console

echo "🚀 Setting up Umoor Sehhat on PythonAnywhere..."

# 1. Clone repository
cd ~
git clone https://github.com/HusainSuksar/Sehhat_Website.git umoor_sehhat
cd umoor_sehhat

# 2. Create virtual environment (Python 3.10)
mkvirtualenv --python=/usr/bin/python3.10 umoor_sehhat_env

# 3. Install dependencies
pip install -r requirements.txt
pip install python-decouple  # For environment management

# 4. Create PythonAnywhere settings
cp umoor_sehhat/settings.py umoor_sehhat/settings_pythonanywhere.py

echo "✅ Basic setup completed!"
echo "Next steps:"
echo "1. Configure settings in settings_pythonanywhere.py"
echo "2. Set up database"
echo "3. Create test users"
echo "4. Configure web app in PythonAnywhere dashboard"