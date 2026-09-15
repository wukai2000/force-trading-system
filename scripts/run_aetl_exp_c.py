#!/usr/bin/env python3
"""AETL Exp C2: motif-fishing on noise. Shows naive FPR rising with search width."""
from __future__ import annotations

import json
import math
import random
from collections import Counter


def tokens(n, seed, p=(0.2, 0.6, 0.2)):
    rng = random.Random(seed)
    alph = "DFR"
    return [alph[rng.choices(range(3), weights=p)[0]] for _ in range(n)]


def grams(seq, k):
    return ["".join(seq[i : i + k]) for i in range(len(seq) - k + 1)]


def lift(seq, k):
    g = grams(seq, k)
    c = Counter(g)
    tot = len(g) or 1
    marg = Counter(seq)
    n = len(seq) or 1
    out = []
    for mot, cnt in c.items():
        p = 1.0
        for ch in mot:
            p *= marg[ch] / n
        exp = p * tot
        out.append((cnt / max(exp, 1e-9), mot, cnt, exp))
    out.sort(reverse=True)
    return out


def holdout_enrichment(pref, hold, mot, k):
    pg = grams(pref, k)
    hg = grams(hold, k)
    rate = pg.count(mot) / max(len(pg), 1)
    obs = hg.count(mot)
    exp = rate * len(hg)
    return obs, exp, obs > exp + 2.0 * math.sqrt(max(exp, 1.0)) and obs >= 4


def run(n_worlds=80, n=400, ks=(2, 3), tops=(1, 3, 8, 20)):
    naive = {t: 0 for t in tops}
    certified = {t: 0 for t in tops}
    for w in range(n_worlds):
        seq = tokens(n, seed=3000 + w)
        mid = int(0.65 * n)
        pref, hold = seq[:mid], seq[mid:]
        cands = []
        for k in ks:
            cands.extend(lift(pref, k))
        cands.sort(reverse=True)
        for t in tops:
            hits = 0
            for _lift, mot, _cnt, _exp in cands[:t]:
                _obs, _hexp, enr = holdout_enrichment(pref, hold, mot, len(mot))
                if enr:
                    hits += 1
            if hits:
                naive[t] += 1
            ok = False
            for _lift, mot, _cnt, _exp in cands[:t]:
                obs, hexp, _ = holdout_enrichment(pref, hold, mot, len(mot))
                if obs >= 4 and (obs - hexp) > 2.0 * math.sqrt(max(hexp, 1.0)) + math.log(t):
                    ok = True
            if ok:
                certified[t] += 1
    w = float(n_worlds)
    return {
        "id": "AETL-EXP-C2",
        "process": "iid_ternary_tokens",
        "n_worlds": n_worlds,
        "naive_fpr_any_holdout_enrichment": {str(t): naive[t] / w for t in tops},
        "certified_fpr_kappa_log_t": {str(t): certified[t] / w for t in tops},
        "label": "LAB_ONLY",
        "capital": 0,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
