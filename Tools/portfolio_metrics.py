import pandas as pd
import numpy as np

BALANCE_PATH = "/Users/nikolarin/Downloads/Custodial Brokerage_XXXX300_Balances_20260626-141945.CSV"
TRANSACTION_PATH = "/Users/nikolarin/Downloads/Custodial_Brokerage_XXX300_Transactions_20260626-132230.csv"

def clean_transaction_data(data):
    df = pd.read_csv(data, index_col="Date")

    df = df.drop(columns=["Fees & Comm"])
    df = df.dropna(subset=["Quantity", "Price", "Amount"])

    return df

def clean_balance_data(data, start_date):
    balance_data = pd.read_csv(data, index_col="Date")
    balance_data = balance_data.drop_duplicates()
    balance_data["Amount"] = balance_data["Amount"].str.replace("$", "", regex=False)
    balance_data["Amount"] = balance_data["Amount"].str.replace(",", "", regex=False)
    
    return balance_data.loc[ : start_date].astype(float)

def get_volatility(balance_data): #Calculate portfolio vol with daily change
    balance_data["Return"] = balance_data["Amount"].pct_change()
    daily_returns = balance_data['Return'].dropna()[:-1]

    daily_volatility = np.std(daily_returns)
    monthly_volatility = np.std(daily_returns) * np.sqrt(21)
    annual_volatility = np.std(daily_returns) * np.sqrt(252)

    volatilities = [daily_volatility, monthly_volatility, annual_volatility]
    
    return [round(float(x), 2) for x in volatilities]
def get_sharpe(balance_data, risk_free_rate = .04):
    balance_data["Return"] = balance_data["Amount"].pct_change()
    daily_returns = balance_data['Return'].dropna()[:-1]
    
    mean_daily_return = daily_returns.mean()
    annual_return = float(mean_daily_return * 252)
    
    annual_volatility = np.std(daily_returns) * np.sqrt(252)

    sharpe = round(float(annual_return - risk_free_rate) / annual_volatility, 2)

    return sharpe
balance_data = clean_balance_data(BALANCE_PATH, "5/7/2026")

print(f'Your Sharpe Ratio is    :   {get_sharpe(balance_data)}\n'\
      f'Dail|Mont|Ann Vol       :   {get_volatility(balance_data)}'
      )

'''
Total volume
Pnl dollar/%
Volatility 
Sharpe
Max drawdown


'''
