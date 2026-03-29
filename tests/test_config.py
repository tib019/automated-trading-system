"""Unit and functional tests for TradingConfig."""
import pytest
from unittest.mock import patch


class TestTradingConfig:
    def _get_config(self):
        from config import TradingConfig
        return TradingConfig()

    def test_crypto_symbols_not_empty(self):
        cfg = self._get_config()
        assert len(cfg.CRYPTO_SYMBOLS) > 0
        assert 'BTC-USD' in cfg.CRYPTO_SYMBOLS
        assert 'ETH-USD' in cfg.CRYPTO_SYMBOLS

    def test_stock_symbols_not_empty(self):
        cfg = self._get_config()
        assert len(cfg.STOCK_SYMBOLS) > 0
        assert 'AAPL' in cfg.STOCK_SYMBOLS
        assert 'TSLA' in cfg.STOCK_SYMBOLS

    def test_symbol_aliases_covers_crypto(self):
        cfg = self._get_config()
        assert 'BTC-USD' in cfg.SYMBOL_ALIASES
        assert 'ETH-USD' in cfg.SYMBOL_ALIASES

    def test_data_collection_has_required_keys(self):
        cfg = self._get_config()
        dc = cfg.DATA_COLLECTION
        assert 'market_data_interval' in dc
        assert 'reddit_post_limit' in dc
        assert 'collection_frequency_minutes' in dc

    def test_backtesting_initial_capital(self):
        cfg = self._get_config()
        assert cfg.BACKTESTING['initial_capital'] > 0

    def test_no_duplicate_crypto_symbols(self):
        cfg = self._get_config()
        assert len(cfg.CRYPTO_SYMBOLS) == len(set(cfg.CRYPTO_SYMBOLS))

    def test_no_duplicate_stock_symbols(self):
        cfg = self._get_config()
        assert len(cfg.STOCK_SYMBOLS) == len(set(cfg.STOCK_SYMBOLS))


class TestGetConfig:
    def test_get_config_returns_trading_config(self):
        from config import get_config, TradingConfig
        result = get_config()
        assert isinstance(result, TradingConfig)

    def test_get_config_singleton_behavior(self):
        """get_config should return same type consistently."""
        from config import get_config, TradingConfig
        a = get_config()
        b = get_config()
        assert type(a) == type(b)


class TestRegressionConfig:
    def test_reddit_post_limit_positive(self):
        from config import TradingConfig
        cfg = TradingConfig()
        assert cfg.DATA_COLLECTION['reddit_post_limit'] > 0

    def test_collection_frequency_positive(self):
        from config import TradingConfig
        cfg = TradingConfig()
        assert cfg.DATA_COLLECTION['collection_frequency_minutes'] > 0

    def test_all_aliases_are_lists(self):
        from config import TradingConfig
        cfg = TradingConfig()
        for symbol, aliases in cfg.SYMBOL_ALIASES.items():
            assert isinstance(aliases, list), f"Aliases for {symbol} should be a list"
