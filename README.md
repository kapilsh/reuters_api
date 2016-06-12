# PyReuters

### Overview

pyreuters provides an API to access reuters market data stored on a remote server.

### Features

1. Command line tools to download data, convert to hdf5 and search remote server
for symbols
2. Functions to read raw market data file, quotes and trades
3. Functions to clean quotes and trades data
4. `Symbol` API to read the load market data for a particular symbol

### Command Line Tools

###### reuters_download

`
$ reuters_download --help
`

```

usage: reuters_download [-h] [-v] [-n NETWORK_IP] [-u USERNAME] [-p PASSWORD]
                        [-i INSTRUMENTS] [-d DIR] [-s START_DATE]
                        [-e END_DATE]

Download Reuters data from the configured server

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Verbose output
  -n NETWORK_IP, --network_ip NETWORK_IP
                        IP address of the server
  -u USERNAME, --username USERNAME
                        Username to connect to reuters data server
  -p PASSWORD, --password PASSWORD
                        Password to connect to reuters data server
  -i INSTRUMENTS, --instruments INSTRUMENTS
                        Instruments for which data is needed. Separate
                        multiple instruments by ,
  -d DIR, --dir DIR     Directory to save data
  -s START_DATE, --start START_DATE
                        Start date for data in format YYYYMMDD
  -e END_DATE, --end END_DATE
                        End date for data in format YYYYMMDD

Example : reuters_download -i ED -s 20160101 -e 20160104 -v -u ksharma -p
*******

```

###### reuters_convert

`
$ reuters_convert --help
`

```
usage: reuters_convert [-h] [-v] [-i INSTRUMENTS] [-k] [-s SYMBOLS]
                       [-e EXCHANGE] [-r DATA_PATH] [-d DEST_PATH]

Convert the raw data files into hdf5 format

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Verbose output for the conversion
  -i INSTRUMENTS, --instruments INSTRUMENTS
                        Instruments to be converted to hdf5separate
                        instruments by ,
  -k, --keep_ric        Keep the RIC symbol as hdf5 filename
  -s SYMBOLS, --symbols SYMBOLS
                        json config file for symbols. Overrides the package
                        symbols config
  -e EXCHANGE, --exchange EXCHANGE
                        Add exchange acronym in hdf5 filename
  -r DATA_PATH, --raw_path DATA_PATH
                        Path with dated folders for tick data
  -d DEST_PATH, --destination DEST_PATH
                        Destination directory

Example : reuters_convert -i ED

```

###### reuters_search

`
$ reuters_search --help
`

```
usage: reuters_search [-h] [-v] [-n NETWORK_IP] -u USERNAME -p PASSWORD
                      [-d DATE] [-g GREP]

Download Reuters data from the configured server

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Verbose output
  -n NETWORK_IP, --network_ip NETWORK_IP
                        IP address of the server
  -u USERNAME, --username USERNAME
                        Username to connect to reuters data server
  -p PASSWORD, --password PASSWORD
                        Password to connect to reuters data server
  -d DATE, --date DATE  Date to check in format YYYYMMDD
  -g GREP, --grep GREP  Search for a particular word

Example : reuters_search -d 20160104 -v -u ksharma -p ******* -g NG

```

