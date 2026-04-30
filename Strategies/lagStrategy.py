import requests

def headers():
    return {
        "accept": "application/json",
        "content-type": "application/json",
        "APCA-API-KEY-ID": 'x',
        "APCA-API-SECRET-KEY": 'x',
    }

def all_positions():
    url = "https://paper-api.alpaca.markets/v2/positions"
    
    response = requests.get(url, headers=headers())
    response = response.json()
    return response

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


syms = [['NVDA', 'AMD'], ['GLD', 'SLV'], ['SPY', 'QQQ']]
while True:
    for i in syms:
        list = get_price_change(i[0], i[1])

        sym1_pct_change = ((list[0][1] + (list[0][0])) / list[0][1] -1) * 100
        sym2_pct_change = ((list[1][1] + (list[1][0])) / list[1][1] -1) * 100
        
        
        if sym1_pct_change - sym2_pct_change > .2:
            #buy mkt sym2
            #set take profit @ sym1 pct_change * .5 * sym2_close + sym2_close
            positions = all_positions()
            if list[1][2] in positions[0].values():
                continue
            
            tp = (sym1_pct_change / 100) * .5 * list[1][1] + list[1][1]
            payload = {
            "type": "market",
            "time_in_force": "day",
            "take_profit": { "limit_price": tp},
            "stop_loss": { "stop_price": "0.99"},
            "symbol": f'{list[1][2]}',
            "side": "buy",
            "order_class": "bracket",
            "qty": f'{round(list[1][1] / 1250)}'
            }
        
            response = requests.post(url, json=payload, headers=headers())
        
            print(f'Buying {list[1][2]} | TP: {tp}')
        
        if sym2_pct_change - sym1_pct_change > .2:
            #buy mkt sym1
            #set take profit @ sym2 pct_change * .5 * sym1_close + sym1_close
            positions = all_positions()
            if list[0][2] in positions[0].values():
                continue
            
            tp = (sym2_pct_change / 100) * .5 * list[0][1] + list[0][1]
            payload = {
            "type": "market",
            "time_in_force": "day",
            "take_profit": { "limit_price": tp},
            "stop_loss": { "stop_price": "0.99" },
            "symbol": f'{list[0][2]}',
            "side": "buy",
            "order_class": "bracket",
            "qty": f'{round(list[0][1] / 1250)}'
            }
        
            response = requests.post(url, json=payload, headers=headers())
        
            print(f'Buying {list[0][2]} | TP: {tp}')
        
        print(f'{list[1][2]}/{list[0][2]}')
