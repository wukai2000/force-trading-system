#!/usr/bin/env python3
"""US crude competing-mechanism replay. Cannot promote, scan, or time returns."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from force_learning.lab.replay import assert_replay, run


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--json", action="store_true")
    p.add_argument("--promote", action="store_true")
    p.add_argument("--tickers", action="store_true")
    p.add_argument("--ir", action="store_true")
    p.add_argument("--open-sidecar", action="store_true")
    p.add_argument("--use-dpr", action="store_true")
    p.add_argument("--use-prices", action="store_true")
    args = p.parse_args()
    if args.promote:
        print("REFUSED: replay cannot promote a Force.")
        return 2
    if args.tickers or args.ir:
        print("REFUSED: returns do not define a Mechanism.")
        return 2
    if args.open_sidecar:
        print("REFUSED: financial sidecar stays sealed.")
        return 2
    if args.use_dpr:
        print("REFUSED: DPR as-revised monthly is a vintage leak.")
        return 2
    if args.use_prices:
        print("REFUSED: prices are excluded during discovery.")
        return 2
    assert_replay()
    result = run()
    if args.json:
        print(json.dumps(result, indent=2))
        return 0
    print(f"replay  {result['id']}  {result['verdict']}")
    print(f"  vintage={result['vintage_quality']}  identified={result['identified']}  n_seeds=0  sidecar=sealed")
    pr = result["primary"]
    print(f"  notes={result['n_notes']}  persist={pr['persist']['overall']['acc']:.3f}  rule={pr['rule']['overall']['acc']:.3f}  beats={pr['beats_persistence']}")
    print(f"  labels={pr['labels']}")
    nc = result["negative_control"]
    print(f"  NC {nc['id']} notes={result['n_nc_notes']} persist={nc['persist']['overall']['acc']:.3f} rule={nc['rule']['overall']['acc']:.3f} beats={nc['beats_persistence']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
