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
    
    api_key = ""
    secret_key = ""
    
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
    options_codes = []
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
        options_codes.append(allCodes)
        
    return pd.DataFrame(at_the_money_iv_list, columns=["IV"], index=tickers_list), options_codes


    # 5. Set the final option code and return
    matched_df["put code"] = matched_df["real_code"]
    return matched_df

if __name__ == "__main__":
    # --- 1. Setup & Configurations ---
    tickers_list = ["SPY", "QQQ", "AAPL", "TSLA", "NVDA", "MU", "INTC", "PLTR", "MSTR", 
                    "AMZN", "MSFT", "META", "HOOD", "IREN", "AMD", "SOFI", "GOOG"]
    dte = 1
    expiration_date = (timedelta(days=dte) + datetime.now()).strftime("%Y-%m-%d")

    # --- 2. Fetch API Data ---
    historical_volatility = get_historical_volatility(get_historical_closes(tickers_list)) 
    implied_volatility, raw_codes_list = get_implied_vol(tickers_list, historical_volatility[0], expiration_date) 
    
    # --- 3. Filter for High-Juice Volatility (IV > HV by 10%+) ---
    final_df = pd.DataFrame(data=historical_volatility).rename(columns={0: 'Price'})
    final_df["IV"] = implied_volatility
    final_df["Difference"] = (final_df["IV"] / final_df["HV"]) - 1 
    final_df = final_df[final_df["Difference"] > 0.1].reset_index(names='Tickers')

    # --- 4. Mathematical Modeling for Expected Move ---
    time_factor = math.sqrt(dte / 365)
    final_df["HV Expected"] = final_df["Price"] * time_factor * final_df["HV"] 
    final_df["IV Expected"] = final_df["Price"] * time_factor * final_df["IV"] 
    final_df["Price - IV_Expected"] = round(final_df["Price"] - final_df["IV Expected"])

    # --- 5. Clean & Flatten Real Market Options Chain ---
    flat_codes = [code for sublist in raw_codes_list for code in sublist]
    real_chain = pd.DataFrame({"real_code": flat_codes})
    
    # Standard OCC slicing (last 15 chars are Date + Put/Call + Strike)
    real_chain["Tickers"] = real_chain["real_code"].str[:-15]
    real_chain["real_strike"] = real_chain["real_code"].str[-8:].astype(float) / 1000

    # --- 6. Match Target Strikes to Active Market Contracts ---
    # Sorting is a strict requirement for pd.merge_asof to function correctly
    real_chain = real_chain.sort_values("real_strike")
    final_df = final_df.sort_values("Price - IV_Expected")

    matched_df = pd.merge_asof(
        final_df,
        real_chain[["Tickers", "real_strike", "real_code"]],
        left_on="Price - IV_Expected",
        right_on="real_strike",
        by="Tickers",
        direction="nearest"  
    )

    # --- 7. Finalize & Print Output ---
    matched_df["put code"] = matched_df["real_code"]
    print(matched_df)


