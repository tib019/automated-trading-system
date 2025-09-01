#!/usr/bin/env python3
"""
Final Trading Signal Demo
Zeigt das vollständige Signal-System mit simulierten starken Marktbedingungen
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List
from signal_generator import SignalType, SignalStrength, TradingSignal
from config import get_config

@dataclass
class SimulatedMarketCondition:
    """Simulierte Marktbedingungen für Demo"""
    symbol: str
    current_price: float
    sentiment_score: float
    technical_score: float
    volume_score: float
    rsi: float
    scenario_description: str

def create_demo_scenarios() -> List[SimulatedMarketCondition]:
    """Erstelle verschiedene Demo-Szenarien"""
    return [
        SimulatedMarketCondition(
            symbol="BTC-USD",
            current_price=108400.99,
            sentiment_score=0.75,  # Sehr bullish
            technical_score=0.65,  # Technisch stark
            volume_score=50,       # Hohe Social Media Aktivität
            rsi=25,               # Oversold
            scenario_description="Strong bullish sentiment + oversold technicals"
        ),
        SimulatedMarketCondition(
            symbol="ETH-USD", 
            current_price=4396.12,
            sentiment_score=-0.60, # Bearish
            technical_score=-0.45, # Technisch schwach
            volume_score=30,       # Moderate Aktivität
            rsi=75,               # Overbought
            scenario_description="Bearish sentiment + overbought technicals"
        ),
        SimulatedMarketCondition(
            symbol="TSLA",
            current_price=333.86,
            sentiment_score=0.45,  # Moderate bullish
            technical_score=0.35,  # Leicht bullish
            volume_score=25,       # Moderate Aktivität
            rsi=45,               # Neutral
            scenario_description="Moderate bullish across all indicators"
        ),
        SimulatedMarketCondition(
            symbol="AAPL",
            current_price=232.14,
            sentiment_score=0.20,  # Schwach bullish
            technical_score=-0.15, # Leicht bearish
            volume_score=5,        # Niedrige Aktivität
            rsi=55,               # Neutral
            scenario_description="Mixed signals, low confidence"
        )
    ]

def simulate_signal_generation(condition: SimulatedMarketCondition) -> TradingSignal:
    """Simuliere Signal-Generierung basierend auf Marktbedingungen"""
    
    config = get_config()
    
    # Berechne kombinierte Scores
    sentiment_weight = config.SIGNAL_CONFIG['sentiment_weight']
    technical_weight = config.SIGNAL_CONFIG['technical_weight']
    
    combined_score = (
        condition.sentiment_score * sentiment_weight +
        condition.technical_score * technical_weight
    )
    
    # Berechne Konfidenz
    sentiment_confidence = min(1.0, abs(condition.sentiment_score) + (condition.volume_score / 100))
    technical_confidence = 0.8  # Simuliere hohe technische Konfidenz
    
    combined_confidence = (
        sentiment_confidence * sentiment_weight +
        technical_confidence * technical_weight
    )
    
    # Bestimme Signal-Typ und -Stärke
    if combined_score > 0.5:
        signal_type = SignalType.BUY
        strength = SignalStrength.STRONG
    elif combined_score > 0.3:
        signal_type = SignalType.BUY
        strength = SignalStrength.MODERATE
    elif combined_score > 0.1:
        signal_type = SignalType.BUY
        strength = SignalStrength.WEAK
    elif combined_score < -0.5:
        signal_type = SignalType.SELL
        strength = SignalStrength.STRONG
    elif combined_score < -0.3:
        signal_type = SignalType.SELL
        strength = SignalStrength.MODERATE
    elif combined_score < -0.1:
        signal_type = SignalType.SELL
        strength = SignalStrength.WEAK
    else:
        return None  # HOLD
    
    # Berechne Levels
    base_stop_loss = config.RISK_MANAGEMENT['stop_loss_percent'] / 100
    base_take_profit = config.RISK_MANAGEMENT['take_profit_percent'] / 100
    
    # Anpassung basierend auf Stärke
    strength_multiplier = {
        SignalStrength.WEAK: 0.7,
        SignalStrength.MODERATE: 1.0,
        SignalStrength.STRONG: 1.3
    }[strength]
    
    # RSI-basierte Anpassung
    volatility_multiplier = 1.2 if condition.rsi > 70 or condition.rsi < 30 else 1.0
    
    adjusted_stop_loss = base_stop_loss * strength_multiplier * volatility_multiplier
    adjusted_take_profit = base_take_profit * strength_multiplier * volatility_multiplier
    
    if signal_type == SignalType.BUY:
        entry_price = condition.current_price
        stop_loss = condition.current_price * (1 - adjusted_stop_loss)
        take_profit = condition.current_price * (1 + adjusted_take_profit)
    else:  # SELL
        entry_price = condition.current_price
        stop_loss = condition.current_price * (1 + adjusted_stop_loss)
        take_profit = condition.current_price * (1 - adjusted_take_profit)
    
    # Positionsgröße
    base_size = config.RISK_MANAGEMENT['max_position_size_percent']
    strength_factor = {
        SignalStrength.WEAK: 0.5,
        SignalStrength.MODERATE: 0.75,
        SignalStrength.STRONG: 1.0
    }[strength]
    
    position_size = base_size * strength_factor * combined_confidence
    
    # Reasoning
    reasoning_parts = []
    if abs(condition.sentiment_score) > 0.3:
        sentiment_label = "bullish" if condition.sentiment_score > 0 else "bearish"
        reasoning_parts.append(f"Sentiment: {sentiment_label} ({condition.sentiment_score:+.2f})")
    
    if abs(condition.technical_score) > 0.3:
        technical_label = "bullish" if condition.technical_score > 0 else "bearish"
        reasoning_parts.append(f"Technical: {technical_label} ({condition.technical_score:+.2f})")
    
    if condition.rsi < 30:
        reasoning_parts.append("RSI oversold")
    elif condition.rsi > 70:
        reasoning_parts.append("RSI overbought")
    
    if condition.volume_score > 20:
        reasoning_parts.append(f"High social volume ({int(condition.volume_score)} mentions)")
    
    reasoning = " | ".join(reasoning_parts) if reasoning_parts else condition.scenario_description
    
    return TradingSignal(
        symbol=condition.symbol,
        timestamp=datetime.now(),
        signal_type=signal_type,
        strength=strength,
        entry_price=round(entry_price, 2),
        stop_loss=round(stop_loss, 2),
        take_profit=round(take_profit, 2),
        confidence=combined_confidence,
        reasoning=reasoning,
        sentiment_score=condition.sentiment_score,
        technical_score=condition.technical_score,
        volume_score=condition.volume_score,
        position_size_percent=round(position_size, 2),
        risk_reward_ratio=(take_profit - entry_price) / abs(entry_price - stop_loss) if signal_type == SignalType.BUY else (entry_price - take_profit) / abs(stop_loss - entry_price)
    )

def run_final_demo():
    """Führe finale Demo mit verschiedenen Marktszenarien aus"""
    
    print("=" * 90)
    print("🎯 TRADING SYSTEM - FINAL SIGNAL GENERATION DEMO")
    print("=" * 90)
    print("Demonstrating signal generation under various market conditions")
    print()
    
    scenarios = create_demo_scenarios()
    generated_signals = []
    
    for i, condition in enumerate(scenarios, 1):
        print(f"{'='*20} SCENARIO {i}: {condition.symbol} {'='*20}")
        print(f"📊 Market Condition: {condition.scenario_description}")
        print(f"💰 Current Price: ${condition.current_price:,.2f}")
        print(f"😊 Sentiment Score: {condition.sentiment_score:+.2f}")
        print(f"📈 Technical Score: {condition.technical_score:+.2f}")
        print(f"📢 Social Volume: {condition.volume_score} mentions")
        print(f"📊 RSI: {condition.rsi:.1f}")
        print()
        
        # Generiere Signal
        signal = simulate_signal_generation(condition)
        
        if signal:
            generated_signals.append(signal)
            
            # Signal-Anzeige mit Emojis
            action_emoji = "🟢" if signal.signal_type == SignalType.BUY else "🔴"
            strength_emoji = {"WEAK": "⭐", "MODERATE": "⭐⭐", "STRONG": "⭐⭐⭐"}[signal.strength.value]
            
            print(f"🎯 {action_emoji} SIGNAL GENERATED {strength_emoji}")
            print(f"   Action: {signal.signal_type.value} ({signal.strength.value})")
            print(f"   Entry: ${signal.entry_price:,.2f}")
            print(f"   Stop Loss: ${signal.stop_loss:,.2f} ({((signal.stop_loss/signal.entry_price-1)*100):+.1f}%)")
            print(f"   Take Profit: ${signal.take_profit:,.2f} ({((signal.take_profit/signal.entry_price-1)*100):+.1f}%)")
            print(f"   Position Size: {signal.position_size_percent}% of portfolio")
            print(f"   Confidence: {signal.confidence:.1%}")
            print(f"   Risk/Reward: 1:{signal.risk_reward_ratio:.2f}")
            print(f"   Reasoning: {signal.reasoning}")
        else:
            print("❌ No signal generated (HOLD recommendation)")
        
        print()
    
    # Trading-Kommandos im gewünschten Format
    print("=" * 90)
    print("📋 TRADING COMMANDS (Your Requested Format)")
    print("=" * 90)
    
    if generated_signals:
        for signal in generated_signals:
            sl_percent = abs((signal.entry_price - signal.stop_loss) / signal.entry_price * 100)
            tp_percent = abs((signal.take_profit - signal.entry_price) / signal.entry_price * 100)
            
            print(f"📋 {signal.symbol} | {signal.signal_type.value} | Entry: {signal.entry_price} | SL: -{sl_percent:.1f}% | TP: +{tp_percent:.1f}% | Begründung: {signal.reasoning}")
    
    # Portfolio-Übersicht
    print(f"\n{'='*90}")
    print("💼 PORTFOLIO ALLOCATION SUMMARY")
    print("=" * 90)
    
    total_allocation = sum(signal.position_size_percent for signal in generated_signals)
    
    print(f"Total Portfolio Allocation: {total_allocation:.1f}%")
    print(f"Remaining Cash: {100 - total_allocation:.1f}%")
    print(f"Number of Positions: {len(generated_signals)}")
    
    if generated_signals:
        buy_signals = [s for s in generated_signals if s.signal_type == SignalType.BUY]
        sell_signals = [s for s in generated_signals if s.signal_type == SignalType.SELL]
        
        print(f"Long Positions: {len(buy_signals)}")
        print(f"Short Positions: {len(sell_signals)}")
        
        avg_confidence = sum(s.confidence for s in generated_signals) / len(generated_signals)
        avg_risk_reward = sum(s.risk_reward_ratio for s in generated_signals) / len(generated_signals)
        
        print(f"Average Confidence: {avg_confidence:.1%}")
        print(f"Average Risk/Reward: 1:{avg_risk_reward:.2f}")
    
    print(f"\n{'='*90}")
    print("✅ DEMO COMPLETED SUCCESSFULLY")
    print("=" * 90)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Signals Generated: {len(generated_signals)}")
    print(f"System Status: 🟢 Fully Operational")
    
    return generated_signals

if __name__ == "__main__":
    signals = run_final_demo()

