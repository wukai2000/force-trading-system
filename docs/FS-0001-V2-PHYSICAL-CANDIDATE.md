# FS-0001.v2 physical candidate

Status: **MEASUREMENT_AUDIT_REQUIRED**  
Frozen: **no**  
T5: **not activated**  
v1 monetary path: **CLOSED**

Three audits agree: MJ/tkm (IEA `ENERGY_INT_TKM`, freight trucks and trains separately) is a scientifically narrower physical object. It is **not** ready to freeze. It is **not** v1 unit cost.

## Learn

- Two-observable design only: intensity (−1, leading) → activity (+1, contemporaneous).
- Outcome tkm from OECD/ITF or Eurostat, not IEA tkm in both slots.
- Inverse (`tkm/MJ`) is the same object. Forbidden as a second stream.
- Eurostat road energy / road tkm is passenger-contaminated. Homemade FAIL.
- IEA EEI full cube is licensed; this repo previously got HTTP 403. Do not invent the panel.

## Dismiss

- Autonomous freeze
- Treating energy intensity as a synonym of currency/tkm
- Utilization / load as a frozen third observable (memo 3)
- Fuel/tkm as PASS (boundary unproven)
- ODYSSEE splice to buy pre-2000 depth
- Locking k=1 vs k=2 before the audit (memos disagree; that is lag shopping if chosen from fit)
- Occupying a second frozen slot

## Mapping break still in play

Intensity uses tkm in the denominator. Conceptual independence ≠ algebraic independence. Disclose it. If a later freeze review requires strict algebraic independence, v2 returns NO_RESULT rather than residualizing the overlap.

Until country×mode continuous IEA pairs are tabulated from the actual cube — without keeping countries because intensity falls — the stack is a design, not a dataset.

## Cube inventory (2026-09-09)

| Metric | Count |
|---|---:|
| Qualifying truck pairs | **0** |
| Qualifying train pairs | **0** |
| Both | **0** |

The licensed cube was not obtained. Highlights are a sparse index, not annual, not freight-train intensity. FILTER 2 (direction) was not applied.

A third memo reported 31/27/25 country pairs with start/end intensities. That panel is **refused**. It is not the cube. Do not load it.

IEA docs: freight-train energy is often included in passenger trains. Total-rail energy + freight tkm is incompatible.

## Observable-pair census

Do not abandon freight. Do not swap the domain because IEA returned 403.

A named census exists at [observable_pairs.yaml](../force_ideas/inventory/observable_pairs.yaml). Steel, cement, aluminium, electricity are **OPEN and unscored**. None are excellent. None are A/B. Electricity carries mix contamination. Data/comms is REJECT. Labor/water/land/compute not opened this quarter.

Rank by measurement integrity after an official extract. Attractiveness ranking is refused. This is not a new freeze and not FS-0001.v3.


