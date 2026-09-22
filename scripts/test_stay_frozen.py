#!/usr/bin/env python3
"""Q4 stay-frozen overlay is load-bearing. Not a new scientific object.

Scientific lock remains c7f21fa (E1.I-local). This test does not score,
does not open a vintage, and does not lock a household option.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import yaml

DESK = yaml.safe_load((ROOT / "force_ideas" / "desk.yaml").read_text())
MISSION = yaml.safe_load((ROOT / "force_ideas" / "inventory" / "explorer_mission.yaml").read_text())

SCIENTIFIC_LOCK = "c7f21fa"

PERMITS = [
    "hold_log",
    "label_tape",
    "count_days_to_spym",
    "confirm_github_and_desk",
    "refresh_notion_snapshot",
    "keep_f1_f2_f3_negative_control",
    "keep_force4_wait",
    "keep_cells_not_i_t",
    "keep_missing_issue_incomplete_not_u",
]
FORBIDS = [
    "reopen_five_nc_cutoffs",
    "drop_five_and_score_15_of_20",
    "score_2014_only",
    "write_e1i_vintages_ok",
    "new_episode_or_later_nc",
    "path_d_from_this_fail",
    "wave1_hou1",
    "fs0001_cousins",
    "force4_scan",
    "capital_deploy",
    "closest_snapshot_as_week",
    "pet_twip_splice",
    "code_missing_as_u",
]


def main() -> None:
    assert DESK["next_object"] == "stay_frozen"
    assert DESK["q4_ack"] == "stay_frozen"
    assert DESK["q4_default"] == "stay_frozen"
    assert DESK["capital"] == 0
    assert DESK["n_seeds"] == 0
    assert DESK["force4"] == "wait"
    assert DESK["gate1"] == "FAIL"
    assert DESK["fail_scope"] == "E1I_LOCAL"
    assert DESK["architecture_kill"] is False
    assert DESK["architecture_observable_implementation"] == "MEASUREMENT_LAYER_YES"
    assert DESK["architecture_status"] == "idle_not_unimplemented"
    assert (
        DESK["idle_threshold"]
        == "measurement_layer_yes_and_identifying_experiment_unconstructible_on_frozen_object"
    )
    assert DESK["e1i_instance"] == "SEALED_NO_RESULT"
    assert DESK["e1i_vintages_ok"] is False
    assert DESK["se_ais_01"] == "candidate_for_gatekeeper_not_freeze"
    assert DESK["state_event_pair"] == "screening_not_freeze"
    assert DESK["stay_frozen_permits"] == PERMITS
    assert DESK["stay_frozen_forbids"] == FORBIDS
    assert "score_2014_only" in DESK["stay_frozen_forbids"]
    assert "freeze_policy" not in DESK
    assert "household_default" not in DESK
    assert "option_a" not in DESK
    if "scientific_lock" in DESK:
        assert DESK["scientific_lock"] == SCIENTIFIC_LOCK
    assert (ROOT / "docs" / "FREEZE_PERMITS.md").exists() is False
    assert (ROOT / "data" / "lab" / "crude" / "e1i_vintages.ok").exists() is False
    assert MISSION["census_size_this_quarter"] == 0
    assert MISSION["seed_finder_this_quarter"] is False
    assert "se_ais_01_freeze_this_pass" in MISSION["refused"]
    print("test_stay_frozen PASS")


if __name__ == "__main__":
    main()
