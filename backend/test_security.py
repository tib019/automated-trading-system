"""
Security-focused Test Suite for Trading System
Tests security manager and related security features
"""

import unittest
import tempfile
import os
import json
import sqlite3
import time
import sys

# Add the trading system to path
sys.path.append('/home/ubuntu/trading_system')

from security_manager import SecurityManager, RateLimiter, SessionManager


class TestSecurityManager(unittest.TestCase):
    """Test security manager functionality"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.security_config = os.path.join(self.temp_dir, 'security_config.json')
        self.security = SecurityManager(self.security_config)
    
    def tearDown(self):
        # Clean up temporary files
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_encryption_decryption(self):
        """Test data encryption and decryption"""
        test_data = "sensitive_api_key_12345"
        
        # Test encryption
        encrypted = self.security.encrypt_data(test_data)
        self.assertNotEqual(encrypted, test_data)
        self.assertIsInstance(encrypted, str)
        
        # Test decryption
        decrypted = self.security.decrypt_data(encrypted)
        self.assertEqual(decrypted, test_data)
        
        print(f"✅ Encryption/Decryption test passed")
    
    def test_api_key_storage(self):
        """Test API key storage and retrieval"""
        service_name = "test_service"
        api_key = "test_key_123"
        api_secret = "test_secret_456"
        
        # Store API key
        self.security.store_api_key(service_name, api_key, api_secret)
        
        # Retrieve API key
        retrieved_key, retrieved_secret = self.security.get_api_key(service_name)
        
        self.assertEqual(retrieved_key, api_key)
        self.assertEqual(retrieved_secret, api_secret)
        
        print(f"✅ API Key storage test passed")
    
    def test_webhook_signature(self):
        """Test webhook signature generation and validation"""
        payload = '{"test": "data"}'
        secret = "webhook_secret"
        
        # Generate signature
        signature = self.security.generate_webhook_signature(payload, secret)
        self.assertIsInstance(signature, str)
        self.assertEqual(len(signature), 64)  # SHA256 hex length
        
        # Validate signature
        is_valid = self.security.validate_webhook_signature(payload, signature, secret)
        self.assertTrue(is_valid)
        
        # Test invalid signature
        invalid_signature = "invalid_signature"
        is_invalid = self.security.validate_webhook_signature(payload, invalid_signature, secret)
        self.assertFalse(is_invalid)
        
        print(f"✅ Webhook signature test passed")
    
    def test_input_sanitization(self):
        """Test input sanitization"""
        dangerous_input = "<script>alert('xss')</script>"
        sanitized = self.security.sanitize_input(dangerous_input)
        self.assertNotIn('<', sanitized)
        self.assertNotIn('>', sanitized)
        
        # Test length limiting
        long_input = "a" * 2000
        sanitized_long = self.security.sanitize_input(long_input, max_length=100)
        self.assertEqual(len(sanitized_long), 100)
        
        print(f"✅ Input sanitization test passed")
    
    def test_security_event_logging(self):
        """Test security event logging"""
        self.security.log_security_event(
            "test_event", 
            "INFO", 
            "Test security event",
            "127.0.0.1",
            "test_agent"
        )
        
        events = self.security.get_security_events(hours=1)
        self.assertGreater(len(events), 0)
        self.assertEqual(events[0]['event_type'], 'test_event')
        
        print(f"✅ Security event logging test passed")


class TestRateLimiter(unittest.TestCase):
    """Test rate limiting functionality"""
    
    def setUp(self):
        self.rate_limiter = RateLimiter()
        # Use test database
        self.rate_limiter.db_path = ':memory:'
        
        # Initialize test database
        conn = sqlite3.connect(self.rate_limiter.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE rate_limits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                request_count INTEGER DEFAULT 1,
                window_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(ip_address, endpoint)
            )
        ''')
        conn.commit()
        conn.close()
    
    def test_rate_limiting(self):
        """Test rate limiting logic"""
        ip_address = "127.0.0.1"
        endpoint = "test"
        
        # Set low limit for testing
        self.rate_limiter.limits['test'] = {'requests': 2, 'window': 60}
        
        # First request should pass
        is_limited = self.rate_limiter.is_rate_limited(ip_address, endpoint)
        self.assertFalse(is_limited)
        
        # Second request should pass
        is_limited = self.rate_limiter.is_rate_limited(ip_address, endpoint)
        self.assertFalse(is_limited)
        
        # Third request should be limited
        is_limited = self.rate_limiter.is_rate_limited(ip_address, endpoint)
        self.assertTrue(is_limited)
        
        print(f"✅ Rate limiting test passed")


class TestSessionManager(unittest.TestCase):
    """Test session management functionality"""
    
    def setUp(self):
        self.session_manager = SessionManager()
        # Use test database
        self.session_manager.db_path = ':memory:'
        
        # Initialize test database
        conn = sqlite3.connect(self.session_manager.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE sessions (
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
    
    def test_session_creation_and_validation(self):
        """Test session creation and validation"""
        user_id = "test_user"
        ip_address = "127.0.0.1"
        user_agent = "test_agent"
        
        # Create session
        session_id = self.session_manager.create_session(user_id, ip_address, user_agent)
        self.assertIsInstance(session_id, str)
        self.assertGreater(len(session_id), 20)
        
        # Validate session
        is_valid = self.session_manager.validate_session(session_id, ip_address)
        self.assertTrue(is_valid)
        
        # Test invalid session
        is_invalid = self.session_manager.validate_session("invalid_session", ip_address)
        self.assertFalse(is_invalid)
        
        # Invalidate session
        self.session_manager.invalidate_session(session_id)
        is_valid_after_invalidation = self.session_manager.validate_session(session_id, ip_address)
        self.assertFalse(is_valid_after_invalidation)
        
        print(f"✅ Session management test passed")


def run_performance_tests():
    """Run performance tests"""
    print("\n" + "="*50)
    print("PERFORMANCE TESTS")
    print("="*50)
    
    # Test encryption performance
    security = SecurityManager()
    test_data = "test_api_key_12345" * 100  # Larger data
    
    start_time = time.time()
    for _ in range(100):
        encrypted = security.encrypt_data(test_data)
        decrypted = security.decrypt_data(encrypted)
    end_time = time.time()
    
    print(f"✅ Encryption/Decryption (100 iterations): {end_time - start_time:.4f} seconds")
    
    # Test signature generation performance
    start_time = time.time()
    for _ in range(1000):
        payload = f'{{"test": "data_{_}"}}'
        signature = security.generate_webhook_signature(payload, "secret")
    end_time = time.time()
    
    print(f"✅ Webhook Signature Generation (1000 iterations): {end_time - start_time:.4f} seconds")


def run_stress_tests():
    """Run stress tests"""
    print("\n" + "="*50)
    print("STRESS TESTS")
    print("="*50)
    
    # Test rate limiter under load
    rate_limiter = RateLimiter()
    rate_limiter.db_path = ':memory:'
    
    # Initialize test database
    conn = sqlite3.connect(rate_limiter.db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE rate_limits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT NOT NULL,
            endpoint TEXT NOT NULL,
            request_count INTEGER DEFAULT 1,
            window_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(ip_address, endpoint)
        )
    ''')
    conn.commit()
    conn.close()
    
    # Simulate high load
    start_time = time.time()
    for i in range(1000):
        ip = f"192.168.1.{i % 255}"
        is_limited = rate_limiter.is_rate_limited(ip, "api")
    end_time = time.time()
    
    print(f"✅ Rate Limiter (1000 requests): {end_time - start_time:.4f} seconds")
    
    # Test database performance under load
    security = SecurityManager()
    
    start_time = time.time()
    for i in range(100):
        security.log_security_event(
            f"test_event_{i}",
            "INFO",
            f"Test event {i}",
            f"192.168.1.{i % 255}",
            "test_agent"
        )
    end_time = time.time()
    
    print(f"✅ Security Event Logging (100 events): {end_time - start_time:.4f} seconds")


def run_security_audit():
    """Run security audit checks"""
    print("\n" + "="*50)
    print("SECURITY AUDIT")
    print("="*50)
    
    security = SecurityManager()
    
    # Check master key file permissions
    key_file = '/home/ubuntu/trading_system/.master_key'
    if os.path.exists(key_file):
        stat_info = os.stat(key_file)
        permissions = oct(stat_info.st_mode)[-3:]
        if permissions == '600':
            print("✅ Master key file has correct permissions (600)")
        else:
            print(f"⚠️ Master key file permissions: {permissions} (should be 600)")
    
    # Check database file permissions
    db_file = '/home/ubuntu/trading_system/security.db'
    if os.path.exists(db_file):
        stat_info = os.stat(db_file)
        permissions = oct(stat_info.st_mode)[-3:]
        print(f"✅ Security database permissions: {permissions}")
    
    # Test input validation
    dangerous_inputs = [
        "<script>alert('xss')</script>",
        "'; DROP TABLE users; --",
        "../../../etc/passwd",
        "\x00\x01\x02",
        "A" * 10000
    ]
    
    all_safe = True
    for dangerous_input in dangerous_inputs:
        sanitized = security.sanitize_input(dangerous_input)
        if any(char in sanitized for char in ['<', '>', '"', "'", '\x00']):
            all_safe = False
            print(f"⚠️ Input sanitization failed for: {dangerous_input[:50]}...")
    
    if all_safe:
        print("✅ Input sanitization working correctly")
    
    # Test encryption strength
    test_data = "sensitive_data_12345"
    encrypted1 = security.encrypt_data(test_data)
    encrypted2 = security.encrypt_data(test_data)
    
    if encrypted1 != encrypted2:
        print("✅ Encryption uses proper randomization (different outputs for same input)")
    else:
        print("⚠️ Encryption may not be using proper randomization")
    
    print("✅ Security audit completed")


if __name__ == "__main__":
    print("="*60)
    print("TRADING SYSTEM SECURITY TEST SUITE")
    print("="*60)
    
    # Run unit tests
    print("\nRunning Security Unit Tests...")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSecurityManager))
    suite.addTests(loader.loadTestsFromTestCase(TestRateLimiter))
    suite.addTests(loader.loadTestsFromTestCase(TestSessionManager))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Run performance tests
    run_performance_tests()
    
    # Run stress tests
    run_stress_tests()
    
    # Run security audit
    run_security_audit()
    
    print("\n" + "="*60)
    print("SECURITY TESTS COMPLETED")
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
    print("="*60)

