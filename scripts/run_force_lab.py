#!/usr/bin/env python3
"""Force Laboratory. Protocol only. Cannot scan, promote, or time returns."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from force_learning.lab.laboratory import assert_lab, report


def main() -> int:
    p = argparse.ArgumentParser(description="Force Laboratory — fingerprints, not IR")
    p.add_argument("--json", action="store_true")
    p.add_argument("--promote", action="store_true")
    p.add_argument("--tickers", action="store_true")
    p.add_argument("--ir", action="store_true")
    p.add_argument("--reconstruct", action="store_true")
    p.add_argument("--scan-force4", action="store_true")
    p.add_argument("--reopen-fs0001", action="store_true")
    args = p.parse_args()
    if args.promote:
        print("REFUSED: laboratory cannot promote a Force.")
        return 2
    if args.tickers or args.ir:
        print("REFUSED: returns and tickers do not define a Force.")
        return 2
    if args.reconstruct:
        print("REFUSED: episodes are NOT_RECONSTRUCTED. Protocol only.")
        return 2
    if args.scan_force4:
        print("REFUSED: Force 4 stays WAIT.")
        return 2
    if args.reopen_fs0001:
        print("REFUSED: FS-0001 stays frozen. Archetype B is not a reopen.")
        return 2
    spec = assert_lab()
    payload = report()
    if args.json:
        print(json.dumps(payload, indent=2))
        return 0
    print(f"force lab  {payload['research_status']}  object={payload['object']}  n_seeds=0  capital=$0")
    print(f"  archetypes={payload['n_archetypes']}  E1={payload['e1']}  E2={payload['e2']}")
    for e in payload["episodes"]:
        print(f"  {e['id']:16} {e['status']}  returns_used={e['returns_used']}")
    print("  MQA still binds. Domain shopping closed. Pipeline ends in falsification.")
    _ = spec
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
