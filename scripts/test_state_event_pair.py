#!/usr/bin/env python3
"""SE-AIS-01 is Gatekeeper, not a freeze. E1.I stays closed."""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import yaml

SPEC = yaml.safe_load((ROOT / "force_ideas" / "inventory" / "state_event_pair.yaml").read_text())
DESK = yaml.safe_load((ROOT / "force_ideas" / "desk.yaml").read_text())
MEMO = (ROOT / "docs" / "MEMO_STATE_EVENT_CONSOLIDATION.md").read_text()
ART = json.loads((ROOT / "artifacts" / "state_event_pair.json").read_text())
EP = yaml.safe_load((ROOT / "force_ideas" / "inventory" / "ep_nc_2011.yaml").read_text())
MISSION = yaml.safe_load((ROOT / "force_ideas" / "inventory" / "explorer_mission.yaml").read_text())


def main() -> None:
    assert SPEC["id"] == "SE-AIS-01"
    assert SPEC["status"] == "CANDIDATE_FOR_GATEKEEPER"
    assert SPEC["not_status"] == "CANDIDATE_FOR_FREEZE"
    assert SPEC["independence_class"] == "I3_provisional"
    assert SPEC["independence_i4"] is False
    assert SPEC["frozen"] is False
    assert SPEC["admitted_as_seeds"] is False
    assert SPEC["n_seeds"] == 0
    assert SPEC["winner"] is None or SPEC["winner"] == "none"
    assert SPEC["e1i_reopened"] is False
    assert SPEC["s_t"]["dwt_join"] == "refused"
    assert SPEC["s_t"]["rule_frozen"] is False
    assert SPEC["s_t"]["polygons_frozen"] is False
    assert "ais_first_occupancy" in SPEC["b"]["not_event"]
    assert "spire" in SPEC["a"]["not_tape"]
    assert "ais_occupancy_as_event" in SPEC["refuse"]
    assert "reopen_e1i" in SPEC["refuse"]
    assert SPEC["next_object"] == "stay_frozen"
    assert DESK["n_seeds"] == 0
    assert DESK["gate1"] == "FAIL"
    assert DESK["e1i_vintages_ok"] is False
    assert DESK["next_object"] == "stay_frozen"
    assert DESK["se_ais_01"] == "candidate_for_gatekeeper_not_freeze"
    assert MISSION["census_size_this_quarter"] == 0
    assert "se_ais_01_freeze_this_pass" in MISSION["refused"]
    assert "dwt_join_as_ais_state" in MISSION["refused"]
    assert "candidate_for_freeze_from_unfrozen_polygons" in MISSION["refused"]
    assert EP["gate1"] == "FAIL"
    assert EP["i_t_constructed"] is False
    assert ART["status"] == "CANDIDATE_FOR_GATEKEEPER"
    assert ART["independence_i4"] is False
    assert ART["note_3_freeze"] == "dismissed"
    assert (ROOT / "data" / "lab" / "crude" / "e1i_vintages.ok").exists() is False
    assert "CANDIDATE_FOR_FREEZE" in MEMO and "Dismiss" in MEMO
    assert "DWT is not in the AIS sentence" in MEMO
    print("test_state_event_pair PASS")


if __name__ == "__main__":
    main()
