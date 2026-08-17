"""
Pure Python simulation backend (default).
No real broker connection.
"""

from __future__ import annotations

from typing import Dict

from trading_interface.base import (
    OrderRequest,
    OrderResult,
    OrderSide,
    OrderStatus,
    TradingInterface,
)
from trading_engine.portfolio import Portfolio


class PythonSimInterface(TradingInterface):
    name = "python_sim"

    def __init__(self, starting_cash: float = 100_000.0):
        self.portfolio = Portfolio(cash=starting_cash)

    def get_cash(self) -> float:
        return self.portfolio.cash

    def get_positions(self) -> Dict[str, float]:
        return {s: p.quantity for s, p in self.portfolio.positions.items()}

    def submit_order(self, order: OrderRequest) -> OrderResult:
        # Extremely simple simulation: fill at a placeholder price
        # Real version will use latest market data
        fill_price = order.limit_price or 100.0  # placeholder

        if order.side == OrderSide.BUY:
            cost = order.quantity * fill_price
            if cost > self.portfolio.cash:
                return OrderResult(
                    request=order,
                    status=OrderStatus.REJECTED,
                    message="Insufficient cash in simulation",
                )
            self.portfolio.cash -= cost
            self.portfolio.update_position(order.symbol, order.quantity, fill_price)
        else:
            pos = self.portfolio.get_position(order.symbol)
            if pos is None or pos.quantity < order.quantity:
                return OrderResult(
                    request=order,
                    status=OrderStatus.REJECTED,
                    message="Insufficient position in simulation",
                )
            self.portfolio.cash += order.quantity * fill_price
            self.portfolio.update_position(order.symbol, -order.quantity, fill_price)

        return OrderResult(
            request=order,
            status=OrderStatus.SIMULATED,
            filled_quantity=order.quantity,
            avg_fill_price=fill_price,
            message="Filled in pure Python simulation",
        )

    def cancel_order(self, order_id: str) -> bool:
        # Simulation has no open orders to cancel
        return False
