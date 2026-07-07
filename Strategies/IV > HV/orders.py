from config import get_headers
import requests

def short_option(option_code):
    "opens a short market order for the provided option code"
    
    url = "https://paper-api.alpaca.markets/v2/orders"

    payload = {
        "time_in_force": "day",
        "type": "market",
        "qty": "1",
        "symbol": option_code,
        "side": "sell"
    }

    response = requests.post(url, json=payload, headers=get_headers())

    return response