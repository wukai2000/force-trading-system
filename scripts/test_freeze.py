#!/usr/bin/env python3
"""T0–T4 freeze guard — no prices, no Force 4."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
import yaml

from force_engine.discovery import ForceDiscoveryEngine
from force_engine.false_discovery import diagnostic_dsr, diagnostic_legacy_time_shuffle, time_shuffle_ir
from force_engine.freeze import (
    FreezeError,
    FrozenHypothesis,
    attach_instruments,
    hypothesis_from_mapping,
    load_freeze,
    refuse_evaluate_unfrozen,
)
from force_engine.guards import RecycleError, WaitLockError
from force_engine.pipeline import CandidateSpec, evaluate_candidate


def _complete_raw(**over):
    raw = {
        "hypothesis_id": "example_not_a_candidate",
        "hypothesis": "Inelastic physical capacity lags committed demand by more than a year.",
        "mechanism": "Lead times on specialized capex cannot clear a committed demand shock quickly.",
        "observables": [
            {
                "name": "order_backlog_months",
                "predicted_sign": 1,
                "lead": "leading",
                "absent_kills": True,
            }
        ],
        "independence_dimensions": [
            {"kind": "geography", "note": "not the same listing country"},
            {"kind": "instrument", "note": "not a US sector ETF cousin"},
        ],
        "tickers": [],
        "controls": [],
        "scannable": False,
        "capital": 0,
    }
    raw.update(over)
    return raw


def test_template_is_incomplete():
    fh = load_freeze(ROOT / "config" / "hypotheses" / "_TEMPLATE.yaml")
    assert fh.freeze_complete is False
    assert "T0_hypothesis" in fh.missing
    assert fh.scannable is False
    assert fh.capital == 0
    print("PASS template incomplete", fh.missing)


def test_incomplete_cannot_claim_complete():
    raw = _complete_raw(hypothesis="", freeze_complete=True)
    try:
        hypothesis_from_mapping(raw)
        raise AssertionError("should refuse claimed complete")
    except FreezeError as e:
        assert "missing" in str(e).lower() or "T0" in str(e)
        print("PASS claimed freeze_complete refused")


def test_tickers_before_t4_refused():
    raw = _complete_raw(hypothesis="short", tickers=["AAA"])
    try:
        hypothesis_from_mapping(raw)
        raise AssertionError("should refuse tickers")
    except FreezeError as e:
        assert "tickers" in str(e).lower()
        print("PASS tickers before T0–T4 refused")


def test_wait_tickers_in_freeze_refused():
    raw = _complete_raw(tickers=["ITA", "XAR"])
    try:
        hypothesis_from_mapping(raw)
        raise AssertionError("should refuse WAIT")
    except WaitLockError:
        print("PASS freeze WAIT tickers refused")


def test_lagging_only_not_complete():
    raw = _complete_raw(
        observables=[{"name": "price_itself", "predicted_sign": 1, "lead": "lagging"}]
    )
    fh = hypothesis_from_mapping(raw)
    assert fh.freeze_complete is False
    assert "T2_at_least_one_leading_observable" in fh.missing
    print("PASS lagging-only is not freeze_complete")


def test_complete_then_attach_then_mismatch():
    fh = hypothesis_from_mapping(_complete_raw())
    assert fh.freeze_complete
    assert fh.tickers == []
    try:
        attach_instruments(fh, ["ITA"], ["SPY"])
        raise AssertionError("WAIT attach should fail")
    except WaitLockError:
        pass
    try:
        attach_instruments(fh, ["VST"], ["XLU"])
        raise AssertionError("recycle attach should fail")
    except RecycleError:
        pass
    out = attach_instruments(fh, ["AAA", "BBB"], ["SPY", "QQQ"])
    assert out.instruments_attached
    assert out.tickers == ["AAA", "BBB"]
    assert out.scannable is False
    assert out.cannot_promote is True
    print("PASS attach after freeze; WAIT/recycle still refused")


def test_evaluate_new_id_without_freeze_refused():
    idx = pd.bdate_range("2018-01-02", periods=80)
    rng = np.random.default_rng(0)
    prices = pd.DataFrame(
        {
            "AAA": 100 * np.exp(np.cumsum(rng.normal(0, 0.01, len(idx)))),
            "SPY": 100 * np.exp(np.cumsum(rng.normal(0, 0.01, len(idx)))),
        },
        index=idx,
    )
    spec = CandidateSpec(
        force_id="brand_new_leftover",
        legs=["AAA"],
        controls=["SPY"],
        gate={"min_clean_ir": 0.0, "max_placebo_ir": 1.0, "min_overlap_years": 0},
    )
    try:
        evaluate_candidate(spec, prices)
        raise AssertionError("should freeze-refuse")
    except FreezeError as e:
        assert "T0" in str(e) or "freeze" in str(e).lower()
        print("PASS evaluate_candidate new id without freeze refused")


def test_grandfathered_still_evaluates():
    idx = pd.bdate_range("2018-01-02", periods=400)
    rng = np.random.default_rng(1)
    x = rng.normal(0.0002, 0.01, len(idx))
    prices = pd.DataFrame(
        {
            "IHF": 100 * np.exp(np.cumsum(0.7 * x + rng.normal(0, 0.002, len(idx)))),
            "XLV": 100 * np.exp(np.cumsum(x)),
        },
        index=idx,
    )
    spec = CandidateSpec(
        force_id="longevity_healthspan_demand",
        legs=["IHF"],
        controls=["XLV"],
        gate={"min_clean_ir": 0.40, "max_placebo_ir": 0.15, "min_overlap_years": 0.5},
    )
    result = evaluate_candidate(spec, prices)
    assert result.gate.verdict in ("FAIL_GATE", "PROMOTE_CANDIDATE", "VETO_LEADING_CLOCK")
    print("PASS grandfathered F3 id still evaluates", result.gate.verdict)


def test_discovery_cannot_name_new_legs_without_freeze(tmp_path=None):
    eng = ForceDiscoveryEngine()
    out_dir = str(ROOT / "config" / "hypotheses")
    try:
        eng.generate_candidate_yaml_spec(
            "Fresh_Leftover",
            legs=["AAA"],
            controls=["SPY"],
            output_dir=out_dir,
            scannable=False,
        )
        raise AssertionError("should freeze-refuse")
    except FreezeError:
        print("PASS discovery cannot name new legs without freeze")
    try:
        eng.generate_candidate_yaml_spec(
            "Fresh_Leftover",
            legs=["AAA"],
            controls=["SPY"],
            output_dir=out_dir,
            scannable=True,
        )
        raise AssertionError("scannable should be refused")
    except FreezeError:
        print("PASS discovery cannot write scannable=true")


def test_discovery_wait_sketch_still_allowed(tmp_path=None):
    eng = ForceDiscoveryEngine()
    out_dir = str(ROOT / "data" / "meta")
    path = eng.generate_candidate_yaml_spec(
        "Defense_WAIT_unit",
        legs=["ITA", "XAR", "PPA"],
        controls=["XLI", "SPY"],
        output_dir=out_dir,
        scannable=False,
    )
    raw = yaml.safe_load(Path(path).read_text())
    assert raw["scannable"] is False
    assert raw["capital"] == 0
    Path(path).unlink()
    print("PASS discovery wait sketch still allowed scannable=false")


def test_aliases_are_legacy_not_null_engine():
    rng = np.random.default_rng(3)
    s = pd.Series(rng.normal(0.0003, 0.01, 400))
    a = time_shuffle_ir(s)
    b = diagnostic_legacy_time_shuffle(s)
    assert a == b
    d = diagnostic_dsr(s)
    assert np.isfinite(d)
    print("PASS diagnostic aliases exist and time_shuffle is the no-op probe")


def test_refuse_helper_on_wait():
    try:
        refuse_evaluate_unfrozen("new_thing", ["ITA", "SPY"])
        raise AssertionError("WAIT should raise")
    except WaitLockError:
        print("PASS refuse_evaluate_unfrozen hits WAIT first")


def main():
    test_template_is_incomplete()
    test_incomplete_cannot_claim_complete()
    test_tickers_before_t4_refused()
    test_wait_tickers_in_freeze_refused()
    test_lagging_only_not_complete()
    test_complete_then_attach_then_mismatch()
    test_evaluate_new_id_without_freeze_refused()
    test_grandfathered_still_evaluates()
    test_discovery_cannot_name_new_legs_without_freeze()
    test_discovery_wait_sketch_still_allowed()
    test_aliases_are_legacy_not_null_engine()
    test_refuse_helper_on_wait()
    print("ALL FREEZE TESTS PASSED")


if __name__ == "__main__":
    main()
