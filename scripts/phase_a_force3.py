#!/usr/bin/env python3
"""
Force 3 Phase A — longevity / healthspan demand residual SPREAD.

Ticket group LOCKED 2026-08-24 before this file existed as a runnable scan:
  legs:      IHF, IHI, XHS
  OLS ctrls: XLV, XBI
  tradable:  residual_spread (long legs, short β-weighted controls)

Promotion uses force_engine.pipeline.evaluate_candidate only.
Raw basket IR is printed as DIAGNOSTIC and cannot pass the gate.

Gated: this script will not fetch or score until FORCE3_LOCK_ACK=1.

  FORCE3_LOCK_ACK=1 PYTHONPATH=. python scripts/phase_a_force3.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd

from force_engine.neutralize import NeutralizationError
from force_engine.pipeline import evaluate_candidate, spec_from_yaml
from force_learning.data.cache import data_root
from force_learning.data.fetch_prices import update_prices
from force_learning.data.panel import _load_close, coherence


def _price_panel(tickers) -> pd.DataFrame:
    cols = {}
    for t in tickers:
        s = _load_close(t)
        if s is None:
            raise NeutralizationError(f"missing price {t} — fetch first")
        cols[t] = s
    return pd.DataFrame(cols)


def maybe_plot(resid: pd.Series, out: Path) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(resid.index, resid.cumsum(), label="cum OOS residual vs XLV+XBI")
    ax.set_title("Force 3 Phase A — IHF+IHI+XHS residual spread vs XLV+XBI")
    ax.legend()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out, dpi=120)
    plt.close(fig)


def main() -> None:
    if os.environ.get("FORCE3_LOCK_ACK") != "1":
        print("=== Force 3 is LOCKED (config/force3.yaml) ===")
        print("Tickets, controls, and gates are pre-registered.")
        print("This script will not fetch prices or score until acknowledged.")
        print("After the lock is accepted in chat:")
        print("  FORCE3_LOCK_ACK=1 PYTHONPATH=. python scripts/phase_a_force3.py")
        sys.exit(2)

    spec = spec_from_yaml(ROOT / "config" / "force3.yaml")
    extra = ["IBB", "SPY", "VOO", "TLT"]
    print("=== Force 3 Phase A (residual spread ONLY) ===")
    print(f"legs={spec.legs}  controls={spec.controls}  tradable={spec.tradable}")
    print("GATE locked before scan:", dict(spec.gate))
    update_prices(tickers=list(spec.legs) + list(spec.controls) + extra, period="max", sleep_s=0.6)
    prices = _price_panel(list(spec.legs) + list(spec.controls) + extra)
    result = evaluate_candidate(spec, prices)

    out_dir = data_root() / "force3"
    out_dir.mkdir(parents=True, exist_ok=True)
    df = pd.concat([result.panel.residual, result.panel.betas, result.panel.basket.rename("basket")], axis=1)
    coh = coherence(legs=spec.legs, lookback=60)
    if coh is not None:
        df["coherence"] = coh
    df.to_csv(out_dir / "force3_daily_residual.csv")
    pd.Series(
        {k: str(v) for k, v in {**result.gate.metrics, "verdict": result.gate.verdict, "failures": result.gate.failures}.items()}
    ).to_csv(out_dir / "force3_gate.csv", header=False)
    maybe_plot(result.panel.residual, ROOT / "artifacts" / "charts" / "force3_residual.png")

    print("DIAGNOSTIC raw basket IR (DO NOT USE FOR GATE):", result.diagnostic.get("raw_basket_ir"))
    print("=== PRE-REGISTERED GATE ===")
    print("  verdict:", result.gate.verdict)
    print("  failures:", result.gate.failures)
    print("  leading veto:", result.clock.veto, result.clock.veto_reason)
    for k, v in result.gate.metrics.items():
        if k != "raw_basket_ir_diagnostic_only":
            print(f"  {k}: {v}")
    print("Capital: $0. Trump Account = SPYM. python_sim only.")


if __name__ == "__main__":
    main()
