import pandas as pd
import ta
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

    def calculate_percentage_change(self):
        self.data['percentage_change'] = self.data['close'].pct_change() * 100

    def calculate_indicators(self):
        """Calculate technical indicators."""
        self.data['SMA_20'] = ta.trend.sma_indicator(self.data['close'], window=20)
        self.data['SMA_50'] = ta.trend.sma_indicator(self.data['close'], window=50)
        self.data['EMA_20'] = ta.trend.ema_indicator(self.data['close'], window=20)
        self.data['EMA_50'] = ta.trend.ema_indicator(self.data['close'], window=50)
        self.data['RSI'] = ta.momentum.RSIIndicator(self.data['close']).rsi()
        self.data['MACD'] = ta.trend.macd(self.data['close'])
        self.data['MACD_SIGNAL'] = ta.trend.macd_signal(self.data['close'])
        self.data['MACD_DIFF'] = ta.trend.macd_diff(self.data['close'])
        self.data['BOLLINGER_HIGH'] = ta.volatility.BollingerBands(self.data['close']).bollinger_hband()
        self.data['BOLLINGER_LOW'] = ta.volatility.BollingerBands(self.data['close']).bollinger_lband()
        self.data['STOCH'] = ta.momentum.StochasticOscillator(self.data['high'], self.data['low'], self.data['close']).stoch()
        self.data['STOCH_SIGNAL'] = ta.momentum.StochasticOscillator(self.data['high'], self.data['low'], self.data['close']).stoch_signal()

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
            self.calculate_percentage_change()

            if not self.clean_data():
                return 'HOLD'

            latest_values = self.data.iloc[-1]

            if self.signal_buy(latest_values):
                strategy_logger.info("BUY signal generated.")
                return 'BUY'
            elif self.signal_sell(latest_values):
                strategy_logger.info("SELL signal generated.")
                return 'SELL'
            return 'HOLD'

        except Exception as e:
            strategy_logger.error(f"Error applying strategy: {e}")
            return 'HOLD'

    def signal_buy(self, values):
        buy_signals = [
            values['RSI'] < 30,
            values['SMA_20'] > values['SMA_50'],
            values['EMA_20'] > values['EMA_50'],
            values['percentage_change'] < -4.0,
            values['MACD'] > values['MACD_SIGNAL'],
            values['close'] < values['BOLLINGER_LOW'],
            values['STOCH'] < values['STOCH_SIGNAL']
        ]
        return any(buy_signals)

    def signal_sell(self, values):
        sell_signals = [
            values['RSI'] > 70,
            values['SMA_20'] < values['SMA_50'],
            values['EMA_20'] < values['EMA_50'],
            values['percentage_change'] > 4.0,
            values['MACD'] < values['MACD_SIGNAL'],
            values['close'] > values['BOLLINGER_HIGH'],
            values['STOCH'] > values['STOCH_SIGNAL']
        ]
        return any(sell_signals)
