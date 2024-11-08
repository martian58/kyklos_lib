from backtesting import Backtest, Strategy
import pandas as pd
import numpy as np
from .backtests import BollingerBandsStrategy


class BacktestStrategy:
    def __init__(self, data: pd.DataFrame, commission: float = 0.001) -> None:
        self.data = data
        for col in ['open', 'high', 'low', 'close', 'volume']:
            self.data[col] = pd.to_numeric(data[col])
        self.data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        
        self.commission = commission

    def backtest_boolinger_bands(self):
        bt = Backtest(
            self.data,
            BollingerBandsStrategy,
            cash=100_000,
            commission=self.commission,
            exclusive_orders=True
        )

        stats = bt.run()
        trades = stats["_trades"]

        # optimized_stats = bt.optimize(
        #     bollinger_period=range(10, 31, 1),
        #     bollinger_std=list(np.linspace(1.5, 3.0, 4)),
        #     maximize='Return [%]',
        # )

        # optimized_trades = optimized_stats["_trades"]
        # strategy_values = optimized_stats["_strategy"]

        results = {
            'stats' : stats,
            'trades': trades
        }

        return results

