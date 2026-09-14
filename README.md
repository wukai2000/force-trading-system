# Force Trading System

Research lab for defining **Forces**: persistent economic pressures with a
temporal fingerprint that can be tested on historical vintages and, later,
measured in markets.

**2026-09-14:** a live book in 2026 is **off the table**. The goal is definition
+ historical testability, not this-year P&L.

**Current phase**: F1 falsified, F2 paused (placebo + Conc A), F3 FAIL_GATE,
F4 wait. FS-0001.v1 frozen / T5 `NO_RESULT`. MTS-0001 frozen. `I_t` **not
constructed**. EP-CRUDE-2014 as-revised smoke = `NO_RESULT_MARGIN_TOO_SMALL`.
**Capital**: $0 experimental. Trump Account stays SPYM (household).
**Protocol:** residualization is falsification, not identification. See
`docs/RESEARCH_PROTOCOL.md`, `docs/I_T_CONTRACT.md`, `docs/PATHS_AND_I_T.md`.


## Architecture (four core components)

```
force_learning/          # observation → claims → laws; experiments
force_engine/            # neutralization BEFORE scoring
  ├── pipeline.py        # only evaluation entry
  ├── neutralize.py      # OOS hedged residual spread (required)
  ├── evaluate.py        # gate; concentration placebo on sign-randomized |IR|
  ├── sieve.py           # leftover vs market + paused F1/F2/F3 (finder)
  ├── literature.py      # academic models as hypothesis simulators (no ticket map)
  ├── discovery.py       # writes YAML sketches; cannot promote
  ├── neighbor.py        # spanning test vs paused F1/F2/F3 (naive-day align)
  ├── false_discovery.py # Null A/B + Null 1 (label permutation); time_shuffle/DSR legacy

  ├── freeze.py          # T0–T4 provenance; evaluate refused until complete
  ├── leading_observables.py  # T2 FRED catalog; veto-only; IR(s,r) refused
  ├── evidence.py        # EvidenceRecord (evidence / veto / promotion=NOT_PERMITTED)
  ├── protocol.py        # FORCE_PROTOCOL_v1.0 hashes
  ├── clocks.py          # 4 clocks + L4 GPR veto-only (real Iacoviello files)
force_ideas/             # Explorer + Gatekeeper; empty registry is success
  ├── registry.yaml      # max 8 seeds, no min; F1–F4 neighborhoods banned
  ├── screen.py          # independence screen; does not import evaluate
  ├── desk.yaml          # operational overlay (not a mutation of frozen YAML)

  ├── layers.py          # L2 vol/credit, L3 breadth
  ├── loader.py          # config/force*.yaml
  └── engine.py          # suggestions only from neutralized panels
trading_engine/          # policies; unused until a Force is paper-authorized
trading_interface/       # python_sim default
```

**Meta-rule (2026-08-24):** if prices are ever scored, the object is the residual
spread (long legs, short β-weighted controls). Long-only theme ETFs are how
F1/F2 failed. See `docs/META_LEARNING.md`.

**Literature firewall (2026-08-29):** academic models generate hypotheses; the
multi-layer gate kills disguised beta. See `docs/LITERATURE_MAP.md`.

**Sieve (2026-08-31):** do not start from a 3-name ETF story. See
`docs/DISCOVERY_SIEVE.md`.

**Research protocol (2026-09-01, Null 1 2026-09-02):** a Force is a pre-specified
economic mechanism. Null A/B/1 cannot promote. F1–F3 are negative controls.
New leftovers need T0–T4 freeze before tickers. Force 4 WAIT.

**Lab v2 (2026-09-12) + I_t (2026-09-14):** a Force is a pressure with a
fingerprint, not a residual IR. E1 is open. E2–E5 locked. Next object is
vintage `I_t` on EP-CRUDE-2014, not a new episode.


## Force registry
1. AI Infra / Memory — **falsified / paused** (IR 0.003)
2. Energy × AI power — **paused** (placebo 0.325; Conc A fail; not funded)
3. Longevity / healthspan demand — **FAIL_GATE** (IHF+IHI+XHS vs XLV+XBI)
4. Defense / sovereign capacity — **sketch only, wait** (ITA+XAR+PPA vs XLI+SPY)

Idea Observatory: **FS-0001** demand expansion after cost collapse — T0–T4
frozen, tickers empty, T5 NO_RESULT, cannot promote.
Measurement freeze: **MTS-0001** — `I_t` not constructed.


## Quick start

```
PYTHONPATH=. python scripts/test_neutralizer.py
PYTHONPATH=. python scripts/test_discovery_sieve.py
PYTHONPATH=. python scripts/test_null_engine.py
PYTHONPATH=. python scripts/test_freeze.py
PYTHONPATH=. python scripts/run_negative_control_audit.py
PYTHONPATH=. python scripts/run_regime_label_null.py
PYTHONPATH=. python scripts/validate_hypothesis_freeze.py
PYTHONPATH=. python scripts/test_leading_observables.py
PYTHONPATH=. python scripts/test_negative_control_contract.py
PYTHONPATH=. python scripts/test_evidence_record.py
PYTHONPATH=. python scripts/run_evidence_record.py
PYTHONPATH=. python scripts/test_idea_registry.py
PYTHONPATH=. python scripts/run_idea_registry.py
PYTHONPATH=. python scripts/run_daily_research.py --skip-fetch --skip-nulls
PYTHONPATH=. python scripts/run_leading_observables.py
PYTHONPATH=. python scripts/run_literature_hypothesis_sim.py
PYTHONPATH=. python scripts/failfast_force_taxonomy.py
```

Honest PIT evaluate (cached prices; research only; close, not open):

```
PYTHONPATH=. python scripts/pit_evaluate.py --spec config/force2.yaml --as-of 2022-06-01
```

Do not run `scripts/phase_a_force3.py` until the Force 3 lock in `config/force3.yaml` is acknowledged (`FORCE3_LOCK_ACK=1`).
Do not scan Force 4. Silent default is wait. `historical_point_in_time_sim.py` refuses ITA/XAR/PPA unless `--research-wait-sketch`.
Do not treat `scripts/run_crude_replay.py` as identification. See `docs/I_T_CONTRACT.md`.

## Post-F3 status (2026-08-25)

All Phase-A forces paused (F1 falsified, F2 soft-fail then placebo kill, F3 FAIL_GATE stealth XLV).
See `docs/FORCE_TAXONOMY.md` and `docs/META_LEARNING.md`.
Fail-fast diagnostics: `PYTHONPATH=. python scripts/failfast_force_taxonomy.py`
Capital $0 / SPYM only. No Option-B.
