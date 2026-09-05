#!/usr/bin/env python3
"""FS-0001 lighting T5 contract. Freight FRED overlay refused. No instruments."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from force_engine.freeze import FreezeError, attach_instruments, load_freeze
from force_ideas.t5_gate import REFUSED_FS0001_V1_SERIES, refused_series_hits, t5_unlock_or_reason
from force_learning.observatory.resource_contract import report_fs0001


def test_contract_on_disk():
    p = ROOT / "force_ideas" / "data_contracts" / "FS-0001-lighting-v1.yaml"
    assert p.exists()
    text = p.read_text()
    import yaml
    spec = yaml.safe_load(p.read_text())
    assert spec["resource_class"] == "lighting"
    assert spec["independent_geography"]["name"] == "European_Union"
    assert spec.get("instruments") == []
    assert refused_series_hits(spec) == ()
    print("PASS lighting contract on disk, no freight FRED ids")



def test_freight_overlay_refused():
    blob = "CASSEXP RAILFRTINTERMODAL TSIFRHT TSIFRGHT"
    hits = refused_series_hits(blob)
    assert "CASSEXP" in hits
    assert "RAILFRTINTERMODAL" in hits
    assert "TSIFRGHT" in hits
    print("PASS freight FRED overlay ids are on the refuse list", hits)


def test_observatory_no_result():
    payload = report_fs0001()
    assert payload["force_id"] == "FS-0001"
    assert payload["resource"] == "lighting"
    assert payload["t5_ready"] is False
    assert payload["prosecutor_allowed"] is False
    assert payload["capital_allowed"] is False
    assert payload["instruments"] == []
    assert payload["status"] in {"NO_RESULT", "REFUSED"}
    assert payload["cells"]["efficiency_data"] == "NO_RESULT"
    assert payload["cells"]["second_geography"] == "PASS"
    print("PASS observatory NO_RESULT, T5_READY false, EU named")


def test_fs0001_cannot_attach():
    fh = load_freeze(ROOT / "config" / "hypotheses" / "FS-0001.yaml")
    assert fh.freeze_complete
    assert fh.tickers == []
    try:
        attach_instruments(fh, ["AAA", "BBB"], ["SPY", "QQQ"])
        raise AssertionError("FS-0001 T5 should be locked")
    except FreezeError as e:
        msg = str(e).lower()
        assert "t5" in msg or "data contract" in msg or "observatory" in msg
    ok, reason = t5_unlock_or_reason("FS-0001")
    assert ok is False
    print("PASS FS-0001 attach_instruments refused:", reason)


def test_rejected_mutation_file():
    p = ROOT / "force_ideas" / "rejected" / "FS-0001-freight-fred-mutation.yaml"
    assert p.exists()
    text = p.read_text()
    assert "REJECTED" in text
    assert "CASSEXP" in text
    print("PASS freight mutation logged as rejected, not admitted")


def main():
    test_contract_on_disk()
    test_freight_overlay_refused()
    test_observatory_no_result()
    test_fs0001_cannot_attach()
    test_rejected_mutation_file()
    print("ALL T5-CONTRACT TESTS PASSED")


if __name__ == "__main__":
    main()
