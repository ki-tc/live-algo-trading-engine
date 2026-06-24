import sys
import os
import yaml
import pandas as pd

# Fix path visibility across packages
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_ingestion import DataIngestionEngine
from src.strategy import RelativePerformanceStrategy
from src.risk_manager import RiskManager
from src.execution import OrderExecutionEngine

class BacktestSimulator:
    """
    Main orchestration loop executing vector/event backtesting over historical data frames.
    """
    def __init__(self, config_path: str):
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)
            
        self.ingestion = DataIngestionEngine(
            benchmark=self.config['trading']['benchmark'],
            universe=self.config['trading']['universe']
        )
        self.strategy = RelativePerformanceStrategy(
            benchmark=self.config['trading']['benchmark'],
            lookback=self.config['trading']['lookback_periods'],
            z_threshold=self.config['trading']['z_score_threshold']
        )
        self.risk = RiskManager(
            max_single_pos=self.config['risk']['max_single_position_pct'],
            stop_loss=self.config['risk']['stop_loss_pct'],
            initial_cap=self.config['risk']['initial_capital']
        )
        self.execution = OrderExecutionEngine(initial_capital=self.config['risk']['initial_capital'])

    def run(self, start_date: str, end_date: str):
        market_data = self.ingestion.fetch_historical_data(start_date, end_date)
        signals = self.strategy.generate_signals(market_data)
        
        # Build an aligned simulation time-series matrix
        tickers = self.config['trading']['universe']
        price_df = pd.DataFrame({t: market_data[t] for t in tickers if t in market_data}).dropna()
        signals = signals.reindex(price_df.index).fillna(0)
        
        portfolio_values = []
        
        print("Running systematic loop across execution matrix rows...")
        for timestamp, price_row in price_df.iterrows():
            total_equity = self.execution.capital
            
            # Step through individual assets to compute current asset values
            for ticker in tickers:
                active_shares = self.execution.positions.get(ticker, 0.0)
                total_equity += active_shares * price_row[ticker]
                
            # Update inline capital balances inside risk engine
            self.risk.current_capital = total_equity
            portfolio_values.append(total_equity)
            
            # Evaluate signals and route to risk firewall -> execution pipeline
            for ticker in tickers:
                current_signal = int(signals.loc[timestamp, ticker])
                current_price = price_row[ticker]
                
                target_shares = self.risk.calculate_position_size(current_price, current_signal)
                self.execution.execute_order(ticker, target_shares, current_price)
                
        perf_series = pd.Series(portfolio_values, index=price_df.index)
        total_return = (perf_series.iloc[-1] / perf_series.iloc[0]) - 1
        
        print("\n--- BACKTEST BACK-END EXECUTION COMPLETE ---")
        print(f"Initial Capital Set: ${perf_series.iloc[0]:,.2f}")
        print(f"Final Capital Value: ${perf_series.iloc[-1]:,.2f}")
        print(f"Net Realized Yield:  {total_return * 100:.2f}%")

if __name__ == "__main__":
    backtest = BacktestSimulator(config_path="config/config.yaml")
    backtest.run(start_date="2024-01-01", end_date="2025-01-01")
