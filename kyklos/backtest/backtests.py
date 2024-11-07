from backtesting import Backtest, Strategy
import datetime as dt
from binance import Client
import pandas as pd
import kyklos.utils.constants as cn
from scipy.signal import find_peaks
import numpy as np
import talib

# data=0

# for col in ['open', 'high', 'low', 'close', 'volume']:
#     data[col] = pd.to_numeric(data[col])

# data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
# data.set_index('timestamp', inplace=True)

# data = data[['open', 'high', 'low', 'close', 'volume']]

# data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']


class BollingerBandsStrategy(Strategy):
    # Define strategy parameters with default values
    bollinger_period = 25
    bollinger_std = 1.5

    def init(self):
        # Calculate Bollinger Bands using TA-Lib
        self.upper_band, self.middle_band, self.lower_band = talib.BBANDS(
            self.data.Close,
            timeperiod=self.bollinger_period,
            nbdevup=self.bollinger_std,
            nbdevdn=self.bollinger_std,
            matype=talib.MA_Type.SMA
        )

    def next(self):
        # Current price
        price = self.data.Close[-1]

        # Current Bollinger Bands
        upper = self.upper_band[-1]
        middle = self.middle_band[-1]
        lower = self.lower_band[-1]

        # Previous price
        prev_price = self.data.Close[-2]

        # Buy Signal: Price crosses below the lower Bollinger Band
        if prev_price > lower and price < lower:
            self.buy()

        # Sell Signal: Price crosses above the upper Bollinger Band
        elif prev_price < upper and price > upper:
            self.sell()

# # 3. Initialize the Backtest with the Bollinger Bands strategy
# bt = Backtest(
#     data,
#     BollingerBandsStrategy,
#     cash=10_000,          # Starting with $100,000
#     commission=0.001,      # 0.1% commission per trade
#     exclusive_orders=True   # Prevent overlapping positions
# )

# # 4. Run the backtest
# stats = bt.run()

# # 5. Print the backtest statistics
# print(stats)
# print(f"\n{cn.bold}{cn.white}{cn.bg_blue}","="*20, "Normal Trades", "="*20 ,f"{cn.reset}\n")
# print(stats["_trades"])


# print(f"\n{cn.bold}{cn.blue}{cn.bg_bright_white}{'+=' * 20} Optimized {'+=' * 20}{cn.reset}\n")



# # # Run the optimization
# optimized_stats = bt.optimize(
#     bollinger_period=range(10, 31, 1),
#     bollinger_std=list(np.linspace(1.5, 3.0, 4)),
#     maximize='Return [%]',
#     constraint=lambda p: p.bollinger_period < 100
# )

# # # Print optimized results
# print(optimized_stats)
# # print(optimized_stats[['bollinger_period', 'Sharpe Ratio']])
# print(f"\n{cn.bold}{cn.white}{cn.bg_blue}","="*20, "Optimized Trades", "="*20 ,f"{cn.reset}\n")


# print(optimized_stats["_trades"])

# print(f"\n{cn.bold}{cn.white}{cn.bg_blue}","="*20, "Optimized Strategy", "="*20 ,f"{cn.reset}\n")

# print(optimized_stats["_strategy"])

# total=100000

# for i in stats['_trades']['PnL']:
#     total+=float(i)

# print(f"Total: {total}")