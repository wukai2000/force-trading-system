#!/usr/bin/env python3
"""
Architecture tests — no Force 3 market data.

Proves the F1/F2 failure mode is now caught *before* a candidate is scored:
  - basket = β·controls + noise  → FAIL_GATE (IR ~ 0)
  - evaluate() without neutralized=True → raises
  - empty controls → NeutralizationError
  - planted residual alpha survives OLS vs the same controls
  - pipeline.evaluate_candidate is the only supported path
  - leading clocks veto a pass; they cannot rescue a fail
  - tradable != residual_spread is refused
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd

from force_engine.clocks import ClockBus, ClockState
from force_engine.evaluate import evaluate_neutralized
from force_engine.neutralize import NeutralizationError, neutralize_prices, rolling_ols_residual
from force_engine.pipeline import CandidateSpec, evaluate_candidate, spec_from_yaml


def _synth(n=1500, seed=7):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2018-01-02", periods=n)
    xlv = rng.normal(0.0003, 0.012, n)
    xbi = rng.normal(0.0002, 0.018, n)
    return idx, xlv, xbi, rng


GATE = {
    "min_clean_ir": 0.40,
    "max_placebo_ir": 0.15,
    "min_overlap_years": 4,
    "max_abs_mean_beta_XLV": 0.80,
    "max_abs_mean_beta_XBI": 0.80,
}


def test_stealth_factor_fails_gate():
    idx, xlv, xbi, rng = _synth()
    # F1/F2 clone: legs are just leveraged XLV+XBI
    basket = 0.7 * xlv + 0.5 * xbi + rng.normal(0, 0.002, len(idx))
    controls = pd.DataFrame({"XLV": xlv, "XBI": xbi}, index=idx)
    panel = rolling_ols_residual(pd.Series(basket, index=idx), controls, lookback=60)
    result = evaluate_neutralized(panel, GATE, neutralized=True)
    assert result.verdict == "FAIL_GATE", result
    print("PASS stealth-factor FAIL_GATE", result.metrics["clean_ir"], result.failures)


def test_planted_alpha_can_pass():
    idx, xlv, xbi, rng = _synth()
    basket = 0.3 * xlv + 0.2 * xbi + 0.0008 + rng.normal(0, 0.004, len(idx))
    controls = pd.DataFrame({"XLV": xlv, "XBI": xbi}, index=idx)
    panel = rolling_ols_residual(pd.Series(basket, index=idx), controls, lookback=60)
    gate = dict(GATE)
    gate["max_placebo_ir"] = 1.0  # planted series is always-positive
    result = evaluate_neutralized(panel, gate, neutralized=True)
    assert result.metrics["clean_ir"] >= 0.40, result
    assert abs(result.metrics["mean_betas"]["XLV"]) < 0.80
    print("PASS planted-alpha IR", result.metrics["clean_ir"], "verdict", result.verdict)


def test_refuses_unmarked_evaluation():
    idx, xlv, xbi, rng = _synth(n=400)
    controls = pd.DataFrame({"XLV": xlv, "XBI": xbi}, index=idx)
    panel = rolling_ols_residual(pd.Series(xlv, index=idx), controls, lookback=60)
    try:
        evaluate_neutralized(panel, {"min_clean_ir": 0.40}, neutralized=False)
        raise AssertionError("should have refused")
    except NeutralizationError:
        print("PASS unmarked evaluation refused")


def test_refuses_empty_controls():
    idx, xlv, xbi, rng = _synth(n=300)
    prices = pd.DataFrame({"IHF": 100 * (1 + xlv).cumprod(), "XLV": 100 * (1 + xlv).cumprod()}, index=idx)
    try:
        neutralize_prices(prices, ["IHF"], controls=[], lookback=60)
        raise AssertionError("should have refused")
    except NeutralizationError:
        print("PASS empty controls refused")


def _prices_from_rets(idx, legs_rets, ctrl_rets):
    px = {}
    for name, r in {**legs_rets, **ctrl_rets}.items():
        px[name] = 100 * (1 + pd.Series(r, index=idx)).cumprod()
    return pd.DataFrame(px)


def test_pipeline_neutralizes_before_gate():
    idx, xlv, xbi, rng = _synth()
    # stealth factor through the pipeline
    ihf = 0.7 * xlv + 0.5 * xbi + rng.normal(0, 0.002, len(idx))
    ihi = 0.65 * xlv + 0.45 * xbi + rng.normal(0, 0.002, len(idx))
    xhs = 0.75 * xlv + 0.4 * xbi + rng.normal(0, 0.002, len(idx))
    prices = _prices_from_rets(
        idx,
        {"IHF": ihf, "IHI": ihi, "XHS": xhs},
        {"XLV": xlv, "XBI": xbi},
    )
    spec = CandidateSpec(
        force_id="longevity_healthspan_demand",
        legs=["IHF", "IHI", "XHS"],
        controls=["XLV", "XBI"],
        gate=GATE,
    )
    result = evaluate_candidate(spec, prices)
    assert result.gate.verdict == "FAIL_GATE", result.gate
    assert result.diagnostic["raw_basket_ir"] is not None
    print("PASS pipeline stealth FAIL_GATE", result.gate.metrics["clean_ir"])


def test_pipeline_refuses_long_only_tradable():
    idx, xlv, xbi, rng = _synth(n=400)
    prices = _prices_from_rets(idx, {"IHF": xlv}, {"XLV": xlv})
    spec = CandidateSpec(
        force_id="bad",
        legs=["IHF"],
        controls=["XLV"],
        gate=GATE,
        tradable="long_only",
    )
    try:
        evaluate_candidate(spec, prices)
        raise AssertionError("should have refused long_only")
    except NeutralizationError as e:
        assert "residual_spread" in str(e)
        print("PASS pipeline refuses long_only tradable")


def test_leading_clock_vetoes_pass_cannot_rescue_fail():
    idx, xlv, xbi, rng = _synth()
    # planted alpha that would pass
    alpha = 0.0008 + rng.normal(0, 0.004, len(idx))
    ihf = 0.3 * xlv + 0.2 * xbi + alpha
    prices = _prices_from_rets(
        idx,
        {"IHF": ihf, "IHI": ihf, "XHS": ihf},
        {"XLV": xlv, "XBI": xbi},
    )
    spec = CandidateSpec(
        force_id="longevity_healthspan_demand",
        legs=["IHF", "IHI", "XHS"],
        controls=["XLV", "XBI"],
        gate={**GATE, "max_placebo_ir": 1.0},
    )
    bus = ClockBus()
    bus.register_leading("credit_spreads", lambda: -2.0)
    result = evaluate_candidate(spec, prices, clock_bus=bus)
    assert result.clock.veto
    assert result.gate.verdict == "VETO_LEADING_CLOCK", result.gate
    print("PASS leading clock vetoed a passing residual")

    # failing residual cannot be rescued by a strongly positive leading clock
    stealth = 0.7 * xlv + 0.5 * xbi + rng.normal(0, 0.002, len(idx))
    prices_fail = _prices_from_rets(
        idx,
        {"IHF": stealth, "IHI": stealth, "XHS": stealth},
        {"XLV": xlv, "XBI": xbi},
    )
    bus2 = ClockBus()
    bus2.register_leading("patent_filings", lambda: 3.0)
    fail = evaluate_candidate(spec, prices_fail, clock_bus=bus2)
    assert fail.gate.verdict == "FAIL_GATE"
    assert not fail.clock.veto  # veto_if_leading_contradicts returns early on IR < 0.40
    print("PASS leading clock cannot rescue FAIL_GATE")


def test_force3_yaml_lock_unscanned():
    spec = spec_from_yaml(ROOT / "config" / "force3.yaml")
    assert spec.force_id == "longevity_healthspan_demand"
    assert spec.legs == ["IHF", "IHI", "XHS"]
    assert spec.controls == ["XLV", "XBI"]
    assert spec.tradable == "residual_spread"
    assert spec.gate["min_clean_ir"] == 0.40
    assert "patent_filings" in spec.leading_clocks
    assert "legislation" in spec.leading_clocks
    assert "credit_spreads" in spec.leading_clocks
    print("PASS force3.yaml lock matches pre-registered tickets")


def test_phase_a_force3_refuses_without_ack():
    import os
    import subprocess

    env = os.environ.copy()
    env.pop("FORCE3_LOCK_ACK", None)
    env["PYTHONPATH"] = str(ROOT)
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "phase_a_force3.py")],
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert "LOCKED" in proc.stdout
    print("PASS phase_a_force3.py refuses to scan without FORCE3_LOCK_ACK")


def test_clock_veto_helper_direct():
    state = ClockState(leading={"legislation": -2.2})
    out = ClockBus.veto_if_leading_contradicts(state, residual_ir=0.55)
    assert out.veto
    fail_state = ClockState(leading={"legislation": -2.2})
    out2 = ClockBus.veto_if_leading_contradicts(fail_state, residual_ir=0.10)
    assert not out2.veto
    print("PASS clock veto helper: pass can be vetoed, fail cannot be rescued")


def main():
    test_refuses_unmarked_evaluation()
    test_refuses_empty_controls()
    test_stealth_factor_fails_gate()
    test_planted_alpha_can_pass()
    test_pipeline_neutralizes_before_gate()
    test_pipeline_refuses_long_only_tradable()
    test_leading_clock_vetoes_pass_cannot_rescue_fail()
    test_force3_yaml_lock_unscanned()
    test_phase_a_force3_refuses_without_ack()
    test_clock_veto_helper_direct()
    print("ALL NEUTRALIZER TESTS PASSED")


if __name__ == "__main__":
    main()
