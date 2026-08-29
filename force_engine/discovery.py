"""
force_engine/discovery.py
=========================
Simulated Force Discovery Engine.

Generates candidate *hypotheses* from literature simulators.
Writes YAML sketches under config/candidates/.

FIREWALL RULE:
This module ONLY proposes. It DOES NOT make trading decisions or bypass
multi-layer gate checks in force_engine.pipeline.evaluate_candidate.

Force 4 tickets are not locked by generating a YAML sketch.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import yaml

from .literature import Hypothesis, run_all_simulators


HARD_EXCLUDED_LEGS = {
    "MAGS",
    "SMH",
    "SPMO",
    "VST",
    "ETN",
    "PWR",
    "IHF",
    "IHI",
    "XHS",
}


class ForceDiscoveryEngine:
    def __init__(self, data_dir: str = "data", map_path: str = "config/theme_ticket_map.yaml"):
        self.data_dir = data_dir
        self.map_path = map_path
        self._theme_map = self._load_map()

    def _load_map(self) -> Dict[str, Any]:
        if not os.path.exists(self.map_path):
            return {}
        with open(self.map_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def simulate_shiller_attention_candidates(self, term_counts_df):
        from .literature import simulate_narrative_economics

        return [
            {"term": h.theme, "type": "shiller_under_noticed", "z_score": h.features.get("z_attn"), "slope": h.features.get("slope_20")}
            for h in simulate_narrative_economics(term_counts_df)
        ]

    def simulate_slow_diffusion_candidates(self, patent_filings_df, cms_data_df=None):
        from .literature import simulate_slow_diffusion

        return [
            {"source": h.features.get("source"), "category": h.theme, "inflection_ratio": h.features.get("inflection_ratio")}
            for h in simulate_slow_diffusion(patent_filings_df, cms_data_df)
        ]

    def simulate_p_factor_candidates(self, epu_index_series, defense_outlays_series=None):
        from .literature import simulate_p_factor

        return [
            {
                "type": "defense_sovereign_industrial",
                "epu_z_score": h.features.get("epu_z"),
                "recommended_theme": h.map_key,
            }
            for h in simulate_p_factor(epu_index_series, defense_outlays_series)
        ]

    def run_literature_scan(self, **kwargs) -> List[Hypothesis]:
        return run_all_simulators(**kwargs)

    def resolve_theme(self, map_key: str) -> Optional[Dict[str, Any]]:
        themes = (self._theme_map or {}).get("themes") or {}
        return themes.get(map_key)

    def generate_candidate_yaml_spec(
        self,
        candidate_name: str,
        legs: List[str],
        controls: List[str],
        taxonomy_class: str = "stable_force",
        output_dir: str = "config/candidates",
        *,
        as_of: Optional[str] = None,
        literature_models: Optional[List[str]] = None,
        scannable: bool = False,
    ) -> str:
        """
        Formats a discovered candidate into a frozen pre-scan YAML sketch.
        scannable defaults to False — generating a file is not a Force lock.
        """
        bad = [t for t in legs if t.upper() in HARD_EXCLUDED_LEGS]
        if bad and not scannable:
            # Research sketches of paused forces are allowed only if explicitly named paused_*
            if not candidate_name.lower().startswith("paused"):
                raise ValueError(f"refusing excluded legs in a new sketch: {bad}")
        if any(t.upper() == "QQQ" for t in legs):
            raise ValueError("QQQ cannot be a leg")

        os.makedirs(output_dir, exist_ok=True)
        spec = {
            "force_id": candidate_name.lower().replace(" ", "_"),
            "name": candidate_name,
            "taxonomy_class": taxonomy_class,
            "status": "pre_scan_frozen_sketch",
            "scannable": bool(scannable),
            "lock_status": "wait",
            "tradable": "residual_spread",
            "as_of": as_of,
            "literature_models": literature_models or [],
            "ticket_group": {"legs": list(legs), "controls": list(controls)},
            "gate": {
                "min_clean_ir": 0.40,
                "max_placebo_ir": 0.15,
                "max_sector_beta": 0.80,
                "min_overlap_years": 8,
                "min_neighbor_ir": 0.40,
                "kill_on_fail": "pause_no_option_b",
            },
            "capital": 0,
            "note": "Sketch only. pipeline.evaluate_candidate is the only evaluation entry.",
        }
        yaml_path = os.path.join(output_dir, f"{spec['force_id']}.yaml")
        with open(yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(spec, f, default_flow_style=False, sort_keys=False)
        print(f"[DISCOVERY] Sketch written (scannable={scannable}, lock=wait): {yaml_path}")
        return yaml_path
