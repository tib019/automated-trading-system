#!/usr/bin/env python3
"""
Trading System - Configuration Module
Zentrale Konfiguration für das automatisierte Trading-System
"""

from typing import Dict, List, Any
from dataclasses import dataclass
import json

@dataclass
class TradingConfig:
    """Hauptkonfiguration für Trading-System"""
    
    # Überwachte Assets
    CRYPTO_SYMBOLS = [
        'BTC-USD', 'ETH-USD', 'ADA-USD', 'DOT-USD', 'LINK-USD',
        'SOL-USD', 'AVAX-USD', 'MATIC-USD', 'ATOM-USD', 'XRP-USD'
    ]
    
    STOCK_SYMBOLS = [
        'AAPL', 'TSLA', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META',
        'NFLX', 'AMD', 'BABA', 'PLTR', 'GME', 'AMC', 'SPY', 'QQQ'
    ]
    
    # Symbol-Aliases für bessere Erkennung in Social Media
    SYMBOL_ALIASES = {
        'BTC-USD': ['BTC', 'BITCOIN', 'BITCOIN'],
        'ETH-USD': ['ETH', 'ETHEREUM', 'ETHER'],
        'TSLA': ['TESLA', 'ELON'],
        'AAPL': ['APPLE', 'IPHONE'],
        'MSFT': ['MICROSOFT', 'MSFT'],
        'GOOGL': ['GOOGLE', 'ALPHABET'],
        'AMZN': ['AMAZON', 'BEZOS'],
        'NVDA': ['NVIDIA', 'AI', 'GPU'],
        'META': ['FACEBOOK', 'META', 'ZUCK'],
        'GME': ['GAMESTOP', 'GME', 'DIAMOND HANDS'],
        'AMC': ['AMC', 'MOVIE THEATER'],
        'SPY': ['SPY', 'S&P500', 'S&P 500'],
        'QQQ': ['QQQ', 'NASDAQ', 'TECH']
    }
    
    # Datensammlung-Einstellungen
    DATA_COLLECTION = {
        'market_data_interval': '1h',  # 1m, 5m, 15m, 30m, 1h, 1d
        'market_data_range': '1d',     # 1d, 5d, 1mo, 3mo, 6mo, 1y
        'reddit_post_limit': 50,
        'twitter_search_limit': 100,
        'collection_frequency_minutes': 15,
        'max_text_length': 500
    }
    
    # Sentiment-Analyse-Einstellungen
    SENTIMENT_CONFIG = {
        'positive_keywords': [
            'moon', 'bullish', 'buy', 'long', 'pump', 'rocket', 'gains',
            'profit', 'bull', 'up', 'rise', 'surge', 'breakout', 'rally'
        ],
        'negative_keywords': [
            'bear', 'bearish', 'sell', 'short', 'dump', 'crash', 'loss',
            'down', 'fall', 'drop', 'decline', 'correction', 'dip'
        ],
        'neutral_threshold': 0.1,  # -0.1 bis +0.1 als neutral
        'strong_sentiment_threshold': 0.5  # > 0.5 oder < -0.5 als stark
    }
    
    # Risikomanagement-Einstellungen
    RISK_MANAGEMENT = {
        'max_position_size_percent': 2.0,  # Max 2% des Portfolios pro Position
        'daily_loss_limit_percent': 10.0,  # Stop bei 10% Tagesverlust
        'max_open_positions': 5,
        'stop_loss_percent': 2.0,  # Standard Stop-Loss bei 2%
        'take_profit_percent': 6.0,  # Standard Take-Profit bei 6%
        'trailing_stop_percent': 1.0
    }
    
    # Signal-Generierung-Einstellungen
    SIGNAL_CONFIG = {
        'min_sentiment_score': 0.3,  # Minimum Sentiment für Signal
        'min_volume_increase': 1.5,  # Mindest-Volumen-Anstieg (1.5x)
        'price_change_threshold': 0.02,  # 2% Preisänderung für Signal
        'sentiment_weight': 0.4,  # Gewichtung Sentiment vs. Technische Analyse
        'technical_weight': 0.6,
        'signal_cooldown_hours': 4  # Mindestabstand zwischen Signalen
    }
    
    # Backtesting-Einstellungen
    BACKTESTING = {
        'initial_capital': 10000,  # $10,000 Startkapital
        'commission_percent': 0.1,  # 0.1% Handelsgebühren
        'slippage_percent': 0.05,  # 0.05% Slippage
        'lookback_days': 90,  # 90 Tage für Backtesting
        'min_trades_for_validation': 20
    }
    
    # API-Einstellungen
    API_CONFIG = {
        'rate_limit_delay': 1.0,  # Sekunden zwischen API-Calls
        'max_retries': 3,
        'timeout_seconds': 30,
        'cache_duration_minutes': 5
    }
    
    # Datenbank-Einstellungen
    DATABASE = {
        'path': '/home/ubuntu/trading_system/trading_data.db',
        'backup_frequency_hours': 24,
        'cleanup_days': 30  # Lösche Daten älter als 30 Tage
    }
    
    # Logging-Einstellungen
    LOGGING = {
        'level': 'INFO',
        'file_path': '/home/ubuntu/trading_system/trading_system.log',
        'max_file_size_mb': 10,
        'backup_count': 5
    }
    
    # Broker-Einstellungen (für später)
    BROKER_CONFIG = {
        'demo_mode': True,  # Immer mit Demo starten
        'binance_testnet': True,
        'ibkr_paper_trading': True,
        'max_daily_trades': 10,
        'order_timeout_minutes': 5,
        'binance': {
            'enabled': False,
            'api_key': '',
            'api_secret': '',
            'testnet': True,
            'base_url': 'https://testnet.binance.vision'
        }
    }
    
    # Webhook-Einstellungen
    WEBHOOK_CONFIG = {
        'secret': 'default_secret',
        'enabled_brokers': ['PAPER_TRADING'],
        'max_requests_per_minute': 60,
        'require_signature': False,
        'allowed_ips': [],  # Leer = alle IPs erlaubt
        'log_all_requests': True
    }

class ConfigManager:
    """Verwaltet Konfiguration und ermöglicht dynamische Updates"""
    
    def __init__(self, config_file: str = '/home/ubuntu/trading_system/config.json'):
        self.config_file = config_file
        self.config = TradingConfig()
        self.load_config()
    
    def load_config(self):
        """Lade Konfiguration aus JSON-Datei falls vorhanden"""
        try:
            with open(self.config_file, 'r') as f:
                custom_config = json.load(f)
                
            # Update Konfiguration mit custom values
            for section, values in custom_config.items():
                if hasattr(self.config, section):
                    current_value = getattr(self.config, section)
                    if isinstance(current_value, dict):
                        current_value.update(values)
                    else:
                        setattr(self.config, section, values)
                        
        except FileNotFoundError:
            # Erstelle Standard-Konfigurationsdatei
            self.save_config()
        except Exception as e:
            print(f"Error loading config: {e}")
    
    def save_config(self):
        """Speichere aktuelle Konfiguration in JSON-Datei"""
        config_dict = {}
        
        for attr_name in dir(self.config):
            if not attr_name.startswith('_'):
                attr_value = getattr(self.config, attr_name)
                if not callable(attr_value):
                    config_dict[attr_name] = attr_value
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config_dict, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get_all_symbols(self) -> List[str]:
        """Erhalte alle überwachten Symbole"""
        return self.config.CRYPTO_SYMBOLS + self.config.STOCK_SYMBOLS
    
    def get_symbol_aliases(self, symbol: str) -> List[str]:
        """Erhalte Aliases für ein Symbol"""
        aliases = self.config.SYMBOL_ALIASES.get(symbol, [])
        return [symbol] + aliases
    
    def is_crypto_symbol(self, symbol: str) -> bool:
        """Prüfe ob Symbol eine Kryptowährung ist"""
        return symbol in self.config.CRYPTO_SYMBOLS
    
    def is_stock_symbol(self, symbol: str) -> bool:
        """Prüfe ob Symbol eine Aktie ist"""
        return symbol in self.config.STOCK_SYMBOLS
    
    def update_config(self, section: str, key: str, value: Any):
        """Update einzelnen Konfigurationswert"""
        if hasattr(self.config, section):
            section_config = getattr(self.config, section)
            if isinstance(section_config, dict):
                section_config[key] = value
                self.save_config()
            else:
                print(f"Section {section} is not a dictionary")
        else:
            print(f"Section {section} not found in config")

# Globale Konfiguration-Instanz
config_manager = ConfigManager()

def get_config() -> TradingConfig:
    """Erhalte aktuelle Konfiguration"""
    return config_manager.config

def get_all_symbols() -> List[str]:
    """Erhalte alle überwachten Symbole"""
    return config_manager.get_all_symbols()

def get_symbol_aliases(symbol: str) -> List[str]:
    """Erhalte Aliases für ein Symbol"""
    return config_manager.get_symbol_aliases(symbol)

if __name__ == "__main__":
    # Test der Konfiguration
    config = get_config()
    
    print("Trading System Configuration")
    print("=" * 40)
    print(f"Crypto Symbols: {len(config.CRYPTO_SYMBOLS)}")
    print(f"Stock Symbols: {len(config.STOCK_SYMBOLS)}")
    print(f"Total Symbols: {len(get_all_symbols())}")
    
    print(f"\nRisk Management:")
    print(f"  Max Position Size: {config.RISK_MANAGEMENT['max_position_size_percent']}%")
    print(f"  Daily Loss Limit: {config.RISK_MANAGEMENT['daily_loss_limit_percent']}%")
    
    print(f"\nData Collection:")
    print(f"  Market Data Interval: {config.DATA_COLLECTION['market_data_interval']}")
    print(f"  Collection Frequency: {config.DATA_COLLECTION['collection_frequency_minutes']} min")
    
    # Test Symbol-Aliases
    print(f"\nSymbol Aliases for BTC-USD: {get_symbol_aliases('BTC-USD')}")
    print(f"Symbol Aliases for TSLA: {get_symbol_aliases('TSLA')}")
    
    print(f"\nConfiguration saved to: {config_manager.config_file}")

