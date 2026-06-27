import math
import requests
import numpy as np
from datetime import datetime, timedelta

API_KEY = "polygon api"  #polygon data

def fetch_historical_closes(ticker, days):
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days * 2)
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{start_date}/{end_date}?adjusted=true&sort=asc&limit=500&apiKey={API_KEY}"
    resp = requests.get(url)
    data = resp.json()
    if "results" not in data:
        raise ValueError(f"Failed to fetch data: {data}")
    closes = [day['c'] for day in data['results'][-days:]]
    return closes

def empirical_close_breach_probability(closes, T_days, std_multiplier):
    log_returns = np.diff(np.log(closes))
    daily_vol = np.std(log_returns)

    breaches_below = 0
    breaches_above = 0
    total_windows = len(closes) - T_days

    for i in range(total_windows):
        start_price = closes[i]
        move = std_multiplier * daily_vol * start_price * math.sqrt(T_days)
        strike_above = start_price + move
        strike_below = start_price - move
        future_window = closes[i+1:i+1+T_days]

        # Check only the CLOSE of the last day in the window
        last_close = future_window[-1]

        if last_close < strike_below:
            breaches_below += 1
        if last_close > strike_above:
            breaches_above += 1

    prob_above = breaches_above / total_windows if total_windows > 0 else 0
    prob_below = breaches_below / total_windows if total_windows > 0 else 0

    return total_windows, breaches_above, breaches_below, prob_above, prob_below, daily_vol

def main():
    ticker = input("Enter Ticker (e.g. AAPL): ").upper()
    
    try:
        T_days = int(input("Enter time horizon in trading days (e.g. 5 for weekly): "))
    except ValueError:
        print("Invalid input. Defaulting to 5 trading days.")
        T_days = 5

    try:
        std_multiplier = float(input("Enter standard deviation multiplier (e.g. 1 for 1 SD, 0.5 for half SD): "))
    except ValueError:
        print("Invalid input. Defaulting to 1 SD multiplier.")
        std_multiplier = 1.0

    lookback_days = 252  # 1 year

    try:
        closes = fetch_historical_closes(ticker, lookback_days)
    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    total, above, below, p_above, p_below, daily_vol = empirical_close_breach_probability(closes, T_days, std_multiplier)

    print(f"\nResults for {ticker}")
    print(f"Total Windows Evaluated: {total}")
    print(f"Number of CLOSES ABOVE {std_multiplier} SD in {T_days} days: {above} ({p_above * 100:.2f}%)")
    print(f"Number of CLOSES BELOW {std_multiplier} SD in {T_days} days: {below} ({p_below * 100:.2f}%)")

    while True:
        live_price_input = input("\nEnter the LIVE current price for the ticker: ").strip()
        try:
            live_price = float(live_price_input)
            break
        except ValueError:
            print("Invalid price, please enter a valid number.")

    sd_move = std_multiplier * daily_vol * live_price * math.sqrt(T_days)
    upper_sd = live_price + sd_move
    lower_sd = live_price - sd_move

    print(f"\nCurrent {T_days}-day {std_multiplier} SD move for {ticker}: ±${sd_move:.2f}")
    print(f"Upper Price Level: ${upper_sd:.2f}")
    print(f"Lower Price Level: ${lower_sd:.2f}")

if __name__ == "__main__":
    main()
