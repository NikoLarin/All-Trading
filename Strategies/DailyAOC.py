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
from alpaca_tools import headers, open_stock_price, current_stock_price

def aoc(ticker):
    '''
    this function pulls open and close data for 100 days and calculates the 
    average open to close change for one day   
    '''
    today = date.today()
    year_ago = today - relativedelta(years=1) # finds the date from a year ago today

    url = f"https://data.alpaca.markets/v2/stocks/bars?symbols={ticker}&timeframe=1D&start={year_ago}&limit=100&adjustment=raw&feed=sip&sort=asc"

    response  = requests.get(url, headers=headers())
    data = response.json()

    bars = data["bars"][ticker]

    abs_pct_changes = [] # creates list of pct changes from the loop

    for candle in bars: # find pct changes loop
        closeD = candle["c"]
        openD = candle["o"]

        if openD != 0: 
            abs_pct_changes.append(abs(((closeD - openD) / openD)))

    today_aoc = sum(abs_pct_changes) / len(abs_pct_changes)
    
    return today_aoc / 2 # returns todays AOC

def aoc_strategy(ticker):
        while True: # while called
            hour = time.localtime() # find the hour
            while hour[3] > 9 or hour[3] < 16: # if we are in market hours
                today_aoc = aoc(ticker) # call todays AOC
                stock_price = current_stock_price(ticker) #call my stock price function
                
                today = str(date.today())
                today = today.replace('-', '') #formatting

                today_open = open_stock_price(ticker)
                highbar = today_open + today_open * today_aoc # calculate low and high bar for AOC
                lowbar =  today_open - today_open * today_aoc


                if stock_price > highbar: # conditional) if above - SELL CALL SPREAD
                    otype = 'C'
                    strike = round(highbar, 0)
                    long_leg = f'{ticker}{today[2:]}{otype}00{int(strike + 1)}000'
                
                elif stock_price < lowbar: # conditional) if below - SELL PUT SPREAD
                    otype = 'P'
                    strike = round(lowbar, 0)
                    long_leg = f'{ticker}{today[2:]}{otype}00{int(strike - 1)}000'
                
                else:
                     print("Waiting") # while we arent above/below AOC print waiting 
                     time.sleep(60) # sleep for 60 seconds
                     continue # check again
                
                short_leg = f'{ticker}{today[2:]}{otype}00{int(strike)}000' # creates the options code for ATM option
                
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
                break # break the loop once a trade has been executed = ONLY 1 trade a day

aoc_strategy('SPY')

