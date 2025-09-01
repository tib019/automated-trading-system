#!/usr/bin/env python3
"""
Trading System - Advanced Sentiment Analysis Module
Erweiterte Sentiment-Analyse für Trading-Entscheidungen
"""

import re
import math
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict, Counter

from config import get_config

# Logging Setup
logger = logging.getLogger(__name__)

@dataclass
class SentimentScore:
    """Erweiterte Sentiment-Score-Klasse"""
    symbol: str
    timestamp: datetime
    raw_score: float  # -1 bis +1
    confidence: float  # 0 bis 1
    volume_score: float  # Anzahl der Mentions
    engagement_score: float  # Social Media Engagement
    final_score: float  # Gewichteter finaler Score
    source_breakdown: Dict[str, float]  # Score pro Quelle
    
class AdvancedSentimentAnalyzer:
    """Erweiterte Sentiment-Analyse mit mehreren Algorithmen"""
    
    def __init__(self):
        self.config = get_config()
        self.positive_keywords = set(self.config.SENTIMENT_CONFIG['positive_keywords'])
        self.negative_keywords = set(self.config.SENTIMENT_CONFIG['negative_keywords'])
        
        # Erweiterte Keyword-Listen mit Gewichtungen
        self.weighted_keywords = self._build_weighted_keywords()
        self.emoji_sentiment = self._build_emoji_sentiment()
        
    def _build_weighted_keywords(self) -> Dict[str, float]:
        """Erstelle gewichtete Keyword-Liste"""
        weighted = {}
        
        # Starke positive Begriffe
        strong_positive = [
            'moon', 'rocket', 'diamond hands', 'hodl', 'bullish', 'pump',
            'breakout', 'rally', 'surge', 'explode', 'skyrocket'
        ]
        for word in strong_positive:
            weighted[word] = 0.8
        
        # Moderate positive Begriffe
        moderate_positive = [
            'buy', 'long', 'up', 'rise', 'gain', 'profit', 'bull',
            'support', 'resistance', 'bounce', 'recovery'
        ]
        for word in moderate_positive:
            weighted[word] = 0.5
        
        # Schwache positive Begriffe
        weak_positive = [
            'good', 'nice', 'ok', 'decent', 'solid', 'stable'
        ]
        for word in weak_positive:
            weighted[word] = 0.3
        
        # Starke negative Begriffe
        strong_negative = [
            'crash', 'dump', 'rekt', 'bearish', 'short', 'collapse',
            'plummet', 'tank', 'destroy', 'dead', 'scam'
        ]
        for word in strong_negative:
            weighted[word] = -0.8
        
        # Moderate negative Begriffe
        moderate_negative = [
            'sell', 'down', 'fall', 'drop', 'decline', 'bear',
            'correction', 'dip', 'weak', 'loss'
        ]
        for word in moderate_negative:
            weighted[word] = -0.5
        
        # Schwache negative Begriffe
        weak_negative = [
            'bad', 'poor', 'disappointing', 'concerning', 'risky'
        ]
        for word in weak_negative:
            weighted[word] = -0.3
        
        return weighted
    
    def _build_emoji_sentiment(self) -> Dict[str, float]:
        """Erstelle Emoji-Sentiment-Mapping"""
        return {
            '🚀': 0.9, '🌙': 0.8, '💎': 0.7, '🔥': 0.6, '💪': 0.5,
            '😍': 0.6, '😎': 0.4, '👍': 0.3, '✅': 0.3, '💰': 0.7,
            '📈': 0.8, '🟢': 0.5, '🎯': 0.4, '⭐': 0.3, '🏆': 0.6,
            '💀': -0.8, '🔻': -0.6, '📉': -0.8, '🔴': -0.5, '😭': -0.6,
            '😱': -0.7, '💸': -0.5, '⚠️': -0.4, '🚨': -0.6, '👎': -0.4
        }
    
    def analyze_text_sentiment(self, text: str) -> Tuple[float, float]:
        """Analysiere Sentiment eines Textes mit Konfidenz"""
        if not text:
            return 0.0, 0.0
        
        text_lower = text.lower()
        
        # Keyword-basierte Analyse
        keyword_score = self._analyze_keywords(text_lower)
        
        # Emoji-Analyse
        emoji_score = self._analyze_emojis(text)
        
        # Kontext-Analyse (Negation, Verstärkung)
        context_modifier = self._analyze_context(text_lower)
        
        # Kombiniere Scores
        raw_score = (keyword_score * 0.6 + emoji_score * 0.4) * context_modifier
        
        # Berechne Konfidenz basierend auf Textlänge und Keyword-Dichte
        confidence = self._calculate_confidence(text, keyword_score, emoji_score)
        
        # Normalisiere Score auf -1 bis +1
        final_score = max(-1.0, min(1.0, raw_score))
        
        return final_score, confidence
    
    def _analyze_keywords(self, text: str) -> float:
        """Analysiere Keywords im Text"""
        words = re.findall(r'\b\w+\b', text)
        total_score = 0.0
        keyword_count = 0
        
        for word in words:
            if word in self.weighted_keywords:
                total_score += self.weighted_keywords[word]
                keyword_count += 1
        
        if keyword_count == 0:
            return 0.0
        
        # Normalisiere basierend auf Textlänge
        text_length = len(words)
        normalized_score = total_score / max(1, text_length * 0.1)
        
        return normalized_score
    
    def _analyze_emojis(self, text: str) -> float:
        """Analysiere Emojis im Text"""
        total_score = 0.0
        emoji_count = 0
        
        for emoji, score in self.emoji_sentiment.items():
            count = text.count(emoji)
            if count > 0:
                total_score += score * min(count, 3)  # Begrenze Emoji-Spam
                emoji_count += count
        
        if emoji_count == 0:
            return 0.0
        
        return total_score / emoji_count
    
    def _analyze_context(self, text: str) -> float:
        """Analysiere Kontext für Negation und Verstärkung"""
        modifier = 1.0
        
        # Negation-Wörter
        negation_words = ['not', 'no', 'never', 'dont', "don't", 'wont', "won't", 'cant', "can't"]
        for neg_word in negation_words:
            if neg_word in text:
                modifier *= 0.7  # Reduziere Sentiment bei Negation
        
        # Verstärkung-Wörter
        amplifier_words = ['very', 'extremely', 'super', 'really', 'absolutely', 'definitely']
        for amp_word in amplifier_words:
            if amp_word in text:
                modifier *= 1.3  # Verstärke Sentiment
        
        # Fragen reduzieren Konfidenz
        if '?' in text:
            modifier *= 0.8
        
        # Caps Lock verstärkt Emotion
        caps_ratio = sum(1 for c in text if c.isupper()) / max(1, len(text))
        if caps_ratio > 0.3:  # Mehr als 30% Großbuchstaben
            modifier *= 1.2
        
        return max(0.1, min(2.0, modifier))  # Begrenze Modifier
    
    def _calculate_confidence(self, text: str, keyword_score: float, emoji_score: float) -> float:
        """Berechne Konfidenz des Sentiment-Scores"""
        confidence = 0.0
        
        # Textlänge-basierte Konfidenz
        text_length = len(text.split())
        if text_length >= 10:
            confidence += 0.3
        elif text_length >= 5:
            confidence += 0.2
        else:
            confidence += 0.1
        
        # Keyword-basierte Konfidenz
        if abs(keyword_score) > 0.5:
            confidence += 0.4
        elif abs(keyword_score) > 0.2:
            confidence += 0.2
        
        # Emoji-basierte Konfidenz
        if abs(emoji_score) > 0.3:
            confidence += 0.3
        elif abs(emoji_score) > 0.1:
            confidence += 0.1
        
        return min(1.0, confidence)

class SentimentAggregator:
    """Aggregiert Sentiment-Daten für Trading-Signale"""
    
    def __init__(self, db_path: str = '/home/ubuntu/trading_system/trading_data.db'):
        self.db_path = db_path
        self.config = get_config()
        self.analyzer = AdvancedSentimentAnalyzer()
    
    def get_recent_sentiment(self, symbol: str, hours: int = 24) -> List[Dict]:
        """Hole recent sentiment data für Symbol"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT timestamp, text, sentiment_score, source, author, engagement, created_at
                FROM sentiment_data 
                WHERE symbol = ? AND timestamp > ?
                ORDER BY timestamp DESC
            ''', (symbol, cutoff_time))
            
            results = cursor.fetchall()
            
            return [
                {
                    'timestamp': row[0],
                    'text': row[1],
                    'sentiment_score': row[2],
                    'source': row[3],
                    'author': row[4],
                    'engagement': row[5],
                    'created_at': row[6]
                }
                for row in results
            ]
    
    def calculate_aggregated_sentiment(self, symbol: str, hours: int = 24) -> SentimentScore:
        """Berechne aggregierten Sentiment-Score für Symbol"""
        sentiment_data = self.get_recent_sentiment(symbol, hours)
        
        if not sentiment_data:
            return SentimentScore(
                symbol=symbol,
                timestamp=datetime.now(),
                raw_score=0.0,
                confidence=0.0,
                volume_score=0.0,
                engagement_score=0.0,
                final_score=0.0,
                source_breakdown={}
            )
        
        # Berechne verschiedene Metriken
        raw_scores = [data['sentiment_score'] for data in sentiment_data]
        sources = [data['source'] for data in sentiment_data]
        engagements = [data['engagement'] for data in sentiment_data]
        
        # Grundlegende Statistiken
        raw_score = sum(raw_scores) / len(raw_scores)
        volume_score = len(sentiment_data)
        engagement_score = sum(engagements) / max(1, len(engagements))
        
        # Source-Breakdown
        source_breakdown = defaultdict(list)
        for data in sentiment_data:
            source_breakdown[data['source']].append(data['sentiment_score'])
        
        source_scores = {
            source: sum(scores) / len(scores)
            for source, scores in source_breakdown.items()
        }
        
        # Zeitgewichtung (neuere Posts haben höheres Gewicht)
        now = datetime.now()
        weighted_scores = []
        
        for data in sentiment_data:
            timestamp = datetime.fromisoformat(data['timestamp']) if isinstance(data['timestamp'], str) else data['timestamp']
            hours_ago = (now - timestamp).total_seconds() / 3600
            
            # Exponential decay weight
            weight = math.exp(-hours_ago / 12)  # Halbwertszeit von 12 Stunden
            weighted_scores.append(data['sentiment_score'] * weight)
        
        time_weighted_score = sum(weighted_scores) / len(weighted_scores) if weighted_scores else 0.0
        
        # Berechne Konfidenz basierend auf Volumen und Konsistenz
        confidence = self._calculate_aggregate_confidence(raw_scores, volume_score, engagement_score)
        
        # Finale Score-Berechnung
        final_score = (
            time_weighted_score * 0.5 +  # Zeitgewichteter Score
            raw_score * 0.3 +             # Durchschnittlicher Score
            (volume_score / 100) * 0.2    # Volumen-Bonus
        )
        
        # Normalisiere final score
        final_score = max(-1.0, min(1.0, final_score))
        
        return SentimentScore(
            symbol=symbol,
            timestamp=datetime.now(),
            raw_score=raw_score,
            confidence=confidence,
            volume_score=volume_score,
            engagement_score=engagement_score,
            final_score=final_score,
            source_breakdown=source_scores
        )
    
    def _calculate_aggregate_confidence(self, scores: List[float], volume: float, engagement: float) -> float:
        """Berechne Konfidenz für aggregierten Score"""
        confidence = 0.0
        
        # Volumen-basierte Konfidenz
        if volume >= 20:
            confidence += 0.4
        elif volume >= 10:
            confidence += 0.3
        elif volume >= 5:
            confidence += 0.2
        else:
            confidence += 0.1
        
        # Konsistenz-basierte Konfidenz
        if scores:
            score_std = math.sqrt(sum((s - sum(scores)/len(scores))**2 for s in scores) / len(scores))
            consistency = max(0, 1 - score_std)  # Niedrige Standardabweichung = hohe Konsistenz
            confidence += consistency * 0.3
        
        # Engagement-basierte Konfidenz
        if engagement > 100:
            confidence += 0.3
        elif engagement > 50:
            confidence += 0.2
        elif engagement > 10:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def get_sentiment_trend(self, symbol: str, hours: int = 72) -> Dict[str, float]:
        """Analysiere Sentiment-Trend über Zeit"""
        sentiment_data = self.get_recent_sentiment(symbol, hours)
        
        if len(sentiment_data) < 5:
            return {'trend': 0.0, 'momentum': 0.0, 'volatility': 0.0}
        
        # Sortiere nach Zeit
        sentiment_data.sort(key=lambda x: x['timestamp'])
        
        # Berechne gleitende Durchschnitte
        scores = [data['sentiment_score'] for data in sentiment_data]
        
        # Trend-Berechnung (lineare Regression)
        n = len(scores)
        x_values = list(range(n))
        
        # Einfache lineare Regression
        sum_x = sum(x_values)
        sum_y = sum(scores)
        sum_xy = sum(x * y for x, y in zip(x_values, scores))
        sum_x2 = sum(x * x for x in x_values)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        # Momentum (Änderung in letzten 25% der Daten)
        recent_count = max(1, n // 4)
        recent_avg = sum(scores[-recent_count:]) / recent_count
        older_avg = sum(scores[:recent_count]) / recent_count
        momentum = recent_avg - older_avg
        
        # Volatilität (Standardabweichung)
        mean_score = sum(scores) / n
        volatility = math.sqrt(sum((s - mean_score)**2 for s in scores) / n)
        
        return {
            'trend': slope,
            'momentum': momentum,
            'volatility': volatility
        }

def main():
    """Test der Sentiment-Analyse"""
    print("=" * 60)
    print("ADVANCED SENTIMENT ANALYSIS TEST")
    print("=" * 60)
    
    analyzer = AdvancedSentimentAnalyzer()
    
    test_texts = [
        "Bitcoin is going to the moon! 🚀🚀🚀 Diamond hands! 💎",
        "TSLA earnings are looking really good, might buy some calls",
        "This market crash is destroying my portfolio 💀📉",
        "Not sure about AAPL, seems risky right now",
        "HODL strong! This dip is just a buying opportunity 💪",
        "Absolutely bearish on this stock, time to short",
        "GME to the moon! Diamond hands forever! 🚀💎🌙",
        "Market looking weak, might see more correction"
    ]
    
    print("Text Sentiment Analysis:")
    print("-" * 60)
    
    for text in test_texts:
        score, confidence = analyzer.analyze_text_sentiment(text)
        sentiment_label = "BULLISH" if score > 0.1 else "BEARISH" if score < -0.1 else "NEUTRAL"
        
        print(f"Text: {text}")
        print(f"Score: {score:.3f} | Confidence: {confidence:.3f} | {sentiment_label}")
        print()
    
    # Test Aggregation mit Dummy-Daten
    print("=" * 60)
    print("SENTIMENT AGGREGATION TEST")
    print("=" * 60)
    
    aggregator = SentimentAggregator()
    
    # Test mit verfügbaren Daten
    try:
        sentiment_score = aggregator.calculate_aggregated_sentiment('BTC-USD', hours=24)
        
        print(f"Symbol: {sentiment_score.symbol}")
        print(f"Raw Score: {sentiment_score.raw_score:.3f}")
        print(f"Final Score: {sentiment_score.final_score:.3f}")
        print(f"Confidence: {sentiment_score.confidence:.3f}")
        print(f"Volume: {sentiment_score.volume_score}")
        print(f"Engagement: {sentiment_score.engagement_score:.1f}")
        print(f"Source Breakdown: {sentiment_score.source_breakdown}")
        
        # Trend-Analyse
        trend_data = aggregator.get_sentiment_trend('BTC-USD', hours=72)
        print(f"\nTrend Analysis:")
        print(f"  Trend: {trend_data['trend']:.4f}")
        print(f"  Momentum: {trend_data['momentum']:.4f}")
        print(f"  Volatility: {trend_data['volatility']:.4f}")
        
    except Exception as e:
        print(f"Error in aggregation test: {e}")

if __name__ == "__main__":
    main()

