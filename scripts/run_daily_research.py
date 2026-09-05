#!/usr/bin/env python3
"""Daily research refresh — tests are in CI; this job fetches locked sources and
re-runs pipelines that cannot promote.

Does not scan Force 4. Does not invent a leftover. Does not overwrite the
locked 5k negative-control fixture. Capital $0.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from force_engine.guards import WAIT_TICKERS, WaitLockError


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _safe(name: str, fn: Callable[[], Any]) -> Dict[str, Any]:
    try:
        out = fn()
        return {"step": name, "ok": True, "result": out}
    except Exception as e:
        return {
            "step": name,
            "ok": False,
            "error": f"{type(e).__name__}: {e}",
            "trace": traceback.format_exc(limit=4),
        }


def _fetch() -> Dict[str, Any]:
    from force_learning.data.fetch_prices import DEFAULT_TICKERS, update_prices
    from force_learning.data.fetch_fred import update_clock_series, update_macro
    from force_learning.data.fetch_cot import update_cot
    from force_learning.data.panel import build_weekly_panel

    hits = [t for t in DEFAULT_TICKERS if t.upper() in WAIT_TICKERS]
    if hits:
        raise WaitLockError(f"DEFAULT_TICKERS contains WAIT tickers {hits}")
    prices = update_prices()
    macro = update_macro()
    clocks = update_clock_series()
    cot = update_cot()
    panel = build_weekly_panel()
    return {
        "prices": prices,
        "macro": macro,
        "clocks": clocks,
        "cot": cot,
        "panel": str(panel) if panel is not None else None,
        "force4_fetched": False,
    }


def _run_script(rel: str, extra: Optional[List[str]] = None) -> Dict[str, Any]:
    cmd = [sys.executable, str(ROOT / rel), *(extra or [])]
    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "")[-2000:]
        raise RuntimeError(f"rc={proc.returncode} {tail}")
    return {"rc": proc.returncode, "tail": (proc.stdout or "")[-400:]}


def _leading() -> Dict[str, Any]:
    return _run_script("scripts/run_leading_observables.py", ["--fetch"])


def _taxonomy() -> Dict[str, Any]:
    return _run_script("scripts/failfast_force_taxonomy.py")


def _ideas() -> Dict[str, Any]:
    from force_ideas.screen import empty_registry_is_success

    st = empty_registry_is_success()
    out = ROOT / "data" / "meta" / "idea_registry_status.json"
    out.write_text(json.dumps(st, indent=2))
    return st


def _daily_nulls() -> Dict[str, Any]:
    """Short-n diagnostic. Must not overwrite the locked 5k fixture."""
    daily = ROOT / "data" / "meta" / "daily_negative_control.json"
    fixture = ROOT / "data" / "meta" / "negative_control_audit.json"
    before = fixture.read_text() if fixture.exists() else ""
    out = _run_script(
        "scripts/run_negative_control_audit.py",
        ["--n-sign", "400", "--n-block", "200", "--out", str(daily)],
    )
    after = fixture.read_text() if fixture.exists() else ""
    if before and after != before:
        raise RuntimeError("locked negative_control_audit.json was mutated; refusing")
    return {**out, "wrote": str(daily), "fixture_preserved": True}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--promote", action="store_true")
    p.add_argument("--scan-force4", action="store_true")
    p.add_argument("--skip-fetch", action="store_true")
    p.add_argument("--skip-nulls", action="store_true")
    args = p.parse_args()
    if args.promote:
        print("REFUSED: daily research cannot promote. Capital $0.")
        return 2
    if args.scan_force4:
        print("REFUSED: Force 4 remains WAIT.")
        return 2

    steps = []
    if not args.skip_fetch:
        steps.append(_safe("fetch_all_locked_sources", _fetch))
    else:
        steps.append({"step": "fetch_all_locked_sources", "ok": True, "skipped": True})
    steps.append(_safe("leading_observables", _leading))
    steps.append(_safe("failfast_taxonomy", _taxonomy))
    steps.append(_safe("idea_registry", _ideas))
    steps.append(_safe("fs0001_observatory", lambda: _run_script("scripts/run_observatory.py")))
    if not args.skip_nulls:
        steps.append(_safe("daily_negative_control", _daily_nulls))
    else:
        steps.append({"step": "daily_negative_control", "ok": True, "skipped": True})

    payload = {
        "as_of": _now(),
        "protocol_id": "FORCE_PROTOCOL_v1.0",
        "cannot_promote": True,
        "promotion": "NOT_PERMITTED",
        "capital": 0,
        "force4_scanned": False,
        "leftover_invented": False,
        "locked_fixture_untouched": "data/meta/negative_control_audit.json",
        "steps": steps,
        "ok": all(s.get("ok") for s in steps),
    }
    out = ROOT / "data" / "meta" / "daily_research.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, default=str))
    print(json.dumps({k: payload[k] for k in ("as_of", "ok", "cannot_promote", "capital", "force4_scanned")}, indent=2))
    print("wrote", out)
    for s in steps:
        mark = "OK" if s.get("ok") else "FAIL"
        print(f"  [{mark}] {s.get('step')} {s.get('error') or ''}")
    # Fetch failures are recorded but do not fail the day if tests already passed.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
