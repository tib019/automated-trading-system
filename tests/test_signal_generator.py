"""Unit tests for TechnicalAnalyzer and signal generation logic."""
import pytest
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# TechnicalAnalyzer – pure calculation methods (no DB needed)
# ---------------------------------------------------------------------------

class TestCalculateSMA:
    def _get_analyzer(self):
        """Create TechnicalAnalyzer with a patched DB so __init__ doesn't crash."""
        with patch('signal_generator.get_config') as mock_cfg, \
             patch('sqlite3.connect'):
            cfg = MagicMock()
            mock_cfg.return_value = cfg
            from signal_generator import TechnicalAnalyzer
            return TechnicalAnalyzer(db_path=':memory:')

    def test_sma_basic(self):
        analyzer = self._get_analyzer()
        prices = [1.0, 2.0, 3.0, 4.0, 5.0]
        result = analyzer.calculate_sma(prices, period=3)
        assert result == [2.0, 3.0, 4.0]

    def test_sma_period_larger_than_data_returns_empty(self):
        analyzer = self._get_analyzer()
        result = analyzer.calculate_sma([1.0, 2.0], period=5)
        assert result == []

    def test_sma_period_equals_data_length(self):
        analyzer = self._get_analyzer()
        prices = [10.0, 20.0, 30.0]
        result = analyzer.calculate_sma(prices, period=3)
        assert result == [20.0]

    def test_sma_period_1_returns_same_list(self):
        analyzer = self._get_analyzer()
        prices = [5.0, 10.0, 15.0]
        result = analyzer.calculate_sma(prices, period=1)
        assert result == prices

    def test_sma_empty_prices_returns_empty(self):
        analyzer = self._get_analyzer()
        assert analyzer.calculate_sma([], period=3) == []


class TestCalculateEMA:
    def _get_analyzer(self):
        with patch('signal_generator.get_config') as mock_cfg, \
             patch('sqlite3.connect'):
            mock_cfg.return_value = MagicMock()
            from signal_generator import TechnicalAnalyzer
            return TechnicalAnalyzer(db_path=':memory:')

    def test_ema_returns_correct_length(self):
        analyzer = self._get_analyzer()
        prices = [10.0] * 10
        result = analyzer.calculate_ema(prices, period=3)
        # EMA needs at least `period` values; length == len(prices) - period + 1
        assert len(result) == len(prices) - 3 + 1

    def test_ema_constant_prices_equals_constant(self):
        analyzer = self._get_analyzer()
        prices = [5.0] * 10
        result = analyzer.calculate_ema(prices, period=3)
        for v in result:
            assert abs(v - 5.0) < 1e-6

    def test_ema_too_short_returns_empty(self):
        analyzer = self._get_analyzer()
        assert analyzer.calculate_ema([1.0], period=5) == []


class TestCalculateRSI:
    def _get_analyzer(self):
        with patch('signal_generator.get_config') as mock_cfg, \
             patch('sqlite3.connect'):
            mock_cfg.return_value = MagicMock()
            from signal_generator import TechnicalAnalyzer
            return TechnicalAnalyzer(db_path=':memory:')

    def test_rsi_all_gains_returns_100(self):
        analyzer = self._get_analyzer()
        prices = [float(i) for i in range(1, 20)]  # constantly rising
        result = analyzer.calculate_rsi(prices, period=14)
        assert result[-1] == pytest.approx(100.0, abs=1.0)

    def test_rsi_all_losses_returns_0(self):
        analyzer = self._get_analyzer()
        prices = [float(20 - i) for i in range(20)]  # constantly falling
        result = analyzer.calculate_rsi(prices, period=14)
        assert result[-1] == pytest.approx(0.0, abs=1.0)

    def test_rsi_values_between_0_and_100(self):
        analyzer = self._get_analyzer()
        import math
        prices = [math.sin(i * 0.3) * 10 + 50 for i in range(50)]
        result = analyzer.calculate_rsi(prices, period=14)
        for v in result:
            assert 0.0 <= v <= 100.0

    def test_rsi_too_short_returns_empty(self):
        analyzer = self._get_analyzer()
        assert analyzer.calculate_rsi([1.0, 2.0], period=14) == []


class TestCalculateBollingerBands:
    def _get_analyzer(self):
        with patch('signal_generator.get_config') as mock_cfg, \
             patch('sqlite3.connect'):
            mock_cfg.return_value = MagicMock()
            from signal_generator import TechnicalAnalyzer
            return TechnicalAnalyzer(db_path=':memory:')

    def test_middle_band_is_sma(self):
        analyzer = self._get_analyzer()
        prices = [10.0] * 25
        result = analyzer.calculate_bollinger_bands(prices, period=20)
        assert 'middle' in result
        for v in result['middle']:
            assert v == pytest.approx(10.0)

    def test_upper_greater_than_middle(self):
        analyzer = self._get_analyzer()
        import random
        random.seed(42)
        prices = [random.uniform(90, 110) for _ in range(30)]
        result = analyzer.calculate_bollinger_bands(prices, period=20)
        for u, m in zip(result['upper'], result['middle']):
            assert u >= m

    def test_lower_less_than_middle(self):
        analyzer = self._get_analyzer()
        import random
        random.seed(0)
        prices = [random.uniform(90, 110) for _ in range(30)]
        result = analyzer.calculate_bollinger_bands(prices, period=20)
        for l, m in zip(result['lower'], result['middle']):
            assert l <= m

    def test_constant_prices_bands_equal_middle(self):
        analyzer = self._get_analyzer()
        prices = [50.0] * 30
        result = analyzer.calculate_bollinger_bands(prices, period=20)
        for u, l, m in zip(result['upper'], result['lower'], result['middle']):
            assert u == pytest.approx(m)
            assert l == pytest.approx(m)


# ---------------------------------------------------------------------------
# SignalType / SignalStrength enums
# ---------------------------------------------------------------------------

class TestEnums:
    def test_signal_types_exist(self):
        from signal_generator import SignalType
        assert SignalType.BUY.value == "BUY"
        assert SignalType.SELL.value == "SELL"
        assert SignalType.HOLD.value == "HOLD"

    def test_signal_strengths_exist(self):
        from signal_generator import SignalStrength
        assert SignalStrength.WEAK.value == "WEAK"
        assert SignalStrength.MODERATE.value == "MODERATE"
        assert SignalStrength.STRONG.value == "STRONG"


# ---------------------------------------------------------------------------
# Regression / edge cases
# ---------------------------------------------------------------------------

class TestRegressionSignalGenerator:
    def _get_analyzer(self):
        with patch('signal_generator.get_config') as mock_cfg, \
             patch('sqlite3.connect'):
            mock_cfg.return_value = MagicMock()
            from signal_generator import TechnicalAnalyzer
            return TechnicalAnalyzer(db_path=':memory:')

    def test_sma_single_price(self):
        analyzer = self._get_analyzer()
        assert analyzer.calculate_sma([42.0], period=1) == [42.0]

    def test_ema_with_zero_prices(self):
        analyzer = self._get_analyzer()
        prices = [0.0] * 10
        result = analyzer.calculate_ema(prices, period=3)
        for v in result:
            assert v == pytest.approx(0.0)

    def test_bollinger_period_larger_than_data(self):
        analyzer = self._get_analyzer()
        result = analyzer.calculate_bollinger_bands([1.0, 2.0], period=20)
        assert result.get('middle', []) == []

    def test_rsi_with_flat_prices(self):
        """Flat prices → no gains/losses → RSI is undefined but shouldn't crash."""
        analyzer = self._get_analyzer()
        prices = [100.0] * 20
        result = analyzer.calculate_rsi(prices, period=14)
        # Result is a list; should not raise, values may be 100 or 0 depending on implementation
        assert isinstance(result, list)
