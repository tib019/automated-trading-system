"""
Security Manager for Trading System
Handles encryption, API key management, authentication, and security monitoring
"""

import os
import json
import hashlib
import hmac
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import sqlite3
import logging
from functools import wraps
import ipaddress

class SecurityManager:
    """Comprehensive security management for the trading system"""
    
    def __init__(self, config_path: str = '/home/ubuntu/trading_system/security_config.json'):
        self.config_path = config_path
        self.db_path = '/home/ubuntu/trading_system/security.db'
        self.logger = self._setup_logging()
        self._init_database()
        self._load_or_create_master_key()
        self.rate_limiter = RateLimiter()
        self.session_manager = SessionManager()
        
    def _setup_logging(self) -> logging.Logger:
        """Setup security-specific logging"""
        logger = logging.getLogger('security')
        logger.setLevel(logging.INFO)
        
        # Create file handler for security logs
        handler = logging.FileHandler('/home/ubuntu/trading_system/security.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def _init_database(self):
        """Initialize security database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # API Keys table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT UNIQUE NOT NULL,
                encrypted_key TEXT NOT NULL,
                encrypted_secret TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Security events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                source_ip TEXT,
                user_agent TEXT,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Rate limiting table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rate_limits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                request_count INTEGER DEFAULT 1,
                window_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(ip_address, endpoint)
            )
        ''')
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT,
                ip_address TEXT,
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_or_create_master_key(self):
        """Load or create master encryption key"""
        key_file = '/home/ubuntu/trading_system/.master_key'
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                key_data = f.read()
                # Extract key from salt+key format
                if len(key_data) > 16:
                    self.master_key = key_data[16:]  # Skip salt
                else:
                    self.master_key = key_data
        else:
            # Generate new master key
            password = os.environ.get('TRADING_MASTER_PASSWORD', 'default_password_change_me')
            salt = os.urandom(16)
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            
            # Save salt and key
            with open(key_file, 'wb') as f:
                f.write(salt + key)
            
            self.master_key = key
            
            # Set restrictive permissions
            os.chmod(key_file, 0o600)
            
            self.logger.info("Master encryption key created")
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        try:
            fernet = Fernet(self.master_key)
            encrypted_data = fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            self.logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        try:
            fernet = Fernet(self.master_key)
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = fernet.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            self.logger.error(f"Decryption failed: {e}")
            raise
    
    def store_api_key(self, service_name: str, api_key: str, api_secret: str = None):
        """Securely store API keys"""
        try:
            encrypted_key = self.encrypt_data(api_key)
            encrypted_secret = self.encrypt_data(api_secret) if api_secret else None
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO api_keys 
                (service_name, encrypted_key, encrypted_secret)
                VALUES (?, ?, ?)
            ''', (service_name, encrypted_key, encrypted_secret))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"API key stored for service: {service_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to store API key for {service_name}: {e}")
            raise
    
    def get_api_key(self, service_name: str) -> Tuple[str, Optional[str]]:
        """Retrieve and decrypt API keys"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT encrypted_key, encrypted_secret FROM api_keys 
                WHERE service_name = ? AND is_active = 1
            ''', (service_name,))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                raise ValueError(f"API key not found for service: {service_name}")
            
            api_key = self.decrypt_data(result[0])
            api_secret = self.decrypt_data(result[1]) if result[1] else None
            
            # Update last used timestamp
            self._update_api_key_usage(service_name)
            
            return api_key, api_secret
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve API key for {service_name}: {e}")
            raise
    
    def _update_api_key_usage(self, service_name: str):
        """Update last used timestamp for API key"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE api_keys SET last_used = CURRENT_TIMESTAMP 
            WHERE service_name = ?
        ''', (service_name,))
        
        conn.commit()
        conn.close()
    
    def generate_webhook_signature(self, payload: str, secret: str) -> str:
        """Generate HMAC signature for webhook validation"""
        return hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def validate_webhook_signature(self, payload: str, signature: str, secret: str) -> bool:
        """Validate webhook signature"""
        expected_signature = self.generate_webhook_signature(payload, secret)
        return hmac.compare_digest(signature, expected_signature)
    
    def log_security_event(self, event_type: str, severity: str, details: str, 
                          source_ip: str = None, user_agent: str = None):
        """Log security events"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO security_events 
                (event_type, severity, source_ip, user_agent, details)
                VALUES (?, ?, ?, ?, ?)
            ''', (event_type, severity, source_ip, user_agent, details))
            
            conn.commit()
            conn.close()
            
            self.logger.warning(f"Security event: {event_type} - {severity} - {details}")
            
        except Exception as e:
            self.logger.error(f"Failed to log security event: {e}")
    
    def get_security_events(self, hours: int = 24) -> List[Dict]:
        """Get recent security events"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT event_type, severity, source_ip, user_agent, details, timestamp
            FROM security_events 
            WHERE timestamp > datetime('now', '-{} hours')
            ORDER BY timestamp DESC
        '''.format(hours))
        
        events = []
        for row in cursor.fetchall():
            events.append({
                'event_type': row[0],
                'severity': row[1],
                'source_ip': row[2],
                'user_agent': row[3],
                'details': row[4],
                'timestamp': row[5]
            })
        
        conn.close()
        return events
    
    def validate_ip_whitelist(self, ip_address: str, whitelist: List[str]) -> bool:
        """Validate IP address against whitelist"""
        if not whitelist:  # Empty whitelist allows all IPs
            return True
        
        try:
            client_ip = ipaddress.ip_address(ip_address)
            
            for allowed_ip in whitelist:
                if '/' in allowed_ip:  # CIDR notation
                    if client_ip in ipaddress.ip_network(allowed_ip):
                        return True
                else:  # Single IP
                    if client_ip == ipaddress.ip_address(allowed_ip):
                        return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"IP validation error: {e}")
            return False
    
    def sanitize_input(self, data: str, max_length: int = 1000) -> str:
        """Sanitize user input"""
        if not isinstance(data, str):
            data = str(data)
        
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', '\x00', '\n', '\r']
        for char in dangerous_chars:
            data = data.replace(char, '')
        
        # Limit length
        if len(data) > max_length:
            data = data[:max_length]
        
        return data.strip()


class RateLimiter:
    """Rate limiting for API endpoints"""
    
    def __init__(self):
        self.db_path = '/home/ubuntu/trading_system/security.db'
        self.limits = {
            'webhook': {'requests': 60, 'window': 60},  # 60 requests per minute
            'api': {'requests': 100, 'window': 60},     # 100 requests per minute
            'auth': {'requests': 5, 'window': 300}      # 5 auth attempts per 5 minutes
        }
    
    def is_rate_limited(self, ip_address: str, endpoint: str) -> bool:
        """Check if IP is rate limited for endpoint"""
        limit_config = self.limits.get(endpoint, self.limits['api'])
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clean old entries
        cursor.execute('''
            DELETE FROM rate_limits 
            WHERE window_start < datetime('now', '-{} seconds')
        '''.format(limit_config['window']))
        
        # Check current rate
        cursor.execute('''
            SELECT request_count FROM rate_limits 
            WHERE ip_address = ? AND endpoint = ?
            AND window_start > datetime('now', '-{} seconds')
        '''.format(limit_config['window']), (ip_address, endpoint))
        
        result = cursor.fetchone()
        
        if result and result[0] >= limit_config['requests']:
            conn.close()
            return True
        
        # Update or insert rate limit entry
        cursor.execute('''
            INSERT OR REPLACE INTO rate_limits 
            (ip_address, endpoint, request_count, window_start)
            VALUES (?, ?, COALESCE((SELECT request_count FROM rate_limits 
                                   WHERE ip_address = ? AND endpoint = ?), 0) + 1, 
                    COALESCE((SELECT window_start FROM rate_limits 
                             WHERE ip_address = ? AND endpoint = ?), CURRENT_TIMESTAMP))
        ''', (ip_address, endpoint, ip_address, endpoint, ip_address, endpoint))
        
        conn.commit()
        conn.close()
        
        return False


class SessionManager:
    """Manage user sessions"""
    
    def __init__(self):
        self.db_path = '/home/ubuntu/trading_system/security.db'
        self.session_timeout = 3600  # 1 hour
    
    def create_session(self, user_id: str, ip_address: str, user_agent: str) -> str:
        """Create new session"""
        session_id = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(seconds=self.session_timeout)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sessions 
            (session_id, user_id, ip_address, user_agent, expires_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (session_id, user_id, ip_address, user_agent, expires_at))
        
        conn.commit()
        conn.close()
        
        return session_id
    
    def validate_session(self, session_id: str, ip_address: str) -> bool:
        """Validate session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id FROM sessions 
            WHERE session_id = ? AND ip_address = ? 
            AND expires_at > CURRENT_TIMESTAMP AND is_active = 1
        ''', (session_id, ip_address))
        
        result = cursor.fetchone()
        conn.close()
        
        return result is not None
    
    def invalidate_session(self, session_id: str):
        """Invalidate session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE sessions SET is_active = 0 
            WHERE session_id = ?
        ''', (session_id,))
        
        conn.commit()
        conn.close()


def require_auth(f):
    """Decorator for authentication requirement"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # This would be implemented with Flask request context
        # For now, it's a placeholder
        return f(*args, **kwargs)
    return decorated_function


def require_rate_limit(endpoint: str):
    """Decorator for rate limiting"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # This would be implemented with Flask request context
            # For now, it's a placeholder
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# Security configuration
SECURITY_CONFIG = {
    'webhook_secret': os.environ.get('WEBHOOK_SECRET', 'default_secret_change_me'),
    'allowed_ips': [],  # Empty list allows all IPs
    'require_signature': True,
    'max_request_size': 1024 * 1024,  # 1MB
    'session_timeout': 3600,  # 1 hour
    'rate_limits': {
        'webhook': {'requests': 60, 'window': 60},
        'api': {'requests': 100, 'window': 60},
        'auth': {'requests': 5, 'window': 300}
    }
}


if __name__ == "__main__":
    # Test security manager
    security = SecurityManager()
    
    # Test encryption
    test_data = "sensitive_api_key_12345"
    encrypted = security.encrypt_data(test_data)
    decrypted = security.decrypt_data(encrypted)
    
    print(f"Original: {test_data}")
    print(f"Encrypted: {encrypted}")
    print(f"Decrypted: {decrypted}")
    print(f"Match: {test_data == decrypted}")
    
    # Test API key storage
    security.store_api_key("test_service", "test_key_123", "test_secret_456")
    key, secret = security.get_api_key("test_service")
    print(f"Retrieved key: {key}")
    print(f"Retrieved secret: {secret}")
    
    # Test webhook signature
    payload = '{"test": "data"}'
    secret_key = "webhook_secret"
    signature = security.generate_webhook_signature(payload, secret_key)
    is_valid = security.validate_webhook_signature(payload, signature, secret_key)
    
    print(f"Webhook signature: {signature}")
    print(f"Signature valid: {is_valid}")
    
    # Test security event logging
    security.log_security_event(
        "test_event", 
        "INFO", 
        "Security manager test completed",
        "127.0.0.1",
        "test_agent"
    )
    
    print("Security manager test completed successfully!")

