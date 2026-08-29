"""
Literature-model simulators.

These functions emit structural *hypotheses*. They do not score IR, do not
allocate capital, and cannot bypass force_engine.pipeline.evaluate_candidate.

Each simulator accepts optional real series. When series are missing it
runs on the provided frame only and returns an empty list rather than
inventing a live trade.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd


@dataclass
class Hypothesis:
    model_id: str
    theme: str
    features: Dict[str, Any]
    map_key: Optional[str] = None
    role: str = "hypothesis"
    cannot_promote: bool = True
    notes: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        d = {
            "model_id": self.model_id,
            "theme": self.theme,
            "features": self.features,
            "map_key": self.map_key,
            "role": self.role,
            "cannot_promote": self.cannot_promote,
            "notes": list(self.notes),
        }
        return d


def _z_last(s: pd.Series, win: int = 60) -> float:
    s = s.dropna()
    if len(s) < win:
        return float("nan")
    mu = s.iloc[-win:].mean()
    sd = s.iloc[-win:].std(ddof=1)
    if sd is None or sd == 0 or np.isnan(sd):
        return float("nan")
    return float((s.iloc[-1] - mu) / sd)


def _slope_last(s: pd.Series, win: int = 20) -> float:
    s = s.dropna()
    if len(s) < win:
        return float("nan")
    y = s.iloc[-win:].astype(float).to_numpy()
    x = np.arange(len(y), dtype=float)
    return float(np.polyfit(x, y, 1)[0])


def simulate_narrative_economics(term_counts: Optional[pd.DataFrame] = None) -> List[Hypothesis]:
    """Shiller / MediaStats: low attention + positive drift."""
    out: List[Hypothesis] = []
    if term_counts is None or term_counts.empty:
        return out
    for term in term_counts.columns:
        counts = term_counts[term].dropna()
        if len(counts) < 60:
            continue
        z = _z_last(counts, 60)
        slope = _slope_last(counts, 20)
        pctile = float(counts.rank(pct=True).iloc[-1])
        if np.isfinite(z) and np.isfinite(slope) and z < 0.2 and slope > 0 and pctile <= 0.40:
            out.append(
                Hypothesis(
                    model_id="narrative_economics",
                    theme=str(term),
                    features={"z_attn": z, "slope_20": slope, "attn_pctile": pctile},
                    map_key=str(term),
                    notes=["under_noticed_steady_drift"],
                )
            )
    return out


def simulate_limited_attention(term_counts: Optional[pd.DataFrame] = None) -> List[Hypothesis]:
    """Attention-capacity companion: neglected category, not viral."""
    out: List[Hypothesis] = []
    if term_counts is None or term_counts.empty:
        return out
    ranks = term_counts.rank(axis=1, pct=True)
    for term in term_counts.columns:
        s = term_counts[term].dropna()
        if len(s) < 60:
            continue
        last_rank = float(ranks[term].dropna().iloc[-1]) if term in ranks else float("nan")
        slope = _slope_last(s, 20)
        if np.isfinite(last_rank) and last_rank <= 0.25 and np.isfinite(slope) and slope > 0:
            out.append(
                Hypothesis(
                    model_id="limited_attention",
                    theme=str(term),
                    features={"cross_section_pctile": last_rank, "slope_20": slope},
                    map_key=str(term),
                    notes=["neglected_category"],
                )
            )
    return out


def simulate_slow_diffusion(
    patent_filings: Optional[pd.DataFrame] = None,
    cms_or_reg: Optional[pd.DataFrame] = None,
) -> List[Hypothesis]:
    """Hong-Stein / PEAD: 15% short vs long MA inflection in non-price series."""
    out: List[Hypothesis] = []
    frames = []
    if patent_filings is not None:
        frames.append(("patent", patent_filings))
    if cms_or_reg is not None:
        frames.append(("regulatory", cms_or_reg))
    for source, df in frames:
        if df is None or df.empty:
            continue
        for col in df.columns:
            series = df[col].dropna()
            if len(series) < 30:
                continue
            ma_s = float(series.iloc[-10:].mean())
            ma_l = float(series.iloc[-60:].mean()) if len(series) >= 60 else float(series.mean())
            if ma_l <= 0:
                continue
            ratio = ma_s / ma_l
            if ratio > 1.15:
                out.append(
                    Hypothesis(
                        model_id="slow_diffusion",
                        theme=str(col),
                        features={"source": source, "inflection_ratio": ratio},
                        map_key=str(col),
                        notes=["structural_lead_time"],
                    )
                )
    return out


def simulate_innovation(patent_value: Optional[pd.DataFrame] = None) -> List[Hypothesis]:
    """KPSS-style: require value/citation proxy, not raw counts."""
    out: List[Hypothesis] = []
    if patent_value is None or patent_value.empty:
        return out
    for col in patent_value.columns:
        s = patent_value[col].dropna()
        if len(s) < 30:
            continue
        z = _z_last(s, min(60, len(s)))
        slope = _slope_last(s, min(20, len(s)))
        if np.isfinite(z) and z > 0.5 and np.isfinite(slope) and slope > 0:
            out.append(
                Hypothesis(
                    model_id="innovation_kpss",
                    theme=str(col),
                    features={"value_z": z, "value_slope": slope},
                    map_key=str(col),
                    notes=["value_weighted_not_count"],
                )
            )
    return out


def simulate_p_factor(
    epu: Optional[pd.Series] = None,
    sheltered_proxy: Optional[pd.Series] = None,
) -> List[Hypothesis]:
    """Baker-Bloom-Davis + Pástor-Veronesi companion."""
    out: List[Hypothesis] = []
    if epu is None or len(pd.Series(epu).dropna()) < 30:
        return out
    s = pd.Series(epu).dropna().astype(float)
    z = float((s.iloc[-1] - s.mean()) / (s.std(ddof=1) + 1e-12))
    if z > 1.0:
        feat: Dict[str, Any] = {"epu_z": z}
        if sheltered_proxy is not None and len(pd.Series(sheltered_proxy).dropna()) >= 20:
            p = pd.Series(sheltered_proxy).dropna().astype(float)
            feat["sheltered_slope"] = _slope_last(p, min(20, len(p)))
        out.append(
            Hypothesis(
                model_id="p_factor_epu",
                theme="policy_sheltered_demand",
                features=feat,
                map_key="defense_sovereign_capacity",
                notes=["elevated_epu", "not_a_ticket_lock"],
            )
        )
    return out


def simulate_gpr(gpr: Optional[pd.Series] = None) -> List[Hypothesis]:
    """Caldara-Iacoviello: elevated GPR is a *veto/hyper* flag, not a promote."""
    out: List[Hypothesis] = []
    if gpr is None or len(pd.Series(gpr).dropna()) < 30:
        return out
    s = pd.Series(gpr).dropna().astype(float)
    z = float((s.iloc[-1] - s.mean()) / (s.std(ddof=1) + 1e-12))
    role = "veto" if z > 1.0 else "diagnostic"
    out.append(
        Hypothesis(
            model_id="geopolitical_gpr",
            theme="geopolitical_risk",
            features={"gpr_z": z},
            map_key="defense_sovereign_capacity",
            role=role,
            notes=["if_price_residual_dies_after_gpr_it_is_hyper"],
        )
    )
    return out


def simulate_slow_capital(residual: Optional[pd.Series] = None) -> List[Hypothesis]:
    """Half-life diagnostic. Persistence ≠ force."""
    out: List[Hypothesis] = []
    if residual is None:
        return out
    r = pd.Series(residual).dropna().astype(float)
    if len(r) < 80:
        return out
    x = r.iloc[:-1].to_numpy()
    y = r.iloc[1:].to_numpy()
    if np.std(x) == 0:
        return out
    rho = float(np.corrcoef(x, y)[0, 1])
    half = float("nan")
    if 0 < rho < 1:
        half = float(np.log(0.5) / np.log(rho))
    out.append(
        Hypothesis(
            model_id="slow_capital",
            theme="capacity_half_life",
            features={"ar1": rho, "half_life_days": half},
            role="diagnostic",
            notes=["persistence_is_not_a_force"],
        )
    )
    return out


def simulate_publication_decay(
    residual: Optional[pd.Series] = None,
    named_on: Optional[str] = None,
) -> List[Hypothesis]:
    """McLean-Pontiff style split around a naming date."""
    out: List[Hypothesis] = []
    if residual is None or not named_on:
        return out
    r = pd.Series(residual).dropna().astype(float)
    t = pd.Timestamp(named_on)
    pre = r[r.index < t]
    post = r[r.index >= t]
    if len(pre) < 40 or len(post) < 40:
        return out

    def _ir(s: pd.Series) -> float:
        if len(s) < 20 or float(s.std()) == 0:
            return float("nan")
        return float(s.mean() / s.std() * np.sqrt(252))

    out.append(
        Hypothesis(
            model_id="publication_decay",
            theme="post_naming_decay",
            features={"ir_pre": _ir(pre), "ir_post": _ir(post), "named_on": named_on},
            role="diagnostic",
            notes=["naming_clock_veto_only"],
        )
    )
    return out


def simulate_demographic(demo_proxy: Optional[pd.Series] = None) -> List[Hypothesis]:
    """Aging-industry demand class. Must not recycle F3 tickets."""
    out: List[Hypothesis] = []
    if demo_proxy is None or len(pd.Series(demo_proxy).dropna()) < 30:
        return out
    s = pd.Series(demo_proxy).dropna().astype(float)
    slope = _slope_last(s, min(36, len(s)))
    if np.isfinite(slope) and slope > 0:
        out.append(
            Hypothesis(
                model_id="demographic_demand",
                theme="aging_wtp",
                features={"proxy_slope": slope},
                notes=["do_not_recycle_IHF_IHI_XHS"],
            )
        )
    return out


def run_all_simulators(
    *,
    term_counts: Optional[pd.DataFrame] = None,
    patent_filings: Optional[pd.DataFrame] = None,
    patent_value: Optional[pd.DataFrame] = None,
    cms_or_reg: Optional[pd.DataFrame] = None,
    epu: Optional[pd.Series] = None,
    gpr: Optional[pd.Series] = None,
    sheltered_proxy: Optional[pd.Series] = None,
    residual: Optional[pd.Series] = None,
    demo_proxy: Optional[pd.Series] = None,
    named_on: Optional[str] = None,
) -> List[Hypothesis]:
    """Run every *hypothesis / veto / diagnostic* simulator. Kill layers stay in pipeline."""
    hyp: List[Hypothesis] = []
    hyp.extend(simulate_narrative_economics(term_counts))
    hyp.extend(simulate_limited_attention(term_counts))
    hyp.extend(simulate_slow_diffusion(patent_filings, cms_or_reg))
    hyp.extend(simulate_innovation(patent_value))
    hyp.extend(simulate_p_factor(epu, sheltered_proxy))
    hyp.extend(simulate_gpr(gpr))
    hyp.extend(simulate_slow_capital(residual))
    hyp.extend(simulate_publication_decay(residual, named_on))
    hyp.extend(simulate_demographic(demo_proxy))
    return hyp
