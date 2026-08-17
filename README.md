# Force Trading System

Unique force-based trading system built around persistent, under-noticed structural forces.

**Current phase**: Pure Python simulator + signature discovery.  
**Capital**: Experimental capital risk-tolerant; Trump Account stays passive in SPYM.

## Architecture (four core components)

```
force_learning/          # Learns & improves forces from Grok discussions + experiments
  └── (formulates forces + signatures, feeds force_engine)

force_engine/            # Runtime force scoring
  ├── base.py
  ├── signatures.py
  └── engine.py          # input + signatures → ForceSuggestions

trading_engine/          # Decision layer
  ├── policies.py        # full_autonomy | require_approval | timed_window
  ├── portfolio.py
  └── engine.py          # force suggestions + portfolio → TradeProposals under policy

trading_interface/       # Swappable execution backends
  ├── base.py            # common interface
  ├── python_sim/        # pure Python simulator (current default)
  ├── ibkr_paper/        # Interactive Brokers paper (future)
  └── robinhood_agentic/ # Robinhood Agentic account (future)
```

### 1. force-learning
- Ingests Grok discussions / observations
- Runs experiments (historical tests, residualization)
- Formulates or updates forces and their signatures
- Continuously improves and feeds the force-engine
- Observation → claims → laws cycle lives here

### 2. force-engine
- Takes market/context input + registered forces + signatures
- Produces scored ForceSuggestions (intensity, confidence, rationale)

### 3. trading-engine
- Takes force suggestions + current portfolio
- Emits TradeProposals under one of three policies:
  | Policy              | Behavior |
  |---------------------|----------|
  | `full_autonomy`     | Execute without human |
  | `require_approval`  | Every proposal needs explicit human approval |
  | `timed_window`      | Human has a time window; after timeout → go-ahead or no-go |

### 4. trading-interface (swappable)
- Abstract interface so the same trading-engine can target:
  - Pure Python simulation (current)
  - IBKR paper account
  - Robinhood Agentic trading account
- Only the interface implementation changes; engines stay the same

## Force Candidates (order locked)
1. **US Structural Advantages** (USD + Technology + Military)
2. **Energy × AI Computation/Communication Synergy**
3. **Longevity / Health Desire**

## Quick start (local)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m force_engine.engine --demo
python -m trading_engine.engine --policy require_approval --demo
```

## Status
- Bare-minimum skeleton only. No live capital.
- Default interface = pure Python simulation.
- Expand as signatures, learning loop, and real interfaces mature.
