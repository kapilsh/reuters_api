import pandas as pd
import tables
import os

from . import hdf5_dir


class Symbol(object):
    def __init__(self, symbol, exchange=None, h5_dir=hdf5_dir,
                 tz="US/Chicago"):
        self.symbol = symbol
        self.exchange = exchange
        self.tz = tz
        filename = "{}.h5".format(symbol) if \
            exchange is None else "{}_{}.h5".format(exchange, symbol)
        self.hdf5_file = os.path.join(os.path.expanduser(h5_dir), filename)
        self.quotes = {}
        self.trades = {}

    def load(self, start_time, end_time):
        start_time = pd.Timestamp(start_time, self.tz).value
        end_time = pd.Timestamp(end_time, self.tz).value
        store = tables.open_file(self.hdf5_file, mode='r')
        existing = Symbol.available(self.hdf5_file)

        quote_tables = existing["Quote"]
        trade_tables = existing["Trade"]

        for qt in quote_tables:
            node = store.get_node("/quotes", qt)
            data = pd.DataFrame(node.read_where(
                '(date_time >= {}) & (date_time < {})'.format(start_time.value,
                                                              end_time.value)))
            self.quotes[qt] = data

        for tt in trade_tables:
            node = store.get_node("/trades", tt)
            data = pd.DataFrame(node.read_where(
                '(date_time >= {}) & (date_time < {})'.format(start_time.value,
                                                              end_time.value)))
            self.trades[tt] = data

        store.close()
        return self

    def load_contract(self, contract, start_time, end_time):
        start_time = pd.Timestamp(start_time, self.tz).value
        end_time = pd.Timestamp(end_time, self.tz).value
        store = tables.open_file(self.hdf5_file, mode='r')

        node = store.get_node("/quotes", contract)
        data = pd.DataFrame(node.read_where(
            '(date_time >= {}) & (date_time < {})'.format(start_time.value,
                                                          end_time.value)))
        data.set_index("date_time")
        self.quotes[contract] = data

        node = store.get_node("/trades", contract)
        data = pd.DataFrame(node.read_where(
            '(date_time >= {}) & (date_time < {})'.format(start_time.value,
                                                          end_time.value)))
        data.set_index("date_time")
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
            qt = qt[['ask', 'ask_size', 'bif', 'bid_size', 'price', 'volume']]
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
