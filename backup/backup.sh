#!/bin/bash

# Umoor Sehhat Backup Script
# Automated database and media backup

# Configuration
BACKUP_DIR="/var/backups/umoor_sehhat"
DB_NAME="umoor_sehhat_prod"
DB_USER="umoor_sehhat_user"
MEDIA_DIR="/var/www/umoor_sehhat/media"
RETENTION_DAYS=30

# Create timestamped backup directory
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="$BACKUP_DIR/$TIMESTAMP"
mkdir -p $BACKUP_PATH

# Database backup
echo "Creating database backup..."
pg_dump -U $DB_USER -h localhost $DB_NAME | gzip > "$BACKUP_PATH/database_$TIMESTAMP.sql.gz"

# Media files backup
echo "Creating media files backup..."
tar -czf "$BACKUP_PATH/media_$TIMESTAMP.tar.gz" -C $(dirname $MEDIA_DIR) $(basename $MEDIA_DIR)

# Application code backup (excluding venv and cache)
echo "Creating application backup..."
cd /var/www/umoor_sehhat
tar --exclude='venv' --exclude='__pycache__' --exclude='*.pyc' --exclude='.git' \
    -czf "$BACKUP_PATH/application_$TIMESTAMP.tar.gz" .

# Clean old backups
echo "Cleaning old backups..."
find $BACKUP_DIR -type d -mtime +$RETENTION_DAYS -exec rm -rf {} +

# Create backup info file
cat > "$BACKUP_PATH/backup_info.txt" << EOF
Backup Created: $(date)
Database: $DB_NAME
Media Directory: $MEDIA_DIR
Backup Size: $(du -sh $BACKUP_PATH | cut -f1)
EOF

echo "Backup completed successfully at $BACKUP_PATH"