#!/usr/bin/env python3
"""Vault is acquisition, not T5 activation. Inventory is not a seed dump."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml


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
    assert spec["oecd_eurostat_breakthrough"] is False
    assert spec["national_accounts_breakthrough"] is False
    assert spec["measurement_dead_end"] is False
    assert spec["mapping_break"] == "residence_vs_territoriality"
    assert spec["closest_failed_candidate"]["status"] == "failed"
    assert spec["closest_failed_candidate"]["id"] == "nace_4941_opex_hire_or_reward"
    ids = refused_ids()
    for k in (
        "eurostat_sbs_pur_meur",
        "nace_4941_opex_hire_or_reward",
        "sna_esa_transport_margins",
        "naio_10_cp1620",
        "itf_infrastructure_spend",
    ):
        assert k in ids
    for label in (
        "SNA transport margins",
        "naio_10_cp1620",
        "NACE 49.41 opex / hire-or-reward tkm",
        "deflate cost by SPPI",
    ):
        try:
            refuse_cousin(label)
            raise AssertionError(f"cousin {label} must be refused")
        except UnitCostError:
            pass
    # last label is SPPI
    try:
        refuse_cousin("freight SPPI as cost deflator")
    except UnitCostError:
        pass
    else:
        raise AssertionError("SPPI must be refused")
    text = (ROOT / "docs" / "FS-0001-UNIT-COST-AUDIT.md").read_text()
    assert "Better ingredients are not a breakthrough" in text
    assert "T5_NO_RESULT" in text
    br = (ROOT / "docs" / "FS-0001-BREAKTHROUGH-OPTIONS.md").read_text()
    assert "territorial freight expenditure" in br
    assert "Attach instruments" in br
    print("PASS national accounts not a breakthrough; margins refused; T5 NO_RESULT")




def test_v2_not_frozen():
    from force_learning.vault.v2_physical import V2Error, assert_v2_not_frozen

    spec = assert_v2_not_frozen()
    assert spec["status"] == "MEASUREMENT_AUDIT_REQUIRED"
    assert spec["frozen"] is False
    assert spec["iea_eei_wired"] is False
    assert spec["cube_obtained"] is False
    assert spec["qualifying_truck_pairs"] == 0
    assert spec["qualifying_train_pairs"] == 0
    assert spec["inventory_verdict"] == "NO_RESULT"
    assert spec["reconstructed_panel_refused"] is True
    inv = json.loads((ROOT / "force_learning" / "vault" / "metadata" / "iea_cube_inventory.json").read_text())
    assert inv["qualifying_truck_pairs"] == 0
    assert 31 in inv["refused_counts"] and 27 in inv["refused_counts"]
    assert "reconstructed_iea_country_panel" in spec["refused"]
    names = [o["name"] for o in spec["observables"]]
    assert names == ["freight_energy_intensity", "aggregate_freight_activity"]
    frozen_dir = ROOT / "force_ideas" / "frozen"
    assert not (frozen_dir / "FS-0001.v2.yaml").exists()
    print("PASS v2 cube inventory empty; 31/27/25 panel refused")


def test_pair_census():
    from force_learning.vault.pair_census import assert_census

    spec = assert_census()
    assert spec["admitted_as_seeds"] is False
    assert spec["attractiveness_rank_refused"] is True
    by = {p["id"]: p for p in spec["pairs"]}
    assert by["OP-01"]["abandoned"] is False
    assert by["OP-01"]["grade"] == "X"
    assert by["OP-03"]["excellent"] is False
    assert by["OP-04"]["excellent"] is False
    assert by["OP-06"]["qualified"] is False
    assert by["OP-06"]["mix_contamination"] is True
    assert spec["immediate_testing_lead"] == "none"
    assert spec["hostile_test_permitted"] is False
    assert spec["memo_20260909_cand_eval"]["CAND-01"]["qualified"] is False
    assert spec["memo_20260909_cand_eval"]["CAND-06"]["abandoned"] is False
    assert "cand01_electricity_grade_A" in spec["refused"]
    assert not any(p.get("grade") in ("A", "B") for p in spec["pairs"])
    frozen_dir = ROOT / "force_ideas" / "frozen"
    assert list(frozen_dir.glob("*.yaml")) == [frozen_dir / "FS-0001.v1.yaml"]
    print("PASS pair census; electricity not A; freight not rejected; no testing lead")


def test_unfrozen_discovery():
    from force_learning.vault.unfrozen_discovery import assert_unfrozen

    spec = assert_unfrozen()
    by = {c["id"]: c for c in spec["candidates"]}
    assert spec["t0_issued"] is False
    assert spec["admitted_as_seeds"] is False
    assert spec["new_frozen_forces_this_quarter"] == 0
    assert by["UD-01"]["classification"] == "PROMISING_FOR_T0_REVIEW"
    assert by["UD-01"]["lag_test_permitted"] is False
    assert by["UD-07"]["classification"] == "DUPLICATE_OF_EXISTING_FORCE"
    assert by["UD-07"]["promising"] is False
    assert by["UD-01"]["cf_same_period_identity"] == "refused"
    assert by["UD-04"]["classification"] == "DATA_FEASIBILITY_PROBLEM"
    assert spec["rank_disagreement"]["winner"] == "none"
    assert spec["census_m3"] == "CONVENTIONAL_EXPLANATION_DOMINATES"
    claimed = yaml.safe_load((ROOT / "force_ideas" / "inventory" / "claimed_series.yaml").read_text())
    assert claimed["extracted"] is False
    assert claimed["order_test_run"] is False
    print("PASS unfrozen discovery; claimed IDs only; no order test; no rank winner")











def main():
    test_vault_not_activation()
    test_inventory()
    test_historical_study_no_result()
    test_unit_cost_not_constructible()
    test_v2_not_frozen()
    test_pair_census()
    test_unfrozen_discovery()
    test_docs()


    print("ALL VAULT/INVENTORY TESTS PASSED")




if __name__ == "__main__":
    main()
