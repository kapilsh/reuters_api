from optparse import OptionParser
import logging
import os
import pandas as pd
from pandas.tseries.offsets import BDay
import datetime
import pysftp
import re

from .. import reuters_data_dir, server_ip, remote_dir


def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    print("*************** " + str(datetime.datetime.now()) + " ***************")

    usage = "usage: %prog [options] arg1 arg2"
    parser = OptionParser(usage=usage)
    parser.add_option("-v", "--verbose", help="Verbose output",
                      action='store_true', dest='verbose')
    parser.add_option("-u", "--username", help="Username to connect to sftp",
                      action="store", type="string", dest="username")
    parser.add_option("-p", "--password", help="Password to connect to sftp",
                      action="store", type="string", dest="password")
    parser.add_option("-i", "--instruments", help="Instruments for which data is needed. "
                                                  "Separate multiple instruments by ,",
                      action="store", type="string", dest="instruments")
    parser.add_option("-d", "--dir", help="Directory to save data",
                      action="store", type="string", dest="dir")
    parser.add_option('-s', '--start', help='Start date for data in format YYYYMMDD',
                      action='store', type='string', dest='start_date')
    parser.add_option('-e', '--end', help='End date for data in format YYYYMMDD',
                      action='store', type='string', dest='end_date')


    (options, args) = parser.parse_args()
    missing_args = not all((options.username, options.password, options.instruments))

    if missing_args:
        if options.verbose is True:
            logger.error("Missing required arguments")
        parser.print_help()
    else:
        server_address = server_ip
        save_dir = options.dir if options.dir else os.path.join(reuters_data_dir)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        start_date = options.start_date if options.start_date else pd.datetime.today() - BDay(1)
        if isinstance(start_date, str):
            try:
                start_date = datetime.datetime.strptime(start_date, '%Y%m%d')
            except ValueError as err:
                logger.error("Failed to parser start date. Error message - ", err)

        end_date = options.end_date if options.end_date else start_date
        if isinstance(end_date, str):
            try:
                end_date = datetime.datetime.strptime(end_date, '%Y%m%d')
            except ValueError as err:
                logger.error("Failed to parser end date. Error message - ", err)

        if options.verbose is True:
            logger.info("Connecting to server ip " + server_address)
            logger.info("Saving to " + save_dir)
            logger.info("Start date: " + start_date.strftime('%Y-%m-%d'))
            logger.info("End date: " + end_date.strftime('%Y-%m-%d'))

        instruments = options.instruments.split(',')
        if options.verbose is True:
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

        for dt in pd.date_range(start=start_date, end=end_date, freq='D'):
            logger.info("Downloading data for date " + dt.strftime('%Y-%m-%d'))
            date_dir = remote_dir + dt.strftime('%Y.%m.%d')
            with connection.cd():
                if connection.exists(date_dir):
                    connection.chdir(date_dir)
                    files = connection.listdir()
                    for inst in instruments:
                        r = re.compile("\\d{4}[.]\\d{2}[.]\\d{2}[.]" + inst +
                                       "[F|G|H|J|K|M|N|Q|U|V|X|Z][0-9][.]csv[.]gz")
                        inst_files = [f for f in files if r.match(f)]
                        if options.verbose is True:
                            logger.info("Downloading data for " + str(inst))
                            logger.info("Found " + str(len(inst_files)) + ' files')

                        for filename in inst_files:
                            to_move = os.path.abspath(filename)
                            dest_dir = os.path.join(save_dir, dt.strftime('%Y%m%d'))
                            dest_file = os.path.join(dest_dir, filename)
                            if not os.path.exists(dest_dir):
                                os.makedirs(dest_dir)
                            if not os.path.exists(dest_file):
                                connection.get(filename)
                                downloaded_file = os.path.join('.', to_move)
                                if os.path.isfile(downloaded_file):
                                    if options.verbose:
                                        logger.info("Moving " + str(downloaded_file) + " to " + str(dest_file))
                                    os.rename(downloaded_file, dest_file)

        if connection is not None:
            connection.close()

if __name__ == '__main__':
    main()