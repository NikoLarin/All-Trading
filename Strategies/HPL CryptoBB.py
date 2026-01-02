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
        curprice = float(dex.fetch_ticker(symbol)["last"])
        symbol = "SOL/USDC:USDC"
        order_type = "limit"
        side = "sell"
        amount = 0.1
        price = curprice
        short = True
        order = dex.create_order(symbol, order_type, side, amount, price=price)
        print("Short Trade Executed")

        while short == True:
            time.sleep(5)
            curprice = float(dex.fetch_ticker(symbol)["last"])
            ohlc = dex.fetch_ohlcv('SOL/USDC:USDC', '1m', limit=500)
            curprice = float(dex.fetch_ticker(symbol)["last"])
            t = [60, 15]
            data = []
            for i in t:
                data.append(bollinger_bands(i))

            msBand = data[0][1]
            print(msBand)
            if curprice <= msBand:
                symbol = "SOL/USDC:USDC"
                order_type = "market"
                side = "buy"
                amount = 0.1
                price = float(dex.fetch_ticker(symbol)["last"])

                dex.create_order(symbol, order_type, side, amount, price=price, params={"reduceOnly":True})
                short = False
                continue

    if curprice < lfBand and curprice < lsBand:
        curprice = float(dex.fetch_ticker(symbol)["last"])
        symbol = "SOL/USDC:USDC"
        order_type = "limit"
        side = "buy"
        amount = 0.1
        price = curprice
        long = True
        order = dex.create_order(symbol, order_type, side, amount, price=price)
        print("Long Trade Executed")
        while long == True:
            time.sleep(5)
            ohlc = dex.fetch_ohlcv('SOL/USDC:USDC', '1m', limit=500)
            curprice = float(dex.fetch_ticker(symbol)["last"])
            t = [60, 15]
            data = []
            for i in t:
                data.append(bollinger_bands(i))
            
            msBand = data[0][1]
            print(msBand)
            curprice = float(dex.fetch_ticker(symbol)["last"])
            if curprice >= msBand:
                symbol = "SOL/USDC:USDC"
                order_type = "market"
                side = "sell"
                amount = 0.1 # doesnt dynamically CLOSE BE CAREFUL
                price = float(dex.fetch_ticker(symbol)["last"])

                dex.create_order(symbol, order_type, side, amount, price=price, params={"reduceOnly":True})
                long = False
                continue
    
    else:
        time.sleep(10)
        print("Searching for trades")
        print(f'HighBand: {hsBand}\nPrice: {curprice}\nLowBand: {lsBand}')
