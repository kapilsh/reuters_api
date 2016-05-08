import logging
import tables
import datetime
import argparse
import os
import re
from .. import reuters_data_dir, hdf5_dir

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

    usage = "usage: %prog [options] arg1 arg2"
    parser = argparse.ArgumentParser(usage=usage)
    parser.add_argument("-q", "--quiet",
                        help="don't print log messages to stdout",
                        action='store_false', default=True, dest='verbose')
    parser.add_argument("-i", "--instruments",
                        help="Instruments to be comnverted to hdf5"
                        "separate instruments by ,",
                        action="store", type="string", dest="dest")
    parser.add_argument("-r", "--raw_path",
                        help="Path with dated folders for tick data",
                        action="store", type="string", dest="data_path")
    parser.add_argument("-d", "--destination", help="Destination directory",
                        action="store", type="string", dest="dest_path")

    options = parser.parse_args()

    missing_args = not options.instruments

    if not missing_args:
        instruments = options.instruments.split(',')

    data_path = options.data_path if options.data_path else \
        os.path.expanduser(reuters_data_dir)
    dest_path = options.dest_path if options.dest_path else \
        os.path.expanduser(hdf5_dir)
    date_match = re.compile("d{8}")
    dated_dirs = [x for x in os.listdir(data_path) if date_match.match(x)]


if __name__ == '__main__':
    main()