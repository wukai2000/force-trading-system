#!/usr/bin/env python3
"""Physical-change survey. Shape only. Cannot promote, lag-test, or freeze."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from force_learning.vault.physical_survey import assert_survey, survey


def main() -> int:
    p = argparse.ArgumentParser(description="Physical measurement survey — shape only")
    p.add_argument("--promote", action="store_true")
    p.add_argument("--audit-volcano", action="store_true")
    p.add_argument("--select-streamflow-dam", action="store_true")
    p.add_argument("--rank", action="store_true")
    p.add_argument("--lag-test", action="store_true")
    p.add_argument("--json", action="store_true")
    p.add_argument("--probe", action="store_true", help="landing-page existence only")
    args = p.parse_args()
    if args.promote:
        print("REFUSED: survey cannot promote a Force, seed, or QUALIFIES.")
        return 2
    if args.audit_volcano:
        print("REFUSED: volcano provenance is not authorized this cycle.")
        return 2
    if args.select_streamflow_dam:
        print("REFUSED: USGS stage is hydrologic load, not dam fabric.")
        return 2
    if args.rank:
        print("REFUSED: attractiveness ranking is refused.")
        return 2
    if args.lag_test:
        print("REFUSED: survey does not time a residual or fit a lag.")
        return 2
    spec = assert_survey()
    if args.probe:
        from force_learning.vault.survey_probe import probe_all
        rows = probe_all()
        n_ok = sum(1 for r in rows if r.get("reachable"))
        print(f"physical probe  landing-page existence  reachable={n_ok}/{len(rows)}  n_seeds=0")
        for r in rows:
            flag = "OK" if r.get("reachable") else "MISS"
            code = r.get("status_code") or r.get("error") or "?"
            print(f"  {flag:4} {r['id']:24} {r['role']:24} {code}")
        return 0 if n_ok else 1

    rows = survey(spec)
    if args.json:
        print(json.dumps({"n": len(rows), "n_seeds": 0, "winner": None, "rows": rows}, indent=2))
        return 0
    print("physical survey  n_seeds=0  winner=none  audit_authorized=false")
    print(f"{'id':28} {'status':28} qualifies seed")
    for r in rows:
        print(f"{r['id']:28} {r['status']:28} {r['qualifies']!s:5} {r['seed']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
