# PowerShell script to reset migrations and database
# Run this in PowerShell as Administrator

Write-Host "===============================================" -ForegroundColor Yellow
Write-Host "UMOOR SEHHAT - MIGRATION RESET SCRIPT" -ForegroundColor Yellow
Write-Host "===============================================" -ForegroundColor Yellow

# Check if venv is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "`nActivating virtual environment..." -ForegroundColor Cyan
    & ".\venv\Scripts\Activate.ps1"
}

# Backup database
Write-Host "`n[1/7] Backing up database..." -ForegroundColor Green
if (Test-Path "db.sqlite3") {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupName = "db.sqlite3.backup_$timestamp"
    Copy-Item "db.sqlite3" $backupName
    Write-Host "✓ Database backed up to $backupName" -ForegroundColor Green
} else {
    Write-Host "✓ No existing database found" -ForegroundColor Green
}

# Delete old database
Write-Host "`n[2/7] Removing old database..." -ForegroundColor Green
if (Test-Path "db.sqlite3") {
    Remove-Item "db.sqlite3" -Force
    Write-Host "✓ Database removed" -ForegroundColor Green
}

# Clean migration files
Write-Host "`n[3/7] Cleaning migration files..." -ForegroundColor Green
$apps = @(
    "accounts", "moze", "mahalshifa", "doctordirectory", 
    "appointments", "surveys", "photos", "evaluation", 
    "araz", "students", "guardian", "services", "bulk_upload"
)

foreach ($app in $apps) {
    $migrationDir = Join-Path $app "migrations"
    if (Test-Path $migrationDir) {
        # Remove all .py files except __init__.py
        Get-ChildItem -Path $migrationDir -Filter "*.py" | 
            Where-Object { $_.Name -ne "__init__.py" } | 
            Remove-Item -Force -ErrorAction SilentlyContinue
        
        # Remove __pycache__
        $pycacheDir = Join-Path $migrationDir "__pycache__"
        if (Test-Path $pycacheDir) {
            Remove-Item $pycacheDir -Recurse -Force -ErrorAction SilentlyContinue
        }
        
        Write-Host "  ✓ Cleaned $app migrations" -ForegroundColor Gray
    }
}

# Create fresh migrations
Write-Host "`n[4/7] Creating fresh migrations..." -ForegroundColor Green
python manage.py makemigrations

# Apply migrations
Write-Host "`n[5/7] Applying migrations..." -ForegroundColor Green
python manage.py migrate

# Create superuser
Write-Host "`n[6/7] Creating superuser (optional)..." -ForegroundColor Green
Write-Host "Username: admin" -ForegroundColor Cyan
Write-Host "Email: admin@example.com" -ForegroundColor Cyan
Write-Host "Password: admin123" -ForegroundColor Cyan
$createSuper = Read-Host "Create superuser with these credentials? (y/n)"

if ($createSuper -eq 'y') {
    $env:DJANGO_SUPERUSER_USERNAME = "admin"
    $env:DJANGO_SUPERUSER_EMAIL = "admin@example.com"
    $env:DJANGO_SUPERUSER_PASSWORD = "admin123"
    python manage.py createsuperuser --noinput
    Write-Host "✓ Superuser created" -ForegroundColor Green
}

# Generate test data
Write-Host "`n[7/7] Generating test data..." -ForegroundColor Green
$generateData = Read-Host "Generate mock data? (y/n)"

if ($generateData -eq 'y') {
    python generate_mock_data.py
}

Write-Host "`n===============================================" -ForegroundColor Yellow
Write-Host "MIGRATION RESET COMPLETE!" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Yellow

Write-Host "`nYou can now run:" -ForegroundColor Cyan
Write-Host "python manage.py runserver" -ForegroundColor White

Write-Host "`nLogin credentials:" -ForegroundColor Cyan
Write-Host "Admin: admin / admin123" -ForegroundColor White
Write-Host "All test users: pass1234" -ForegroundColor White