"""
Signals routes for the Flask API
Handles signal generation, analysis, and recommendations
"""

from flask import Blueprint, jsonify, request, current_app
import sys

# Add trading system to path
sys.path.append('/home/ubuntu/trading_system')

signals_bp = Blueprint('signals', __name__)

@signals_bp.route('/generate', methods=['POST'])
def generate_signal():
    """Generate trading signal for given data"""
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

@signals_bp.route('/analyze/<symbol>', methods=['GET'])
def analyze_symbol(symbol):
    """Analyze symbol and generate signal"""
    try:
        components = current_app.config['TRADING_COMPONENTS']
        data_collector = components['data_collector']
        sentiment_analyzer = components['sentiment_analyzer']
        signal_generator = components['signal_generator']
        
        # Collect market data
        market_data = data_collector.collect_yahoo_finance_data(symbol)
        if not market_data:
            return jsonify({
                'status': 'error',
                'error': f'No market data available for {symbol}'
            }), 404
        
        # Mock sentiment analysis (in production, this would collect real sentiment)
        sentiment_text = f"{symbol} trading analysis"
        sentiment_data = sentiment_analyzer.analyze_sentiment(sentiment_text)
        
        # Generate signal
        signal = signal_generator.generate_signal(market_data, sentiment_data)
        
        return jsonify({
            'status': 'success',
            'symbol': symbol,
            'analysis': {
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

@signals_bp.route('/batch-analyze', methods=['POST'])
def batch_analyze():
    """Analyze multiple symbols"""
    try:
        components = current_app.config['TRADING_COMPONENTS']
        data_collector = components['data_collector']
        sentiment_analyzer = components['sentiment_analyzer']
        signal_generator = components['signal_generator']
        
        data = request.get_json()
        if not data or 'symbols' not in data:
            return jsonify({
                'status': 'error',
                'error': 'Symbols array is required'
            }), 400
        
        symbols = data['symbols']
        results = []
        
        for symbol in symbols:
            try:
                # Collect market data
                market_data = data_collector.collect_yahoo_finance_data(symbol)
                if not market_data:
                    results.append({
                        'symbol': symbol,
                        'status': 'no_data',
                        'error': 'No market data available'
                    })
                    continue
                
                # Mock sentiment analysis
                sentiment_text = f"{symbol} trading analysis"
                sentiment_data = sentiment_analyzer.analyze_sentiment(sentiment_text)
                
                # Generate signal
                signal = signal_generator.generate_signal(market_data, sentiment_data)
                
                results.append({
                    'symbol': symbol,
                    'status': 'success',
                    'analysis': {
                        'market_data': market_data,
                        'sentiment_data': sentiment_data,
                        'signal': signal
                    }
                })
                
            except Exception as e:
                results.append({
                    'symbol': symbol,
                    'status': 'error',
                    'error': str(e)
                })
        
        successful = len([r for r in results if r['status'] == 'success'])
        
        return jsonify({
            'status': 'completed',
            'total_symbols': len(symbols),
            'successful': successful,
            'failed': len(symbols) - successful,
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@signals_bp.route('/recommendations', methods=['GET'])
def get_recommendations():
    """Get trading recommendations for all symbols"""
    try:
        components = current_app.config['TRADING_COMPONENTS']
        config = components['config']
        data_collector = components['data_collector']
        signal_generator = components['signal_generator']
        
        # Get all configured symbols
        all_symbols = config.CRYPTO_SYMBOLS + config.STOCK_SYMBOLS
        
        recommendations = []
        
        for symbol in all_symbols[:10]:  # Limit to first 10 for performance
            try:
                # Collect market data
                market_data = data_collector.collect_yahoo_finance_data(symbol)
                if not market_data:
                    continue
                
                # Mock sentiment data
                sentiment_data = {
                    'sentiment_score': 0.1,
                    'confidence': 0.6
                }
                
                # Generate signal
                signal = signal_generator.generate_signal(market_data, sentiment_data)
                
                if signal['action'] in ['BUY', 'SELL']:
                    recommendations.append({
                        'symbol': symbol,
                        'action': signal['action'],
                        'strength': signal['strength'],
                        'confidence': signal['confidence'],
                        'price': market_data['price'],
                        'reasoning': signal.get('reasoning', 'Technical analysis'),
                        'entry_price': signal.get('entry_price'),
                        'stop_loss': signal.get('stop_loss'),
                        'take_profit': signal.get('take_profit')
                    })
                
            except Exception:
                continue
        
        # Sort by confidence and strength
        recommendations.sort(key=lambda x: (x['confidence'], x['strength']), reverse=True)
        
        return jsonify({
            'status': 'success',
            'recommendations': recommendations,
            'count': len(recommendations),
            'timestamp': market_data.get('timestamp') if 'market_data' in locals() else None
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@signals_bp.route('/technical-indicators/<symbol>', methods=['GET'])
def get_technical_indicators(symbol):
    """Get technical indicators for a symbol"""
    try:
        components = current_app.config['TRADING_COMPONENTS']
        data_collector = components['data_collector']
        signal_generator = components['signal_generator']
        
        # Collect market data
        market_data = data_collector.collect_yahoo_finance_data(symbol)
        if not market_data:
            return jsonify({
                'status': 'error',
                'error': f'No market data available for {symbol}'
            }), 404
        
        # Calculate technical indicators
        price_history = market_data.get('price_history', [market_data['price']] * 20)
        
        indicators = {
            'sma_20': signal_generator.calculate_sma(price_history, 20),
            'ema_12': signal_generator.calculate_ema(price_history, 12),
            'rsi': signal_generator.calculate_rsi(price_history),
            'macd': signal_generator.calculate_macd(price_history),
            'bollinger_bands': signal_generator.calculate_bollinger_bands(price_history),
            'current_price': market_data['price'],
            'volume': market_data.get('volume', 0)
        }
        
        return jsonify({
            'status': 'success',
            'symbol': symbol,
            'indicators': indicators
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@signals_bp.route('/sentiment/<symbol>', methods=['GET'])
def get_sentiment(symbol):
    """Get sentiment analysis for a symbol"""
    try:
        components = current_app.config['TRADING_COMPONENTS']
        sentiment_analyzer = components['sentiment_analyzer']
        
        # Mock sentiment text (in production, this would come from social media, news, etc.)
        sentiment_text = f"{symbol} is showing strong momentum with positive market sentiment"
        
        sentiment_data = sentiment_analyzer.analyze_sentiment(sentiment_text)
        
        return jsonify({
            'status': 'success',
            'symbol': symbol,
            'sentiment': sentiment_data
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

