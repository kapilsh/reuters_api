import logging
import tables
import datetime
import numpy as np
import argparse
import os
import re
import json

from pyreuters.clean import clean_quotes, clean_trades
from ..data import Quote, Trade, read_raw, quotes_data, trades_data
from .. import reuters_data_dir, hdf5_dir, hdf_repos_filters, symbols


def main():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    parser = argparse.ArgumentParser(
        description="Convert the raw data files into hdf5 format",
        epilog="Example : reuters_convert -i ED")
    parser.add_argument("-v", "--verbose",
                        help="Verbose output for the conversion",
                        action='store_true', default=False, dest='verbose')
    parser.add_argument("-i", "--instruments",
                        help="Instruments to be converted to hdf5"
                        "separate instruments by ,",
                        action="store", type=str, dest="instruments")
    parser.add_argument("-k", "--keep_ric",
                        help="Keep the RIC symbol as hdf5 filename",
                        action="store_true", dest="keep_ric")
    parser.add_argument("-s", "--symbols",
                        help="json config file for symbols."
                             " Overrides the package symbols config",
                        action="store", type=str, dest="symbols")
    parser.add_argument("-e", "--exchange",
                        help="Add exchange acronym in hdf5 filename",
                        action="store", type=str, dest="exchange")
    parser.add_argument("-c", "--clean",
                        help="Clean the market data before saving",
                        action="store_true", dest="clean")
    parser.add_argument("-r", "--raw_path",
                        help="Path with dated folders for tick data",
                        action="store", type=str, dest="data_path")
    parser.add_argument("-d", "--destination", help="Destination directory",
                        action="store", type=str, dest="dest_path")

    options = parser.parse_args()

    missing_args = not options.instruments

    if missing_args:
        parser.print_help()
    else:
        instruments = options.instruments.split(',')

        data_path = options.data_path if options.data_path else \
            os.path.expanduser(reuters_data_dir)
        dest_path = options.dest_path if options.dest_path else \
            os.path.expanduser(hdf5_dir)
        date_match = re.compile("\\d{8}")
        dated_dirs = [x for x in os.listdir(data_path) if date_match.match(x)]
        for dr in np.sort(dated_dirs):
            if options.verbose:
                logger.info("Loading data for {}".format(dr))
            for instrument in instruments:
                if options.verbose:
                    logger.info("Converting data for {}".format(instrument))

                replace_symbols = symbols

                if options.symbols:
                    with open(options.config) as data_file:
                        replace_symbols = json.load(data_file)

                hdf_file = "{}.h5".format(replace_symbols[instrument])
                if options.keep_ric:
                    hdf_file = "{}.h5".format(instrument)

                if options.exchange:
                    hdf_file = "{}_{}".format(options.exchange, hdf_file)

                hdf_file = os.path.join(dest_path, hdf_file)

                if options.verbose:
                    logger.info("HDF5 File for {} : {}".format(instrument,
                                                               hdf_file))
                store = tables.open_file(hdf_file, mode='a',
                                         filters=hdf_repos_filters)
                if not store.__contains__("/quotes"):
                    if options.verbose:
                        logger.info("quotes node doesn not exist in the file."
                                    "Creating...")
                    store.create_group("/", "quotes", "Quotes Market Data")
                if not store.__contains__("/trades"):
                    if options.verbose:
                        logger.info("trades node doesn not exist in the file."
                                    "Creating...")
                    store.create_group("/", "trades", "Trades Market Data")

                dir = os.path.join(data_path, dr)
                date_files = np.array(os.listdir(dir))
                reg = re.compile("\\d{4}\\.\\d{2}\\.\\d{2}\\.(" + instrument +
                                 "(BF)*[FGHJKMNQUVXZ]\\S*\\d)\\.csv\\.gz")
                inst_files = [x for x in date_files if reg.match(x)]
                if options.verbose:
                    logger.info("Found {} files for {}".format(len(inst_files),
                                                               instrument))
                for f in inst_files:
                    contract = reg.match(f).group(1)
                    table_name = contract.replace(".", "_")

                    raw_data = None

                    quotes_group = store.get_node("/", "quotes")
                    if not quotes_group.__contains__(table_name):
                        if options.verbose:
                            logger.info(
                                "{} table does not exist in quotes group. "
                                "Creating...".format(table_name))
                        store.create_table(quotes_group, table_name, Quote,
                                           "Quotes data for {}".format(
                                               table_name))

                    table = store.get_node(quotes_group, table_name)
                    existing = np.array([str(x) for x in
                                np.unique(table.col('file_date'))])
                    date_exists = np.any(existing == dr)

                    if not date_exists:
                        raw_data = read_raw(symbol=contract,
                                            date=datetime.datetime.strptime(
                                                dr, "%Y%m%d"),
                                            path=reuters_data_dir,
                                            verbose=options.verbose,
                                            logger=logger)
                        quotes = quotes_data(raw_data=raw_data)
                        if options.clean:
                            quotes = clean_quotes(quotes)
                        num_rows = len(quotes.index)
                        if options.verbose:
                            logger.info("Adding {} new quotes to {}".format(
                                num_rows, hdf_file))
                        if num_rows > 0:
                            row = table.row
                            quotes['DateTime'] = quotes.index.astype(np.int64)
                            for index, q in quotes.iterrows():
                                row['file_date'] = int(dr)
                                row['date_time'] = q['date_time']
                                if not np.isnan(q['bid']):
                                    row['bid'] = float(q['bid'])
                                if not np.isnan(q['ask']):
                                    row['ask'] = float(q['ask'])
                                if not np.isnan(q['bid_size']):
                                    row['bid_size'] = int(q['bid_size'])
                                if not np.isnan(q['ask_size']):
                                    row['ask_size'] = int(q['ask_size'])
                                row.append()
                        table.flush()

                    trades_group = store.get_node("/", "trades")

                    if not trades_group.__contains__(table_name):
                        if options.verbose:
                            logger.info(
                                "{} table does not exist in the trades "
                                "group. Creating...".format(table_name))
                        store.create_table(trades_group, table_name, Trade,
                                           "Trades data for {}".format(
                                               table_name))

                    table = store.get_node(trades_group, table_name)
                    existing = np.array([str(x) for x in
                                np.unique(table.col('file_date'))])
                    date_exists = np.any(existing == dr)

                    if not date_exists:
                        row = table.row
                        if raw_data is None:
                            raw_data = read_raw(symbol=contract,
                                                date=datetime.datetime.strptime(
                                                    dr, "%Y%m%d"),
                                                path=reuters_data_dir,
                                                verbose=options.verbose,
                                                logger=logger)

                        trades = trades_data(raw_data=raw_data)
                        if options.clean:
                            trades = clean_trades(trades)
                        num_rows = len(trades.index)
                        if options.verbose:
                            logger.info("Adding {} new trades to {}".format(
                                num_rows, hdf_file))
                        if num_rows > 0:
                            trades['DateTime'] = trades.index.astype(np.int64)
                            for index, trd in trades.iterrows():
                                row['file_date'] = int(dr)
                                row['date_time'] = trd['date_time']
                                if not np.isnan(trd['volume']):
                                    row['volume'] = int(trd['volume'])
                                if not np.isnan(trd['price']):
                                    row['price'] = float(trd['price'])
                                row.append()
                        table.flush()

                store.flush()
                store.close()


if __name__ == '__main__':
    main()