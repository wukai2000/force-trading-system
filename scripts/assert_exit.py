#!/usr/bin/env python3
"""CI helper: succeed only if a command exits with the expected code.

GitHub Actions uses `bash -e`, so `python foo.py --promote; test $? -eq 2`
never reaches the test when --promote correctly returns 2.
"""
from __future__ import annotations

import subprocess
import sys


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: assert_exit.py EXPECTED_RC CMD...")
        return 2
    want = int(sys.argv[1])
    cmd = sys.argv[2:]
    proc = subprocess.run(cmd)
    if proc.returncode != want:
        print(f"expected exit {want}, got {proc.returncode}: {cmd}")
        return 1
    print(f"ok: exit {want} as required")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
