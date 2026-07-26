"""Unit tests for the advanced risk mathematics in risk_analytics."""
import math

import numpy as np
import pytest

import risk_analytics as ra


class TestReturnsAndVol:
    def test_log_returns_values(self):
        r = ra.log_returns([100, 110, 121])
        # two equal +10% log steps
        assert np.allclose(r, [math.log(1.1), math.log(1.1)])

    def test_log_returns_short_series(self):
        assert ra.log_returns([100]).size == 0

    def test_ewma_vol_positive_and_reacts(self):
        calm = [0.001, -0.001, 0.001, -0.001] * 10
        shock = calm + [0.10]  # a big recent move
        assert ra.ewma_volatility(shock) > ra.ewma_volatility(calm)

    def test_ewma_vol_rejects_bad_lambda(self):
        with pytest.raises(ValueError):
            ra.ewma_volatility([0.01, -0.01], lam=1.5)

    def test_annualize(self):
        assert math.isclose(ra.annualize_vol(0.01, 252), 0.01 * math.sqrt(252))


class TestTailRisk:
    def test_historical_var_is_positive_loss(self):
        rng = np.random.default_rng(0)
        r = rng.normal(0, 0.02, 10000)
        var95 = ra.historical_var(r, 0.95)
        # ~1.645 sigma for a normal
        assert 0.02 * 1.4 < var95 < 0.02 * 1.9

    def test_cvar_exceeds_var(self):
        rng = np.random.default_rng(1)
        r = rng.normal(0, 0.02, 10000)
        assert ra.historical_cvar(r, 0.95) > ra.historical_var(r, 0.95)

    def test_parametric_var_matches_normal_quantile(self):
        rng = np.random.default_rng(2)
        r = rng.normal(0.0, 0.02, 200000)
        # analytic 99% VaR for mean 0, sigma 0.02 is 2.326*sigma
        assert math.isclose(ra.parametric_var(r, 0.99), 2.326 * 0.02, rel_tol=0.05)

    def test_cornish_fisher_reduces_to_parametric_for_normal(self):
        rng = np.random.default_rng(3)
        r = rng.normal(0, 0.02, 100000)
        cf = ra.cornish_fisher_var(r, 0.95)
        pv = ra.parametric_var(r, 0.95)
        assert math.isclose(cf, pv, rel_tol=0.10)

    def test_cornish_fisher_larger_for_left_skewed_fat_tails(self):
        rng = np.random.default_rng(4)
        # left-skewed, fat-tailed: normal body plus rare large losses
        r = np.concatenate([rng.normal(0, 0.01, 9000), rng.normal(-0.08, 0.02, 1000)])
        assert ra.cornish_fisher_var(r, 0.99) > ra.parametric_var(r, 0.99)


class TestPerformance:
    def test_max_drawdown_known(self):
        # peak 120 -> trough 60 is the worst: 50%
        eq = [100, 120, 90, 60, 80, 130, 110]
        assert math.isclose(ra.max_drawdown(eq), 0.5, rel_tol=1e-9)

    def test_max_drawdown_monotonic_up_is_zero(self):
        assert ra.max_drawdown([1, 2, 3, 4]) == 0.0

    def test_sortino_ge_sharpe_when_downside_small(self):
        r = [0.01, 0.02, -0.005, 0.015, 0.01, -0.002]
        assert ra.sortino_ratio(r) >= ra.sharpe_ratio(r)

    def test_sharpe_zero_variance(self):
        assert ra.sharpe_ratio([0.01, 0.01, 0.01]) == 0.0


class TestSizing:
    def test_kelly_known_value(self):
        # p=0.6, b=1  -> 0.6 - 0.4/1 = 0.2
        assert math.isclose(ra.kelly_fraction(0.6, 1.0), 0.2)

    def test_kelly_no_edge_clamped(self):
        assert ra.kelly_fraction(0.4, 1.0) == 0.0

    def test_vol_target_weight(self):
        # asset twice as volatile as target -> half weight
        assert math.isclose(ra.volatility_target_weight(0.04, 0.02), 0.5)
        assert ra.volatility_target_weight(0.0, 0.02) == 0.0

    def test_risk_adjusted_fraction_caps_and_shrinks(self):
        base = ra.risk_adjusted_position_fraction(
            confidence=0.8, win_loss_ratio=2.0, asset_vol=0.02, target_vol=0.02,
            max_position=0.10,
        )
        assert 0.0 < base["fraction"] <= 0.10
        # higher tail risk must shrink the size
        risky = ra.risk_adjusted_position_fraction(
            confidence=0.8, win_loss_ratio=2.0, asset_vol=0.02, target_vol=0.02,
            max_position=0.10, cvar=0.20, cvar_budget=0.05,
        )
        assert risky["fraction"] < base["fraction"]

    def test_risk_adjusted_fraction_no_edge_is_zero(self):
        out = ra.risk_adjusted_position_fraction(
            confidence=0.3, win_loss_ratio=1.0, asset_vol=0.02,
        )
        assert out["fraction"] == 0.0


class TestPortfolio:
    def test_portfolio_vol_accounts_for_correlation(self):
        # two assets, equal vol; correlation makes the combined vol differ
        sigma = 0.02
        w = [0.5, 0.5]
        cov_pos = np.array([[sigma**2, 0.8 * sigma**2], [0.8 * sigma**2, sigma**2]])
        cov_neg = np.array([[sigma**2, -0.8 * sigma**2], [-0.8 * sigma**2, sigma**2]])
        # negative correlation reduces portfolio vol; positive raises it
        assert ra.portfolio_volatility(w, cov_neg) < ra.portfolio_volatility(w, cov_pos)

    def test_portfolio_vol_analytic(self):
        # independent, equal vol: sigma_p = sigma * sqrt(sum w^2)
        sigma = 0.03
        w = [0.5, 0.5]
        cov = np.array([[sigma**2, 0.0], [0.0, sigma**2]])
        expected = sigma * math.sqrt(0.5**2 + 0.5**2)
        assert math.isclose(ra.portfolio_volatility(w, cov), expected, rel_tol=1e-9)

    def test_portfolio_var_positive(self):
        cov = np.array([[0.02**2, 0.0], [0.0, 0.02**2]])
        assert ra.portfolio_var([0.5, 0.5], cov, 0.95) > 0.0

    def test_diversification_ratio_ge_one_for_imperfect_corr(self):
        rets = {
            "A": list(np.random.default_rng(5).normal(0, 0.02, 300)),
            "B": list(np.random.default_rng(6).normal(0, 0.02, 300)),
        }
        cov = ra.covariance_matrix(rets)
        assert ra.diversification_ratio([0.5, 0.5], cov) > 1.0
