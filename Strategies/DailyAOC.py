'''
SUMMARY:
This strategy is based on my own Average Open-Close Change indicator which takes a look back period to calculate the % change from the open to close of the amt of bars in that lookback period.
A credit spread is executed when an equities price goes above/below the AOC. This strategy can be classified as a mean reversion strategy and is executed currently using only 0-DTE options.

FUTURE UPDATES:
1. Allow for a list of [ticker] so we can use this on more than one name at a time.
2. Dynamic allocation: 'I want to use 5% of my portfolio for this strategy'.
3. Instead of executing at the market price, set a limit order at a more favorable fill.  
4. Bug fixes.
'''

import requests
import time
from datetime import date
from dateutil.relativedelta import relativedelta
from alpaca_tools import headers, open_stock_price, current_stock_price, aoc, BASE_URL

def aoc_strategy(ticker):
        while True:    
            hour = time.localtime() # current time
            while hour[3] > 9 or hour[3] < 16:
                today_aoc = aoc(ticker)
                stock_price = current_stock_price(ticker)
                
                today = str(date.today())
                today = today.replace('-', '')

                today_open = open_stock_price(ticker)
                highbar = today_open + today_open * today_aoc
                lowbar =  today_open - today_open * today_aoc

                if stock_price > highbar: # if price is higher than top AOC
                    otype = 'C'
                    strike = round(stock_price, 0)
                    long_leg = f'{ticker}{today[2:]}{otype}00{int(strike + 1)}000'
                
                elif stock_price < lowbar: #if price is lower than bottom AOC
                    otype = 'P'
                    strike = round(stock_price, 0)
                    long_leg = f'{ticker}{today[2:]}{otype}00{int(strike - 1)}000'
                
                else:
                     print(f'Highbar:{highbar} Lowbar: {lowbar}')
                     print("Waiting")
                     time.sleep(60)
                     continue
                
                short_leg = f'{ticker}{today[2:]}{otype}00{int(strike)}000'
                
                url = f'{BASE_URL}/orders'

                payload = { #creates the debit spread
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
            break # ends the loop once a trade is executed, only one trade a day.
            
print(aoc('SPY')) # just prints the AOC that was calculated
aoc_strategy('SPY') # runs strategy



