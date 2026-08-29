"""
scripts/run_force_discovery_simulation.py
=========================================
Runs literature simulators on non-price proxies (synthetic if needed).
Writes a YAML *sketch* only. Firewalled from live trading.
Force 4 remains wait / not scannable.
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


def main():
    print("=== Simulated Force Discovery (hypotheses only) ===")
    engine = ForceDiscoveryEngine()

    np.random.seed(42)
    n = 100
    term_data = pd.DataFrame(
        {
            "sovereign_capacity": np.linspace(10, 25, n) + np.random.normal(0, 1, n),
            "ai_energy_grid": np.linspace(50, 200, n) + np.random.normal(0, 10, n),
        }
    )
    hyps = run_all_simulators(term_counts=term_data)
    print(f"[Discovery] literature hits: {len(hyps)}")
    for h in hyps:
        print(f"  -> {h.model_id:20s} {h.theme}  {h.features}")

    mapped = engine.resolve_theme("defense_sovereign_capacity") or {}
    yaml_path = engine.generate_candidate_yaml_spec(
        candidate_name="Defense Sovereign Capacity",
        legs=list(mapped.get("legs") or ["ITA", "XAR", "PPA"]),
        controls=list(mapped.get("controls") or ["XLI", "SPY"]),
        taxonomy_class="stable_force",
        literature_models=[h.model_id for h in hyps],
        scannable=False,
    )
    print("\n=== Discovery simulation complete ===")
    print(f"Sketch: {yaml_path}")
    print("lock_status=wait  scannable=false  capital=0")
    print("Evaluate only via: PYTHONPATH=. python scripts/pit_evaluate.py --spec <yaml> --research-only")


if __name__ == "__main__":
    main()
