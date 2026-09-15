#!/usr/bin/env python3
"""PASS-0 runner. Lab only. Capital $0. Does not open HOU-1."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from aetl.pass0 import run, GATE

ART = ROOT / "artifacts"
ART.mkdir(exist_ok=True)


def main() -> None:
    report = run()
    rows = report.pop("_rows")
    csv_path = ART / "pass0_ladder_replicates.csv"
    fields = ["world", "r", "T", "ll_m0", "ll_m1", "ll_m2", "d10", "d21", "d20", "g1", "g2", "label"]
    with csv_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow({k: row[k] for k in fields})
    out = ART / "pass0_result.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in (
        "id", "decision", "label", "gate_nats", "gate_moved",
        "F1_A_invents", "F2_B_misses", "F3_C_false_g2",
        "naive_recoding", "hou1", "ladder", "collapse_naive",
        "identity_order_search",
    )}, indent=2))
    if report["gate_nats"] != GATE or report["gate_moved"]:
        sys.exit(2)
    if report["hou1"] != "REFUSE":
        sys.exit(3)
    if report["decision"] != "HOLD":
        sys.exit(4)


if __name__ == "__main__":
    main()
