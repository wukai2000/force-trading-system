#!/usr/bin/env python3
"""2026-09-23 census is screening. Qualifies labels are not live."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import yaml

SPEC = yaml.safe_load((ROOT / "force_ideas" / "inventory" / "ma_census_20260923.yaml").read_text())
DESK = yaml.safe_load((ROOT / "force_ideas" / "desk.yaml").read_text())
MISSION = yaml.safe_load((ROOT / "force_ideas" / "inventory" / "explorer_mission.yaml").read_text())
PRIOR = yaml.safe_load((ROOT / "force_ideas" / "inventory" / "architecture_census.yaml").read_text())
SURVEY = yaml.safe_load((ROOT / "force_ideas" / "inventory" / "physical_survey.yaml").read_text())
MEMO = (ROOT / "docs" / "MEMO_ARCHITECTURE_CENSUS_20260923.md").read_text()
ART = json.loads((ROOT / "artifacts" / "ma_census_20260923.json").read_text())
LAB = yaml.safe_load((ROOT / "force_ideas" / "inventory" / "force_lab.yaml").read_text())


def main() -> None:
    assert SPEC["id"] == "MA-CENSUS-20260923"
    assert SPEC["verdict"] == "PARTIAL_PROVENANCE_OPEN"
    assert SPEC["qualifies_live"] is False
    assert SPEC["deeper_audit_authorized"] is False
    assert SPEC["pair_reconstructed"] is False
    assert SPEC["n_seeds"] == 0
    assert SPEC["winner"] == "none"
    assert SPEC["e1i_reopened"] is False
    assert SPEC["independence_i4_claimed_as_proven"] is False
    assert SPEC["admitted_as_seeds"] is False
    assert SPEC["next_object"] == "stay_frozen"
    assert SPEC["scientific_lock"] == "c7f21fa"
    assert "QUALIFIES_FOR_DEEPER_AUDIT" in SPEC["not_verdict"]
    assert "QUALIFIES_FOR_VINTAGE_AUDIT" in SPEC["not_verdict"]
    assert "QUALIFIES_FOR_E2_VINTAGE_TEST" in SPEC["not_verdict"]
    assert "protocol_E2_unlocked" in SPEC["not_verdict"]
    by = {r["id"]: r for r in SPEC["rows"]}
    assert all(r["qualifies"] is False for r in SPEC["rows"])
    assert by["MA-CROP-RMA"]["status"] == "SCREENING"
    assert by["MA-SDR-NTSB"]["status"] == "SCREENING"
    assert by["MA-HYD-SPILL"]["status"] == "DISMISSED_AS_NEXT"
    assert by["MA-INSAR-MSHA"]["status"] == "DISMISSED"
    assert by["MA-COF-SLAUGHTER"]["status"] == "PARTIAL"
    assert by["MA-FIA-MTBS"]["status"] == "SCREENING"
    assert by["MA-FIA-MTBS"]["qualifies"] is False
    assert by["MA-FIA-MTBS"]["prior"] == "OA-FIA-MTBS-FIRE"
    assert by["MA-CEMS-EIA860"]["status"] == "DISMISSED"
    assert by["MA-CEMS-EIA860"]["qualifies"] is False
    assert by["MA-NBI-COMPLETION"]["status"] == "DISMISSED_AS_NEXT"
    assert by["MA-NBI-COMPLETION"]["qualifies"] is False
    assert by["MA-CROP-RMA"]["qualifies"] is False
    assert "RMA-universe intersection" in by["MA-CROP-RMA"]["note"]
    assert by["MA-MSHA-ACCIDENT"]["status"] == "SCREENING"
    assert by["MA-MSHA-ACCIDENT"]["qualifies"] is False
    assert by["MA-CEMS-GADS"]["status"] == "DISMISSED"
    assert by["MA-CEMS-GADS"]["qualifies"] is False
    assert by["MA-CEMS-GADS"]["prior"] == "C-EIA-860"
    assert "lees_ferry_2011_as_episode" in SPEC["refuse"]
    assert "economic_bridge_as_reason_to_keep" in SPEC["refuse"]
    assert "fia_mtbs_2010_cutoff_this_pass" in SPEC["refuse"]
    assert "cems_eia860_as_executed_audit" in SPEC["refuse"]
    assert "qualifies_for_vintage_audit_as_live" in SPEC["refuse"]
    assert "one_bridge_from_2014_nbi_this_pass" in SPEC["refuse"]
    assert "qualifies_for_e2_vintage_test_as_live" in SPEC["refuse"]
    assert "nass_rma_2005_july_freeze_this_pass" in SPEC["refuse"]
    assert "rma_universe_intersection_as_A" in SPEC["refuse"]
    assert "msha_accident_cohort_this_pass" in SPEC["refuse"]
    assert "cems_gads_as_executed_lock" in SPEC["refuse"]
    assert "placeholder_hash_as_freeze" in SPEC["refuse"]
    assert "protocol_e2_unlock_from_census" in SPEC["refuse"]
    assert "reopen_e1i" in SPEC["refuse"]
    assert any(m["id"] == "F11" for m in SPEC["new_modes"])
    assert DESK["next_object"] == "stay_frozen"
    assert DESK["n_seeds"] == 0
    assert DESK["capital"] == 0
    assert DESK["gate1"] == "FAIL"
    assert DESK["e1i_vintages_ok"] is False
    assert DESK["ma_census_20260923"] == "screening_not_audit"
    assert DESK["ma_census_pass2"] == "no_new_qualifies"
    assert DESK["ma_census_pass3"] == "no_new_qualifies"
    assert DESK["qualifies_labels_live"] is False
    assert DESK["se_ais_01"] == "candidate_for_gatekeeper_not_freeze"
    assert MISSION["census_size_this_quarter"] == 0
    assert "streamflow_dam_as_next" in MISSION["refused"]
    assert "qualifies_for_deeper_audit_as_live_status" in MISSION["refused"]
    assert "lees_ferry_2011_as_episode" in MISSION["refused"]
    assert "sdr_ntsb_as_experiment" in MISSION["refused"]
    assert "fia_mtbs_2010_cutoff_this_pass" in MISSION["refused"]
    assert "cems_eia860_as_executed_audit" in MISSION["refused"]
    assert "qualifies_for_vintage_audit_as_live" in MISSION["refused"]
    assert "one_bridge_from_2014_nbi_this_pass" in MISSION["refused"]
    assert "qualifies_for_e2_vintage_test_as_live" in MISSION["refused"]
    assert "nass_rma_2005_july_freeze_this_pass" in MISSION["refused"]
    assert "msha_accident_cohort_this_pass" in MISSION["refused"]
    assert "cems_gads_as_executed_lock" in MISSION["refused"]
    assert "placeholder_hash_as_freeze" in MISSION["refused"]
    assert "protocol_e2_unlock_from_census" in MISSION["refused"]
    assert "another_bridge_hunt" in MISSION["refused"]
    assert "nbi_as_qualifies" in MISSION["refused"]
    assert PRIOR["deeper_audit_authorized"] is False
    assert PRIOR["n_seeds"] == 0
    sdr = next(c for c in SURVEY["candidates"] if c["id"] == "OA-AIRCRAFT-SDR")
    assert sdr["status"] == "PARTIAL"
    assert sdr["qualifies"] is False
    assert sdr["independence_proven"] is False
    fire = next(c for c in SURVEY["candidates"] if c["id"] == "OA-FIA-MTBS-FIRE")
    assert fire["status"] == "SHAPE_INTERESTING"
    assert fire["qualifies"] is False
    assert fire["seed"] is False
    assert fire["independence_proven"] is False
    assert fire["collapse_if"] == "fia_own_fire_indicator_used_as_event"
    eia = next(c for c in PRIOR["transition_census_failures"] if c["id"] == "C-EIA-860")
    assert eia["status"] == "NO_RESULT"
    assert eia["reason"] == "electricity_domain_frozen"
    parked = next(c for c in PRIOR["parked_not_this_cycle"] if c["id"] == "OA-FIA-MTBS-FIRE")
    assert parked["status"] == "SHAPE_INTERESTING"
    assert parked["qualifies"] is False
    assert ART["verdict"] == "PARTIAL_PROVENANCE_OPEN"
    assert ART["note3_pass_stamps"] == "dismissed"
    assert ART["pass2"] == "no_new_qualifies"
    assert ART["claimed_cems_execution"] == "not_in_repo"
    assert ART["fia_2010_cutoff"] == "not_authorized"
    assert ART["one_bridge_2014"] == "not_authorized"
    assert ART["pass3"] == "no_new_qualifies"
    assert ART["protocol_e2"] == "LOCKED"
    assert ART["qualifies_for_e2_vintage_test"] == "not_live"
    assert ART["nass_rma_2005_july"] == "not_authorized"
    assert ART["msha_accident_cohort"] == "not_authorized"
    assert ART["claimed_cems_gads_lock"] == "not_in_repo"
    assert ART["placeholder_hash"] == "not_a_checksum"
    assert LAB["experiments"]["E2_blind_reconstruction"]["status"] == "LOCKED"
    assert (ROOT / "data" / "lab" / "crude" / "e1i_vintages.ok").exists() is False
    assert (ROOT / "E2_A_2005JUL.lock").exists() is False
    assert "QUALIFIES" in MEMO and "Overclaim" in MEMO
    assert "impact-informed index" in MEMO
    assert "not in the repo" in MEMO
    assert "PROMISING_BUT_PROVENANCE_UNRESOLVED" in MEMO
    assert "another_bridge_hunt" in MEMO
    assert "QUALIFIES_FOR_E2_VINTAGE_TEST" in MEMO
    assert "placeholder" in MEMO
    assert "E2_blind_reconstruction" in MEMO
    print("test_ma_census_20260923 PASS")


if __name__ == "__main__":
    main()
