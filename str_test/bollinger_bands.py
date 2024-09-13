from kyklos.api import BinanceAPI
import pandas as pd
import ta
import time
import datetime
from binance.enums import ORDER_TYPE_MARKET, SIDE_BUY, SIDE_SELL

class BollingerBandsStrategy:

    def __init__(self):
        self.api = BinanceAPI()
        self.green = "\033[1;32m"
        self.red = "\033[1;31m"
        self.reset = "\033[0m"

        self.status = 'hold'
        self.symbol = "BTCUSDT"

        self.bought_at = ''
        self.buy_fee = ''

    def get_latest_1minute_data(self):
        # Fetch the latest 1-hour of 1-minute candlestick data
        klines = self.api.get_historical_data(
            "BTCUSDT",
            self.api.client.KLINE_INTERVAL_1MINUTE,
            "1 hour"
        )
        df = pd.DataFrame(klines, columns=[
            'open', 'high', 'low', 'close', 'volume'
        ])
        df['close'] = df['close'].astype(float)
        return df

    def calculate_fee(self, trade_price):
        return trade_price / 1000

    def calculate_bollinger_bands(self, df, window=20, std_dev=2):
        # Calculate the moving average and the standard deviation
        df['sma'] = df['close'].rolling(window=window).mean()
        df['stddev'] = df['close'].rolling(window=window).std()
        # Calculate the upper and lower Bollinger Bands
        df['upper_band'] = df['sma'] + (std_dev * df['stddev'])
        df['lower_band'] = df['sma'] - (std_dev * df['stddev'])
        return df

    def analyze_bollinger_bands(self, df):
        latest_price = df['close'].iloc[-1]
        upper_band = df['upper_band'].iloc[-1]
        lower_band = df['lower_band'].iloc[-1]
        current_time = datetime.datetime.now().strftime("%H:%M:%S")

        if latest_price < lower_band:
            # Buy signal: Price is below the lower Bollinger Band (Oversold)
            print(f"\n{self.green}{current_time}{self.reset}: Price {latest_price} is below the lower Bollinger Band ({lower_band}). BUY signal!")
            return "BUY"
        elif latest_price > upper_band:
            # Sell signal: Price is above the upper Bollinger Band (Overbought)
            print(f"\n{self.red}{current_time}{self.reset}: Price {latest_price} is above the upper Bollinger Band ({upper_band}). SELL signal!")
            return "SELL"
        else:
            # Hold: Price is between the bands
            print(f"\n{self.green}{current_time}{self.reset}: Price {latest_price} is within the Bollinger Bands range. HOLD.")
            return "HOLD"

    def main(self):
        print("Monitoring Bollinger Bands every minute...")

        while True:
            df = self.get_latest_1minute_data()
            df = self.calculate_bollinger_bands(df)

            if not df.empty:
                action = self.analyze_bollinger_bands(df)

                if action == "SELL":
                    free_balances = self.api.get_free_balances()
                    free_btc = free_balances.get("BTC", 0)

                    if (self.status == "bought" or self.status == "hold") and free_btc > 0:
                        tradable_btc = "{:.5f}".format(free_btc)[:7] 
                        self.api.place_order("BTCUSDT", SIDE_SELL, tradable_btc)
                        print(f"\n\n{self.red}SOLDDDDDD{self.reset}")
                        self.status = "sold"
                    else:
                        print(f"\nStatus is already {self.red}SOLD{self.reset}")

                if action == "BUY":
                    free_balances = self.api.get_free_balances()
                    free_usdt = free_balances.get("USDT", 0)

                    if self.status == "sold" or self.status == "hold":
                        value_in_usd = self.api.get_crypto_price_in_usd("BTC")
                        tradable_btc = float(free_usdt) / float(value_in_usd)
                        str_tradable_btc = "{:.5f}".format(tradable_btc)[:7]

                        self.api.place_order("BTCUSDT", SIDE_BUY, str_tradable_btc)
                        print(f"\n\n{self.green}BOUGHTTTT{self.reset}")
                        self.status = "bought"
                    else:
                        print(f"\nStatus is already {self.green}BOUGHTTT{self.reset}")

            # Wait for 1 minute before fetching new data
            time.sleep(60)

if __name__ == '__main__':
    bot = BollingerBandsStrategy()
    bot.main()
