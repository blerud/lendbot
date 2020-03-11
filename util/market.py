from datetime import date, datetime, timedelta
import pytz
from io import BytesIO

import matplotlib.colors as mcolors
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import yfinance as yf

fill_green = (0.5, 1, 0.5)
fill_red = (1, 0.5, 0.5)
market_green = mcolors.LinearSegmentedColormap.from_list('market_green', [(0, 1, 0), (0, 1, 0)])
market_red = mcolors.LinearSegmentedColormap.from_list('market_red', [(1, 0, 0), (1, 0, 0)])

def get_stock_price(symbol):
    info = yf.Ticker(symbol).info
    return (info['ask'] + info['bid']) / 2

def get_intraday_graph(symbol):
    now = datetime.now()
    today = date.today()

    # Dataframe
    df = yf.download(symbol, datetime.now() - timedelta(days=7), interval='5m')
    last_business_day = df.iloc[[-1]].index.floor(freq='d')[0]
    df = df.truncate(before=pd.Timestamp(ts_input=last_business_day))

    # Axis
    close = df['Close']
    bull = close[-1] >= close[0]
    ax = close.plot(colormap=market_green if bull else market_red)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%I:%M %p", tz=pytz.timezone('America/New_York')))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter("%I:%M %p", tz=pytz.timezone('America/New_York')))
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('$%1.2f'))
    ax.set_xlabel(None)

    plt.fill_between(close.index, close.min(0), close, alpha=0.5, color=fill_green if bull else fill_red)
    plt.margins(x=0, y=0)
    plt.grid(axis='y')
    plt.title("{}: {}".format(symbol, last_business_day.strftime("%A, %B %d %Y")))

    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.clf()
    buf.seek(0)
    return buf
