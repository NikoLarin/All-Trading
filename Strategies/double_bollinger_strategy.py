import pandas as pd
import time
from ta import add_all_ta_features
import requests
from ta.volatility import BollingerBands
from ta.utils import dropna
from alpaca_tools import get_ohlc, current_stock_price, headers, stock_order_mkt, bollinger_bands, BASE_URL

URL = f'{BASE_URL}/orders'

ticker = input("Enter the ticker to trade(ALL CAPS): ")
amt = int(input("Input the # of shares: "))
trading = True

while trading == True:
    hour = time.localtime()
    while (hour[3] >= 9 and hour[4] >= 30)  or hour[3] < 16:
        
        t = [60, 15] # bollinger look backs
        bb = []
        for look_back in t:    
            bb.append(bollinger_bands(look_back))

        (bb_h_60, bb_m_60, bb_l_60) = bb[0]
        (bb_h_15, bb_m_15, bb_l_15) = bb[1]

        highband1 = bb_h_60
        highband2 = bb_h_15

        midband1 = bb_m_60

        lowband1 = bb_l_60
        lowband2 = bb_l_15

        price = current_stock_price('SPY') # get spy stock price 

        print(f'Upper: {highband1}\nPrice: {price}\nLower: {lowband1})')
        time.sleep(1) # for safety no spam...

#----------------SHORT ORDER CONDITION----------------#
        if price > highband1 and price > highband2:
            short = True
            response = requests.post(URL, json=stock_order_mkt(ticker=ticker, side='sell', amt=amt), headers=headers()) # order submission
            print('ORDER SENT')
            while short == True:
                if price == midband1:# take profit
                    response = requests.post(URL, json=stock_order_mkt(ticker, side='buy', amt=amt), headers=headers()) #take profit order submission
                    short = False
                    print('FLATTEN ORDER SENT')
        
#----------------LONG ORDER CONDITION----------------#
        elif price < lowband1 and price < lowband2: 
            long = True
            response = requests.post(URL, json=stock_order_mkt(ticker=ticker, side='buy',amt=amt), headers=headers()) # order submission
            print('ORDER SENT')
            while long == True:
                if price == midband1: # take profit
                    response = requests.post(URL, json=stock_order_mkt(ticker=ticker, side='sell',amt=amt), headers=headers()) #take profit order submission
                    long = False
                    print('FLATTEN ORDER SENT')


#----------------RESTART LOOP IF NO CONDITIONS MET----------------#        
        else:
            time.sleep(60)
            continue


    print('Restarting loop: Searching for trade :)')

