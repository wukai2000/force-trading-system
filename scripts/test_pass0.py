#!/usr/bin/env python3
"""PASS-0 spec locks. Does not score BR-0001. Does not open HOU-1."""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from aetl.pass0 import GATE, MASTER, evaluate_ladder, gen_modular2, rng_for, WORLD_R
import yaml

SPEC = yaml.safe_load((ROOT / "force_ideas" / "inventory" / "pass0.yaml").read_text())


def main() -> None:
    assert SPEC["id"] == "PASS-0"
    assert SPEC["gate_nats"] == GATE == 6.0
    assert SPEC["gate_moved"] is False
    assert SPEC["opens_hou1"] is False
    assert SPEC["amends_br_0001"] is False
    assert SPEC["master_seed"] == MASTER
    assert SPEC["worlds"]["A"]["R"] == WORLD_R["A"]
    assert SPEC["worlds"]["B"]["R"] == WORLD_R["B"]
    assert SPEC["worlds"]["C"]["R"] == WORLD_R["C"]
    # Modular DGP: M1 must not eat World B on a long draw.
    seq = gen_modular2(1500, rng_for("B", 0, "dgp"))
    ev = evaluate_ladder(seq)
    assert ev["g2"], ev
    assert ev["d21"] > 50, ev["d21"]
    print("test_pass0 PASS")


if __name__ == "__main__":
    main()
