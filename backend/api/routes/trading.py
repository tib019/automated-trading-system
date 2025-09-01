"""
Trading routes for the Flask API
Handles data collection, signal generation, and trading operations
"""

from flask import Blueprint, jsonify, request, current_app
import sys
import os

# Add trading system to path
sys.path.append('/home/ubuntu/trading_system')

trading_bp = Blueprint('trading', __name__)

@trading_bp.route('/collect-data', methods=['POST'])
def collect_data():
    """Trigger data collection for specified symbols"""
    try:
        components = current_app.config['TRADING_COMPONENTS']
        data_collector = components['data_collector']
        
        data = request.get_json() or {}
        symbols = data.get('symbols', ['BTC-USD', 'ETH-USD', 'AAPL', 'TSLA'])
        
        results = []
        for symbol in symbols:
            try:
                # Collect market data
                market_data = data_collector.collect_yahoo_finance_data(symbol)
                if market_data:
                    results.append({
                        'symbol': symbol,
                        'status': 'success',
                        'data': market_data
                    })
                else:
                    results.append({
                        'symbol': symbol,
                        'status': 'no_data',
                        'data': None
                    })
            except Exception as e:
                results.append({
                    'symbol': symbol,
                    'status': 'error',
                    'error': str(e)
                })
        
        return jsonify({
            'status': 'completed',
            'collected': len([r for r in results if r['status'] == 'success']),
            'total': len(symbols),
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@trading_bp.route('/analyze-sentiment', methods=['POST'])
def analyze_sentiment():
    """Analyze sentiment for given text"""
    try:
        components = current_app.config['TRADING_COMPONENTS']
        sentiment_analyzer = components['sentiment_analyzer']
        
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({
                'status': 'error',
                'error': 'Text is required'
            }), 400
        
        text = data['text']
        result = sentiment_analyzer.analyze_sentiment(text)
        
        return jsonify({
            'status': 'success',
            'sentiment': result
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@trading_bp.route('/generate-signal', methods=['POST'])
def generate_signal():
    """Generate trading signal for given market and sentiment data"""
    try:
        components = current_app.config['TRADING_COMPONENTS']
        signal_generator = components['signal_generator']
        
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'error': 'Market data is required'
            }), 400
        
        market_data = data.get('market_data', {})
        sentiment_data = data.get('sentiment_data', {})
        
        if not market_data:
            return jsonify({
                'status': 'error',
                'error': 'Market data is required'
            }), 400
        
        signal = signal_generator.generate_signal(market_data, sentiment_data)
        
        return jsonify({
            'status': 'success',
            'signal': signal
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@trading_bp.route('/auto-trade', methods=['POST'])
def auto_trade():
    """Execute automated trading workflow"""
    try:
        components = current_app.config['TRADING_COMPONENTS']
        data_collector = components['data_collector']
        sentiment_analyzer = components['sentiment_analyzer']
        signal_generator = components['signal_generator']
        risk_manager = components['risk_manager']
        order_manager = components['order_manager']
        
        data = request.get_json() or {}
        symbol = data.get('symbol', 'BTC-USD')
        
        # Step 1: Collect market data
        market_data = data_collector.collect_yahoo_finance_data(symbol)
        if not market_data:
            return jsonify({
                'status': 'error',
                'error': f'No market data available for {symbol}'
            }), 400
        
        # Step 2: Collect sentiment data (mock for now)
        sentiment_data = {
            'sentiment_score': 0.3,
            'confidence': 0.7,
            'source': 'aggregated'
        }
        
        # Step 3: Generate signal
        signal = signal_generator.generate_signal(market_data, sentiment_data)
        
        # Step 4: Validate with risk management
        if signal['action'] in ['BUY', 'SELL']:
            position = {
                'symbol': symbol,
                'side': signal['action'],
                'quantity': signal.get('quantity', 0.1),
                'price': market_data['price'],
                'order_type': 'MARKET'
            }
            
            is_valid = risk_manager.validate_position(position)
            
            if is_valid:
                # Step 5: Execute order
                order = order_manager.create_order(position)
                
                return jsonify({
                    'status': 'success',
                    'workflow': {
                        'market_data': market_data,
                        'sentiment_data': sentiment_data,
                        'signal': signal,
                        'order': order
                    }
                })
            else:
                return jsonify({
                    'status': 'rejected',
                    'reason': 'Risk management validation failed',
                    'workflow': {
                        'market_data': market_data,
                        'sentiment_data': sentiment_data,
                        'signal': signal
                    }
                })
        else:
            return jsonify({
                'status': 'hold',
                'workflow': {
                    'market_data': market_data,
                    'sentiment_data': sentiment_data,
                    'signal': signal
                }
            })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@trading_bp.route('/symbols', methods=['GET'])
def get_symbols():
    """Get list of supported trading symbols"""
    try:
        components = current_app.config['TRADING_COMPONENTS']
        config = components['config']
        
        return jsonify({
            'status': 'success',
            'symbols': {
                'crypto': config.CRYPTO_SYMBOLS,
                'stocks': config.STOCK_SYMBOLS,
                'all': config.CRYPTO_SYMBOLS + config.STOCK_SYMBOLS
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@trading_bp.route('/market-data/<symbol>', methods=['GET'])
def get_market_data(symbol):
    """Get current market data for a symbol"""
    try:
        components = current_app.config['TRADING_COMPONENTS']
        data_collector = components['data_collector']
        
        market_data = data_collector.collect_yahoo_finance_data(symbol)
        
        if market_data:
            return jsonify({
                'status': 'success',
                'symbol': symbol,
                'data': market_data
            })
        else:
            return jsonify({
                'status': 'error',
                'error': f'No data available for {symbol}'
            }), 404
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

