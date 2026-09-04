#!/usr/bin/env python3
"""Leading-observable catalog — veto-only, cannot promote."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from force_engine.clocks import ClockBus, ClockState
from force_engine.leading_observables import (
    TimingOverlayError,
    last_z,
    load_catalog,
    read_one,
    refuse_timing_overlay,
    report,
    signed_opposition,
    veto_flag,
)


def _write_series(path: Path, values, start="2018-01-01", freq="ME"):
    idx = pd.date_range(start, periods=len(values), freq=freq)
    df = pd.DataFrame({"value": values}, index=idx)
    df.index.name = "date"
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path)


def test_catalog_lock():
    cat = load_catalog()
    assert cat.cannot_promote is True
    assert cat.capital == 0
    assert cat.force4 == "wait"
    assert cat.refuse_timing_overlay is True
    refused = {o.id for o in cat.refused()}
    for name in (
        "port_congestion",
        "satellite_thermal",
        "ads_b_air_cargo",
        "linkedin_requisitions",
        "warn_act_nlp",
        "h1b_filings",
        "sec_mda_sentiment",
        "earnings_call_prosody",
        "lobbying_spend",
        "private_credit_covenants",
    ):
        assert name in refused, name
    wired_fred = cat.fred_map()
    assert "BAMLH0A0HYM2" in wired_fred
    assert "AWHMAN" in wired_fred
    assert "DRTSCILM" in wired_fred
    print("PASS catalog lock: refused theater, wired FRED subset, capital 0")


def test_signed_opposition_and_veto():
    cat = load_catalog()
    hy = cat.by_id("hy_oas")
    assert signed_opposition(2.0, "high_z") == -2.0
    assert signed_opposition(-2.0, "low_z") == -2.0
    assert signed_opposition(2.0, "never") is None
    assert veto_flag(2.0, hy) is True
    assert veto_flag(0.2, hy) is False
    freight = cat.by_id("cass_freight")
    assert veto_flag(-2.0, freight) is True
    assert veto_flag(2.0, freight) is False
    ism = cat.by_id("ism_supplier_deliveries")
    assert veto_flag(-3.0, ism) is False  # diagnostic, never
    print("PASS signed opposition matches ClockBus (more negative = oppose)")


def test_missing_cache_does_not_veto(tmp_path: Path):
    cat = load_catalog()
    r = read_one(cat.by_id("hy_oas"), macro_dir=tmp_path)
    assert r.status == "cache_missing"
    assert r.z is None
    assert r.veto_flag is False
    state = ClockState(leading={"credit_spreads": r.opposition})
    out = ClockBus.veto_if_leading_contradicts(state, residual_ir=0.55)
    assert not out.veto
    print("PASS missing cache → None → no veto, no promote")


def test_high_hy_vetoes_pass_not_fail(tmp_path: Path):
    cat = load_catalog()
    hist = np.concatenate([np.full(260, 4.0), np.array([8.0])])
    _write_series(tmp_path / "hy_oas.csv", hist, start="2018-01-01", freq="B")
    r = read_one(cat.by_id("hy_oas"), macro_dir=tmp_path)
    assert r.z is not None and r.z >= 1.5, r
    assert r.veto_flag is True
    assert r.opposition is not None and r.opposition <= -1.5
    state = ClockState(leading={"credit_spreads": r.opposition})
    out = ClockBus.veto_if_leading_contradicts(state, residual_ir=0.55)
    assert out.veto
    out2 = ClockBus.veto_if_leading_contradicts(
        ClockState(leading={"credit_spreads": r.opposition}), residual_ir=0.10
    )
    assert not out2.veto
    print("PASS high HY OAS vetoes PASS and cannot rescue FAIL")


def test_low_freight_vetoes_pass(tmp_path: Path):
    cat = load_catalog()
    hist = np.concatenate([np.full(48, 1.10), np.array([0.80])])
    _write_series(tmp_path / "cass_freight.csv", hist, start="2018-01-01", freq="ME")
    r = read_one(cat.by_id("cass_freight"), macro_dir=tmp_path)
    assert r.veto_flag is True, r
    state = ClockState(leading={"cass_freight": r.opposition})
    out = ClockBus.veto_if_leading_contradicts(state, residual_ir=0.70)
    assert out.veto
    print("PASS freight collapse vetoes a passing residual")


def test_refuse_timing_overlay():
    try:
        refuse_timing_overlay(pd.Series([0.01, -0.01]), pd.Series([1.0, 0.0]))
        raise AssertionError("should have refused")
    except TimingOverlayError:
        pass
    print("PASS IR(s_t, r_t) overlay refused")


def test_cli_refuses_promote_and_force4():
    env = {"PYTHONPATH": str(ROOT)}
    for flag in ("--promote", "--scan-force4", "--time-residual"):
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "run_leading_observables.py"), flag],
            cwd=str(ROOT),
            env={**__import__("os").environ, **env},
            capture_output=True,
            text=True,
        )
        assert proc.returncode == 2, proc.stdout + proc.stderr
        assert "REFUSED" in proc.stdout
    print("PASS CLI refuses --promote / --scan-force4 / --time-residual")


def test_report_never_promotes():
    payload = report()
    assert payload["cannot_promote"] is True
    assert payload["capital"] == 0
    assert payload["force4"] == "wait"
    print("PASS report cannot_promote")


def test_last_z_short_series_none():
    s = pd.Series([1.0, 1.1, 1.2])
    assert last_z(s, lookback=36) is None
    print("PASS short series is None, not a fake z")


def main():
    tmp = ROOT / "data" / "meta" / "_test_clocks"
    if tmp.exists():
        for p in tmp.glob("*.csv"):
            p.unlink()
    tmp.mkdir(parents=True, exist_ok=True)
    test_catalog_lock()
    test_signed_opposition_and_veto()
    test_missing_cache_does_not_veto(tmp)
    test_high_hy_vetoes_pass_not_fail(tmp)
    test_low_freight_vetoes_pass(tmp)
    test_refuse_timing_overlay()
    test_cli_refuses_promote_and_force4()
    test_report_never_promotes()
    test_last_z_short_series_none()
    print("ALL LEADING-OBSERVABLE TESTS PASSED")


if __name__ == "__main__":
    main()
