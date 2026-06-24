import pandas as pd
import yfinance as yf
from typing import List, Dict

class DataIngestionEngine:
    """
    Handles streaming historical and real-time market data ingestion.
    For this implementation, it interfaces with Yahoo Finance to pull high-fidelity bars.
    """
    def __init__(self, benchmark: str, universe: List[str]):
        self.benchmark = benchmark
        self.universe = universe
        self.all_tickers = [benchmark] + universe

    def fetch_historical_data(self, start_date: str, end_date: str) -> Dict[str, pd.Series]:
        """
        Fetches historical daily adjusted closing prices for the asset universe and benchmark.
        """
        print(f"Ingesting historical market data from {start_date} to {end_date}...")
        data = yf.download(self.all_tickers, start=start_date, end=end_date, progress=False)
        
        # Extract adjusted close columns cleanly
        adj_close = data['Adj Close']
        
        market_data = {}
        for ticker in self.all_tickers:
            if ticker in adj_close.columns:
                market_data[ticker] = adj_close[ticker].dropna()
                
        return market_data
