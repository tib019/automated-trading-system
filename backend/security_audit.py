"""
Security Audit Tool for Trading System
Comprehensive security assessment and vulnerability scanning
"""

import os
import sqlite3
import json
import hashlib
import subprocess
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import sys

sys.path.append('/home/ubuntu/trading_system')
from security_manager import SecurityManager


class SecurityAuditor:
    """Comprehensive security auditing for the trading system"""
    
    def __init__(self):
        self.security_manager = SecurityManager()
        self.audit_results = {
            'timestamp': datetime.now().isoformat(),
            'checks': [],
            'vulnerabilities': [],
            'recommendations': [],
            'score': 0
        }
    
    def run_full_audit(self) -> Dict:
        """Run complete security audit"""
        print("🔒 Starting Security Audit...")
        print("=" * 50)
        
        # File system security
        self.check_file_permissions()
        self.check_sensitive_files()
        
        # Database security
        self.check_database_security()
        
        # Configuration security
        self.check_configuration_security()
        
        # API security
        self.check_api_security()
        
        # Encryption security
        self.check_encryption_security()
        
        # Network security
        self.check_network_security()
        
        # Input validation
        self.check_input_validation()
        
        # Authentication and authorization
        self.check_auth_security()
        
        # Logging and monitoring
        self.check_logging_security()
        
        # Calculate overall security score
        self.calculate_security_score()
        
        return self.audit_results
    
    def check_file_permissions(self):
        """Check file and directory permissions"""
        print("📁 Checking file permissions...")
        
        critical_files = [
            '/home/ubuntu/trading_system/.master_key',
            '/home/ubuntu/trading_system/security.db',
            '/home/ubuntu/trading_system/trading_data.db',
            '/home/ubuntu/trading_system/config.py'
        ]
        
        for file_path in critical_files:
            if os.path.exists(file_path):
                stat_info = os.stat(file_path)
                permissions = oct(stat_info.st_mode)[-3:]
                
                if file_path.endswith('.master_key'):
                    if permissions == '600':
                        self.add_check("✅ Master key file has secure permissions (600)")
                    else:
                        self.add_vulnerability(f"⚠️ Master key file permissions: {permissions} (should be 600)")
                
                elif file_path.endswith('.db'):
                    if permissions in ['600', '640']:
                        self.add_check(f"✅ Database file {os.path.basename(file_path)} has secure permissions ({permissions})")
                    else:
                        self.add_vulnerability(f"⚠️ Database file {os.path.basename(file_path)} permissions: {permissions} (should be 600 or 640)")
                
                else:
                    if permissions in ['644', '640', '600']:
                        self.add_check(f"✅ Config file {os.path.basename(file_path)} has acceptable permissions ({permissions})")
                    else:
                        self.add_vulnerability(f"⚠️ Config file {os.path.basename(file_path)} permissions: {permissions}")
            else:
                self.add_check(f"ℹ️ File {os.path.basename(file_path)} does not exist")
    
    def check_sensitive_files(self):
        """Check for sensitive files in wrong locations"""
        print("🔍 Checking for sensitive files...")
        
        # Check for API keys in code files
        code_files = []
        for root, dirs, files in os.walk('/home/ubuntu/trading_system'):
            for file in files:
                if file.endswith(('.py', '.js', '.json', '.yaml', '.yml')):
                    code_files.append(os.path.join(root, file))
        
        sensitive_patterns = [
            'api_key',
            'api_secret',
            'password',
            'token',
            'secret_key'
        ]
        
        for file_path in code_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().lower()
                    
                for pattern in sensitive_patterns:
                    if pattern in content and 'test' not in content:
                        # Check if it's a hardcoded value
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if pattern in line and '=' in line and not line.strip().startswith('#'):
                                self.add_vulnerability(f"⚠️ Potential hardcoded {pattern} in {os.path.basename(file_path)}:{i+1}")
                                break
            except Exception:
                continue
        
        self.add_check("✅ Sensitive file scan completed")
    
    def check_database_security(self):
        """Check database security configuration"""
        print("🗄️ Checking database security...")
        
        db_files = [
            '/home/ubuntu/trading_system/security.db',
            '/home/ubuntu/trading_system/trading_data.db'
        ]
        
        for db_file in db_files:
            if os.path.exists(db_file):
                try:
                    conn = sqlite3.connect(db_file)
                    cursor = conn.cursor()
                    
                    # Check for tables
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = cursor.fetchall()
                    
                    if tables:
                        self.add_check(f"✅ Database {os.path.basename(db_file)} has {len(tables)} tables")
                        
                        # Check for encrypted data
                        for table in tables:
                            table_name = table[0]
                            cursor.execute(f"PRAGMA table_info({table_name})")
                            columns = cursor.fetchall()
                            
                            encrypted_columns = [col for col in columns if 'encrypted' in col[1].lower()]
                            if encrypted_columns:
                                self.add_check(f"✅ Table {table_name} has encrypted columns")
                    
                    conn.close()
                    
                except Exception as e:
                    self.add_vulnerability(f"⚠️ Database {os.path.basename(db_file)} access error: {e}")
    
    def check_configuration_security(self):
        """Check configuration security"""
        print("⚙️ Checking configuration security...")
        
        # Check environment variables
        sensitive_env_vars = [
            'TRADING_MASTER_PASSWORD',
            'WEBHOOK_SECRET',
            'OPENAI_API_KEY'
        ]
        
        for env_var in sensitive_env_vars:
            if os.environ.get(env_var):
                if env_var == 'TRADING_MASTER_PASSWORD' and os.environ.get(env_var) == 'default_password_change_me':
                    self.add_vulnerability("⚠️ Default master password is being used")
                else:
                    self.add_check(f"✅ Environment variable {env_var} is set")
            else:
                self.add_vulnerability(f"⚠️ Environment variable {env_var} is not set")
        
        # Check config file
        config_file = '/home/ubuntu/trading_system/config.py'
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                content = f.read()
                
            if 'default_secret_change_me' in content:
                self.add_vulnerability("⚠️ Default webhook secret found in config")
            else:
                self.add_check("✅ No default secrets found in config")
    
    def check_api_security(self):
        """Check API security measures"""
        print("🌐 Checking API security...")
        
        # Check if API keys are encrypted
        try:
            # Try to get a test API key
            self.security_manager.store_api_key("audit_test", "test_key", "test_secret")
            key, secret = self.security_manager.get_api_key("audit_test")
            
            if key == "test_key" and secret == "test_secret":
                self.add_check("✅ API key encryption/decryption working")
            else:
                self.add_vulnerability("⚠️ API key encryption/decryption failed")
                
        except Exception as e:
            self.add_vulnerability(f"⚠️ API key system error: {e}")
        
        # Check webhook signature validation
        try:
            payload = '{"test": "data"}'
            secret = "test_secret"
            signature = self.security_manager.generate_webhook_signature(payload, secret)
            is_valid = self.security_manager.validate_webhook_signature(payload, signature, secret)
            
            if is_valid:
                self.add_check("✅ Webhook signature validation working")
            else:
                self.add_vulnerability("⚠️ Webhook signature validation failed")
                
        except Exception as e:
            self.add_vulnerability(f"⚠️ Webhook signature system error: {e}")
    
    def check_encryption_security(self):
        """Check encryption implementation"""
        print("🔐 Checking encryption security...")
        
        try:
            # Test encryption strength
            test_data = "sensitive_test_data_12345"
            
            # Encrypt same data multiple times
            encrypted1 = self.security_manager.encrypt_data(test_data)
            encrypted2 = self.security_manager.encrypt_data(test_data)
            
            if encrypted1 != encrypted2:
                self.add_check("✅ Encryption uses proper randomization")
            else:
                self.add_vulnerability("⚠️ Encryption may not use proper randomization")
            
            # Test decryption
            decrypted = self.security_manager.decrypt_data(encrypted1)
            if decrypted == test_data:
                self.add_check("✅ Encryption/decryption integrity verified")
            else:
                self.add_vulnerability("⚠️ Encryption/decryption integrity failed")
                
        except Exception as e:
            self.add_vulnerability(f"⚠️ Encryption system error: {e}")
    
    def check_network_security(self):
        """Check network security configuration"""
        print("🌍 Checking network security...")
        
        # Check for open ports
        try:
            result = subprocess.run(['netstat', '-tuln'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                open_ports = []
                
                for line in lines:
                    if ':5000' in line or ':5173' in line or ':5174' in line:
                        open_ports.append(line.strip())
                
                if open_ports:
                    self.add_check(f"ℹ️ Found {len(open_ports)} development ports open")
                else:
                    self.add_check("✅ No unexpected ports found")
                    
        except Exception as e:
            self.add_check(f"ℹ️ Network scan skipped: {e}")
    
    def check_input_validation(self):
        """Check input validation and sanitization"""
        print("🧹 Checking input validation...")
        
        dangerous_inputs = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "../../../etc/passwd",
            "\x00\x01\x02",
            "A" * 10000
        ]
        
        all_safe = True
        for dangerous_input in dangerous_inputs:
            try:
                sanitized = self.security_manager.sanitize_input(dangerous_input)
                
                # Check if dangerous characters are removed
                if any(char in sanitized for char in ['<', '>', '"', "'", '\x00']):
                    all_safe = False
                    self.add_vulnerability(f"⚠️ Input sanitization failed for: {dangerous_input[:20]}...")
                    
            except Exception as e:
                all_safe = False
                self.add_vulnerability(f"⚠️ Input sanitization error: {e}")
        
        if all_safe:
            self.add_check("✅ Input sanitization working correctly")
    
    def check_auth_security(self):
        """Check authentication and authorization"""
        print("🔑 Checking authentication security...")
        
        # Check session management
        try:
            session_manager = self.security_manager.session_manager
            
            # Test session creation
            session_id = session_manager.create_session("test_user", "127.0.0.1", "test_agent")
            
            if session_id and len(session_id) > 20:
                self.add_check("✅ Session ID generation working")
                
                # Test session validation
                is_valid = session_manager.validate_session(session_id, "127.0.0.1")
                if is_valid:
                    self.add_check("✅ Session validation working")
                else:
                    self.add_vulnerability("⚠️ Session validation failed")
                    
            else:
                self.add_vulnerability("⚠️ Session ID generation failed")
                
        except Exception as e:
            self.add_vulnerability(f"⚠️ Session management error: {e}")
    
    def check_logging_security(self):
        """Check logging and monitoring"""
        print("📝 Checking logging security...")
        
        log_files = [
            '/home/ubuntu/trading_system/security.log',
            '/home/ubuntu/trading_system/trading_system.log'
        ]
        
        for log_file in log_files:
            if os.path.exists(log_file):
                stat_info = os.stat(log_file)
                permissions = oct(stat_info.st_mode)[-3:]
                
                if permissions in ['644', '640', '600']:
                    self.add_check(f"✅ Log file {os.path.basename(log_file)} has secure permissions")
                else:
                    self.add_vulnerability(f"⚠️ Log file {os.path.basename(log_file)} permissions: {permissions}")
            else:
                self.add_check(f"ℹ️ Log file {os.path.basename(log_file)} not found")
        
        # Test security event logging
        try:
            self.security_manager.log_security_event(
                "audit_test",
                "INFO",
                "Security audit test event",
                "127.0.0.1",
                "audit_tool"
            )
            
            events = self.security_manager.get_security_events(hours=1)
            if events:
                self.add_check("✅ Security event logging working")
            else:
                self.add_vulnerability("⚠️ Security event logging failed")
                
        except Exception as e:
            self.add_vulnerability(f"⚠️ Security logging error: {e}")
    
    def calculate_security_score(self):
        """Calculate overall security score"""
        total_checks = len(self.audit_results['checks'])
        vulnerabilities = len(self.audit_results['vulnerabilities'])
        
        if total_checks > 0:
            score = max(0, ((total_checks - vulnerabilities) / total_checks) * 100)
            self.audit_results['score'] = round(score, 1)
        else:
            self.audit_results['score'] = 0
        
        # Add recommendations based on vulnerabilities
        if vulnerabilities == 0:
            self.audit_results['recommendations'].append("✅ Excellent security posture!")
        elif vulnerabilities <= 2:
            self.audit_results['recommendations'].append("🟡 Good security with minor issues to address")
        elif vulnerabilities <= 5:
            self.audit_results['recommendations'].append("🟠 Moderate security risks - address vulnerabilities soon")
        else:
            self.audit_results['recommendations'].append("🔴 High security risk - immediate action required")
        
        # Specific recommendations
        if any("default" in vuln for vuln in self.audit_results['vulnerabilities']):
            self.audit_results['recommendations'].append("• Change all default passwords and secrets")
        
        if any("permission" in vuln for vuln in self.audit_results['vulnerabilities']):
            self.audit_results['recommendations'].append("• Fix file permissions for sensitive files")
        
        if any("hardcoded" in vuln for vuln in self.audit_results['vulnerabilities']):
            self.audit_results['recommendations'].append("• Remove hardcoded secrets from code")
    
    def add_check(self, message: str):
        """Add a security check result"""
        self.audit_results['checks'].append(message)
        print(f"  {message}")
    
    def add_vulnerability(self, message: str):
        """Add a security vulnerability"""
        self.audit_results['vulnerabilities'].append(message)
        print(f"  {message}")
    
    def generate_report(self) -> str:
        """Generate detailed security report"""
        report = f"""
# Trading System Security Audit Report

**Audit Date:** {self.audit_results['timestamp']}
**Security Score:** {self.audit_results['score']}/100

## Summary
- **Total Checks:** {len(self.audit_results['checks'])}
- **Vulnerabilities Found:** {len(self.audit_results['vulnerabilities'])}
- **Overall Status:** {'PASS' if self.audit_results['score'] >= 80 else 'NEEDS ATTENTION'}

## Security Checks Passed
"""
        
        for check in self.audit_results['checks']:
            report += f"- {check}\n"
        
        if self.audit_results['vulnerabilities']:
            report += "\n## Vulnerabilities Found\n"
            for vuln in self.audit_results['vulnerabilities']:
                report += f"- {vuln}\n"
        
        if self.audit_results['recommendations']:
            report += "\n## Recommendations\n"
            for rec in self.audit_results['recommendations']:
                report += f"- {rec}\n"
        
        report += f"""
## Security Checklist
- [ ] All default passwords changed
- [ ] File permissions properly configured
- [ ] API keys encrypted and stored securely
- [ ] Input validation implemented
- [ ] Logging and monitoring active
- [ ] Network security configured
- [ ] Regular security audits scheduled

---
*Generated by Trading System Security Auditor*
"""
        
        return report


def main():
    """Run security audit"""
    auditor = SecurityAuditor()
    results = auditor.run_full_audit()
    
    print("\n" + "=" * 50)
    print("SECURITY AUDIT SUMMARY")
    print("=" * 50)
    print(f"Security Score: {results['score']}/100")
    print(f"Checks Passed: {len(results['checks'])}")
    print(f"Vulnerabilities: {len(results['vulnerabilities'])}")
    
    if results['score'] >= 90:
        print("🟢 EXCELLENT SECURITY")
    elif results['score'] >= 80:
        print("🟡 GOOD SECURITY")
    elif results['score'] >= 60:
        print("🟠 MODERATE SECURITY")
    else:
        print("🔴 POOR SECURITY")
    
    # Save report
    report = auditor.generate_report()
    report_file = f"/home/ubuntu/trading_system/security_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"\nDetailed report saved to: {report_file}")
    
    return results


if __name__ == "__main__":
    main()

