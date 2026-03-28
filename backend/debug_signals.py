#!/usr/bin/env python3
"""
Debug-Tool für Signal-Generierung
Analysiert warum keine Signale generiert werden
"""

from signal_generator import SignalGenerator, TechnicalAnalyzer
from sentiment_analyzer import SentimentAggregator
from config import get_config

def debug_signal_generation():
    """Debug Signal-Generierung für verschiedene Symbole"""
    
    generator = SignalGenerator()
    sentiment_aggregator = SentimentAggregator()
    technical_analyzer = TechnicalAnalyzer()
    config = get_config()
    
    test_symbols = ['BTC-USD', 'ETH-USD', 'AAPL', 'TSLA']
    
    print("=" * 80)
    print("SIGNAL GENERATION DEBUG ANALYSIS")
    print("=" * 80)
    
    for symbol in test_symbols:
        print(f"\n{'='*20} {symbol} {'='*20}")
        
        # 1. Sentiment-Analyse
        print("\n1. SENTIMENT ANALYSIS:")
        sentiment_score = sentiment_aggregator.calculate_aggregated_sentiment(symbol, hours=24)
        print(f"   Raw Score: {sentiment_score.raw_score:.3f}")
        print(f"   Final Score: {sentiment_score.final_score:.3f}")
        print(f"   Confidence: {sentiment_score.confidence:.3f}")
        print(f"   Volume: {sentiment_score.volume_score}")
        print(f"   Sources: {sentiment_score.source_breakdown}")
        
        # 2. Technische Analyse
        print("\n2. TECHNICAL ANALYSIS:")
        technical_data = technical_analyzer.analyze_technical_indicators(symbol)
        print(f"   Technical Score: {technical_data['score']:.3f}")
        print(f"   Confidence: {technical_data['confidence']:.3f}")
        print(f"   Current Price: ${technical_data.get('current_price', 'N/A')}")
        print(f"   RSI: {technical_data.get('rsi', 'N/A')}")
        
        if 'signals' in technical_data:
            print(f"   Technical Signals:")
            for signal_name, signal_score in technical_data['signals']:
                print(f"     - {signal_name}: {signal_score:.3f}")
        
        # 3. Marktdaten-Verfügbarkeit
        print("\n3. MARKET DATA AVAILABILITY:")
        market_data = technical_analyzer.get_market_data(symbol, hours=168)
        print(f"   Data Points: {len(market_data)}")
        if market_data:
            print(f"   Price Range: ${min(d['close'] for d in market_data):.2f} - ${max(d['close'] for d in market_data):.2f}")
            print(f"   Latest Price: ${market_data[-1]['close']:.2f}")
            print(f"   Latest Volume: {market_data[-1]['volume']:,}")
        
        # 4. Signal-Schwellenwerte prüfen
        print("\n4. SIGNAL THRESHOLDS:")
        min_sentiment = config.SIGNAL_CONFIG['min_sentiment_score']
        print(f"   Min Sentiment Score: {min_sentiment}")
        print(f"   Sentiment Weight: {config.SIGNAL_CONFIG['sentiment_weight']}")
        print(f"   Technical Weight: {config.SIGNAL_CONFIG['technical_weight']}")
        
        # 5. Kombinierte Score-Berechnung
        print("\n5. COMBINED SCORE CALCULATION:")
        if sentiment_score.confidence > 0 or technical_data['confidence'] > 0:
            combined_score = (
                sentiment_score.final_score * config.SIGNAL_CONFIG['sentiment_weight'] +
                technical_data['score'] * config.SIGNAL_CONFIG['technical_weight']
            )
            combined_confidence = (
                sentiment_score.confidence * config.SIGNAL_CONFIG['sentiment_weight'] +
                technical_data['confidence'] * config.SIGNAL_CONFIG['technical_weight']
            )
            
            print(f"   Combined Score: {combined_score:.3f}")
            print(f"   Combined Confidence: {combined_confidence:.3f}")
            
            # Signal-Entscheidung
            if combined_score > min_sentiment and combined_confidence > 0.5:
                signal_type = "BUY"
            elif combined_score < -min_sentiment and combined_confidence > 0.5:
                signal_type = "SELL"
            else:
                signal_type = "HOLD"
            
            print(f"   Signal Decision: {signal_type}")
            print(f"   Reason: Score={combined_score:.3f} (threshold=±{min_sentiment}), Confidence={combined_confidence:.3f} (min=0.5)")
        else:
            print("   No data available for combined calculation")
        
        print("-" * 60)

def test_with_lower_thresholds():
    """Test mit niedrigeren Schwellenwerten"""
    print("\n" + "=" * 80)
    print("TESTING WITH LOWER THRESHOLDS")
    print("=" * 80)
    
    # Temporär niedrigere Schwellenwerte setzen
    config = get_config()
    original_min_sentiment = config.SIGNAL_CONFIG['min_sentiment_score']
    config.SIGNAL_CONFIG['min_sentiment_score'] = 0.1  # Reduziere von 0.3 auf 0.1
    
    generator = SignalGenerator()
    
    test_symbols = ['BTC-USD', 'ETH-USD']
    
    for symbol in test_symbols:
        print(f"\nTesting {symbol} with min_sentiment_score = 0.1:")
        signal = generator.generate_signal(symbol)
        
        if signal:
 print(f" SIGNAL GENERATED!")
            print(f"   Type: {signal.signal_type.value} ({signal.strength.value})")
            print(f"   Entry: ${signal.entry_price}")
            print(f"   Confidence: {signal.confidence:.3f}")
            print(f"   Reasoning: {signal.reasoning}")
        else:
 print(" Still no signal generated")
    
    # Restore original threshold
    config.SIGNAL_CONFIG['min_sentiment_score'] = original_min_sentiment

if __name__ == "__main__":
    debug_signal_generation()
    test_with_lower_thresholds()

