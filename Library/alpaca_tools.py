import requests
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://paper-api.alpaca.markets/v2"

def headers():
    return {
        "accept": "application/json",
        "APCA-API-KEY-ID": 'YOUR API KEY',
        "APCA-API-SECRET-KEY": 'YOUR API KEY',
    }

def accountValue():
    response = requests.get(f'{BASE_URL}/account', headers=headers()) # calls headers
    response = response.json()
    
    return response['portfolio_value']

def stockPrice(sym):
    url = f"https://data.alpaca.markets/v2/stocks/{sym}/snapshot"

    response = requests.get(url, headers=headers()) #calls headers function
    response = response.json()

    return response['dailyBar']['c']
        
def pctDailyChange(sym):
    url = f"https://data.alpaca.markets/v2/stocks/{sym}/snapshot"

    response = requests.get(url, headers=headers()) #calls headers function
    response = response.json()
    
    openPrice = response['prevDailyBar']['c'] #Daily bar open 
    closePrice = response['dailyBar']['c'] #latest price    
    
    pctChange = round(((closePrice - openPrice) / openPrice), 4) * 100

    return pctChange
    

