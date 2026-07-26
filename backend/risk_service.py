"""
risk_service - bridges the market-data database to risk_analytics and turns the
advanced math into concrete, live risk controls (per-symbol risk reports,
risk-adjusted position sizing, correlation-aware portfolio risk gates).

Kept separate from risk_analytics (pure math) so the math stays trivially
testable and this layer owns the I/O.
"""

from __future__ import annotations

import os
import sqlite3
from typing import Dict, List, Optional, Sequence, Tuple

import risk_analytics as ra

TRADING_HOME = os.environ.get("TRADING_HOME") or os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
)
DEFAULT_DB = os.path.join(TRADING_HOME, "trading_data.db")

# Portfolio-level risk budget: if the correlation-aware portfolio CVaR/VaR
# exceeds these, the gate closes (block new risk / advise kill-switch).
DEFAULT_CONFIDENCE = 0.95
DEFAULT_CVAR_BUDGET = 0.05          # 5% expected-shortfall budget per position
PORTFOLIO_VAR_BUDGET = 0.06         # 6% one-day 95% portfolio VaR budget


def _closes(symbol: str, db_path: str = DEFAULT_DB, limit: int = 500) -> List[float]:
    """Most recent close prices for a symbol, oldest-first."""
    if not os.path.exists(db_path):
        return []
    try:
        with sqlite3.connect(db_path) as conn:
            rows = conn.execute(
                "SELECT close_price FROM market_data WHERE symbol = ? "
                "ORDER BY timestamp DESC LIMIT ?",
                (symbol, limit),
            ).fetchall()
    except sqlite3.Error:
        return []
    return [float(r[0]) for r in reversed(rows) if r[0] is not None]


def symbol_risk(symbol: str, db_path: str = DEFAULT_DB,
                confidence: float = DEFAULT_CONFIDENCE) -> Dict:
    """Full risk report for one symbol derived from its price history."""
    closes = _closes(symbol, db_path)
    returns = ra.log_returns(closes)
    n = int(returns.size)
    if n < 2:
        return {
            "symbol": symbol,
            "samples": n,
            "sufficient_data": False,
            "message": "not enough price history for a risk estimate",
        }
    ewma = ra.ewma_volatility(returns)
    return {
        "symbol": symbol,
        "samples": n,
        "sufficient_data": True,
        "confidence": confidence,
        "volatility_period": round(ewma, 6),
        "volatility_annualized": round(ra.annualize_vol(ewma), 6),
        "var_historical": round(ra.historical_var(returns, confidence), 6),
        "var_cornish_fisher": round(ra.cornish_fisher_var(returns, confidence), 6),
        "cvar_expected_shortfall": round(ra.historical_cvar(returns, confidence), 6),
        "max_drawdown": round(ra.max_drawdown(closes), 6),
        "sharpe_ratio": round(ra.sharpe_ratio(returns), 4),
        "sortino_ratio": round(ra.sortino_ratio(returns), 4),
    }


def recommended_position(
    symbol: str,
    confidence: float,
    risk_reward_ratio: float,
    db_path: str = DEFAULT_DB,
    target_vol: float = 0.02,
    max_position_pct: float = 10.0,
) -> Dict:
    """Risk-adjusted position size (percent of portfolio) for a signal.

    Combines fractional Kelly (edge), volatility targeting and a CVaR budget via
    risk_analytics.risk_adjusted_position_fraction. Falls back to a conservative
    fixed cap when there is not enough price history.
    """
    closes = _closes(symbol, db_path)
    returns = ra.log_returns(closes)
    if returns.size < 2:
        return {
            "recommended_pct": round(min(1.0, max_position_pct), 4),
            "basis": "insufficient_data_conservative_default",
            "max_position_pct": max_position_pct,
        }
    ewma = ra.ewma_volatility(returns)
    cvar = ra.historical_cvar(returns, DEFAULT_CONFIDENCE)
    sizing = ra.risk_adjusted_position_fraction(
        confidence=confidence,
        win_loss_ratio=max(risk_reward_ratio, 1e-9),
        asset_vol=ewma,
        target_vol=target_vol,
        cvar=cvar,
        cvar_budget=DEFAULT_CVAR_BUDGET,
        max_position=max_position_pct / 100.0,
    )
    sizing["recommended_pct"] = round(sizing["fraction"] * 100.0, 4)
    sizing["basis"] = "kelly x vol-target x cvar-budget"
    sizing["asset_vol_period"] = round(ewma, 6)
    sizing["cvar"] = round(cvar, 6)
    return sizing


def cap_position_pct(symbol: str, requested_pct: float, confidence: float,
                     risk_reward_ratio: float, db_path: str = DEFAULT_DB,
                     max_position_pct: float = 10.0) -> Tuple[float, Dict]:
    """Clamp a requested position size to the risk-adjusted maximum.

    Returns (applied_pct, detail). The applied size never exceeds either the
    requested size or the math-driven recommendation - risk can only shrink it.
    """
    rec = recommended_position(symbol, confidence, risk_reward_ratio,
                               db_path=db_path, max_position_pct=max_position_pct)
    recommended = rec.get("recommended_pct", max_position_pct)
    applied = float(max(0.0, min(requested_pct, recommended)))
    return applied, {
        "requested_pct": requested_pct,
        "risk_capped_pct": round(applied, 4),
        "recommended_pct": recommended,
        "capped": applied < requested_pct,
        "sizing": rec,
    }


def portfolio_risk(positions: Sequence[Tuple[str, float]],
                   db_path: str = DEFAULT_DB,
                   confidence: float = DEFAULT_CONFIDENCE) -> Dict:
    """Correlation-aware portfolio risk from open positions.

    ``positions`` is a list of (symbol, weight) where weight is the fraction of
    portfolio value in that symbol. Uses the covariance matrix of the symbols'
    return series, so correlated positions are not treated as independent.
    """
    symbols = [s for s, _ in positions]
    weights = [w for _, w in positions]
    returns_by_asset = {s: ra.log_returns(_closes(s, db_path)) for s in symbols}
    returns_by_asset = {s: r for s, r in returns_by_asset.items() if r.size >= 2}

    usable = [(s, w) for s, w in positions if s in returns_by_asset]
    if len(usable) == 0:
        return {"positions": len(positions), "sufficient_data": False,
                "message": "no return history for the held symbols"}

    syms = [s for s, _ in usable]
    w = [w for _, w in usable]
    cov = ra.covariance_matrix({s: returns_by_asset[s] for s in syms})
    pvol = ra.portfolio_volatility(w, cov)
    pvar = ra.portfolio_var(w, cov, confidence)
    div = ra.diversification_ratio(w, cov)

    # Sum of standalone VaRs vs the (lower) diversified portfolio VaR shows the
    # diversification benefit explicitly.
    standalone = sum(
        abs(wi) * ra.parametric_var(returns_by_asset[si], confidence)
        for si, wi in usable
    )
    gate_open = pvar <= PORTFOLIO_VAR_BUDGET
    return {
        "positions": len(usable),
        "sufficient_data": True,
        "confidence": confidence,
        "portfolio_volatility_period": round(pvol, 6),
        "portfolio_var": round(pvar, 6),
        "sum_standalone_var": round(standalone, 6),
        "diversification_ratio": round(div, 4),
        "var_budget": PORTFOLIO_VAR_BUDGET,
        "risk_gate_open": bool(gate_open),
        "recommendation": "ok" if gate_open else "reduce_exposure_or_halt",
    }
