import os
from binance.client import Client
from binance.enums import ORDER_TYPE_MARKET, SIDE_BUY, SIDE_SELL
from dotenv import load_dotenv
import pandas as pd
from .utils import Utils

load_dotenv()

class BinanceAPI:   
    def __init__(self):
        self.api_key = os.getenv('BINANCE_API_KEY')
        self.api_secret = os.getenv('BINANCE_API_SECRET')
        self.client = Client(self.api_key, self.api_secret)

    def get_historical_data(self, symbol: str, interval: str, lookback: str) -> pd.DataFrame:
        """_summary_

        Args:
            symbol (str): Symbol of the cryptocurency pair.
            interval (str): The interval to get the data.
            lookback (str): The lookback time. e.g "5 days"

        Returns:
            pd.DataFrame: Returns the historical data.
        """        
        try:
            klines = self.client.get_historical_klines(symbol, interval, lookback)
            
            if not klines:
                print(f"No data returned for {symbol}.")
                return pd.DataFrame()  
            
            df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            df = df[['open', 'high', 'low', 'close', 'volume']]
            df = df.astype(float)  # Ensure data is of type float
            
            # print(f"Data for {symbol} fetched successfully.")
            return df

        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()  


    def place_order(self, symbol: str, side: str, quantity: str):
        """_summary_

        Args:
            symbol (str): Symbol of the cryptocurency pair.
            side (str): "BUY" or "SELL"
            quantity (str): Quantity for action in "str" format.

        Returns:
            _type_: _description_
        """        
        try:
            order = self.client.create_test_order(
                symbol=symbol,
                side=side,
                type=ORDER_TYPE_MARKET,
                quantity=quantity
            )
            return order
        except Exception as e:
            print(f"Error placing order: {e}")
            return None

    
    def get_all_symbols(self):
        exchange_info = self.client.get_exchange_info()
        symbols = [s['symbol'] for s in exchange_info['symbols'] if s['quoteAsset'] == 'USDT']
        return symbols
    
    def get_min_quantity_for_order(self, symbol):
        try:
            exchange_info = self.client.get_exchange_info()

            # Find the symbol in the exchange info
            for sym in exchange_info['symbols']:
                if sym['symbol'] == symbol:
                    # Find LOT_SIZE filter
                    lot_size_filter = next((f for f in sym['filters'] if f['filterType'] == 'LOT_SIZE'), None)
                    
                    if lot_size_filter:
                        # Return minQty
                        return lot_size_filter['minQty']
                    else:
                        return 'LOT_SIZE filter not found for this symbol'

            return 'Symbol not found'

        except Exception as e:
            print(f"An error occurred: {e}")
            return None
        
    def get_min_notional_value(self, symbol):
        try:
            exchange_info = self.client.get_exchange_info()
            
            symbol_info = None
            for s in exchange_info['symbols']:
                if s['symbol'] == symbol:
                    symbol_info = s
                    break

            if symbol_info:
                # Loop through the filters to find the MIN_NOTIONAL filter
                for filt in symbol_info['filters']:
                    if filt['filterType'] == 'NOTIONAL':
                        min_notional_value = float(filt['minNotional'])
                        return min_notional_value
            else:
                print(f"Symbol {symbol} not found.")
                return None

        except Exception as e:
            print(f"Error fetching min notional value for {symbol}: {e}")
            return None


    def get_non_zero_balances(self):
        try:
            account_info = self.client.get_account()

            non_zero_balances = {}

            for balance in account_info['balances']:
                free = float(balance['free'])
                locked = float(balance['locked'])

                # Check if either free or locked is non-zero
                if free > 0 or locked > 0:
                    total_balance = free + locked
                    non_zero_balances[balance['asset']] = format(total_balance, '.8f')

            return non_zero_balances

        except Exception as e:
            print(f"An error occurred: {e}")
            return {}
        
    def get_free_balances(self):
        try:
            account_info = self.client.get_account()

            free_balances = {}

            for balance in account_info['balances']:
                free = float(balance['free'])

                if free > 0:
                    free_balances[balance['asset']] = f"{free:.8f}"

            return free_balances

        except Exception as e:
            print(f"An error occurred: {e}")
            return {}
        
    def get_crypto_price_in_usd(self, symbol: str) -> float:
        """_summary_

        Args:
            symbol (str): Symbol for the crypto pair.

        Returns:
            float: Returns the price.
        """        
        ticker = self.client.get_symbol_ticker(symbol=f"{symbol}USDT") 
        return float(ticker['price']) if ticker else None




    """
    The rest of the code:
        Print functions.
    
    """

    def print_account_info(self):
        try:
            account_info = self.client.get_account()

            # Print formatted account info
            print("\n\033[1;30m----- Account Info -----\033[0m")
            print(f"Commission Rates: Maker: {float(account_info['commissionRates']['maker']):.6f}, "
                f"Taker: {float(account_info['commissionRates']['taker']):.6f}, "
                f"Buyer: {float(account_info['commissionRates']['buyer']):.6f}, "
                f"Seller: {float(account_info['commissionRates']['seller']):.6f}")
            print(f"Can Trade: {'Yes' if account_info['canTrade'] else 'No'}")
            print(f"Can Withdraw: {'Yes' if account_info['canWithdraw'] else 'No'}")
            print(f"Can Deposit: {'Yes' if account_info['canDeposit'] else 'No'}")

            print("\n\033[1;30m----- Balances -----\033[0m")
            for balance in account_info['balances']:
                free = float(balance['free'])
                locked = float(balance['locked'])

                if free > 0 or locked > 0:
                    print(f"Asset: {balance['asset']} | Free: {free:.8f} | Locked: {locked:.8f}\n")

        except Exception as e:
            print(f"An error occurred: {e}")
            return None
    
    def print_all_min_prices(self):
        try:
            exchange_info = self.client.get_exchange_info()

            # List of symbols to find min prices for
            symbols = Utils.get_allowed_symbols()

            # Create dictionaries to hold min prices and min quantities
            min_prices = {}
            min_quantities = {}

            # Iterate through each symbol
            for symbol in exchange_info['symbols']:
                if symbol['symbol'] in symbols:
                    # Find PRICE_FILTER filter
                    price_filter = next((f for f in symbol['filters'] if f['filterType'] == 'PRICE_FILTER'), None)
                    # Find LOT_SIZE filter
                    lot_size_filter = next((f for f in symbol['filters'] if f['filterType'] == 'LOT_SIZE'), None)

                    if price_filter:
                        # Extract minPrice
                        min_price = price_filter['minPrice']
                        min_prices[symbol['symbol']] = min_price
                    
                    if lot_size_filter:
                        # Extract minQty
                        min_qty = lot_size_filter['minQty']
                        min_quantities[symbol['symbol']] = min_qty

            # Print min prices and min quantities
            print()
            for symbol in symbols:
                min_price = min_prices.get(symbol, 'N/A')
                min_qty = min_quantities.get(symbol, 'N/A')
                print(f"{symbol}: Min Price = {min_price}, Min Qty = {min_qty}")
            print()

        except Exception as e:
            print(f"An error occurred: {e}")
