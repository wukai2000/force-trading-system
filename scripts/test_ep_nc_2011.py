#!/usr/bin/env python3
"""EP-NC-2011 is the 2011 US window, not North Carolina. Gate 1 stays unresolved."""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import yaml

SPEC = yaml.safe_load((ROOT / "force_ideas" / "inventory" / "ep_nc_2011.yaml").read_text())
DESK = yaml.safe_load((ROOT / "force_ideas" / "desk.yaml").read_text())


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
    assert "padd_1c_substitution" in SPEC["refuse"]
    assert "missing_file_coded_as_U" in SPEC["refuse"]
    assert DESK["e1i_vintages_ok"] is False
    assert DESK["gate1"] == "UNRESOLVED"
    assert DESK["next_object"] == "2011_ep_nc_us_wpsr_or_fail"
    assert (ROOT / "data" / "lab" / "crude" / "e1i_vintages.ok").exists() is False
    print("test_ep_nc_2011 PASS")


if __name__ == "__main__":
    main()
