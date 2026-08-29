# Literature Map — hypothesis engines vs kill layers

Locked 2026-08-29. Academic / institutional models **generate or condition
hypotheses**. They never allocate capital and they never promote a failing
price residual. The multi-layer gate in `config/multilayer_gate.yaml` is the
only promotion path.

Firewall:

```
literature / discovery  →  frozen YAML sketch  →  pipeline.evaluate_candidate
     (hypotheses)              (not a lock)           (ruthless beta kill)
```

Capital remains $0. Force 4 tickets are **not** locked by this document.

## Original five (kept)

| # | Framework | Origin | Engine role | Operational constraint |
|---|---|---|---|---|
| 1 | Narrative Economics | Shiller (2019); State Street MediaStats | Low-attention, steady-drift themes (`z_attn` low, slope > 0). Drops viral peaks (hyper / noisy). | Veto / filter only. Cannot promote a failing residual. |
| 2 | Slow Information Diffusion | Hong & Stein (1999); PEAD | Structural lead-times in patents, CMS, legislation. | Surfaces sub-industry pairs vs absorbing sector ETFs. Tickets stay sketches until a human lock. |
| 3 | Factor Neutralization | Fama–French; MSCI Barra | Strip linear market / sector / style exposure. | **Kill layer 1.** Tradable object is `r_legs,t − β_{t−1}' r_controls,t`. |
| 4 | Political Risk (P-factor) | Baker, Bloom & Davis EPU | Policy-sheltered demand while EPU is elevated. | Hypothesis only. Must still die if it is just XLI or SPY. |
| 5 | Overfitting & False Discovery | Harvey, Liu, Zhu; López de Prado DSR / CPCV | Pre-registration + permutation. | **Kill layer.** Placebo IR < 0.15 is a hard gate. Do not loosen after F2. |

## What the original five missed

These were already implied by the taxonomy / L2–L4 instruments but were not
named as first-class simulation models. They are now.

| # | Framework | Origin | Why it was missing | Engine role | Constraint |
|---|---|---|---|---|---|
| 6 | Geopolitical Risk | Caldara & Iacoviello GPR / AI-GPR | EPU is policy-text uncertainty, not war/threat intensity. Defense sketches need both. | L4 veto clock + diagnostic residual vs ΔGPR. | If residual dies after GPR, it is a hyper overlay, not a stable force. |
| 7 | Limited Attention / Category | Barberis–Shleifer–Vishny; DellaVigna–Pollet; Da–Engelberg–Gao | Shiller is epidemic stories; attention is a *capacity* constraint. | Hypothesis: theme in a neglected category. Condition: residualize vs search/news intensity. | High-attention residual = hyper, not stable. |
| 8 | Slow-moving Capital / Inelastic Markets | Duffie (2010); Gabaix–Koijen | Explains why a residual can persist without being a new cash-flow force. | Diagnostic half-life / capacity proxy. | Persistence alone is not a force. Neighbor + placebo still required. |
| 9 | Variance Risk / Vol Term Structure | Bollerslev–Tauchen–Zhou; VIX/VIX3M | F2 died as a shock overlay. Calendar regimes are not vol regimes. | **Kill / condition layer 2** (already instrumented). | IR must hold in ≥2 non-shock regimes. Complacency-only IR is a fail. |
| 10 | Breadth / Disagreement | Chen–Hong–Stein; RSP−SPY, IWM−SPY | Single-layer residuals confuse participation with structure. | **Condition layer 3.** | If residual vanishes after breadth, it was rotation. |
| 11 | Innovation / Patent Value | Kogan–Papanikolaou–Seru–Stoffman (KPSS); Hall–Jaffe–Trajtenberg | Raw patent *counts* are not economic value. | Slow-diffusion upgrade: inflection in grants × citation/value proxy. | Count-only spikes are noisy. |
| 12 | Intermediary / Credit | He–Kelly–Manela; Gilchrist–Zakrajšek EBP | Sector OLS does not remove dealer / credit capacity. | Extra L2 control: ΔBAA, HY OAS, NFCI. | Credit-only residual is regular-market stress, not a force. |
| 13 | Spanning / Neighbor | Huberman–Kandel; Barillas–Shanken | F3 ⊥ F2 IR was 0.048. New tickets can be linear combos of paused forces. | **Kill layer 4 (neighbor).** | Neighbor IR ≥ 0.40 after orthogonalizing vs paused F1/F2/F3 residuals. |
| 14 | Publication / Crowding Decay | McLean–Pontiff | Once a story is named, sector ETFs absorb it. | Diagnostic: post-naming IR decay. | Naming clock may veto; cannot promote. |
| 15 | Multiple-testing proper | Bailey–Borwein–López de Prado DSR; combinatorial purged CV | Sign-randomization is necessary but not sufficient once many as-of dates are scanned. | Research diagnostic (deflated Sharpe / date-wise CPCV). | Does **not** replace the locked placebo < 0.15 gate. |
| 16 | Demographic demand | DellaVigna–Pollet (2007) aging-industry | F3's claim class, without recycling F3 tickets. | Hypothesis only for *new* demand-side maps. | Hard exclusion: no IHF/IHI/XHS recycle. |
| 17 | Political uncertainty (theory) | Pástor–Veronesi | EPU index ≠ priced political-uncertainty premium. | P-factor companion: elevated uncertainty + policy-sheltered cash flows. | Same kill stack as #4. |
| 18 | Style / q-factor controls | Fama–French 5; Hou–Xue–Zhang q | Sector ETFs miss value/profit/investment. | Optional extra L1 controls (research). | Unwired until Ken French series are cached. Not a ticket change. |

## Mapping onto the tug-of-war taxonomy

| Taxonomy class | Literature that *finds* it | Literature that *kills* lookalikes |
|---|---|---|
| Stable | 1, 2, 4, 7, 11, 16, 17 | 3, 5, 6, 9, 10, 12, 13, 14, 15 |
| Hyper | 1 (inverted: high z), 6 (GPR spike), 14 | 9, 5, 13 |
| Regular market | — (we do not hunt this) | 3, 9, 10, 12, 18 |
| Noisy | — | 5, 15, low coherence |

## What is still not a trading model

- IPCA / instrumented PCA (Kelly–Pruitt–Su): research-only later. Too many free parameters for $0 capital.
- Paid MediaStats / McClellan: stay on free proxies (dictionary counts, RSP−SPY, public GPR).
- Any literature hit that does not produce a residual surviving `multilayer_gate.yaml`.

## Code hooks

| Model # | Python |
|---|---|
| 1, 2, 4, 7, 11, 17 | `force_engine.literature` + `force_engine.discovery` |
| 3 | `force_engine.neutralize` / `pipeline.evaluate_candidate` |
| 5, 15 | `force_engine.evaluate.sign_placebo_ir` + `force_engine.false_discovery` |
| 6, 9, 10, 12 | `force_engine.layers` + `force_engine.clocks` |
| 13 | `force_engine.neighbor` |
| 14 | naming clock (veto-only, unwired intensity) |

See `docs/SIMULATION_RESEARCH_PLAN.md` for the work sequence.
This page does not lock Force 4.
