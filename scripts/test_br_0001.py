#!/usr/bin/env python3
"""Contract tests for BR-0001. Must stay red on score / promote / new episode."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(extra: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "run_br_0001.py"), *extra],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def main() -> int:
    ok = run([])
    if ok.returncode != 0 or "REFUSED" not in ok.stdout:
        print("FAIL: default run should report REFUSED and exit 0")
        print(ok.stdout, ok.stderr)
        return 1
    for flag, expect in (
        ("--score", 2),
        ("--promote", 2),
        ("--tickers", 2),
        ("--new-episode", 2),
        ("--use-stocks-as-x", 2),
        ("--open-sidecar", 2),
    ):
        r = run([flag])
        if r.returncode != expect:
            print(f"FAIL: {flag} expected {expect} got {r.returncode}")
            print(r.stdout, r.stderr)
            return 1
    print("test_br_0001  PASS  freeze loadable, scoring refused")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
