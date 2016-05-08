import logging
import tables
import datetime
import argparse
import os
import re
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
        for dr in dated_dirs:
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
                root = store.root

if __name__ == '__main__':
    main()