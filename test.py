from kyklos.api import BinanceAPI
from kyklos.strategy import TradingStrategy
import pandas as pd
from binance.enums import ORDER_TYPE_MARKET, SIDE_BUY, SIDE_SELL



if __name__ == '__main__':
    api = BinanceAPI()

    min_value = api.get_min_notional_value('BTCUSDT')

    print(min_value)









    # Use a string representation with the correct precision
    # quantity = "{:.8f}".format(0.00001)  # Format the quantity to 8 decimal places

    # try:
    #     orders = api.client.create_order(
    #         symbol='BTCUSDT',
    #         side=SIDE_SELL,
    #         type=ORDER_TYPE_MARKET,
    #         quantity=quantity  # Pass quantity as a string
    #     )
    #     print(orders)
    # except Exception as e:
    #     print(f"Error: {e}")




# Create a list of trading symbols
symbols = [
    "BTCUSDT",
    "ETHUSDT",
    "BNBUSDT",
    "XRPUSDT",
    "DOTUSDT",
    "ADAUSDT",
    "SOLUSDT",
    "AVAXUSDT",
    "MATICUSDT",
    "LTCUSDT"
]

# # Write the symbols to a text file
# file_path = "allowed_symbols.txt"
# with open(file_path, "w") as file:
#     for symbol in symbols:
#         file.write(f"{symbol}\n")


