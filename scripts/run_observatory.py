#!/usr/bin/env python3
"""FS-0001 lighting data-contract report. No IR. No tickers. Cannot promote."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from force_learning.observatory.resource_contract import report_fs0001


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--promote", action="store_true")
    p.add_argument("--scan-force4", action="store_true")
    p.add_argument("--attach-instruments", action="store_true")
    args = p.parse_args()
    if args.promote or args.scan_force4 or args.attach_instruments:
        print("REFUSED: observatory cannot promote, scan Force 4, or attach instruments.")
        return 2
    payload = report_fs0001()
    print(json.dumps(payload, indent=2))
    print("T5_READY", payload["t5_ready"], "PROSECUTOR", payload["prosecutor_allowed"], "CAPITAL", payload["capital_allowed"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
