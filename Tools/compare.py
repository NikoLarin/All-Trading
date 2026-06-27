import requests
import pandas as pd
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, font
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np

TIINGO_API_KEY = "Your Key"

def get_date_range(range_key):
    today = datetime.today()
    if range_key == "1M":
        return today - timedelta(days=30), today
    elif range_key == "3M":
        return today - timedelta(days=90), today
    elif range_key == "6M":
        return today - timedelta(days=180), today
    elif range_key == "1Y":
        return today - timedelta(days=365), today
    elif range_key == "3Y":
        return today - timedelta(days=3 * 365), today
    elif range_key == "5Y":
        return today - timedelta(days=5 * 365), today
    elif range_key == "MAX":
        return datetime(2010, 1, 1), today
    else:
        raise ValueError("Invalid range")

def fetch_etf_data(etf, start_date, end_date):
    url = f"https://api.tiingo.com/tiingo/daily/{etf}/prices"
    headers = {"Authorization": f"Token {TIINGO_API_KEY}"}
    params = {
        "startDate": start_date.strftime("%Y-%m-%d"),
        "endDate": end_date.strftime("%Y-%m-%d"),
        "resampleFreq": "daily"
    }
    r = requests.get(url, headers=headers, params=params)
    r.raise_for_status()
    df = pd.DataFrame(r.json())
    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)
    return df[["adjClose"]].rename(columns={"adjClose": etf})

def calculate_stats(series):
    returns = series.pct_change().dropna()
    total_return = series.iloc[-1] / series.iloc[0] - 1
    cagr = (series.iloc[-1] / series.iloc[0]) ** (1 / (len(series)/252)) - 1
    vol = returns.std() * np.sqrt(252)
    drawdown = (series / series.cummax() - 1).min()
    return {
        "Total Return": f"{total_return*100:.2f}%",
        "CAGR": f"{cagr*100:.2f}%",
        "Volatility": f"{vol*100:.2f}%",
        "Max Drawdown": f"{drawdown*100:.2f}%"
    }

def simulate(etfs, range_key):
    start_date, end_date = get_date_range(range_key)
    dfs = [fetch_etf_data(etf, start_date, end_date) for etf in etfs]
    df = pd.concat(dfs, axis=1).dropna()
    df = df / df.iloc[0] * 10000
    return df

class ComparerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Comparer - Matrix Theme")
        self.root.geometry("1100x1000")
        self.root.configure(bg="#000000")

        self.matrix_font = font.Font(family="OCR A Extended", size=14)
        self.label_font = font.Font(family="OCR A Extended", size=11)
        self.stat_font = font.Font(family="OCR A Extended", size=10)

        tk.Label(root, text="Comparer", font=self.matrix_font, fg="#00FF00", bg="#000000").pack(pady=(10, 15))

        input_frame = tk.Frame(root, bg="#000000")
        input_frame.pack(pady=5)

        tk.Label(input_frame, text="Tickers (comma-separated):", font=self.label_font, fg="#00FF00", bg="#000000").grid(row=0, column=0, sticky="w")

        self.etf_entry = tk.Entry(
            input_frame, width=30, font=self.label_font,
            fg="#00FF00", bg="#101010", insertbackground="#00FF00", relief="flat",
            highlightbackground="#00FF00", highlightcolor="#00FF00", highlightthickness=1
        )
        self.etf_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(input_frame, text="Select Range:", font=self.label_font, fg="#00FF00", bg="#000000").grid(row=1, column=0, sticky="w")

        self.range_var = tk.StringVar(value="1Y")
        ranges = ["1M", "3M", "6M", "1Y", "3Y", "5Y", "MAX"]

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TCombobox",
                        fieldbackground="#101010",
                        background="#101010",
                        foreground="#00FF00",
                        arrowcolor="#00FF00")

        self.range_menu = ttk.Combobox(input_frame, textvariable=self.range_var, values=ranges,
                                       font=self.label_font, width=10, state="readonly")
        self.range_menu.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        self.compare_btn = tk.Button(root, text="Compare", command=self.run_comparison,
                                     bg="#003300", fg="#00FF00", font=self.label_font,
                                     relief="flat", padx=10, pady=6, cursor="hand2")
        self.compare_btn.pack(pady=15)

        self.chart_frame = tk.Frame(root, bg="#000000")
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=20)

        self.stats_frame = tk.Frame(root, bg="#000000")
        self.stats_frame.pack(pady=10, padx=20)  # no fill initially

    def run_comparison(self):
        
        tickers = [t.strip().upper() for t in self.etf_entry.get().split(",") if t.strip()]
        range_key = self.range_var.get()

        # Clear previous chart and stats
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        for widget in self.stats_frame.winfo_children():
            widget.destroy()

        if not tickers:
            self.stats_frame.pack_forget()  # Hide stats if no input
            return

        try:
            df = simulate(tickers, range_key)
        except Exception as e:
            self.show_error(f"Error fetching data: {e}")
            self.stats_frame.pack_forget()
            return

        # Show stats frame only now, and expand horizontally
        self.stats_frame.pack_configure(fill=tk.X)

        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(9, 5))

        colors = ['#00FF00', "#727579", '#009900', '#006600', '#33FF33', '#66FF66']

        for i, ticker in enumerate(tickers):
            df[ticker].plot(ax=ax, color=colors[i % len(colors)], label=ticker, linewidth=2)

        ax.set_facecolor('#000000')
        ax.figure.set_facecolor('#000000')
        ax.title.set_color('#00FF00')
        ax.yaxis.label.set_color('#00FF00')
        ax.xaxis.label.set_color('#00FF00')
        ax.tick_params(axis='x', colors='#00FF00')
        ax.tick_params(axis='y', colors='#00FF00')
        ax.grid(color='#004400')

        leg = ax.legend(facecolor='#000000', edgecolor='#00FF00', labelcolor='#00FF00')
        leg.get_frame().set_linewidth(1.5)

        plt.tight_layout()


        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Show stats
        for ticker in tickers:
            stats = calculate_stats(df[ticker])
            stat_text = f"{ticker}:\n" + "\n".join([f"{k}: {v}" for k, v in stats.items()])
            label = tk.Label(self.stats_frame, text=stat_text, justify=tk.LEFT,
                             font=self.stat_font, fg="#00FF00", bg="#000000",
                             bd=1, relief="solid", padx=10, pady=6)
            label.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.Y)

    def show_error(self, message):
        error_win = tk.Toplevel(self.root)
        error_win.title("Error")
        error_win.geometry("400x150")
        error_win.configure(bg="#330000")
        tk.Label(error_win, text=message, fg="#FF4444", bg="#330000", font=("OCR A Extended", 12), wraplength=380).pack(padx=10, pady=40)
        tk.Button(error_win, text="Close", command=error_win.destroy, bg="#660000", fg="#FF4444", padx=10, pady=5).pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = ComparerApp(root)
    root.mainloop()
