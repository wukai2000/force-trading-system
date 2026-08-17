"""
Minimal portfolio state for the pure Python simulator.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Position:
    symbol: str
    quantity: float
    avg_price: float = 0.0
    meta: Dict = field(default_factory=dict)

    @property
    def market_value(self) -> float:
        # Placeholder: real sim will mark to market
        return self.quantity * self.avg_price


@dataclass
class Portfolio:
    cash: float = 100_000.0  # default paper cash
    positions: Dict[str, Position] = field(default_factory=dict)
    currency: str = "USD"

    def get_position(self, symbol: str) -> Optional[Position]:
        return self.positions.get(symbol)

    def update_position(self, symbol: str, quantity_delta: float, price: float):
        pos = self.positions.get(symbol)
        if pos is None:
            if quantity_delta == 0:
                return
            self.positions[symbol] = Position(
                symbol=symbol, quantity=quantity_delta, avg_price=price
            )
        else:
            new_qty = pos.quantity + quantity_delta
            if new_qty == 0:
                del self.positions[symbol]
            else:
                # Simple average price update
                if quantity_delta > 0:
                    total_cost = pos.avg_price * pos.quantity + price * quantity_delta
                    pos.avg_price = total_cost / new_qty
                pos.quantity = new_qty

    def summary(self) -> Dict:
        return {
            "cash": self.cash,
            "positions": {
                s: {"quantity": p.quantity, "avg_price": p.avg_price}
                for s, p in self.positions.items()
            },
        }
