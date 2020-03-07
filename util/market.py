from datetime import date, datetime, timedelta
import pytz.reference
from io import BytesIO

import yfinance as yf
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

def get_stock_price(symbol):
    info = yf.Ticker(symbol).info
    return (info['ask'] + info['bid']) / 2

def get_intraday_graph(symbol):
    now = datetime.now()
    today = date.today()
    df = yf.download(symbol, datetime.now() - timedelta(days=7), interval='5m')
    last_business_day = df.iloc[[-1]].index.floor(freq='d')[0]
    df = df.truncate(before=pd.Timestamp(ts_input=last_business_day))
    ax = df['Close'].plot()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%I:%M %p"))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter("%I:%M %p"))
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('$%1.2f'))

    plt.title(symbol)
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.clf()
    buf.seek(0)
    return buf
