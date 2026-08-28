"""
force_engine/discovery.py
=========================
Simulated Force Discovery Engine.

Generates candidate force hypotheses by scanning:
  1. Shiller MediaStats Proxy: Low-attention / steady-drift narrative signals.
  2. Slow Diffusion Proxy: Patent, legislative, and regulatory lead-time clocks.
  3. Political Risk (P-Factor) Proxy: Policy/geopolitical demand shifts.

FIREWALL RULE:
This module ONLY proposes candidate ticket groups and YAML definitions.
It DOES NOT make trading decisions or bypass multi-layer gate checks in pipeline_v2.py.
"""

import os
import yaml
import numpy as np
import pandas as pd

class ForceDiscoveryEngine:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir

    def simulate_shiller_attention_candidates(self, term_counts_df):
        """
        Shiller / MediaStats Simulator:
        Identifies themes where narrative mention velocity is positive and steady,
        but total attention (z-score) remains below the 20th percentile.
        """
        candidates = []
        for term in term_counts_df.columns:
            counts = term_counts_df[term].dropna()
            if len(counts) < 60:
                continue
            
            # 60d rolling attention z-score
            z_score = (counts.iloc[-1] - counts.rolling(60).mean().iloc[-1]) / (counts.rolling(60).std().iloc[-1] + 1e-8)
            # 20d slope (drift velocity)
            slope = np.polyfit(np.arange(20), counts.iloc[-20:], 1)[0]
            
            # Low attention (z < 0.2) AND positive low-velocity drift (slope > 0)
            if z_score < 0.2 and slope > 0:
                candidates.append({
                    'term': term,
                    'type': 'shiller_under_noticed',
                    'z_score': float(z_score),
                    'slope': float(slope)
                })
        return candidates

    def simulate_slow_diffusion_candidates(self, patent_filings_df, cms_data_df=None):
        """
        Slow-Moving Information / Friction Simulator:
        Detects structural lead-times in non-financial data (USPTO patents, CMS policy).
        """
        candidates = []
        if patent_filings_df is not None:
            for col in patent_filings_df.columns:
                series = patent_filings_df[col].dropna()
                if len(series) >= 30:
                    ma_short = series.iloc[-10:].mean()
                    ma_long = series.iloc[-60:].mean() if len(series) >= 60 else series.mean()
                    
                    if ma_short > ma_long * 1.15:  # 15% upward structural inflection
                        candidates.append({
                            'source': 'patent_grants',
                            'category': col,
                            'inflection_ratio': float(ma_short / ma_long)
                        })
        return candidates

    def simulate_p_factor_candidates(self, epu_index_series, defense_outlays_series=None):
        """
        Political Risk (P-Factor) & Policy Simulator:
        Scans for policy-sheltered sub-sectors expanding during elevated Economic Policy Uncertainty.
        """
        candidates = []
        if epu_index_series is not None and len(epu_index_series) >= 30:
            epu_z = (epu_index_series.iloc[-1] - epu_index_series.mean()) / (epu_index_series.std() + 1e-8)
            if epu_z > 1.0: # Elevated policy risk regime
                candidates.append({
                    'type': 'defense_sovereign_industrial',
                    'epu_z_score': float(epu_z),
                    'recommended_theme': 'us_defense_sovereign_capacity'
                })
        return candidates

    def generate_candidate_yaml_spec(self, candidate_name, legs, controls, taxonomy_class="stable_force", output_dir="config/candidates"):
        """
        Formats a discovered candidate into a frozen pre-scan YAML specification
        strictly compatible with pipeline_v2.py execution.
        """
        os.makedirs(output_dir, exist_ok=True)
        
        spec = {
            'force_id': candidate_name.lower().replace(" ", "_"),
            'name': candidate_name,
            'taxonomy_class': taxonomy_class,
            'status': 'pre_scan_frozen',
            'tradable': 'residual_spread',
            'ticket_group': {
                'legs': legs,
                'controls': controls
            },
            'gate': {
                'min_clean_ir': 0.40,
                'max_placebo_ir': 0.15,
                'max_sector_beta': 0.80,
                'min_overlap_years': 8,
                'kill_on_fail': 'pause_no_option_b'
            }
        }
        
        yaml_path = os.path.join(output_dir, f"{spec['force_id']}.yaml")
        with open(yaml_path, 'w') as f:
            yaml.dump(spec, f, default_flow_style=False)
            
        print(f"[DISCOVERY] Pre-scan spec frozen and written to: {yaml_path}")
        return yaml_path