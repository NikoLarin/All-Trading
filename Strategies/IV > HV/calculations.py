from data import historical_closes
import pandas as pd
import numpy as np

# historical volatility calculation function
def calculate_historical_volatility(closes_data_frame):
    '''takes a data frame of closing data and calculates standard deviation'''

    daily_returns = closes_data_frame.pct_change(axis=0).dropna()
    historical_volatility = daily_returns.std(axis=0) * np.sqrt(365)

    return historical_volatility



