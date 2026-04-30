import requests
import dotenv

def headers():
    return {
        "accept": "application/json",
        "content-type": "application/json",
        "APCA-API-KEY-ID": 'urkey',
        "APCA-API-SECRET-KEY": 'urkey',
    }

def get_price_change(sym1,sym2):
    url = f'https://data.alpaca.markets/v2/stocks/bars/latest?symbols={sym1}%2C{sym2}&feed=delayed_sip'

    response = requests.get(url, headers=headers()) #calls headers function
    response = response.json()

    sym1_close = response['bars'][sym1]['c']
    sym1_open = response['bars'][sym1]['o']
    sym1_change = sym1_open - sym1_close

    sym2_close = response['bars'][sym2]['c']
    sym2_open = response['bars'][sym2]['o']
    sym2_change = sym2_open - sym2_close

    return ([sym1_change, sym1_close, sym1], [sym2_change, sym2_close, sym2])

url = "https://paper-api.alpaca.markets/v2/orders"


syms = [[NVDA, AMD], [GLD,SLV], [SPY, QQQ]]
while True:
    for i in syms:
        list = get_price_change(i[0], i[1])

        sym1_pct_change = ((list[0][1] + (list[0][0])) / list[0][1] -1) * 100
        sym2_pct_change = ((list[1][1] + (list[1][0])) / list[1][1] -1) * 100
        
        
        if sym1_pct_change - sym2_pct_change > .4:
            #buy mkt sym2
            #set take profit @ sym1 pct_change * .5 * sym2_close + sym2_close
            
            payload = {
            "type": "market",
            "time_in_force": "day",
            "take_profit": { "limit_price": f'{sym1_pct_change * .5 * list[1][1] + list[1][1]}'},
            "symbol": f'{list[1][2]}',
            "notional": "100",
            "side": "buy"
            }
        
            response = requests.post(url, json=payload, headers=headers())
        
            print(response.text)
        
        if sym2_pct_change - sym1_pct_change > .4:
            #buy mkt sym1
            #set take profit @ sym2 pct_change * .5 * sym1_close + sym1_close
            payload = {
            "type": "market",
            "time_in_force": "day",
            "take_profit": { "limit_price": f'{sym2_pct_change * .5 * list[0][1] + list[0][1]}'},
            "symbol": f'{list[0][2]}',
            "notional": "100",
            "side": "buy"
            }
        
            response = requests.post(url, json=payload, headers=headers())
        
            print(response.text)
        
        print(sym1_pct_change, sym2_pct_change)
                
