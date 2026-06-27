import pandas as pd
import numpy as np

BALANCE_PATH = "C:\Desktop\Custodial Brokerage_XXXX300_Balances_20260626-141945.CSV"
TRANSACTION_PATH = "C:\Desktop\Custodial_Brokerage_XXX300_Transactions_20260626-132230.csv"
def clean_transaction_data(data):
    df = pd.read_csv(data, index_col="Date")

    df = df.drop(columns=["Fees & Comm"])
    df = df.dropna(subset=["Quantity", "Price", "Amount"])
    df["Amount"] = df["Amount"].str.replace("$", "", regex=False)
    df["Amount"] = df["Amount"].str.replace("-", "", regex=False)
    
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
def get_pnl(data):
    start = data["Amount"].iloc[0]
    end = data["Amount"].iloc[-2]
    pct_change = round((start - end) / end * 100, 2)

    return [round(start - end), float(pct_change)]

def get_transaction_volume(transaction_data):
    transaction_volume = transaction_data["Amount"]
    transaction_volume = transaction_volume.astype(float)
    transaction_volume = transaction_volume.sum()

    return transaction_volume


balance_data = clean_balance_data(BALANCE_PATH, "5/7/2026")
transaction_data = clean_transaction_data(TRANSACTION_PATH)



reporting_period = f'{balance_data.index[-1]} ----> {balance_data.index[0]}'
portfolio_value = balance_data["Amount"][0]
portfolio_sharpe = get_sharpe(balance_data)
portfolio_volatility = get_volatility(balance_data)
profit_loss = get_pnl(balance_data)
all_time_transaction_volume = round(get_transaction_volume(transaction_data))


print(f'Reporting Period        :   {reporting_period}\n'
      f'Portfolio Value         :   ${portfolio_value}\n'
      f'Your P&L is             :   ${profit_loss[0]} | {profit_loss[1]}%\n'
      f'All time trading volume :   ${all_time_transaction_volume}\n'
      f'Your Sharpe Ratio is    :   {portfolio_sharpe}\n'
      f'Dail|Mont|Ann Vol       :   {portfolio_volatility}\n'
)
    


'''
Total volume
Pnl dollar/%
Volatility 
Sharpe
Max drawdown


'''
