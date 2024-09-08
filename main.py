from kyklos import TradingBot

if __name__ == '__main__':
    default_trade_quantity = '0.0001'  # Set your default trade quantity
    bot = TradingBot(default_trade_quantity)
    bot.run()