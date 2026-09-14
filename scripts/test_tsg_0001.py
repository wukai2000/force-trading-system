#!/usr/bin/env python3
"""Contract tests for TSG-0001. Mining/fitting/promote stay red."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(extra: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "run_tsg_0001.py"), *extra],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def main() -> int:
    ok = run([])
    if ok.returncode != 0 or "PREMATURE" not in ok.stdout:
        print("FAIL: default should report PREMATURE")
        print(ok.stdout, ok.stderr)
        return 1
    for flag in (
        "--mine",
        "--prefixspan",
        "--fit",
        "--score",
        "--promote",
        "--add-letter",
        "--amend-br",
    ):
        r = run([flag])
        if r.returncode != 2:
            print(f"FAIL: {flag} expected 2 got {r.returncode}")
            print(r.stdout, r.stderr)
            return 1
    print("test_tsg_0001  PASS  freeze loadable, mining refused")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
