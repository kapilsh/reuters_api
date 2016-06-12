# PyReuters

### Overview

pyreuters provides an API to access reuters market data stored on a remote server.

###### Version Info

Release v1.0.0: v1.0.0. would be a major release.

It would be one and only feature release. No new features will be added afterwards. Later versions will only be bug fixes.

-------------------------

### Features

- [x] Command line tools to download data, convert to hdf5 and search remote server
for symbols
- [x]  Functions to read raw market data file, quotes and trades
- [ ]  Functions to clean quotes and trades data
- [ ]  `Symbol` API to load market data for a particular symbol, and merge quotes and trades data

-------------------------

### Command Line Tools

###### reuters_download

```
$ reuters_download --help
```

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

```
$ reuters_convert --help
```

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

```
$ reuters_search --help
```

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
-------------------------

### Reading Raw Data

```
In[1] import pyreuters.data as reuters

In[2] reuters.read_raw("NGQ6", "2016-01-03")[:1]
Out[2]:
                            #RIC      Date[G]          Time[G]  GMT Offset  \
DateTime
2016-01-03 17:00:04.259805  NGQ6  03-JAN-2016  17:00:04.259805          -5

                                  Type  Price  Volume  Bid Price  Bid Size  \
DateTime
2016-01-03 17:00:04.259805  Correction    0.0     NaN        NaN       NaN

                            Ask Price  Ask Size  \
DateTime
2016-01-03 17:00:04.259805        NaN       NaN

                                                                   Qualifiers  \
DateTime
2016-01-03 17:00:04.259805    [CLSRNGTP];   [IRGCOND];   [MKT_ST_IND];  [O...

                            New Price  New Vol
DateTime
2016-01-03 17:00:04.259805        NaN      NaN
```

```
In[3] reuters.quotes_data(symbol="NGQ6", date="2016-01-03")[:1]
Out[3]:
                            Bid  BidSize    Ask  AskSize
DateTime
2016-01-03 20:00:31.929364  NaN      NaN  2.594      1.0
```

```
In[4]: reuters.trades_data(symbol="NGQ6", date="2016-01-03")[:1]
Out[4]:
                            Price  Volume
DateTime
2016-01-03 23:08:03.323453    NaN     1.0
```
-------------------------

### Configuration

Default configuration is provided with package distribution. `json` config can be found in `pyreuters/resources`. These config files can be changed to have user's own settings before/after install.

###### server_config.json

Change settings for server and local machine.

- Used by `reuters_download` to point to a particular network ip.
- Used by `reuters_convert` to access files for hdf5 conversion.
- Provides the default directory for functions that read raw files


```
{
  "local_machine": {
    "reuters_data_dir": "~/dev/reuters/data",
    "hdf5_dir": "~/dev/reuters"
  },
  "server": {
    "server_ip": "10.10.100.222",
    "server_dir": "/home/storage/csv/"
  }
}
```


###### symbols.json

Allows user to save symbol specific market data files with actual exchange symbols and not the `RIC` code

```
{
  "NG": "NG",
  "CL": "CL",
  "HO": "HO",
  "NTG": "NN",
  "BZZ": "BZ",
  "ED": "GE",
  "GE": "GE"
}
```