"""
Security Setup Script for Trading System
Configures security settings and environment variables
"""

import os
import secrets
import subprocess
import sys

def setup_environment_variables():
    """Setup required environment variables"""
    print("🔧 Setting up environment variables...")
    
    # Generate secure random values
    master_password = secrets.token_urlsafe(32)
    webhook_secret = secrets.token_urlsafe(32)
    
    # Create environment file
    env_file = '/home/ubuntu/trading_system/.env'
    
    env_content = f"""# Trading System Environment Variables
# Generated on {os.popen('date').read().strip()}

# Master encryption password
export TRADING_MASTER_PASSWORD="{master_password}"

# Webhook secret for signature validation
export WEBHOOK_SECRET="{webhook_secret}"

# OpenAI API (already set)
# export OPENAI_API_KEY="your_openai_api_key"

# Binance API (for production)
# export BINANCE_API_KEY="your_binance_api_key"
# export BINANCE_API_SECRET="your_binance_secret"

# Interactive Brokers (for production)
# export IBKR_USERNAME="your_ibkr_username"
# export IBKR_PASSWORD="your_ibkr_password"
"""
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    # Set secure permissions
    os.chmod(env_file, 0o600)
    
    print(f"✅ Environment file created: {env_file}")
    print("📝 To load variables, run: source /home/ubuntu/trading_system/.env")
    
    return master_password, webhook_secret

def fix_file_permissions():
    """Fix file permissions for security"""
    print("🔒 Fixing file permissions...")
    
    files_to_secure = [
        ('/home/ubuntu/trading_system/.master_key', 0o600),
        ('/home/ubuntu/trading_system/security.db', 0o600),
        ('/home/ubuntu/trading_system/trading_data.db', 0o600),
        ('/home/ubuntu/trading_system/security.log', 0o600),
        ('/home/ubuntu/trading_system/.env', 0o600)
    ]
    
    for file_path, permissions in files_to_secure:
        if os.path.exists(file_path):
            os.chmod(file_path, permissions)
            print(f"✅ Set permissions {oct(permissions)} for {os.path.basename(file_path)}")
        else:
            print(f"ℹ️ File {os.path.basename(file_path)} does not exist")

def create_security_policy():
    """Create security policy document"""
    print("📋 Creating security policy...")
    
    policy_content = """# Trading System Security Policy

## Access Control
- All sensitive files must have 600 permissions (owner read/write only)
- Database files must be encrypted and access-controlled
- API keys must be stored encrypted in secure database

## Authentication
- Strong passwords required (minimum 32 characters)
- Session tokens must be cryptographically secure
- Multi-factor authentication recommended for production

## Data Protection
- All sensitive data encrypted at rest
- API keys encrypted with master key
- Database backups encrypted

## Network Security
- HTTPS required for all external communications
- Webhook signatures required for all incoming requests
- Rate limiting implemented on all endpoints

## Monitoring
- All security events logged
- Failed authentication attempts monitored
- Unusual trading activity flagged

## Incident Response
- Security incidents logged immediately
- Kill switch activated for critical threats
- System shutdown procedures documented

## Regular Audits
- Weekly security scans
- Monthly penetration testing
- Quarterly security reviews

## Compliance
- Follow financial industry security standards
- Regular security training for operators
- Documentation of all security procedures
"""
    
    policy_file = '/home/ubuntu/trading_system/SECURITY_POLICY.md'
    with open(policy_file, 'w') as f:
        f.write(policy_content)
    
    print(f"✅ Security policy created: {policy_file}")

def create_security_checklist():
    """Create security checklist for operators"""
    print("✅ Creating security checklist...")
    
    checklist_content = """# Trading System Security Checklist

## Daily Checks
- [ ] Review security logs for anomalies
- [ ] Check system resource usage
- [ ] Verify all services are running
- [ ] Monitor trading activity for unusual patterns

## Weekly Checks
- [ ] Run security audit script
- [ ] Review and rotate API keys if needed
- [ ] Check file permissions
- [ ] Update security patches

## Monthly Checks
- [ ] Full security assessment
- [ ] Backup encryption verification
- [ ] Access control review
- [ ] Incident response drill

## Before Production Deployment
- [ ] Change all default passwords
- [ ] Set production API keys
- [ ] Configure firewall rules
- [ ] Enable monitoring alerts
- [ ] Test kill switch functionality
- [ ] Verify backup procedures

## Emergency Procedures
- [ ] Kill switch activation: `python3 risk_manager.py --kill-switch`
- [ ] System shutdown: `python3 shutdown_system.py`
- [ ] Incident reporting: Document in security.log
- [ ] Recovery procedures: Follow disaster recovery plan

## Security Contacts
- System Administrator: [Your Contact]
- Security Team: [Security Contact]
- Emergency Response: [Emergency Contact]
"""
    
    checklist_file = '/home/ubuntu/trading_system/SECURITY_CHECKLIST.md'
    with open(checklist_file, 'w') as f:
        f.write(checklist_content)
    
    print(f"✅ Security checklist created: {checklist_file}")

def setup_automated_security():
    """Setup automated security monitoring"""
    print("🤖 Setting up automated security...")
    
    # Create security monitoring script
    monitor_script = """#!/bin/bash
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
free -m | awk 'NR==2{printf "Memory Usage: %s/%sMB (%.2f%%)\n", $3,$2,$3*100/$2 }' >> $LOG_FILE 2>&1

echo "[$DATE] Security monitor completed" >> $LOG_FILE
"""
    
    monitor_file = '/home/ubuntu/trading_system/security_monitor.sh'
    with open(monitor_file, 'w') as f:
        f.write(monitor_script)
    
    os.chmod(monitor_file, 0o755)
    print(f"✅ Security monitor script created: {monitor_file}")

def main():
    """Main setup function"""
    print("🔒 Trading System Security Setup")
    print("=" * 40)
    
    # Setup environment variables
    master_password, webhook_secret = setup_environment_variables()
    
    # Fix file permissions
    fix_file_permissions()
    
    # Create security documentation
    create_security_policy()
    create_security_checklist()
    
    # Setup automated monitoring
    setup_automated_security()
    
    print("\n" + "=" * 40)
    print("✅ SECURITY SETUP COMPLETED")
    print("=" * 40)
    
    print("\n📋 Next Steps:")
    print("1. Load environment variables: source /home/ubuntu/trading_system/.env")
    print("2. Run security audit: python3 security_audit.py")
    print("3. Review security policy: cat SECURITY_POLICY.md")
    print("4. Follow security checklist: cat SECURITY_CHECKLIST.md")
    print("5. Test all security features")
    
    print("\n🔑 Generated Credentials:")
    print(f"Master Password: {master_password[:20]}... (see .env file)")
    print(f"Webhook Secret: {webhook_secret[:20]}... (see .env file)")
    
    print("\n⚠️ IMPORTANT:")
    print("- Keep the .env file secure and never commit to version control")
    print("- Change default credentials before production use")
    print("- Run regular security audits")
    print("- Monitor security logs daily")

if __name__ == "__main__":
    main()

