#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from aetl.lab_e0 import run

def main() -> None:
    report = run()
    print(json.dumps(report, indent=2))
    if not report["pass_refuse_iid"]:
        sys.exit(2)
    if not report["pass_recover_order2"]:
        sys.exit(3)
    if not report["pass_no_extra_on_markov1"]:
        sys.exit(4)

if __name__ == "__main__":
    main()
