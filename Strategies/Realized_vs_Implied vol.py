import os
from dotenv import load_dotenv
import math
import pandas as pd
import numpy as np
import requests
import json
from collections import namedtuple
load_dotenv()

def get_headers() -> dict:
    """Return Alpaca API headers from .env file."""
    
    api_key = os.getenv("APCA_API_KEY_ID")
    secret_key = os.getenv("APCA_API_SECRET_KEY")
    
    if not api_key or not secret_key:
        raise ValueError(
            "API keys not found! Check your .env file and make sure load_dotenv() is called."
        )
    
    return {
        "accept": "application/json",
        "APCA-API-KEY-ID": api_key,
        "APCA-API-SECRET-KEY": secret_key,
    }

def get_historical_closes(tickers_list :list): 
            
    symbols = ",".join(tickers_list) # formatting for api urll

    #stopping at [:-3] because the %2C format needs to be excluded on the last ticker
    url = f"https://data.alpaca.markets/v2/stocks/bars?symbols={symbols}&timeframe=1D&start=2026-06-02&limit=1000&adjustment=raw&feed=sip&sort=desc"

    response = requests.get(url, headers=get_headers())
    response.raise_for_status()
    data = response.json()

    current_price_list = []
    closes_list = []
    for ticker in tickers_list:
        bars = data["bars"].get(ticker, [])
        closes = [bar["c"] for bar in bars]
        closes_list.append(closes)
        current_price_list.append(closes[0])
    
    return pd.DataFrame(closes_list, index=tickers_list)

def get_historical_volatility(closes_df):
    """Calculate historical volatility from list of closes."""
    daily_returns = closes_df.pct_change(axis=1)

    # 2. Calculate the standard deviation across the columns for each row
    # (We drop the first column '0' because pct_change makes it NaN)
    historical_volatility = daily_returns.std(axis=1) * np.sqrt(252)
    
    recent_price = closes_df[0]
    df = pd.DataFrame(recent_price)
    df["HV"]=historical_volatility.round(4)
    # 3. View your volatilities rounded nicely
    return df

def get_implied_vol(tickers_list :list, recent_price :float, date :str):
    tickers_and_price = list(zip(tickers_list, recent_price))
    at_the_money_iv_list = []
    for ticker_data in (tickers_and_price):
    
        url = f"https://data.alpaca.markets/v1beta1/options/snapshots/{ticker_data[0]}?feed=opra&limit=1000&type=put&strike_price_lte={ticker_data[1]}&expiration_date={date}"

        response = requests.get(url, headers=get_headers())
        response = response.json()
        allCodes = sorted(response['snapshots'].keys())
        
        try:
            at_the_money_option_code = allCodes[-1] # get last option code in json format : SPY260717P00635000
        except IndexError:
            at_the_money_iv_list.append(0)
            continue
        at_the_money_iv = response['snapshots'][at_the_money_option_code]['impliedVolatility']

        at_the_money_iv_list.append(at_the_money_iv)

        
    return pd.DataFrame(at_the_money_iv_list, columns=["IV"], index=tickers_list)

tickers_list = ["SPY", "QQQ", "AAPL"]

historical_volatility = get_historical_volatility(get_historical_closes(tickers_list))
implied_volatility_list = (get_implied_vol(tickers_list, historical_volatility[0], "2026-07-15"))

final_df = pd.DataFrame(data=historical_volatility)

final_df["IV"] = implied_volatility_list
final_df.rename(columns={'0': 'Price'}, inplace=True)

print(final_df)
