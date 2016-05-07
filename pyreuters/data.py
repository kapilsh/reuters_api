import pandas as pd
from pandas.tseries.offsets import BDay
import os
import datetime
import logging
from . import reuters_data_dir

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def read_raw(symbol, date=pd.datetime.today() - BDay(1),
             path=reuters_data_dir, verbose=False):
    if isinstance(date, str):
        date = datetime.datetime.strptime(date, '%Y-%m-%d')
    if isinstance(path, str):
        path = os.path.expanduser(path)
    date_dir = os.path.join(path, date.strftime('%Y%m%d'))
    to_read = os.path.join(date_dir, date.strftime("%Y.%m.%d") + '.' +
                           symbol + ".csv.gz")
    if verbose:
        logger.info("Reading market data file - {}".format(to_read))
    if os.path.exists(to_read):
        rd = pd.read_csv(to_read, compression='gzip')
        rd['DateTime'] = pd.to_datetime(rd['Date[G]'] + " " + rd['Time[G]'],
                                        format='%d-%b-%Y %H:%M:%S.%f')
        rd.set_index('DateTime', inplace=True)
        return rd
    else:
        return None


def quotes_data(symbol, **kargs):
    date = None
    path = None

    if 'date' in kargs.keys():
        date = kargs['date']

    if 'path' in kargs.keys():
        path = kargs['path']

    if date is None and path is None:
        tick_data = read_raw(symbol=symbol)
    else:
        if date is None:
            tick_data = read_raw(symbol=symbol, path=path)
        else:
            if path is None:
                tick_data = read_raw(symbol=symbol, date=date)
            else:
                tick_data = read_raw(symbol=symbol, date=date, path=path)

    if tick_data is not None:
        qd = tick_data[tick_data.Type == 'Quote']
        qd = qd[['Bid Price', 'Bid Size', 'Ask Price', 'Ask Size']]
        qd.columns = ['Bid', 'BidSize', 'Ask', 'AskSize']
        return qd
    else:
        return None


def trades_data(symbol, **kargs):
    date = None
    path = None

    if 'date' in kargs.keys():
        date = kargs['date']

    if 'path' in kargs.keys():
        path = kargs['path']

    tick_data = None

    if date is None and path is None:
        tick_data = read_raw(symbol=symbol)
    else:
        if date is None:
            tick_data = read_raw(symbol=symbol, path=path)
        else:
            if path is None:
                tick_data = read_raw(symbol=symbol, date=date)
            else:
                tick_data = read_raw(symbol=symbol, date=date, path=path)

    if tick_data is not None:
        td = tick_data[tick_data.Type == 'Trade']
        td = td[['Price', 'Volume']]
        return td
    else:
        return None
