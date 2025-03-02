import tkinter as tk
from tkinter import ttk, messagebox
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression
import threading

class Node:
    def __init__(self, date, price):
        self.date = date
        self.price = price
        self.next = None

class StockPriceList:
    def __init__(self):
        self.head = None
        
    def append(self, date, price):
        new_node = Node(date, price)
        if not self.head:
            self.head = new_node
            return
        current = self.head
        while current.next:
            current = current.next
        current.next = new_node
        
    def to_arrays(self):
        dates = []
        prices = []
        current = self.head
        while current:
            dates.append(current.date)
            prices.append(current.price)
            current = current.next
        return np.array(dates), np.array(prices)

class StockPredictor:
    def __init__(self):
        self.stock_data = StockPriceList()
        self.window = tk.Tk()
        self.window.title("Stock Price Predictor")
        self.window.geometry("800x600")
        self.setup_gui()
        
    def setup_gui(self):
        # Input Frame
        input_frame = ttk.LabelFrame(self.window, text="Input Parameters", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(input_frame, text="Stock Symbol:").grid(row=0, column=0, padx=5)
        self.symbol_entry = ttk.Entry(input_frame)
        self.symbol_entry.grid(row=0, column=1, padx=5)
        self.symbol_entry.insert(0, "AAPL")
        
        ttk.Label(input_frame, text="Prediction Days:").grid(row=0, column=2, padx=5)
        self.days_entry = ttk.Entry(input_frame)
        self.days_entry.grid(row=0, column=3, padx=5)
        self.days_entry.insert(0, "30")
        
        ttk.Button(input_frame, text="Fetch & Predict", command=self.fetch_and_predict).grid(row=0, column=4, padx=5)
        
        # Graph Frame
        self.graph_frame = ttk.LabelFrame(self.window, text="Price Graph", padding=10)
        self.graph_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Results Frame
        self.results_frame = ttk.LabelFrame(self.window, text="Prediction Results", padding=10)
        self.results_frame.pack(fill="x", padx=10, pady=5)
        
        self.result_text = tk.Text(self.results_frame, height=4, width=60)
        self.result_text.pack(fill="x", expand=True)
        
    def fetch_stock_data(self, symbol):
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="1y")
            
            self.stock_data = StockPriceList()
            for date, row in hist.iterrows():
                self.stock_data.append(date, row['Close'])
            
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch stock data: {str(e)}")
            return False
            
    def predict_prices(self, days):
        dates, prices = self.stock_data.to_arrays()
        
        # Prepare data for prediction
        X = np.arange(len(prices)).reshape(-1, 1)
        y = prices.reshape(-1, 1)
        
        scaler = MinMaxScaler()
        X_scaled = scaler.fit_transform(X)
        y_scaled = scaler.fit_transform(y)
        
        # Train model
        model = LinearRegression()
        model.fit(X_scaled, y_scaled)
        
        # Predict future prices
        future_dates = pd.date_range(dates[-1], periods=days+1)[1:]
        future_X = np.arange(len(prices), len(prices) + days).reshape(-1, 1)
        future_X_scaled = scaler.transform(future_X)
        
        future_y_scaled = model.predict(future_X_scaled)
        future_prices = scaler.inverse_transform(future_y_scaled)
        
        return future_dates, future_prices.flatten()
        
    def plot_data(self, future_dates, future_prices):
        dates, prices = self.stock_data.to_arrays()
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(dates, prices, label='Historical Prices')
        ax.plot(future_dates, future_prices, 'r--', label='Predicted Prices')
        
        ax.set_xlabel('Date')
        ax.set_ylabel('Price')
        ax.set_title('Stock Price Prediction')
        ax.legend()
        plt.xticks(rotation=45)
        
        # Clear previous graph
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
            
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
    def fetch_and_predict(self):
        symbol = self.symbol_entry.get().upper()
        days = int(self.days_entry.get())
        
        if self.fetch_stock_data(symbol):
            future_dates, future_prices = self.predict_prices(days)
            self.plot_data(future_dates, future_prices)
            
            # Update results
            last_price = future_prices[-1]
            first_price = future_prices[0]
            change = ((last_price - first_price) / first_price) * 100
            
            result_text = f"Predicted price after {days} days: ${last_price:.2f}\n"
            result_text += f"Expected change: {change:.2f}%\n"
            result_text += f"If you are stupid enough to believe this prediction, Then you are stupid enough to jump from the ninth floor. I can assure you that it wil not hurt you. please Jump."
            
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, result_text)
            
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    predictor = StockPredictor()
    predictor.run()m 