from kyklos.api import BinanceAPI
import pandas as pd
import ta
import time
import datetime

class Test:

    def __init__(self):
        self.api = BinanceAPI()
        self.green = "\033[1;32m"
        self.reset = "\033[0m"

        self.status = 'hold'

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
            if latest_rsi > previous_rsi > previous2_rsi > previous3_rsi:
                print(f"\n{self.green}{current_time}{self.reset}:RSI above 70, *Increasing 4*, HOLD")

            elif latest_rsi > previous_rsi > previous2_rsi:
                print(f"\n{current_time}:RSI above 70, *Increasing 3*, HOLD")

            elif latest_rsi > previous_rsi:
                print(f"\n{current_time}:RSI above 70, *Increasing 2*, HOLD")

            elif latest_rsi < previous_rsi:
                print(f"\n{current_time}:RSI above 70, *Decresing 2*, HOLD")

            elif latest_rsi < previous_rsi < previous2_rsi:
                print(f"\n{current_time}:RSI above 70, *Decresing 3*, HOLD")

            elif latest_rsi < previous_rsi < previous2_rsi < previous3_rsi:
                print(f"\n{current_time}:RSI *Decresing* 4, SELL")
                return "SELL"
            else:
                print(f"\n{current_time}:RSI *ABOVE 70*, SELL")
                return "SELL"
        
        elif latest_rsi < 30:
            # If RSI is oversold, wait for it to increase to signal a buy
            if latest_rsi < previous_rsi < previous2_rsi < previous3_rsi:
                print(f"\n{current_time}:RSI below 30, *Decresing* 4, HOLD")

            elif latest_rsi < previous_rsi < previous2_rsi:
                print(f"\n{current_time}:RSI below 30, *Decresing* 3, HOLD")
            
            elif latest_rsi < previous_rsi:
                print(f"\n{current_time}:RSI below 30, *Decresing* 2, HOLD")

            elif latest_rsi > previous_rsi:
                print(f"\n{current_time}:RSI below 30 *Increasing 2*, HOLD")

            elif latest_rsi > previous_rsi > previous2_rsi:
                print(f"\n{current_time}:RSI above 70, *Increasing 3*, HOLD")

            elif latest_rsi > previous_rsi > previous2_rsi > previous3_rsi:
                print(f"\n{current_time}:RSI above 70, *Increasing 4*, BUY")
            else:

                print(f"\n{current_time}:RSI *BELOW 30*, BUY")
                return "BUY"


        else:
            # RSI is between 30 and 70, analyze trend
            if latest_rsi > previous_rsi:
                print(f"\n{self.green}{current_time}{self.reset}: RSI is rising, possible upward trend, HOLD")
                return "HOLD"
            else:
                print(f"\n{current_time}: RSI is falling, possible downward trend, HOLD")
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
                action = self.analyze_rsi_trend(df)

                if action == "SELL" or action == "BUY":
                    break  # Exit loop on sell or buy signal

            # Wait for 1 minute before fetching new data
            time.sleep(60)

if __name__ == '__main__':
    bot = Test()
    bot.main()
