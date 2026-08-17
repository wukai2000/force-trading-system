"""
Trading Engine (bare minimum).

Takes force suggestions + current portfolio and produces TradeProposal(s)
under the active PolicyConfig.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from force_engine.base import ForceSuggestion
from .policies import PolicyConfig, PolicyMode
from .portfolio import Portfolio


class ProposalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    EXPIRED = "expired"
    AUTO_EXECUTED = "auto_executed"
    AUTO_CANCELLED = "auto_cancelled"


@dataclass
class TradeProposal:
    id: str
    symbol: str
    side: str  # "buy" | "sell"
    quantity: float
    rationale: str
    force_ids: List[str] = field(default_factory=list)
    status: ProposalStatus = ProposalStatus.PENDING
    created_at: str = ""
    policy_mode: str = ""
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "symbol": self.symbol,
            "side": self.side,
            "quantity": self.quantity,
            "rationale": self.rationale,
            "force_ids": self.force_ids,
            "status": self.status.value,
            "created_at": self.created_at,
            "policy_mode": self.policy_mode,
            "meta": self.meta,
        }


class TradingEngine:
    def __init__(
        self,
        portfolio: Optional[Portfolio] = None,
        policy: Optional[PolicyConfig] = None,
    ):
        self.portfolio = portfolio or Portfolio()
        self.policy = policy or PolicyConfig(mode=PolicyMode.REQUIRE_APPROVAL)
        self._proposal_counter = 0
        self.proposals: List[TradeProposal] = []

    def _next_id(self) -> str:
        self._proposal_counter += 1
        return f"prop-{self._proposal_counter:04d}"

    def propose_from_forces(
        self,
        suggestions: List[ForceSuggestion],
        max_positions: int = 3,
    ) -> List[TradeProposal]:
        """
        Extremely simple mapping from force suggestions → trade proposals.
        Real logic will use force intensity, related assets, risk rules, etc.
        Currently produces no real trades (placeholder).
        """
        now = datetime.now(timezone.utc).isoformat()
        proposals: List[TradeProposal] = []

        # Placeholder: if any force has non-zero intensity, note it
        active = [s for s in suggestions if abs(s.intensity) > 1e-6]
        if not active:
            # Still emit a diagnostic "no action" style note via empty list
            return proposals

        # Future: map high-intensity forces to concrete symbols from force.meta["related"]
        for s in active:
            prop = TradeProposal(
                id=self._next_id(),
                symbol="SPY",  # placeholder
                side="buy" if s.intensity > 0 else "sell",
                quantity=0.0,  # size later
                rationale=f"Placeholder proposal driven by {s.force_name}: {s.rationale}",
                force_ids=[s.force_id],
                status=ProposalStatus.PENDING,
                created_at=now,
                policy_mode=self.policy.mode.value,
            )
            proposals.append(prop)
            self.proposals.append(prop)

        return proposals

    def apply_policy(self, proposal: TradeProposal) -> TradeProposal:
        """
        Apply the current policy to a proposal.
        In pure simulation we only set status; no real execution.
        """
        if self.policy.mode == PolicyMode.FULL_AUTONOMY:
            proposal.status = ProposalStatus.AUTO_EXECUTED
            # Future: call portfolio update here
        elif self.policy.mode == PolicyMode.REQUIRE_APPROVAL:
            proposal.status = ProposalStatus.PENDING
            # Human must approve later
        elif self.policy.mode == PolicyMode.TIMED_WINDOW:
            proposal.status = ProposalStatus.PENDING
            proposal.meta["window_minutes"] = self.policy.window_minutes
            proposal.meta["timeout_go_ahead"] = self.policy.timeout_go_ahead
            # Scheduler / human will resolve later
        return proposal

    def approve(self, proposal_id: str) -> Optional[TradeProposal]:
        for p in self.proposals:
            if p.id == proposal_id and p.status == ProposalStatus.PENDING:
                p.status = ProposalStatus.APPROVED
                # Future: execute against portfolio
                return p
        return None

    def reject(self, proposal_id: str) -> Optional[TradeProposal]:
        for p in self.proposals:
            if p.id == proposal_id and p.status == ProposalStatus.PENDING:
                p.status = ProposalStatus.REJECTED
                return p
        return None


def main():
    import argparse
    import json
    from force_engine.engine import ForceEngine

    parser = argparse.ArgumentParser(description="Trading Engine demo")
    parser.add_argument(
        "--policy",
        choices=[m.value for m in PolicyMode],
        default=PolicyMode.REQUIRE_APPROVAL.value,
    )
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args()

    force_engine = ForceEngine()
    suggestions = force_engine.suggest()

    policy = PolicyConfig(mode=PolicyMode(args.policy))
    te = TradingEngine(policy=policy)

    print(f"Policy: {policy.to_dict()}")
    print("Force suggestions:")
    for s in suggestions:
        print(f"  {s.force_name}: intensity={s.intensity:.2f} conf={s.confidence:.2f}")

    proposals = te.propose_from_forces(suggestions)
    for p in proposals:
        te.apply_policy(p)
        print(json.dumps(p.to_dict(), indent=2))

    if not proposals:
        print("No trade proposals generated (expected while force intensities are placeholders).")


if __name__ == "__main__":
    main()
