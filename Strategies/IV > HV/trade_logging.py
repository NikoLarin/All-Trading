import os
import pandas as pd
from datetime import datetime, timedelta
from data import historical_closes

def log_trade_to_csv(option_code, main_dataframe, log_file="options_trade_log.csv"):
    """
    Extracts analytics data for a specific option from main_dataframe 
    and records it as an open trade inside a CSV log file.
    """
    # 1. Extract the ticker characters from the option code (e.g., 'AMZN')
    ticker_match = pd.Series([option_code]).str.extract(r"^([A-Za-z]+)").iloc[0, 0]
    
    # 2. Extract that specific stock's data from your main DataFrame
    ticker_row = main_dataframe[main_dataframe["tickers"] == ticker_match]
    
    if ticker_row.empty:
        print(f"Warning: No metrics found in DataFrame for {ticker_match}. Log skipped.")
        return False

    # 3. Construct a clean dictionary of metrics at execution time
    log_entry = {
        "execution_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "option_code": option_code,
        "ticker": ticker_match,
        "underlying_price": float(ticker_row["price"].values[0]),
        "historical_vol": float(ticker_row["hv"].values[0]),
        "implied_vol": float(ticker_row["iv"].values[0]),
        "vol_difference": float(ticker_row["difference"].values[0]),
        "target_implied_move": float(ticker_row["implied move"].values[0]),
        "trade_status": "OPEN",
        "exit_time": None,
        "exit_underlying_price": None,
        "pnl": None
    }
    
    # 4. Save seamlessly to CSV without locking up memory
    df_log_entry = pd.DataFrame([log_entry])
    file_exists = os.path.isfile(log_file)
    df_log_entry.to_csv(log_file, mode='a', index=False, header=not file_exists)
    return True


def process_expiry_and_strikes(df_log):
    """Parses standard OSI codes to extract actual Expiry Dates and Strikes."""
    # Extract the YYMMDD string (chars 4 to 10)
    df_log['expiry_str'] = df_log['option_code'].str[4:10]
    
    # Convert YYMMDD to a clean datetime object
    df_log['expiry_date'] = pd.to_datetime(df_log['expiry_str'], format='%y%m%d')
    
    # Isolate strike prices (last 8 digits divided by 1000)
    df_log['strike'] = df_log['option_code'].str[-8:].astype(float) / 1000.0
    
    return df_log

def analyze_expired_trades(log_file="options_trade_log.csv"):
    # 1. Load your trade ledger
    if not os.path.isfile(log_file):
        print("Trade log file not found.")
        return
    
    df_log = pd.read_csv(log_file)
    df_log = process_expiry_and_strikes(df_log)
    
    # 2. Get a list of all tickers we need data for
    unique_tickers = df_log['ticker'].unique().tolist()
    
    # 3. Pull historical daily data (reusing your existing historical closes function)
    # Ensure this function returns a DataFrame where the index consists of Datetime objects
    historical_data = historical_closes(unique_tickers)
    
    # 4. Match the strike price to the stock price on the exact expiry day
    expiry_prices = []
    distances = []
    moneyness_status = []
    
    for idx, row in df_log.iterrows():
        ticker = row['ticker']
        expiry_dt = row['expiry_date']
        strike = row['strike']
        
        # Pull the closing price for that specific ticker on that specific day
        try:
            # Handle cases where the index is a datetime or string timestamp
            final_stock_price = historical_data.loc[expiry_dt, ticker]
            expiry_prices.append(round(final_stock_price, 2))
            
            # Calculate dollar distance: (Stock Price - Strike Price)
            # Positive means stock finished above strike, negative means below
            diff = final_stock_price - strike
            distances.append(round(diff, 2))
            
            # Check option settlement outcome
            is_put = "P" in row['option_code'][10:12]
            if is_put:
                status = "ITM (Loss)" if final_stock_price < strike else "OTM (Win)"
            else: # Call option
                status = "ITM (Loss)" if final_stock_price > strike else "OTM (Win)"
            moneyness_status.append(status)
            
        except KeyError:
            # If the market hasn't reached that date yet, or it was a market holiday
            expiry_prices.append(None)
            distances.append(None)
            moneyness_status.append("PENDING EXPIRY")
            
    # 5. Append analysis directly into your DataFrame columns
    df_log['stock_price_at_expiry'] = expiry_prices
    df_log['dollar_distance'] = distances
    df_log['outcome'] = moneyness_status
    
    return df_log[['ticker', 'option_code', 'expiry_date', 'strike', 'stock_price_at_expiry', 'dollar_distance', 'outcome']]
