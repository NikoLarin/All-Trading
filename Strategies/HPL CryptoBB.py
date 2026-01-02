'''
Summary:
A bollinger bands strategy built for hyperliquid perps. 

Future Fixes:
1. Abstract and clean up the code
'''

import ccxt
import pandas as pd
from alpaca_tools import bollinger_bands
from ta.utils import dropna
from ta.volatility import BollingerBands
import time

dex = ccxt.hyperliquid({
    "walletAddress": "YOURwalletADDRESS :)",
    "privateKey": "YOURprivateKEY :)",
    })
symbol = 'SOL/USDC:USDC'
dex.set_leverage(20, symbol)  # ← ADD THIS LINE (example: 10x)

def bollinger_bands(t):    
    df = pd.DataFrame(ohlc)
    df = df.rename(columns={  # names columns
                'o': 'Open',
                'h': 'High',
                'l': 'Low',
                'c': 'Close',
                't': 'Date'
            }
    )
    df = dropna(df)
    indicator_bb = BollingerBands(close=df[3], window=t, window_dev=2)

    # Add Bollinger Bands features
    df['bb_bbm'] = indicator_bb.bollinger_mavg()
    df['bb_bbh'] = indicator_bb.bollinger_hband()
    df['bb_bbl'] = indicator_bb.bollinger_lband()

    # Add Bollinger Band high indicator
    df['bb_bbhi'] = indicator_bb.bollinger_hband_indicator()

    # Add Bollinger Band low indicator
    df['bb_bbli'] = indicator_bb.bollinger_lband_indicator()

    return df['bb_bbh'].iloc[-2], df['bb_bbm'].iloc[-2], df['bb_bbl'].iloc[-2]

trading = True
while trading == True:
    symbol = 'SOL/USDC:USDC'
    ohlc = dex.fetch_ohlcv('SOL/USDC:USDC', '1m', limit=500)
    curprice = float(dex.fetch_ticker(symbol)["last"])
    t = [60, 15]
    data = []
    for i in t:
        data.append(bollinger_bands(i))

    hsBand = data[0][0]
    hfBand = data[1][2]

    msBand = data[0][1]

    lsBand = data[0][2]
    lfBand = data[1][2]

    curprice = float(dex.fetch_ticker(symbol)["last"])
    if curprice > hsBand and curprice > hfBand:
        short = True
        order = dex.create_order("SOL/USDC:USDC", "limit", "sell", 0.1, float(dex.fetch_ticker(symbol)["last"]))
        print("Short Trade Executed")

        while short == True:
            time.sleep(5)            
            ohlc = dex.fetch_ohlcv('SOL/USDC:USDC', '1m', limit=500)
            t = [60, 15]
            data = []
            for i in t:
                data.append(bollinger_bands(i))

            msBand = data[0][1]
            print(f'Your take profit is: {msBand}')
            if curprice <= msBand:
                dex.create_order("SOL/USDC:USDC", "market", "buy", 0.1, , params={"reduceOnly":True})
                short = False
                continue

    if curprice < lfBand and curprice < lsBand:
        long = True
        order = dex.create_order("SOL/USDC:USDC", "limit", "buy", 0.1, float(dex.fetch_ticker(symbol)["last"]))
        print("Long Trade Executed")
        while long == True:
            time.sleep(5)
            ohlc = dex.fetch_ohlcv('SOL/USDC:USDC', '1m', limit=500)
            t = [60, 15]
            data = []
            for i in t:
                data.append(bollinger_bands(i))
            
            msBand = data[0][1]
            print(f'Your take profit is: {msBand}')
            curprice = float(dex.fetch_ticker(symbol)["last"])
            if curprice >= msBand:
                dex.create_order("SOL/USDC:USDC", "market", "sell", 0.1, float(dex.fetch_ticker(symbol)["last"]), params={"reduceOnly":True})
                long = False
                continue
    else:
        print(f'HighBand: {hsBand}\nPrice: {curprice}\nLowBand: {lsBand}')
        time.sleep(10)
        print("Searching for trades")
