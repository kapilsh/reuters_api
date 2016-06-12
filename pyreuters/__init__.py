"""pyreuters package to read and store Reuters market data.
"""

import tables
import json
from pkg_resources import resource_filename

__version__ = '0.0.15'
__package__ = 'pyreuters'


hdf_repos_filters = tables.Filters(complevel=1, complib='zlib')


with open(resource_filename(__name__, './resources/symbols.json')) as \
        data_file:
    symbols = json.load(data_file)

with open(resource_filename(__name__, './resources/server_config.json')) as \
        data_file:
    server_config = json.load(data_file)

server_ip = server_config["server"]["server_ip"]

remote_dir = server_config["server"]["server_dir"]

reuters_data_dir = server_config["local_machine"]["reuters_data_dir"]

hdf5_dir = server_config["local_machine"]["hdf5_dir"]
