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
    import yaml

    light = ROOT / "force_ideas" / "data_contracts" / "FS-0001-lighting-v1.yaml"
    freight = ROOT / "force_ideas" / "data_contracts" / "FS-0001-freight-v1.yaml"
    idx = yaml.safe_load((ROOT / "force_ideas" / "data_contracts" / "index.yaml").read_text())
    assert idx["t5_resource"] == "freight"
    assert "lighting" in idx["observatory_only"]
    spec = yaml.safe_load(light.read_text())
    assert spec["resource_class"] == "lighting"
    assert spec.get("t5_candidate") is False
    assert refused_series_hits(spec) == ()
    fr = yaml.safe_load(freight.read_text())
    assert fr["resource_class"] == "freight"
    assert fr["lock"]["independent_geography"] == "European_Union"
    assert fr.get("instruments") == []
    assert str(fr["efficiency"]["series"]).upper() == "TBD"
    assert refused_series_hits(fr) == ()
    print("PASS lighting observatory-only; freight T5 preregistration TBD")



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
    assert payload["resource"] == "freight"
    assert payload["lighting_role"] == "observatory_only"
    assert payload["t5_ready"] is False
    assert payload["prosecutor_allowed"] is False
    assert payload["capital_allowed"] is False
    assert payload["instruments"] == []
    assert payload["status"] in {"NO_RESULT", "REFUSED"}
    assert payload["cells"]["efficiency_data"] == "NO_RESULT"
    assert payload["cells"]["second_geography"] == "PASS"
    md = ROOT / "docs" / "FS-0001-T5-DATA-CONTRACT-REPORT.md"
    assert md.exists()
    text = md.read_text()
    assert "No IR" in text
    assert "T5_READY: False" in text
    print("PASS observatory NO_RESULT, T5_READY false, EU named, markdown written")


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


def test_lock_cannot_silently_swap():
    import yaml
    from force_ideas.t5_gate import load_index

    idx = load_index()
    assert idx["t5_resource"] == "freight"
    freight = yaml.safe_load(
        (ROOT / "force_ideas" / "data_contracts" / "FS-0001-freight-v1.yaml").read_text()
    )
    assert freight["resource_class"] == freight["lock"]["resource_class"] == "freight"
    assert freight["lead_lag"]["search_after_returns"] is False
    print("PASS resource/geography/lead-lag locks intact")


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
    test_lock_cannot_silently_swap()
    test_rejected_mutation_file()
    print("ALL T5-CONTRACT TESTS PASSED")


if __name__ == "__main__":
    main()
