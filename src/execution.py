import pandas as pd
from typing import Dict

class OrderExecutionEngine:
    """
    Simulates automated order routing interfaces and tracks trade transaction costs/slippage models.
    """
    def __init__(self, initial_capital: float):
        self.capital = initial_capital
        self.positions = {}  # Tracks net active shares

    def execute_order(self, ticker: str, target_shares: float, current_price: float) -> float:
        """
        Routes simulated orders, modifies cash positions, and applies transaction friction adjustments.
        """
        current_shares = self.positions.get(ticker, 0.0)
        shares_to_trade = target_shares - current_shares
        
        if shares_to_trade == 0:
            return 0.0
            
        # Linear slippage and commission friction simulation (0.1%)
        friction_multiplier = 1.001 if shares_to_trade > 0 else 0.999
        execution_price = current_price * friction_multiplier
        
        transaction_cost = shares_to_trade * execution_price
        self.capital -= transaction_cost
        self.positions[ticker] = target_shares
        
        return transaction_cost
