#!/usr/bin/env python3
"""
Trading System - Enhanced Data Collector Module v2
Verbesserte Datensammlung mit besserer Symbol-Erkennung und Scheduling
"""

import sys
import re
import time
import sqlite3
import logging
import schedule
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass

sys.path.append('/opt/.manus/.sandbox-runtime')
from data_api import ApiClient
from config import get_config, get_all_symbols, get_symbol_aliases

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/trading_system/data_collector_v2.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class MarketData:
    """Datenklasse für Marktdaten"""
    symbol: str
    timestamp: datetime
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int
    source: str

@dataclass
class SentimentData:
    """Datenklasse für Sentiment-Daten"""
    symbol: str
    timestamp: datetime
    text: str
    sentiment_score: float
    source: str
    author: str = ""
    engagement: int = 0
    confidence: float = 0.0

class EnhancedSymbolExtractor:
    """Verbesserte Symbol-Erkennung in Texten"""
    
    def __init__(self):
        self.config = get_config()
        self.symbol_patterns = self._build_symbol_patterns()
    
    def _build_symbol_patterns(self) -> Dict[str, List[str]]:
        """Erstelle Regex-Patterns für Symbol-Erkennung"""
        patterns = {}
        
        for symbol in get_all_symbols():
            symbol_patterns = []
            aliases = get_symbol_aliases(symbol)
            
            for alias in aliases:
                # Exakte Matches mit Wort-Grenzen
                symbol_patterns.append(rf'\b{re.escape(alias.upper())}\b')
                # Dollar-Symbol Prefix
                symbol_patterns.append(rf'\${re.escape(alias.upper())}\b')
                # Hashtag-Format
                symbol_patterns.append(rf'#{re.escape(alias.upper())}\b')
            
            patterns[symbol] = symbol_patterns
        
        return patterns
    
    def extract_symbols(self, text: str) -> Set[str]:
        """Extrahiere alle relevanten Symbole aus Text"""
        if not text:
            return set()
        
        text_upper = text.upper()
        found_symbols = set()
        
        for symbol, patterns in self.symbol_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_upper):
                    found_symbols.add(symbol)
                    break  # Ein Match reicht pro Symbol
        
        return found_symbols
    
    def get_symbol_confidence(self, text: str, symbol: str) -> float:
        """Berechne Konfidenz-Score für Symbol-Erkennung"""
        if not text:
            return 0.0
        
        text_upper = text.upper()
        confidence = 0.0
        
        aliases = get_symbol_aliases(symbol)
        
        for alias in aliases:
            alias_upper = alias.upper()
            
            # Exakte Matches (höchste Konfidenz)
            if f"${alias_upper}" in text_upper:
                confidence = max(confidence, 0.9)
            elif f"#{alias_upper}" in text_upper:
                confidence = max(confidence, 0.8)
            elif f" {alias_upper} " in text_upper:
                confidence = max(confidence, 0.7)
            elif alias_upper in text_upper:
                confidence = max(confidence, 0.5)
        
        # Reduziere Konfidenz bei sehr kurzen Texten
        if len(text) < 50:
            confidence *= 0.8
        
        return confidence

class EnhancedRedditCollector:
    """Verbesserte Reddit-Datensammlung"""
    
    def __init__(self):
        self.client = ApiClient()
        self.config = get_config()
        self.symbol_extractor = EnhancedSymbolExtractor()
        self.logger = logging.getLogger(f"{__name__}.Reddit")
    
    def collect_data(self, limit: int = None) -> List[SentimentData]:
        """Sammle Reddit-Posts für Sentiment-Analyse"""
        if limit is None:
            limit = self.config.DATA_COLLECTION['reddit_post_limit']
        
        sentiment_data = []
        target_subreddits = ['wallstreetbets', 'cryptocurrency', 'investing', 'stocks']
        
        for subreddit in target_subreddits:
            try:
                result = self.client.call_api('Reddit/AccessAPI', query={
                    'subreddit': subreddit,
                    'limit': str(limit)
                })
                
                if result and 'posts' in result:
                    posts = result['posts']
                    
                    for post_wrapper in posts:
                        post = post_wrapper.get('data', {})
                        title = post.get('title', '')
                        selftext = post.get('selftext', '')
                        text = f"{title} {selftext}".strip()
                        
                        # Begrenze Text-Länge
                        max_length = self.config.DATA_COLLECTION['max_text_length']
                        if len(text) > max_length:
                            text = text[:max_length] + "..."
                        
                        # Extrahiere relevante Symbole
                        found_symbols = self.symbol_extractor.extract_symbols(text)
                        
                        if found_symbols and text and len(text) > 20:  # Mindest-Text-Länge
                            for symbol in found_symbols:
                                confidence = self.symbol_extractor.get_symbol_confidence(text, symbol)
                                
                                sentiment_data.append(SentimentData(
                                    symbol=symbol,
                                    timestamp=datetime.fromtimestamp(post.get('created_utc', 0)),
                                    text=text,
                                    sentiment_score=0.0,  # Wird später berechnet
                                    source=f'reddit_{subreddit}',
                                    author=post.get('author', ''),
                                    engagement=post.get('score', 0) + post.get('num_comments', 0),
                                    confidence=confidence
                                ))
                    
                    self.logger.info(f"Collected {len(posts)} posts from r/{subreddit}")
                    
            except Exception as e:
                self.logger.error(f"Error collecting from r/{subreddit}: {str(e)}")
        
        # Filtere nach Konfidenz
        high_confidence_data = [
            data for data in sentiment_data 
            if data.confidence >= 0.6  # Nur hohe Konfidenz
        ]
        
        self.logger.info(f"Extracted {len(high_confidence_data)} high-confidence sentiment data points")
        return high_confidence_data

class EnhancedTwitterCollector:
    """Verbesserte Twitter-Datensammlung"""
    
    def __init__(self):
        self.client = ApiClient()
        self.config = get_config()
        self.symbol_extractor = EnhancedSymbolExtractor()
        self.logger = logging.getLogger(f"{__name__}.Twitter")
    
    def collect_data(self, symbols: List[str] = None) -> List[SentimentData]:
        """Sammle Twitter-Daten für Sentiment-Analyse"""
        if symbols is None:
            symbols = get_all_symbols()[:10]  # Begrenze auf 10 Symbole für API-Limits
        
        sentiment_data = []
        
        for symbol in symbols:
            try:
                # Erstelle bessere Suchanfrage
                aliases = get_symbol_aliases(symbol)
                query_terms = []
                
                for alias in aliases[:3]:  # Max 3 Aliases pro Symbol
                    query_terms.append(f"${alias}")
                    query_terms.append(alias)
                
                query = " OR ".join(query_terms[:6])  # Max 6 Suchbegriffe
                
                result = self.client.call_api('Twitter/search_twitter', query={
                    'query': query
                })
                
                if result and 'tweets' in result:
                    tweets = result['tweets']
                    
                    for tweet in tweets:
                        text = tweet.get('text', '')
                        if text and len(text) > 20:  # Mindest-Text-Länge
                            
                            # Extrahiere Symbole aus Tweet
                            found_symbols = self.symbol_extractor.extract_symbols(text)
                            
                            for found_symbol in found_symbols:
                                confidence = self.symbol_extractor.get_symbol_confidence(text, found_symbol)
                                
                                if confidence >= 0.6:  # Nur hohe Konfidenz
                                    sentiment_data.append(SentimentData(
                                        symbol=found_symbol,
                                        timestamp=datetime.now(),
                                        text=text[:280],  # Twitter-Limit
                                        sentiment_score=0.0,
                                        source='twitter',
                                        author=tweet.get('user', {}).get('username', ''),
                                        engagement=tweet.get('public_metrics', {}).get('like_count', 0),
                                        confidence=confidence
                                    ))
                    
                    self.logger.info(f"Collected {len(tweets)} tweets for {symbol}")
                    
                # Rate limiting
                time.sleep(self.config.API_CONFIG['rate_limit_delay'])
                
            except Exception as e:
                self.logger.error(f"Error collecting tweets for {symbol}: {str(e)}")
        
        self.logger.info(f"Total Twitter sentiment data points: {len(sentiment_data)}")
        return sentiment_data

class BasicSentimentAnalyzer:
    """Einfache Sentiment-Analyse basierend auf Keywords"""
    
    def __init__(self):
        self.config = get_config()
        self.positive_keywords = set(self.config.SENTIMENT_CONFIG['positive_keywords'])
        self.negative_keywords = set(self.config.SENTIMENT_CONFIG['negative_keywords'])
    
    def analyze_sentiment(self, text: str) -> float:
        """Analysiere Sentiment eines Textes (-1 bis +1)"""
        if not text:
            return 0.0
        
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        positive_count = sum(1 for word in words if word in self.positive_keywords)
        negative_count = sum(1 for word in words if word in self.negative_keywords)
        
        total_words = len(words)
        if total_words == 0:
            return 0.0
        
        # Berechne Sentiment-Score
        positive_ratio = positive_count / total_words
        negative_ratio = negative_count / total_words
        
        sentiment_score = positive_ratio - negative_ratio
        
        # Normalisiere auf -1 bis +1
        sentiment_score = max(-1.0, min(1.0, sentiment_score * 10))
        
        return sentiment_score

class EnhancedTradingDataCollector:
    """Verbesserte Hauptklasse für koordinierte Datensammlung"""
    
    def __init__(self):
        self.config = get_config()
        self.reddit_collector = EnhancedRedditCollector()
        self.twitter_collector = EnhancedTwitterCollector()
        self.sentiment_analyzer = BasicSentimentAnalyzer()
        self.db_manager = self._init_database()
        self.logger = logging.getLogger(__name__)
    
    def _init_database(self):
        """Initialisiere erweiterte Datenbank"""
        from data_collector import DatabaseManager
        return DatabaseManager()
    
    def collect_all_data(self) -> Dict[str, Any]:
        """Sammle alle Daten"""
        symbols = get_all_symbols()
        
        results = {
            'timestamp': datetime.now(),
            'symbols_count': len(symbols),
            'market_data_count': 0,
            'sentiment_data_count': 0,
            'errors': []
        }
        
        try:
            # Sammle Marktdaten (nur für aktive Symbole)
            active_symbols = symbols[:10]  # Begrenze für Demo
            self.logger.info(f"Collecting market data for {len(active_symbols)} symbols")
            
            from data_collector import YahooFinanceCollector
            yahoo_collector = YahooFinanceCollector()
            market_data = yahoo_collector.collect_data(
                active_symbols, 
                interval=self.config.DATA_COLLECTION['market_data_interval'],
                range_period=self.config.DATA_COLLECTION['market_data_range']
            )
            results['market_data_count'] = self.db_manager.save_market_data(market_data)
            
            # Sammle und analysiere Sentiment-Daten
            self.logger.info("Collecting sentiment data from Reddit and Twitter")
            
            reddit_sentiment = self.reddit_collector.collect_data()
            twitter_sentiment = self.twitter_collector.collect_data(active_symbols)
            
            # Führe Sentiment-Analyse durch
            all_sentiment = reddit_sentiment + twitter_sentiment
            
            for sentiment_data in all_sentiment:
                sentiment_data.sentiment_score = self.sentiment_analyzer.analyze_sentiment(sentiment_data.text)
            
            # Speichere nur Sentiment-Daten mit signifikantem Score
            significant_sentiment = [
                data for data in all_sentiment 
                if abs(data.sentiment_score) > self.config.SENTIMENT_CONFIG['neutral_threshold']
            ]
            
            results['sentiment_data_count'] = self.db_manager.save_sentiment_data(significant_sentiment)
            
            self.logger.info(f"Data collection completed successfully")
            
        except Exception as e:
            error_msg = f"Error in data collection: {str(e)}"
            self.logger.error(error_msg)
            results['errors'].append(error_msg)
        
        return results
    
    def start_scheduled_collection(self):
        """Starte geplante Datensammlung"""
        frequency = self.config.DATA_COLLECTION['collection_frequency_minutes']
        
        schedule.every(frequency).minutes.do(self.collect_all_data)
        
        self.logger.info(f"Started scheduled data collection every {frequency} minutes")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Prüfe jede Minute

def main():
    """Hauptfunktion für Testing"""
    collector = EnhancedTradingDataCollector()
    
    print("=" * 60)
    print("ENHANCED TRADING DATA COLLECTOR v2")
    print("=" * 60)
    
    # Einmalige Datensammlung für Test
    results = collector.collect_all_data()
    
    print(f"Zeitstempel: {results['timestamp']}")
    print(f"Überwachte Symbole: {results['symbols_count']}")
    print(f"Marktdaten gesammelt: {results['market_data_count']}")
    print(f"Sentiment-Daten gesammelt: {results['sentiment_data_count']}")
    
    if results['errors']:
        print(f"Fehler: {len(results['errors'])}")
        for error in results['errors']:
            print(f"  - {error}")
    
    # Test Symbol-Extraktor
    print("\n" + "=" * 60)
    print("SYMBOL EXTRACTION TEST")
    print("=" * 60)
    
    extractor = EnhancedSymbolExtractor()
    test_texts = [
        "I'm bullish on $BTC and think Tesla will moon soon!",
        "AAPL earnings looking good, might buy some calls",
        "Bitcoin is crashing, time to short BTC-USD",
        "Diamond hands on GME and AMC to the moon! 🚀",
        "S&P 500 looking weak, SPY puts might print"
    ]
    
    for text in test_texts:
        symbols = extractor.extract_symbols(text)
        print(f"Text: {text}")
        print(f"Symbols: {symbols}")
        
        for symbol in symbols:
            confidence = extractor.get_symbol_confidence(text, symbol)
            print(f"  {symbol}: {confidence:.2f} confidence")
        print()

if __name__ == "__main__":
    main()

