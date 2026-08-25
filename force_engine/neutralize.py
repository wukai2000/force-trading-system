"""
Dynamic factor neutralization.

Tradable series = out-of-sample hedged return:
    r_basket_t − β_{t-1}' r_controls_t

Betas are estimated on the prior `lookback` window **with intercept**
(so β is not biased by a mean), but the intercept is NOT subtracted from
the traded residual. A persistent force premium must survive here; F1/F2
used in-sample residuals *including* intercept, which mechanically
zeroed a slow alpha.

Raw long-only baskets cannot be scored.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence

import numpy as np
import pandas as pd


class NeutralizationError(ValueError):
    """Raised when a candidate is offered without valid controls / residual."""


@dataclass
class NeutralizedPanel:
    residual: pd.Series  # OOS hedged return (promotion series)
    betas: pd.DataFrame
    basket: pd.Series
    lookback: int
    controls: List[str]

    @property
    def latest_hedge_weights(self) -> Dict[str, float]:
        if self.betas.empty:
            return {}
        last = self.betas.iloc[-1]
        return {c: float(last.get(f"beta_{c}", np.nan)) for c in self.controls}


def equal_weight_returns(prices: pd.DataFrame, legs: Sequence[str]) -> pd.Series:
    missing = [t for t in legs if t not in prices.columns]
    if missing:
        raise NeutralizationError(f"missing legs: {missing}")
    rets = prices[list(legs)].pct_change(fill_method=None)
    return rets.mean(axis=1).rename("basket")


def rolling_ols_residual(
    basket: pd.Series,
    controls: pd.DataFrame,
    lookback: int = 60,
) -> NeutralizedPanel:
    if controls is None or controls.empty:
        raise NeutralizationError("controls are required — raw baskets cannot be scored")
    if lookback < 20:
        raise NeutralizationError("lookback too short for stable betas")

    df = pd.concat([basket.rename("basket"), controls], axis=1).dropna()
    ctrl_names = list(controls.columns)
    if len(df) < lookback + 5:
        raise NeutralizationError(f"not enough overlapping rows ({len(df)}) for lookback={lookback}")

    y_all = df["basket"].values
    x_factors = np.column_stack([df[c].values for c in ctrl_names])
    x_with_int = np.column_stack([np.ones(len(df)), x_factors])

    resid = []
    betas = {c: [] for c in ctrl_names}
    idx = []
    # Estimate on [i-lookback, i) ; apply to i  (strictly lagged β)
    for i in range(lookback, len(df)):
        sl = slice(i - lookback, i)
        coef, *_ = np.linalg.lstsq(x_with_int[sl], y_all[sl], rcond=None)
        b = coef[1:]
        hedged = float(y_all[i] - b @ x_factors[i])
        resid.append(hedged)
        for j, c in enumerate(ctrl_names):
            betas[c].append(float(b[j]))
        idx.append(df.index[i])

    beta_df = pd.DataFrame({f"beta_{c}": betas[c] for c in ctrl_names}, index=idx)
    return NeutralizedPanel(
        residual=pd.Series(resid, index=idx, name="resid_oos_hedged"),
        betas=beta_df,
        basket=df["basket"].loc[idx],
        lookback=lookback,
        controls=ctrl_names,
    )


def neutralize_prices(
    prices: pd.DataFrame,
    legs: Sequence[str],
    controls: Sequence[str],
    lookback: int = 60,
) -> NeutralizedPanel:
    if not controls:
        raise NeutralizationError("refusing to score a basket with empty controls")
    missing_c = [t for t in controls if t not in prices.columns]
    if missing_c:
        raise NeutralizationError(f"missing controls: {missing_c}")
    px = prices[list(dict.fromkeys(list(legs) + list(controls)))].dropna(how="any")
    if px.empty:
        raise NeutralizationError("no overlapping dates across legs and controls")
    basket = equal_weight_returns(px, legs)
    ctrl_rets = px[list(controls)].pct_change(fill_method=None)
    return rolling_ols_residual(basket, ctrl_rets, lookback=lookback)
