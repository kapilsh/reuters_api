import argparse
import logging
import os
import pandas as pd
from pandas.tseries.offsets import BDay
import datetime
import pysftp
import re

from .. import reuters_data_dir, server_ip, remote_dir


def main():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    parser = argparse.ArgumentParser(
        description="Download Reuters data from the configured server",
        epilog="Example : reuters_download -i ED -s 20160101 -e 20160104 -v "
               "-u ksharma -p *******")
    parser.add_argument("-v", "--verbose", help="Verbose output",
                        action='store_true', dest='verbose')
    parser.add_argument("-u", "--username",
                        help="Username to connect to reuters data server",
                        action="store", type=str, dest="username")
    parser.add_argument("-p", "--password",
                        help="Password to connect to reuters data server",
                        action="store", type=str, dest="password")
    parser.add_argument("-i", "--instruments",
                        help="Instruments for which data is needed. "
                             "Separate multiple instruments by ,",
                        action="store", type=str, dest="instruments")
    parser.add_argument("-d", "--dir", help="Directory to save data",
                        action="store", type=str, dest="dir")
    parser.add_argument('-s', '--start', help='Start date for data in format '
                                              'YYYYMMDD', action='store',
                        type=str, dest='start_date')
    parser.add_argument('-e', '--end',
                        help='End date for data in format YYYYMMDD',
                        action='store', type=str, dest='end_date')

    options = parser.parse_args()
    missing_args = not all((options.username, options.password,
                            options.instruments))

    if missing_args:
        if options.verbose is True:
            logger.error("Missing required arguments")
        parser.print_help()
    else:
        server_address = server_ip
        save_dir = options.dir if options.dir else \
            os.path.expanduser(reuters_data_dir)
        cache_dir = os.path.abspath(os.path.join(save_dir, "../cache"))

        for the_file in os.listdir(cache_dir):
            file_path = os.path.join(cache_dir, the_file)
            try:
                if os.path.isfile(file_path):
                    if options.verbose:
                        logger.info("Removing {} from cache directory".format(
                            file_path))
                    os.unlink(file_path)
            except Exception as e:
                logger.error("Failed to delete file in cache directory with "
                             "error - {}", e)

        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        if options.verbose:
            logger.info("Saving data to {}".format(save_dir))
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        start_date = options.start_date if options.start_date else \
            pd.datetime.today() - BDay(1)
        if isinstance(start_date, str):
            try:
                start_date = datetime.datetime.strptime(start_date, '%Y%m%d')
            except ValueError as err:
                logger.error("Failed to parser start date. Error message - ",
                             err)

        end_date = options.end_date if options.end_date else start_date
        if isinstance(end_date, str):
            try:
                end_date = datetime.datetime.strptime(end_date, '%Y%m%d')
            except ValueError as err:
                logger.error("Failed to parser end date. Error message - ",
                             err)

        if options.verbose:
            logger.info("Connecting to server ip " + server_address)
            logger.info("Saving to " + save_dir)
            logger.info("Start date: " + start_date.strftime('%Y-%m-%d'))
            logger.info("End date: " + end_date.strftime('%Y-%m-%d'))

        instruments = options.instruments.split(',')
        if options.verbose:
            logger.info("Instruments " + str(instruments))

        connection = None
        try:
            connection = pysftp.Connection(server_address,
                                           username=options.username,
                                           password=options.password)
        except (pysftp.ConnectionException,
                pysftp.CredentialException,
                pysftp.SSHException,
                pysftp.AuthenticationException) as e:
            logger.error("Sftp connection error. Error message: ", e)
            connection.close()
            return

        wd = os.getcwd()
        os.chdir(cache_dir)

        for dt in pd.date_range(start=start_date, end=end_date, freq='D'):
            if options.verbose:
                logger.info("Downloading data for date " + dt.strftime('%Y-%m-%d'))
            date_dir = remote_dir + dt.strftime('%Y.%m.%d')
            with connection.cd():
                if connection.exists(date_dir):
                    connection.chdir(date_dir)
                    files = connection.listdir()
                    for inst in instruments:
                        r = re.compile("\\d{4}\\.\\d{2}\\.\\d{2}\\." + inst +
                                       "(BF)*[FGHJKMNQUVXZ]\\S*\\d\\.csv\\.gz")
                        inst_files = [f for f in files if r.match(f)]
                        if options.verbose:
                            logger.info("Found {0} files on the server "
                                        "for {}".format(len(inst_files), inst))
                            logger.info("Downloading data for " + str(inst))
                            logger.info("Found " + str(len(inst_files)) +
                                        ' files')

                        for filename in inst_files:
                            to_move = os.path.abspath(filename)
                            dest_dir = os.path.join(save_dir,
                                                    dt.strftime('%Y%m%d'))
                            dest_file = os.path.join(dest_dir, filename)
                            if not os.path.exists(dest_dir):
                                os.makedirs(dest_dir)
                            if not os.path.exists(dest_file):
                                connection.get(filename)
                                downloaded_file = os.path.join('.', to_move)
                                if os.path.isfile(downloaded_file):
                                    if options.verbose:
                                        logger.info("Moving " +
                                                    str(downloaded_file) +
                                                    " to " + str(dest_file))
                                    os.rename(downloaded_file, dest_file)

        os.chdir(wd)

        if connection is not None:
            connection.close()

if __name__ == '__main__':
    main()
