import time
import datetime
import pandas as pd
import ta
import logging
from binance.enums import ORDER_TYPE_MARKET, SIDE_BUY, SIDE_SELL
from kyklos.api import BinanceAPI

# Logging setup
logging.basicConfig(filename='trading_bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TradingBot:

    def __init__(self):
        self.api = BinanceAPI()
        self.symbol = "BTCUSDT"
        self.status = "hold"
        self.buy_price = 0
        self.buy_fee = 0
        self.green = "\033[1;32m"
        self.reset = "\033[0m"
        self.stop_loss = 0.97  # Example: Stop-loss set at 3% loss
        self.take_profit = 1.05  # Example: Take-profit set at 5% gain

    def fetch_candle_data(self):
        try:
            klines = self.api.get_historical_data(
                self.symbol,
                self.api.client.KLINE_INTERVAL_1MINUTE,
                "1 hour"
            )
            df = pd.DataFrame(klines, columns=['open', 'high', 'low', 'close', 'volume'])
            df['close'] = df['close'].astype(float)
            return df
        except Exception as e:
            logging.error(f"Error fetching candle data: {e}")
            return pd.DataFrame()

    def calculate_indicators(self, df):
        """ Calculate RSI and other indicators """
        df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
        return df.dropna()

    def should_buy(self, df):
        latest_rsi = df['rsi'].iloc[-1]
        return latest_rsi < 30  # RSI below 30 is typically a buy signal

    def should_sell(self, df):
        latest_rsi = df['rsi'].iloc[-1]
        return latest_rsi > 70  # RSI above 70 is typically a sell signal

    def place_order(self, side, quantity):
        try:
            self.api.place_order(self.symbol, side, quantity)
        except Exception as e:
            logging.error(f"Error placing order: {e}")

    def manage_position(self):
        """ Check if current position needs to be closed """
        current_price = self.api.get_crypto_price_in_usd("BTC")
        if self.status == "bought":
            if current_price <= self.buy_price * self.stop_loss:
                logging.info(f"Stop-loss triggered. Current Price: {current_price}, Buy Price: {self.buy_price}")
                self.place_order(SIDE_SELL, self.api.get_free_balances()["BTC"])
                self.status = "sold"
            elif current_price >= self.buy_price * self.take_profit:
                logging.info(f"Take-profit triggered. Current Price: {current_price}, Buy Price: {self.buy_price}")
                self.place_order(SIDE_SELL, self.api.get_free_balances()["BTC"])
                self.status = "sold"

    def trade_logic(self):
        """ Main trading logic: Buy and Sell based on RSI """
        df = self.fetch_candle_data()
        if df.empty:
            return

        df = self.calculate_indicators(df)
        action = "hold"

        # Buy logic
        if self.status == "sold" or self.status == "hold":
            if self.should_buy(df):
                free_usdt = self.api.get_free_balances().get("USDT", 0)
                current_price = self.api.get_crypto_price_in_usd("BTC")
                quantity = free_usdt / current_price
                self.place_order(SIDE_BUY, quantity)
                self.buy_price = current_price
                self.status = "bought"
                action = "buy"
                logging.info(f"BUY executed at {current_price}")

        # Sell logic
        elif self.status == "bought":
            if self.should_sell(df):
                free_btc = self.api.get_free_balances().get("BTC", 0)
                self.place_order(SIDE_SELL, free_btc)
                self.status = "sold"
                action = "sell"
                logging.info(f"SELL executed at {df['close'].iloc[-1]}")

        # Manage stop-loss/take-profit
        self.manage_position()

        logging.info(f"Action: {action}, Status: {self.status}")

    def start_trading(self):
        logging.info("Starting trading bot...")
        while True:
            try:
                self.trade_logic()
            except Exception as e:
                logging.error(f"Error in main loop: {e}")
            time.sleep(60)  # Fetch data and make decisions every 1 minute


if __name__ == "__main__":
    bot = TradingBot()
    bot.start_trading()
