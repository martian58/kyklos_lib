from ..backtest import BacktestStrategy
from ..data import Data
import os
import logging
import datetime as dt


# Ensure the 'log' directory exists
if not os.path.exists('log'):
    os.makedirs('log')


bot_logger = logging.getLogger('bot_logger')
bot_logger.setLevel(logging.INFO)
bot_handler = logging.FileHandler('log/bot.log')
bot_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
bot_handler.setFormatter(bot_formatter)
bot_logger.addHandler(bot_handler)

class Bot:

    def __init__(self) -> None:
        self.api_key = os.getenv('BINANCE_API_KEY')
        self.api_secret = os.getenv('BINANCE_API_SECRET')

    def run(self):
        data_obj = Data(self.api_key, self.api_secret)
        start = dt.datetime(2024, 10, 30)
        end = dt.datetime.now()

        data = data_obj.get_data_start_end(symbol='BTCUSDT',interval='1h', start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"))

        print(data.close.iloc[-1])






    