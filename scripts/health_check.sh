#!/bin/bash
# Health Check Script for Trading System

API_URL="http://localhost:5001/api/health"
DASHBOARD_URL="http://localhost:3000"
LOG_FILE="/var/log/trading_system_health.log"

echo "$(date): Starting health check..." >> $LOG_FILE

# Check API health
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $API_URL)
if [ $API_STATUS -eq 200 ]; then
    echo "$(date): API is healthy" >> $LOG_FILE
else
    echo "$(date): API is unhealthy (status: $API_STATUS)" >> $LOG_FILE
    # Send alert (implement notification system)
fi

# Check Dashboard
DASHBOARD_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $DASHBOARD_URL)
if [ $DASHBOARD_STATUS -eq 200 ]; then
    echo "$(date): Dashboard is healthy" >> $LOG_FILE
else
    echo "$(date): Dashboard is unhealthy (status: $DASHBOARD_STATUS)" >> $LOG_FILE
fi

# Check disk space
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "$(date): High disk usage: ${DISK_USAGE}%" >> $LOG_FILE
fi

# Check memory usage
MEMORY_USAGE=$(free | awk 'NR==2{printf "%.2f", $3*100/$2}')
if (( $(echo "$MEMORY_USAGE > 80" | bc -l) )); then
    echo "$(date): High memory usage: ${MEMORY_USAGE}%" >> $LOG_FILE
fi

echo "$(date): Health check completed" >> $LOG_FILE
