"""
risk_analytics - advanced quantitative risk mathematics for the trading system.

Pure functions, dependency-light (numpy + the standard library only), so they
are easy to unit-test and reuse. Everything works on *periodic returns*
(fraction, e.g. 0.012 for +1.2%) unless noted.

Contents
--------
Returns / volatility
    log_returns, simple_returns, ewma_volatility, rolling_volatility, annualize_vol
Tail risk
    historical_var, historical_cvar, parametric_var, cornish_fisher_var, parametric_cvar
Performance
    sharpe_ratio, sortino_ratio, max_drawdown, calmar_ratio
Position sizing
    kelly_fraction, volatility_target_weight, risk_adjusted_position_fraction
Portfolio (correlation-aware)
    covariance_matrix, correlation_matrix, portfolio_volatility, portfolio_var,
    diversification_ratio

Conventions
-----------
* VaR / CVaR are returned as **positive loss magnitudes** (fraction of capital).
  A 95% VaR of 0.03 means: with 95% confidence the one-period loss will not
  exceed 3% of the position.
* ``confidence`` is the VaR confidence level, e.g. 0.95 or 0.99.
"""

from __future__ import annotations

import math
from statistics import NormalDist
from typing import Sequence

import numpy as np

TRADING_DAYS = 252
_N = NormalDist()  # standard normal, stdlib - no scipy dependency


# --------------------------------------------------------------------------- #
# Returns & volatility
# --------------------------------------------------------------------------- #
def log_returns(prices: Sequence[float]) -> np.ndarray:
    """Continuously-compounded returns from a price series."""
    p = np.asarray(prices, dtype=float)
    p = p[np.isfinite(p) & (p > 0)]
    if p.size < 2:
        return np.array([])
    return np.diff(np.log(p))


def simple_returns(prices: Sequence[float]) -> np.ndarray:
    p = np.asarray(prices, dtype=float)
    p = p[np.isfinite(p) & (p > 0)]
    if p.size < 2:
        return np.array([])
    return p[1:] / p[:-1] - 1.0


def ewma_volatility(returns: Sequence[float], lam: float = 0.94) -> float:
    """RiskMetrics exponentially-weighted volatility (per period).

    sigma_t^2 = lam * sigma_{t-1}^2 + (1 - lam) * r_{t-1}^2

    Reacts faster to regime changes than an equal-weighted std, which makes it
    a better risk gate for a live system. ``lam=0.94`` is the RiskMetrics daily
    default.
    """
    r = np.asarray(returns, dtype=float)
    r = r[np.isfinite(r)]
    if r.size == 0:
        return 0.0
    if not 0.0 < lam < 1.0:
        raise ValueError("lam must be in (0, 1)")
    var = float(np.var(r)) if r.size > 1 else float(r[0] ** 2)
    for x in r:
        var = lam * var + (1.0 - lam) * x * x
    return math.sqrt(max(var, 0.0))


def rolling_volatility(returns: Sequence[float], window: int = 20) -> float:
    """Equal-weighted sample volatility over the last ``window`` observations."""
    r = np.asarray(returns, dtype=float)
    r = r[np.isfinite(r)]
    if r.size < 2:
        return 0.0
    w = r[-window:] if r.size > window else r
    return float(np.std(w, ddof=1))


def annualize_vol(vol_per_period: float, periods_per_year: int = TRADING_DAYS) -> float:
    return vol_per_period * math.sqrt(periods_per_year)


# --------------------------------------------------------------------------- #
# Tail risk: Value-at-Risk and Conditional VaR (Expected Shortfall)
# --------------------------------------------------------------------------- #
def historical_var(returns: Sequence[float], confidence: float = 0.95) -> float:
    """Non-parametric VaR from the empirical return distribution."""
    r = np.asarray(returns, dtype=float)
    r = r[np.isfinite(r)]
    if r.size == 0:
        return 0.0
    q = float(np.quantile(r, 1.0 - confidence))
    return max(-q, 0.0)


def historical_cvar(returns: Sequence[float], confidence: float = 0.95) -> float:
    """Expected Shortfall: mean loss *beyond* the VaR threshold.

    CVaR answers "if we breach VaR, how bad is it on average" and is a coherent
    risk measure (unlike VaR), which is why it drives the kill-switch here.
    """
    r = np.asarray(returns, dtype=float)
    r = r[np.isfinite(r)]
    if r.size == 0:
        return 0.0
    q = np.quantile(r, 1.0 - confidence)
    tail = r[r <= q]
    if tail.size == 0:
        return max(-float(q), 0.0)
    return max(-float(tail.mean()), 0.0)


def parametric_var(returns: Sequence[float], confidence: float = 0.95) -> float:
    """Gaussian (variance-covariance) VaR."""
    r = np.asarray(returns, dtype=float)
    r = r[np.isfinite(r)]
    if r.size < 2:
        return 0.0
    mu, sigma = float(np.mean(r)), float(np.std(r, ddof=1))
    z = _N.inv_cdf(1.0 - confidence)  # negative
    return max(-(mu + sigma * z), 0.0)


def parametric_cvar(returns: Sequence[float], confidence: float = 0.95) -> float:
    """Gaussian Expected Shortfall (closed form)."""
    r = np.asarray(returns, dtype=float)
    r = r[np.isfinite(r)]
    if r.size < 2:
        return 0.0
    mu, sigma = float(np.mean(r)), float(np.std(r, ddof=1))
    a = 1.0 - confidence
    # ES = -mu + sigma * pdf(z_a) / a
    z = _N.inv_cdf(a)
    es = -mu + sigma * _N.pdf(z) / a
    return max(es, 0.0)


def cornish_fisher_var(returns: Sequence[float], confidence: float = 0.95) -> float:
    """Modified VaR that corrects the Gaussian quantile for skewness and excess
    kurtosis (Cornish-Fisher expansion). Fat-tailed / skewed return series -
    exactly what markets produce - get a more honest, usually larger, VaR.
    """
    r = np.asarray(returns, dtype=float)
    r = r[np.isfinite(r)]
    if r.size < 3:
        return parametric_var(r, confidence)
    mu, sigma = float(np.mean(r)), float(np.std(r, ddof=1))
    if sigma == 0.0:
        return 0.0
    std = (r - mu) / sigma
    s = float(np.mean(std ** 3))               # skewness
    k = float(np.mean(std ** 4)) - 3.0         # excess kurtosis
    z = _N.inv_cdf(1.0 - confidence)
    z_cf = (
        z
        + (z * z - 1.0) * s / 6.0
        + (z ** 3 - 3.0 * z) * k / 24.0
        - (2.0 * z ** 3 - 5.0 * z) * (s ** 2) / 36.0
    )
    return max(-(mu + sigma * z_cf), 0.0)


# --------------------------------------------------------------------------- #
# Performance / drawdown
# --------------------------------------------------------------------------- #
def sharpe_ratio(returns: Sequence[float], risk_free: float = 0.0,
                 periods_per_year: int = TRADING_DAYS) -> float:
    r = np.asarray(returns, dtype=float)
    r = r[np.isfinite(r)]
    if r.size < 2:
        return 0.0
    excess = r - risk_free / periods_per_year
    sd = float(np.std(excess, ddof=1))
    if sd == 0.0:
        return 0.0
    return float(np.mean(excess)) / sd * math.sqrt(periods_per_year)


def sortino_ratio(returns: Sequence[float], risk_free: float = 0.0,
                  periods_per_year: int = TRADING_DAYS) -> float:
    """Like Sharpe but penalises only downside volatility."""
    r = np.asarray(returns, dtype=float)
    r = r[np.isfinite(r)]
    if r.size < 2:
        return 0.0
    excess = r - risk_free / periods_per_year
    downside = excess[excess < 0.0]
    dd = math.sqrt(float(np.mean(downside ** 2))) if downside.size else 0.0
    if dd == 0.0:
        return 0.0
    return float(np.mean(excess)) / dd * math.sqrt(periods_per_year)


def max_drawdown(equity_curve: Sequence[float]) -> float:
    """Largest peak-to-trough decline as a positive fraction (0.2 == -20%)."""
    e = np.asarray(equity_curve, dtype=float)
    e = e[np.isfinite(e)]
    if e.size < 2:
        return 0.0
    peak = np.maximum.accumulate(e)
    dd = (e - peak) / peak
    return float(-dd.min())


def calmar_ratio(returns: Sequence[float], periods_per_year: int = TRADING_DAYS) -> float:
    """Annualised return divided by max drawdown."""
    r = np.asarray(returns, dtype=float)
    r = r[np.isfinite(r)]
    if r.size < 2:
        return 0.0
    equity = np.cumprod(1.0 + r)
    mdd = max_drawdown(np.concatenate([[1.0], equity]))
    if mdd == 0.0:
        return 0.0
    ann_return = float(equity[-1]) ** (periods_per_year / r.size) - 1.0
    return ann_return / mdd


# --------------------------------------------------------------------------- #
# Position sizing
# --------------------------------------------------------------------------- #
def kelly_fraction(win_prob: float, win_loss_ratio: float) -> float:
    """Kelly-optimal fraction of capital for a bet with the given edge.

    f* = p - (1 - p) / b   where b is the payoff (win/loss) ratio.
    Negative (no edge) is clamped to 0.
    """
    p = min(max(win_prob, 0.0), 1.0)
    b = max(win_loss_ratio, 1e-9)
    return max(p - (1.0 - p) / b, 0.0)


def volatility_target_weight(asset_vol: float, target_vol: float,
                             max_weight: float = 1.0) -> float:
    """Weight so that position volatility ~= target volatility.

    weight = target_vol / asset_vol, capped at ``max_weight``. Low-vol assets
    get more capital, high-vol assets less - equalising risk contribution.
    """
    if asset_vol <= 0.0:
        return 0.0
    return float(min(target_vol / asset_vol, max_weight))


def risk_adjusted_position_fraction(
    *,
    confidence: float,
    win_loss_ratio: float,
    asset_vol: float,
    target_vol: float = 0.02,
    kelly_fraction_cap: float = 0.5,
    max_position: float = 0.10,
    cvar: float | None = None,
    cvar_budget: float = 0.05,
) -> dict:
    """Combine several risk controls into one position fraction of the portfolio.

    Layers (each can only *shrink* the size):
      1. Fractional Kelly from the model's edge (confidence -> win probability).
      2. Volatility targeting (scale down when the asset is more volatile than
         the target risk budget).
      3. CVaR budget (scale down when tail risk exceeds the allowed budget).
      4. Hard cap ``max_position``.

    Returns a dict with the final ``fraction`` and every intermediate factor so
    the decision is fully auditable.
    """
    win_prob = min(max(confidence, 0.0), 1.0)
    kelly = kelly_fraction(win_prob, win_loss_ratio)
    frac_kelly = kelly * kelly_fraction_cap

    vol_scale = volatility_target_weight(asset_vol, target_vol, max_weight=1.0) if asset_vol > 0 else 1.0

    cvar_scale = 1.0
    if cvar is not None and cvar > 0.0:
        cvar_scale = min(cvar_budget / cvar, 1.0)

    fraction = frac_kelly * vol_scale * cvar_scale
    fraction = float(min(max(fraction, 0.0), max_position))
    return {
        "fraction": fraction,
        "kelly": kelly,
        "fractional_kelly": frac_kelly,
        "vol_scale": vol_scale,
        "cvar_scale": cvar_scale,
        "capped_at": max_position,
    }


# --------------------------------------------------------------------------- #
# Portfolio (correlation-aware) risk
# --------------------------------------------------------------------------- #
def _returns_matrix(returns_by_asset: dict[str, Sequence[float]]) -> tuple[list[str], np.ndarray]:
    symbols = list(returns_by_asset.keys())
    series = [np.asarray(returns_by_asset[s], dtype=float) for s in symbols]
    n = min(len(s) for s in series) if series else 0
    if n < 2:
        return symbols, np.empty((0, len(symbols)))
    mat = np.column_stack([s[-n:] for s in series])
    return symbols, mat


def covariance_matrix(returns_by_asset: dict[str, Sequence[float]]) -> np.ndarray:
    _, mat = _returns_matrix(returns_by_asset)
    if mat.shape[0] < 2:
        return np.zeros((mat.shape[1], mat.shape[1]))
    return np.cov(mat, rowvar=False, ddof=1)


def correlation_matrix(returns_by_asset: dict[str, Sequence[float]]) -> np.ndarray:
    _, mat = _returns_matrix(returns_by_asset)
    if mat.shape[0] < 2:
        return np.eye(mat.shape[1])
    return np.corrcoef(mat, rowvar=False)


def portfolio_volatility(weights: Sequence[float], cov: np.ndarray) -> float:
    """sqrt(w' Σ w) - portfolio vol that accounts for correlations.

    Treating positions independently understates risk when they are correlated;
    this does not.
    """
    w = np.asarray(weights, dtype=float)
    c = np.asarray(cov, dtype=float)
    if w.size == 0 or c.size == 0 or c.shape[0] != w.size:
        return 0.0
    var = float(w @ c @ w)
    return math.sqrt(max(var, 0.0))


def portfolio_var(weights: Sequence[float], cov: np.ndarray,
                  confidence: float = 0.95) -> float:
    """Gaussian portfolio VaR from the covariance matrix (positive loss)."""
    vol = portfolio_volatility(weights, cov)
    if vol == 0.0:
        return 0.0
    z = _N.inv_cdf(1.0 - confidence)
    return max(-vol * z, 0.0)


def diversification_ratio(weights: Sequence[float], cov: np.ndarray) -> float:
    """Weighted average of individual vols divided by portfolio vol.

    >1 means diversification is reducing risk; ==1 means no benefit.
    """
    w = np.asarray(weights, dtype=float)
    c = np.asarray(cov, dtype=float)
    if w.size == 0 or c.shape[0] != w.size:
        return 1.0
    indiv = np.sqrt(np.clip(np.diag(c), 0.0, None))
    weighted_avg = float(np.abs(w) @ indiv)
    pvol = portfolio_volatility(w, c)
    if pvol == 0.0:
        return 1.0
    return weighted_avg / pvol
