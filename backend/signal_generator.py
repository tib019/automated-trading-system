#!/usr/bin/env python3
"""
Trading System - Signal Generation Module
Generiert Trading-Signale basierend auf Sentiment und technischen Indikatoren
"""

import sqlite3
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from config import get_config
from sentiment_analyzer import SentimentAggregator, SentimentScore

# Logging Setup
logger = logging.getLogger(__name__)

class SignalType(Enum):
    """Trading-Signal-Typen"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

class SignalStrength(Enum):
    """Signal-Stärke"""
    WEAK = "WEAK"
    MODERATE = "MODERATE"
    STRONG = "STRONG"

@dataclass
class TradingSignal:
    """Trading-Signal-Datenklasse"""
    symbol: str
    timestamp: datetime
    signal_type: SignalType
    strength: SignalStrength
    entry_price: float
    stop_loss: float
    take_profit: float
    confidence: float
    reasoning: str
    
    # Signal-Komponenten
    sentiment_score: float
    technical_score: float
    volume_score: float
    
    # Risikomanagement
    position_size_percent: float
    risk_reward_ratio: float

class TechnicalAnalyzer:
    """Technische Analyse-Komponenten"""
    
    def __init__(self, db_path: str = '/home/ubuntu/trading_system/trading_data.db'):
        self.db_path = db_path
        self.config = get_config()
    
    def get_market_data(self, symbol: str, hours: int = 168) -> List[Dict]:
        """Hole Marktdaten für technische Analyse (7 Tage default)"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT timestamp, open_price, high_price, low_price, close_price, volume
                FROM market_data 
                WHERE symbol = ? AND timestamp > ?
                ORDER BY timestamp ASC
            ''', (symbol, cutoff_time))
            
            results = cursor.fetchall()
            
            return [
                {
                    'timestamp': row[0],
                    'open': row[1],
                    'high': row[2],
                    'low': row[3],
                    'close': row[4],
                    'volume': row[5]
                }
                for row in results
            ]
    
    def calculate_sma(self, prices: List[float], period: int) -> List[float]:
        """Berechne Simple Moving Average"""
        if len(prices) < period:
            return []
        
        sma = []
        for i in range(period - 1, len(prices)):
            avg = sum(prices[i - period + 1:i + 1]) / period
            sma.append(avg)
        
        return sma
    
    def calculate_ema(self, prices: List[float], period: int) -> List[float]:
        """Berechne Exponential Moving Average"""
        if len(prices) < period:
            return []
        
        multiplier = 2 / (period + 1)
        ema = [sum(prices[:period]) / period]  # Erste EMA ist SMA
        
        for i in range(period, len(prices)):
            ema_value = (prices[i] * multiplier) + (ema[-1] * (1 - multiplier))
            ema.append(ema_value)
        
        return ema
    
    def calculate_rsi(self, prices: List[float], period: int = 14) -> List[float]:
        """Berechne Relative Strength Index"""
        if len(prices) < period + 1:
            return []
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [delta if delta > 0 else 0 for delta in deltas]
        losses = [-delta if delta < 0 else 0 for delta in deltas]
        
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        
        rsi = []
        
        for i in range(period, len(deltas)):
            if avg_loss == 0:
                rsi.append(100)
            else:
                rs = avg_gain / avg_loss
                rsi_value = 100 - (100 / (1 + rs))
                rsi.append(rsi_value)
            
            # Update averages
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        
        return rsi
    
    def calculate_macd(self, prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, List[float]]:
        """Berechne MACD (Moving Average Convergence Divergence)"""
        if len(prices) < slow:
            return {'macd': [], 'signal': [], 'histogram': []}
        
        ema_fast = self.calculate_ema(prices, fast)
        ema_slow = self.calculate_ema(prices, slow)
        
        # Align EMAs (slow EMA starts later)
        start_idx = slow - fast
        ema_fast_aligned = ema_fast[start_idx:]
        
        macd_line = [fast_val - slow_val for fast_val, slow_val in zip(ema_fast_aligned, ema_slow)]
        signal_line = self.calculate_ema(macd_line, signal)
        
        # Align for histogram calculation
        histogram_start = len(macd_line) - len(signal_line)
        macd_aligned = macd_line[histogram_start:]
        histogram = [macd_val - signal_val for macd_val, signal_val in zip(macd_aligned, signal_line)]
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    def calculate_bollinger_bands(self, prices: List[float], period: int = 20, std_dev: float = 2) -> Dict[str, List[float]]:
        """Berechne Bollinger Bands"""
        if len(prices) < period:
            return {'upper': [], 'middle': [], 'lower': []}
        
        sma = self.calculate_sma(prices, period)
        upper_band = []
        lower_band = []
        
        for i in range(period - 1, len(prices)):
            price_slice = prices[i - period + 1:i + 1]
            std = np.std(price_slice)
            sma_val = sma[i - period + 1]
            
            upper_band.append(sma_val + (std * std_dev))
            lower_band.append(sma_val - (std * std_dev))
        
        return {
            'upper': upper_band,
            'middle': sma,
            'lower': lower_band
        }
    
    def analyze_technical_indicators(self, symbol: str) -> Dict[str, float]:
        """Analysiere technische Indikatoren für Signal-Generierung"""
        market_data = self.get_market_data(symbol, hours=168)  # 7 Tage
        
        if len(market_data) < 50:  # Mindestens 50 Datenpunkte
            return {'score': 0.0, 'confidence': 0.0}
        
        closes = [data['close'] for data in market_data]
        volumes = [data['volume'] for data in market_data]
        
        current_price = closes[-1]
        
        # Berechne Indikatoren
        sma_20 = self.calculate_sma(closes, 20)
        sma_50 = self.calculate_sma(closes, 50)
        ema_12 = self.calculate_ema(closes, 12)
        rsi = self.calculate_rsi(closes)
        macd_data = self.calculate_macd(closes)
        bollinger = self.calculate_bollinger_bands(closes)
        
        # Analysiere Signale
        signals = []
        
        # Moving Average Signale
        if sma_20 and sma_50 and len(sma_20) > 1 and len(sma_50) > 1:
            if sma_20[-1] > sma_50[-1] and sma_20[-2] <= sma_50[-2]:
                signals.append(('MA_GOLDEN_CROSS', 0.7))
            elif sma_20[-1] < sma_50[-1] and sma_20[-2] >= sma_50[-2]:
                signals.append(('MA_DEATH_CROSS', -0.7))
            elif current_price > sma_20[-1]:
                signals.append(('ABOVE_SMA20', 0.3))
            else:
                signals.append(('BELOW_SMA20', -0.3))
        
        # RSI Signale
        if rsi:
            current_rsi = rsi[-1]
            if current_rsi < 30:
                signals.append(('RSI_OVERSOLD', 0.6))
            elif current_rsi > 70:
                signals.append(('RSI_OVERBOUGHT', -0.6))
            elif 40 <= current_rsi <= 60:
                signals.append(('RSI_NEUTRAL', 0.0))
        
        # MACD Signale
        if macd_data['histogram'] and len(macd_data['histogram']) > 1:
            if macd_data['histogram'][-1] > 0 and macd_data['histogram'][-2] <= 0:
                signals.append(('MACD_BULLISH_CROSS', 0.5))
            elif macd_data['histogram'][-1] < 0 and macd_data['histogram'][-2] >= 0:
                signals.append(('MACD_BEARISH_CROSS', -0.5))
        
        # Bollinger Bands Signale
        if bollinger['upper'] and bollinger['lower']:
            if current_price <= bollinger['lower'][-1]:
                signals.append(('BB_OVERSOLD', 0.4))
            elif current_price >= bollinger['upper'][-1]:
                signals.append(('BB_OVERBOUGHT', -0.4))
        
        # Volumen-Analyse
        if len(volumes) >= 20:
            avg_volume = sum(volumes[-20:]) / 20
            current_volume = volumes[-1]
            volume_ratio = current_volume / avg_volume
            
            if volume_ratio > 1.5:
                signals.append(('HIGH_VOLUME', 0.3))
            elif volume_ratio < 0.5:
                signals.append(('LOW_VOLUME', -0.2))
        
        # Berechne finalen technischen Score
        if signals:
            total_score = sum(score for _, score in signals)
            avg_score = total_score / len(signals)
            confidence = min(1.0, len(signals) / 5.0)  # Mehr Signale = höhere Konfidenz
        else:
            avg_score = 0.0
            confidence = 0.0
        
        return {
            'score': max(-1.0, min(1.0, avg_score)),
            'confidence': confidence,
            'signals': signals,
            'current_price': current_price,
            'rsi': rsi[-1] if rsi else 50,
            'volume_ratio': volume_ratio if 'volume_ratio' in locals() else 1.0
        }

class SignalGenerator:
    """Hauptklasse für Trading-Signal-Generierung"""
    
    def __init__(self):
        self.config = get_config()
        self.sentiment_aggregator = SentimentAggregator()
        self.technical_analyzer = TechnicalAnalyzer()
        self.db_path = self.config.DATABASE['path']
    
    def generate_signal(self, symbol: str) -> Optional[TradingSignal]:
        """Generiere Trading-Signal für Symbol"""
        try:
            # Sammle Sentiment-Daten
            sentiment_score = self.sentiment_aggregator.calculate_aggregated_sentiment(symbol, hours=24)
            
            # Sammle technische Analyse-Daten
            technical_data = self.technical_analyzer.analyze_technical_indicators(symbol)
            
            # Prüfe Mindestanforderungen
            if (sentiment_score.confidence < 0.3 and technical_data['confidence'] < 0.3):
                return None  # Nicht genug Daten für Signal
            
            # Berechne kombinierte Scores
            combined_score = self._calculate_combined_score(sentiment_score, technical_data)
            
            # Bestimme Signal-Typ und -Stärke
            signal_type, strength = self._determine_signal_type(combined_score)
            
            if signal_type == SignalType.HOLD:
                return None  # Kein Trading-Signal
            
            # Berechne Entry, Stop-Loss und Take-Profit
            current_price = technical_data['current_price']
            entry_price, stop_loss, take_profit = self._calculate_levels(
                current_price, signal_type, strength, technical_data
            )
            
            # Berechne Positionsgröße
            position_size = self._calculate_position_size(signal_type, strength, combined_score['confidence'])
            
            # Erstelle Reasoning
            reasoning = self._generate_reasoning(sentiment_score, technical_data, combined_score)
            
            return TradingSignal(
                symbol=symbol,
                timestamp=datetime.now(),
                signal_type=signal_type,
                strength=strength,
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                confidence=combined_score['confidence'],
                reasoning=reasoning,
                sentiment_score=sentiment_score.final_score,
                technical_score=technical_data['score'],
                volume_score=sentiment_score.volume_score,
                position_size_percent=position_size,
                risk_reward_ratio=(take_profit - entry_price) / abs(entry_price - stop_loss) if signal_type == SignalType.BUY else (entry_price - take_profit) / abs(stop_loss - entry_price)
            )
            
        except Exception as e:
            logger.error(f"Error generating signal for {symbol}: {e}")
            return None
    
    def _calculate_combined_score(self, sentiment: SentimentScore, technical: Dict) -> Dict[str, float]:
        """Kombiniere Sentiment und technische Analyse"""
        sentiment_weight = self.config.SIGNAL_CONFIG['sentiment_weight']
        technical_weight = self.config.SIGNAL_CONFIG['technical_weight']
        
        # Gewichtete Kombination
        combined_score = (
            sentiment.final_score * sentiment_weight +
            technical['score'] * technical_weight
        )
        
        # Kombinierte Konfidenz
        combined_confidence = (
            sentiment.confidence * sentiment_weight +
            technical['confidence'] * technical_weight
        )
        
        return {
            'score': combined_score,
            'confidence': combined_confidence
        }
    
    def _determine_signal_type(self, combined_score: Dict) -> Tuple[SignalType, SignalStrength]:
        """Bestimme Signal-Typ und -Stärke"""
        score = combined_score['score']
        confidence = combined_score['confidence']
        
        min_score = self.config.SIGNAL_CONFIG['min_sentiment_score']
        
        if score > min_score and confidence > 0.5:
            if score > 0.6:
                return SignalType.BUY, SignalStrength.STRONG
            elif score > 0.3:
                return SignalType.BUY, SignalStrength.MODERATE
            else:
                return SignalType.BUY, SignalStrength.WEAK
        elif score < -min_score and confidence > 0.5:
            if score < -0.6:
                return SignalType.SELL, SignalStrength.STRONG
            elif score < -0.3:
                return SignalType.SELL, SignalStrength.MODERATE
            else:
                return SignalType.SELL, SignalStrength.WEAK
        else:
            return SignalType.HOLD, SignalStrength.WEAK
    
    def _calculate_levels(self, current_price: float, signal_type: SignalType, 
                         strength: SignalStrength, technical_data: Dict) -> Tuple[float, float, float]:
        """Berechne Entry, Stop-Loss und Take-Profit Levels"""
        
        # Basis-Prozentsätze aus Konfiguration
        base_stop_loss = self.config.RISK_MANAGEMENT['stop_loss_percent'] / 100
        base_take_profit = self.config.RISK_MANAGEMENT['take_profit_percent'] / 100
        
        # Anpassung basierend auf Signal-Stärke
        strength_multiplier = {
            SignalStrength.WEAK: 0.7,
            SignalStrength.MODERATE: 1.0,
            SignalStrength.STRONG: 1.3
        }[strength]
        
        # Anpassung basierend auf Volatilität (RSI als Proxy)
        rsi = technical_data.get('rsi', 50)
        volatility_multiplier = 1.0
        if rsi > 70 or rsi < 30:  # Hohe Volatilität
            volatility_multiplier = 1.2
        
        adjusted_stop_loss = base_stop_loss * strength_multiplier * volatility_multiplier
        adjusted_take_profit = base_take_profit * strength_multiplier * volatility_multiplier
        
        if signal_type == SignalType.BUY:
            entry_price = current_price
            stop_loss = current_price * (1 - adjusted_stop_loss)
            take_profit = current_price * (1 + adjusted_take_profit)
        else:  # SELL
            entry_price = current_price
            stop_loss = current_price * (1 + adjusted_stop_loss)
            take_profit = current_price * (1 - adjusted_take_profit)
        
        return round(entry_price, 2), round(stop_loss, 2), round(take_profit, 2)
    
    def _calculate_position_size(self, signal_type: SignalType, strength: SignalStrength, confidence: float) -> float:
        """Berechne Positionsgröße basierend auf Risikomanagement"""
        base_size = self.config.RISK_MANAGEMENT['max_position_size_percent']
        
        # Anpassung basierend auf Signal-Stärke
        strength_factor = {
            SignalStrength.WEAK: 0.5,
            SignalStrength.MODERATE: 0.75,
            SignalStrength.STRONG: 1.0
        }[strength]
        
        # Anpassung basierend auf Konfidenz
        confidence_factor = confidence
        
        position_size = base_size * strength_factor * confidence_factor
        
        return round(position_size, 2)
    
    def _generate_reasoning(self, sentiment: SentimentScore, technical: Dict, combined: Dict) -> str:
        """Generiere Begründung für Signal"""
        reasoning_parts = []
        
        # Sentiment-Begründung
        if abs(sentiment.final_score) > 0.3:
            sentiment_label = "bullish" if sentiment.final_score > 0 else "bearish"
            reasoning_parts.append(f"Sentiment: {sentiment_label} ({sentiment.final_score:.2f})")
        
        # Technische Begründung
        if abs(technical['score']) > 0.3:
            technical_label = "bullish" if technical['score'] > 0 else "bearish"
            reasoning_parts.append(f"Technical: {technical_label} ({technical['score']:.2f})")
        
        # Spezifische technische Signale
        if 'signals' in technical:
            strong_signals = [name for name, score in technical['signals'] if abs(score) > 0.5]
            if strong_signals:
                reasoning_parts.append(f"Key signals: {', '.join(strong_signals[:3])}")
        
        # Volumen
        if sentiment.volume_score > 10:
            reasoning_parts.append(f"High social volume ({int(sentiment.volume_score)} mentions)")
        
        return " | ".join(reasoning_parts) if reasoning_parts else "Mixed signals"

def main():
    """Test der Signal-Generierung"""
    print("=" * 60)
    print("TRADING SIGNAL GENERATOR TEST")
    print("=" * 60)
    
    generator = SignalGenerator()
    
    # Test mit verfügbaren Symbolen
    test_symbols = ['BTC-USD', 'ETH-USD', 'AAPL', 'TSLA']
    
    for symbol in test_symbols:
        print(f"\nGenerating signal for {symbol}:")
        print("-" * 40)
        
        signal = generator.generate_signal(symbol)
        
        if signal:
            print(f"Symbol: {signal.symbol}")
            print(f"Signal: {signal.signal_type.value} ({signal.strength.value})")
            print(f"Entry: ${signal.entry_price}")
            print(f"Stop Loss: ${signal.stop_loss} ({((signal.stop_loss/signal.entry_price-1)*100):+.1f}%)")
            print(f"Take Profit: ${signal.take_profit} ({((signal.take_profit/signal.entry_price-1)*100):+.1f}%)")
            print(f"Position Size: {signal.position_size_percent}%")
            print(f"Confidence: {signal.confidence:.2f}")
            print(f"Risk/Reward: 1:{signal.risk_reward_ratio:.2f}")
            print(f"Reasoning: {signal.reasoning}")
            
            # Signal-Komponenten
            print(f"\nSignal Components:")
            print(f"  Sentiment Score: {signal.sentiment_score:.3f}")
            print(f"  Technical Score: {signal.technical_score:.3f}")
            print(f"  Volume Score: {signal.volume_score}")
        else:
            print("No signal generated (insufficient data or HOLD)")

if __name__ == "__main__":
    main()

