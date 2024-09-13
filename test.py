from kyklos.api import BinanceAPI
import pandas as pd
import ta
import time
import datetime
from binance.enums import ORDER_TYPE_MARKET, SIDE_BUY, SIDE_SELL


class Test:

    def __init__(self):
        self.api = BinanceAPI()
        self.green = "\033[1;32m"
        self.reset = "\033[0m"

        self.status = 'hold'
        self.symbol = "BTCUSDT"

        self.bought_at = ''
        self.buy_fee = ''
        self.bought_ammount = ''

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


    def calculate_rsi(self, df):
        rsi = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
        df['rsi'] = rsi
        return df

    def analyze_rsi_trend(self, df):
        # Extract the last 2 RSI values
        latest_rsi = df['rsi'].iloc[-1]
        previous_rsi = df['rsi'].iloc[-2]
        previous2_rsi = df['rsi'].iloc[-3]
        previous3_rsi = df['rsi'].iloc[-4]
        current_time = datetime.datetime.now().strftime("%H:%M:%S")

        if latest_rsi > 70:
            # If RSI is overbought, wait for it to decrease to signal a sell

            # if latest_rsi > previous_rsi > previous2_rsi:
            #     print(f"\n{self.green}{current_time}{self.reset}:RSI above 70, *Increasing 3*, HOLD")

            if latest_rsi > previous_rsi:
                print(f"\n{self.green}{current_time}{self.reset}:RSI above 70, *Increasing 2*, HOLD")

            elif latest_rsi < previous_rsi:
                print(f"\n{self.green}{current_time}{self.reset}:RSI above 70, *Decresing 2*, SELL")
                return "SELL"
                
            else:
                print(f"\n{self.green}{current_time}{self.reset}:RSI *ABOVE 70*, SELL")
                return "SELL"
        
        elif latest_rsi < 30:
            # If RSI is oversold, wait for it to increase to signal a buy
            if latest_rsi < previous_rsi < previous2_rsi < previous3_rsi:
                print(f"\n{self.green}{current_time}{self.reset}:RSI below 30, *Decresing* 4, HOLD")

            elif latest_rsi < previous_rsi < previous2_rsi:
                print(f"\n{self.green}{current_time}{self.reset}:RSI below 30, *Decresing* 3, HOLD")
            
            elif latest_rsi < previous_rsi:
                print(f"\n{self.green}{current_time}{self.reset}:RSI below 30, *Decresing* 2, HOLD")

            elif latest_rsi > previous_rsi:
                print(f"\n{self.green}{current_time}{self.reset}:RSI below 30 *Increasing 2*, BUY") 
                return "BUY"
            else:

                print(f"\n{self.green}{current_time}{self.reset}:RSI *BELOW 30*, BUY")
                return "BUY"


        else:
            # RSI is between 30 and 70, analyze trend
            if latest_rsi > previous_rsi:
                print(f"\n{self.green}{current_time}{self.reset}: RSI is rising, possible upward trend, HOLD")
                return "HOLD"
            else:
                print(f"\n{self.green}{current_time}{self.reset}: RSI is falling, possible downward trend, HOLD")
                return "HOLD"
        
        return "HOLD"

    def main(self):
        # Continuous monitoring loop
        print("Monitoring RSI every minute...")

        while True:
            df = self.get_latest_1minute_data()
            df = self.calculate_rsi(df)


            # Drop NaN rows (first 14 rows will be NaN due to RSI window size)
            df = df.dropna(subset=['rsi'])

            if not df.empty:
                action = "BUY"

                if action == "SELL":
                    free_balances = self.api.get_free_balances()
                    free_usdt = 0
                    free_btc = 0

                    for key, value in free_balances.items():
                        if key == "USDT":
                            # print(f"{key}: {value}")
                            free_usdt = float(value)
                        elif key == "BTC":
                            free_btc = float(value)

                    print(free_btc)
                    print(free_usdt)
                    print(free_balances)

                    if (self.status == "bought" or self.status == "hold") and free_btc != 0:
                        value_in_usd = self.api.get_crypto_price_in_usd("BTC")
                        str_tradible_btc = "{:.5f}".format(free_btc)[:7] 
                        fee = (float(str_tradible_btc)*float(value_in_usd)) / 1000

                        if (float(value_in_usd) - (float(self.bought_at)/float(self.bought_at))*float(self.bought_ammount) > (float(self.buy_fee) + float(fee))):
                            self.api.place_order("BTCUSDT", SIDE_SELL, str_tradible_btc )
                            print(f"\n\n{self.green}SOLDDDDDD{self.reset}")
                            self.status = "sold"
                        else:
                            print(f"\nStoped buy order, {self.green}NO PROFIT{self.reset}")

                    elif self.status == "sold":
                        print(f"\nStatus is alredy {self.green}SOLD{self.reset}")
                        
                if action == "BUY":
                    free_balances = self.api.get_free_balances()
                    free_usdt = 0
                    free_btc = 0
                    for key, value in free_balances.items():
                        if key == "USDT":
                            # print(f"{key}: {value}")
                            free_usdt = float(value)
                        elif key == "BTC":
                            free_btc = float(value)
                            
                    if (self.status == "sold" or self.status == "hold") and (free_usdt > 0):
                        value_in_usd = self.api.get_crypto_price_in_usd("BTC")
                        tradible_btc = float(free_usdt) / float(value_in_usd)
                        str_tradible_btc = "{:.5f}".format(tradible_btc)[:7]

                        print(type(str_tradible_btc))
                        print(str_tradible_btc)

                        self.api.place_order("BTCUSDT", SIDE_BUY, str_tradible_btc )

                        self.bought_ammount = str_tradible_btc
                        self.bought_at = value_in_usd
                        fee = (float(str_tradible_btc)*float(value_in_usd)) / 1000
                        self.buy_fee = str(fee)
                        print(f"\n\n{self.green}BOUGHTTTT{self.reset}")

                        self.status = "bought"
                    elif self.status == "bought":
                        print(f"\nStatus is alredy {self.green}BOUGHTTT{self.reset}")

                    

            # Wait for 1 minute before fetching new data
            time.sleep(30)

if __name__ == '__main__':
    bot = Test()
    bot.main()
