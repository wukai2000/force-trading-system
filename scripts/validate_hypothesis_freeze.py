#!/usr/bin/env python3
"""Validate a T0–T4 freeze YAML. Cannot promote. Cannot scan Force 4."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from force_engine.freeze import FreezeError, load_freeze  # noqa: E402
from force_engine.guards import RecycleError, WaitLockError  # noqa: E402


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Validate T0–T4 freeze. Cannot promote.")
    p.add_argument("path", type=Path, nargs="?", default=ROOT / "config" / "hypotheses" / "_TEMPLATE.yaml")
    args = p.parse_args(argv)
    try:
        fh = load_freeze(args.path)
    except (FreezeError, WaitLockError, RecycleError) as e:
        print(f"FREEZE_REFUSED {args.path}: {e}")
        return 2
    payload = fh.as_dict()
    print(json.dumps(payload, indent=2))
    if fh.freeze_complete:
        print("freeze_complete=true; T5 attach_instruments is allowed; evaluate still cannot promote")
    else:
        print(f"freeze_complete=false missing={fh.missing}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
