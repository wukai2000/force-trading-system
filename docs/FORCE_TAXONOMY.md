# Force Taxonomy — Tug-of-War Model (locked 2026-08-25 post-F3)

After three consecutive Phase-A gate failures (F1 IR 0.003, F2 IR 0.013 then soft 0.52 with concentration, F3 IR 0.131 + stealth β_XLV 0.841), the identification problem is reframed.

## Core hypothesis

A slow **stable force** (demographic WTP, multi-year infrastructure scarcity, structural power constraint, etc.) is continuously tugged by three other force classes. Raw or single-layer residuals therefore measure the instantaneous position of the knot, not the rope.

| Class | Nature | Half-life | Typical amplitude | Detection signature |
|-------|--------|-----------|-------------------|---------------------|
| **Stable** | Structural, under-noticed, persistent claim about cash-flows / discount rates / capital allocation | Years–decades | Low-to-moderate, regime-dependent | Survives multi-layer residualization; positive IR in low-dispersion, low-stress regimes |
| **Hyper** | Narrative / hype / media / thematic momentum spikes | Days–months | High, bursty | Lights up with news density, VIX term-structure inversion, high cross-sectional dispersion |
| **Regular market** | Systematic beta, sector rotation, style (value/growth/size/mom), liquidity | Continuous, rapidly arbitraged | Medium, always present | Absorbed by major ETFs (SPY, QQQ, XLV, XLU, SMH…); high |β| on controls |
| **Noisy / idiosyncratic** | Single-name earnings, microstructure, one-off events that do not propagate | Hours–weeks | High frequency, mean-reverting | High residual variance after all other layers; low coherence across legs |

## Why previous definitions failed

1. Long-only theme baskets = regular-market force dressed as stable.
2. In-sample OLS *including intercept* zeroed any persistent premium by construction.
3. Single-layer residual vs one or two sector ETFs still left stealth factor exposure (β_XLV = 0.84 on F3).
4. No explicit measurement of hyper or noisy layers → false positives in high-attention regimes (2022–23 energy shock for F2).

## Measurement layers (instrument these as continuous state variables)

1. **Cross-asset & macro factor exposure**  
   Rolling OLS vs SPY/VOO + sector ETFs + yield-curve (10y–2y, real 10y) + credit spreads.  
   Output: β vector + residual return series (lagged β, no intercept in PnL).

2. **Liquidity & volatility regime**  
   VIX/VXV term-structure, cross-sectional vol dispersion inside legs vs inside controls, ETF volume imbalance / realized spread proxies.  
   Output: regime label (stress / normal / complacency) and conditioned residual IR.

3. **Breadth & internal participation**  
   Advance-decline, high-beta/low-vol ratio, factor-rotation velocity (value–growth, small–large momentum spreads).  
   Output: participation residual; if original residual vanishes, it was rotation, not stable force.

4. **Narrative & thematic momentum**  
   Dictionary / Google-Trends / simple NLP residualized against recent price momentum.  
   Output: narrative residual; lead-lag vs price residual reveals whether story is still lagging (under-noticed window) or catching up (absorption).

## Tradable object (unchanged law)

```
r_stable,t = r_legs,t − β_{t−1}' r_controls,t
```
(Intercept used only for β estimation; never subtracted from traded PnL. Dates = intersection of all series.)

Multi-layer extension:

```
r_stable,t = r_legs,t − β_mkt' r_mkt − β_sec' r_sec − β_hyper' r_vol_or_narrative − β_noise' r_idio_proxy
```

## Fail-fast tests (direct future exploration)

See `scripts/failfast_force_taxonomy.py`. Core questions each test answers:

- Does any sub-period or regime of an existing residual still clear IR ≥ 0.40 after an extra layer?
- Do the four residual series (stable / hyper / market / noise) show systematic lead-lag structure?
- Is the apparent force just a neighbor (orthogonalized residual ≈ 0 against prior paused forces)?

## Gate discipline (still absolute)

- min_clean_ir ≥ 0.40 on the *final* multi-layer residual  
- placebo (sign-randomization or time-shuffle) < 0.15  
- |mean β| on original sector controls < 0.80  
- Fail → pause, no Option-B re-specification of the same tickets  
- Leading clocks remain veto-only  

Capital stays $0 experimental / SPYM passive until a candidate survives the full taxonomy.

## How to unearth each type

| Target type | Primary filter | Kill if… | Promotion signal |
|-------------|----------------|----------|------------------|
| Stable | Multi-layer residual + low-dispersion regime IR | Residual dies after sector+vol+breadth | IR ≥ 0.40 persists across ≥2 non-overlapping regimes |
| Hyper | High news density + high dispersion residual | Residual survives after narrative residualization | Short-horizon IR high *only* while narrative residual is elevated |
| Regular market | β loadings on major ETFs / styles | Already priced; residual IR ≈ 0 by construction | N/A (we do not trade pure market factors) |
| Noisy | High residual variance after all layers, low coherence | Coherence across legs collapses | N/A (noise is not a tradeable force) |

Neighboring-force test: after orthogonalizing a new candidate against the residual series of all paused forces, residual IR must still clear the gate. Otherwise it is a linear combination / neighbor, not independent.

