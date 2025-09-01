"""
Comprehensive Test Suite for Trading System
Tests all critical components and security features
"""

import unittest
import tempfile
import os
import json
import sqlite3
import time
from unittest.mock import Mock, patch, MagicMock
import sys

# Add the trading system to path
sys.path.append('/home/ubuntu/trading_system')

from security_manager import SecurityManager, RateLimiter, SessionManager
from config import TradingConfig
from data_collector_v2 import DataCollector
from sentiment_analyzer import SentimentAnalyzer
from signal_generator import SignalGenerator
from risk_manager import RiskManager
from order_manager import OrderManager


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


class TestDataCollector(unittest.TestCase):
    """Test data collection functionality"""
    
    def setUp(self):
        self.config = TradingConfig()
        self.collector = DataCollector(self.config)
    
    @patch('requests.get')
    def test_yahoo_finance_data(self, mock_get):
        """Test Yahoo Finance data collection"""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            'chart': {
                'result': [{
                    'meta': {'regularMarketPrice': 50000},
                    'timestamp': [1693526400],
                    'indicators': {
                        'quote': [{
                            'open': [49000],
                            'high': [51000],
                            'low': [48000],
                            'close': [50000],
                            'volume': [1000000]
                        }]
                    }
                }]
            }
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Test data collection
        data = self.collector.collect_yahoo_finance_data('BTC-USD')
        self.assertIsNotNone(data)
        self.assertIn('price', data)
        self.assertEqual(data['price'], 50000)
    
    def test_symbol_detection(self):
        """Test symbol detection in text"""
        text = "I think $BTC will go to the moon! Tesla stock is also looking good."
        symbols = self.collector.detect_symbols(text)
        
        self.assertIn('BTC', [s['symbol'] for s in symbols])
        self.assertIn('TSLA', [s['symbol'] for s in symbols])


class TestSentimentAnalyzer(unittest.TestCase):
    """Test sentiment analysis functionality"""
    
    def setUp(self):
        self.analyzer = SentimentAnalyzer()
    
    def test_sentiment_analysis(self):
        """Test sentiment analysis"""
        # Positive sentiment
        positive_text = "Bitcoin is going to the moon! 🚀 Great investment!"
        positive_result = self.analyzer.analyze_sentiment(positive_text)
        self.assertGreater(positive_result['sentiment_score'], 0)
        
        # Negative sentiment
        negative_text = "Bitcoin is crashing! Sell everything! 💀"
        negative_result = self.analyzer.analyze_sentiment(negative_text)
        self.assertLess(negative_result['sentiment_score'], 0)
        
        # Neutral sentiment
        neutral_text = "Bitcoin price is $50000"
        neutral_result = self.analyzer.analyze_sentiment(neutral_text)
        self.assertAlmostEqual(neutral_result['sentiment_score'], 0, delta=0.3)
    
    def test_confidence_calculation(self):
        """Test confidence score calculation"""
        text = "Bitcoin is absolutely amazing! Best investment ever! 🚀🚀🚀"
        result = self.analyzer.analyze_sentiment(text)
        
        self.assertGreater(result['confidence'], 0.5)
        self.assertLessEqual(result['confidence'], 1.0)


class TestSignalGenerator(unittest.TestCase):
    """Test signal generation functionality"""
    
    def setUp(self):
        self.generator = SignalGenerator()
    
    def test_technical_indicators(self):
        """Test technical indicator calculations"""
        # Mock price data
        prices = [100, 102, 101, 103, 105, 104, 106, 108, 107, 109]
        
        # Test SMA
        sma = self.generator.calculate_sma(prices, period=5)
        self.assertIsInstance(sma, float)
        self.assertGreater(sma, 0)
        
        # Test EMA
        ema = self.generator.calculate_ema(prices, period=5)
        self.assertIsInstance(ema, float)
        self.assertGreater(ema, 0)
        
        # Test RSI
        rsi = self.generator.calculate_rsi(prices, period=5)
        self.assertIsInstance(rsi, float)
        self.assertGreaterEqual(rsi, 0)
        self.assertLessEqual(rsi, 100)
    
    def test_signal_generation(self):
        """Test signal generation"""
        # Mock market data
        market_data = {
            'symbol': 'BTC-USD',
            'price': 50000,
            'volume': 1000000,
            'price_history': [48000, 49000, 50000, 51000, 50000]
        }
        
        # Mock sentiment data
        sentiment_data = {
            'sentiment_score': 0.5,
            'confidence': 0.8
        }
        
        signal = self.generator.generate_signal(market_data, sentiment_data)
        
        self.assertIn('action', signal)
        self.assertIn('strength', signal)
        self.assertIn('confidence', signal)
        self.assertIn(signal['action'], ['BUY', 'SELL', 'HOLD'])
        self.assertIn(signal['strength'], ['WEAK', 'MODERATE', 'STRONG'])


class TestRiskManager(unittest.TestCase):
    """Test risk management functionality"""
    
    def setUp(self):
        self.risk_manager = RiskManager()
    
    def test_position_sizing(self):
        """Test position sizing calculation"""
        account_balance = 10000
        risk_per_trade = 0.02  # 2%
        entry_price = 50000
        stop_loss_price = 47500
        
        position_size = self.risk_manager.calculate_position_size(
            account_balance, risk_per_trade, entry_price, stop_loss_price
        )
        
        self.assertGreater(position_size, 0)
        self.assertLess(position_size, account_balance)
    
    def test_risk_validation(self):
        """Test risk validation"""
        # Test valid position
        valid_position = {
            'symbol': 'BTC-USD',
            'side': 'BUY',
            'quantity': 0.1,
            'price': 50000
        }
        
        is_valid = self.risk_manager.validate_position(valid_position)
        self.assertTrue(is_valid)
        
        # Test oversized position
        oversized_position = {
            'symbol': 'BTC-USD',
            'side': 'BUY',
            'quantity': 10,  # Too large
            'price': 50000
        }
        
        is_valid = self.risk_manager.validate_position(oversized_position)
        self.assertFalse(is_valid)
    
    def test_kill_switch(self):
        """Test kill switch functionality"""
        # Simulate large losses
        self.risk_manager.portfolio_value = 8000  # 20% loss from 10000
        
        should_trigger = self.risk_manager.should_trigger_kill_switch()
        self.assertTrue(should_trigger)


class TestOrderManager(unittest.TestCase):
    """Test order management functionality"""
    
    def setUp(self):
        self.order_manager = OrderManager()
    
    def test_order_creation(self):
        """Test order creation"""
        order_data = {
            'symbol': 'BTC-USD',
            'side': 'BUY',
            'quantity': 0.1,
            'price': 50000,
            'order_type': 'MARKET'
        }
        
        order = self.order_manager.create_order(order_data)
        
        self.assertIn('id', order)
        self.assertIn('status', order)
        self.assertEqual(order['symbol'], 'BTC-USD')
        self.assertEqual(order['side'], 'BUY')
    
    def test_order_validation(self):
        """Test order validation"""
        # Valid order
        valid_order = {
            'symbol': 'BTC-USD',
            'side': 'BUY',
            'quantity': 0.1,
            'price': 50000,
            'order_type': 'LIMIT'
        }
        
        is_valid = self.order_manager.validate_order(valid_order)
        self.assertTrue(is_valid)
        
        # Invalid order (missing required fields)
        invalid_order = {
            'symbol': 'BTC-USD',
            'side': 'BUY'
            # Missing quantity and price
        }
        
        is_valid = self.order_manager.validate_order(invalid_order)
        self.assertFalse(is_valid)


class TestIntegration(unittest.TestCase):
    """Integration tests for complete workflows"""
    
    def setUp(self):
        self.config = TradingConfig()
        self.security = SecurityManager()
        self.collector = DataCollector(self.config)
        self.analyzer = SentimentAnalyzer()
        self.generator = SignalGenerator()
        self.risk_manager = RiskManager()
        self.order_manager = OrderManager()
    
    def test_complete_trading_workflow(self):
        """Test complete trading workflow"""
        # 1. Collect market data (mocked)
        market_data = {
            'symbol': 'BTC-USD',
            'price': 50000,
            'volume': 1000000,
            'price_history': [48000, 49000, 50000, 51000, 50000]
        }
        
        # 2. Analyze sentiment (mocked)
        sentiment_data = {
            'sentiment_score': 0.5,
            'confidence': 0.8
        }
        
        # 3. Generate signal
        signal = self.generator.generate_signal(market_data, sentiment_data)
        self.assertIsNotNone(signal)
        
        # 4. Validate risk
        if signal['action'] in ['BUY', 'SELL']:
            position = {
                'symbol': signal['symbol'],
                'side': signal['action'],
                'quantity': 0.1,
                'price': market_data['price']
            }
            
            is_valid = self.risk_manager.validate_position(position)
            
            # 5. Create order if valid
            if is_valid:
                order = self.order_manager.create_order(position)
                self.assertIsNotNone(order)
                self.assertIn('id', order)
    
    def test_security_integration(self):
        """Test security integration with other components"""
        # Test API key storage and retrieval
        self.security.store_api_key("binance", "test_key", "test_secret")
        key, secret = self.security.get_api_key("binance")
        
        self.assertEqual(key, "test_key")
        self.assertEqual(secret, "test_secret")
        
        # Test webhook signature validation
        payload = '{"symbol": "BTC-USD", "action": "BUY"}'
        secret_key = "webhook_secret"
        signature = self.security.generate_webhook_signature(payload, secret_key)
        
        is_valid = self.security.validate_webhook_signature(payload, signature, secret_key)
        self.assertTrue(is_valid)


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
    
    print(f"Encryption/Decryption (100 iterations): {end_time - start_time:.4f} seconds")
    
    # Test signal generation performance
    generator = SignalGenerator()
    market_data = {
        'symbol': 'BTC-USD',
        'price': 50000,
        'volume': 1000000,
        'price_history': list(range(48000, 52000, 10))  # 400 data points
    }
    sentiment_data = {'sentiment_score': 0.5, 'confidence': 0.8}
    
    start_time = time.time()
    for _ in range(100):
        signal = generator.generate_signal(market_data, sentiment_data)
    end_time = time.time()
    
    print(f"Signal Generation (100 iterations): {end_time - start_time:.4f} seconds")


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
    
    print(f"Rate Limiter (1000 requests): {end_time - start_time:.4f} seconds")
    
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
    
    print(f"Security Event Logging (100 events): {end_time - start_time:.4f} seconds")


if __name__ == "__main__":
    print("="*60)
    print("TRADING SYSTEM COMPREHENSIVE TEST SUITE")
    print("="*60)
    
    # Run unit tests
    print("\nRunning Unit Tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run performance tests
    run_performance_tests()
    
    # Run stress tests
    run_stress_tests()
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETED")
    print("="*60)

