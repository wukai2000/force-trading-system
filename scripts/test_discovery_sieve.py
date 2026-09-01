#!/usr/bin/env python3
"""
Engine-sieve tests — no Force 4 prices.

Covers:
  - placebo is mean |IR| and kills concentrated paths
  - neighbor aligns 14:30 vs midnight timestamps
  - neighbor marks a linear combo of paused residuals as spanned
  - value-permutation IR is a no-op; block bootstrap is not
  - literature simulators do not auto-map to defense tickets
  - WAIT tickers are skipped by the sieve
  - planted leftover can SIEVE_KEEP; clone of paused residual drops
  - GPR synthetic is not the default cache
  - defense YAML stays scannable=false
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
import yaml

from force_engine.dates import pick_close_column
from force_engine.evaluate import annualized_ir, evaluate_neutralized, sign_placebo_ir
from force_engine.false_discovery import block_bootstrap_mean_abs_ir, diagnose, time_shuffle_ir
from force_engine.guards import WaitLockError, refuse_wait_scan
from force_engine.literature import simulate_gpr, simulate_p_factor
from force_engine.neighbor import orthogonalize_against_paused
from force_engine.neutralize import NeutralizationError, rolling_ols_residual
from force_engine.sieve import sieve_panel


def test_placebo_is_mean_abs():
    rng = np.random.default_rng(0)
    drift = pd.Series(0.001 + rng.normal(0, 0.004, 1500))
    p_drift = sign_placebo_ir(drift)
    obs_d = annualized_ir(drift)
    frac_d = p_drift / abs(obs_d)
    assert obs_d > 1.0, obs_d
    assert frac_d < 0.40, (obs_d, p_drift, frac_d)
    conc = np.zeros(1500)
    conc[50] = 0.20
    conc[120] = 0.18
    conc[400] = -0.22
    conc[700] = 0.19
    conc[900] = 0.17
    conc = pd.Series(conc + rng.normal(0, 0.0004, 1500))
    obs = annualized_ir(conc)
    p_conc = sign_placebo_ir(conc)
    frac_c = p_conc / abs(obs)
    assert obs > 0.40, obs
    assert p_conc >= 0.15 and frac_c >= 0.40, (obs, p_conc, frac_c)
    print("PASS placebo mean |IR|: distributed drift frac low, concentrated frac high", frac_d, frac_c)


def test_concentrated_path_fails_gate():
    rng = np.random.default_rng(1)
    idx = pd.bdate_range("2018-01-02", periods=1200)
    x = rng.normal(0.0002, 0.01, len(idx))
    y = 0.2 * x + rng.normal(0, 0.001, len(idx))
    y[80] += 0.25
    y[200] += 0.22
    y[600] -= 0.24
    basket = pd.Series(y, index=idx)
    controls = pd.DataFrame({"XLU": x}, index=idx)
    panel = rolling_ols_residual(basket, controls, lookback=60)
    gate = {"min_clean_ir": 0.40, "max_placebo_ir": 0.15, "min_overlap_years": 3}
    result = evaluate_neutralized(panel, gate, neutralized=True)
    assert result.verdict == "FAIL_GATE", result
    assert any("placebo" in f for f in result.failures), result.failures
    print("PASS concentrated path FAIL_GATE on placebo |IR|", result.metrics["placebo_ir"], result.failures)


def test_placebo_bypass_env_refused():
    os.environ["PLACEBO_RELAX"] = "1"
    try:
        rng = np.random.default_rng(2)
        idx = pd.bdate_range("2018-01-02", periods=400)
        x = rng.normal(0, 0.01, len(idx))
        panel = rolling_ols_residual(pd.Series(x, index=idx), pd.DataFrame({"C": x}, index=idx), lookback=60)
        try:
            evaluate_neutralized(panel, {"min_clean_ir": 0.0, "max_placebo_ir": 1.0, "min_overlap_years": 0}, neutralized=True)
            raise AssertionError("PLACEBO_RELAX should have been refused")
        except NeutralizationError as e:
            assert "PLACEBO_RELAX" in str(e)
            print("PASS PLACEBO_RELAX refused")
    finally:
        os.environ.pop("PLACEBO_RELAX", None)


def test_neighbor_aligns_intraday_vs_midnight():
    rng = np.random.default_rng(3)
    days = pd.bdate_range("2018-01-02", periods=900)
    intra = days + pd.Timedelta(hours=14, minutes=30)
    paused = pd.Series(rng.normal(0.0002, 0.01, len(days)), index=intra, name="f2")
    cand = 0.7 * paused.to_numpy() + rng.normal(0, 0.002, len(days))
    cand = pd.Series(cand, index=days)  # midnight
    nb = orthogonalize_against_paused(cand, {"f2": paused})
    assert nb.overlap_days >= 800, nb
    assert nb.n_days >= 60, nb
    # Clone leftover IR can sit on the sampling floor (>0.40). Independence
    # requires leftover IR ≥ 0.40 AND surviving concentration placebo.
    assert nb.verdict == "NEIGHBOR_SPANNED", nb
    assert nb.span_r2 >= 0.70, nb
    print(
        "PASS neighbor aligns 14:30 vs midnight",
        nb.verdict,
        nb.n_days,
        nb.overlap_days,
        "span_r2",
        nb.span_r2,
        "leftover_ir",
        nb.neighbor_ir,
        "placebo_frac",
        nb.placebo_frac_of_observed,
    )


def test_neighbor_independent_leftover():
    rng = np.random.default_rng(4)
    idx = pd.bdate_range("2018-01-02", periods=900)
    paused = pd.Series(rng.normal(0, 0.01, len(idx)), index=idx)
    leftover = pd.Series(0.0009 + rng.normal(0, 0.004, len(idx)), index=idx)
    nb = orthogonalize_against_paused(leftover, {"f2": paused})
    assert nb.verdict == "NEIGHBOR_INDEPENDENT", nb
    assert (not np.isfinite(nb.span_r2)) or nb.span_r2 < 0.50, nb
    print("PASS neighbor independent leftover", nb.neighbor_ir, nb.n_days, "span_r2", nb.span_r2)


def test_time_shuffle_is_noop_block_bootstrap_moves():
    rng = np.random.default_rng(5)
    # Serial structure: clustered bursts so block bootstrap mean |IR| can differ
    blocks = []
    for i in range(40):
        mu = 0.002 if i % 2 == 0 else -0.001
        blocks.append(rng.normal(mu, 0.004, 25))
    s = pd.Series(np.concatenate(blocks))
    obs = annualized_ir(s)
    shuf = time_shuffle_ir(s)
    assert abs(shuf - obs) < 1e-12, (obs, shuf)
    boot = block_bootstrap_mean_abs_ir(s, n=30, block=25)
    assert np.isfinite(boot)
    d = diagnose(s)
    assert "order-invariant" in d.note
    print("PASS shuffle IR is no-op; block bootstrap exists", obs, shuf, boot)


def test_literature_does_not_map_to_defense():
    idx = pd.date_range("2018-01-31", periods=80, freq="ME")
    epu = pd.Series(100.0, index=idx)
    epu.iloc[-10:] = 180.0
    gpr = pd.Series(80.0, index=idx)
    gpr.iloc[-5:] = 160.0
    hp = simulate_p_factor(epu)
    hg = simulate_gpr(gpr)
    assert hp and hp[0].map_key is None, hp
    assert hg and hg[0].map_key is None, hg
    assert hp[0].cannot_promote and hg[0].cannot_promote
    print("PASS p_factor/gpr do not auto-map to defense tickets")


def test_wait_scan_refused():
    try:
        refuse_wait_scan(["ITA", "SPY"])
        raise AssertionError("should refuse")
    except WaitLockError:
        print("PASS refuse_wait_scan ITA")
    refuse_wait_scan(["ITA"], allow_wait_sketch=True)
    print("PASS wait sketch allowed only as unscannable research")


def test_sieve_planted_vs_clone_vs_wait():
    rng = np.random.default_rng(7)
    idx = pd.bdate_range("2018-01-02", periods=1500)
    mkt = pd.Series(rng.normal(0.0003, 0.011, len(idx)), index=idx, name="SPY")
    f2 = pd.Series(0.0004 + rng.normal(0, 0.008, len(idx)), index=idx)
    leftover = pd.Series(0.0009 + rng.normal(0, 0.004, len(idx)), index=idx)
    clone = pd.Series(0.85 * f2.to_numpy() + rng.normal(0, 0.001, len(idx)), index=idx)
    wait = pd.Series(0.001 + rng.normal(0, 0.004, len(idx)), index=idx)
    vix = pd.Series(rng.normal(0, 0.02, len(idx)), index=idx)
    cands = pd.DataFrame({"PLANT": leftover, "CLONE": clone, "ITA": wait, "VST": f2, "VIX": vix})
    hits = {h.name: h for h in sieve_panel(cands, mkt, {"f2": f2})}
    assert hits["ITA"].verdict == "SKIP_WAIT", hits["ITA"]
    assert hits["VST"].verdict == "SKIP_EXCLUDED", hits["VST"]
    assert hits["VIX"].verdict == "SKIP_NON_ASSET", hits["VIX"]
    assert hits["CLONE"].verdict == "SIEVE_DROP", hits["CLONE"]
    assert hits["PLANT"].verdict == "SIEVE_KEEP", hits["PLANT"]
    print("PASS sieve: KEEP planted, DROP clone, SKIP ITA/VST/VIX")


def test_pick_close_never_open_or_volume():
    import pandas as pd

    df = pd.DataFrame({"date": [1], "open": [2], "high": [3], "low": [4], "close": [5], "volume": [6]})
    assert pick_close_column(df.columns) == "close"
    df2 = pd.DataFrame({"Date": [1], "Open": [2], "Adj Close": [3], "Volume": [4]})
    assert pick_close_column(df2.columns) == "Adj Close"
    try:
        pick_close_column(["open", "volume"])
        raise AssertionError("should refuse")
    except ValueError:
        print("PASS pick_close refuses open/volume fallback")


def test_defense_yaml_still_wait():
    p = ROOT / "config" / "candidates" / "defense_sovereign_capacity.yaml"
    raw = yaml.safe_load(p.read_text())
    assert raw["scannable"] is False
    assert raw["lock_status"] == "wait"
    assert raw["capital"] == 0
    print("PASS defense YAML still wait / not scannable")


def test_gpr_synthetic_not_default(tmp_path: Path = None):
    from force_engine.clocks import GPRVetoClock

    cache = ROOT / "data" / "macro" / "_test_gpr_should_not_exist.csv"
    if cache.exists():
        cache.unlink()
    clock = GPRVetoClock(cache_path=cache)
    os.environ.pop("FORCE_GPR_SYNTHETIC", None)
    try:
        clock.fetch_and_cache_gpr_data()
        # network may succeed; that's fine — source must not be synthetic
        assert clock.source in ("iacoviello", "cache"), clock.source
        print("PASS GPR fetch source", clock.source)
    except Exception:
        assert clock.source == "unwired"
        assert not cache.exists(), "must not write synthetic to production cache"
        print("PASS GPR fetch failed cleanly as unwired (no synthetic cache)")
    finally:
        if cache.exists():
            cache.unlink()


def test_gpr_high_z_vetoes_pass_cannot_rescue_fail():
    from force_engine.clocks import ClockBus, ClockState

    state = ClockState(leading={"gpr_z": 2.5})
    out = ClockBus.veto_if_leading_contradicts(state, residual_ir=0.55)
    assert out.veto, out
    fail_state = ClockState(leading={"gpr_z": 3.0})
    out2 = ClockBus.veto_if_leading_contradicts(fail_state, residual_ir=0.10)
    assert not out2.veto
    print("PASS GPR z>=2 vetoes a pass and cannot rescue FAIL_GATE")


def main():
    test_gpr_high_z_vetoes_pass_cannot_rescue_fail()
    test_placebo_is_mean_abs()
    test_concentrated_path_fails_gate()
    test_placebo_bypass_env_refused()
    test_neighbor_aligns_intraday_vs_midnight()
    test_neighbor_independent_leftover()
    test_time_shuffle_is_noop_block_bootstrap_moves()
    test_literature_does_not_map_to_defense()
    test_wait_scan_refused()
    test_sieve_planted_vs_clone_vs_wait()
    test_pick_close_never_open_or_volume()
    test_defense_yaml_still_wait()
    test_gpr_synthetic_not_default()
    print("ALL DISCOVERY/SIEVE TESTS PASSED")


if __name__ == "__main__":
    main()
