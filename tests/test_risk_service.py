"""Tests for the DB<->risk bridge and the risk-based position cap."""
import math
import os
import sqlite3

import pytest


def _seed_db(path, symbol, prices):
    con = sqlite3.connect(path)
    con.execute(
        "CREATE TABLE IF NOT EXISTS market_data ("
        "id INTEGER PRIMARY KEY, symbol TEXT, timestamp TEXT, "
        "open_price REAL, high_price REAL, low_price REAL, "
        "close_price REAL, volume REAL, source TEXT)"
    )
    for i, p in enumerate(prices):
        con.execute(
            "INSERT INTO market_data (symbol,timestamp,open_price,high_price,"
            "low_price,close_price,volume,source) VALUES (?,?,?,?,?,?,?,?)",
            (symbol, f"2026-01-01T{i:02d}:00:00", p, p, p, p, 1000, "test"),
        )
    con.commit()
    con.close()


@pytest.fixture()
def db(tmp_path):
    return str(tmp_path / "trading_data.db")


class TestSymbolRisk:
    def test_insufficient_data(self, db):
        import risk_service as rs
        _seed_db(db, "AAA", [100.0])
        out = rs.symbol_risk("AAA", db_path=db)
        assert out["sufficient_data"] is False

    def test_full_report_fields(self, db):
        import risk_service as rs
        prices = [100 * (1.001 ** i) + (i % 5) for i in range(120)]
        _seed_db(db, "AAA", prices)
        out = rs.symbol_risk("AAA", db_path=db)
        assert out["sufficient_data"] is True
        for k in ("volatility_period", "var_historical", "var_cornish_fisher",
                  "cvar_expected_shortfall", "max_drawdown", "sharpe_ratio"):
            assert k in out
        # CVaR (expected shortfall) is never smaller than historical VaR
        assert out["cvar_expected_shortfall"] >= out["var_historical"] - 1e-9


class TestPositionCap:
    def test_cap_only_shrinks(self, db):
        import risk_service as rs
        # volatile series -> risk sizing should cap below a large request
        prices = [100 + 8 * math.sin(i / 3.0) for i in range(150)]
        _seed_db(db, "AAA", prices)
        applied, detail = rs.cap_position_pct(
            "AAA", requested_pct=9.0, confidence=0.7, risk_reward_ratio=2.0, db_path=db)
        assert applied <= 9.0
        assert detail["risk_capped_pct"] == pytest.approx(applied)

    def test_cap_never_exceeds_request(self, db):
        import risk_service as rs
        prices = [100 + 0.01 * i for i in range(200)]  # very calm
        _seed_db(db, "AAA", prices)
        applied, _ = rs.cap_position_pct(
            "AAA", requested_pct=1.0, confidence=0.9, risk_reward_ratio=3.0, db_path=db)
        assert applied <= 1.0

    def test_insufficient_data_conservative(self, db):
        import risk_service as rs
        _seed_db(db, "AAA", [100.0])
        applied, detail = rs.cap_position_pct(
            "AAA", requested_pct=5.0, confidence=0.8, risk_reward_ratio=2.0, db_path=db)
        assert applied <= 5.0


class TestPortfolioRisk:
    def test_portfolio_gate(self, db):
        import numpy as np
        import risk_service as rs
        rng = np.random.default_rng(11)
        # two noisy, essentially uncorrelated price series -> real diversification
        a = 100 * np.cumprod(1 + rng.normal(0, 0.02, 200))
        b = 50 * np.cumprod(1 + rng.normal(0, 0.02, 200))
        _seed_db(db, "AAA", list(a))
        _seed_db(db, "BBB", list(b))
        out = rs.portfolio_risk([("AAA", 0.5), ("BBB", 0.5)], db_path=db)
        assert out["sufficient_data"] is True
        assert "portfolio_var" in out and "risk_gate_open" in out
        # with imperfect correlation the diversified portfolio VaR is strictly
        # below the naive sum of standalone VaRs
        assert out["portfolio_var"] < out["sum_standalone_var"]
        assert out["diversification_ratio"] > 1.0
