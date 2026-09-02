"""
False-discovery *diagnostics*.

The locked promotion gate is the concentration kill in force_engine.evaluate
(sign-randomization mean |IR| staying ≥40% of observed |IR|). These extra
statistics exist because a walk of many as-of dates inflates discovery even
when each single date is clean.

They cannot promote a failing residual and they cannot loosen the locked gate.

Two null families (protocol 2026-09-01, docs/RESEARCH_PROTOCOL.md):

  Null A — residual sign-null. Flip signs of r_t. Magnitude path is (almost)
  fixed; only the signed mean moves. Report the percentile of observed IR
  inside that signed-IR null, plus empirical p. Draw count is a computational
  sample, not proof of rigor.

  Null B — block bootstrap at {5, 21, 60}. Mean AND std may move. Do not
  average block lengths. A 60-day block that preserves 2022 is not validation.

  Null 1 — regime-label permutation (2026-09-02). Shuffle the locked
  {complacency, normal, stress} labels, residual fixed. Asks whether
  IR_complacency − IR_stress is larger than chance given occupancy / dwell.
  Cannot promote. Not an HMM. Not a position_scale map.


Permutation of the residual *values* leaves mean and std unchanged, so IR
is invariant. The old time_shuffle_ir was a no-op (PIT JSONs had
time_shuffle_ir == observed_ir). Use block bootstrap with replacement
and a concentration share instead.

Sign-null percentile (Null A) does not replace mean |IR| concentration
(Concentration A). They answer different questions. A concentrated path
can look unusual under Null A and still fail the locked gate.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Mapping, Sequence

import numpy as np
import pandas as pd

from .evaluate import (
    DEFAULT_MAX_PLACEBO_FRAC,
    DEFAULT_MAX_PLACEBO_IR,
    annualized_ir,
    is_concentrated_placebo,
    placebo_frac_of_observed,
    sign_placebo_ir,
)


# F1/F2/F3 are negative-control objects for the new methodology. Not revival.
RESEARCH_ROLES: Dict[str, str] = {
    "f1": "negative_control",
    "f2": "negative_control",
    "f3": "negative_control",
    "f2_oos_hedged": "negative_control",
    "f2_resid_ols": "negative_control",
    "f2_resid_l2": "negative_control",
    "ai_infra_memory_bottleneck": "negative_control",
    "energy_x_ai_power_coupling": "negative_control",
    "longevity_healthspan_demand": "negative_control",
}

DEFAULT_SIGN_NULL_N = 5000
DEFAULT_BLOCK_NULL_N = 2000
DEFAULT_BLOCK_LENGTHS = (5, 21, 60)
DEFAULT_REGIME_NULL_N = 2000
GATE_IR_FLOOR = 0.40
REGIME_CONTRAST = ("complacency", "stress")
LOCKED_REGIME_LABELS = ("complacency", "normal", "stress")



@dataclass
class DiscoveryDiagnostics:
    n: int
    observed_ir: float
    time_shuffle_ir: float
    block_bootstrap_mean_abs_ir: float
    concentration_top5_share: float
    placebo_abs_ir: float
    deflated_sharpe: float
    note: str


def time_shuffle_ir(resid: pd.Series, n: int = 50, seed: int = 7) -> float:
    """LEGACY probe: MUST equal observed IR (order-invariant). Never a promotion test."""
    rng = np.random.default_rng(seed)
    vals = pd.Series(resid).dropna().to_numpy()
    if len(vals) < 60:
        return float("nan")
    irs = []
    for _ in range(n):
        shuf = rng.permutation(vals)
        irs.append(annualized_ir(pd.Series(shuf)))
    return float(np.nanmean(irs))


# Canonical name — same object. Do not treat 50-draw shuffle as Null A.
diagnostic_legacy_time_shuffle = time_shuffle_ir


def block_bootstrap_mean_abs_ir(
    resid: pd.Series, n: int = 50, block: int = 21, seed: int = 7
) -> float:
    """Resample contiguous blocks WITH replacement so mean/std can move."""
    dist = block_bootstrap_distribution(resid, n=n, block=block, seed=seed)
    return float(dist.mean_abs_ir)


def concentration_share(resid: pd.Series, q: float = 0.05) -> float:
    """Fraction of sum |r| coming from the largest q of |r| days (F2 diagnostic)."""
    s = pd.Series(resid).dropna().astype(float)
    if s.empty:
        return float("nan")
    mag = s.abs()
    k = max(1, int(round(len(mag) * q)))
    return float(mag.nlargest(k).sum() / (mag.sum() + 1e-12))


def deflated_sharpe_ratio(
    resid: pd.Series,
    *,
    n_trials: int = 1,
    observations_per_year: int = 252,
) -> float:
    """
    Bailey-Borwein-Lopez de Prado DSR-style deflation of the observed IR.
    Research logging only. Does not replace the locked concentration placebo.
    """
    s = pd.Series(resid).dropna().astype(float)
    n = len(s)
    if n < 60 or float(s.std()) == 0:
        return float("nan")
    daily_sr = float(s.mean() / s.std())
    t = float(n)
    g3 = float(s.skew())
    g4 = float(s.kurtosis() + 3.0)
    from math import erfc, sqrt, log

    if n_trials < 1:
        n_trials = 1
    if n_trials == 1:
        sr0 = 0.0
    else:
        z = sqrt(2.0 * log(n_trials))
        sr0 = z - (log(log(n_trials)) + log(4.0 * np.pi)) / (2.0 * z)
        sr0 = sr0 / sqrt(observations_per_year)
    denom = sqrt(max(1e-12, 1.0 - g3 * daily_sr + ((g4 - 1.0) / 4.0) * daily_sr**2))
    x = ((daily_sr - sr0) * sqrt(t - 1.0)) / denom
    dsr = 0.5 * erfc(-x / sqrt(2.0))
    return float(dsr)


# Canonical name — research logging only. Does not replace Concentration A.
diagnostic_dsr = deflated_sharpe_ratio


def diagnose(resid: pd.Series, n_trials: int = 1) -> DiscoveryDiagnostics:
    s = pd.Series(resid).dropna()
    return DiscoveryDiagnostics(
        n=int(len(s)),
        observed_ir=annualized_ir(s),
        time_shuffle_ir=time_shuffle_ir(s),
        block_bootstrap_mean_abs_ir=block_bootstrap_mean_abs_ir(s),
        concentration_top5_share=concentration_share(s),
        placebo_abs_ir=sign_placebo_ir(s),
        deflated_sharpe=deflated_sharpe_ratio(s, n_trials=n_trials),
        note=(
            "diagnostic only; locked gate is concentration placebo "
            "(mean |IR| of sign-randomized copies staying ≥40% of observed). "
            "time_shuffle_ir / diagnostic_legacy_time_shuffle equals observed_ir "
            "by construction (IR is order-invariant) — never a promotion test. "
            "deflated_sharpe / diagnostic_dsr is supplementary. "
            "Canonical research objects: Null A sign_null_distribution, "
            "Null B block_bootstrap_distribution, Concentration A/B. "
            "Neither null can promote."
        ),
    )


# ---------------------------------------------------------------------------
# Null A — residual sign-null (signed IR distribution)
# ---------------------------------------------------------------------------


def _as_vals(resid: pd.Series) -> np.ndarray:
    return pd.Series(resid).dropna().astype(float).to_numpy()


def _irs_from_matrix(samples: np.ndarray) -> np.ndarray:
    """Annualized IR for each row. pandas-compatible ddof=1 std."""
    means = samples.mean(axis=1)
    stds = samples.std(axis=1, ddof=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(stds > 0.0, means / stds * np.sqrt(252.0), np.nan)


def _empirical_ps(null_irs: np.ndarray, observed_ir: float) -> Dict[str, float]:
    finite = null_irs[np.isfinite(null_irs)]
    n = int(len(finite))
    if n == 0 or not np.isfinite(observed_ir):
        return {
            "observed_percentile": float("nan"),
            "empirical_p_value_one_sided": float("nan"),
            "empirical_p_value_two_sided": float("nan"),
        }
    obs = float(observed_ir)
    # Mid-rank percentile so a typical draw sits near 50, not 0/100 from ties.
    perc = 100.0 * (float(np.sum(finite < obs)) + 0.5 * float(np.sum(finite == obs))) / n
    if obs >= 0:
        p1 = (1.0 + float(np.sum(finite >= obs))) / (1.0 + n)
    else:
        p1 = (1.0 + float(np.sum(finite <= obs))) / (1.0 + n)
    p2 = (1.0 + float(np.sum(np.abs(finite) >= abs(obs)))) / (1.0 + n)
    return {
        "observed_percentile": float(perc),
        "empirical_p_value_one_sided": float(p1),
        "empirical_p_value_two_sided": float(p2),
    }


@dataclass
class SignNullResult:
    n: int
    seed: int
    observed_ir: float
    null_mean_ir: float
    null_std_ir: float
    null_mean_abs_ir: float
    observed_percentile: float
    empirical_p_value_one_sided: float
    empirical_p_value_two_sided: float
    cannot_promote: bool = True
    note: str = (
        "Null A: percentile of observed IR inside the signed-IR null. "
        "Not a promotion gate. Draw count is a computational sample."
    )

    def to_dict(self) -> Dict[str, Any]:
        return _jsonable(asdict(self))


def sign_null_distribution(
    resid: pd.Series,
    n: int = DEFAULT_SIGN_NULL_N,
    seed: int = 24,
) -> SignNullResult:
    """
    Vectorized sign-flip of r_t. Denominator magnitude structure is nearly
    fixed (var = E[r^2] − mean*^2); only the signed mean moves freely.
    """
    vals = _as_vals(resid)
    observed = annualized_ir(pd.Series(vals))
    if len(vals) < 60:
        return SignNullResult(
            n=0,
            seed=int(seed),
            observed_ir=float(observed) if np.isfinite(observed) else float("nan"),
            null_mean_ir=float("nan"),
            null_std_ir=float("nan"),
            null_mean_abs_ir=float("nan"),
            observed_percentile=float("nan"),
            empirical_p_value_one_sided=float("nan"),
            empirical_p_value_two_sided=float("nan"),
        )
    n = int(max(1, n))
    rng = np.random.default_rng(seed)
    signs = rng.choice(np.array([-1.0, 1.0]), size=(n, len(vals)))
    irs = _irs_from_matrix(signs * vals)
    finite = irs[np.isfinite(irs)]
    ps = _empirical_ps(irs, observed)
    return SignNullResult(
        n=int(len(finite)),
        seed=int(seed),
        observed_ir=float(observed),
        null_mean_ir=float(np.nanmean(finite)) if len(finite) else float("nan"),
        null_std_ir=float(np.nanstd(finite, ddof=1)) if len(finite) > 1 else float("nan"),
        null_mean_abs_ir=float(np.nanmean(np.abs(finite))) if len(finite) else float("nan"),
        observed_percentile=ps["observed_percentile"],
        empirical_p_value_one_sided=ps["empirical_p_value_one_sided"],
        empirical_p_value_two_sided=ps["empirical_p_value_two_sided"],
    )


# ---------------------------------------------------------------------------
# Null B — block bootstrap (mean and std both move)
# ---------------------------------------------------------------------------


def _block_sample_irs(
    vals: np.ndarray, block: int, n: int, rng: np.random.Generator
) -> np.ndarray:
    T = len(vals)
    b = max(5, int(block))
    n_blocks = int(np.ceil(T / b))
    n_pos = max(1, T - b + 1)
    cells = int(n) * n_blocks * b
    if cells > 8_000_000:
        irs = np.empty(n, dtype=float)
        offsets = np.arange(b)
        for i in range(n):
            starts = rng.integers(0, n_pos, size=n_blocks)
            idx = (starts[:, None] + offsets[None, :]).ravel()[:T]
            sample = vals[idx]
            sd = sample.std(ddof=1)
            irs[i] = (sample.mean() / sd) * np.sqrt(252.0) if sd > 0 else np.nan
        return irs
    starts = rng.integers(0, n_pos, size=(n, n_blocks))
    idx = starts[..., None] + np.arange(b)[None, None, :]
    idx = idx.reshape(n, n_blocks * b)[:, :T]
    return _irs_from_matrix(vals[idx])


@dataclass
class BlockNullResult:
    block: int
    n: int
    seed: int
    observed_ir: float
    mean_ir: float
    std_ir: float
    mean_abs_ir: float
    observed_percentile: float
    empirical_p_value_one_sided: float
    empirical_p_value_two_sided: float
    frac_ir_positive: float
    frac_ir_ge_gate: float
    p5: float
    p95: float
    cannot_promote: bool = True
    note: str = (
        "Null B: alternative histories retaining serial dependence. "
        "Do not average block lengths. 60-day blocks that keep 2022 are not "
        "validation. Cannot promote."
    )

    def to_dict(self) -> Dict[str, Any]:
        return _jsonable(asdict(self))


def block_bootstrap_distribution(
    resid: pd.Series,
    n: int = DEFAULT_BLOCK_NULL_N,
    block: int = 21,
    seed: int = 7,
) -> BlockNullResult:
    """Moving-block bootstrap WITH replacement. Mean and std both move."""
    vals = _as_vals(resid)
    observed = annualized_ir(pd.Series(vals))
    empty = BlockNullResult(
        block=int(block),
        n=0,
        seed=int(seed),
        observed_ir=float(observed) if np.isfinite(observed) else float("nan"),
        mean_ir=float("nan"),
        std_ir=float("nan"),
        mean_abs_ir=float("nan"),
        observed_percentile=float("nan"),
        empirical_p_value_one_sided=float("nan"),
        empirical_p_value_two_sided=float("nan"),
        frac_ir_positive=float("nan"),
        frac_ir_ge_gate=float("nan"),
        p5=float("nan"),
        p95=float("nan"),
    )
    if len(vals) < 60:
        return empty
    n = int(max(1, n))
    rng = np.random.default_rng(seed)
    irs = _block_sample_irs(vals, int(block), n, rng)
    finite = irs[np.isfinite(irs)]
    if len(finite) == 0:
        return empty
    ps = _empirical_ps(irs, observed)
    return BlockNullResult(
        block=int(max(5, int(block))),
        n=int(len(finite)),
        seed=int(seed),
        observed_ir=float(observed),
        mean_ir=float(np.nanmean(finite)),
        std_ir=float(np.nanstd(finite, ddof=1)) if len(finite) > 1 else float("nan"),
        mean_abs_ir=float(np.nanmean(np.abs(finite))),
        observed_percentile=ps["observed_percentile"],
        empirical_p_value_one_sided=ps["empirical_p_value_one_sided"],
        empirical_p_value_two_sided=ps["empirical_p_value_two_sided"],
        frac_ir_positive=float(np.mean(finite > 0.0)),
        frac_ir_ge_gate=float(np.mean(finite >= GATE_IR_FLOOR)),
        p5=float(np.nanpercentile(finite, 5)),
        p95=float(np.nanpercentile(finite, 95)),
    )


def block_bootstrap_family(
    resid: pd.Series,
    n: int = DEFAULT_BLOCK_NULL_N,
    blocks: Sequence[int] = DEFAULT_BLOCK_LENGTHS,
    seed: int = 7,
) -> Dict[int, BlockNullResult]:
    """One Null B result per block length. Never average the lengths."""
    return {
        int(b): block_bootstrap_distribution(resid, n=n, block=int(b), seed=seed + int(b))
        for b in blocks
    }


# ---------------------------------------------------------------------------
# Two concentration stats — do not fuse
# ---------------------------------------------------------------------------


@dataclass
class ConcentrationReport:
    ir_persistence_ratio: float
    ir_persistence_kill: bool
    placebo_abs_ir: float
    pnl_mass_top5: float
    pnl_mass_top10: float
    max_placebo_frac: float = DEFAULT_MAX_PLACEBO_FRAC
    cannot_promote: bool = True
    note: str = (
        "Concentration A = IR-persistence ratio (locked kill ≥0.40). "
        "Concentration B = P&L mass (top 5%/10% of |r| days). Do not fuse."
    )

    def to_dict(self) -> Dict[str, Any]:
        return _jsonable(asdict(self))


def concentration_report(resid: pd.Series) -> ConcentrationReport:
    s = pd.Series(resid).dropna()
    ir = annualized_ir(s)
    p_ir = sign_placebo_ir(s)
    frac = placebo_frac_of_observed(p_ir, ir)
    kill = is_concentrated_placebo(
        p_ir,
        ir,
        max_placebo_ir=DEFAULT_MAX_PLACEBO_IR,
        max_frac=DEFAULT_MAX_PLACEBO_FRAC,
    )
    return ConcentrationReport(
        ir_persistence_ratio=float(frac) if np.isfinite(frac) else float("nan"),
        ir_persistence_kill=bool(kill),
        placebo_abs_ir=float(p_ir) if np.isfinite(p_ir) else float("nan"),
        pnl_mass_top5=concentration_share(s, 0.05),
        pnl_mass_top10=concentration_share(s, 0.10),
    )


# ---------------------------------------------------------------------------
# Null 1 — regime-label permutation (diagnostic only)
# ---------------------------------------------------------------------------
# L2 labels {complacency, normal, stress} stay the 2026-08-27 classifier.
# This null asks whether IR differences across those labels exceed chance
# given occupancy (and, separately, given run lengths). It is not a timing
# signal s_t, not an HMM, and not a position_scale map.


def _day_index(idx) -> pd.DatetimeIndex:
    di = pd.DatetimeIndex(pd.to_datetime(idx, errors="coerce"))
    if getattr(di, "tz", None) is not None:
        di = di.tz_localize(None)
    return di.normalize()


def align_resid_labels(resid: pd.Series, labels: pd.Series) -> pd.DataFrame:
    """Inner-join residual and labels on a naive day index. Drops NaN residual."""
    r = pd.Series(resid).dropna().astype(float)
    g = pd.Series(labels)
    r.index = _day_index(r.index)
    g.index = _day_index(g.index)
    r = r[~r.index.duplicated(keep="last")].sort_index()
    g = g[~g.index.duplicated(keep="last")].sort_index()
    df = pd.concat([r.rename("r"), g.rename("g")], axis=1, join="inner")
    df = df[np.isfinite(df["r"])]
    df["g"] = df["g"].astype(str)
    return df.dropna(subset=["g"])


def _ir_vals(vals: np.ndarray) -> float:
    if len(vals) < 60:
        return float("nan")
    sd = float(np.std(vals, ddof=1))
    if sd == 0.0 or not np.isfinite(sd):
        return float("nan")
    return float(np.mean(vals) / sd * np.sqrt(252.0))


def regime_ir_table(resid: pd.Series, labels: pd.Series) -> Dict[str, Dict[str, float]]:
    df = align_resid_labels(resid, labels)
    out: Dict[str, Dict[str, float]] = {}
    for lab, sl in df.groupby("g"):
        vals = sl["r"].to_numpy(dtype=float)
        out[str(lab)] = {"n": int(len(vals)), "ir": _ir_vals(vals)}
    out["full"] = {"n": int(len(df)), "ir": _ir_vals(df["r"].to_numpy(dtype=float))}
    return out


def _contrast(r: np.ndarray, g: np.ndarray, a: str, b: str) -> float:
    ir_a = _ir_vals(r[g == a])
    ir_b = _ir_vals(r[g == b])
    if not (np.isfinite(ir_a) and np.isfinite(ir_b)):
        return float("nan")
    return float(ir_a - ir_b)


def regime_dwell_report(labels: pd.Series) -> Dict[str, Any]:
    g = pd.Series(labels).dropna().astype(str).to_numpy()
    if len(g) == 0:
        return {"n": 0, "by_label": {}, "frac_1day_runs": float("nan")}
    runs: List[tuple[str, int]] = []
    start = 0
    for i in range(1, len(g) + 1):
        if i == len(g) or g[i] != g[start]:
            runs.append((str(g[start]), int(i - start)))
            start = i
    by: Dict[str, Dict[str, float]] = {}
    for lab, length in runs:
        slot = by.setdefault(lab, {"n_runs": 0, "lengths": []})
        slot["n_runs"] += 1
        slot["lengths"].append(length)
    summary: Dict[str, Any] = {}
    n_one = 0
    for lab, slot in by.items():
        lens = np.asarray(slot["lengths"], dtype=float)
        n_one += int(np.sum(lens == 1))
        summary[lab] = {
            "n_runs": int(slot["n_runs"]),
            "mean_dwell": float(np.mean(lens)),
            "median_dwell": float(np.median(lens)),
            "max_dwell": float(np.max(lens)),
            "frac_1day": float(np.mean(lens == 1)),
        }
    n_runs = int(len(runs))
    return {
        "n": int(len(g)),
        "n_runs": n_runs,
        "frac_1day_runs": float(n_one / n_runs) if n_runs else float("nan"),
        "by_label": summary,
        "note": "Dwell of the locked 2026-08-27 labels. Not a new classifier.",
    }


def hysteresis_smooth(labels: pd.Series, min_dwell: int = 2) -> pd.Series:
    """
    Diagnostic smoother. Stay in the current label until a different label
    prints `min_dwell` consecutive days. Does NOT replace classify_regime.
    There is no dislocation override — that would be a timing signal s_t.
    """
    s = pd.Series(labels)
    g = s.astype(str).to_numpy()
    if len(g) == 0:
        return s.copy()
    md = max(1, int(min_dwell))
    out = np.empty(len(g), dtype=object)
    current = g[0]
    pending = None
    pending_n = 0
    for i, lab in enumerate(g):
        if lab == current:
            pending = None
            pending_n = 0
        else:
            if pending == lab:
                pending_n += 1
            else:
                pending = lab
                pending_n = 1
            if pending_n >= md:
                current = lab
                pending = None
                pending_n = 0
        out[i] = current
    return pd.Series(out, index=s.index, name=s.name or "regime_hysteresis")


def _run_blocks(g: np.ndarray) -> List[np.ndarray]:
    blocks: List[np.ndarray] = []
    start = 0
    for i in range(1, len(g) + 1):
        if i == len(g) or g[i] != g[start]:
            blocks.append(g[start:i])
            start = i
    return blocks


@dataclass
class RegimeLabelNullResult:
    n: int
    seed: int
    mode: str
    label_a: str
    label_b: str
    observed_ir_a: float
    observed_ir_b: float
    observed_delta: float
    null_mean_delta: float
    null_std_delta: float
    observed_percentile: float
    empirical_p_value_one_sided: float
    empirical_p_value_two_sided: float
    n_finite: int
    cannot_promote: bool = True
    note: str = (
        "Null 1: permute L2 labels, residual fixed. Occupancy mode keeps "
        "label counts; run_length mode shuffles dwell blocks. Not a timing "
        "signal. Not an HMM. Cannot promote."
    )

    def to_dict(self) -> Dict[str, Any]:
        return _jsonable(asdict(self))


def regime_label_permutation(
    resid: pd.Series,
    labels: pd.Series,
    *,
    n: int = DEFAULT_REGIME_NULL_N,
    seed: int = 31,
    mode: str = "occupancy",
    label_a: str = REGIME_CONTRAST[0],
    label_b: str = REGIME_CONTRAST[1],
) -> RegimeLabelNullResult:
    """
    Null 1. Residual path is fixed. Labels move.

    occupancy: shuffle day labels (same counts).
    run_length: shuffle contiguous label blocks (same dwell multiset).
    """
    df = align_resid_labels(resid, labels)
    r = df["r"].to_numpy(dtype=float)
    g = df["g"].to_numpy()
    obs_a = _ir_vals(r[g == label_a])
    obs_b = _ir_vals(r[g == label_b])
    observed = (
        float(obs_a - obs_b)
        if np.isfinite(obs_a) and np.isfinite(obs_b)
        else float("nan")
    )
    empty = RegimeLabelNullResult(
        n=0,
        seed=int(seed),
        mode=str(mode),
        label_a=str(label_a),
        label_b=str(label_b),
        observed_ir_a=float(obs_a) if np.isfinite(obs_a) else float("nan"),
        observed_ir_b=float(obs_b) if np.isfinite(obs_b) else float("nan"),
        observed_delta=observed,
        null_mean_delta=float("nan"),
        null_std_delta=float("nan"),
        observed_percentile=float("nan"),
        empirical_p_value_one_sided=float("nan"),
        empirical_p_value_two_sided=float("nan"),
        n_finite=0,
    )
    if len(r) < 120 or not np.isfinite(observed):
        return empty
    n = int(max(1, n))
    rng = np.random.default_rng(seed)
    deltas = np.empty(n, dtype=float)
    if mode == "run_length":
        blocks = _run_blocks(g)
        n_blocks = len(blocks)
        for i in range(n):
            order = rng.permutation(n_blocks)
            g_perm = np.concatenate([blocks[j] for j in order])
            deltas[i] = _contrast(r, g_perm, label_a, label_b)
    else:
        # occupancy (default)
        for i in range(n):
            g_perm = rng.permutation(g)
            deltas[i] = _contrast(r, g_perm, label_a, label_b)
    ps = _empirical_ps(deltas, observed)
    finite = deltas[np.isfinite(deltas)]
    return RegimeLabelNullResult(
        n=int(n),
        seed=int(seed),
        mode=str(mode),
        label_a=str(label_a),
        label_b=str(label_b),
        observed_ir_a=float(obs_a),
        observed_ir_b=float(obs_b),
        observed_delta=float(observed),
        null_mean_delta=float(np.nanmean(finite)) if len(finite) else float("nan"),
        null_std_delta=float(np.nanstd(finite, ddof=1)) if len(finite) > 1 else float("nan"),
        observed_percentile=ps["observed_percentile"],
        empirical_p_value_one_sided=ps["empirical_p_value_one_sided"],
        empirical_p_value_two_sided=ps["empirical_p_value_two_sided"],
        n_finite=int(len(finite)),
    )


def hysteresis_sensitivity(
    resid: pd.Series,
    labels: pd.Series,
    min_dwell: int = 2,
) -> Dict[str, Any]:
    """IR table and dwell under hysteresis-smoothed labels. Sensitivity only."""
    smoothed = hysteresis_smooth(labels, min_dwell=min_dwell)
    return {
        "min_dwell": int(min_dwell),
        "cannot_promote": True,
        "ir_by_regime": regime_ir_table(resid, smoothed),
        "dwell": regime_dwell_report(smoothed),
        "note": (
            "Hysteresis is a sensitivity of the locked labels, not a replacement "
            "classifier and not a position_scale input."
        ),
    }


# ---------------------------------------------------------------------------
# Negative-control audit (cannot promote)
# ---------------------------------------------------------------------------


def _q1(p_one: float) -> str:
    if not np.isfinite(p_one):
        return "inconclusive"
    if p_one <= 0.05:
        return "yes"  # observed IR is unusual under sign-null
    if p_one > 0.10:
        return "no"
    return "inconclusive"


def _q2(blocks: Mapping[int, BlockNullResult]) -> str:
    b5 = blocks.get(5)
    b21 = blocks.get(21)
    b60 = blocks.get(60)
    if not (b5 and b21 and b60):
        return "inconclusive"
    f5, f21, f60 = b5.frac_ir_ge_gate, b21.frac_ir_ge_gate, b60.frac_ir_ge_gate
    if not all(np.isfinite(x) for x in (f5, f21, f60)):
        return "inconclusive"
    if f5 >= 0.80 and f21 >= 0.80 and f60 >= 0.80:
        return "robust_dependence_evidence"
    if f5 < 0.50 and f60 >= 0.80:
        return "regime_cluster_dependence"
    if f5 < 0.50 and f21 < 0.50 and f60 < 0.50:
        return "weak_statistical_evidence"
    return "mixed"


def _q3(conc: ConcentrationReport) -> str:
    if conc.ir_persistence_kill:
        return "yes"  # concentrated (kill)
    if not np.isfinite(conc.ir_persistence_ratio):
        return "inconclusive"
    return "no"


def label_negative_control(
    *,
    sign_null: SignNullResult,
    conc: ConcentrationReport,
    blocks: Mapping[int, BlockNullResult],
) -> List[str]:
    labels: List[str] = []
    if np.isfinite(sign_null.empirical_p_value_one_sided) and (
        sign_null.empirical_p_value_one_sided > 0.10
    ):
        labels.append("STATISTICAL_FAIL")
    if conc.ir_persistence_kill:
        labels.append("CONCENTRATION_FAIL")
    q2 = _q2(blocks)
    if q2 == "regime_cluster_dependence":
        labels.append("DEPENDENCE_FAIL")
    # Mechanism / replication are Phase C — never inferred here.
    if "CONCENTRATION_FAIL" in labels and q2 == "regime_cluster_dependence":
        labels.append("REGIME_FAIL")
    return labels


@dataclass
class NegativeControlAudit:
    force_id: str
    research_role: str
    source: str
    n_days: int
    observed_ir: float
    sign_null: Dict[str, Any]
    block_bootstrap: Dict[str, Any]
    concentration: Dict[str, Any]
    labels: List[str]
    audit_questions: Dict[str, str]
    cannot_promote: bool = True
    capital: int = 0
    note: str = (
        "Negative-control audit. Desired result is that the methodology "
        "exposes why this object must not be promoted. F2 → PASS would "
        "mean distrust the framework, not revive F2."
    )

    def to_dict(self) -> Dict[str, Any]:
        return _jsonable(asdict(self))


def audit_residual(
    resid: pd.Series,
    *,
    force_id: str,
    source: str = "",
    n_sign: int = DEFAULT_SIGN_NULL_N,
    n_block: int = DEFAULT_BLOCK_NULL_N,
    sign_seed: int = 24,
    block_seed: int = 7,
) -> NegativeControlAudit:
    """Run Null A, Null B, and both concentration stats. Cannot promote."""
    s = pd.Series(resid).dropna()
    observed = annualized_ir(s)
    sign_null = sign_null_distribution(s, n=n_sign, seed=sign_seed)
    blocks = block_bootstrap_family(s, n=n_block, seed=block_seed)
    conc = concentration_report(s)
    labels = label_negative_control(sign_null=sign_null, conc=conc, blocks=blocks)
    role = RESEARCH_ROLES.get(str(force_id).lower(), "negative_control")
    questions = {
        "Q1_statistical_null": _q1(sign_null.empirical_p_value_one_sided),
        "Q2_dependence": _q2(blocks),
        "Q3_concentration": _q3(conc),
        "Q4_mechanism": "queued",
        "Q5_independence": "queued",
    }
    # 60 looks great + concentration kill → still kill (already in labels).
    if conc.ir_persistence_kill:
        questions["concentration_overrides_block60"] = "still_kill"
    return NegativeControlAudit(
        force_id=str(force_id),
        research_role=role,
        source=str(source),
        n_days=int(len(s)),
        observed_ir=float(observed) if np.isfinite(observed) else float("nan"),
        sign_null=sign_null.to_dict(),
        block_bootstrap={str(k): v.to_dict() for k, v in blocks.items()},
        concentration=conc.to_dict(),
        labels=labels,
        audit_questions=questions,
    )


def distrust_framework_if_f2_looks_clean(audits: Sequence[NegativeControlAudit]) -> bool:
    """If F2 is unusual under Null A and is not concentration-killed, the validator is too loose."""
    for a in audits:
        fid = str(a.force_id).lower()
        if not (fid.startswith("f2") or fid == "energy_x_ai_power_coupling"):
            continue
        conc_fail = "CONCENTRATION_FAIL" in a.labels
        stat_fail = "STATISTICAL_FAIL" in a.labels
        if (not conc_fail) and (not stat_fail):
            return True
    return False


def _jsonable(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {str(k): _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonable(v) for v in obj]
    if isinstance(obj, (np.floating, float)):
        x = float(obj)
        if not np.isfinite(x):
            return None
        return x
    if isinstance(obj, (np.integer, int)) and not isinstance(obj, bool):
        return int(obj)
    if isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    if obj is None:
        return None
    return obj
