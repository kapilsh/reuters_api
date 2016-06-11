import argparse
import logging
import os
import pandas as pd
import numpy as np
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
        epilog="Example : reuters_search -d 20160104 -v -u ksharma -p *******")
    parser.add_argument("-v", "--verbose", help="Verbose output",
                        action='store_true', dest='verbose')
    parser.add_argument("-n", "--network_ip", help="IP address of the server",
                        type=str, dest='network_ip', default=server_ip)
    parser.add_argument("-u", "--username", required=True,
                        help="Username to connect to reuters data server",
                        action="store", type=str, dest="username")
    parser.add_argument("-p", "--password", required=True,
                        help="Password to connect to reuters data server",
                        action="store", type=str, dest="password")
    parser.add_argument("-d", "--date", help="Date to check in format YYYYMMDD",
                        action="store", type=str, dest="date")
    parser.add_argument("-g", "--grep", help="Search for a particular word",
                        action="store", type=str, dest="grep")

    options = parser.parse_args()

    server_address = server_ip if options.network_ip else options.network_ip

    date = options.date if options.date else pd.datetime.today() - BDay(1)
    if isinstance(date, str):
        try:
            date = datetime.datetime.strptime(date, '%Y%m%d')
        except ValueError as err:
            logger.error("Failed to parser start date. Error message - ",
                         err)

    if options.verbose:
        logger.info("Connecting to server ip " + server_address)
        logger.info("Date: " + date.strftime('%Y-%m-%d'))

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

    date_dir = remote_dir + date.strftime('%Y.%m.%d')
    with connection.cd():
        if connection.exists(date_dir):
            connection.chdir(date_dir)
            files = connection.listdir()
            instruments = [f[11:][:-7].replace("\.", "_") for f in files]
            if options.grep:
                if options.verbose:
                    logger.info("Filtering for {}".format(options.grep))
                reg = re.compile(options.grep)
                instruments = [x for x in instruments if reg.search(x)]
            for inst in instruments:
                print(inst)
    if connection is not None:
        connection.close()

if __name__ == '__main__':
    main()
