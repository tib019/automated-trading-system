#!/usr/bin/env python3
"""
Demo Trading Signals mit realistischen Schwellenwerten
Zeigt wie das System mit angepassten Parametern funktioniert
"""

from signal_generator import SignalGenerator, TechnicalAnalyzer
from sentiment_analyzer import SentimentAggregator
from config import get_config
from datetime import datetime

def demo_with_realistic_thresholds():
    """Demo mit realistischen Schwellenwerten für echte Marktbedingungen"""
    
    print("=" * 80)
    print("TRADING SIGNAL GENERATOR - REALISTIC DEMO")
    print("=" * 80)
    
    # Konfiguration für Demo anpassen
    config = get_config()
    
    # Speichere Original-Werte
    original_min_sentiment = config.SIGNAL_CONFIG['min_sentiment_score']
    original_sentiment_weight = config.SIGNAL_CONFIG['sentiment_weight']
    original_technical_weight = config.SIGNAL_CONFIG['technical_weight']
    
    # Setze realistische Werte für Demo
    config.SIGNAL_CONFIG['min_sentiment_score'] = 0.05  # Sehr niedrig für Demo
    config.SIGNAL_CONFIG['sentiment_weight'] = 0.3      # Weniger Gewicht auf Sentiment
    config.SIGNAL_CONFIG['technical_weight'] = 0.7      # Mehr Gewicht auf Technische Analyse
    
    print(f"Demo Configuration:")
    print(f"  Min Sentiment Score: {config.SIGNAL_CONFIG['min_sentiment_score']}")
    print(f"  Sentiment Weight: {config.SIGNAL_CONFIG['sentiment_weight']}")
    print(f"  Technical Weight: {config.SIGNAL_CONFIG['technical_weight']}")
    print()
    
    generator = SignalGenerator()
    test_symbols = ['BTC-USD', 'ETH-USD', 'TSLA', 'AAPL']
    
    signals_generated = []
    
    for symbol in test_symbols:
        print(f"{'='*20} {symbol} SIGNAL ANALYSIS {'='*20}")
        
        # Generiere Signal
        signal = generator.generate_signal(symbol)
        
        if signal:
            signals_generated.append(signal)
            
 print(f" SIGNAL GENERATED!")
            print(f"   Symbol: {signal.symbol}")
            print(f"   Type: {signal.signal_type.value}")
            print(f"   Strength: {signal.strength.value}")
            print(f"   Entry Price: ${signal.entry_price:,.2f}")
            print(f"   Stop Loss: ${signal.stop_loss:,.2f} ({((signal.stop_loss/signal.entry_price-1)*100):+.1f}%)")
            print(f"   Take Profit: ${signal.take_profit:,.2f} ({((signal.take_profit/signal.entry_price-1)*100):+.1f}%)")
            print(f"   Position Size: {signal.position_size_percent}% of portfolio")
            print(f"   Confidence: {signal.confidence:.1%}")
            print(f"   Risk/Reward Ratio: 1:{signal.risk_reward_ratio:.2f}")
            print(f"   Reasoning: {signal.reasoning}")
            
 print(f"\n Signal Components:")
            print(f"      Sentiment Score: {signal.sentiment_score:+.3f}")
            print(f"      Technical Score: {signal.technical_score:+.3f}")
            print(f"      Social Volume: {signal.volume_score} mentions")
            
        else:
 print(f" No signal generated for {symbol}")
        
        print()
    
    # Zusammenfassung
    print("=" * 80)
    print("SIGNAL SUMMARY")
    print("=" * 80)
    
    if signals_generated:
 print(f" Generated {len(signals_generated)} trading signals:")
        print()
        
        for i, signal in enumerate(signals_generated, 1):
            action_color = "🟢" if signal.signal_type.value == "BUY" else "🔴"
            print(f"{i}. {action_color} {signal.symbol} | {signal.signal_type.value} | Entry: ${signal.entry_price:,.2f} | Size: {signal.position_size_percent}%")
        
        print(f"\nExample Trading Command Format:")
        best_signal = max(signals_generated, key=lambda s: s.confidence)
 print(f" {best_signal.symbol} | {best_signal.signal_type.value} | Entry: {best_signal.entry_price} | SL: -{abs((best_signal.entry_price-best_signal.stop_loss)/best_signal.entry_price*100):.1f}% | TP: +{abs((best_signal.take_profit-best_signal.entry_price)/best_signal.entry_price*100):.1f}% | Grund: {best_signal.reasoning}")
        
    else:
 print(" No signals generated. Market conditions may be too neutral or volatile.")
    
    # Restore original configuration
    config.SIGNAL_CONFIG['min_sentiment_score'] = original_min_sentiment
    config.SIGNAL_CONFIG['sentiment_weight'] = original_sentiment_weight
    config.SIGNAL_CONFIG['technical_weight'] = original_technical_weight
    
    return signals_generated

def analyze_current_market_conditions():
    """Analysiere aktuelle Marktbedingungen"""
    
    print("\n" + "=" * 80)
    print("CURRENT MARKET CONDITIONS ANALYSIS")
    print("=" * 80)
    
    technical_analyzer = TechnicalAnalyzer()
    sentiment_aggregator = SentimentAggregator()
    
    symbols = ['BTC-USD', 'ETH-USD', 'TSLA', 'AAPL']
    
    market_summary = {
        'bullish_signals': 0,
        'bearish_signals': 0,
        'neutral_signals': 0,
        'high_volume_symbols': [],
        'oversold_symbols': [],
        'overbought_symbols': []
    }
    
    for symbol in symbols:
        technical_data = technical_analyzer.analyze_technical_indicators(symbol)
        sentiment_data = sentiment_aggregator.calculate_aggregated_sentiment(symbol, hours=24)
        
        print(f"\n{symbol}:")
        print(f"  Price: ${technical_data.get('current_price', 0):,.2f}")
        print(f"  RSI: {technical_data.get('rsi', 50):.1f}")
        print(f"  Technical Score: {technical_data['score']:+.3f}")
        print(f"  Sentiment Score: {sentiment_data.final_score:+.3f}")
        print(f"  Social Volume: {sentiment_data.volume_score} mentions")
        
        # Kategorisiere Signale
        combined_score = technical_data['score'] * 0.7 + sentiment_data.final_score * 0.3
        
        if combined_score > 0.05:
            market_summary['bullish_signals'] += 1
 print(f" Leaning BULLISH ({combined_score:+.3f})")
        elif combined_score < -0.05:
            market_summary['bearish_signals'] += 1
 print(f" Leaning BEARISH ({combined_score:+.3f})")
        else:
            market_summary['neutral_signals'] += 1
 print(f" ️ NEUTRAL ({combined_score:+.3f})")
        
        # Spezielle Bedingungen
        rsi = technical_data.get('rsi', 50)
        if rsi < 30:
            market_summary['oversold_symbols'].append(symbol)
        elif rsi > 70:
            market_summary['overbought_symbols'].append(symbol)
        
        if sentiment_data.volume_score > 5:
            market_summary['high_volume_symbols'].append(symbol)
    
    # Market Summary
 print(f"\n MARKET SUMMARY:")
    print(f"   Bullish Signals: {market_summary['bullish_signals']}")
    print(f"   Bearish Signals: {market_summary['bearish_signals']}")
    print(f"   Neutral Signals: {market_summary['neutral_signals']}")
    
    if market_summary['oversold_symbols']:
 print(f" Oversold (RSI < 30): {', '.join(market_summary['oversold_symbols'])}")
    
    if market_summary['overbought_symbols']:
 print(f" Overbought (RSI > 70): {', '.join(market_summary['overbought_symbols'])}")
    
    if market_summary['high_volume_symbols']:
 print(f" High Social Volume: {', '.join(market_summary['high_volume_symbols'])}")

def main():
    """Hauptfunktion für Demo"""
    signals = demo_with_realistic_thresholds()
    analyze_current_market_conditions()
    
    print(f"\n{'='*80}")
    print("DEMO COMPLETED")
    print(f"{'='*80}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Signals Generated: {len(signals)}")
 print(f"System Status: Operational")

if __name__ == "__main__":
    main()

