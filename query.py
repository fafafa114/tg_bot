import requests
import talib
import pandas as pd
import numpy as np
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import mpl_finance as mpl
from mplfinance.original_flavor import candlestick_ohlc

my_red = (192/255, 28/255, 29/255)
my_green = (13/255, 119/255, 9/255)
my_white = (48/255, 48/255, 48/255)
my_black = (31/255, 31/255, 31/255)

np.seterr(invalid='ignore', divide='ignore')
plt.rcParams['axes.unicode_minus'] = False
fig = plt.figure(figsize=(22, 16), dpi=250, facecolor=my_black)

# modified from the code of https://stackoverflow.com/a/74628882
def request_binance(ticker, interval, limit=250):
    columns = ['time', 'open', 'high', 'low', 'close', 'vol', 'close_time',
               'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol', 'ignore']
    url = f'https://www.binance.com/api/v3/klines?symbol={ticker}&interval={interval}&limit={limit}'
    data = pd.DataFrame(requests.get(url).json(), columns=columns, dtype=float)
    data.time = [pd.to_datetime(x, unit='ms').strftime(
        '%Y-%m-%d %H:%M:%S') for x in data.time]
    usecols = ['time', 'open', 'high', 'low', 'close', 'vol']
    data = data[usecols]
    return data


def query(name, interval):
    name = name.upper()
    currence_data = request_binance(name, interval, 300)
    if len(currence_data) == 0:
        print('No data')
        return

    currence_data['time'] = pd.to_datetime(currence_data['time'])
    currence_data = currence_data.set_index('time')
    l_xlim = len(currence_data.index)

    Grids = gridspec.GridSpec(4, 1, left=0.04, bottom=0.04, right=1,
                              top=0.96, wspace=None, hspace=0, height_ratios=[5, 1, 1, 1])

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


    delta = currence_data.close[-1] - currence_data.close[0]
    delta_rate = (currence_data.close[-1] - currence_data.close[0]) / currence_data.close[0] * 100
    high = currence_data.high.max()
    high_rate = (high - currence_data.close[0]) / currence_data.close[0] * 100
    low = currence_data.low.min()
    low_rate = (low - currence_data.close[0]) / currence_data.close[0] * 100
    mpl.candlestick2_ochl(KAV, currence_data.open, currence_data.close, currence_data.high, currence_data.low, width=0.65,
                          colorup='g', colordown='r') # draw k line

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
    # set title as green string "sdfas" + red string "sdfas"

    KAV.legend(loc='best')
    KAV.text(0.3, 1.035, name + ' until ' + currence_data.index[-1].strftime('%Y/%m/%d %H:%M')+'(UTC)', color='white', fontsize=20, horizontalalignment='right', verticalalignment='top', transform=KAV.transAxes, fontweight='bold')
    KAV.text(0.42, 1.035, f'Delta: {delta:.2f} {delta_rate:.2f}%', color='g' if delta >= 0 else 'r', fontsize=20, horizontalalignment='left', verticalalignment='top', transform=KAV.transAxes, fontweight='bold')
    KAV.text(0.99, 1.035, f'High: {high:.2f} {high_rate:.2f}%    Low: {low:.2f} {low_rate:.2f}%', color='white', fontsize=20, horizontalalignment='right', verticalalignment='top', transform=KAV.transAxes, fontweight='bold')
    KAV.set_ylabel(u"PRICE", color='white', fontweight='bold')
    KAV.set_xlim(0, l_xlim)

    VOL.bar(np.arange(0, l_xlim), currence_data.vol, color=[
        my_green if currence_data.open[x] > currence_data.close[x] else my_red for x in range(0, l_xlim)])

    VOL.set_ylabel(u"VOLUME", color='white', fontweight='bold')
    VOL.set_xlim(0, l_xlim)
    VOL.set_xticks(range(0, l_xlim, 12))

    MACD_dif, MACD_dea, MACD_bar = talib.MACD(
        currence_data['close'].values, fastperiod=6, slowperiod=13, signalperiod=4.5)
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
    MACD.set_ylabel(u"MACD", color='white', fontweight='bold')
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
    KDJ.set_ylabel(u"KDJ", color='white', fontweight='bold')
    KDJ.set_xlim(0, l_xlim)
    KDJ.set_xticks(range(0, l_xlim, 15))
    KDJ.set_xticklabels(
        [currence_data.index.strftime('%m-%d %H:%M')[index] for index in KDJ.get_xticks()])

    for label in KDJ.yaxis.get_ticklabels():
        label.set_color("white")
        label.set_fontweight('bold')
    for label in KAV.yaxis.get_ticklabels():
        label.set_color("white")
        label.set_fontweight('bold')
    for label in MACD.yaxis.get_ticklabels():
        label.set_color("white")
        label.set_fontweight('bold')
    for label in VOL.yaxis.get_ticklabels():
        label.set_color("white")
        label.set_fontweight('bold')

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
        label.set_fontweight('bold')
    plt.savefig('kl.jpg')
    # plt.show()


# query('BTCUSDT')
