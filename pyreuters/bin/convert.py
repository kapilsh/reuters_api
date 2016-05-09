import logging
import tables
import datetime
import numpy as np
import argparse
import os
import re

from ..data import Quote, Trade, read_raw, quotes_data, trades_data
from .. import reuters_data_dir, hdf5_dir, hdf_repos_filters

# TODO
# load all the filenames for a date
# check the if the combination of symbol and file_date exists
# if not then read quotes and trades
# insert quotes and trades


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
                        help="Instruments to be comnverted to hdf5"
                        "separate instruments by ,",
                        action="store", type=str, dest="instruments")
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
                hdf_file = os.path.join(dest_path, "{}.h5".format(instrument))
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
                for file in inst_files:
                    contract = reg.match(file).group(1)
                    table_name = contract.replace(".", "_")

                    raw_data = None

                    quotes_group = store.get_node("/", "quotes")
                    if not quotes_group.__contains__(table_name):
                        if options.verbose:
                            logger.info(
                                "{} table does not exist in quotes group"
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
                        num_rows = len(quotes.index)
                        if options.verbose:
                            logger.info("Adding {} new quotes to {}".format(
                                num_rows, hdf_file))
                        if num_rows > 0:
                            row = table.row
                            quotes['DateTime'] = quotes.index.astype(np.int64)
                            for index, q in quotes.iterrows():
                                row['file_date'] = int(dr)
                                row['date_time'] = q['DateTime']
                                row['bid'] = -1.0 if np.isnan(
                                    q['Bid']) else float(q['Bid'])
                                row['ask'] = -1.0 if np.isnan(
                                    q['Ask']) else float(q['Ask'])
                                row['bid_size'] = -1 if np.isnan(
                                    q['BidSize']) else int(q['BidSize'])
                                row['ask_size'] = -1.0 if np.isnan(
                                    q['AskSize']) else int(q['AskSize'])
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
                        num_rows = len(trades.index)
                        if options.verbose:
                            logger.info("Adding {} new trades to {}".format(
                                num_rows, hdf_file))
                        if num_rows > 0:
                            trades['DateTime'] = trades.index.astype(np.int64)
                            for index, trd in trades.iterrows():
                                row['file_date'] = int(dr)
                                row['date_time'] = trd['DateTime']
                                row['volume'] = -1 if np.isnan(
                                    trd['Volume']) else int(trd['Volume'])
                                row['price'] = -1.0 if np.isnan(
                                    trd['Volume']) else float(trd['Price'])
                                row.append()
                        table.flush()

                store.flush()
                store.close()


if __name__ == '__main__':
    main()