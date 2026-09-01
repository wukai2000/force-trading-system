"""
scripts/run_force_discovery_simulation.py
=========================================
Runs literature simulators on non-price proxies (synthetic if needed).
Does NOT convert a theme hit into ITA/XAR/PPA. Force 4 remains wait.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd

from force_engine.discovery import ForceDiscoveryEngine
from force_engine.literature import run_all_simulators
from force_engine.sieve import sieve_panel


def main():
    print("=== Simulated Force Discovery (hypotheses only) ===")
    engine = ForceDiscoveryEngine()

    rng = np.random.default_rng(42)
    n = 100
    term_data = pd.DataFrame(
        {
            "under_noticed_widget": np.linspace(10, 25, n) + rng.normal(0, 1, n),
            "viral_headline": np.linspace(50, 200, n) + rng.normal(0, 10, n),
        }
    )
    hyps = run_all_simulators(term_counts=term_data)
    print(f"[Discovery] literature hits: {len(hyps)}")
    for h in hyps:
        print(f"  -> {h.model_id:20s} {h.theme}  map={h.map_key}  {h.features}")
        if h.map_key in ("defense_sovereign_capacity", "defense_avionics"):
            raise SystemExit("literature must not auto-map to defense tickets")

    mapped = engine.resolve_theme("defense_sovereign_capacity") or {}
    print(
        f"existing wait sketch on disk: status={mapped.get('status')} "
        f"scannable={mapped.get('scannable')} (not rewritten by discovery)"
    )
    print("Not generating ITA/XAR/PPA YAML from a theme lookup.")
    print("Use scripts/run_panel_sieve.py to find leftovers vs paused residuals.")
    print("lock_status=wait  scannable=false  capital=0")


if __name__ == "__main__":
    main()
