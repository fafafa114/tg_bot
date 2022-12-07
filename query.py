import requests
import talib
import pandas as pd
import datetime
import numpy as np
import matplotlib.gridspec as gridspec
import psycopg2 as pg
import matplotlib.pyplot as plt
import mpl_finance as mpl

my_red = (192/255, 28/255, 29/255)
my_green = (13/255, 119/255, 9/255)
my_white = (48/255, 48/255, 48/255)
my_black = (31/255, 31/255, 31/255)

np.seterr(divide='ignore', invalid='ignore')
plt.rcParams['axes.unicode_minus'] = False
fig = plt.figure(figsize=(19, 11), dpi=80, facecolor=my_black)

# https://stackoverflow.com/a/74628882
def request_binance(ticker, interval='4h', limit=300):
    columns = ['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time',
               'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol', 'ignore']
    url = f'https://www.binance.com/api/v3/klines?symbol={ticker}&interval={interval}&limit={limit}'
    data = pd.DataFrame(requests.get(url).json(), columns=columns, dtype=float)
    data.open_time = [pd.to_datetime(x, unit='ms').strftime(
        '%Y-%m-%d %H:%M:%S') for x in data.open_time]
    data.rename(columns={'volume': 'vol'}, inplace=True)
    usecols = ['open_time', 'open', 'high', 'low', 'close', 'vol']
    data = data[usecols]
    return data

def query(name):
    name = name.upper()
    currence_data = request_binance(name, '1h')
    if len(currence_data) == 0:
        print('No data')
        return
        
    currence_data['open_time'] = pd.to_datetime(currence_data['open_time'])
    currence_data = currence_data.set_index('open_time')
    l_xlim = len(currence_data.index)

    Grids = gridspec.GridSpec(4, 1, left=0.08, bottom=0.15, right=1,
                              top=0.96, wspace=None, hspace=0, height_ratios=[4, 1.5, 1, 1])

    KAV = fig.add_subplot(Grids[0, :])
    VOL = fig.add_subplot(Grids[1, :])
    MACD = fig.add_subplot(Grids[2, :])
    KDJ = fig.add_subplot(Grids[3, :])

    KAV.set_facecolor(my_black)
    KAV.grid(True, color=my_white)

    VOL.set_facecolor(my_black)
    VOL.grid(True, color=my_white)

    MACD.set_facecolor(my_black)
    MACD.grid(True, color=my_white)

    KDJ.set_facecolor(my_black)
    KDJ.grid(True, color=my_white)

    mpl.candlestick2_ochl(KAV, currence_data.open, currence_data.close, currence_data.high, currence_data.low, width=0.5,
                          colorup=my_green, colordown=my_red)

    currence_data['MA10'] = currence_data.close.rolling(window=10).mean()
    currence_data['MA30'] = currence_data.close.rolling(window=30).mean()
    currence_data['MA60'] = currence_data.close.rolling(window=60).mean()

    KAV.plot(np.arange(0, l_xlim),
             currence_data['MA10'], 'green', label='M10', lw=0.9)
    KAV.plot(np.arange(0, l_xlim),
             currence_data['MA30'], 'pink', label='M30', lw=0.9)
    KAV.plot(np.arange(0, l_xlim),
             currence_data['MA60'], 'yellow', label='M60', lw=0.9)

    KAV.set_facecolor(my_black)
    KAV.grid(True, color=my_white)

    KAV.legend(loc='best')
    KAV.set_title(name, color='white')
    KAV.set_ylabel(u"PRICE", color='white')
    KAV.set_xlim(0, l_xlim)

    VOL.bar(np.arange(0, l_xlim), currence_data.vol, color=[
        my_green if currence_data.open[x] > currence_data.close[x] else my_red for x in range(0, l_xlim)])


    VOL.set_ylabel(u"VOLUME")
    VOL.yaxis.label.set_color("white")
    VOL.set_xlim(0, l_xlim)
    VOL.set_xticks(range(0, l_xlim, 12))

    MACD_dif, MACD_dea, MACD_bar = talib.MACD(
        currence_data['close'].values, fastperiod=13, slowperiod=28, signalperiod=10)
    MACD.plot(np.arange(0, l_xlim),
              MACD_dif, 'pink', label='MACD dif')
    MACD.plot(np.arange(0, l_xlim),
              MACD_dea, 'yellow', label='MACD dea')

    red_where = np.where(MACD_bar >= 0, 2 * MACD_bar, 0)
    green_where = np.where(MACD_bar < 0, 2 * MACD_bar, 0)
    MACD.bar(np.arange(0, l_xlim),
             red_where, facecolor=my_red)
    MACD.bar(np.arange(0, l_xlim),
             green_where, facecolor=my_green)

    MACD.legend(loc='best', shadow=True, fontsize='10')
    MACD.set_ylabel(u"MACD", color='white')
    MACD.set_xlim(0, l_xlim)
    MACD.set_xticks(
        range(0, l_xlim, 15))
    currence_data['K'], currence_data['D'] = talib.STOCH(currence_data.high.values, currence_data.low.values, currence_data.close.values,
                                                         fastk_period=9, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
    currence_data['J'] = 3 * currence_data['K'] - 2 * currence_data['D']

    KDJ.plot(np.arange(0, l_xlim),
             currence_data['K'], 'b--', label='K')
    KDJ.plot(np.arange(0, l_xlim),
             currence_data['D'], 'g--', label='D')
    KDJ.plot(np.arange(0, l_xlim),
             currence_data['J'], 'r--', label='J')

    KDJ.legend(loc='best', shadow=True, fontsize=9)
    KDJ.set_ylabel(u"KDJ", color='white')
    KDJ.set_xlim(0, l_xlim)
    KDJ.set_xticks(range(0, l_xlim, 15))
    KDJ.set_xticklabels(
        [currence_data.index.strftime('%m-%d %H:%M')[index] for index in KDJ.get_xticks()])

    for label in KDJ.yaxis.get_ticklabels():
        label.set_color("white")
    for label in KAV.yaxis.get_ticklabels():
        label.set_color("white")
    for label in MACD.yaxis.get_ticklabels():
        label.set_color("white")
    for label in VOL.yaxis.get_ticklabels():
        label.set_color("white")


    for label in KAV.xaxis.get_ticklabels():
        label.set_visible(False)
    for label in VOL.xaxis.get_ticklabels():
        label.set_visible(False)
    for label in MACD.xaxis.get_ticklabels():
        label.set_visible(False)

    for label in KDJ.xaxis.get_ticklabels():
        label.set_rotation(30)
        label.set_color("white")
        label.set_fontsize(9)
    plt.savefig('kl.jpg')
    # plt.show()


# query('BTCUSDT')