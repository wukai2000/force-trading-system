#!/usr/bin/env python3
"""
Force 2 — walk-forward + costs under the *corrected* OOS hedged residual.

Same tickets as Phase A (not Option-B):
  legs:      VST, ETN, PWR
  controls:  XLU, QQQ
  residual:  r_basket,t − β_{t−1}' r_controls,t   (lookback=60)

This is an engine-correction review of a *paused* force. It does not un-pause
or allocate capital. Verdict is advisory for the human.

Cost model (one-way bps applied to estimated daily turnover):
  - Hedge turnover: |Δβ_XLU| + |Δβ_QQQ|
  - Leg rebalance:  0.5 * Σ_i |r_i − r_basket|  (daily restore to EW)
  - Net residual = gross residual − turnover * (bps / 1e4)

Scenarios: 0 / 1 / 5 / 10 bps one-way.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd

from force_engine.evaluate import annualized_ir, sign_placebo_ir
from force_engine.neutralize import neutralize_prices
from force_learning.data.cache import data_root
from force_learning.data.panel import _load_close

LEGS = ["VST", "ETN", "PWR"]
CONTROLS = ["XLU", "QQQ"]
OLS_LB = 60
COST_BPS = [0, 1, 5, 10]

# Advisory review criteria (not a silent un-pause)
HARD = {
    "min_full_ir_gross": 0.40,
    "min_full_ir_5bp": 0.40,
    "max_abs_beta": 0.80,
    "max_placebo_ir": 0.15,
    "min_overlap_years": 8,
}
SOFT = {
    "min_ir_ex_2022_23": 0.20,  # concentration stress
    "min_positive_regimes": 3,  # of 4 calendar blocks
}


def load_prices() -> pd.DataFrame:
    cols = {}
    for t in LEGS + CONTROLS:
        s = _load_close(t)
        if s is None or s.empty:
            raise RuntimeError(f"missing price {t}")
        cols[t] = s
    return pd.DataFrame(cols)


def leg_rebalance_turnover(prices: pd.DataFrame, legs: list[str]) -> pd.Series:
    """Daily turnover to restore equal weights after return drift."""
    rets = prices[legs].pct_change(fill_method=None)
    basket = rets.mean(axis=1)
    # fraction of portfolio traded ≈ 0.5 * sum |r_i - r_b|
    to = 0.5 * (rets.sub(basket, axis=0).abs().sum(axis=1))
    return to.rename("leg_turnover")


def hedge_turnover(betas: pd.DataFrame, controls: list[str]) -> pd.Series:
    cols = [f"beta_{c}" for c in controls]
    d = betas[cols].diff().abs().sum(axis=1)
    return d.rename("hedge_turnover")


def apply_costs(residual: pd.Series, turnover: pd.Series, bps: float) -> pd.Series:
    cost = turnover.reindex(residual.index).fillna(0.0) * (bps / 1e4)
    return (residual - cost).rename(f"resid_net_{bps:g}bp")


def window_ir(s: pd.Series, start: str, end: str) -> dict:
    sl = s.loc[start:end].dropna()
    return {
        "start": start,
        "end": end,
        "n": int(len(sl)),
        "ir": annualized_ir(sl) if len(sl) >= 40 else float("nan"),
        "mean_daily": float(sl.mean()) if len(sl) else float("nan"),
        "ann_vol": float(sl.std() * np.sqrt(252)) if len(sl) > 1 else float("nan"),
    }


def calendar_regimes(s: pd.Series) -> list[dict]:
    blocks = [
        ("2017-01-01", "2019-12-31", "2017–2019"),
        ("2020-01-01", "2021-12-31", "2020–2021"),
        ("2022-01-01", "2023-12-31", "2022–2023"),
        ("2024-01-01", "2026-12-31", "2024–2026"),
    ]
    out = []
    for a, b, label in blocks:
        m = window_ir(s, a, b)
        m["label"] = label
        out.append(m)
    return out


def annual_folds(s: pd.Series) -> list[dict]:
    years = sorted({d.year for d in s.dropna().index})
    out = []
    for y in years:
        m = window_ir(s, f"{y}-01-01", f"{y}-12-31")
        m["label"] = str(y)
        out.append(m)
    return out


def rolling_2y_ir(s: pd.Series) -> pd.DataFrame:
    """Trailing 2-year (504d) IR path."""
    s = s.dropna()
    win = 504
    rows = []
    for i in range(win, len(s)):
        sl = s.iloc[i - win : i]
        rows.append(
            {
                "date": s.index[i],
                "ir_2y": annualized_ir(sl),
            }
        )
    return pd.DataFrame(rows).set_index("date")


def maybe_plot(
    resid_gross: pd.Series,
    resid_5bp: pd.Series,
    regimes: list[dict],
    roll: pd.DataFrame,
    out: Path,
) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return
    fig, axes = plt.subplots(3, 1, figsize=(12, 9), sharex=False)
    ax = axes[0]
    ax.plot(resid_gross.index, resid_gross.cumsum(), label="gross OOS residual", color="#1f4e79", lw=1.2)
    ax.plot(resid_5bp.index, resid_5bp.cumsum(), label="net 5bp one-way", color="#8b4a2b", lw=1.0, alpha=0.9)
    ax.set_title("Force 2 — cumulative OOS residual (VST+ETN+PWR vs XLU+QQQ)")
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(True, alpha=0.25)

    ax = axes[1]
    labels = [r["label"] for r in regimes]
    irs = [r["ir"] if r["ir"] == r["ir"] else 0 for r in regimes]
    colors = ["#2d6a4f" if v >= 0.40 else ("#b08900" if v >= 0 else "#9b2226") for v in irs]
    ax.bar(labels, irs, color=colors, edgecolor="#333", width=0.6)
    ax.axhline(0.40, color="#333", ls="--", lw=0.8, label="gate 0.40")
    ax.axhline(0, color="#666", lw=0.6)
    ax.set_ylabel("IR")
    ax.set_title("Calendar-block IR (gross)")
    ax.legend(fontsize=8)
    ax.grid(True, axis="y", alpha=0.25)

    ax = axes[2]
    if not roll.empty:
        ax.plot(roll.index, roll["ir_2y"], color="#1f4e79", lw=1.0)
        ax.axhline(0.40, color="#333", ls="--", lw=0.8)
        ax.axhline(0, color="#666", lw=0.6)
        ax.set_title("Trailing 2-year IR (gross)")
        ax.set_ylabel("IR")
        ax.grid(True, alpha=0.25)

    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=130)
    plt.close(fig)


def advisory_verdict(
    full_gross: float,
    full_5bp: float,
    mean_betas: dict,
    placebo: float,
    years: float,
    regimes: list[dict],
    ir_ex_2223: float,
) -> dict:
    fail_hard: list[str] = []
    fail_soft: list[str] = []

    if years < HARD["min_overlap_years"]:
        fail_hard.append(f"years {years:.1f} < {HARD['min_overlap_years']}")
    if not (full_gross >= HARD["min_full_ir_gross"]):
        fail_hard.append(f"gross IR {full_gross:.3f} < {HARD['min_full_ir_gross']}")
    if not (full_5bp >= HARD["min_full_ir_5bp"]):
        fail_hard.append(f"5bp net IR {full_5bp:.3f} < {HARD['min_full_ir_5bp']}")
    if not (placebo < HARD["max_placebo_ir"]):
        fail_hard.append(f"placebo IR {placebo:.3f} ≥ {HARD['max_placebo_ir']}")
    for c, b in mean_betas.items():
        if abs(b) >= HARD["max_abs_beta"]:
            fail_hard.append(f"|β_{c}| {abs(b):.3f} ≥ {HARD['max_abs_beta']}")

    pos = sum(1 for r in regimes if r["ir"] == r["ir"] and r["ir"] > 0)
    if pos < SOFT["min_positive_regimes"]:
        fail_soft.append(f"positive regimes {pos} < {SOFT['min_positive_regimes']}")
    if not (ir_ex_2223 >= SOFT["min_ir_ex_2022_23"]):
        fail_soft.append(
            f"IR ex-2022/23 {ir_ex_2223:.3f} < soft floor {SOFT['min_ir_ex_2022_23']}"
        )
    # Concentration: 2022-23 dominates if its IR is high and others weak
    r22 = next((r for r in regimes if r["label"] == "2022–2023"), None)
    r17 = next((r for r in regimes if r["label"] == "2017–2019"), None)
    if r22 and r17 and r22["ir"] == r22["ir"] and r17["ir"] == r17["ir"]:
        if r22["ir"] > 1.0 and r17["ir"] < 0.25:
            fail_soft.append("2022–23 concentration (IR>1.0 while 2017–19 <0.25)")

    if fail_hard:
        status = "KEEP_PAUSED_HARD_FAIL"
    elif fail_soft:
        status = "KEEP_PAUSED_SOFT_FAIL"
    else:
        status = "CANDIDATE_FOR_HUMAN_UNPAUSE"  # still no capital

    return {
        "status": status,
        "fail_hard": fail_hard,
        "fail_soft": fail_soft,
        "capital": 0,
        "force_status_action": "leave_paused",
    }


def main() -> None:
    print("=== Force 2 walk-forward + costs (OOS hedged residual) ===")
    print(f"legs={LEGS}  controls={CONTROLS}  lookback={OLS_LB}")
    print("NOTE: advisory only — does not un-pause or allocate capital.\n")

    prices = load_prices()
    panel = neutralize_prices(prices, LEGS, CONTROLS, lookback=OLS_LB)
    resid = panel.residual.dropna()
    betas = panel.betas.reindex(resid.index)

    # Turnover
    leg_to = leg_rebalance_turnover(prices, LEGS).reindex(resid.index).fillna(0.0)
    hedge_to = hedge_turnover(betas, CONTROLS).reindex(resid.index).fillna(0.0)
    total_to = (leg_to + hedge_to).rename("turnover")

    # Cost scenarios
    net = {bps: apply_costs(resid, total_to, bps) for bps in COST_BPS}

    years = (resid.index.max() - resid.index.min()).days / 365.25
    mean_betas = {c: float(betas[f"beta_{c}"].mean()) for c in CONTROLS}
    placebo = sign_placebo_ir(resid)
    full_gross = annualized_ir(resid)
    full_nets = {bps: annualized_ir(net[bps]) for bps in COST_BPS}

    regimes = calendar_regimes(resid)
    annuals = annual_folds(resid)
    # Exclude 2022-23
    mask_ex = ~((resid.index >= "2022-01-01") & (resid.index <= "2023-12-31"))
    ir_ex = annualized_ir(resid.loc[mask_ex])
    roll = rolling_2y_ir(resid)

    # Mean daily turnover stats
    to_stats = {
        "mean_daily_turnover": float(total_to.mean()),
        "mean_leg_turnover": float(leg_to.mean()),
        "mean_hedge_turnover": float(hedge_to.mean()),
        "ann_turnover_approx": float(total_to.mean() * 252),
    }

    verdict = advisory_verdict(
        full_gross=full_gross,
        full_5bp=full_nets[5],
        mean_betas=mean_betas,
        placebo=placebo,
        years=years,
        regimes=regimes,
        ir_ex_2223=ir_ex,
    )

    out_dir = data_root() / "force2"
    out_dir.mkdir(parents=True, exist_ok=True)
    charts = ROOT / "charts" / "force2"
    charts.mkdir(parents=True, exist_ok=True)

    # Daily series
    daily = pd.concat(
        [
            resid.rename("resid_gross"),
            net[5].rename("resid_net_5bp"),
            net[10].rename("resid_net_10bp"),
            total_to,
            leg_to,
            hedge_to,
            betas,
            panel.basket.reindex(resid.index).rename("basket"),
        ],
        axis=1,
    )
    daily.to_csv(out_dir / "force2_walkforward_daily.csv")

    # Regime + annual tables
    pd.DataFrame(regimes).to_csv(out_dir / "force2_walkforward_regimes.csv", index=False)
    pd.DataFrame(annuals).to_csv(out_dir / "force2_walkforward_annual.csv", index=False)
    if not roll.empty:
        roll.to_csv(out_dir / "force2_walkforward_rolling2y.csv")

    summary = {
        "force_id": "energy_x_ai_power_coupling",
        "tradable": "residual_spread",
        "legs": LEGS,
        "controls": CONTROLS,
        "n_days": int(len(resid)),
        "years": years,
        "start": str(resid.index.min().date()),
        "end": str(resid.index.max().date()),
        "full_ir_gross": full_gross,
        "full_ir_by_cost_bps": full_nets,
        "placebo_ir": placebo,
        "mean_betas": mean_betas,
        "turnover": to_stats,
        "regimes_gross": regimes,
        "ir_excluding_2022_23": ir_ex,
        "verdict": verdict,
        "note": "Advisory engine-correction review. Leave force paused. Capital $0.",
    }
    with (out_dir / "force2_walkforward_summary.json").open("w") as f:
        json.dump(summary, f, indent=2, default=str)

    maybe_plot(resid, net[5], regimes, roll, charts / "force2_walkforward.png")

    # Console report
    print("--- Full sample ---")
    print(f"  window: {resid.index.min().date()} → {resid.index.max().date()}  n={len(resid)}  years={years:.2f}")
    print(f"  gross IR:           {full_gross:.3f}")
    for bps in COST_BPS:
        print(f"  net IR ({bps:2g}bp 1-way): {full_nets[bps]:.3f}")
    print(f"  placebo IR:         {placebo:.3f}")
    print(f"  mean β_XLU:         {mean_betas['XLU']:.3f}")
    print(f"  mean β_QQQ:         {mean_betas['QQQ']:.3f}")
    print(f"  mean daily turnover:{to_stats['mean_daily_turnover']:.4f}  (~{to_stats['ann_turnover_approx']:.1f}x /yr)")
    print(f"    leg / hedge:      {to_stats['mean_leg_turnover']:.4f} / {to_stats['mean_hedge_turnover']:.4f}")
    print()
    print("--- Calendar regimes (gross) ---")
    for r in regimes:
        flag = "PASS" if r["ir"] == r["ir"] and r["ir"] >= 0.40 else ("+" if r["ir"] == r["ir"] and r["ir"] > 0 else "WEAK")
        print(f"  {r['label']:12s}  n={r['n']:4d}  IR={r['ir']:.3f}  [{flag}]")
    print(f"  ex-2022/23           IR={ir_ex:.3f}")
    print()
    print("--- Annual folds (gross) ---")
    for a in annuals:
        if a["n"] < 40:
            continue
        print(f"  {a['label']}  n={a['n']:4d}  IR={a['ir']:.3f}")
    print()
    print("=== ADVISORY VERDICT ===")
    print(f"  status:     {verdict['status']}")
    print(f"  hard fails: {verdict['fail_hard'] or 'none'}")
    print(f"  soft fails: {verdict['fail_soft'] or 'none'}")
    print(f"  action:     {verdict['force_status_action']}  capital={verdict['capital']}")
    print()
    print(f"Wrote {out_dir / 'force2_walkforward_summary.json'}")
    print(f"Chart  {charts / 'force2_walkforward.png'}")
    print("Capital: $0. Trump Account = SPYM. Force 2 remains paused.")


if __name__ == "__main__":
    main()
