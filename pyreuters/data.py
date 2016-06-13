import pandas as pd
from pandas.tseries.offsets import BDay
import numpy as np
import os
import datetime

from tables.description import IsDescription, Float64Col, UInt64Col, UInt32Col, \
    Int32Col, Int64Col

from . import reuters_data_dir


def read_raw(symbol, date=pd.datetime.today() - BDay(1),
             path=reuters_data_dir, verbose=False, logger=None):
    if isinstance(date, str):
        date = datetime.datetime.strptime(date, '%Y-%m-%d')

    path = os.path.expanduser(path)

    date_dir = os.path.join(path, date.strftime('%Y%m%d'))
    to_read = os.path.join(date_dir, date.strftime("%Y.%m.%d") + '.' +
                           symbol + ".csv.gz")
    if verbose and logger is not None:
        logger.info("Reading market data file - {}".format(to_read))
    if os.path.exists(to_read):
        rd = pd.read_csv(to_read, compression='gzip')
        rd['date_time'] = pd.to_datetime(rd['Date[G]'] + " " + rd['Time[G]'],
                                        format='%d-%b-%Y %H:%M:%S.%f')
        rd.set_index('date_time', inplace=True)
        return rd
    else:
        return None


def quotes_data(symbol=None, **kargs):
    date = None
    path = None

    tick_data = None

    if 'raw_data' in kargs.keys():
        tick_data = kargs["raw_data"]

    if 'date' in kargs.keys():
        date = kargs['date']

    if 'path' in kargs.keys():
        path = kargs['path']

    if tick_data is None:
        if symbol is None:
            return None
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
        qd.columns = ['bid', 'bid_size', 'ask', 'ask_size']
        return qd
    else:
        return None


def trades_data(symbol=None, **kargs):
    date = None
    path = None

    tick_data = None

    if 'raw_data' in kargs.keys():
        tick_data = kargs["raw_data"]

    if 'date' in kargs.keys():
        date = kargs['date']

    if 'path' in kargs.keys():
        path = kargs['path']

    if tick_data is None:
        if symbol is None:
            return None
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
        td = td[['price', 'volume']]
        return td
    else:
        return None


class Quote(IsDescription):
    file_date = UInt32Col(dflt=0)
    date_time = Int64Col()
    bid = Float64Col(dflt=np.NaN)
    ask = Float64Col(dflt=np.NaN)
    bid_size = Int64Col(dflt=-1)
    ask_size = Int64Col(dflt=-1)


class Trade(IsDescription):
    file_date = UInt32Col(dflt=0)
    date_time = Int64Col()
    price = Float64Col(dflt=np.NaN)
    volume = Int64Col(dflt=-1)
