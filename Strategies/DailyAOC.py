'''
SUMMARY:
This strategy is based on my own Average Open-Close Change indicator which takes a look back period to calculate the % change from the open to close of the amt of bars in that lookback period.
A credit spread is executed when an equities price goes above/below the AOC. This strategy can be classified as a mean reversion strategy and is executed currently using only 0-DTE options.

FUTURE UPDATES:
1. Dynamic allocation: 'I want to use 5% of my portfolio for this strategy'.
2. Instead of executing at the market price, set a limit order at a more favorable fill.  
3. Bug fixes.
'''

import requests
import time
from datetime import date
from dateutil.relativedelta import relativedelta
from alpaca_tools import headers, open_stock_price, current_stock_price, aoc

def aoc_strategy(ticker):
            for t in ticker:
                while True:    
                    hour = time.localtime()
                    while hour[3] > 9 or hour[3] < 16:
                        today_aoc = aoc(t)
                        stock_price = current_stock_price(t)
                        
                        today = str(date.today())
                        today = today.replace('-', '')

                        today_open = open_stock_price(t)
                        highbar = today_open + today_open * today_aoc
                        lowbar =  today_open - today_open * today_aoc


                        if stock_price > highbar:
                            otype = 'C'
                            strike = round(stock_price, 0)
                            long_leg = f'{ticker}{today[2:]}{otype}00{int(strike + 1)}000'
                        
                        elif stock_price < lowbar:
                            otype = 'P'
                            strike = round(stock_price, 0)
                            long_leg = f'{t}{today[2:]}{otype}00{int(strike - 1)}000'
                        
                        else:
                            print(f'Highbar:{highbar} Lowbar: {lowbar}')
                            print("Waiting")
                            time.sleep(60)
                            continue
                        
                        short_leg = f'{t}{today[2:]}{otype}00{int(strike)}000'
                        
                        url = "https://paper-api.alpaca.markets/v2/orders"

                        payload = {
                            "type": "market",
                            "time_in_force": "day",
                            "legs": [
                                {
                                    "side": "buy",
                                    "symbol": long_leg,
                                    "ratio_qty": "1"
                                },
                                {
                                    "side": "sell",
                                    "symbol": short_leg,
                                    "ratio_qty": "1"
                                }
                            ],
                            "order_class": "mleg",
                            "qty": "1"
                        }

                        response = requests.post(url, json=payload, headers=headers())

                        print(response.text)
                        break
                    break


ticker = ['SPY', 'QQQ']
for t in ticker:
    print(aoc(t))
aoc_strategy(ticker)

