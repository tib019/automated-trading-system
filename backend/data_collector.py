#!/usr/bin/env python3
"""
Trading System - Data Collector Module
Sammelt Daten von verschiedenen Quellen für automatisierte Trading-Entscheidungen
"""

import sys
import json
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod

sys.path.append('/opt/.manus/.sandbox-runtime')
from data_api import ApiClient

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/trading_system/data_collector.log'),
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

class DataCollector(ABC):
    """Abstrakte Basisklasse für Datensammler"""
    
    def __init__(self, name: str):
        self.name = name
        self.client = ApiClient()
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    @abstractmethod
    def collect_data(self, symbols: List[str], **kwargs) -> List[Any]:
        """Sammle Daten für gegebene Symbole"""
        pass
    
    def log_collection(self, symbol: str, count: int, data_type: str):
        """Logge Datensammlung"""
        self.logger.info(f"Collected {count} {data_type} for {symbol}")

class YahooFinanceCollector(DataCollector):
    """Sammelt Marktdaten von Yahoo Finance"""
    
    def __init__(self):
        super().__init__("YahooFinance")
    
    def collect_data(self, symbols: List[str], interval: str = '1h', range_period: str = '1d') -> List[MarketData]:
        """Sammle Marktdaten für Symbole"""
        market_data = []
        
        for symbol in symbols:
            try:
                result = self.client.call_api('YahooFinance/get_stock_chart', query={
                    'symbol': symbol,
                    'region': 'US',
                    'interval': interval,
                    'range': range_period,
                    'includeAdjustedClose': True
                })
                
                if result and 'chart' in result and result['chart']['result']:
                    chart_result = result['chart']['result'][0]
                    timestamps = chart_result.get('timestamp', [])
                    quotes = chart_result['indicators']['quote'][0]
                    
                    for i, timestamp in enumerate(timestamps):
                        if (quotes['open'][i] is not None and 
                            quotes['high'][i] is not None and 
                            quotes['low'][i] is not None and 
                            quotes['close'][i] is not None and
                            quotes['volume'][i] is not None):
                            
                            market_data.append(MarketData(
                                symbol=symbol,
                                timestamp=datetime.fromtimestamp(timestamp),
                                open_price=quotes['open'][i],
                                high_price=quotes['high'][i],
                                low_price=quotes['low'][i],
                                close_price=quotes['close'][i],
                                volume=quotes['volume'][i],
                                source='yahoo_finance'
                            ))
                    
                    self.log_collection(symbol, len(timestamps), "market data points")
                    
            except Exception as e:
                self.logger.error(f"Error collecting data for {symbol}: {str(e)}")
        
        return market_data

class RedditCollector(DataCollector):
    """Sammelt Sentiment-Daten von Reddit"""
    
    def __init__(self):
        super().__init__("Reddit")
        self.target_subreddits = ['wallstreetbets', 'cryptocurrency', 'investing']
    
    def collect_data(self, symbols: List[str], limit: int = 25) -> List[SentimentData]:
        """Sammle Reddit-Posts für Sentiment-Analyse"""
        sentiment_data = []
        
        for subreddit in self.target_subreddits:
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
                        
                        # Prüfe ob Post trading-relevante Symbole enthält
                        relevant_symbols = self._extract_symbols(text, symbols)
                        
                        if relevant_symbols and text:
                            for symbol in relevant_symbols:
                                sentiment_data.append(SentimentData(
                                    symbol=symbol,
                                    timestamp=datetime.fromtimestamp(post.get('created_utc', 0)),
                                    text=text[:500],  # Begrenze Text-Länge
                                    sentiment_score=0.0,  # Wird später berechnet
                                    source=f'reddit_{subreddit}',
                                    author=post.get('author', ''),
                                    engagement=post.get('score', 0) + post.get('num_comments', 0)
                                ))
                    
                    self.log_collection(subreddit, len(posts), "posts")
                    
            except Exception as e:
                self.logger.error(f"Error collecting from r/{subreddit}: {str(e)}")
        
        return sentiment_data
    
    def _extract_symbols(self, text: str, symbols: List[str]) -> List[str]:
        """Extrahiere relevante Symbole aus Text"""
        text_upper = text.upper()
        found_symbols = []
        
        for symbol in symbols:
            # Suche nach $SYMBOL oder SYMBOL
            if f"${symbol.upper()}" in text_upper or f" {symbol.upper()} " in text_upper:
                found_symbols.append(symbol)
        
        return found_symbols

class TwitterCollector(DataCollector):
    """Sammelt Sentiment-Daten von Twitter"""
    
    def __init__(self):
        super().__init__("Twitter")
    
    def collect_data(self, symbols: List[str]) -> List[SentimentData]:
        """Sammle Twitter-Daten für Sentiment-Analyse"""
        sentiment_data = []
        
        for symbol in symbols:
            try:
                # Suche nach Symbol-spezifischen Tweets
                query = f"${symbol} OR {symbol} trading OR {symbol} stock"
                
                result = self.client.call_api('Twitter/search_twitter', query={
                    'query': query
                })
                
                if result and 'tweets' in result:
                    tweets = result['tweets']
                    
                    for tweet in tweets:
                        text = tweet.get('text', '')
                        if text:
                            sentiment_data.append(SentimentData(
                                symbol=symbol,
                                timestamp=datetime.now(),  # Twitter API liefert möglicherweise kein Timestamp
                                text=text[:280],  # Twitter-Limit
                                sentiment_score=0.0,  # Wird später berechnet
                                source='twitter',
                                author=tweet.get('user', {}).get('username', ''),
                                engagement=tweet.get('public_metrics', {}).get('like_count', 0)
                            ))
                    
                    self.log_collection(symbol, len(tweets), "tweets")
                    
            except Exception as e:
                self.logger.error(f"Error collecting tweets for {symbol}: {str(e)}")
        
        return sentiment_data

class DatabaseManager:
    """Verwaltet SQLite-Datenbank für gesammelte Daten"""
    
    def __init__(self, db_path: str = '/home/ubuntu/trading_system/trading_data.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialisiere Datenbank-Tabellen"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Marktdaten-Tabelle
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS market_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    open_price REAL NOT NULL,
                    high_price REAL NOT NULL,
                    low_price REAL NOT NULL,
                    close_price REAL NOT NULL,
                    volume INTEGER NOT NULL,
                    source TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, timestamp, source)
                )
            ''')
            
            # Sentiment-Daten-Tabelle
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sentiment_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    text TEXT NOT NULL,
                    sentiment_score REAL DEFAULT 0.0,
                    source TEXT NOT NULL,
                    author TEXT DEFAULT '',
                    engagement INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, timestamp, text, source)
                )
            ''')
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    def save_market_data(self, market_data: List[MarketData]) -> int:
        """Speichere Marktdaten in Datenbank"""
        saved_count = 0
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for data in market_data:
                try:
                    cursor.execute('''
                        INSERT OR IGNORE INTO market_data 
                        (symbol, timestamp, open_price, high_price, low_price, close_price, volume, source)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        data.symbol, data.timestamp, data.open_price, data.high_price,
                        data.low_price, data.close_price, data.volume, data.source
                    ))
                    
                    if cursor.rowcount > 0:
                        saved_count += 1
                        
                except sqlite3.Error as e:
                    logger.error(f"Error saving market data: {e}")
            
            conn.commit()
        
        logger.info(f"Saved {saved_count} market data records")
        return saved_count
    
    def save_sentiment_data(self, sentiment_data: List[SentimentData]) -> int:
        """Speichere Sentiment-Daten in Datenbank"""
        saved_count = 0
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for data in sentiment_data:
                try:
                    cursor.execute('''
                        INSERT OR IGNORE INTO sentiment_data 
                        (symbol, timestamp, text, sentiment_score, source, author, engagement)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        data.symbol, data.timestamp, data.text, data.sentiment_score,
                        data.source, data.author, data.engagement
                    ))
                    
                    if cursor.rowcount > 0:
                        saved_count += 1
                        
                except sqlite3.Error as e:
                    logger.error(f"Error saving sentiment data: {e}")
            
            conn.commit()
        
        logger.info(f"Saved {saved_count} sentiment data records")
        return saved_count

class TradingDataCollector:
    """Hauptklasse für koordinierte Datensammlung"""
    
    def __init__(self):
        self.yahoo_collector = YahooFinanceCollector()
        self.reddit_collector = RedditCollector()
        self.twitter_collector = TwitterCollector()
        self.db_manager = DatabaseManager()
        self.logger = logging.getLogger(__name__)
    
    def collect_all_data(self, symbols: List[str]) -> Dict[str, Any]:
        """Sammle alle Daten für gegebene Symbole"""
        results = {
            'timestamp': datetime.now(),
            'symbols': symbols,
            'market_data_count': 0,
            'sentiment_data_count': 0,
            'errors': []
        }
        
        try:
            # Sammle Marktdaten
            self.logger.info(f"Collecting market data for {len(symbols)} symbols")
            market_data = self.yahoo_collector.collect_data(symbols, interval='1h', range_period='1d')
            results['market_data_count'] = self.db_manager.save_market_data(market_data)
            
            # Sammle Reddit-Sentiment
            self.logger.info("Collecting Reddit sentiment data")
            reddit_sentiment = self.reddit_collector.collect_data(symbols)
            
            # Sammle Twitter-Sentiment
            self.logger.info("Collecting Twitter sentiment data")
            twitter_sentiment = self.twitter_collector.collect_data(symbols)
            
            # Kombiniere Sentiment-Daten
            all_sentiment = reddit_sentiment + twitter_sentiment
            results['sentiment_data_count'] = self.db_manager.save_sentiment_data(all_sentiment)
            
            self.logger.info(f"Data collection completed: {results['market_data_count']} market data, {results['sentiment_data_count']} sentiment data")
            
        except Exception as e:
            error_msg = f"Error in data collection: {str(e)}"
            self.logger.error(error_msg)
            results['errors'].append(error_msg)
        
        return results

def main():
    """Hauptfunktion für Testing"""
    # Test-Symbole
    test_symbols = ['AAPL', 'TSLA', 'BTC-USD', 'ETH-USD', 'MSFT']
    
    collector = TradingDataCollector()
    results = collector.collect_all_data(test_symbols)
    
    print("=" * 50)
    print("DATENSAMMLUNG ABGESCHLOSSEN")
    print("=" * 50)
    print(f"Zeitstempel: {results['timestamp']}")
    print(f"Symbole: {', '.join(results['symbols'])}")
    print(f"Marktdaten gesammelt: {results['market_data_count']}")
    print(f"Sentiment-Daten gesammelt: {results['sentiment_data_count']}")
    
    if results['errors']:
        print(f"Fehler: {len(results['errors'])}")
        for error in results['errors']:
            print(f"  - {error}")

if __name__ == "__main__":
    main()

