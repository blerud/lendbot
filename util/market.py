from datetime import date, datetime
from io import BytesIO

from iexfinance.stocks import Stock, get_historical_data, get_historical_intraday
import matplotlib.pyplot as plt
import pandas as pd

def get_stock_price(symbol):
    return Stock(symbol).get_price()

def get_intraday_graph(symbol):
    today = date.today()
    df = get_stock_intraday(symbol, today)
    df = df[df.average != -1]
    df.index = pd.to_datetime(df.index)
    df['average'].plot()
    plt.title(symbol)
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.clf()
    buf.seek(0)
    return buf

def get_stock_intraday(symbol, date):
    return get_historical_intraday(symbol, date, output_format='pandas')
