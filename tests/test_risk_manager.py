"""Unit tests for RiskManager and PortfolioTracker."""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime


def _make_signal(symbol='BTC-USD', signal_type_str='BUY', confidence=0.7,
                 entry_price=50000.0, stop_loss=48000.0, take_profit=55000.0,
                 position_size_percent=2.0, risk_reward_ratio=2.5):
    with patch('signal_generator.get_config'), patch('sqlite3.connect'):
        from signal_generator import TradingSignal, SignalType, SignalStrength
        return TradingSignal(
            symbol=symbol,
            timestamp=datetime.now(),
            signal_type=SignalType[signal_type_str],
            strength=SignalStrength.MODERATE,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            confidence=confidence,
            reasoning="test signal",
            sentiment_score=0.6,
            technical_score=0.7,
            volume_score=0.5,
            position_size_percent=position_size_percent,
            risk_reward_ratio=risk_reward_ratio,
        )


def _make_portfolio_metrics(total_value=10000, cash=8000, invested=2000,
                             total_pnl=0, daily_pnl=0, open_positions=0,
                             total_positions=0, win_rate=50, max_drawdown=0,
                             risk_level_str='LOW'):
    from risk_manager import PortfolioMetrics, RiskLevel
    return PortfolioMetrics(
        total_value=total_value,
        cash_balance=cash,
        invested_amount=invested,
        total_pnl=total_pnl,
        daily_pnl=daily_pnl,
        open_positions=open_positions,
        total_positions=total_positions,
        win_rate=win_rate,
        max_drawdown=max_drawdown,
        risk_level=RiskLevel[risk_level_str],
    )


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class TestEnums:
    def test_position_statuses(self):
        from risk_manager import PositionStatus
        assert PositionStatus.OPEN.value == "OPEN"
        assert PositionStatus.CLOSED.value == "CLOSED"
        assert PositionStatus.STOPPED.value == "STOPPED"
        assert PositionStatus.PROFIT_TAKEN.value == "PROFIT_TAKEN"

    def test_risk_levels(self):
        from risk_manager import RiskLevel
        assert RiskLevel.LOW.value == "LOW"
        assert RiskLevel.MODERATE.value == "MODERATE"
        assert RiskLevel.HIGH.value == "HIGH"
        assert RiskLevel.CRITICAL.value == "CRITICAL"


# ---------------------------------------------------------------------------
# RiskManager.validate_signal
# ---------------------------------------------------------------------------

def _make_rm():
    with patch('risk_manager.get_config') as mock_cfg, \
         patch('risk_manager.PortfolioTracker') as mock_pt_cls, \
         patch('sqlite3.connect'):
        cfg = MagicMock()
        cfg.RISK_MANAGEMENT = {
            'max_position_size_percent': 5.0,
            'daily_loss_limit_percent': 10.0,
            'max_open_positions': 5,
            'stop_loss_percent': 2.0,
            'take_profit_percent': 6.0,
            'trailing_stop_percent': 1.0,
        }
        mock_cfg.return_value = cfg

        # Default: healthy portfolio with no open positions
        mock_pt = MagicMock()
        mock_pt.get_portfolio_metrics.return_value = _make_portfolio_metrics()
        mock_pt.get_open_positions.return_value = []
        mock_pt_cls.return_value = mock_pt

        from risk_manager import RiskManager
        rm = RiskManager()
        return rm, mock_pt


class TestRiskManagerValidateSignal:
    def test_valid_signal_passes(self):
        rm, _ = _make_rm()
        signal = _make_signal(position_size_percent=2.0)
        valid, reason = rm.validate_signal(signal)
        assert valid is True
        assert "validiert" in reason.lower()

    def test_kill_switch_active_fails(self):
        rm, _ = _make_rm()
        rm.kill_switch_active = True
        signal = _make_signal()
        valid, reason = rm.validate_signal(signal)
        assert valid is False
        assert "kill-switch" in reason.lower()

    def test_max_positions_exceeded_fails(self):
        rm, mock_pt = _make_rm()
        mock_pt.get_portfolio_metrics.return_value = _make_portfolio_metrics(
            open_positions=5  # equals max_open_positions
        )
        signal = _make_signal(position_size_percent=2.0)
        valid, reason = rm.validate_signal(signal)
        assert valid is False
        assert "positionen" in reason.lower()

    def test_critical_risk_level_fails(self):
        rm, mock_pt = _make_rm()
        mock_pt.get_portfolio_metrics.return_value = _make_portfolio_metrics(
            risk_level_str='CRITICAL'
        )
        signal = _make_signal(position_size_percent=1.0)
        valid, reason = rm.validate_signal(signal)
        assert valid is False
        assert "critical" in reason.lower()

    def test_extreme_exposure_fails(self):
        rm, mock_pt = _make_rm()
        # invested_amount already at 80% → adding more fails
        mock_pt.get_portfolio_metrics.return_value = _make_portfolio_metrics(
            total_value=10000, invested=8500, cash=1500
        )
        signal = _make_signal(position_size_percent=5.0)
        valid, reason = rm.validate_signal(signal)
        assert valid is False


# ---------------------------------------------------------------------------
# PortfolioTracker – _calculate_risk_level
# ---------------------------------------------------------------------------

class TestCalculateRiskLevel:
    def _get_tracker(self):
        with patch('risk_manager.get_config') as mock_cfg, \
             patch('sqlite3.connect'):
            cfg = MagicMock()
            cfg.BACKTESTING = {'initial_capital': 10000}
            mock_cfg.return_value = cfg
            from risk_manager import PortfolioTracker
            tracker = PortfolioTracker.__new__(PortfolioTracker)
            tracker.config = cfg
            tracker.initial_capital = 10000
            return tracker

    def test_small_loss_is_low_or_moderate(self):
        from risk_manager import RiskLevel
        tracker = self._get_tracker()
        level = tracker._calculate_risk_level(
            total_pnl=-100, invested_amount=2000, total_value=9900
        )
        assert level in (RiskLevel.LOW, RiskLevel.MODERATE)

    def test_large_loss_is_high_or_critical(self):
        from risk_manager import RiskLevel
        tracker = self._get_tracker()
        level = tracker._calculate_risk_level(
            total_pnl=-4000, invested_amount=8000, total_value=6000
        )
        assert level in (RiskLevel.HIGH, RiskLevel.CRITICAL)

    def test_profit_is_low_risk(self):
        from risk_manager import RiskLevel
        tracker = self._get_tracker()
        level = tracker._calculate_risk_level(
            total_pnl=500, invested_amount=3000, total_value=10500
        )
        assert level == RiskLevel.LOW


# ---------------------------------------------------------------------------
# Regression tests
# ---------------------------------------------------------------------------

class TestRegressionRiskManager:
    def test_zero_open_positions_allows_signal(self):
        rm, mock_pt = _make_rm()
        mock_pt.get_portfolio_metrics.return_value = _make_portfolio_metrics(open_positions=0)
        signal = _make_signal(position_size_percent=1.0)
        valid, _ = rm.validate_signal(signal)
        assert valid is True

    def test_daily_loss_limit_triggers_kill_switch(self):
        rm, mock_pt = _make_rm()
        # daily_pnl exceeds 10% of 10,000 = -1000
        mock_pt.get_portfolio_metrics.return_value = _make_portfolio_metrics(
            total_value=10000, daily_pnl=-1500
        )
        mock_pt.get_open_positions.return_value = []
        with patch('sqlite3.connect'):
            signal = _make_signal()
            valid, reason = rm.validate_signal(signal)
        assert valid is False
        assert rm.kill_switch_active is True

    def test_validate_signal_returns_tuple(self):
        rm, _ = _make_rm()
        result = rm.validate_signal(_make_signal())
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], bool)
        assert isinstance(result[1], str)
