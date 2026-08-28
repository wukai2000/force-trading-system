# L2-REGIME experiment — locked 2026-08-27

Live tape is a **complacency** window (VIX 15.45, VIX3M 18.21, term 0.85 contango, HY OAS 2.70, BAA10Y 1.62). Ideal to test whether paused residuals behave like a *stable* force when hyper/stress is off.

## Locked multi-layer gate (do not move)

| Rule | Number |
|------|--------|
| Multi-layer residual IR | ≥ 0.40 |
| IR in non-shock calendar regimes | ≥ 0.35 in **≥ 2** of {2017–19, 2020–21, 2024–26} |
| Placebo (sign-randomization) IR | < 0.15 |
| \|β\| on original sector controls | < 0.80 |
| Neighbor IR vs paused F1/F2/F3 residuals | ≥ 0.40 |
| Clocks | veto-only |

Fail → stay paused, no Option-B, capital $0.

## What each layer is

**L2 vol/credit (this experiment)**  
State variables: VIX, VIX3M (FRED VXVCLS), VIX/VIX3M term, T10Y2Y, DFII10, BAA10Y (long credit), HY OAS (live tape), NFCI.  
Regimes: stress if VIX≥20 or backwardation or BAA percentile≥80; complacency if VIX<16 and contango and credit not tight-stressed.  
Tradable extra-neutralization: lagged-β residual of the force residual on (ΔVIX, ΔBAA, Δcurve). Intercept not in PnL.

**L3 breadth**  
RSP−SPY (equal-weight vs cap-weight) and IWM−SPY (small vs large). Optional extra layer after L2.

**L4 AI-GPR**  
Stub. Unwired. Cannot promote.

## Results (existing residuals only)

### Force 2 (engine-corrected OOS residual vs XLU+QQQ)

| Object | IR | Notes |
|--------|----|-------|
| L1 (sector residual) | **0.524** | matches walk-forward 0.52 |
| L2 (extra-neutralized vs vol/credit deltas) | **0.725** | IR *rose* — vol/credit was a drag, not the source |
| L2+L3 | 0.623 | breadth takes some but not all |
| L2 placebo | **0.325** | **FAIL** (≥ 0.15) |
| L1 complacency / stress | 0.91 / 0.24 | historically stronger when calm |
| L2 2017–19 / 20–21 / 24–26 | 0.47 / 0.75 / 0.65 | all ≥ 0.35 |
| Last 60 sessions L2 IR | **−1.05** | live complacency tape is *not* paying F2 right now |

**Verdict: FAIL_GATE on placebo.** Soft observation: L2 made F2 look *more* stable across calendar regimes, but sign-randomization still prints 0.32 — the path is too concentrated in a handful of signed days to treat as a general stable force. Last-60 IR is negative. Stay paused.

### Force 3 (OOS residual vs XLV+XBI)

| Object | IR |
|--------|----|
| L1 | 0.131 |
| L2 | 0.114 |
| L2+L3 | 0.108 |
| Neighbor F3 ⊥ F2 | 0.048 |
| L1 complacency / stress | 0.64 / −0.50 |

**Verdict: FAIL_GATE** (IR 0.114 < 0.40; only 1 non-shock regime ≥ 0.35). Longevity residual is a complacency-beta, not a demand-side stable force. Dies in stress. Almost fully absorbed by the F2 neighbor test.

## How to use this on past / future forces

1. Every candidate must publish L1 (sector residual) **and** L2 (vol/credit extra residual) IRs.  
2. Condition both on `{complacency, normal, stress}` and on the four calendar windows.  
3. A “stable” claim requires L2 IR ≥ 0.40 **and** ≥2 non-shock windows ≥ 0.35 **and** placebo < 0.15.  
4. If L2 IR collapses vs L1, the candidate was a hyper/market vol-credit trade.  
5. If L2 IR rises but placebo fails (F2 this cycle), the path is concentrated — treat as un-proven.  
6. Neighbor-orthogonalize against every paused residual before naming a new force.  
7. Live-tape class is a *timing* filter only after a force already passes the gate. Today is complacency; F2 last-60 L2 IR is negative, so even a passing force would be vetoed by current tape if we had a live policy.

Capital $0. Trump Account = SPYM. No un-pause.
