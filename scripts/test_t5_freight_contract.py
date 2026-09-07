#!/usr/bin/env python3
"""FS-0001 freight T5 audit: NO_RESULT is success. No silent inversion. No SPPI."""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from force_engine.freeze import FreezeError, attach_instruments, load_freeze
from force_ideas.t5_gate import t5_unlock_or_reason
from force_learning.observatory.resource_contract import report_fs0001

AUDIT = ROOT / "config" / "t5" / "fs0001_freight_contract.yaml"
HYP = ROOT / "config" / "hypotheses" / "FS-0001.yaml"


def test_audit_no_result():
    raw = yaml.safe_load(AUDIT.read_text())
    assert raw["hypothesis_id"] == "FS-0001"
    assert raw["status"] == "NO_RESULT"
    assert raw["t5_ready"] is False
    assert raw["unlock"] is False
    assert raw["prosecutor_allowed"] is False
    assert int(raw["capital"]) == 0
    assert raw["instruments"] == []
    assert raw["tickers"] == []
    assert raw["new_version_required"] is False
    print("PASS audit file is NO_RESULT / T5_READY false / not an unlock")


def test_unit_cost_sppi_refused():
    raw = yaml.safe_load(AUDIT.read_text())
    uc = raw["unit_cost"]
    assert uc["status"] == "unavailable"
    refused = [str(x).lower() for x in uc.get("refused_substitutes") or []]
    assert any("sppi" in x for x in refused)
    assert "no_harmonized_cross_country_cost_per_tkm" in str(uc.get("reason"))
    print("PASS unit cost unavailable; SPPI is a refused substitute")


def test_efficiency_inversion_not_silent():
    raw = yaml.safe_load(AUDIT.read_text())
    eff = raw["efficiency"]
    assert eff["native_measure"] == "I_TKM_E"
    assert eff["native_sign"] == -1
    assert eff["frozen_sign"] == +1
    assert eff["silent_inversion_allowed"] is False
    assert eff["frozen_observable_operationalized"] is False
    assert eff["status"] == "available_substrate"
    print("PASS I_TKM_E is substrate only; inversion not frozen")


def test_lead_horizon_unresolved():
    raw = yaml.safe_load(AUDIT.read_text())
    ll = raw["lead_lag"]
    assert ll["status"] == "unresolved"
    assert ll["rule"] is None
    assert ll["selection_after_outcomes"] is False
    print("PASS lead horizon unresolved; cannot infer from outcomes")


def test_hypothesis_fields_unmutated():
    hyp = yaml.safe_load(HYP.read_text())
    names = [o["name"] for o in hyp["observables"]]
    assert names == [
        "resource_efficiency_index",
        "resource_unit_cost",
        "aggregate_resource_use",
    ]
    signs = [int(o["predicted_sign"]) for o in hyp["observables"]]
    assert signs == [1, -1, 1]
    leads = [o["lead"] for o in hyp["observables"]]
    assert leads == ["leading", "leading", "contemporaneous"]
    assert hyp.get("tickers") == []
    print("PASS FS-0001 T0–T4 observables/signs/timing unmodified")


def test_t5_still_locked():
    fh = load_freeze(HYP)
    assert fh.freeze_complete
    try:
        attach_instruments(fh, ["AAA", "BBB"], ["SPY", "QQQ"])
        raise AssertionError("T5 must stay locked")
    except FreezeError:
        pass
    ok, reason = t5_unlock_or_reason("FS-0001")
    assert ok is False
    print("PASS attach_instruments refused:", reason)


def test_observatory_agrees():
    payload = report_fs0001()
    assert payload["t5_ready"] is False
    assert payload["status"] in {"NO_RESULT", "REFUSED"}
    assert payload["prosecutor_allowed"] is False
    assert payload["capital_allowed"] is False
    assert payload["instruments"] == []
    print("PASS observatory still NO_RESULT")


def test_docs():
    report = (ROOT / "docs" / "FS-0001-T5-DATA-CONTRACT-REPORT.md").read_text()
    matrix = (ROOT / "docs" / "FS-0001-T5-DATA-SOURCE-MATRIX.md").read_text()
    assert "NO_RESULT" in report
    assert "T5_READY: False" in report
    assert "No IR" in report
    assert "SPPI" in report and "SPPI" in matrix
    assert "I_TKM_E" in report
    print("PASS audit docs record NO_RESULT and the unit-cost failure")


def main():
    test_audit_no_result()
    test_unit_cost_sppi_refused()
    test_efficiency_inversion_not_silent()
    test_lead_horizon_unresolved()
    test_hypothesis_fields_unmutated()
    test_t5_still_locked()
    test_observatory_agrees()
    test_docs()
    print("ALL T5-FREIGHT-AUDIT TESTS PASSED")


if __name__ == "__main__":
    main()
