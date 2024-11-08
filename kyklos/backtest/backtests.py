from backtesting import Backtest, Strategy
import datetime as dt
import pandas as pd
import kyklos.utils.constants as cn
from scipy.signal import find_peaks
import numpy as np
import talib


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
