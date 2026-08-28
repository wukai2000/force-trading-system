"""
scripts/run_force_discovery_simulation.py
=========================================
Runs the Simulated Force Discovery Engine across non-price proxies.
Outputs candidate YAML definitions to config/candidates/ for human/system review.
"""

import sys
import os
import numpy as np
import pandas as pd

# Append project root directory to sys.path for robust import resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from force_engine.discovery import ForceDiscoveryEngine

def main():
    print("=== Running Simulated Force Discovery Engine ===")
    engine = ForceDiscoveryEngine()

    # 1. Mock/Load Shiller Attention Proxy Data
    np.random.seed(42)
    term_data = pd.DataFrame({
        'sovereign_capacity': np.linspace(10, 25, 100) + np.random.normal(0, 1, 100),
        'ai_energy_grid': np.linspace(50, 200, 100) + np.random.normal(0, 10, 100),  # High attention
    })
    
    shiller_candidates = engine.simulate_shiller_attention_candidates(term_data)
    print(f"[Discovery] Shiller Under-Noticed Candidates Found: {len(shiller_candidates)}")
    for c in shiller_candidates:
        print(f"  -> Term: {c['term']} (z-score: {c['z_score']:.2f}, slope: {c['slope']:.2f})")

    # 2. Export Pre-Registered Spec for Candidate Force 4 (Defense / Sovereign Industrial Capacity)
    yaml_path = engine.generate_candidate_yaml_spec(
        candidate_name="Defense Sovereign Capacity",
        legs=['ITA', 'XAR', 'PPA'],
        controls=['XLI', 'SPY'],
        taxonomy_class="stable_force"
    )
    
    print("\n=== Discovery Simulation Complete ===")
    print("Candidate specs generated. Firewalled from live trading until cleared by pipeline_v2.py.")

if __name__ == "__main__":
    main()