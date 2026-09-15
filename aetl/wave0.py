"""Wave 0 — SYN-G1 / SYN-N1 / SYN-A1. Architecture unchanged. Force off."""
from __future__ import annotations

import math
import random
from collections import Counter, defaultdict

from aetl.governor import Candidate, Governor, GovernorError
from aetl.ledger import SearchLedger, spec_hash

ALPH = "ABC"


def g1_planted(n: int, seed: int) -> list[str]:
    rng = random.Random(seed)
    out: list[str] = []
    while len(out) < n:
        if rng.random() < 0.32 and len(out) + 3 <= n:
            out.extend(["A", "B", "C"])
        else:
            out.append(rng.choice(ALPH))
    return out[:n]


def n1_dependent(n: int, seed: int) -> list[str]:
    rng = random.Random(seed)
    x = 0.0
    xs = []
    for t in range(n):
        season = 1.4 * math.sin(2 * math.pi * t / 12.0)
        shift = 2.5 if t >= n // 2 else 0.0
        x = 0.7 * x + season + shift + rng.gauss(0.0, 1.0)
        xs.append(x)
    seq = []
    win = 40
    for i, v in enumerate(xs):
        if i < win:
            seq.append("B")
            continue
        past = xs[i - win : i]
        mu = sum(past) / win
        var = sum((p - mu) ** 2 for p in past) / (win - 1)
        sig = math.sqrt(var) if var > 0 else 1.0
        z = (v - mu) / sig
        seq.append("C" if z > 0.75 else ("A" if z < -0.75 else "B"))
    return seq


def a1_dev_only(n: int, seed: int) -> list[str]:
    mid = int(0.65 * n)
    return g1_planted(mid, seed) + [random.Random(seed + 99).choice(ALPH) for _ in range(n - mid)]


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


def certify(seq, cand_id: str, ledger: SearchLedger, gov: Governor) -> dict:
    mid = int(0.65 * len(seq))
    pref, hold = seq[:mid], seq[mid:]
    cand = Candidate(
        candidate_id=cand_id,
        representation={"alphabet": list(ALPH), "models": ["M0", "M1", "M2"]},
        grammar={"family": "nested_markov"},
        claim_class="predictive_grammar",
        lineage=[],
    )
    cand.status = "DISCOVERED"
    ledger.append(
        actor="EXPLORER", action="PROPOSE", candidate_id=cand_id, partition="DISCOVER",
        representation_hash=spec_hash(cand.representation), grammar_hash=spec_hash(cand.grammar),
        search_burden_note="wave0 nested M0/M1/M2 only", outcome_summary="DISCOVERED",
    )
    gov.touch_cert(cand_id)
    m0, m1, m2 = nll_marginal(pref, hold), nll_markov1(pref, hold), nll_order2(pref, hold)
    d21, d10 = m2 - m1, m1 - m0
    if d21 < -6.0 and (m2 - m0) < -6.0:
        gov.set_status(cand, "STATISTICALLY_SUPPORTED", "CERTIFIER")
        status = "STATISTICALLY_SUPPORTED"
    elif d10 < -6.0:
        gov.set_status(cand, "UNRESOLVED", "CERTIFIER")
        status = "MARKOV1_ONLY"
    else:
        gov.set_status(cand, "REFUTED", "CERTIFIER")
        status = "REFUTED"
    return {"status": status, "d_m2_m1": d21, "d_m1_m0": d10}


GENERATORS = {"SYN-G1": g1_planted, "SYN-N1": n1_dependent, "SYN-A1": a1_dev_only}


def run_candidate(cid: str, n_worlds: int = 20, n: int = 900) -> dict:
    ledger = SearchLedger()
    gov = Governor(ledger)
    gen = GENERATORS[cid]
    tallies = Counter()
    lifts = []
    for w in range(n_worlds):
        ev = certify(gen(n, seed=100 + w), f"{cid}-{w}", ledger, gov)
        tallies[ev["status"]] += 1
        lifts.append(ev)
    profile = {
        "candidate_id": cid,
        "representations_searched": 1,
        "models_searched": ["M0", "M1", "M2"],
        "adaptive_iterations": 0,
        "human_interventions": 0,
        "search_budget": "frozen_nested_only",
        "ledger_burden": ledger.burden(),
    }
    return {
        "id": cid,
        "n_worlds": n_worlds,
        "tallies": dict(tallies),
        "mean_d_m2_m1": sum(x["d_m2_m1"] for x in lifts) / n_worlds,
        "mean_d_m1_m0": sum(x["d_m1_m0"] for x in lifts) / n_worlds,
        "discovery_profile": profile,
    }


def run() -> dict:
    g1 = run_candidate("SYN-G1")
    n1 = run_candidate("SYN-N1")
    a1 = run_candidate("SYN-A1")
    g1_ok = g1["tallies"].get("STATISTICALLY_SUPPORTED", 0) >= 15
    n1_ok = n1["tallies"].get("STATISTICALLY_SUPPORTED", 0) == 0
    a1_ok = a1["tallies"].get("STATISTICALLY_SUPPORTED", 0) == 0
    halt_historical = not (g1_ok and n1_ok and a1_ok)
    return {
        "id": "CER-0001-WAVE0",
        "architecture": "UNCHANGED",
        "capital": 0,
        "force_language": "OFF",
        "wave1_historical": "CLOSED" if halt_historical else "NOT_OPENED_YET",
        "SYN-G1": g1,
        "SYN-N1": n1,
        "SYN-A1": a1,
        "pass_G1_recover": g1_ok,
        "pass_N1_refuse": n1_ok,
        "pass_A1_protected": a1_ok,
        "admissible": ["NO_RESULT", "REJECT", "PARK", "LOCAL_ONLY", "GRAMMAR_ONLY"],
        "label": "WAVE0_ONLY",
    }
