#!/bin/bash

# Umoor Sehhat Production Monitoring Script
# Run this script periodically to monitor application health

# Configuration
APP_URL="https://your-domain.com"
LOG_FILE="/var/log/umoor_sehhat/monitor.log"
ALERT_EMAIL="admin@your-domain.com"

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

# Function to send alert
send_alert() {
    echo "$1" | mail -s "Umoor Sehhat Alert" $ALERT_EMAIL
    log_message "ALERT: $1"
}

# Check application health
check_app_health() {
    log_message "Checking application health..."
    
    if curl -f "$APP_URL/health/" > /dev/null 2>&1; then
        log_message "✅ Application is healthy"
        return 0
    else
        send_alert "❌ Application health check failed"
        return 1
    fi
}

# Check database connection
check_database() {
    log_message "Checking database connection..."
    
    cd /var/www/umoor_sehhat
    source venv/bin/activate
    
    if python manage.py dbshell --settings=umoor_sehhat.settings_production -c "SELECT 1;" > /dev/null 2>&1; then
        log_message "✅ Database is accessible"
        return 0
    else
        send_alert "❌ Database connection failed"
        return 1
    fi
}

# Check disk space
check_disk_space() {
    log_message "Checking disk space..."
    
    DISK_USAGE=$(df /var/www/umoor_sehhat | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [ $DISK_USAGE -gt 80 ]; then
        send_alert "❌ Disk space is low: ${DISK_USAGE}% used"
        return 1
    else
        log_message "✅ Disk space is OK: ${DISK_USAGE}% used"
        return 0
    fi
}

# Check memory usage
check_memory() {
    log_message "Checking memory usage..."
    
    MEMORY_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    
    if [ $MEMORY_USAGE -gt 90 ]; then
        send_alert "❌ Memory usage is high: ${MEMORY_USAGE}%"
        return 1
    else
        log_message "✅ Memory usage is OK: ${MEMORY_USAGE}%"
        return 0
    fi
}

# Check service status
check_services() {
    log_message "Checking service status..."
    
    services=("umoor_sehhat" "nginx" "postgresql" "redis")
    
    for service in "${services[@]}"; do
        if systemctl is-active --quiet $service; then
            log_message "✅ $service is running"
        else
            send_alert "❌ $service is not running"
        fi
    done
}

# Run all checks
main() {
    log_message "=== Starting health check ==="
    
    check_app_health
    check_database
    check_disk_space
    check_memory
    check_services
    
    log_message "=== Health check completed ==="
    echo ""
}

# Run main function
main