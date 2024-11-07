from ..backtest import BacktestStrategy
from ..data import Data
import os
import logging
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
        pass

    def run(self):
        data_obj = Data()
        data = data_obj.get_data_last_month_1hour(symbol='BTCUSDT')

        backtest_obj = BacktestStrategy(data=data)



        result = backtest_obj.backtest_boolinger_bands()

        print(result['trades'])
        # print(result['optimized_trades'])
        # print(result['trades'])


    