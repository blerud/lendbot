from datetime import datetime, timedelta
from io import BytesIO

import matplotlib.colors as mcolors
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import pytz
import yfinance as yf

fill_green = (0.5, 1, 0.5)
fill_red = (1, 0.5, 0.5)
market_green = mcolors.LinearSegmentedColormap.from_list('market_green', [(0, 1, 0), (0, 1, 0)])
market_red = mcolors.LinearSegmentedColormap.from_list('market_red', [(1, 0, 0), (1, 0, 0)])


def get_stock_price(symbol):
    info = yf.Ticker(symbol).info
    return (info['ask'] + info['bid']) / 2


def get_intraday_graph(symbol):
    symbol = symbol.upper()

    # Dataframe
    df = yf.download(symbol, datetime.now() - timedelta(days=7), interval='5m')
    last_business_day = df.iloc[[-1]].index.floor(freq='d')[0]
    last_business_day_ts = pd.Timestamp(ts_input=last_business_day)
    previous_close = df.truncate(after=last_business_day_ts)['Close'][-1]
    df = df.truncate(before=last_business_day_ts)

    # Axis
    close = df['Close']
    bull = close[-1] >= previous_close
    ax = close.plot(colormap=market_green if bull else market_red)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%I:%M %p", tz=pytz.timezone('America/New_York')))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter("%I:%M %p", tz=pytz.timezone('America/New_York')))
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('$%1.2f'))
    ax.set_xlabel(None)

    graph_max = max(close.max(0), previous_close)
    graph_min = min(close.min(0), previous_close)
    graph_delta = graph_max - graph_min
    graph_max_margin = graph_max + 0.1 * graph_delta
    graph_min_margin = max(0, graph_min - 0.1 * graph_delta)
    plt.hlines((graph_max_margin, graph_min_margin), df.first_valid_index(), df.last_valid_index(), linestyles='solid')

    plt.hlines(previous_close, df.first_valid_index(), df.last_valid_index(), linestyles='dotted')
    plt.fill_between(close.index, graph_min_margin, close, alpha=0.5, color=fill_green if bull else fill_red)
    plt.margins(0)
    plt.grid(axis='y')
    plt.title("{}: {}".format(symbol, last_business_day.strftime("%A, %B %d %Y")))

    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.clf()
    buf.seek(0)
    return buf
