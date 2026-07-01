def aoc(ticker):
    '''
    this function pulls open and close data for 100 days and calculates the 
    average open to close change for one day   
    '''
    
    today = date.today()
    year_ago = today - relativedelta(years=1)
    
    url = f"https://data.alpaca.markets/v2/stocks/bars?symbols={ticker}&timeframe=1D&start={year_ago}&limit=100&adjustment=raw&feed=sip&sort=asc"

    response  = requests.get(url, headers=headers())
    data = response.json()

    bars = data["bars"][ticker]

    abs_pct_changes = []

    for candle in bars:
        closeD = candle["c"]
        openD = candle["o"]

        if openD != 0:
            abs_pct_changes.append(abs(((closeD - openD) / openD)))

    today_aoc = sum(abs_pct_changes) / len(abs_pct_changes)

    return today_aoc / 2
