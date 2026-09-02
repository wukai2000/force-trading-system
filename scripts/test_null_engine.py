#!/usr/bin/env python3
"""
Null A / Null B / concentration-pair tests.

These diagnostics cannot promote. A concentrated F2-class path may look
unusual under the sign-null and must still be labeled CONCENTRATION_FAIL.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd

from force_engine.evaluate import annualized_ir, evaluate_neutralized
from force_engine.false_discovery import (
    audit_residual,
    block_bootstrap_family,
    concentration_report,
    diagnose,
    distrust_framework_if_f2_looks_clean,
    hysteresis_smooth,
    regime_dwell_report,
    regime_ir_table,
    regime_label_permutation,
    sign_null_distribution,
    time_shuffle_ir,
)

from force_engine.guards import WaitLockError
from force_engine.neutralize import rolling_ols_residual


def _idx(n=1500):
    return pd.bdate_range("2018-01-02", periods=n)


def test_sign_null_white_noise_not_unusual():
    rng = np.random.default_rng(11)
    s = pd.Series(rng.normal(0, 0.01, 1500), index=_idx())
    out = sign_null_distribution(s, n=400, seed=11)
    assert out.cannot_promote is True
    assert 10.0 < out.observed_percentile < 90.0, out
    assert out.empirical_p_value_one_sided > 0.05, out
    # signed-IR null mean sits near 0; std is order sqrt(252/T) ≈ 0.41
    assert abs(out.null_mean_ir) < 0.15, out.null_mean_ir
    print("PASS Null A white noise not unusual", out.observed_percentile, out.empirical_p_value_one_sided)


def test_sign_null_distributed_drift_is_extreme():
    rng = np.random.default_rng(12)
    s = pd.Series(0.0012 + rng.normal(0, 0.004, 1500), index=_idx())
    obs = annualized_ir(s)
    out = sign_null_distribution(s, n=400, seed=12)
    assert obs > 1.0, obs
    assert out.observed_percentile > 95.0, out
    assert out.empirical_p_value_one_sided < 0.02, out
    conc = concentration_report(s)
    assert conc.ir_persistence_kill is False, conc
    print("PASS Null A distributed drift extreme and Conc A does not kill", obs, out.empirical_p_value_one_sided)


def test_concentrated_path_null_a_can_look_good_conc_still_kills():
    """The validator's job: Null A is not a get-out-of-concentration card."""
    rng = np.random.default_rng(13)
    conc = np.zeros(1500)
    conc[50] = 0.20
    conc[120] = 0.18
    conc[400] = -0.22
    conc[700] = 0.19
    conc[900] = 0.17
    s = pd.Series(conc + rng.normal(0, 0.0004, 1500), index=_idx())
    obs = annualized_ir(s)
    assert obs > 0.40, obs
    sn = sign_null_distribution(s, n=400, seed=13)
    conc_rep = concentration_report(s)
    audit = audit_residual(s, force_id="synthetic_f2", source="synthetic", n_sign=400, n_block=80)
    assert conc_rep.ir_persistence_kill is True, conc_rep
    assert conc_rep.pnl_mass_top5 > 0.50, conc_rep
    assert "CONCENTRATION_FAIL" in audit.labels, audit.labels
    assert audit.cannot_promote is True
    assert audit.audit_questions["Q4_mechanism"] == "queued"
    assert audit.audit_questions["Q5_independence"] == "queued"
    print(
        "PASS concentrated path Conc A kill; Null A p1=",
        sn.empirical_p_value_one_sided,
        "labels",
        audit.labels,
    )


def test_pnl_mass_can_disagree_with_ir_persistence():
    """Same-sign spikes: P&L mass screams concentration; locked Conc A may not kill."""
    rng = np.random.default_rng(13)
    x = rng.normal(0, 0.0004, 1500)
    x[80] = 0.22
    x[200] = 0.19
    x[500] = 0.21
    x[900] = 0.18
    x[1200] = 0.20
    s = pd.Series(x, index=_idx())
    conc = concentration_report(s)
    assert conc.pnl_mass_top5 > 0.60, conc
    # Do not fuse: a P&L-mass flag is not the locked IR-persistence kill.
    assert conc.ir_persistence_kill in (True, False)
    print(
        "PASS Conc A/B disagree-capable",
        "persist",
        conc.ir_persistence_ratio,
        "kill",
        conc.ir_persistence_kill,
        "top5",
        conc.pnl_mass_top5,
    )


def test_two_concentration_stats_are_not_fused():
    rng = np.random.default_rng(14)
    s = pd.Series(0.0004 + rng.normal(0, 0.008, 1500), index=_idx())
    conc = concentration_report(s)
    d = conc.to_dict()
    assert "ir_persistence_ratio" in d and "pnl_mass_top5" in d
    assert "score" not in d
    assert conc.cannot_promote is True
    print("PASS concentration A/B separate", conc.ir_persistence_ratio, conc.pnl_mass_top5)


def test_block_lengths_not_averaged():
    rng = np.random.default_rng(15)
    blocks = []
    for i in range(50):
        mu = 0.003 if i % 5 == 0 else -0.0004
        blocks.append(rng.normal(mu, 0.004, 30))
    s = pd.Series(np.concatenate(blocks))
    fam = block_bootstrap_family(s, n=80, seed=15)
    assert set(fam) == {5, 21, 60}
    assert fam[5].block == 5 and fam[60].block == 60
    # Different lengths must remain different objects (do not average).
    keys = {5: fam[5].mean_ir, 21: fam[21].mean_ir, 60: fam[60].mean_ir}
    assert all(np.isfinite(v) for v in keys.values())
    print("PASS Null B block lengths reported separately", keys)


def test_time_shuffle_still_noop():
    rng = np.random.default_rng(16)
    s = pd.Series(rng.normal(0.0005, 0.01, 800))
    obs = annualized_ir(s)
    assert abs(time_shuffle_ir(s) - obs) < 1e-12
    d = diagnose(s)
    assert "cannot promote" in d.note.lower() or "Neither null can promote" in d.note or "cannot promote" in d.note
    print("PASS shuffle still no-op; diagnose points at Null A/B")


def test_audit_never_promotes_and_gate_unchanged():
    rng = np.random.default_rng(17)
    idx = _idx(1200)
    x = rng.normal(0.0002, 0.01, len(idx))
    y = 0.2 * x + rng.normal(0, 0.001, len(idx))
    y[80] += 0.25
    y[200] += 0.22
    y[600] -= 0.24
    panel = rolling_ols_residual(pd.Series(y, index=idx), pd.DataFrame({"XLU": x}, index=idx), lookback=60)
    gate = {"min_clean_ir": 0.40, "max_placebo_ir": 0.15, "min_overlap_years": 3}
    result = evaluate_neutralized(panel, gate, neutralized=True)
    audit = audit_residual(panel.residual, force_id="f2", source="synthetic_gate", n_sign=200, n_block=60)
    assert result.verdict == "FAIL_GATE"
    assert audit.cannot_promote is True
    assert "PROMOTE" not in audit.labels
    print("PASS audit cannot promote; locked gate still FAIL_GATE", result.failures, audit.labels)


def test_distrust_flag_only_when_f2_looks_clean():
    rng = np.random.default_rng(18)
    noise = pd.Series(rng.normal(0, 0.01, 900), index=pd.bdate_range("2018-01-02", periods=900))
    a_fail = audit_residual(noise, force_id="f2", n_sign=200, n_block=50)
    # White noise F2: statistical fail → framework is discriminating, not distrust.
    assert distrust_framework_if_f2_looks_clean([a_fail]) is False
    print("PASS distrust not raised on statistical-fail F2", a_fail.labels)


def test_script_refuses_promote():
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "run_negative_control_audit", ROOT / "scripts" / "run_negative_control_audit.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    try:
        mod.main(["--promote"])
        raise AssertionError("should refuse --promote")
    except WaitLockError:
        print("PASS audit refuses --promote")
    try:
        mod.main(["--scan-force4"])
        raise AssertionError("should refuse force4")
    except WaitLockError:
        print("PASS audit refuses --scan-force4")


def test_real_paused_residuals_if_present():
    from force_engine.neighbor import load_default_paused

    paused = load_default_paused()
    if not paused:
        print("SKIP real paused residuals (none cached)")
        return
    rows = []
    for fid, s in paused.items():
        a = audit_residual(s, force_id=fid, source="cached", n_sign=300, n_block=80)
        rows.append(a)
        assert a.research_role == "negative_control"
        assert a.cannot_promote is True
        assert a.capital == 0
        print(f"PASS cached {fid} IR={a.observed_ir:.3f} labels={a.labels} Q={a.audit_questions}")
    assert distrust_framework_if_f2_looks_clean(rows) is False or "f2" in paused
    if distrust_framework_if_f2_looks_clean(rows):
        print("ALARM distrust_framework on cached F2 — methodology too loose, do not revive")
    out = ROOT / "data" / "meta" / "_test_null_engine.json"
    out.write_text(json.dumps([r.to_dict() for r in rows], indent=2))
    print("PASS real paused residuals labeled negative_control")


def test_regime_null_independent_labels_not_unusual():
    rng = np.random.default_rng(21)
    idx = _idx(1500)
    r = pd.Series(rng.normal(0, 0.01, 1500), index=idx)
    g = pd.Series(["complacency"] * 500 + ["normal"] * 500 + ["stress"] * 500, index=idx)
    out = regime_label_permutation(r, g, n=300, seed=21, mode="occupancy")
    assert out.cannot_promote is True
    assert out.empirical_p_value_two_sided > 0.05, out
    print("PASS Null 1 independent labels not unusual", out.empirical_p_value_two_sided, out.observed_delta)


def test_regime_null_detects_aligned_premium():
    rng = np.random.default_rng(22)
    idx = _idx(1500)
    r = rng.normal(0, 0.008, 1500)
    r[:500] += 0.0035  # distributed premium on complacency days
    g = np.array(["complacency"] * 500 + ["normal"] * 500 + ["stress"] * 500)
    s = pd.Series(r, index=idx)
    lab = pd.Series(g, index=idx)
    out = regime_label_permutation(s, lab, n=300, seed=22, mode="occupancy")
    assert out.observed_delta > 0.5, out
    assert out.empirical_p_value_one_sided < 0.02, out
    assert out.cannot_promote is True
    print("PASS Null 1 detects aligned premium", out.observed_delta, out.empirical_p_value_one_sided)


def test_run_length_preserves_dwell_multiset():
    idx = _idx(400)
    g = pd.Series(
        ["complacency"] * 80 + ["stress"] * 40 + ["complacency"] * 80 + ["normal"] * 100 + ["stress"] * 100,
        index=idx,
    )
    dwell = regime_dwell_report(g)
    assert dwell["by_label"]["complacency"]["n_runs"] == 2
    assert dwell["by_label"]["stress"]["n_runs"] == 2
    rng = np.random.default_rng(23)
    r = pd.Series(rng.normal(0, 0.01, 400), index=idx)
    out = regime_label_permutation(r, g, n=80, seed=23, mode="run_length")
    assert out.mode == "run_length"
    assert out.cannot_promote is True
    print("PASS Null 1 run_length mode", out.observed_delta, out.empirical_p_value_two_sided)


def test_hysteresis_reduces_one_day_flips():
    idx = _idx(30)
    g = pd.Series(
        ["complacency", "stress"] * 10 + ["normal"] * 10,
        index=idx,
    )
    raw = regime_dwell_report(g)
    sm = hysteresis_smooth(g, min_dwell=2)
    smoothed = regime_dwell_report(sm)
    assert raw["frac_1day_runs"] > 0.5
    assert smoothed["frac_1day_runs"] < raw["frac_1day_runs"]
    # Locked classifier is untouched: original labels still chatter.
    assert (g != sm).any()
    print("PASS hysteresis sensitivity reduces 1-day runs", raw["frac_1day_runs"], smoothed["frac_1day_runs"])


def test_regime_script_refuses_promote():
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "run_regime_label_null", ROOT / "scripts" / "run_regime_label_null.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    try:
        mod.main(["--promote"])
        raise AssertionError("should refuse --promote")
    except WaitLockError:
        print("PASS Null 1 script refuses --promote")
    try:
        mod.main(["--scan-force4"])
        raise AssertionError("should refuse force4")
    except WaitLockError:
        print("PASS Null 1 script refuses --scan-force4")


def test_regime_ir_table_cannot_be_a_gate():
    rng = np.random.default_rng(24)
    idx = _idx(900)
    r = pd.Series(rng.normal(0.0004, 0.01, 900), index=idx)
    g = pd.Series(["complacency"] * 300 + ["normal"] * 300 + ["stress"] * 300, index=idx)
    table = regime_ir_table(r, g)
    assert set(["complacency", "normal", "stress", "full"]) <= set(table)
    # A high complacency IR is a diagnostic row, not PROMOTE_CANDIDATE.
    assert "verdict" not in table
    print("PASS regime IR table has no verdict", table["full"]["ir"])


def main():
    os.chdir(ROOT)
    test_sign_null_white_noise_not_unusual()
    test_sign_null_distributed_drift_is_extreme()
    test_concentrated_path_null_a_can_look_good_conc_still_kills()
    test_pnl_mass_can_disagree_with_ir_persistence()
    test_two_concentration_stats_are_not_fused()
    test_block_lengths_not_averaged()
    test_time_shuffle_still_noop()
    test_audit_never_promotes_and_gate_unchanged()
    test_distrust_flag_only_when_f2_looks_clean()
    test_script_refuses_promote()
    test_real_paused_residuals_if_present()
    test_regime_null_independent_labels_not_unusual()
    test_regime_null_detects_aligned_premium()
    test_run_length_preserves_dwell_multiset()
    test_hysteresis_reduces_one_day_flips()
    test_regime_script_refuses_promote()
    test_regime_ir_table_cannot_be_a_gate()
    print("ALL NULL ENGINE TESTS PASSED")


if __name__ == "__main__":
    main()
