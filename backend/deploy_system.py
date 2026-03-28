"""
Deployment Script for Trading System
Handles system integration, deployment, and monitoring setup
"""

import os
import subprocess
import json
import shutil
from datetime import datetime

class TradingSystemDeployer:
    """Handles deployment of the complete trading system"""
    
    def __init__(self):
        self.base_dir = '/home/ubuntu/trading_system'
        self.api_dir = '/home/ubuntu/trading-api'
        self.dashboard_dir = '/home/ubuntu/trading-dashboard'
        self.deployment_log = []
    
    def log(self, message: str, level: str = 'INFO'):
        """Log deployment messages"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {level}: {message}"
        self.deployment_log.append(log_entry)
        print(log_entry)
    
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met"""
        self.log("Checking deployment prerequisites...")
        
        required_dirs = [self.base_dir, self.api_dir, self.dashboard_dir]
        for dir_path in required_dirs:
            if not os.path.exists(dir_path):
                self.log(f"Missing required directory: {dir_path}", 'ERROR')
                return False
            else:
                self.log(f"✅ Found directory: {dir_path}")
        
        # Check Python dependencies
        required_packages = ['flask', 'flask-cors', 'cryptography', 'pandas', 'numpy']
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                self.log(f"✅ Package available: {package}")
            except ImportError:
                self.log(f"Missing package: {package}", 'ERROR')
                return False
        
        return True
    
    def create_docker_files(self):
        """Create Docker configuration files"""
        self.log("Creating Docker configuration...")
        
        # Dockerfile for the trading system
        dockerfile_content = """FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data /app/logs

# Set environment variables
ENV PYTHONPATH=/app
ENV FLASK_APP=src/main_simple.py
ENV FLASK_ENV=production

# Expose port
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:5001/api/health || exit 1

# Run the application
CMD ["python", "src/main_simple.py"]
"""
        
        with open(os.path.join(self.api_dir, 'Dockerfile'), 'w') as f:
            f.write(dockerfile_content)
        
        # Docker Compose file
        docker_compose_content = """version: '3.8'

services:
  trading-api:
    build: .
    ports:
      - "5001:5001"
    environment:
      - FLASK_ENV=production
      - TRADING_MASTER_PASSWORD=${TRADING_MASTER_PASSWORD}
      - WEBHOOK_SECRET=${WEBHOOK_SECRET}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5001/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  trading-dashboard:
    image: nginx:alpine
    ports:
      - "3000:80"
    volumes:
      - ./dashboard/dist:/usr/share/nginx/html
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - trading-api
    restart: unless-stopped

volumes:
  trading_data:
  trading_logs:
"""
        
        with open(os.path.join(self.api_dir, 'docker-compose.yml'), 'w') as f:
            f.write(docker_compose_content)
        
        self.log("✅ Docker files created")
    
    def create_requirements_file(self):
        """Create requirements.txt for deployment"""
        self.log("Creating requirements.txt...")
        
        requirements = [
            'flask==3.1.1',
            'flask-cors==6.0.0',
            'flask-sqlalchemy==3.1.1',
            'cryptography==45.0.7',
            'pandas==2.3.2',
            'numpy==2.3.2',
            'requests==2.32.5',
            'schedule==1.2.2',
            'matplotlib==3.10.6'
        ]
        
        with open(os.path.join(self.api_dir, 'requirements.txt'), 'w') as f:
            f.write('\n'.join(requirements))
        
        self.log("✅ Requirements file created")
    
    def create_nginx_config(self):
        """Create Nginx configuration for reverse proxy"""
        self.log("Creating Nginx configuration...")
        
        nginx_config = """events {
    worker_connections 1024;
}

http {
    upstream trading_api {
        server trading-api:5001;
    }
    
    server {
        listen 80;
        server_name localhost;
        
        # Serve static files
        location / {
            root /usr/share/nginx/html;
            index index.html;
            try_files $uri $uri/ /index.html;
        }
        
        # Proxy API requests
        location /api/ {
            proxy_pass http://trading_api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Health check
        location /health {
            access_log off;
            return 200 "healthy\\n";
            add_header Content-Type text/plain;
        }
    }
}
"""
        
        with open(os.path.join(self.api_dir, 'nginx.conf'), 'w') as f:
            f.write(nginx_config)
        
        self.log("✅ Nginx configuration created")
    
    def create_monitoring_scripts(self):
        """Create monitoring and maintenance scripts"""
        self.log("Creating monitoring scripts...")
        
        # Health check script
        health_check_script = """#!/bin/bash
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
"""
        
        with open(os.path.join(self.base_dir, 'health_check.sh'), 'w') as f:
            f.write(health_check_script)
        
        os.chmod(os.path.join(self.base_dir, 'health_check.sh'), 0o755)
        
        # Backup script
        backup_script = """#!/bin/bash
# Backup Script for Trading System

BACKUP_DIR="/backup/trading_system"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="trading_system_backup_$DATE.tar.gz"

mkdir -p $BACKUP_DIR

echo "$(date): Starting backup..." >> /var/log/trading_system_backup.log

# Create backup
tar -czf "$BACKUP_DIR/$BACKUP_FILE" \\
    /home/ubuntu/trading_system \\
    /home/ubuntu/trading-api \\
    /home/ubuntu/trading-dashboard \\
    --exclude="*.log" \\
    --exclude="node_modules" \\
    --exclude="venv" \\
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
"""
        
        with open(os.path.join(self.base_dir, 'backup.sh'), 'w') as f:
            f.write(backup_script)
        
        os.chmod(os.path.join(self.base_dir, 'backup.sh'), 0o755)
        
        self.log("✅ Monitoring scripts created")
    
    def create_systemd_services(self):
        """Create systemd service files"""
        self.log("Creating systemd service files...")
        
        # Trading API service
        api_service = """[Unit]
Description=Trading System API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/trading-api
Environment=PATH=/home/ubuntu/trading-api/venv/bin
Environment=PYTHONPATH=/home/ubuntu/trading_system
ExecStart=/home/ubuntu/trading-api/venv/bin/python src/main_simple.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        with open('/tmp/trading-api.service', 'w') as f:
            f.write(api_service)
        
        self.log("✅ Systemd service files created in /tmp/")
        self.log("To install: sudo cp /tmp/trading-api.service /etc/systemd/system/")
    
    def create_deployment_summary(self):
        """Create deployment summary and instructions"""
        self.log("Creating deployment summary...")
        
        summary = f"""# Trading System Deployment Summary

**Deployment Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## System Components

### 1. Core Trading System
- **Location:** `/home/ubuntu/trading_system`
- **Components:** Data collection, signal generation, risk management, order execution
- **Security:** 95.5/100 security score, encrypted API keys, comprehensive audit system

### 2. Flask API Server
- **Location:** `/home/ubuntu/trading-api`
- **Port:** 5001
- **Endpoints:** Health, status, portfolio, orders, signals, security
- **Features:** CORS enabled, comprehensive error handling, security integration

### 3. React Dashboard
- **Location:** `/home/ubuntu/trading-dashboard`
- **Port:** 5174 (development)
- **Features:** Real-time monitoring, interactive charts, webhook testing

## Deployment Options

### Option 1: Docker Deployment (Recommended)
```bash
cd /home/ubuntu/trading-api
docker-compose up -d
```

### Option 2: Systemd Services
```bash
sudo cp /tmp/trading-api.service /etc/systemd/system/
sudo systemctl enable trading-api
sudo systemctl start trading-api
```

### Option 3: Manual Deployment
```bash
cd /home/ubuntu/trading-api
source venv/bin/activate
python src/main_simple.py
```

## Monitoring and Maintenance

### Health Checks
- **Script:** `/home/ubuntu/trading_system/health_check.sh`
- **Frequency:** Every 5 minutes (recommended)
- **Logs:** `/var/log/trading_system_health.log`

### Backups
- **Script:** `/home/ubuntu/trading_system/backup.sh`
- **Frequency:** Daily (recommended)
- **Location:** `/backup/trading_system/`

### Security Audits
```bash
cd /home/ubuntu/trading_system
python security_audit.py
```

## API Endpoints

- **Health Check:** `GET /api/health`
- **System Status:** `GET /api/status`
- **Portfolio:** `GET /api/portfolio/status`
- **Orders:** `GET /api/orders`
- **Signals:** `GET /api/signals/recommendations`
- **Security Events:** `GET /api/security/events`
- **Emergency Kill Switch:** `POST /api/emergency/kill-switch`

## Production Checklist

- [ ] Set production environment variables
- [ ] Configure SSL/TLS certificates
- [ ] Set up firewall rules
- [ ] Configure monitoring alerts
- [ ] Test backup and recovery procedures
- [ ] Set up log rotation
- [ ] Configure rate limiting
- [ ] Set up load balancing (if needed)

## Support and Maintenance

### Log Files
- API logs: `/home/ubuntu/trading-api/logs/`
- Security logs: `/home/ubuntu/trading_system/security.log`
- System logs: `/var/log/trading_system_*.log`

### Configuration Files
- Security config: `/home/ubuntu/trading_system/.env`
- API config: `/home/ubuntu/trading-api/src/main_simple.py`
- Docker config: `/home/ubuntu/trading-api/docker-compose.yml`

### Emergency Procedures
1. **System Shutdown:** `POST /api/emergency/kill-switch`
2. **Service Restart:** `sudo systemctl restart trading-api`
3. **Full System Reset:** Run deployment script again

---
*Generated by Trading System Deployer v1.0*
"""
        
        with open(os.path.join(self.base_dir, 'DEPLOYMENT_SUMMARY.md'), 'w') as f:
            f.write(summary)
        
        self.log("✅ Deployment summary created")
    
    def run_deployment(self):
        """Run complete deployment process"""
        self.log("🚀 Starting Trading System Deployment")
        self.log("=" * 50)
        
        if not self.check_prerequisites():
            self.log("Prerequisites check failed. Aborting deployment.", 'ERROR')
            return False
        
        try:
            self.create_requirements_file()
            self.create_docker_files()
            self.create_nginx_config()
            self.create_monitoring_scripts()
            self.create_systemd_services()
            self.create_deployment_summary()
            
            self.log("=" * 50)
            self.log("✅ DEPLOYMENT COMPLETED SUCCESSFULLY")
            self.log("=" * 50)
            
            self.log("📋 Next Steps:")
            self.log("1. Review deployment summary: cat DEPLOYMENT_SUMMARY.md")
            self.log("2. Choose deployment method (Docker recommended)")
            self.log("3. Set up monitoring and backups")
            self.log("4. Configure production environment")
            
            return True
            
        except Exception as e:
            self.log(f"Deployment failed: {e}", 'ERROR')
            return False
    
    def save_deployment_log(self):
        """Save deployment log to file"""
        log_file = os.path.join(self.base_dir, f'deployment_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')
        with open(log_file, 'w') as f:
            f.write('\n'.join(self.deployment_log))
        self.log(f"Deployment log saved to: {log_file}")


def main():
    """Main deployment function"""
    deployer = TradingSystemDeployer()
    success = deployer.run_deployment()
    deployer.save_deployment_log()
    
    if success:
 print("\n Trading System is ready for deployment!")
 print("Read DEPLOYMENT_SUMMARY.md for detailed instructions")
    else:
 print("\n Deployment failed. Check the logs for details.")
    
    return success


if __name__ == "__main__":
    main()

