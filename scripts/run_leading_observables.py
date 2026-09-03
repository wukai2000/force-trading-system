#!/usr/bin/env python3
"""Fetch (optional) and report the T2 leading-observable catalog.

Veto-only. Cannot promote. Cannot scan Force 4. Cannot time a residual.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from force_engine.leading_observables import (
    TimingOverlayError,
    load_catalog,
    refuse_timing_overlay,
    report,
)


def main() -> int:
    p = argparse.ArgumentParser(description="Leading observables — veto-only catalog")
    p.add_argument("--fetch", action="store_true", help="pull FRED graph CSVs for wired ids")
    p.add_argument("--promote", action="store_true")
    p.add_argument("--scan-force4", action="store_true")
    p.add_argument("--time-residual", action="store_true")
    args = p.parse_args()

    if args.promote:
        print("REFUSED: leading observables cannot promote.")
        return 2
    if args.scan_force4:
        print("REFUSED: Force 4 remains WAIT. Catalog does not scan ITA/XAR/PPA/XLI.")
        return 2
    if args.time_residual:
        try:
            refuse_timing_overlay()
        except TimingOverlayError as e:
            print(f"REFUSED: {e}")
            return 2

    cat = load_catalog()
    print(f"catalog: {len(cat.observables)} observables  cannot_promote={cat.cannot_promote}  capital={cat.capital}  force4={cat.force4}")
    print(f"refused: {[o.id for o in cat.refused()]}")

    fetch_results = None
    if args.fetch:
        from force_learning.data.fetch_fred import update_clock_series

        fetch_results = update_clock_series()
        failed = [k for k, v in fetch_results.items() if not v.get("ok")]
        if failed:
            print(f"FRED miss (stay unwired, no synthetic): {failed}")

    payload = report(cat)
    payload["fetch"] = fetch_results
    out = ROOT / "data" / "meta" / "leading_observables.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, default=str))
    print(f"wired_cache={payload['n_wired_cache']} refused={payload['n_refused']} unwired/missing={payload['n_unwired']}")
    print(f"veto_ids={payload['veto_ids']}")
    print(f"wrote {out}")
    print("CANNOT_PROMOTE. Clocks veto; they do not time r_t. Capital $0.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
