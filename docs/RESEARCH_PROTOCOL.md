# Research protocol — locked 2026-09-01

A Force is a **pre-specified economic mechanism** whose independently
specified manifestations exhibit consistent, **leading** relationships
across sufficiently independent observations, and whose price expression
survives appropriate null and concentration tests.

**Residualization is a falsification layer, not evidence of existence.**

F1, F2, and F3 are **negative-control objects**. They are not candidates
for revival. Force 4 remains **WAIT**. Capital **$0**. Trump Account = SPYM.

This document is architectural. It does not allocate capital and it does
not scan ITA/XAR/PPA/XLI.

---

## Five immutable principles

1. Residualization is falsification, not identification.
2. Statistical significance and concentration are independent gates.
   Neither rescues the other.
3. Null tests do not validate an economic mechanism.
4. Replication requires economic independence (geography / instrument /
   manifestation / market expression), not correlated US securities.
5. Evidence may veto a Force. No clock, statistic, narrative, or
   leftover IR may promote one.

---

## What the tradable object is

Always-on OOS residual:

```
r_t = r_legs,t − β_{t−1}' r_controls,t
```

There is **no** separate timing signal `s_t`. Sign-randomization is
applied to `r_t`, not to `IR(s, r)`. Inventing `s_t` from the same
equities is the MAGS move at the statistic layer.

---

## Phase plan

### Phase A — statistical infrastructure (this package)

Two **separate** null families plus two **separate** concentration
stats. They cannot promote. They cannot loosen `multilayer_gate.yaml`.

**Null A — residual sign-null.** Flip signs of `r_t`. Denominator
(magnitude path) is invariant; only the signed mean moves. Report the
percentile of observed IR inside that null, plus one-sided and
two-sided empirical p. Draw count is a computational sample (default
5k–10k), not proof of rigor.

**Null B — block bootstrap.** Blocks {5, 21, 60}. Mean **and** std
may move. Do **not** average block lengths.

| Result | Interpretation |
|---|---|
| 5, 21, and 60 all unusual | more robust serial-dependence evidence |
| 5 fails, 60 passes | regime / cluster dependence |
| all fail | weak statistical evidence |
| 60 looks great, concentration fails | **still kill** |

A 60-day block that preserves 2022 is **not** validation of F2.

**Concentration A — IR persistence.** Locked: `p_IR / |IR| ≥ 0.40` is a
kill (`force_engine.evaluate`). Sign-flipped copies keeping the IR.

**Concentration B — P&L mass.** Share of `∑|r|` in the top 5% and top 10%
of |r| days. Not interchangeable with A. Do not fuse into one score.

**Null 1 — regime-label permutation (2026-09-02).** Residual path is
fixed. Shuffle the locked 2026-08-27 labels `{complacency, normal, stress}`.
Occupancy mode keeps label counts. Run-length mode shuffles dwell blocks.
Report whether `IR_complacency − IR_stress` is unusual. Draw count is a
computational sample. **Cannot promote.** Calendar windows
`{2017–19, 2020–21, 2024–26}` remain the locked REGIME_FAIL partitions
because they are exogenous. L2 labels are conditioning, not identification.

HMM / GMM hidden states, hysteresis as a live classifier, and any
`position_scale` / `max_leverage` / `active_strategies` map are **refused**.
Those objects are a timing signal `s_t`. The tradable object stays always-on
`r_t`. Dwell and hysteresis are reported as **sensitivity** of the locked
labels, never as a replacement classifier.

**Leading observables (2026-09-03).** `config/leading_observables.yaml` is a
T2 library. FRED-backed physical / labor / credit series may **veto** a
passing residual once cached. NLP, satellite, scrapes are **refused**.
`IR(s, r)` against this catalog is refused. See `docs/LEADING_OBSERVABLES.md`.

**FORCE_PROTOCOL_v1.0 (2026-09-04).** Canonical research output is an
`EvidenceRecord` (`force_engine/evidence.py`): Evidence / Veto / Promotion
are three objects. Promotion is always `NOT_PERMITTED` from code. Null B
has no pass/fail. Conc A stays the kill. F1/F2/F3 are regression fixtures
(`config/negative_controls.yaml`). A quarter with no leftover is
`NO_RESULT` — a success. Blind-candidate (P3) stays queued until a
genuine leftover exists. Do not invent one. See `docs/EVIDENCE_RECORD.md`.

**Idea Observatory (2026-09-04).** `force_ideas/` is the Explorer and
Gatekeeper. It does not import the Prosecutor. Flow: seed → independence
screen → T0–T4 freeze → T5 instruments → EvidenceRecord → Case Against.
Maximum 8 seeds, no minimum. T4 is mandatory. Cousins of F1–F4 are
rejected at the door. See `docs/IDEA_OBSERVATORY.md`.


### Phase B — validate the validator (this package)


Run Phase A against F1 / F2 / F3 as `research_role: negative_control`.

Desired result is **not** “F2 looks better.” Desired result:

> the methodology exposes why these objects must not be promoted.

If the new reports say **F2 → PASS**, distrust the framework.
If they say **FAIL** for the reasons already known (concentration,
2022–23 cluster, last-60 collapse), the validator is discriminating.

### Phase C — freeze protocol for the NEXT leftover

T0–T4 is a **refuse-guard** in this package (`force_engine/freeze.py`).
T5+ (names → residual → Null A/B → paper) stays queued until a genuinely
new leftover exists. Do **not** use Force 4 as that leftover.

```
T0 hypothesis
T1 economic mechanism
T2 observables (at least one leading)
T3 predicted sign on each observable
T4 independence dimensions (≥2 of geography / instrument / manifestation / market_expression)
   → freeze_complete (computed, not a YAML flag)
T5 names/instruments (attach_instruments)     # queued until a leftover
T6 ticket frozen, still scannable=false
T7 prices
T8 residualization
T9 Null A / Conc A/B / Null B
T10 neighbor vs paused F1/F2/F3
T11 mechanism veto (absent leading observable → KILL; present → no promotion)
T12 paper → wait
```

No failed stage may be rescued by a later stage.
`evaluate_candidate` refuses unknown force_ids without a complete freeze
and T5 instruments. F1/F2/F3 are grandfathered as negative controls only.

Mechanism-absence kill is **not** implemented as “missing transformer-queue
file → KILL every candidate.” Observables must be named at T2; the kill
runs later when that series is actually read. GPR z≥2 remains a veto of a
passing residual and still cannot promote.

Do **not** pre-register a 2026 F2 cousin map (CEG/NEE/GEV/HUBB/EME).
That is Option-B. CEG on the panel sieve is a hint, not a manifestation.

PCA of cousin residuals is a **spanning diagnostic**, not identification.
Cross-manifestation prediction (leading non-price A,B,C → D,E OOS) is
the replication shape for a *future* hypothesis, not an F2 study.

---

## Failure vocabulary (diagnostic labels)

These are research-memory labels. They are not promotion verdicts.

| Label | Meaning |
|---|---|
| `STATISTICAL_FAIL` | observed IR is not unusual under Null A |
| `DEPENDENCE_FAIL` | only long blocks make the IR look unusual |
| `CONCENTRATION_FAIL` | IR-persistence and/or P&L-mass kill |
| `SPANNING_FAIL` | neighbor leftover is paused F1/F2/F3 |
| `MECHANISM_FAIL` | frozen leading observables did not move as predicted (Phase C) |
| `REPLICATION_FAIL` | no economically independent manifestation (Phase C) |
| `REGIME_FAIL` | lives in one shock window |

PASS on statistics is **paper**, then **wait**, never capital.

---

## F2 audit questions (negative control, not revival)

1. Sign-null: where does observed IR sit in the signed-IR distribution?
2. Dependence: 5 / 21 / 60 day block bootstrap — does the conclusion move?
3. Concentration: IR-persistence and P&L-mass.
4. Mechanism: queued until observables are frozen *for a new hypothesis*.
   Do not invent F2 leads after the fact.
5. Independence: queued. Another US equity cousin is not an observation.

Answers: yes / no / inconclusive. No capital. No un-pause.

---

## Explicitly refused

- Force 4 because F1–F3 died
- Treating 0.725 or 0.593 as almost-alpha
- 18-row literature table as a discovery engine
- Score deltas of 0.1 as evidence
- Live-tape sentences as trades
- Cousin-basket PCA as identification
- `max_story_changes: 0` as a test
- `IR(s_t, r_t)` timing null without a frozen non-price `s_t`
- PLACEBO_RELAX / SKIP_PLACEBO / RELAX_GATE
- Option-B recycle of MAGS/SMH/SPMO, VST/ETN/PWR, IHF/IHI/XHS
- HMM / GMM hidden states as the L2 classifier
- `REGIME_CONTROL_MAP` (`position_scale`, `max_leverage`, `active_strategies`)
- `IR(s_t, r_t)` with `s_t` = L2 regime (including hysteresis-smoothed labels)
- DSR or CPCV as promotion kills (research logging only)
- 18 academic frameworks as a ticket factory (already: literature firewall)
- Extra-neutralization described as vol/credit *scaling* — L2 residualizes, it does not size
- Treating F2 full-sample IR 0.118 as the attractive object (that is walk-forward collapse; the attractive object is OOS hedged 0.593, still CONCENTRATION_FAIL)
- Force 4 PIT IR 0.389–0.573 / neighbor 0.28 as measured facts
- Fama-French / Barra as default L1 (different object; diagnostic extra-neutralize only on a frozen leftover)
- `IR(s_t, r_t)` with `s` from `config/leading_observables.yaml` (catalog is T2/veto, not a timing overlay)
- Satellite / LinkedIn / WARN-NLP / 10-K tone / ADS-B as wired clocks (no corpus; theater)
- Treating a GDP/NFP nowcast as a Force
- Auto-promotion from an EvidenceRecord
- Inventing a leftover to “prove” the evaluator (P3 stays queued)
- Fusing Null B into pass/fail
- Mechanism evidence rescuing a statistical fail



---

## Commands

```
PYTHONPATH=. python scripts/test_neutralizer.py
PYTHONPATH=. python scripts/test_discovery_sieve.py
PYTHONPATH=. python scripts/test_null_engine.py
PYTHONPATH=. python scripts/test_freeze.py
PYTHONPATH=. python scripts/run_negative_control_audit.py
PYTHONPATH=. python scripts/run_regime_label_null.py
PYTHONPATH=. python scripts/validate_hypothesis_freeze.py
PYTHONPATH=. python scripts/test_leading_observables.py
PYTHONPATH=. python scripts/run_leading_observables.py
PYTHONPATH=. python scripts/test_negative_control_contract.py
PYTHONPATH=. python scripts/test_evidence_record.py
PYTHONPATH=. python scripts/run_evidence_record.py
PYTHONPATH=. python scripts/test_idea_registry.py
PYTHONPATH=. python scripts/run_idea_registry.py



```

`run_negative_control_audit.py` writes `data/meta/negative_control_audit.json`.
It cannot promote. It cannot scan Force 4. Draw counts (`--n-sign`, `--n-block`)
are a computational sample, not proof of rigor.

Implemented 2026-09-01 in `force_engine/false_discovery.py`:

- Null A: `sign_null_distribution` (signed-IR percentile + empirical p)
- Null B: `block_bootstrap_distribution` at {5, 21, 60} (not averaged)
- Null 1: `regime_label_permutation` (occupancy + run-length; cannot promote)
- Concentration A/B: `concentration_report` (IR-persistence kill stays locked; P&L mass is separate)
- Labels: `STATISTICAL_FAIL`, `CONCENTRATION_FAIL`, `DEPENDENCE_FAIL`, `REGIME_FAIL`
- Q4 mechanism / Q5 independence stay **queued**
- Dwell / hysteresis: `regime_dwell_report`, `hysteresis_smooth` — sensitivity only


### Phase B measured (2026-09-01, cannot promote)

`PYTHONPATH=. python scripts/run_negative_control_audit.py`
n_sign=5000, n_block=2000. Computational sample.

| object | residual | n | IR | Null A p1 | perc | Conc A persist | Conc B top5 | labels |
|---|---|---|---|---|---|---|---|---|
| f1 | factor_clean_resid | 1606 | 0.003 | 0.50 | 50 | 105.5 | 0.22 | STATISTICAL_FAIL, CONCENTRATION_FAIL |
| f2 | walkforward resid_gross | 2437 | 0.156 | 0.31 | 69 | 1.43 | 0.22 | STATISTICAL_FAIL, CONCENTRATION_FAIL |
| **f2_oos_hedged** | close lagged-β (the attractive one) | 2436 | **0.593** | **0.032** | 97 | **0.435** | 0.22 | **CONCENTRATION_FAIL** |
| f2_resid_l2 | L2 aligned | 2274 | 0.364 | 0.13 | 87 | 0.63 | 0.22 | STATISTICAL_FAIL, CONCENTRATION_FAIL |
| f2_resid_ols | Phase A resid_ols | 2438 | −0.262 | 0.20 | 20 | 0.97 | 0.21 | STATISTICAL_FAIL, CONCENTRATION_FAIL |
| f3 | resid_oos_hedged | 3686 | 0.131 | 0.31 | 69 | 1.65 | 0.19 | STATISTICAL_FAIL, CONCENTRATION_FAIL |

`distrust_framework`: **false**. The attractive F2 object (IR 0.593, Null A unusual) is still killed by locked IR-persistence 43.5%. Null B on that object does **not** destroy it (≈78% of 5/21/60 bootstraps still IR≥0.40; p5>0) — that is the concentration/regime warning, not validation.

Q4/Q5 remain queued. Force 4 not scanned. Capital $0.

### Null 1 measured (2026-09-02, cannot promote)

`PYTHONPATH=. python scripts/run_regime_label_null.py`
n=2000. Computational sample. Contrast = IR_complacency − IR_stress on locked 2026-08-27 labels.

| object | n | IR_c | IR_s | delta | occ p1 | run p1 | frac 1-day runs |
|---|---|---|---|---|---|---|---|
| f2_l1 (walkforward) | 2425 | 0.54 | −0.13 | 0.66 | 0.19 | 0.14 | 0.36 |
| f2_l2 | 2274 | 0.41 | 0.96 | −0.55 | 0.27 | 0.19 | 0.35 |
| **f2_oos_hedged** | 2424 | **1.47** | 0.38 | 1.09 | **0.083** | 0.063 | 0.36 |
| f3_l1 | 3686 | 0.64 | −0.50 | 1.14 | **0.037** | **0.022** | 0.38 |
| f3_l2 | 3505 | 0.37 | 0.01 | 0.36 | 0.30 | 0.26 | 0.37 |

Reading: F2's calm-vs-stress split is **not unusual** under occupancy (p=0.19, attractive object p=0.083). F3 L1 **is** a complacency-beta (p=0.037) — already FAIL_GATE, not a timing overlay to harvest. Locked labels chatter (36% of runs are 1-day; median dwell 2). Hysteresis min_dwell=2 **flips** F2 OOS ranking (complacency 1.47 → 0.46, stress 0.38 → 0.76). Do not feed labels to `position_scale`.

T0–T4 freeze guard implemented 2026-09-01 afternoon in `force_engine/freeze.py`.

Template: `config/hypotheses/_TEMPLATE.yaml` (incomplete by design).
`evaluate_candidate` refuses unknown force_ids without freeze + T5.
Discovery cannot name non-WAIT legs before freeze. Discovery cannot
write `scannable: true`. Mechanism-absence is still not a ClockBus kill
on missing files.


