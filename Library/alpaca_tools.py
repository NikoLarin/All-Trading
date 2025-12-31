import requests
import os
import time
from datetime import date
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv

load_dotenv()
BASE_URL = "https://paper-api.alpaca.markets/v2"
def headers():
    return {
        "accept": "application/json",
        "content-type": "application/json",
        "APCA-API-KEY-ID": 'YOUR-API-KEY',
        "APCA-API-SECRET-KEY": 'YOUR-SECRET-API-KEY',
    }

#----------ACCOUNT----------#
def accountValue():
    response = requests.get(f'{BASE_URL}/account', headers=headers()) # calls headers
    response = response.json()
    
    return response['portfolio_value']

def get_open_positions(): # return all open positions
    response = requests.get(f'{BASE_URL}/positions', headers=headers()) # calls headers
    response = response.json()
    
    return response['positions'] # all open positions

def position_history():
    pass

#----------STOCK----------#
def current_stock_price(sym):
    url = f"https://data.alpaca.markets/v2/stocks/{sym}/snapshot"

    response = requests.get(url, headers=headers()) #calls headers function
    response = response.json()

    return response['dailyBar']['c']

def open_stock_price(sym):
    url = f"https://data.alpaca.markets/v2/stocks/{sym}/snapshot"

    response = requests.get(url, headers=headers()) #calls headers function
    response = response.json()

    return response['dailyBar']['o']

def pctDailyChange(sym):
    url = f"https://data.alpaca.markets/v2/stocks/{sym}/snapshot"

    response = requests.get(url, headers=headers()) #calls headers function
    response = response.json()
    
    openPrice = response['prevDailyBar']['c'] #Daily bar open 
    closePrice = response['dailyBar']['c'] #latest price    
    
    pctChange = round(((closePrice - openPrice) / openPrice), 4) * 100

    return pctChange
    
def is_market_open():
    response = requests.get(f'{BASE_URL}/clock', headers=headers()) # calls headers
    response = response.json()

    return response['is_open'] #returns bool if mkt open/closed


#----------OPTIONS----------#
def option(oCode): #needs symbol and option code
    url = f"https://data.alpaca.markets/v1beta1/options/snapshots?symbols={oCode}&feed=indicative&limit=1"

    
    response = requests.get(url, headers=headers()) # gets live option based on oCode
    response = response.json()

    snap = response["snapshots"][oCode]

    code = snap
    greeks = snap['greeks']
    impliedVolatility = snap['impliedVolatility'] 
    price = snap['latestQuote']['ap']

    return (greeks, impliedVolatility, price) # returnts a tuple

def options_chain(ticker):
    #implement a simple filter to only get the most recent x strikes
    url = f"https://data.alpaca.markets/v1beta1/options/snapshots/{ticker}"
    
    response = requests.get(url, headers=headers())
    response = response.json()
    
    return response#['snapshots'] # returns huge chain

#----------INDICATOR----------#
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


