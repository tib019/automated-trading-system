"""
Portfolio routes for the Flask API
Handles portfolio management, positions, and performance tracking
"""

from flask import Blueprint, jsonify, request, current_app
import sys

# Add trading system to path
sys.path.append('/home/ubuntu/trading_system')

portfolio_bp = Blueprint('portfolio', __name__)

@portfolio_bp.route('/status', methods=['GET'])
def get_portfolio_status():
    """Get current portfolio status"""
    try:
        components = current_app.config['TRADING_COMPONENTS']
        risk_manager = components['risk_manager']
        
        status = risk_manager.get_portfolio_status()
        
        return jsonify({
            'status': 'success',
            'portfolio': status
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@portfolio_bp.route('/positions', methods=['GET'])
def get_positions():
    """Get all current positions"""
    try:
        components = current_app.config['TRADING_COMPONENTS']
        risk_manager = components['risk_manager']
        
        positions = risk_manager.get_positions()
        
        return jsonify({
            'status': 'success',
            'positions': positions,
            'count': len(positions)
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@portfolio_bp.route('/positions/<symbol>', methods=['GET'])
def get_position(symbol):
    """Get position for specific symbol"""
    try:
        components = current_app.config['TRADING_COMPONENTS']
        risk_manager = components['risk_manager']
        
        position = risk_manager.get_position(symbol)
        
        if position:
            return jsonify({
                'status': 'success',
                'position': position
            })
        else:
            return jsonify({
                'status': 'not_found',
                'message': f'No position found for {symbol}'
            }), 404
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@portfolio_bp.route('/performance', methods=['GET'])
def get_performance():
    """Get portfolio performance metrics"""
    try:
        components = current_app.config['TRADING_COMPONENTS']
        risk_manager = components['risk_manager']
        
        # Get query parameters
        days = request.args.get('days', 30, type=int)
        
        performance = risk_manager.get_performance_metrics(days=days)
        
        return jsonify({
            'status': 'success',
            'performance': performance,
            'period_days': days
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@portfolio_bp.route('/risk-metrics', methods=['GET'])
def get_risk_metrics():
    """Get current risk metrics"""
    try:
        components = current_app.config['TRADING_COMPONENTS']
        risk_manager = components['risk_manager']
        
        risk_metrics = {
            'portfolio_value': risk_manager.portfolio_value,
            'max_portfolio_risk': risk_manager.max_portfolio_risk,
            'max_position_size': risk_manager.max_position_size,
            'daily_loss_limit': risk_manager.daily_loss_limit,
            'kill_switch_active': risk_manager.kill_switch_active,
            'risk_level': risk_manager.get_risk_level()
        }
        
        return jsonify({
            'status': 'success',
            'risk_metrics': risk_metrics
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@portfolio_bp.route('/balance', methods=['GET'])
def get_balance():
    """Get account balance information"""
    try:
        components = current_app.config['TRADING_COMPONENTS']
        order_manager = components['order_manager']
        
        # Get balance from paper trading broker
        balance = order_manager.get_account_balance()
        
        return jsonify({
            'status': 'success',
            'balance': balance
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@portfolio_bp.route('/history', methods=['GET'])
def get_portfolio_history():
    """Get portfolio value history"""
    try:
        components = current_app.config['TRADING_COMPONENTS']
        risk_manager = components['risk_manager']
        
        # Get query parameters
        days = request.args.get('days', 30, type=int)
        
        history = risk_manager.get_portfolio_history(days=days)
        
        return jsonify({
            'status': 'success',
            'history': history,
            'period_days': days
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@portfolio_bp.route('/allocation', methods=['GET'])
def get_allocation():
    """Get portfolio allocation breakdown"""
    try:
        components = current_app.config['TRADING_COMPONENTS']
        risk_manager = components['risk_manager']
        
        allocation = risk_manager.get_portfolio_allocation()
        
        return jsonify({
            'status': 'success',
            'allocation': allocation
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@portfolio_bp.route('/rebalance', methods=['POST'])
def rebalance_portfolio():
    """Trigger portfolio rebalancing"""
    try:
        components = current_app.config['TRADING_COMPONENTS']
        risk_manager = components['risk_manager']
        order_manager = components['order_manager']
        
        data = request.get_json() or {}
        target_allocation = data.get('target_allocation', {})
        
        # Perform rebalancing
        rebalance_orders = risk_manager.calculate_rebalancing_orders(target_allocation)
        
        executed_orders = []
        for order_data in rebalance_orders:
            try:
                order = order_manager.create_order(order_data)
                executed_orders.append(order)
            except Exception as e:
                executed_orders.append({
                    'error': str(e),
                    'order_data': order_data
                })
        
        return jsonify({
            'status': 'success',
            'rebalance_orders': len(rebalance_orders),
            'executed_orders': len([o for o in executed_orders if 'error' not in o]),
            'failed_orders': len([o for o in executed_orders if 'error' in o]),
            'orders': executed_orders
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

