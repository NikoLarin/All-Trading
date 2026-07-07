import os
from datetime import datetime, timedelta
import pandas as pd
import math
from data import historical_closes, get_implied_volatility, all_positions
from calculations import calculate_historical_volatility
from orders import short_option
from trade_logging import log_trade_to_csv

if __name__ == "__main__":
    trading_range = 32
    for dte in range(1, trading_range):
        expiration_date = (timedelta(days=dte) + datetime.now()).strftime("%Y-%m-%d")

        tickers_list = ["SPY", "QQQ", "AAPL", "TSLA", "NVDA", "MU", "INTC", "PLTR", "MSTR", 
                            "AMZN", "MSFT", "META", "HOOD", "IREN", "AMD", "SOFI", "GOOG"]

        historical_closes_data = historical_closes(tickers_list)
        historical_volatility_series = calculate_historical_volatility(historical_closes_data)
        iv_series, options_codes = get_implied_volatility(historical_closes_data, expiration_date)
        
        if not options_codes:
            print(f"{expiration_date} Market closed / No options")
            continue

        # Build all main_df columns 
        main_dataframe = pd.DataFrame()
        main_dataframe["tickers"] = tickers_list
        main_dataframe["price"] = historical_closes_data.iloc[-1].to_list()
        main_dataframe["hv"] = historical_volatility_series.to_list()
        main_dataframe["iv"] = iv_series.to_list()
        main_dataframe["difference"] = (main_dataframe["iv"] / main_dataframe["hv"]) - 1
        main_dataframe["implied move"] = main_dataframe["price"] - (main_dataframe["price"] * main_dataframe["iv"] * math.sqrt(1/365))
        # main_dateframe["option code"] = option code at the implied move here

        # Filtering main_df
        main_dataframe = main_dataframe[main_dataframe['iv'] != -1]
        #main_dataframe = main_dataframe[main_dataframe['iv' != -1]
        main_dataframe = main_dataframe[main_dataframe["difference"] > .1]

        # Flatten options codes list and put in dataframe
        options_codes = [code for sublist in options_codes for code in sublist]
        try:
            df_options = pd.DataFrame({'option_code': options_codes})
            # Extract ONLY the letters at the start of the option code
            df_options['ticker'] = df_options['option_code'].str.extract(r'^([A-Za-z]+)')

            # Extract Strike (last 8 digits divided by 1000)
            df_options['strike'] = df_options['option_code'].str[-8:].astype(float) / 1000.0

            # Sort by strike (Mandatory for pd.merge_asof)
            df_options = df_options.sort_values('strike')
        
        except AttributeError:
            print(f'{expiration_date} - market closed / no options found')
            continue

        

        # Clean Main DataFrame & Merge
        # Force types and remove whitespace to guarantee exact matching keys
        main_dataframe['tickers'] = main_dataframe['tickers'].astype(str).str.strip()
        main_dataframe['implied move'] = main_dataframe['implied move'].astype(float)

        # Sort by the target match column (Mandatory for pd.merge_asof)
        main_dataframe = main_dataframe.sort_values('implied move')

        main_dataframe = pd.merge_asof(
            main_dataframe,
            df_options,
            left_on='implied move',    # Target value from main_dataframe
            right_on='strike',         # Search value from df_options
            left_by='tickers',         # Exact match left key
            right_by='ticker',         # Exact match right key
            direction='nearest'        # Finds closest value
        )

        main_dataframe.drop(columns=["ticker"], inplace=True)

        # 1. Extract the Ticker+Expiry+Type (first 13 chars) from your open positions
        # 1. Isolate the Ticker + Expiry + Type (first 13 chars) from your active positions
        owned_prefixes = {pos[:13] for pos in all_positions() if isinstance(pos, str)}

        # 2. Get the same 13-character prefix for your DataFrame option codes
        df_prefixes = main_dataframe["option_code"].astype(str).str[:13]

        # 3. Filter for rows where the prefix is NOT in your owned positions
        not_owned_df = main_dataframe[~df_prefixes.isin(owned_prefixes)]

        # 4. Generate your clean flat list of unowned full option codes
        not_owned_list = not_owned_df["option_code"].dropna().tolist()

        print(main_dataframe)
        print(expiration_date)


        for option in not_owned_list:
            short_option(option)
            print(f"Shorted : {option}")
            log_trade_to_csv(option, main_dataframe)
        

    print("Blast finished")
