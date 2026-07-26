#!/usr/bin/env python3
"""
Trading System - TradingView Webhook Server
Flask-basierter Webhook-Server für TradingView-Signale
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
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
            
            # Risiko-Deckelung: Ordergroesse auf das mathematisch begruendete
            # Maximum begrenzen (fractional Kelly x Volatilitaets-Targeting x
            # CVaR-Budget). Risiko kann die Groesse nur verkleinern.
            risk_detail = None
            try:
                from risk_service import cap_position_pct
                applied, risk_detail = cap_position_pct(
                    signal.symbol, signal.position_size_percent,
                    signal.confidence, signal.risk_reward_ratio,
                )
                signal.position_size_percent = applied
            except Exception as exc:
                logger.warning(f"Risk sizing skipped for {signal.symbol}: {exc}")

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
                        'strength': signal.strength.value,
                        'position_size_pct': signal.position_size_percent
                    },
                    'risk': risk_detail,
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
@app.route('/health', methods=['GET'])
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

@app.route('/signals/<symbol>', methods=['GET'])
def get_signal(symbol):
    """Run the real data -> sentiment -> signal pipeline for a symbol.

    Best-effort refresh of market/sentiment data for the symbol, then generate
    a trading signal from the technical + sentiment fusion. Returns HOLD (200)
    when there is not enough data or no actionable signal.
    """
    symbol = symbol.upper()
    try:
        # Lazy imports: keep server startup light and avoid a hard dependency
        # if the analytics stack is unavailable in a given deployment.
        from data_collector import TradingDataCollector
        from signal_generator import SignalGenerator

        try:
            TradingDataCollector().collect_all_data([symbol])
        except Exception as exc:
            logger.warning(f"Data collection for {symbol} failed: {exc}")

        from risk_service import symbol_risk, recommended_position

        signal = SignalGenerator().generate_signal(symbol)
        if signal is None:
            return jsonify({
                'symbol': symbol,
                'signal': 'HOLD',
                'reason': 'insufficient data or no actionable signal',
                'risk': symbol_risk(symbol),
                'timestamp': datetime.now().isoformat(),
            })

        return jsonify({
            'symbol': symbol,
            'signal': signal.signal_type.value,
            'strength': signal.strength.value,
            'confidence': round(signal.confidence, 4),
            'entry_price': signal.entry_price,
            'stop_loss': signal.stop_loss,
            'take_profit': signal.take_profit,
            'risk_reward_ratio': round(signal.risk_reward_ratio, 3),
            'sentiment_score': round(signal.sentiment_score, 4),
            'technical_score': round(signal.technical_score, 4),
            'reasoning': signal.reasoning,
            'risk': symbol_risk(symbol),
            'recommended_position': recommended_position(
                symbol, signal.confidence, signal.risk_reward_ratio),
            'timestamp': signal.timestamp.isoformat(),
        })
    except Exception as exc:
        logger.error(f"Signal generation for {symbol} failed: {exc}")
        return jsonify({'symbol': symbol, 'error': str(exc)}), 500

@app.route('/risk/<symbol>', methods=['GET'])
def risk_report(symbol):
    """Advanced risk report for a symbol: EWMA volatility, historical and
    Cornish-Fisher VaR, CVaR (expected shortfall), max drawdown, Sharpe/Sortino.
    """
    try:
        from risk_service import symbol_risk
        return jsonify(symbol_risk(symbol.upper()))
    except Exception as exc:
        logger.error(f"Risk report for {symbol} failed: {exc}")
        return jsonify({'symbol': symbol.upper(), 'error': str(exc)}), 500


@app.route('/risk/portfolio', methods=['GET'])
def portfolio_risk_report():
    """Correlation-aware portfolio risk across the current open paper positions.

    Uses the covariance matrix of the held symbols' returns, so correlated
    positions are not treated as independent, and reports whether the portfolio
    VaR is within budget (risk gate).
    """
    try:
        from risk_service import portfolio_risk
        status = webhook_server.order_manager.get_broker_status()
        positions = []
        for broker in status.values():
            total = 0.0
            for pos in broker.get('positions', []):
                total += float(pos.get('value', pos.get('market_value', 0)) or 0)
            for pos in broker.get('positions', []):
                sym = pos.get('symbol')
                val = float(pos.get('value', pos.get('market_value', 0)) or 0)
                if sym and total > 0:
                    positions.append((sym, val / total))
        if not positions:
            return jsonify({'positions': 0, 'sufficient_data': False,
                            'message': 'no open positions'})
        return jsonify(portfolio_risk(positions))
    except Exception as exc:
        logger.error(f"Portfolio risk failed: {exc}")
        return jsonify({'error': str(exc)}), 500


if __name__ == '__main__':
    host = os.environ.get('API_HOST', '0.0.0.0')
    port = int(os.environ.get('API_PORT', '5001'))
    print("=" * 80)
    print("TRADINGVIEW WEBHOOK SERVER")
    print("=" * 80)
    print("Starting TradingView Webhook Server...")
    print(f"Health Check: http://localhost:{port}/")
    print(f"TradingView Webhook: http://localhost:{port}/webhook/tradingview")
    print(f"Test Webhook: http://localhost:{port}/webhook/test")
    print(f"Status: http://localhost:{port}/status")
    print(f"Orders: http://localhost:{port}/orders")
    print("=" * 80)

    # Starte Flask-Server
    app.run(host=host, port=port, debug=False)

