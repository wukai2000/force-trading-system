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


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    assert SPEC["id"] == "EP-NC-2011"
    assert SPEC["nc_means"] == "negative_control_2011"
    assert SPEC["not_north_carolina"] is True
    assert SPEC["north_carolina_wpsr_search"] == "dismissed"
    assert SPEC["geography"] == "US"
    assert SPEC["i_t_constructed"] is False
    assert SPEC["e1i_vintages_ok"] is False
    assert SPEC["gate1"] == "UNRESOLVED"
    assert SPEC["gate1_fail_this_pass"] is False
    assert SPEC["calendar_year_2011_enumerated"] is True
    assert SPEC["wayback_exhausted"] is False
    assert "padd_1c_substitution" in SPEC["refuse"]
    assert "missing_file_coded_as_U" in SPEC["refuse"]
    assert "wayback_closest_snapshot_as_week" in SPEC["refuse"]
    assert DESK["e1i_vintages_ok"] is False
    assert DESK["gate1"] == "UNRESOLVED"
    assert DESK["next_object"] == "2011_ep_nc_fill_remaining_or_fail"
    assert SPEC["next_object"] == "2011_ep_nc_fill_remaining_or_fail"
    assert (ROOT / "data" / "lab" / "crude" / "e1i_vintages.ok").exists() is False

    assert WB["i_t_constructed"] is False
    assert WB["e1i_vintages_ok"] is False
    assert WB["gate1"] == "UNRESOLVED"
    assert WB["gate1_fail_this_pass"] is False
    assert WB["cdx_exhausted"] is False
    assert WB["calendar_year_2011_enumerated_for_named_urls"] is True
    assert WB["n_wednesdays_in_hole"] == 30
    assert WB["closest_snapshot_as_week"] == "refused"
    assert WB["june_301_collapse"]["class"] == "NOT_JUNE_EXISTENCE"

    may = ROOT / "data" / "lab" / "crude" / "wpsr" / "2011-05-18" / "table1.csv"
    jul = ROOT / "data" / "lab" / "crude" / "wpsr" / "2011-07-27" / "table1.csv"
    assert sha256(may) == "616f0308ae94d5c267420c1777f4a2bbdc94aafa64a17cf6a5214264081b2998"
    assert sha256(jul) == "21dbed1132f1101589e246206f74e8240993001980153374fbabd804a5f9b4a6"
    may_txt = may.read_text(errors="replace")
    jul_txt = jul.read_text(errors="replace")
    assert "5/13/11" in may_txt
    assert '"5,618"' in may_txt
    assert '"370.312"' in may_txt
    assert '"18,515"' in may_txt
    assert "7/22/11" in jul_txt
    assert '"5,377"' in jul_txt
    assert '"354.025"' in jul_txt
    assert '"18,426"' in jul_txt

    hits = {h["issue"]: h for h in WB["hits"]}
    assert hits["2011-05-18"]["production_kbd"] == 5618
    assert hits["2011-05-18"]["stocks_ex_spr_mb"] == 370.312
    assert hits["2011-05-18"]["product_supplied_kbd"] == 18515
    assert hits["2011-07-27"]["production_kbd"] == 5377
    assert hits["2011-07-27"]["class"] == "LIVE_UNLISTED_NOT_FIRST_PRINT"
    print("test_ep_nc_2011 PASS")


if __name__ == "__main__":
    main()
