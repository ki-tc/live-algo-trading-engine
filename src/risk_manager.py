class RiskManager:
    """
    Acts as an inline risk firewall intercepting trade signals to protect capital
    via strict position-sizing, concentration ceilings, and risk barriers.
    """
    def __init__(self, max_single_pos: float, stop_loss: float, initial_cap: float):
        self.max_single_pos = max_single_pos
        self.stop_loss = stop_loss
        self.current_capital = initial_cap

    def calculate_position_size(self, asset_price: float, signal: int) -> float:
        """
        Enforces maximum single-position equity risk constraints to scale position parameters.
        """
        if signal == 0:
            return 0.0
            
        # Allocate a strict subset of total portfolio equity to a single trade
        allocated_capital = self.current_capital * self.max_single_pos
        shares = allocated_capital / asset_price
        
        return float(shares * signal)

    def validate_execution(self, current_drawdown: float) -> bool:
        """
        Circuit breaker to instantly halt execution if portfolio wide drawdown thresholds are breached.
        """
        if current_drawdown >= 0.05:
            print("CRITICAL RISK METRIC BREACHED: Portfolio circuit breaker deployed. System halting.")
            return False
        return True
