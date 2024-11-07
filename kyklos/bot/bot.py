import pandas as pd
import time, os
import logging
from .data.api import BinanceAPI
from .strategy import TradingStrategy
from .utils import Utils
from binance.enums import ORDER_TYPE_MARKET, SIDE_BUY, SIDE_SELL

# Ensure the 'log' directory exists
if not os.path.exists('log'):
    os.makedirs('log')

# Set up logging for bot
bot_logger = logging.getLogger('bot_logger')
bot_logger.setLevel(logging.INFO)
bot_handler = logging.FileHandler('log/bot.log')
bot_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
bot_handler.setFormatter(bot_formatter)
bot_logger.addHandler(bot_handler)

class TradingBot:
    def __init__(self, default_trade_quantity, trade_interval='1h', history_duration='5 days'):
        self.default_trade_quantity = default_trade_quantity
        self.trade_interval = trade_interval
        self.history_duration = history_duration
        self.api = BinanceAPI()

    def analyze_markets(self):
        symbols = Utils.get_allowed_symbols()
        best_symbol = None
        best_signal = None
        
        for symbol in symbols:
            try:
                klines = self.api.get_historical_data(symbol, self.trade_interval, self.history_duration)
                data = self.prepare_data(klines)
                
                strategy = TradingStrategy(data)
                signal = strategy.apply_strategy()
                
                if signal in ['BUY', 'SELL']:
                    bot_logger.info(f"Trading signal found: {signal} for {symbol}")
                    best_symbol = symbol
                    best_signal = signal
                    break
            except Exception as e:
                bot_logger.error(f"Error analyzing {symbol}: {e}")
        
        return best_symbol, best_signal

    def prepare_data(self, klines):
        data = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ])
        data['close'] = data['close'].astype(float)
        data.drop(columns=[
            'volume', 'close_time', 'timestamp', 'quote_asset_volume',
            'number_of_trades', 'taker_buy_base_asset_volume',
            'taker_buy_quote_asset_volume', 'ignore'
        ], inplace=True)
        return data

    def get_trade_quantity(self, symbol):
        min_qty = self.api.get_min_quantity_for_order(symbol)
        if min_qty:
            trade_quantity = max(self.default_trade_quantity, min_qty)
            return trade_quantity
        else:
            bot_logger.error(f"Could not determine minimum quantity for {symbol}. Using default trade quantity.")
            return self.default_trade_quantity

    def execute_trade(self, symbol, signal):
        price_in_usd = self.api.get_crypto_price_in_usd(symbol)
        trade_quantity = self.get_trade_quantity(symbol)
        try:
            if signal == 'BUY':
                self.api.place_order(symbol, SIDE_BUY, trade_quantity)
                bot_logger.info(f"Executed BUY order for {symbol} with quantity {trade_quantity}")
            elif signal == 'SELL':
                self.api.place_order(symbol, SIDE_SELL, trade_quantity)
                bot_logger.info(f"Executed SELL order for {symbol} with quantity {trade_quantity}")
        except Exception as e:
            bot_logger.error(f"Error executing trade for {symbol}: {e}")

    def run(self):
        while True:
            symbol, signal = self.analyze_markets()
            if symbol and signal:
                print(f"Trading Signal: {signal} for {symbol}")
                self.execute_trade(symbol, signal)
            else:
                print("No trading signal found")
            
            time.sleep(3)  
