"""
Security routes for the Flask API
Handles security monitoring, audit, and management
"""

from flask import Blueprint, jsonify, request, current_app
import sys

# Add trading system to path
sys.path.append('/home/ubuntu/trading_system')

security_bp = Blueprint('security', __name__)

@security_bp.route('/events', methods=['GET'])
def get_security_events():
    """Get recent security events"""
    try:
        components = current_app.config['TRADING_COMPONENTS']
        security_manager = components['security_manager']
        
        hours = request.args.get('hours', 24, type=int)
        
        events = security_manager.get_security_events(hours=hours)
        
        return jsonify({
            'status': 'success',
            'events': events,
            'count': len(events),
            'period_hours': hours
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@security_bp.route('/audit', methods=['POST'])
def run_security_audit():
    """Run security audit"""
    try:
        # Import audit tool
        from security_audit import SecurityAuditor
        
        auditor = SecurityAuditor()
        results = auditor.run_full_audit()
        
        return jsonify({
            'status': 'success',
            'audit_results': results
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@security_bp.route('/validate-signature', methods=['POST'])
def validate_signature():
    """Validate webhook signature"""
    try:
        components = current_app.config['TRADING_COMPONENTS']
        security_manager = components['security_manager']
        
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'error': 'Payload, signature, and secret are required'
            }), 400
        
        payload = data.get('payload', '')
        signature = data.get('signature', '')
        secret = data.get('secret', '')
        
        if not all([payload, signature, secret]):
            return jsonify({
                'status': 'error',
                'error': 'Payload, signature, and secret are required'
            }), 400
        
        is_valid = security_manager.validate_webhook_signature(payload, signature, secret)
        
        return jsonify({
            'status': 'success',
            'valid': is_valid
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@security_bp.route('/generate-signature', methods=['POST'])
def generate_signature():
    """Generate webhook signature"""
    try:
        components = current_app.config['TRADING_COMPONENTS']
        security_manager = components['security_manager']
        
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'error': 'Payload and secret are required'
            }), 400
        
        payload = data.get('payload', '')
        secret = data.get('secret', '')
        
        if not all([payload, secret]):
            return jsonify({
                'status': 'error',
                'error': 'Payload and secret are required'
            }), 400
        
        signature = security_manager.generate_webhook_signature(payload, secret)
        
        return jsonify({
            'status': 'success',
            'signature': signature
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@security_bp.route('/rate-limit-status', methods=['GET'])
def get_rate_limit_status():
    """Get rate limiting status for IP"""
    try:
        components = current_app.config['TRADING_COMPONENTS']
        security_manager = components['security_manager']
        
        ip_address = request.remote_addr
        endpoint = request.args.get('endpoint', 'api')
        
        is_limited = security_manager.rate_limiter.is_rate_limited(ip_address, endpoint)
        
        return jsonify({
            'status': 'success',
            'ip_address': ip_address,
            'endpoint': endpoint,
            'rate_limited': is_limited
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@security_bp.route('/log-event', methods=['POST'])
def log_security_event():
    """Log a security event"""
    try:
        components = current_app.config['TRADING_COMPONENTS']
        security_manager = components['security_manager']
        
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'error': 'Event data is required'
            }), 400
        
        event_type = data.get('event_type', 'unknown')
        severity = data.get('severity', 'INFO')
        details = data.get('details', '')
        
        security_manager.log_security_event(
            event_type,
            severity,
            details,
            request.remote_addr,
            request.headers.get('User-Agent')
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Security event logged'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@security_bp.route('/session', methods=['POST'])
def create_session():
    """Create new session"""
    try:
        components = current_app.config['TRADING_COMPONENTS']
        security_manager = components['security_manager']
        
        data = request.get_json()
        if not data or 'user_id' not in data:
            return jsonify({
                'status': 'error',
                'error': 'User ID is required'
            }), 400
        
        user_id = data['user_id']
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')
        
        session_id = security_manager.session_manager.create_session(
            user_id, ip_address, user_agent
        )
        
        return jsonify({
            'status': 'success',
            'session_id': session_id
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@security_bp.route('/session/<session_id>/validate', methods=['POST'])
def validate_session(session_id):
    """Validate session"""
    try:
        components = current_app.config['TRADING_COMPONENTS']
        security_manager = components['security_manager']
        
        ip_address = request.remote_addr
        
        is_valid = security_manager.session_manager.validate_session(session_id, ip_address)
        
        return jsonify({
            'status': 'success',
            'valid': is_valid,
            'session_id': session_id
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@security_bp.route('/session/<session_id>/invalidate', methods=['POST'])
def invalidate_session(session_id):
    """Invalidate session"""
    try:
        components = current_app.config['TRADING_COMPONENTS']
        security_manager = components['security_manager']
        
        security_manager.session_manager.invalidate_session(session_id)
        
        return jsonify({
            'status': 'success',
            'message': f'Session {session_id} invalidated'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@security_bp.route('/encrypt', methods=['POST'])
def encrypt_data():
    """Encrypt data"""
    try:
        components = current_app.config['TRADING_COMPONENTS']
        security_manager = components['security_manager']
        
        data = request.get_json()
        if not data or 'data' not in data:
            return jsonify({
                'status': 'error',
                'error': 'Data to encrypt is required'
            }), 400
        
        plain_data = data['data']
        encrypted_data = security_manager.encrypt_data(plain_data)
        
        return jsonify({
            'status': 'success',
            'encrypted_data': encrypted_data
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@security_bp.route('/decrypt', methods=['POST'])
def decrypt_data():
    """Decrypt data"""
    try:
        components = current_app.config['TRADING_COMPONENTS']
        security_manager = components['security_manager']
        
        data = request.get_json()
        if not data or 'encrypted_data' not in data:
            return jsonify({
                'status': 'error',
                'error': 'Encrypted data is required'
            }), 400
        
        encrypted_data = data['encrypted_data']
        decrypted_data = security_manager.decrypt_data(encrypted_data)
        
        return jsonify({
            'status': 'success',
            'decrypted_data': decrypted_data
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

