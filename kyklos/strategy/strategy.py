import pandas as pd
import talib
import os
import logging

# Ensure the 'log' directory exists
if not os.path.exists('log'):
    os.makedirs('log')

# Set up logging for strategy
strategy_logger = logging.getLogger('strategy_logger')
strategy_logger.setLevel(logging.INFO)

# Create a file handler for logging
strategy_handler = logging.FileHandler('log/strategy.log')
strategy_handler.setLevel(logging.INFO)  # Set level to log INFO or higher

# Create a console handler to debug
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create a formatter and set it for both handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
strategy_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
strategy_logger.addHandler(strategy_handler)
strategy_logger.addHandler(console_handler)


class TradingStrategy:
    def __init__(self, data):
        self.data = data

    def calculate_indicators(self):
        """Calculate technical indicators using TA-Lib."""
        self.data['SMA_20'] = talib.SMA(self.data['close'], timeperiod=20)
        self.data['SMA_50'] = talib.SMA(self.data['close'], timeperiod=50)
        self.data['EMA_20'] = talib.EMA(self.data['close'], timeperiod=20)
        self.data['EMA_50'] = talib.EMA(self.data['close'], timeperiod=50)
        self.data['RSI'] = talib.RSI(self.data['close'], timeperiod=14)
        self.data['MACD'], self.data['MACD_SIGNAL'], self.data['MACD_DIFF'] = talib.MACD(
            self.data['close'], fastperiod=12, slowperiod=26, signalperiod=9
        )
        self.data['BOLLINGER_HIGH'], self.data['BOLLINGER_LOW'] = talib.BBANDS(
            self.data['close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0
        )[:2]  # High and Low bands only, excluding middle band
        self.data['STOCH'], self.data['STOCH_SIGNAL'] = talib.STOCH(
            self.data['high'], self.data['low'], self.data['close'], 
            fastk_period=14, slowk_period=3, slowk_matype=0, 
            slowd_period=3, slowd_matype=0
        )


    def clean_data(self):
        """Drop rows with NaN values and ensure enough data."""
        self.data = self.data.dropna()
        if len(self.data) < 50:
            print("Not enough data after cleaning.")
            return False
        return True

    def apply_strategy(self):
        try:
            if len(self.data) < 50:
                strategy_logger.warning("Not enough data to apply strategy.")
                return 'HOLD'

            self.calculate_indicators()

            if not self.clean_data():
                return 'HOLD'

            buy_signals = self.signal_buy(self.data)
            sell_signals = self.signal_sell(self.data)

            print(f"Buy signals: \n\n{buy_signals}\n\nSell signals:\n\n{sell_signals}")

        except Exception as e:
            strategy_logger.error(f"Error applying strategy: {e}")
            return 'HOLD'

    def signal_buy(self, values):
        buy_signals = [
            values['RSI'].iloc[-1] < 30,
            values['SMA_20'].iloc[-1] > values['SMA_50'],
            values['EMA_20'].iloc[-1] > values['EMA_50'],
            values['MACD'].iloc[-1] > values['MACD_SIGNAL'],
            values['close'].iloc[-1] < values['BOLLINGER_LOW'],
            values['STOCH'].iloc[-1] < values['STOCH_SIGNAL']
        ]
        # strategy_logger.info(f"Trading signal Buy: {buy_signals}")
        return buy_signals

    def signal_sell(self, values):
        sell_signals = [
            values['RSI'].iloc[-1] > 70,
            values['SMA_20'].iloc[-1] < values['SMA_50'],
            values['EMA_20'].iloc[-1] < values['EMA_50'],
            values['MACD'].iloc[-1] < values['MACD_SIGNAL'],
            values['close'].iloc[-1] > values['BOLLINGER_HIGH'],
            values['STOCH'].iloc[-1] > values['STOCH_SIGNAL']
        ]
        # strategy_logger.info(f"Trading signal Sell: {sell_signals}")

        return sell_signals
