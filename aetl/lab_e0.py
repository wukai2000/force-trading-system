"""E0 integrity lab. P2 order-2 plant, P1 Markov-1 plant, IID. No Force."""
from __future__ import annotations

import math
import random
from collections import Counter, defaultdict

from aetl.governor import Candidate, Governor, GovernorError
from aetl.ledger import SearchLedger, spec_hash

ALPH = "ABC"


def iid_tokens(n: int, seed: int) -> list[str]:
    rng = random.Random(seed)
    return [rng.choice(ALPH) for _ in range(n)]


def planted_markov1(n: int, seed: int, noise: float = 0.12) -> list[str]:
    rng = random.Random(seed)
    nxt = {"A": "B", "B": "C", "C": "A"}
    s = rng.choice(ALPH)
    out = [s]
    for _ in range(n - 1):
        s = rng.choice(ALPH) if rng.random() < noise else nxt[s]
        out.append(s)
    return out


def planted_order2(n: int, seed: int) -> list[str]:
    rng = random.Random(seed)
    out: list[str] = []
    while len(out) < n:
        if rng.random() < 0.32 and len(out) + 3 <= n:
            out.extend(["A", "B", "C"])
        else:
            out.append(rng.choice(ALPH))
    return out[:n]


def nll_marginal(pref, hold) -> float:
    marg = Counter(pref)
    tot = sum(marg.values()) or 1
    acc = 0.0
    for s in hold:
        p = (marg[s] / tot) if marg[s] else 1e-12
        acc -= math.log(max(p, 1e-12))
    return acc


def nll_markov1(pref, hold) -> float:
    trans = defaultdict(Counter)
    marg = Counter(pref)
    for a, b in zip(pref, pref[1:]):
        trans[a][b] += 1
    tot = sum(marg.values()) or 1
    acc = 0.0
    for i, s in enumerate(hold):
        if i == 0:
            p = marg[s] / tot if marg[s] else 1e-12
        else:
            row = trans[hold[i - 1]]
            den = sum(row.values())
            p = (row[s] + 1e-12) / (den + 1e-12 * 3) if den else 1e-12
        acc -= math.log(max(p, 1e-12))
    return acc


def nll_order2(pref, hold) -> float:
    t2 = defaultdict(Counter)
    trans = defaultdict(Counter)
    marg = Counter(pref)
    for a, b, c in zip(pref, pref[1:], pref[2:]):
        t2[(a, b)][c] += 1
    for a, b in zip(pref, pref[1:]):
        trans[a][b] += 1
    tot = sum(marg.values()) or 1
    acc = 0.0
    for i, s in enumerate(hold):
        if i == 0:
            p = marg[s] / tot if marg[s] else 1e-12
        elif i == 1:
            row = trans[hold[0]]
            den = sum(row.values())
            p = (row[s] + 1e-12) / (den + 1e-12 * 3) if den else 1e-12
        else:
            row = t2[(hold[i - 2], hold[i - 1])]
            den = sum(row.values())
            if den == 0:
                row1 = trans[hold[i - 1]]
                den1 = sum(row1.values())
                p = (row1[s] + 1e-12) / (den1 + 1e-12 * 3) if den1 else 1e-12
            else:
                p = (row[s] + 1e-12) / (den + 1e-12 * 3)
        acc -= math.log(max(p, 1e-12))
    return acc


def explore_models(seq, ledger: SearchLedger, world: str):
    mid = int(0.65 * len(seq))
    pref, hold = seq[:mid], seq[mid:]
    cid = f"{world}-nested"
    rep = {"alphabet": list(ALPH), "models": ["M0", "M1", "M2"]}
    gram = {"family": "nested_markov"}
    c = Candidate(candidate_id=cid, representation=rep, grammar=gram, claim_class="predictive_grammar", lineage=[])
    c.status = "DISCOVERED"
    ledger.append(
        actor="EXPLORER", action="PROPOSE", candidate_id=cid, partition="DISCOVER",
        info_set_id=f"{world}:prefix", representation_hash=spec_hash(rep),
        grammar_hash=spec_hash(gram), search_burden_note="nested M0/M1/M2", outcome_summary="DISCOVERED",
    )
    return c, pref, hold


def certify_nested(cand: Candidate, pref, hold, gov: Governor) -> dict:
    gov.touch_cert(cand.candidate_id)
    m0 = nll_marginal(pref, hold)
    m1 = nll_markov1(pref, hold)
    m2 = nll_order2(pref, hold)
    d21 = m2 - m1
    d10 = m1 - m0
    if d21 < -6.0:
        gov.set_status(cand, "STATISTICALLY_SUPPORTED", "CERTIFIER")
        status = "STATISTICALLY_SUPPORTED"
    elif d10 < -6.0:
        gov.set_status(cand, "UNRESOLVED", "CERTIFIER")
        status = "MARKOV1_ONLY"
    else:
        gov.set_status(cand, "REFUTED", "CERTIFIER")
        status = "REFUTED"
    return {"status": status, "d_m2_m1": d21, "d_m1_m0": d10}


def run_kind(kind: str, n_worlds: int = 20, n: int = 900) -> dict:
    ledger = SearchLedger()
    gov = Governor(ledger)
    try:
        gov.check_lesson("tighten threshold from 0.73 to 0.68")
        chasing_blocked = False
    except GovernorError:
        chasing_blocked = True
    tallies = Counter()
    lifts = []
    for w in range(n_worlds):
        if kind == "P2":
            seq = planted_order2(n, seed=20 + w)
        elif kind == "P1":
            seq = planted_markov1(n, seed=40 + w)
        else:
            seq = iid_tokens(n, seed=80 + w)
        cand, pref, hold = explore_models(seq, ledger, f"{kind}-{w}")
        ev = certify_nested(cand, pref, hold, gov)
        tallies[ev["status"]] += 1
        lifts.append(ev)
    return {
        "kind": kind,
        "n_worlds": n_worlds,
        "tallies": dict(tallies),
        "mean_d_m2_m1": sum(x["d_m2_m1"] for x in lifts) / n_worlds,
        "mean_d_m1_m0": sum(x["d_m1_m0"] for x in lifts) / n_worlds,
        "chasing_lesson_blocked": chasing_blocked,
        "ledger_burden": ledger.burden(),
    }


def run() -> dict:
    p2 = run_kind("P2")
    p1 = run_kind("P1")
    iid = run_kind("IID")
    return {
        "id": "AETL-E0",
        "phase": "synthetic_integrity",
        "capital": 0,
        "force_language": "OFF",
        "P2_order2_plant": p2,
        "P1_markov1_plant": p1,
        "IID": iid,
        "pass_recover_order2": p2["tallies"].get("STATISTICALLY_SUPPORTED", 0) >= 15,
        "pass_refuse_iid": iid["tallies"].get("STATISTICALLY_SUPPORTED", 0) == 0,
        "pass_no_extra_on_markov1": p1["tallies"].get("STATISTICALLY_SUPPORTED", 0) == 0,
        "historical_experiment_open": False,
        "label": "LAB_ONLY",
        "note": "M2 vs M1 locked margin -6 nats on holdout. Debt is the ledger, not a scalar.",
    }
