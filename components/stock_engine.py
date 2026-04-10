import yfinance as yf
import pandas as pd

def get_stock_data(symbol, period="30d"):
    # Fetch historical stock data for the given symbol and period
    stock = yf.Ticker(symbol)
    df = stock.history(period=period)
    df = df[['Close', 'Volume']].reset_index()
    df.columns = ['Date', 'Close', 'Volume']
    return df

def get_current_price(symbol):
    # Return the latest closing price of a stock
    stock = yf.Ticker(symbol)
    data = stock.history(period="1d")
    if not data.empty:
        return round(data['Close'].iloc[-1], 2)
    return None

def get_moving_average(symbol, window=30):
    # Calculate the moving average over a given window of days
    df = get_stock_data(symbol, period="90d")
    df['MA'] = df['Close'].rolling(window=window).mean()
    return df

def get_stock_info(symbol):
    # Return basic company info as a dictionary
    stock = yf.Ticker(symbol)
    info = stock.info
    return {
        'name': info.get('longName', 'N/A'),
        'sector': info.get('sector', 'N/A'),
        'country': info.get('country', 'N/A'),
        'currency': info.get('currency', 'N/A')
    }