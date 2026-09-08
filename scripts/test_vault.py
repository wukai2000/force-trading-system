#!/usr/bin/env python3
"""Vault is acquisition, not T5 activation. Inventory is not a seed dump."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from force_ideas.inventory.catalog import summary
from force_ideas.state import fs0001_desk
from force_learning.vault.vault import assert_not_activation, report


def test_vault_not_activation():
    assert_not_activation()
    payload = report()
    assert payload["t5_ready"] is False
    assert payload["episode_search"] is False
    assert payload["unit_cost_status"] == "critical_blocker"
    assert payload["capital"] == 0
    assert payload.get("decision") == "NO_RESULT"
    desk = fs0001_desk()
    assert desk["t5_status"] == "NO_RESULT"
    assert desk["research_state"] == "T5_NO_RESULT"
    print("PASS vault does not unlock T5; unit cost still blocker")


def test_inventory():
    st = summary()
    assert st["n_items"] == 20
    assert st["admitted_as_seeds"] is False
    assert st["already_frozen"] == ["PX-04"]
    assert "PX-10" in st["cousins_refused"]
    assert st["active_frozen"] == ["FS-0001"]
    assert st["ticker_hits"] == []
    assert st["by_status"]["inventory_only"] == 18
    print("PASS 20-item inventory; PX-04 is FS-0001; PX-10 refused; no tickers")


def test_historical_study_no_result():
    from force_learning.vault.coverage import OUT

    assert OUT.exists(), "coverage.json must be committed"
    cov = json.loads(OUT.read_text())
    assert cov.get("t5_ready") is False
    assert cov.get("decision") == "NO_RESULT"
    assert cov.get("new_version_required") is False
    assert cov.get("episode_search") is False
    assert cov["unit_cost"]["status"] == "critical_blocker"
    assert cov["unit_cost"].get("sppi_refused") is True
    assert cov["aggregate_use"]["window_2000_2024"]["n_geo"] >= 50
    study = (ROOT / "docs" / "FS-0001-HISTORICAL-STUDY.md").read_text()
    assert "NO_RESULT" in study and "No tickers" in study
    print("PASS historical study remains NO_RESULT; OECD tkm coverage present")


def test_docs():
    text = (ROOT / "docs" / "OBSERVABLE_INVENTORY.md").read_text()
    assert "Not admitted" in text
    feas = (ROOT / "force_learning" / "vault" / "feasibility.yaml").read_text()
    assert "episode_search: false" in feas
    print("PASS inventory + feasibility docs")


def test_unit_cost_not_constructible():
    from force_learning.vault.unit_cost import (
        UnitCostError,
        assert_not_constructible,
        refuse_cousin,
        refused_ids,
    )

    spec = assert_not_constructible()
    assert spec["verdict"] == "NOT_CONSTRUCTIBLE_WITHOUT_DISCRETION"
    assert spec["t5_ready"] is False
    assert spec["preregistered_construction_rule"] == "none"
    assert spec["joint_cost_tkm_coverage"] == "empty"
    ids = refused_ids()
    for k in ("eurostat_sbs", "eurostat_sppi", "us_bts_revenue_per_ton_mile", "cass_drewry_bdi"):
        assert k in ids
    for label in ("Eurostat SBS turnover", "SPPI road freight", "Cass Freight Index", "BTS ton-mile"):
        try:
            refuse_cousin(label)
            raise AssertionError(f"cousin {label} must be refused")
        except UnitCostError:
            pass
    text = (ROOT / "docs" / "FS-0001-UNIT-COST-AUDIT.md").read_text()
    assert "NOT_CONSTRUCTIBLE_WITHOUT_DISCRETION" in text
    print("PASS unit cost not constructible; cousins refused; T5 stays NO_RESULT")


def main():
    test_vault_not_activation()
    test_inventory()
    test_historical_study_no_result()
    test_unit_cost_not_constructible()
    test_docs()
    print("ALL VAULT/INVENTORY TESTS PASSED")



if __name__ == "__main__":
    main()
