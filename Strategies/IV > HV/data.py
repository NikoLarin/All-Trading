import os
from dotenv import load_dotenv
import math
import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime, timedelta
from config import get_headers
load_dotenv()

# historical closes
def historical_closes(tickers):
    "Function get a years worth of closing data for each given ticker"
    
    tickers_url_format = ','.join(tickers)
    url = f"https://data.alpaca.markets/v2/stocks/bars?symbols={tickers_url_format}&timeframe=1D&start=2025-07-06&limit=10000&adjustment=raw&feed=sip&sort=asc"

    response = requests.get(url, headers=get_headers())
    response = response.json()

    ticker_dfs = []
    
    for ticker in tickers:
        if ticker in response['bars'] and response['bars'][ticker]:
            # Pull out timestamps ('t') and closing prices ('c')
            dates = [data['t'][:10] for data in response['bars'][ticker]] # Keeps 'YYYY-MM-DD'
            closes = [data['c'] for data in response['bars'][ticker]]
            
            # Create a clean single-ticker DataFrame indexed by date
            ticker_df = pd.DataFrame({ticker: closes}, index=pd.to_datetime(dates))
            ticker_dfs.append(ticker_df)

    # Outer join merges all tickers correctly on their dates, even if data is missing for one
    if ticker_dfs:
        final_df = pd.concat(ticker_dfs, axis=1, join='outer')
        return final_df
    else:
        return pd.DataFrame()


# IV which is pooled from the atm money option on an options chain
def get_implied_volatility(historical_closes, expiration_date: str):
    "Function gets at the money options IV"
    
    tickers = historical_closes.columns.to_list()
    current_stock_price = historical_closes.iloc[-1].to_list()
    options_codes_list = []
    iv_series = pd.Series(index=tickers)

    for i, ticker in enumerate(tickers):
        url = f"https://data.alpaca.markets/v1beta1/options/snapshots/{ticker}?feed=opra&limit=100&strike_price_lte={math.floor(current_stock_price[i])}&expiration_date={expiration_date}&type=put"

        response = requests.get(url, headers=get_headers())
        response = response.json()
        
        try: # this ensures there are options and fails safely if there isnt
            options_codes = sorted(response['snapshots'].keys())
            at_the_money_option_code = options_codes[-1]  # highest strike <= current price
            
            iv = response['snapshots'][at_the_money_option_code]['impliedVolatility']
            iv_series[ticker] = iv
            #historical_closes[f'{ticker}_IV'] = iv
        
        except (IndexError, KeyError, TypeError):
            iv_series[ticker] = 0
            #historical_closes[f'{ticker}_IV'] = 0.0
            continue
        
        options_codes_list.append(options_codes)

    return iv_series, options_codes_list

# all open account posititions
def all_positions():
    "Simple function to get all open portfolio positions"
    
    url = "https://paper-api.alpaca.markets/v2/positions"

    response = requests.get(url, headers=get_headers())
    response = response.json()

    return [option['symbol'] for option in response]
