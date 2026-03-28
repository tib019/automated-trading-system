import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'trading_system_secret_key_change_in_production'

# Enable CORS for all routes
CORS(app, origins="*")

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Trading System API',
        'version': '1.0.0',
        'components': {
            'api_server': 'active',
            'database': 'active',
            'cors': 'enabled'
        }
    })

@app.route('/api/status')
def system_status():
    """Get comprehensive system status"""
    try:
        return jsonify({
            'status': 'operational',
            'timestamp': '2025-09-01T08:00:00Z',
            'portfolio': {
                'total_value': 100000,
                'cash_balance': 95000,
                'positions': [
                    {'symbol': 'BTC-USD', 'quantity': 0.08, 'value': 4000},
                    {'symbol': 'AAPL', 'quantity': 10, 'value': 1800}
                ],
                'risk_level': 'LOW'
            },
            'trading': {
                'recent_orders': 6,
                'last_order': {
                    'id': 'order_123',
                    'symbol': 'BTC-USD',
                    'side': 'BUY',
                    'status': 'FILLED'
                }
            },
            'security': {
                'events_24h': 12,
                'last_audit': 'recent',
                'security_score': 95.5
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/trading/symbols')
def get_symbols():
    """Get list of supported trading symbols"""
    return jsonify({
        'status': 'success',
        'symbols': {
            'crypto': ['BTC-USD', 'ETH-USD', 'ADA-USD', 'DOT-USD', 'LINK-USD'],
            'stocks': ['AAPL', 'TSLA', 'GOOGL', 'MSFT', 'AMZN', 'NVDA'],
            'all': ['BTC-USD', 'ETH-USD', 'ADA-USD', 'DOT-USD', 'LINK-USD', 'AAPL', 'TSLA', 'GOOGL', 'MSFT', 'AMZN', 'NVDA']
        }
    })

@app.route('/api/portfolio/status')
def get_portfolio_status():
    """Get current portfolio status"""
    return jsonify({
        'status': 'success',
        'portfolio': {
            'total_value': 100000,
            'cash_balance': 95000,
            'unrealized_pnl': 500,
            'realized_pnl': -200,
            'positions': [
                {
                    'symbol': 'BTC-USD',
                    'quantity': 0.08,
                    'avg_price': 50000,
                    'current_price': 50500,
                    'market_value': 4040,
                    'unrealized_pnl': 40,
                    'pnl_percent': 1.0
                },
                {
                    'symbol': 'AAPL',
                    'quantity': 10,
                    'avg_price': 180,
                    'current_price': 185,
                    'market_value': 1850,
                    'unrealized_pnl': 50,
                    'pnl_percent': 2.78
                }
            ],
            'risk_metrics': {
                'portfolio_risk': 'LOW',
                'max_drawdown': 2.5,
                'sharpe_ratio': 1.8,
                'exposure': 5.89
            }
        }
    })

@app.route('/api/orders')
def get_orders():
    """Get order history"""
    return jsonify({
        'status': 'success',
        'orders': [
            {
                'id': 'order_123',
                'symbol': 'BTC-USD',
                'side': 'BUY',
                'quantity': 0.08,
                'price': 50000,
                'status': 'FILLED',
                'timestamp': '2025-09-01T07:30:00Z'
            },
            {
                'id': 'order_124',
                'symbol': 'AAPL',
                'side': 'BUY',
                'quantity': 10,
                'price': 180,
                'status': 'FILLED',
                'timestamp': '2025-09-01T07:25:00Z'
            }
        ],
        'count': 2
    })

@app.route('/api/signals/recommendations')
def get_recommendations():
    """Get trading recommendations"""
    return jsonify({
        'status': 'success',
        'recommendations': [
            {
                'symbol': 'BTC-USD',
                'action': 'BUY',
                'strength': 'MODERATE',
                'confidence': 0.75,
                'price': 50500,
                'reasoning': 'Bullish sentiment + oversold RSI',
                'entry_price': 50400,
                'stop_loss': 48900,
                'take_profit': 55200
            },
            {
                'symbol': 'ETH-USD',
                'action': 'SELL',
                'strength': 'WEAK',
                'confidence': 0.65,
                'price': 4400,
                'reasoning': 'Bearish sentiment + overbought RSI',
                'entry_price': 4396,
                'stop_loss': 4530,
                'take_profit': 4020
            }
        ],
        'count': 2,
        'timestamp': '2025-09-01T08:00:00Z'
    })

@app.route('/api/security/events')
def get_security_events():
    """Get recent security events"""
    return jsonify({
        'status': 'success',
        'events': [
            {
                'event_type': 'order_created',
                'severity': 'INFO',
                'details': 'Order created: order_123 for BTC-USD',
                'timestamp': '2025-09-01T07:30:00Z',
                'source_ip': '127.0.0.1'
            },
            {
                'event_type': 'security_audit',
                'severity': 'INFO',
                'details': 'Security audit completed with score 95.5/100',
                'timestamp': '2025-09-01T07:00:00Z',
                'source_ip': '127.0.0.1'
            }
        ],
        'count': 2,
        'period_hours': 24
    })

@app.route('/api/emergency/kill-switch', methods=['POST'])
def emergency_kill_switch():
    """Emergency kill switch endpoint"""
    return jsonify({
        'status': 'success',
        'message': 'Kill switch activated (simulation)',
        'result': {
            'positions_closed': 2,
            'orders_cancelled': 0,
            'portfolio_protected': True
        }
    })

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve frontend files or API info"""
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return jsonify({
            'message': 'Trading System API',
            'version': '1.0.0',
            'status': 'operational',
            'endpoints': {
                'health': '/api/health',
                'status': '/api/status',
                'portfolio': '/api/portfolio/status',
                'orders': '/api/orders',
                'signals': '/api/signals/recommendations',
                'security': '/api/security/events',
                'emergency': '/api/emergency/kill-switch'
            },
            'documentation': 'https://github.com/trading-system/api-docs'
        })

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return jsonify({
                'message': 'Trading System API',
                'version': '1.0.0',
                'status': 'operational',
                'endpoints': {
                    'health': '/api/health',
                    'status': '/api/status',
                    'portfolio': '/api/portfolio/status',
                    'orders': '/api/orders',
                    'signals': '/api/signals/recommendations',
                    'security': '/api/security/events',
                    'emergency': '/api/emergency/kill-switch'
                }
            })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'The requested endpoint does not exist',
        'available_endpoints': [
            '/api/health',
            '/api/status',
            '/api/portfolio/status',
            '/api/orders',
            '/api/signals/recommendations',
            '/api/security/events'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500

if __name__ == '__main__':
 print("Starting Trading System API...")
 print("API Base: http://localhost:5000")
 print("Health Check: http://localhost:5000/api/health")
 print("System Status: http://localhost:5000/api/status")
 print("Portfolio: http://localhost:5000/api/portfolio/status")
 print("Orders: http://localhost:5000/api/orders")
 print("Signals: http://localhost:5000/api/signals/recommendations")
 print("Security: http://localhost:5000/api/security/events")
    app.run(host='0.0.0.0', port=5001, debug=True)

