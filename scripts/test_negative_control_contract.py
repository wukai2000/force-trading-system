#!/usr/bin/env python3
"""F1/F2/F3 are fixtures. Rescuing one is a framework regression."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from force_engine.false_discovery import distrust_framework_if_f2_looks_clean
from force_engine.false_discovery import NegativeControlAudit


AUDIT = ROOT / "data" / "meta" / "negative_control_audit.json"
CONTRACT = ROOT / "config" / "negative_controls.yaml"


def _audit_map(raw: dict) -> dict:
    out = {}
    for row in raw.get("controls") or []:
        out[str(row["force_id"])] = row
    return out


def test_contract_against_audit():
    spec = yaml.safe_load(CONTRACT.read_text())
    raw = json.loads(AUDIT.read_text())
    rows = _audit_map(raw)
    forbidden = set(spec.get("must_not_contain") or [])
    for fid, exp in (spec.get("controls") or {}).items():
        assert fid in rows, f"missing audit row {fid}"
        row = rows[fid]
        labels = set(row.get("labels") or [])
        for lab in exp.get("required_labels") or []:
            assert lab in labels, f"{fid} missing {lab}: {labels}"
        joined = " ".join(labels) + " " + str(row.get("expected_status") or "")
        for bad in forbidden:
            assert bad not in joined, f"{fid} contains forbidden {bad}"
        ir = float(row["observed_ir"])
        if "max_observed_ir" in exp:
            assert ir <= float(exp["max_observed_ir"]), f"{fid} IR {ir} too high"
        if "min_observed_ir" in exp:
            assert ir >= float(exp["min_observed_ir"]), f"{fid} IR {ir} lost attractiveness (not a revival)"
        if "min_ir_persistence" in exp:
            persist = float(row["concentration"]["ir_persistence_ratio"])
            assert persist >= float(exp["min_ir_persistence"]), f"{fid} persist {persist}"
            assert row["concentration"]["ir_persistence_kill"] is True
        assert row.get("cannot_promote") is True
        assert int(row.get("capital") or 0) == 0
        print(f"PASS {fid} status={exp['expected_status']} labels={sorted(labels)} ir={ir:.3f}")
    assert raw.get("distrust_framework") is False
    assert raw.get("force4_scanned") is False
    print("PASS audit still discriminates; Force 4 not scanned")


def test_distrust_hook():
    raw = json.loads(AUDIT.read_text())
    audits = []
    for row in raw["controls"]:
        audits.append(
            NegativeControlAudit(
                force_id=row["force_id"],
                research_role="negative_control",
                source=row.get("source") or "",
                n_days=int(row.get("n_days") or 0),
                observed_ir=float(row["observed_ir"]),
                sign_null=row["sign_null"],
                block_bootstrap=row["block_bootstrap"],
                concentration=row["concentration"],
                labels=list(row["labels"]),
                audit_questions=row.get("audit_questions") or {},
            )
        )
    assert distrust_framework_if_f2_looks_clean(audits) is False
    rescued = NegativeControlAudit(
        force_id="f2_oos_hedged",
        research_role="negative_control",
        source="synthetic",
        n_days=100,
        observed_ir=0.9,
        sign_null={"empirical_p_value_one_sided": 0.01},
        block_bootstrap={},
        concentration={"ir_persistence_kill": False, "ir_persistence_ratio": 0.1},
        labels=[],
        audit_questions={},
    )
    assert distrust_framework_if_f2_looks_clean([rescued]) is True
    print("PASS distrust hook fires only if F2 is rescued")


def main():
    test_contract_against_audit()
    test_distrust_hook()
    print("ALL NEGATIVE-CONTROL CONTRACT TESTS PASSED")


if __name__ == "__main__":
    main()
