def open_stock_price(sym):
    url = f"https://data.alpaca.markets/v2/stocks/{sym}/snapshot"

    response = requests.get(url, headers=headers()) #calls headers function
    response = response.json()

    return response['dailyBar']['o']
