#!/usr/bin/env python3
"""EvidenceRecord: evidence / veto / promotion are separate. Promotion never automatic."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from force_engine.evidence import (
    PromotionError,
    no_result_record,
    record_from_residual,
    refuse_promote,
)
from force_engine.ledger import KINDS, append_entry, load_ledger
from force_engine.protocol import load_protocol, provenance


def test_protocol_lock():
    p = load_protocol()
    assert p["protocol_id"] == "FORCE_PROTOCOL_v1.0"
    assert p["cannot_promote"] is True
    assert p["capital"] == 0
    assert p["force4"] == "wait"
    assert p["promotion"] == "NOT_PERMITTED"
    assert p["no_result_is_success"] is True
    prov = provenance()
    assert prov["file_sha256"]["config/multilayer_gate.yaml"] != "missing"
    assert prov["promotion"] == "NOT_PERMITTED"
    print("PASS protocol v1.0 locked")


def test_attractive_residual_cannot_promote():
    rng = np.random.default_rng(7)
    n = 800
    r = pd.Series(0.0015 + rng.normal(0, 0.01, n))
    rec = record_from_residual(r, candidate_id="planted_not_a_force", n_sign=200, n_block=80)
    d = rec.to_dict()
    assert d["promotion"] == "NOT_PERMITTED"
    assert d["cannot_promote"] is True
    assert d["capital"] == 0
    assert "pass" not in str(d["null_a"]).lower() or "not a pass" in str(d["null_a"]).lower()
    for blk in d["null_b"].values():
        if isinstance(blk, dict):
            assert "pass" not in str(blk.get("note", "")).lower() or "not a pass" in str(blk.get("note", "")).lower()
    print(f"PASS planted residual IR={d['observed_ir']:.3f} status={d['evidence_status']} promotion=NOT_PERMITTED vetoes={d['vetoes']}")


def test_no_result_is_success():
    rec = no_result_record()
    assert rec.evidence_status == "no_result"
    assert rec.candidate_id == "NO_RESULT"
    assert rec.promotion == "NOT_PERMITTED"
    assert rec.capital == 0
    assert "success" in rec.note.lower()
    print("PASS no-result quarter is a success state")


def test_refuse_promote():
    try:
        refuse_promote()
        raise AssertionError("should refuse")
    except PromotionError:
        pass
    print("PASS refuse_promote")


def test_ledger_zero_for_blind():
    tmp = ROOT / "data" / "meta" / "_test_ledger.json"
    if tmp.exists():
        tmp.unlink()
    append_entry(
        kind="instrument_hardening",
        reason="FORCE_PROTOCOL_v1.0 EvidenceRecord",
        counts={k: 0 for k in KINDS},
        path=tmp,
    )
    data = load_ledger(tmp)
    assert data["entries"][-1]["intervention_count"] == 0
    tmp.unlink()
    print("PASS ledger records intervention_count=0")


def main():
    test_protocol_lock()
    test_attractive_residual_cannot_promote()
    test_no_result_is_success()
    test_refuse_promote()
    test_ledger_zero_for_blind()
    print("ALL EVIDENCE-RECORD TESTS PASSED")


if __name__ == "__main__":
    main()
