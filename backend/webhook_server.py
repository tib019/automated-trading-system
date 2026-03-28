#!/usr/bin/env python3
"""
Trading System - TradingView Webhook Server
Flask-basierter Webhook-Server für TradingView-Signale
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import logging
from datetime import datetime
from typing import Dict, Optional
import hashlib
import hmac

from order_manager import OrderManager, BrokerType
from signal_generator import TradingSignal, SignalType, SignalStrength
from config import get_config

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Erlaube Cross-Origin Requests

class WebhookServer:
    """TradingView Webhook Server"""
    
    def __init__(self):
        self.config = get_config()
        self.order_manager = OrderManager()
        self.webhook_secret = self.config.WEBHOOK_CONFIG.get('secret', 'default_secret')
        self.enabled_brokers = self.config.WEBHOOK_CONFIG.get('enabled_brokers', ['PAPER_TRADING'])
        
        # Verbinde mit Brokern
        self.order_manager.connect_brokers()
        
        # Webhook-Statistiken
        self.stats = {
            'total_webhooks': 0,
            'successful_orders': 0,
            'failed_orders': 0,
            'last_webhook': None
        }
    
    def verify_signature(self, payload: str, signature: str) -> bool:
        """Verifiziere Webhook-Signatur"""
        if not signature:
            return False
        
        expected_signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    
    def parse_tradingview_alert(self, alert_data: Dict) -> Optional[TradingSignal]:
        """Parse TradingView Alert zu TradingSignal"""
        try:
            # Standard TradingView Alert Format
            symbol = alert_data.get('ticker', alert_data.get('symbol', ''))
            action = alert_data.get('action', alert_data.get('side', '')).upper()
            price = float(alert_data.get('price', alert_data.get('close', 0)))
            
            # Signal-Type bestimmen
            if action in ['BUY', 'LONG']:
                signal_type = SignalType.BUY
            elif action in ['SELL', 'SHORT']:
                signal_type = SignalType.SELL
            else:
                logger.warning(f"Unknown action: {action}")
                return None
            
            # Signal-Stärke aus Alert ableiten
            strength_indicator = alert_data.get('strength', alert_data.get('confidence', 'MODERATE')).upper()
            if strength_indicator in ['STRONG', 'HIGH']:
                strength = SignalStrength.STRONG
            elif strength_indicator in ['WEAK', 'LOW']:
                strength = SignalStrength.WEAK
            else:
                strength = SignalStrength.MODERATE
            
            # Stop-Loss und Take-Profit
            stop_loss = float(alert_data.get('stop_loss', price * 0.95 if signal_type == SignalType.BUY else price * 1.05))
            take_profit = float(alert_data.get('take_profit', price * 1.10 if signal_type == SignalType.BUY else price * 0.90))
            
            # Position-Size
            position_size = float(alert_data.get('position_size', 2.0))
            
            # Erstelle TradingSignal
            signal = TradingSignal(
                symbol=symbol,
                timestamp=datetime.now(),
                signal_type=signal_type,
                strength=strength,
                entry_price=price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                confidence=float(alert_data.get('confidence_score', 0.75)),
                reasoning=alert_data.get('message', f"TradingView {action} signal"),
                sentiment_score=float(alert_data.get('sentiment', 0.0)),
                technical_score=float(alert_data.get('technical_score', 0.5)),
                volume_score=float(alert_data.get('volume_score', 0.0)),
                position_size_percent=position_size,
                risk_reward_ratio=abs(take_profit - price) / abs(price - stop_loss)
            )
            
            return signal
            
        except Exception as e:
            logger.error(f"Error parsing TradingView alert: {e}")
            return None
    
    def process_webhook(self, webhook_data: Dict) -> Dict:
        """Verarbeite eingehenden Webhook"""
        self.stats['total_webhooks'] += 1
        self.stats['last_webhook'] = datetime.now()
        
        try:
            # Parse Alert zu Signal
            signal = self.parse_tradingview_alert(webhook_data)
            
            if not signal:
                self.stats['failed_orders'] += 1
                return {
                    'success': False,
                    'error': 'Failed to parse alert data',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Führe Signal aus (standardmäßig Paper Trading)
            broker_type = BrokerType.PAPER_TRADING
            if 'broker' in webhook_data:
                try:
                    broker_type = BrokerType(webhook_data['broker'].upper())
                    if broker_type.value not in self.enabled_brokers:
                        broker_type = BrokerType.PAPER_TRADING
                except ValueError:
                    pass
            
            success, message = self.order_manager.execute_signal(signal, broker_type)
            
            if success:
                self.stats['successful_orders'] += 1
                return {
                    'success': True,
                    'message': message,
                    'signal': {
                        'symbol': signal.symbol,
                        'action': signal.signal_type.value,
                        'price': signal.entry_price,
                        'strength': signal.strength.value
                    },
                    'broker': broker_type.value,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                self.stats['failed_orders'] += 1
                return {
                    'success': False,
                    'error': message,
                    'signal': {
                        'symbol': signal.symbol,
                        'action': signal.signal_type.value,
                        'price': signal.entry_price
                    },
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            self.stats['failed_orders'] += 1
            logger.error(f"Error processing webhook: {e}")
            return {
                'success': False,
                'error': f'Processing error: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }

# Globale Webhook-Server-Instanz
webhook_server = WebhookServer()

@app.route('/', methods=['GET'])
def health_check():
    """Health Check Endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'TradingView Webhook Server',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'stats': webhook_server.stats
    })

@app.route('/webhook/tradingview', methods=['POST'])
def tradingview_webhook():
    """TradingView Webhook Endpoint"""
    try:
        # Hole Request-Daten
        payload = request.get_data(as_text=True)
        signature = request.headers.get('X-Signature', '')
        
        # Verifiziere Signatur (optional)
        if webhook_server.webhook_secret != 'default_secret':
            if not webhook_server.verify_signature(payload, signature):
                logger.warning("Invalid webhook signature")
                return jsonify({'error': 'Invalid signature'}), 401
        
        # Parse JSON
        try:
            webhook_data = json.loads(payload)
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid JSON'}), 400
        
        # Verarbeite Webhook
        result = webhook_server.process_webhook(webhook_data)
        
        # Log Ergebnis
        if result['success']:
            logger.info(f"Webhook processed successfully: {result['message']}")
        else:
            logger.error(f"Webhook processing failed: {result['error']}")
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        logger.error(f"Webhook endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/webhook/test', methods=['POST'])
def test_webhook():
    """Test Webhook Endpoint"""
    test_data = {
        'ticker': 'BTC-USD',
        'action': 'BUY',
        'price': 50000.00,
        'strength': 'MODERATE',
        'stop_loss': 48000.00,
        'take_profit': 55000.00,
        'position_size': 2.0,
        'message': 'Test webhook signal',
        'confidence_score': 0.8
    }
    
    result = webhook_server.process_webhook(test_data)
    return jsonify(result)

@app.route('/status', methods=['GET'])
def get_status():
    """Status Endpoint"""
    broker_status = webhook_server.order_manager.get_broker_status()
    order_history = webhook_server.order_manager.get_order_history(10)
    
    return jsonify({
        'webhook_stats': webhook_server.stats,
        'broker_status': broker_status,
        'recent_orders': [
            {
                'id': order.id,
                'symbol': order.symbol,
                'side': order.side.value,
                'quantity': order.quantity,
                'price': order.price,
                'status': order.status.value,
                'broker': order.broker.value,
                'created_at': order.created_at.isoformat()
            }
            for order in order_history
        ],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/orders', methods=['GET'])
def get_orders():
    """Order-Historie Endpoint"""
    limit = request.args.get('limit', 50, type=int)
    orders = webhook_server.order_manager.get_order_history(limit)
    
    return jsonify({
        'orders': [
            {
                'id': order.id,
                'broker_order_id': order.broker_order_id,
                'symbol': order.symbol,
                'order_type': order.order_type.value,
                'side': order.side.value,
                'quantity': order.quantity,
                'price': order.price,
                'status': order.status.value,
                'broker': order.broker.value,
                'created_at': order.created_at.isoformat(),
                'filled_quantity': order.filled_quantity,
                'avg_fill_price': order.avg_fill_price,
                'commission': order.commission,
                'error_message': order.error_message
            }
            for order in orders
        ],
        'total': len(orders),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/brokers', methods=['GET'])
def get_brokers():
    """Broker-Status Endpoint"""
    return jsonify(webhook_server.order_manager.get_broker_status())

if __name__ == '__main__':
    print("=" * 80)
 print("TRADINGVIEW WEBHOOK SERVER")
    print("=" * 80)
    print("Starting TradingView Webhook Server...")
    print(f"Health Check: http://localhost:5000/")
    print(f"TradingView Webhook: http://localhost:5000/webhook/tradingview")
    print(f"Test Webhook: http://localhost:5000/webhook/test")
    print(f"Status: http://localhost:5000/status")
    print(f"Orders: http://localhost:5000/orders")
    print("=" * 80)
    
    # Starte Flask-Server
    app.run(host='0.0.0.0', port=5000, debug=False)

