import pandas as pd
import numpy as np
import tables
import os

from . import hdf5_dir


class Symbol(object):
    def __init__(self, symbol, exchange=None, h5_dir=hdf5_dir,
                 tz="US/Central"):
        self.symbol = symbol
        self.exchange = exchange
        self.tz = tz
        filename = "{}.h5".format(symbol) if \
            exchange is None else "{}_{}.h5".format(exchange, symbol)
        self.hdf5_file = os.path.join(os.path.expanduser(h5_dir), filename)
        self.quotes = {}
        self.trades = {}

    def load(self, start_time, end_time):
        start_time = pd.Timestamp(start_time, tz=self.tz).value
        end_time = pd.Timestamp(end_time, tz=self.tz).value
        store = tables.open_file(self.hdf5_file, mode='r')
        existing = Symbol.available(self.hdf5_file)

        quote_tables = existing["Quote"]
        trade_tables = existing["Trade"]

        for qt in quote_tables:
            print("Loading quotes for {}".format(qt))
            node = store.get_node("/quotes", qt)
            data = pd.DataFrame(node.read_where(
                '(date_time >= {}) & (date_time < {})'.format(start_time,
                                                              end_time)))
            data["bid_size"] = data["bid_size"].astype(np.float64)
            data.loc[data["bid_size"] == -1, "bid_size"] = np.nan
            data["ask_size"] = data["ask_size"].astype(np.float64)
            data.loc[data["ask_size"] == -1, "ask_size"] = np.nan
            data.index = pd.DatetimeIndex(data.date_time.values,
                                          tz="UTC").tz_convert(self.tz)
            data = data[["bid", "bid_size", "ask", "ask_size"]]

            self.quotes[qt] = data

        for tt in trade_tables:
            print("Loading trades for {}".format(tt))
            node = store.get_node("/trades", tt)
            data = pd.DataFrame(node.read_where(
                '(date_time >= {}) & (date_time < {})'.format(start_time,
                                                              end_time)))

            data["volume"] = data["volume"].astype(np.float64)
            data.loc[data["volume"] == -1, "volume"] = np.nan
            data.index = pd.DatetimeIndex(data.date_time.values,
                                          tz="UTC").tz_convert(self.tz)
            data = data[["price", "volume"]]

            self.trades[tt] = data

        store.close()
        return self

    def load_contract(self, contract, start_time, end_time):
        start_time = pd.Timestamp(start_time, self.tz).value
        end_time = pd.Timestamp(end_time, self.tz).value
        store = tables.open_file(self.hdf5_file, mode='r')

        node = store.get_node("/quotes", contract)
        data = pd.DataFrame(node.read_where(
            '(date_time >= {}) & (date_time < {})'.format(start_time,
                                                          end_time)))

        data["bid_size"] = data["bid_size"].astype(np.float64)
        data.loc[data["bid_size"] == -1, "bid_size"] = np.nan
        data["ask_size"] = data["ask_size"].astype(np.float64)
        data.loc[data["ask_size"] == -1, "ask_size"] = np.nan
        data.index = pd.DatetimeIndex(data.date_time.values,
                                      tz="UTC").tz_convert(self.tz)
        data = data[["bid", "bid_size", "ask", "ask_size"]]

        self.quotes[contract] = data

        node = store.get_node("/trades", contract)
        data = pd.DataFrame(node.read_where(
            '(date_time >= {}) & (date_time < {})'.format(start_time,
                                                          end_time)))

        data["volume"] = data["volume"].astype(np.float64)
        data.loc[data["volume"] == -1, "volume"] = np.nan
        data.index = pd.DatetimeIndex(data.date_time.values,
                                      tz="UTC").tz_convert(self.tz)
        data = data[["price", "volume"]]

        self.trades[contract] = data

    def loaded_contracts(self, data_type="Quote"):
        if data_type is "Quote":
            return self.quotes.keys()
        if data_type is "Trade":
            return self.trades.keys()

    def merge_qt(self, contract=None):
        contracts = self.quotes.keys()
        if contract is not None:
            contracts = [contract]
        for cont in contracts:
            q = self.quotes[cont]
            t = self.trades[cont]
            qt = q.combine_first(t)
            self.quotes[cont] = qt
        return self

    def get_quotes(self, contract):
        if self.quotes.__contains__(contract):
            return self.quotes[contract]

    def get_trades(self, contract):
        if self.trades.__contains__(contract):
            return self.trades[contract]

    @staticmethod
    def available(hdf_file):
        store = tables.open_file(hdf_file, mode='r')
        quote_tables = [x.name for x in store.list_nodes("/quotes", "Table")]
        trade_tables = [x.name for x in store.list_nodes("/trades", "Table")]
        store.close()
        return {"Quote": quote_tables, "Trade": trade_tables}
