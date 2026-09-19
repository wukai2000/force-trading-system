# I_t contract — MTS-0001 / EP-CRUDE-2014

Frozen experiment sketch. Not a Force. Not a ticker map. Capital $0.
Promotion remains `NOT_PERMITTED`. Do not retune the 2014 discrete rule.
Do not open a new episode. Do not mutate `force_ideas/frozen/FS-0001.v1.yaml`.

Locked 2026-09-14. Companion: `docs/PATHS_AND_I_T.md`, `docs/FORCE_LAB_REPLAY.md`,
`docs/FORCE_SYSTEM_REDESIGN_v2.md`.

## Why this exists

EP-CRUDE-2014 ran a competing-mechanism cutoff rule on **as-revised** weekly EIA
plus a 5-day WPSR lag. Verdict: `NO_RESULT_MARGIN_TOO_SMALL`.

| window | persist | rule | edge |
|---|---:|---:|---:|
| 2014-07-02 … 2016-06-29 (n=27 notes) | 0.617 | 0.642 | 0.025 |
| 2011-01-05 … 2012-06-27 negative control | 0.441 | 0.441 | 0.000 |

The architecture (identity + pair + cutoff + next-state + persistence +
negative control) is kept. The missing object is **identification**, not another
domain. As-revised smoke is not identification. `identified: false` stays.

## Goal restated (2026-09-14)

Find and **define** a Force that can later be:

1. tested on historical vintages,
2. expressed as a measurable process,
3. eventually traded and scored for effect.

A 2026 live book is **off the table**. That deadline is not a research clock.

Path-C freeze (2026-09-15, one sentence): mechanism + `I_t=f(F_t)` + vintage
reconstruct + next-state vs persist; `U` is legal; tickers/IR last.

## What I_t is

`I_t` is a state available to an observer at decision time `t` from information
set `F_t` only.

```
F_t  = first-print / vintage releases available at t
I_t  = f(F_t)  ∈ {A, B, U}   or a real-valued intensity
Y_{t+h} = next physical state of the identity legs
kill if I_t uses Y_{t+h}, later revisions, prices, or tickers
```

`I_t` is not a residual IR. It is not Clock B = flow/state. It is not Δstock
called a transition. It names **which competing mechanism is winning now**.

On this identity the locked discrete rule (do not retune) is:

- **B** (lagged supply) if production ↑ and product supplied ↓ over the locked
  4-week cutoff, using only vintages in `F_t`.
- **A** if both ↓.
- **U** otherwise → persistence forecast.

Horizon stays 8 weeks. Scored series stay production, stocks, product supplied.

## What the 2026-09-12 replay was not

1. **Vintage leak.** `vintage_quality: AS_REVISED_PLUS_RELEASE_LAG`.
   Later revisions of week *s* sit inside the file used at week *t>s*.
2. **Label starvation.** 13/27 primary notes unidentified. Almost no A (2).
   A three-way label that is U half the time cannot identify a Force.
3. **Fragile edge.** Entire +0.025 is two extra stock hits. Production =
   persistence. Product supplied = persistence. Negative control edge = 0.
4. **No constructed state.** The rule classifies the current window. It does
   not emit a standing `I_t` series an observer could have written down each
   Wednesday without the outcome in hand.

## Experiment E1.I (authorized shape only)

Object = same identity, same windows, same rule, **true vintages**.

1. Replace as-revised EIA weekly with WPSR / ALFRED first-print vintages for
   the same three legs. Record release timestamps. No Baker Hughes until its
   calendar is wired. No DPR monthly (as-revised leak already dismissed).
2. At each Wednesday decision `t`, build `F_t` from prints whose release time
   is ≤ `t`. Recompute the locked {A,B,U} label. That label **is** `I_t`.
3. Forecast `Y_{t+8w}` from `I_t` exactly as the sealed rule does. Compare to
   persistence. Keep margin **0.05**. Keep the 2011 negative control.
4. Report, then stop:
   - vintage `I_t` coverage (% notes not U)
   - primary edge vs persist
   - NC edge vs persist
   - revision-gap diagnostic (as-revised label vs first-print label disagreement)

Pass shape (still cannot promote, still not a Force):

- primary edge ≥ 0.05
- NC edge < 0.05
- revision-gap not the whole primary edge
- `I_t` written as a series under `data/lab/crude/` with `F_t` hashes

Fail shape: seal MTS-0001 as `NO_RESULT` and **do not pick a new episode**.

## Addendum 2026-09-19 — fail shape fired; scope is E1.I-local

Gate 1 `FAIL`. Reconstruction `NO_RESULT`. `e1i_vintages.ok` unwritten.
The fail shape above fired on the locked NC window (5/20 cutoffs
unrecoverable). Scope is `E1I_LOCAL`. The measurement layer of the
historical architecture is observed (2014–2016 cells; listed 2011 half).
The identifying experiment on this frozen object is not constructible.
That is not an architecture kill. Do not pick a new episode. Receipt:
`docs/E1I_FAIL_SCOPE.md`.

## Explicitly refused this cycle

- Retuning cutoffs, horizon, or the A/B predicate on 2014 residuals
- Particle filters, trade-gap G(t), SEMI/WSTS, grid 2021–24, AI capex
- Opening the financial sidecar
- Treating a numeric intensity as a silent substitute for the locked rule
- A second frozen Force slot
- Force 4 / FS-0001.v2 / Item-106 / EIA existence check as a substitute for `I_t`

## Optional later version (not this experiment)

A real-valued intensity `I_t = z_t(Δprod) − z_t(Δsupplied)` with expanding
history inside `F_t` is a **new YAML version**, not a retune. It may only be
opened after E1.I is sealed pass or fail. It cannot share a frozen slot with
FS-0001.v1.

## Mapping to redesign v2

| lab step | this contract |
|---|---|
| E1 historical reconstruction without returns | E1.I vintages |
| E2 blind reconstruction | locked until E1.I sealed |
| E3 competing-force test | the A vs B label *is* the test; U is not a winner |
| E4 market-efficiency challenge | sidecar stays sealed |
| E5 financial transmission | not this year |

## Success for the desk

We can point to a file and say: this is `I_t`, this is `F_t`, this is the
next-state score, this is why it is or is not identification. That is the
prerequisite for ever defining a Force that could later be traded.
