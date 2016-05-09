import tables

__version__ = '0.0.7'
__package__ = 'pyreuters'


server_ip = "10.10.100.222"

remote_dir = "/home/storage/csv/"

reuters_data_dir = "~/dev/reuters/data"

# Direct
hdf5_dir = "~/dev/reuters"

# FIlters used in H5 files
hdf_repos_filters = tables.Filters(complevel=1, complib='zlib')
