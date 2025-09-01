import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Add trading system to path
sys.path.append('/home/ubuntu/trading_system')

from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.trading import trading_bp
from src.routes.portfolio import portfolio_bp
from src.routes.orders import orders_bp
from src.routes.signals import signals_bp
from src.routes.security import security_bp

# Import trading system components
from config import TradingConfig
from data_collector_v2 import DataCollector
from sentiment_analyzer import SentimentAnalyzer
from signal_generator import SignalGenerator
from risk_manager import RiskManager
from order_manager import OrderManager
from security_manager import SecurityManager

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'trading_system_secret_key_change_in_production'

# Enable CORS for all routes
CORS(app, origins="*")

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(trading_bp, url_prefix='/api/trading')
app.register_blueprint(portfolio_bp, url_prefix='/api/portfolio')
app.register_blueprint(orders_bp, url_prefix='/api/orders')
app.register_blueprint(signals_bp, url_prefix='/api/signals')
app.register_blueprint(security_bp, url_prefix='/api/security')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Initialize trading system components
config = TradingConfig()
data_collector = DataCollector(config)
sentiment_analyzer = SentimentAnalyzer()
signal_generator = SignalGenerator()
risk_manager = RiskManager()
order_manager = OrderManager()
security_manager = SecurityManager()

# Store components in app context for access in routes
app.config['TRADING_COMPONENTS'] = {
    'config': config,
    'data_collector': data_collector,
    'sentiment_analyzer': sentiment_analyzer,
    'signal_generator': signal_generator,
    'risk_manager': risk_manager,
    'order_manager': order_manager,
    'security_manager': security_manager
}

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
            'data_collector': 'active',
            'signal_generator': 'active',
            'risk_manager': 'active',
            'order_manager': 'active',
            'security_manager': 'active'
        }
    })

@app.route('/api/status')
def system_status():
    """Get comprehensive system status"""
    try:
        # Get portfolio status
        portfolio_status = risk_manager.get_portfolio_status()
        
        # Get recent orders
        recent_orders = order_manager.get_recent_orders(limit=5)
        
        # Get security events
        security_events = security_manager.get_security_events(hours=24)
        
        return jsonify({
            'status': 'operational',
            'timestamp': portfolio_status.get('timestamp'),
            'portfolio': {
                'total_value': portfolio_status.get('total_value', 0),
                'cash_balance': portfolio_status.get('cash_balance', 0),
                'positions': portfolio_status.get('positions', []),
                'risk_level': portfolio_status.get('risk_level', 'UNKNOWN')
            },
            'trading': {
                'recent_orders': len(recent_orders),
                'last_order': recent_orders[0] if recent_orders else None
            },
            'security': {
                'events_24h': len(security_events),
                'last_audit': 'recent'
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/emergency/kill-switch', methods=['POST'])
def emergency_kill_switch():
    """Emergency kill switch endpoint"""
    try:
        # Activate kill switch
        result = risk_manager.activate_kill_switch()
        
        # Log security event
        security_manager.log_security_event(
            'kill_switch_activated',
            'CRITICAL',
            'Emergency kill switch activated via API',
            request.remote_addr,
            request.headers.get('User-Agent')
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Kill switch activated',
            'result': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve frontend files"""
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

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
                'endpoints': [
                    '/api/health',
                    '/api/status',
                    '/api/trading/*',
                    '/api/portfolio/*',
                    '/api/orders/*',
                    '/api/signals/*',
                    '/api/security/*'
                ]
            })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'The requested endpoint does not exist'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500

if __name__ == '__main__':
    print("🚀 Starting Trading System API...")
    print("📊 Dashboard: http://localhost:5000")
    print("🔗 API Health: http://localhost:5000/api/health")
    print("📈 System Status: http://localhost:5000/api/status")
    app.run(host='0.0.0.0', port=5000, debug=True)

