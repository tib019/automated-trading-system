"""
Orders routes for the Flask API
Handles order management, execution, and history
"""

from flask import Blueprint, jsonify, request, current_app
import sys

# Add trading system to path
sys.path.append('/home/ubuntu/trading_system')

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/', methods=['GET'])
def get_orders():
    """Get order history"""
    try:
        components = current_app.config['TRADING_COMPONENTS']
        order_manager = components['order_manager']
        
        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        status = request.args.get('status')
        symbol = request.args.get('symbol')
        
        orders = order_manager.get_orders(limit=limit, status=status, symbol=symbol)
        
        return jsonify({
            'status': 'success',
            'orders': orders,
            'count': len(orders)
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@orders_bp.route('/<order_id>', methods=['GET'])
def get_order(order_id):
    """Get specific order by ID"""
    try:
        components = current_app.config['TRADING_COMPONENTS']
        order_manager = components['order_manager']
        
        order = order_manager.get_order(order_id)
        
        if order:
            return jsonify({
                'status': 'success',
                'order': order
            })
        else:
            return jsonify({
                'status': 'not_found',
                'message': f'Order {order_id} not found'
            }), 404
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@orders_bp.route('/', methods=['POST'])
def create_order():
    """Create new order"""
    try:
        components = current_app.config['TRADING_COMPONENTS']
        order_manager = components['order_manager']
        risk_manager = components['risk_manager']
        security_manager = components['security_manager']
        
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'error': 'Order data is required'
            }), 400
        
        # Validate required fields
        required_fields = ['symbol', 'side', 'quantity', 'order_type']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Validate order data
        if not order_manager.validate_order(data):
            return jsonify({
                'status': 'error',
                'error': 'Invalid order data'
            }), 400
        
        # Risk management validation
        if not risk_manager.validate_position(data):
            return jsonify({
                'status': 'error',
                'error': 'Order rejected by risk management'
            }), 400
        
        # Create order
        order = order_manager.create_order(data)
        
        # Log security event
        security_manager.log_security_event(
            'order_created',
            'INFO',
            f'Order created: {order["id"]} for {data["symbol"]}',
            request.remote_addr,
            request.headers.get('User-Agent')
        )
        
        return jsonify({
            'status': 'success',
            'order': order
        }), 201
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@orders_bp.route('/<order_id>/cancel', methods=['POST'])
def cancel_order(order_id):
    """Cancel an order"""
    try:
        components = current_app.config['TRADING_COMPONENTS']
        order_manager = components['order_manager']
        security_manager = components['security_manager']
        
        result = order_manager.cancel_order(order_id)
        
        if result:
            # Log security event
            security_manager.log_security_event(
                'order_cancelled',
                'INFO',
                f'Order cancelled: {order_id}',
                request.remote_addr,
                request.headers.get('User-Agent')
            )
            
            return jsonify({
                'status': 'success',
                'message': f'Order {order_id} cancelled successfully'
            })
        else:
            return jsonify({
                'status': 'error',
                'error': f'Failed to cancel order {order_id}'
            }), 400
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@orders_bp.route('/stats', methods=['GET'])
def get_order_stats():
    """Get order statistics"""
    try:
        components = current_app.config['TRADING_COMPONENTS']
        order_manager = components['order_manager']
        
        # Get query parameters
        days = request.args.get('days', 30, type=int)
        
        stats = order_manager.get_order_statistics(days=days)
        
        return jsonify({
            'status': 'success',
            'stats': stats,
            'period_days': days
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@orders_bp.route('/recent', methods=['GET'])
def get_recent_orders():
    """Get recent orders"""
    try:
        components = current_app.config['TRADING_COMPONENTS']
        order_manager = components['order_manager']
        
        limit = request.args.get('limit', 10, type=int)
        
        orders = order_manager.get_recent_orders(limit=limit)
        
        return jsonify({
            'status': 'success',
            'orders': orders,
            'count': len(orders)
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@orders_bp.route('/validate', methods=['POST'])
def validate_order():
    """Validate order without executing"""
    try:
        components = current_app.config['TRADING_COMPONENTS']
        order_manager = components['order_manager']
        risk_manager = components['risk_manager']
        
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'error': 'Order data is required'
            }), 400
        
        # Validate order format
        format_valid = order_manager.validate_order(data)
        
        # Validate with risk management
        risk_valid = risk_manager.validate_position(data)
        
        # Calculate position size if not provided
        if 'quantity' not in data and 'price' in data:
            suggested_quantity = risk_manager.calculate_position_size(
                account_balance=100000,  # Default balance
                risk_per_trade=0.02,
                entry_price=data['price'],
                stop_loss_price=data.get('stop_loss', data['price'] * 0.95)
            )
        else:
            suggested_quantity = data.get('quantity')
        
        return jsonify({
            'status': 'success',
            'validation': {
                'format_valid': format_valid,
                'risk_valid': risk_valid,
                'overall_valid': format_valid and risk_valid,
                'suggested_quantity': suggested_quantity,
                'order_data': data
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@orders_bp.route('/bulk', methods=['POST'])
def create_bulk_orders():
    """Create multiple orders at once"""
    try:
        components = current_app.config['TRADING_COMPONENTS']
        order_manager = components['order_manager']
        risk_manager = components['risk_manager']
        security_manager = components['security_manager']
        
        data = request.get_json()
        if not data or 'orders' not in data:
            return jsonify({
                'status': 'error',
                'error': 'Orders array is required'
            }), 400
        
        orders_data = data['orders']
        if not isinstance(orders_data, list):
            return jsonify({
                'status': 'error',
                'error': 'Orders must be an array'
            }), 400
        
        results = []
        for i, order_data in enumerate(orders_data):
            try:
                # Validate order
                if not order_manager.validate_order(order_data):
                    results.append({
                        'index': i,
                        'status': 'error',
                        'error': 'Invalid order format'
                    })
                    continue
                
                # Risk validation
                if not risk_manager.validate_position(order_data):
                    results.append({
                        'index': i,
                        'status': 'error',
                        'error': 'Risk validation failed'
                    })
                    continue
                
                # Create order
                order = order_manager.create_order(order_data)
                results.append({
                    'index': i,
                    'status': 'success',
                    'order': order
                })
                
            except Exception as e:
                results.append({
                    'index': i,
                    'status': 'error',
                    'error': str(e)
                })
        
        # Log bulk order creation
        successful_orders = len([r for r in results if r['status'] == 'success'])
        security_manager.log_security_event(
            'bulk_orders_created',
            'INFO',
            f'Bulk order creation: {successful_orders}/{len(orders_data)} successful',
            request.remote_addr,
            request.headers.get('User-Agent')
        )
        
        return jsonify({
            'status': 'completed',
            'total_orders': len(orders_data),
            'successful': successful_orders,
            'failed': len(orders_data) - successful_orders,
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

