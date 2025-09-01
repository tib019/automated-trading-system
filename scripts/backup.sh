#!/bin/bash
# Backup Script for Trading System

BACKUP_DIR="/backup/trading_system"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="trading_system_backup_$DATE.tar.gz"

mkdir -p $BACKUP_DIR

echo "$(date): Starting backup..." >> /var/log/trading_system_backup.log

# Create backup
tar -czf "$BACKUP_DIR/$BACKUP_FILE" \
    /home/ubuntu/trading_system \
    /home/ubuntu/trading-api \
    /home/ubuntu/trading-dashboard \
    --exclude="*.log" \
    --exclude="node_modules" \
    --exclude="venv" \
    --exclude="__pycache__"

if [ $? -eq 0 ]; then
    echo "$(date): Backup created successfully: $BACKUP_FILE" >> /var/log/trading_system_backup.log
    
    # Keep only last 7 backups
    cd $BACKUP_DIR
    ls -t trading_system_backup_*.tar.gz | tail -n +8 | xargs -r rm
    
    echo "$(date): Old backups cleaned up" >> /var/log/trading_system_backup.log
else
    echo "$(date): Backup failed" >> /var/log/trading_system_backup.log
fi
