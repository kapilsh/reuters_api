import tables

__version__ = '0.0.9'
__package__ = 'pyreuters'


server_ip = "10.10.100.222"

remote_dir = "/home/storage/csv/"

# HDF5 data directory
reuters_data_dir = "~/dev/reuters/data"

# HDF5 data directory
hdf5_dir = "~/dev/reuters"

# Filters used in H5 files
hdf_repos_filters = tables.Filters(complevel=1, complib='zlib')
