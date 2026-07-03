import os
from dotenv import load_dotenv
import math
import pandas as pd
import numpy as np
import requests
import json
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

def get_implied_vol(ticker :str,price , date :str):
    url = f"https://data.alpaca.markets/v1beta1/options/snapshots/{ticker}?feed=opra&limit=1000&type=put&strike_price_lte={price}&expiration_date={date}"
    
    response = requests.get(url, headers=get_headers())
    response = response.json()
    allCodes = sorted(response['snapshots'].keys())
    
    atm_option_code = allCodes[-1]
    
    atm_iv = response['snapshots'][atm_option_code]['impliedVolatility']

    return atm_iv


def get_historical_closes(tickers_list :list): 
            
    #Logic for creating/formatting URL ticker string
    url_string = ''
    
    for ticker in tickers_list:
        url_string += f'{ticker}%2C' # creates a string of ticker like this "AAPL%2CTSLA%2CGOOGL%2C"
    
    #stopping at [:-3] because the %2C format needs to be excluded on the last ticker
    url = f"https://data.alpaca.markets/v2/stocks/bars?symbols={url_string[:-3]}&timeframe=1D&start=2026-06-02&limit=1000&adjustment=raw&feed=sip&sort=desc"

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
    
    
    return closes_list, current_price_list

def get_implied_move(ticker_list :list):
    '''A function to get the move implied by IV '''
    # we need to format the option URL to get the ATM option 
    url = "https://data.alpaca.markets/v1beta1/options/snapshots?symbols=AAPL260202C00300000%2CAAPL240315C00625000&feed=opra&limit=100"



    #IV * Price * sqrt(trading days to exp/252)
    pass

def get_historical_volatility(close_data: list, tickers_list: list):
    """Calculate historical volatility from list of closes."""
    
    # Create one DataFrame with all tickers
    
    closes_df = pd.DataFrame(dict(zip(tickers_list, close_data)))

    # Calculate returns and volatility for all at once
    returns = closes_df.pct_change()
    volatility = (returns.std() * np.sqrt(252))
    
    return volatility.round(4)   # returns a pandas Series

tickers_list = ["SPY", "QQQ", "HOOD", "AMD", "NVDA", "PYPL", "ORCL", "AAPL", "RIOT", "META"]

historical_closes = get_historical_closes(tickers_list)
volatility_series = get_historical_volatility(historical_closes[0], tickers_list)

dte = math.sqrt(10 / 365)

df = pd.DataFrame(columns=["Tickers"],data=tickers_list)
df["Price"] = historical_closes[1]
df["HV"] = volatility_series.to_numpy()
df["Expected Move"] = round(df["HV"] * df["Price"] * dte, 2)
df["Upper"] = df["Price"] + df["Expected Move"]
df["Lower"] = df["Price"] - df["Expected Move"]

implied_volatility_list = []
for ticker in range(len(tickers_list)):
    implied_volatility_list.append(get_implied_vol(tickers_list[ticker], df["Price"].iloc[ticker], "2026-07-10"))

df["IV"] = implied_volatility_list
df["IV Expected Move"] = (dte * 1.2 * df["IV"] * df["Price"])
df["IV Upper"] = df["Price"] + df["IV Expected Move"]
df["IV Lower"] = df["Price"] - df["IV Expected Move"]
df["IV - HV"] = df["IV"] - df["HV"]
print(df)
