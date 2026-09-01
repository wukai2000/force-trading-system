"""Scan / ticket guards. Capital stays $0. Force 4 stays WAIT.

Literature simulators and the panel sieve must import these instead of
hardcoding a theme → ITA/XAR/PPA map.
"""
from __future__ import annotations

from typing import Iterable, List, Sequence


HARD_EXCLUDED_LEGS = {
    "MAGS",
    "SMH",
    "SPMO",
    "VST",
    "ETN",
    "PWR",
    "IHF",
    "IHI",
    "XHS",
}

# Defense sketch — not locked, not scannable. Do not fetch or score as a live force.
WAIT_TICKERS = {"ITA", "XAR", "PPA", "XLI"}

# Vol / level series that are not equity-force candidates.
NON_CANDIDATE_TICKERS = {"VIX", "VIX3M", "VIXCLS", "VXVCLS"}

QQQ_AS_LEG_FORBIDDEN = True


class WaitLockError(RuntimeError):
    """Raised when a caller tries to scan Force 4 / WAIT tickers."""


class RecycleError(RuntimeError):
    """Raised when a caller recycles paused F1/F2/F3 legs as a new force."""


def _up(tickers: Iterable[str]) -> List[str]:
    return [str(t).upper() for t in tickers]


def wait_hits(tickers: Iterable[str]) -> List[str]:
    return [t for t in _up(tickers) if t in WAIT_TICKERS]


def excluded_hits(tickers: Iterable[str]) -> List[str]:
    return [t for t in _up(tickers) if t in HARD_EXCLUDED_LEGS]


def refuse_wait_scan(tickers: Sequence[str], *, allow_wait_sketch: bool = False) -> None:
    hits = wait_hits(tickers)
    if hits and not allow_wait_sketch:
        raise WaitLockError(
            f"WAIT lock: refusing {hits}. ITA/XAR/PPA/XLI are not scannable. "
            "Silent default remains wait. Pass allow_wait_sketch only for a "
            "research YAML rewrite that stays scannable=false."
        )


def refuse_recycled_legs(tickers: Sequence[str], *, research_paused: bool = False) -> None:
    hits = excluded_hits(tickers)
    if hits and not research_paused:
        raise RecycleError(f"refusing paused-force recycle as candidate legs: {hits}")


def refuse_qqq_as_leg(tickers: Sequence[str]) -> None:
    if any(t == "QQQ" for t in _up(tickers)):
        raise RecycleError("QQQ cannot be a leg")
