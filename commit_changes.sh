#!/bin/bash

echo "🔍 Checking git status..."
git status

echo ""
echo "📦 Adding all changes..."
git add .

echo ""
echo "📋 Checking staged files..."
git status

echo ""
echo "💾 Committing changes..."
git commit -m "Fix mahalshifa create functionality and add admin links

- Fixed create buttons in hospital_list.html and patient_list.html
- Updated hospital_create.html and patient_create.html to use proper Django forms
- Added all mahalshifa admin links to dropdown menu in base.html
- Fixed form field rendering to use {{ form.field_name }} instead of hardcoded HTML
- Added proper error handling and validation in create templates
- Ensured all create views have correct permission checks
- Added missing admin links: Patients, Appointments, Medical Records, Analytics, Inventory, Export Data"

echo ""
echo "🚀 Pushing to main branch..."
git push origin main

echo ""
echo "✅ Done!"