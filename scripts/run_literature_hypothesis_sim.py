#!/usr/bin/env python3
"""
Run every literature simulator as a hypothesis engine.

No prices required. No capital. Cannot promote.
Uses synthetic proxies when real series are absent so the loop is testable.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd

from force_engine.discovery import ForceDiscoveryEngine
from force_engine.literature import run_all_simulators


def synthetic_proxies(n: int = 120, seed: int = 42):
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2018-01-31", periods=n, freq="ME")
    # under-noticed rising theme vs viral theme
    sovereign = np.linspace(10, 22, n) + rng.normal(0, 0.6, n)
    viral = np.linspace(40, 180, n) + rng.normal(0, 8, n)
    terms = pd.DataFrame({"sovereign_capacity": sovereign, "ai_energy_grid": viral}, index=idx)
    patents = pd.DataFrame(
        {"defense_avionics": np.concatenate([np.full(80, 10.0), np.linspace(10, 16, n - 80)]) + rng.normal(0, 0.4, n)},
        index=idx,
    )
    epu = pd.Series(100 + rng.normal(0, 10, n), index=idx)
    epu.iloc[-12:] += 40  # elevated EPU at the end
    gpr = pd.Series(80 + rng.normal(0, 8, n), index=idx)
    gpr.iloc[-6:] += 25
    return terms, patents, epu, gpr


def main() -> int:
    print("=== Literature hypothesis simulation (cannot promote, capital=0) ===")
    terms, patents, epu, gpr = synthetic_proxies()
    hyps = run_all_simulators(
        term_counts=terms,
        patent_filings=patents,
        epu=epu,
        gpr=gpr,
    )
    engine = ForceDiscoveryEngine()
    rows = []
    for h in hyps:
        rec = h.as_dict()
        mapped = engine.resolve_theme(h.map_key) if h.map_key else None
        rec["mapped_lock_status"] = None if mapped is None else mapped.get("status")
        rec["mapped_scannable"] = False
        rows.append(rec)
        print(
            f"  [{h.role:11s}] {h.model_id:24s} theme={h.theme:28s} "
            f"map={h.map_key} features={h.features}"
        )

    out = ROOT / "data" / "meta" / "literature_hypotheses.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "n_hypotheses": len(rows),
        "capital": 0,
        "force4_lock_status": "wait",
        "note": "Hypotheses only. Run pit_evaluate.py + pipeline to kill beta.",
        "hypotheses": rows,
    }
    out.write_text(json.dumps(payload, indent=2, default=str))
    print(f"\nWrote {out}")
    print("No tickets locked. No scan. No capital.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
