import tkinter as tk
from tkinter import ttk
import numpy as np
import scipy.stats as stats
import fear_and_greed
import yfinance as yf
import webbrowser  # to open URLs in the browser
import pandas as pd
from time import strftime


def probability_OTM(S0, K, T_days, r_percentage, sigma_percentage):
    T_years = T_days / 365
    r = r_percentage / 100
    sigma = sigma_percentage / 100
    d1 = (np.log(S0 / K) + (r + 0.5 * sigma**2) * T_years) / (sigma * np.sqrt(T_years))
    d2 = d1 - sigma * np.sqrt(T_years)
    return stats.norm.cdf(d2), d1

def probability_touch(S0, K, T_days, r_percentage, sigma_percentage):
    _, d1 = probability_OTM(S0, K, T_days, r_percentage, sigma_percentage)
    prob_touch = 2 * stats.norm.cdf(d1) - 1
    return prob_touch

def calculate_OTM():
    try:
        S0 = float(entry_S0.get())
        K = float(entry_K.get())
        T_days = float(entry_T.get())
        r_percentage = float(entry_r.get())
        sigma_percentage = float(entry_sigma.get())
        prob_OTM, d1 = probability_OTM(S0, K, T_days, r_percentage, sigma_percentage)
        prob_touch = probability_touch(S0, K, T_days, r_percentage, sigma_percentage)
        
        # Inverse the Probability of Touch (POT) display
        inverse_prob_touch = 1 - prob_touch
        
        color_OTM = 'green' if prob_OTM > 0.50 else 'red'
        
        # Update the text with the inverse probability of touch
        label_result.config(text=f'Probability OTM: {prob_OTM:.2%}\nProbability of Touch: {inverse_prob_touch:.2%}', foreground=color_OTM)
    except ValueError:
        label_result.config(text='Invalid input. Please enter numerical values.', foreground='white')

def update_fear_greed_index():
    fgi = fear_and_greed.get()
    index_value = fgi.value
    description = fgi.description.capitalize()
    
    label_fgi_value.config(text=f'Fear & Greed Index: {index_value:.2f} ({description})', foreground='white')

def update_vix():
    try:
        vix_data = yf.Ticker("^VIX").history(period="5d")
        
        # Check if data is available
        if vix_data.empty:
            label_vix_value.config(text="VIX data not available", foreground="gray")
            return
        
        vix = vix_data.iloc[-1]['Close']
        
        if vix < 15:
            vix_color = 'dark green'
        elif 15 <= vix < 20:
            vix_color = 'light green'
        elif 20 <= vix < 25:
            vix_color = 'yellow'
        elif 25 <= vix < 30:
            vix_color = 'orange'
        elif 30 <= vix < 40:
            vix_color = 'red'
        else:
            vix_color = 'dark red'
        
        label_vix_value.config(text=f'VIX: {vix:.2f}', foreground=vix_color)
    except Exception as e:
        # In case there's an error (e.g., network issue, or invalid symbol)
        label_vix_value.config(text="Error fetching VIX data", foreground="red")
        print(f"Error updating VIX: {e}")

    # Refresh the VIX every 30 seconds
    root.after(30000, update_vix)


def update_font_size(event):
    new_font_size = max(12, int(event.width / 500))  # Adjust font size dynamically
    font = ('FixedSys', new_font_size + 10)
    style.configure('TLabel', font=font)
    style.configure('TButton', font=font)
    style.configure('TEntry', font=font)

    # Specifically larger font size for the Fear & Greed Index and VIX labels
    large_font = ('FixedSys', max(18, new_font_size + 4))
    label_fgi_value.config(font=large_font)
    label_vix_value.config(font=large_font)

def add_stock():
    ticker = entry_stock_ticker.get().strip().upper()  # Get ticker symbol
    if ticker:
        try:
            stock = yf.Ticker(ticker)
            stock_price = stock.history(period="1d").iloc[-1]['Close']
            stock_info_frame = ttk.Frame(frame_stocks, style='TFrame')
            stock_info_frame.pack(anchor=tk.W, padx=10, pady=5, fill=tk.X,)

            remove_button = ttk.Button(stock_info_frame, text="X", command=lambda: remove_stock(ticker, stock_info_frame), style='TButton', width=2)
            remove_button.pack(side=tk.LEFT, padx=5)

            stock_info_label = ttk.Label(stock_info_frame, text=f'{ticker}: ${stock_price:.2f}', font=('FixedSys', 14), background='black', foreground='white')
            stock_info_label.pack(side=tk.LEFT, anchor=tk.W)

            stock_labels[ticker] = {'label': stock_info_label, 'frame': stock_info_frame, 'remove_button': remove_button}  # Store label and remove button for updating later
        except Exception as e:
            error_label = ttk.Label(frame_stocks, text=f"Error fetching {ticker} data", font=('FixedSys', 14), background='black', foreground='red')
            error_label.pack(anchor=tk.W, padx=10, pady=10)
    
    entry_stock_ticker.delete(0, tk.END)  # Clear the ticker entry after adding

def remove_stock(ticker, frame):
    frame.destroy()
    del stock_labels[ticker]

def refresh_stock_prices():
    for ticker, stock_info in stock_labels.items():
        try:
            stock = yf.Ticker(ticker)
            stock_price = stock.history(period="5d").iloc[-1]['Close']
            stock_info['label'].config(text=f'{ticker}: ${stock_price:.2f}')
        except Exception as e:
            stock_info['label'].config(text=f"Error fetching {ticker} data")
    # Refresh the stock prices every 10 seconds
    root.after(5000, refresh_stock_prices)

def open_stock_analysis():
    ticker = entry_stock_ticker.get().strip().upper()  # Get ticker symbol
    if ticker:
        stock_analysis_url = f"https://www.stockanalysis.com/stocks/{ticker.lower()}/"
        webbrowser.open(stock_analysis_url)

def open_trading_view():
    ticker = entry_stock_ticker.get().strip().upper()  # Get ticker symbol
    if ticker:
        trading_view_url = f"https://www.tradingview.com/symbols/{ticker}/"
        webbrowser.open(trading_view_url)


def calculate_risk_reward_ratio():
    itm1 = float(itm_entry.get())
    profit1 = float(remaining_entry.get())
    rr_ratio = itm1 / profit1
    label_risk_reward_result.config(text=f'{rr_ratio:.2f}')
    if rr_ratio > 1:
        label_signal = tk.Label(
                    text = 'Hold',
                    font = ('FixedSys',25,'bold'),
                    fg = 'green',
                    bg = 'black')
        label_signal.place(x=560,y=107)
    else:
        label_signal = tk.Label(
                    text = 'Exit',
                    font = ('FixedSys',25,'bold'),
                    fg = 'red',
                    bg = 'black')
        label_signal.place(x=560,y=107)

def time():
    string = strftime('%H:%M:%S %p')
    lbl.config(text=string)
    lbl.after(1000, time)



root = tk.Tk()
root.title('Probability OTM Calculator')
root.geometry('1100x900')
root.configure(bg='black')

style = ttk.Style()
style.theme_use('clam')
style.configure('TLabel', font=('FixedSys', 14), foreground='white', background='black')
style.configure('TButton', font=('FixedSys', 14), foreground='white', background='black')
style.configure('TEntry', font=('FixedSys', 14), foreground='white', fieldbackground='black')
style.configure('TFrame', background='black')

frame = ttk.Frame(root, padding='5', style='TFrame')
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

frame_fgi_vix = ttk.Frame(root, padding='5', style='TFrame')
frame_fgi_vix.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

frame_stocks = ttk.Frame(root, padding='5', style='TFrame')
frame_stocks.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))

root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=3)
root.grid_columnconfigure(1, weight=1)

frame.grid_rowconfigure(0, weight=1)
frame.grid_rowconfigure(1, weight=1)
frame.grid_rowconfigure(2, weight=1)
frame.grid_rowconfigure(3, weight=1)
frame.grid_rowconfigure(4, weight=1)
frame.grid_rowconfigure(5, weight=1)
frame.grid_rowconfigure(6, weight=1)

frame.grid_columnconfigure(0, weight=1)
frame.grid_columnconfigure(1, weight=2)

label_S0 = ttk.Label(frame, text='Current Stock Price:')
label_S0.grid(column=0, row=0, sticky=tk.W)
entry_S0 = ttk.Entry(frame)
entry_S0.place(x=365,y=33)

label_K = ttk.Label(frame, text='Strike Price:')
label_K.place(x=1,y=65)
entry_K = ttk.Entry(frame)
entry_K.place(x=365,y=70)

label_T = ttk.Label(frame, text='Time to Expiry (days):')
label_T.place(x=1,y=100)
entry_T = ttk.Entry(frame)
entry_T.place(x=365,y=108)

label_r = ttk.Label(frame, text='Risk-Free Rate (%):')
label_r.place(x=1,y=135)
entry_r = ttk.Entry(frame)
entry_r.place(x=365,y=138)

label_sigma = ttk.Label(frame, text='Volatility (%):')
label_sigma.place(x=1,y=165)
entry_sigma = ttk.Entry(frame)
entry_sigma.place(x=365,y=176)

button_calculate = ttk.Button(frame, text='Calculate', command=calculate_OTM)
button_calculate.grid(column=0, row=5, columnspan=2, sticky=(tk.W, tk.E))

label_result = ttk.Label(frame, text='', font=('FixedSys', 14, 'bold'))
label_result.grid(column=0, row=6, columnspan=2, sticky=(tk.W, tk.E))

label_fgi_value = ttk.Label(frame_fgi_vix, text='Fear & Greed Index:', font=('FixedSys', 14, 'bold'))
label_fgi_value.pack(fill=tk.X)

label_vix_value = ttk.Label(frame_fgi_vix, text='VIX:', font=('FixedSys', 14, 'bold'))
label_vix_value.pack(fill=tk.X)

label_stock_ticker = ttk.Label(frame_stocks, text="Add Stock Ticker :", background='black', foreground='white')
label_stock_ticker.pack(fill=tk.X, padx=10, pady=5)

entry_stock_ticker = ttk.Entry(frame_stocks)
entry_stock_ticker.pack(fill=tk.X, padx=10)

button_add_stock = ttk.Button(frame_stocks, text='Add Stock', command=add_stock)
button_add_stock.place(x=240,y=70)

label_profit_risk = ttk.Label(text='%Remaining:%ITM',font = ('FixedSys',20,'bold'))
label_profit_risk.place(x=520,y=75)

itm_entry = ttk.Entry(width = 15)
itm_entry.place(x=820,y=84)

remaining_entry = ttk.Entry(width = 15)
remaining_entry.place(x=980,y=84)


button_calculate_risk_profit = ttk.Button(text = 'Calcuate',width=15, command = calculate_risk_reward_ratio)
button_calculate_risk_profit.place(x=820,y=110)

label_risk_reward_result = ttk.Label(
                            text='',
                            font=('FixedSys',25,'bold'))
label_risk_reward_result.place(x=690,y=110)

label_divide_symbol = ttk.Label(text = '/', font = ('FixedSys',20,'bold'))
label_divide_symbol.place(x=940,y=75)


# creates line divider
Watchlist_divider = tk.Canvas(width = 1, height = 10000 )
Watchlist_divider.place(x=240, y=615)

Trading_reminder_header_boarder = tk.Canvas(width = 200, height = 1 )
Trading_reminder_header_boarder.place(x=580, y=650)


# Create separate buttons for each stock analysis website
button_stock_analysis = ttk.Button(frame_stocks, text='Open Stock Analysis', command=open_stock_analysis, )
button_stock_analysis.place(x=445,y=70)

button_trading_view = ttk.Button(frame_stocks, text='Open Trading View', command=open_trading_view)
button_trading_view.place(x=780,y=70)

trading_laws_header = tk.Label(text = 'Trading Reminders:',
                        bg = 'black',
                        fg = 'Pink',
                        font = ('FixedSys',20,'bold'))
trading_laws_header.place(x=540,y=600)

trading_law_1 = tk.Label(text='1.If its going up it will keep going up.',
                        bg = 'black',
                        fg = 'Green',
                        font = ('FixedSys',20,'bold'))
trading_law_1.place(x=265,y=660)

trading_law_2 = tk.Label(text='2.Account for losses before profits.',
                        bg = 'black',
                        fg = 'Orange',
                        font = ('FixedSys',20,'bold'))
trading_law_2.place(x=265,y=690)

trading_law_3 = tk.Label(text='3.You shouldnt be excited.',
                        bg = 'black',
                        fg = 'Yellow',
                        font = ('FixedSys',20,'bold'))
trading_law_3.place(x=265,y=720)

trading_law_4 = tk.Label(text='4.Losses are garunteed, cut them when necessary.',
                        bg = 'black',
                        fg = 'Red',
                        font = ('FixedSys',20,'bold'))
trading_law_4.place(x=265,y=750)

trading_law_4 = tk.Label(text='5.You are not the hero',
                          bg = 'black',
                          fg = 'blue',
                          font = ('FixedSys',20,'bold'))
trading_law_4.place(x=265,y=780)

lbl = tk.Label(root, font=('FixedSys', 20, 'bold'),
            background='black',
            foreground='white',)
lbl.place(x=950,y=860)
time()


notepad_frame = tk.Canvas(width =508, height = 330, bg = 'Gray' )
notepad_frame.place(x=565,y=170)

notepad_header = tk.Label(text= 'Notebook',
                          font = ('FixedSys',20,'bold'),
                          bg = 'Gray')
notepad_header.place(x=790,y=172)

notepad_entry = tk.Entry( bg = 'gray')
notepad_entry.place(x=660,y=210,width=400, height = 280)

stock_labels = {}

update_fear_greed_index()
update_vix()
refresh_stock_prices()

root.bind("<Configure>", update_font_size)

root.resizable(False,False)

root.mainloop()
