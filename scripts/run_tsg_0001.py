#!/usr/bin/env python3
"""TSG-0001 v0.1. Prints freeze. Refuses mining, fitting, promotion."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from force_learning.lab.tsg import assert_tsg, report


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--json", action="store_true")
    p.add_argument("--mine", action="store_true")
    p.add_argument("--fit", action="store_true")
    p.add_argument("--score", action="store_true")
    p.add_argument("--promote", action="store_true")
    p.add_argument("--add-letter", action="store_true")
    p.add_argument("--prefixspan", action="store_true")
    p.add_argument("--amend-br", action="store_true")
    args = p.parse_args()
    if args.promote:
        print("REFUSED: a motif is not a Force.")
        return 2
    if args.mine or args.prefixspan:
        print("REFUSED: M5 / PrefixSpan locked in v0.1.")
        return 2
    if args.fit or args.score:
        print("REFUSED: PREMATURE. No BR-0001 first-print tape. M0-M2 not fitted.")
        return 2
    if args.add_letter:
        print("REFUSED: do not add C/D to spell a sentence.")
        return 2
    if args.amend_br:
        print("REFUSED: TSG does not amend BR-0001.")
        return 2
    assert_tsg()
    out = report()
    if args.json:
        print(json.dumps(out, indent=2))
        return 0
    print(f"TSG-0001  {out['label']}  {out['why']}")
    print(f"  parent={out['parent_tape']}  vintages_ready={out['vintages_ready']}")
    print(f"  authorized={out['models_authorized']}  locked={out['models_locked']}")
    print(f"  alphabet={out['alphabet']}  h2={out['h2_authorized']}  capital=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
