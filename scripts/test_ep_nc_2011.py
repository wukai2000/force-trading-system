#!/usr/bin/env python3
"""EP-NC-2011 is the 2011 US window, not North Carolina. Gate 1 stays unresolved."""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import yaml

SPEC = yaml.safe_load((ROOT / "force_ideas" / "inventory" / "ep_nc_2011.yaml").read_text())
DESK = yaml.safe_load((ROOT / "force_ideas" / "desk.yaml").read_text())
WB = json.loads((ROOT / "artifacts" / "ep_nc_2011_wayback.json").read_text())
FP = json.loads((ROOT / "artifacts" / "ep_nc_2011_first_print.json").read_text())
EIGHT = json.loads((ROOT / "artifacts" / "ep_nc_2011_eight.json").read_text())
LISTED = json.loads((ROOT / "data" / "lab" / "crude" / "wpsr" / "AUG2011_JUN2012_CELLS.json").read_text())
HOLE = json.loads((ROOT / "data" / "lab" / "crude" / "wpsr" / "JAN_JUL_2011_CELLS.json").read_text())


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    assert SPEC["id"] == "EP-NC-2011"
    assert SPEC["nc_means"] == "negative_control_2011"
    assert SPEC["not_north_carolina"] is True
    assert SPEC["geography"] == "US"
    assert SPEC["i_t_constructed"] is False
    assert SPEC["e1i_vintages_ok"] is False
    assert SPEC["gate1"] == "UNRESOLVED"
    assert SPEC["gate1_fail_this_pass"] is False
    assert SPEC["listed_archive_ok"] == 48
    assert SPEC["jan_jul_three_leg"] == 7
    assert SPEC["nc_cutoffs_have_issue"] == 15
    assert SPEC["nc_cutoffs_incomplete"] == 5
    assert "psw09_history_as_earlier_cutoff" in SPEC["refuse"]
    assert DESK["e1i_vintages_ok"] is False
    assert DESK["gate1"] == "UNRESOLVED"
    assert DESK["next_object"] == "2011_five_cutoffs_or_fail"
    assert SPEC["next_object"] == "2011_five_cutoffs_or_fail"
    assert (ROOT / "data" / "lab" / "crude" / "e1i_vintages.ok").exists() is False

    assert FP["i_t_constructed"] is False
    assert FP["e1i_vintages_ok"] is False
    assert FP["gate1"] == "UNRESOLVED"
    assert FP["listed_archive"]["n_ok"] == 48
    assert FP["nc_cutoffs_every_4w"]["incomplete"] == 8
    assert EIGHT["recovered_three_leg"] == 3
    assert EIGHT["still_incomplete"] == 5
    assert EIGHT["i_t_constructed"] is False
    assert EIGHT["govinfo_issue_file"] is False
    assert len(LISTED) == 48
    assert LISTED[0]["release"] == "2011-08-03"
    assert LISTED[0]["production_kbd"] == 5523
    assert LISTED[-1]["release"] == "2012-06-27"
    assert LISTED[-1]["production_kbd"] == 6257
    assert all(r.get("production_kbd") and r.get("stocks_ex_spr_mb") and r.get("product_supplied_kbd") for r in LISTED)
    assert sum(1 for r in LISTED if r.get("slip_days") == 1) == 7

    three = [h for h in HOLE if h.get("three_legs")]
    assert len(three) == 7
    by = {h["release"]: h for h in HOLE}
    assert by["2011-01-19"]["production_kbd"] == 5205
    assert by["2011-05-11"]["product_supplied_kbd"] == 18164
    assert by["2011-05-18"]["production_kbd"] == 5618
    assert by["2011-07-27"]["class"] == "LIVE_UNLISTED_NOT_FIRST_PRINT"
    assert by["2011-03-30"]["production_kbd"] == 5568
    assert by["2011-03-30"]["product_supplied_kbd"] == 18605
    assert by["2011-04-27"]["production_kbd"] == 5610
    assert by["2011-07-20"]["three_legs"] is True
    assert by["2011-07-20"]["production_kbd"] == 5591
    assert by["2011-07-20"]["product_supplied_kbd"] == 18853

    may = ROOT / "data" / "lab" / "crude" / "wpsr" / "2011-05-18" / "table1.csv"
    jul = ROOT / "data" / "lab" / "crude" / "wpsr" / "2011-07-27" / "table1.csv"
    mar = ROOT / "data" / "lab" / "crude" / "wpsr" / "2011-03-30" / "table9.csv"
    jul20 = ROOT / "data" / "lab" / "crude" / "wpsr" / "2011-07-20" / "table9.pdf"
    assert sha256(may) == "616f0308ae94d5c267420c1777f4a2bbdc94aafa64a17cf6a5214264081b2998"
    assert sha256(jul) == "21dbed1132f1101589e246206f74e8240993001980153374fbabd804a5f9b4a6"
    assert sha256(mar) == "6da408f9f643551f1a388bb3c1500a2897f85d1439e4f327dddde5a07140553a"
    assert sha256(jul20) == "969aa09a714c2d2ffac73bf8239f05e5734a5a81eb5541ac41f42093596a131f"
    assert WB["closest_snapshot_as_week"] == "refused"
    print("test_ep_nc_2011 PASS")


if __name__ == "__main__":
    main()
