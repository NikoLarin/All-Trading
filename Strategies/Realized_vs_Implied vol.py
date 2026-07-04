import os
from dotenv import load_dotenv
import math
import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime, timedelta
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
    '''A function that returns a pandas dataframe of daily close prices'''

    symbols = ",".join(tickers_list) # formatting for api URL

    url = f"https://data.alpaca.markets/v2/stocks/bars?symbols={symbols}&timeframe=1D&start=2025-07-04&limit=10000&adjustment=raw&feed=sip&sort=desc"

    response = requests.get(url, headers=get_headers())
    response.raise_for_status() # raise for status will return an error code if requests fail
    data = response.json() # the close price dats is stored in data

    current_price_list = [] 
    closes_list = []
    for ticker in tickers_list: # for every ticker we're using
        bars = data["bars"].get(ticker, []) # get OHLC data for the current ticker
        closes = [bar["c"] for bar in bars] # index into the close prices for each day
        closes_list.append(closes) 
        current_price_list.append(closes[0])

    return pd.DataFrame(closes_list, index=tickers_list)

def get_historical_volatility(closes_df):
    """Calculate historical volatility from list of closes."""
    daily_returns = closes_df.pct_change(axis=1)

    # 2. Calculate the standard deviation across the columns for each row
    # (We drop the first column '0' because pct_change makes it NaN)
    historical_volatility = daily_returns.std(axis=1) * np.sqrt(365)
    
    recent_price = closes_df[0]
    df = pd.DataFrame(recent_price)
    df["HV"]=historical_volatility.round(4)
    # 3. View your volatilities rounded nicely
    return df

def get_implied_vol(tickers_list :list, recent_price :float, date :str):
    '''A fucntion to call the alpaca api to get a list of options codes <= the current price (puts only)
        The function specifically parses the implied volatility of the at the money option.
    '''
    
    tickers_and_price = list(zip(tickers_list, recent_price)) #format [[ticker, current_price],[ticker_current_price]]
    at_the_money_iv_list = []
    for ticker_data in (tickers_and_price):
    
        url = f"https://data.alpaca.markets/v1beta1/options/snapshots/{ticker_data[0]}?feed=opra&limit=1000&type=put&strike_price_lte={ticker_data[1]}&expiration_date={date}"

        response = requests.get(url, headers=get_headers())
        response = response.json()
        allCodes = sorted(response['snapshots'].keys()) # save the options codes
        
        try:
            at_the_money_option_code = allCodes[-1] # get last option code in json format : SPY260717P00635000
        except IndexError:
            at_the_money_iv_list.append(0) # This happens if the expiry for the option is unavailable
            continue
        at_the_money_iv = response['snapshots'][at_the_money_option_code]['impliedVolatility'] # index at the money option iv

        at_the_money_iv_list.append(at_the_money_iv)

        
    return pd.DataFrame(at_the_money_iv_list, columns=["IV"], index=tickers_list)

if __name__ == "__main__":
    tickers_list = ["SPY", "QQQ", "AAPL", "TSLA", "NVDA", "MU", "INTC", "PLTR", "MSTR", 
                    "AMZN", "MSFT", "META", "HOOD", "IREN", "AMD", "SOFI", "GOOG"]

    dte = 6
    expiration_date = (timedelta(days=dte) + datetime.now())

    historical_volatility = get_historical_volatility(get_historical_closes(tickers_list)) # Gives us a dataframe with stock price and HV indexed by ticker
    implied_volatility = (get_implied_vol(tickers_list, historical_volatility[0], expiration_date.strftime("%Y-%m-%d"))) # Implied volatility by ticker in a dataframe 
    
    '''This section builds our clean dataframe containing tickers with an 
    implied volatility that is at least 10% larger than historical volatility'''
    final_df = pd.DataFrame(data=historical_volatility)

    final_df["IV"] = implied_volatility
    final_df.rename(columns={0: 'Price'}, inplace=True)
    final_df["Difference"] = (final_df["IV"] / final_df["HV"]) - 1 
    final_df = final_df[final_df["Difference"] > 0.1] # filter rows where (iv / hv) - 1 < .10

    final_df["HV Expected"] = final_df["Price"] * math.sqrt(dte / 365) * final_df["HV"] # Stock price * sqrt(dte/365) * HV
    final_df["IV Expected"] = final_df["Price"] * math.sqrt(dte / 365) * final_df["IV"] # Stock price * sqrt(dte/365) * IV
    
    print(final_df)

