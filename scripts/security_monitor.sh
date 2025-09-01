#!/bin/bash
# Automated Security Monitor for Trading System

LOG_FILE="/home/ubuntu/trading_system/security_monitor.log"
DATE=$(date)

echo "[$DATE] Starting security monitor..." >> $LOG_FILE

# Check file permissions
find /home/ubuntu/trading_system -name "*.db" -not -perm 600 >> $LOG_FILE 2>&1
find /home/ubuntu/trading_system -name ".master_key" -not -perm 600 >> $LOG_FILE 2>&1

# Check for suspicious processes
ps aux | grep -E "(bitcoin|mining|crypto)" >> $LOG_FILE 2>&1

# Check disk usage
df -h | awk '$5 > 90 {print "High disk usage: " $0}' >> $LOG_FILE 2>&1

# Check memory usage
free -m | awk 'NR==2{printf "Memory Usage: %s/%sMB (%.2f%%)
", $3,$2,$3*100/$2 }' >> $LOG_FILE 2>&1

echo "[$DATE] Security monitor completed" >> $LOG_FILE
