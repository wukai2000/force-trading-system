#!/usr/bin/env python3
"""Report Idea Observatory status. Empty = NO_RESULT success. Cannot promote. Cannot scan Force 4."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from force_ideas.screen import ScreenError, empty_registry_is_success, screen_path


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--file", default="", help="screen one YAML card")
    p.add_argument("--writing-to", default="seeds", choices=["seeds", "hypotheses", "frozen"])
    p.add_argument("--promote", action="store_true")
    p.add_argument("--scan-force4", action="store_true")
    args = p.parse_args()

    if args.promote:
        print("REFUSED: Idea Observatory cannot promote. Capital $0.")
        return 2
    if args.scan_force4:
        print("REFUSED: Force 4 remains WAIT.")
        return 2

    if args.file:
        try:
            out = screen_path(Path(args.file), writing_to=args.writing_to)
        except ScreenError as e:
            print(f"REJECTED: {e}")
            return 1
        print(json.dumps(out, indent=2))
        return 0

    st = empty_registry_is_success()
    out = ROOT / "data" / "meta" / "idea_registry_status.json"
    out.write_text(json.dumps(st, indent=2))
    print(json.dumps(st, indent=2))
    print(f"wrote {out}")
    if st.get("empty"):
        print("NO_RESULT is a successful research period. Capital $0. Do not invent a leftover.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
