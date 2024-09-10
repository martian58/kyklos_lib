import pandas as pd
import ta
from kyklos import BinanceAPI

# Sample data: create a DataFrame with a 'close' price series
data = {
    'close': [44.0, 45.0, 46.0, 47.0, 46.5, 45.5, 44.5, 43.5, 44.0, 45.0, 46.5, 47.5, 50.0, 55.5, 60.0]
}
df = pd.DataFrame(data)

# Calculate RSI using the ta library (default period is 14)
rsi = ta.momentum.RSIIndicator(df['close'], window=14)
df['rsi'] = rsi.rsi()
df.dropna(subset=['rsi'], inplace=True)


# Show the data with RSI values
print(df)



    # def get_2month_1day_data(self):

    #     klines = self.api.get_historical_data(
    #     "BTCUSDT", 
    #     self.api.client.KLINE_INTERVAL_1DAY, 
    #     "60 day"
    #     )
    #     df = pd.DataFrame(klines, columns=[
    #         'open', 'high', 'low', 'close', 'volume'
    #     ])

    #     return df
    
    # def get_2day_1hour_data(self):
    #     klines = self.api.get_historical_data(
    #     "BTCUSDT", 
    #     self.api.client.KLINE_INTERVAL_1HOUR, 
    #     "2 day"
    #     )
    #     df = pd.DataFrame(klines, columns=[
    #         'open', 'high', 'low', 'close', 'volume'
    #     ])

    #     return df
    
    # def get_1day_15minute(self):
    #     klines = self.api.get_historical_data(
    #     "BTCUSDT", 
    #     self.api.client.KLINE_INTERVAL_15MINUTE, 
    #     "1 day"
    #     )
    #     df = pd.DataFrame(klines, columns=[
    #         'open', 'high', 'low', 'close', 'volume'
    #     ])

    #     return df