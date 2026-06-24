import numpy as np
import pandas as pd
from typing import Dict

class RelativePerformanceStrategy:
    """
    Generates alpha trading signals by tracking statistical divergence 
    between individual equities and a major market benchmark.
    """
    def __init__(self, benchmark: str, lookback: int, z_threshold: float):
        self.benchmark = benchmark
        self.lookback = lookback
        self.z_threshold = z_threshold

    def generate_signals(self, market_data: Dict[str, pd.Series]) -> pd.DataFrame:
        """
        Calculates the relative performance spread, rolling z-scores, and entry/exit signals.
        """
        print("Executing relative-performance signal generation matrix...")
        benchmark_series = market_data[self.benchmark]
        signals_dict = {}

        for ticker, series in market_data.items():
            if ticker == self.benchmark:
                continue
                
            # Align asset data with benchmark indices
            df = pd.DataFrame({'asset': series, 'benchmark': benchmark_series}).dropna()
            
            # Calculate log returns
            df['asset_ret'] = np.log(df['asset'] / df['asset'].shift(1))
            df['bench_ret'] = np.log(df['benchmark'] / df['benchmark'].shift(1))
            
            # Calculate rolling relative performance spread (residual return spread)
            df['spread'] = df['asset_ret'] - df['bench_ret']
            df['rolling_mean'] = df['spread'].rolling(window=self.lookback).mean()
            df['rolling_std'] = df['spread'].rolling(window=self.lookback).std()
            
            # Calculate dynamic Z-Score
            df['z_score'] = (df['spread'] - df['rolling_mean']) / df['rolling_std']
            
            # Formulate cross-sectional signals: 1 (Long Alpha), -1 (Short Alpha), 0 (Flat)
            df['signal'] = 0
            df.loc[df['z_score'] < -self.z_threshold, 'signal'] = 1   # Asset oversold relative to market
            df.loc[df['z_score'] > self.z_threshold, 'signal'] = -1   # Asset overbought relative to market
            
            signals_dict[ticker] = df['signal']

        return pd.DataFrame(signals_dict).fillna(0)
