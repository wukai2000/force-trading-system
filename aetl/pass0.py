"""PASS-0 — frozen M0/M1/M2 discrimination. Not a Force. HOU-1 closed."""
from __future__ import annotations

import hashlib
import math
import random
from collections import Counter, defaultdict
from typing import Dict, List, Sequence, Tuple

MASTER = 20260915
GATE = 6.0
K = 3
ALPHA = 1.0
ALPH = (0, 1, 2)


def rng_for(world: str, r: int, tag: str = "dgp") -> random.Random:
    h = hashlib.sha256(f"{MASTER}|{world}|{r}|{tag}".encode()).digest()
    return random.Random(int.from_bytes(h[:8], "big"))


def gen_markov1(T: int, stay: float, rng: random.Random) -> List[int]:
    off = (1.0 - stay) / (K - 1)
    x = rng.randrange(K)
    out = [x]
    for _ in range(T - 1):
        u = rng.random()
        if u < stay:
            x = x
        else:
            others = [s for s in ALPH if s != x]
            # remaining mass split equally
            x = others[0] if (u - stay) < off else others[1]
        out.append(x)
    return out


def gen_modular2(T: int, rng: random.Random, p_true: float = 0.80) -> List[int]:
    a, b = rng.randrange(K), rng.randrange(K)
    out = [a, b]
    p_other = (1.0 - p_true) / (K - 1)
    for _ in range(T - 2):
        target = (out[-2] + out[-1] + 1) % K
        u = rng.random()
        if u < p_true:
            nxt = target
        else:
            others = [s for s in ALPH if s != target]
            nxt = others[0] if (u - p_true) < p_other else others[1]
        out.append(nxt)
    return out


def split_seq(seq: Sequence[int]) -> Tuple[List[int], int, int, int]:
    T = len(seq)
    n_train = T // 2
    n_dev = T // 4
    n_prot = T - n_train - n_dev
    return list(seq), n_train, n_dev, n_prot


def loglik_order0(seq: Sequence[int], fit_end: int, sc_start: int, sc_end: int, k: int = K) -> float:
    marg = Counter(seq[:fit_end])
    tot = sum(marg.values()) or 1
    acc = 0.0
    for t in range(sc_start, sc_end):
        p = (marg[seq[t]] + ALPHA) / (tot + ALPHA * k)
        acc += math.log(max(p, 1e-15))
    return acc


def loglik_markov(seq: Sequence[int], order: int, fit_end: int, sc_start: int, sc_end: int, k: int = K) -> float:
    if order == 0:
        return loglik_order0(seq, fit_end, sc_start, sc_end, k)
    ctx = defaultdict(Counter)
    for t in range(order, fit_end):
        ctx[tuple(seq[t - order : t])][seq[t]] += 1
    acc = 0.0
    t0 = max(sc_start, order)
    for t in range(t0, sc_end):
        row = ctx[tuple(seq[t - order : t])]
        den = sum(row.values())
        p = (row[seq[t]] + ALPHA) / (den + ALPHA * k)
        acc += math.log(max(p, 1e-15))
    return acc


def evaluate_ladder(seq: Sequence[int]) -> Dict:
    _, n_train, n_dev, n_prot = split_seq(seq)
    T = len(seq)
    prot_start = n_train + n_dev
    m0 = loglik_markov(seq, 0, n_train, prot_start, T)
    m1 = loglik_markov(seq, 1, n_train, prot_start, T)
    m2 = loglik_markov(seq, 2, n_train, prot_start, T)
    d10 = m1 - m0
    d21 = m2 - m1
    d20 = m2 - m0
    g1 = d10 >= GATE
    g2 = (d21 >= GATE) and (d20 >= GATE)
    if g2:
        label = "M2_claimed"
    elif g1:
        label = "M1_sufficient"
    else:
        label = "no_dependence"
    return {
        "T": T,
        "n_train": n_train,
        "n_dev": n_dev,
        "n_prot": n_prot,
        "ll_m0": m0,
        "ll_m1": m1,
        "ll_m2": m2,
        "d10": d10,
        "d21": d21,
        "d20": d20,
        "g1": g1,
        "g2": g2,
        "label": label,
        "sign_m2_gt_m1": d21 > 0,
    }


def make_seq(world: str, r: int) -> List[int]:
    rng = rng_for(world, r, "dgp")
    if world == "A":
        return gen_markov1(1500, 0.70, rng)
    if world == "B":
        return gen_modular2(1500, rng)
    if world == "C":
        return gen_markov1(400, 0.50, rng)
    raise ValueError(world)


def summarize(rows: List[Dict]) -> Dict:
    n = len(rows)
    g1 = sum(1 for x in rows if x["g1"]) / n
    g2 = sum(1 for x in rows if x["g2"]) / n
    m1s = sum(1 for x in rows if x["label"] == "M1_sufficient") / n
    d10 = [x["d10"] for x in rows]
    d21 = [x["d21"] for x in rows]
    d21s = sorted(d21)

    def mean(xs):
        return sum(xs) / len(xs)

    def pct(xs, p):
        i = min(len(xs) - 1, max(0, int(round(p * (len(xs) - 1)))))
        return xs[i]

    return {
        "n": n,
        "g1_rate": g1,
        "g2_rate": g2,
        "m1_sufficient_rate": m1s,
        "mean_d10": mean(d10),
        "mean_d21": mean(d21),
        "p05_d21": pct(d21s, 0.05),
        "p95_d21": pct(d21s, 0.95),
        "max_d21": max(d21),
        "sign_m2_gt_m1": sum(1 for x in rows if x["sign_m2_gt_m1"]) / n,
        "n_g2": sum(1 for x in rows if x["g2"]),
    }


def collapse(seq: Sequence[int]) -> List[int]:
    return [0] * len(seq)


def naive_collapse_claim(seq: Sequence[int]) -> Dict:
    """Incommensurable: 1-symbol collapse M0 has ll≈0 vs original M1."""
    _, n_train, n_dev, _ = split_seq(seq)
    T = len(seq)
    prot_start = n_train + n_dev
    m1 = loglik_markov(seq, 1, n_train, prot_start, T, k=K)
    col = collapse(seq)
    m0c = loglik_markov(col, 0, n_train, prot_start, T, k=1)
    return {"ll_m1": m1, "ll_collapse": m0c, "delta_collapse_minus_m1": m0c - m1, "alt_claim": (m0c - m1) >= GATE}


def identity_order_search(seq: Sequence[int], max_order: int = 4) -> Dict:
    _, n_train, n_dev, _ = split_seq(seq)
    T = len(seq)
    dev_start, prot_start = n_train, n_train + n_dev
    best_o, best_dev = 0, -1e18
    for o in range(0, max_order + 1):
        ll = loglik_markov(seq, o, n_train, dev_start, prot_start)
        if ll > best_dev:
            best_dev, best_o = ll, o
    m1 = loglik_markov(seq, 1, n_train, prot_start, T)
    m0 = loglik_markov(seq, 0, n_train, prot_start, T)
    sel = loglik_markov(seq, best_o, n_train, prot_start, T)
    d_sel_m1 = sel - m1
    d_sel_m0 = sel - m0
    alt = (d_sel_m1 >= GATE) and (d_sel_m0 >= GATE) and best_o >= 2
    return {
        "dev_pick_order": best_o,
        "dev_picks_gt1": best_o > 1,
        "prot_d_sel_m1": d_sel_m1,
        "prot_alt_claim": alt,
    }


WORLD_R = {"A": 80, "B": 80, "C": 200}


def run() -> Dict:
    ladder = {}
    ladder_rows = []
    for world, R in WORLD_R.items():
        rows = []
        for r in range(R):
            ev = evaluate_ladder(make_seq(world, r))
            ev["world"] = world
            ev["r"] = r
            rows.append(ev)
            ladder_rows.append(ev)
        ladder[world] = summarize(rows)

    # Naive collapse on all worlds, first 40 / 40 / 40 to keep bounded
    collapse_tab = {}
    for world, cap in (("A", 40), ("B", 40), ("C", 40)):
        hits = 0
        n = 0
        for r in range(cap):
            n += 1
            if naive_collapse_claim(make_seq(world, r))["alt_claim"]:
                hits += 1
        collapse_tab[world] = {"n": n, "alt_claim_rate": hits / n}

    ident = {}
    for world, cap in (("A", 80), ("C", 80), ("B", 40)):
        picks = 0
        alts = 0
        n = 0
        for r in range(cap):
            n += 1
            ev = identity_order_search(make_seq(world, r), 4)
            picks += int(ev["dev_picks_gt1"])
            alts += int(ev["prot_alt_claim"])
        ident[world] = {"n": n, "dev_picks_gt1": picks / n, "prot_alt_claim": alts / n}

    f1 = ladder["A"]["g2_rate"] > 0.10
    f2 = ladder["B"]["g2_rate"] < 0.80
    f3 = ladder["C"]["g2_rate"] > 0.10
    collapse_refuse = all(v["alt_claim_rate"] >= 0.99 for v in collapse_tab.values())
    decision = "HOLD"
    if f1 or f2 or f3:
        decision = "LADDER_FAIL"
    return {
        "id": "PASS-0",
        "protocol": "FORCE_PROTOCOL_v1.0",
        "capital": 0,
        "force_language": "OFF",
        "gate_nats": GATE,
        "gate_moved": False,
        "master_seed": MASTER,
        "split": "50/25/25",
        "laplace_alpha": ALPHA,
        "ladder": ladder,
        "collapse_naive": collapse_tab,
        "identity_order_search": ident,
        "F1_A_invents": f1,
        "F2_B_misses": f2,
        "F3_C_false_g2": f3,
        "naive_recoding": "REFUSE" if collapse_refuse else "UNEXPECTED",
        "hou1": "REFUSE",
        "wave1": "NOT_OPENED",
        "evidence_record": "NOT_PERMITTED",
        "decision": decision,
        "label": "HOLD" if decision == "HOLD" else decision,
        "note": "Sidecar lab. Does not amend BR-0001. Cells are not I_t.",
        "_rows": ladder_rows,
    }
