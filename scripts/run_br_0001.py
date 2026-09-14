#!/usr/bin/env python3
"""BR-0001. Prints freeze status. Refuses to score. Cannot promote."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from force_learning.lab.br import assert_br, refuse_score, report, vintages_ready


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--json", action="store_true")
    p.add_argument("--score", action="store_true")
    p.add_argument("--promote", action="store_true")
    p.add_argument("--tickers", action="store_true")
    p.add_argument("--ir", action="store_true")
    p.add_argument("--new-episode", action="store_true")
    p.add_argument("--use-stocks-as-x", action="store_true")
    p.add_argument("--open-sidecar", action="store_true")
    args = p.parse_args()
    if args.promote:
        print("REFUSED: BR-0001 cannot promote a Force.")
        return 2
    if args.tickers or args.ir:
        print("REFUSED: returns do not define a CAP.")
        return 2
    if args.new_episode:
        print("REFUSED: no new episode. MTS-0002/E2.I is killed.")
        return 2
    if args.use_stocks_as_x:
        print("REFUSED: x stays production_kbd. Stocks edge is a retune.")
        return 2
    if args.open_sidecar:
        print("REFUSED: financial sidecar stays sealed.")
        return 2
    assert_br()
    if args.score:
        if not vintages_ready():
            out = refuse_score("e1i_vintages_missing")
            if args.json:
                print(json.dumps(out, indent=2))
            else:
                print("BR-0001  REFUSED  e1i_vintages_missing")
                print("  Gate 1 not run. Scoring is not identification.")
            return 2
        print("REFUSED: scoring path is not implemented. Do not fake a tape.")
        return 2
    out = report()
    if args.json:
        print(json.dumps(out, indent=2))
        return 0
    print(f"BR-0001  {out['label']}  {out['why']}")
    print(f"  parent={out['parent']}  e1i={out['e1i']}  vintages_ready={out['vintages_ready']}")
    print(f"  x={out['x']}  episode={out['episode']}  path_c={out['path_c']}")
    print(f"  ontology={out['ontology']}  identified={out['identified']}  capital=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
