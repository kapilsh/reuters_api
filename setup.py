from setuptools import setup, find_packages
from pyreuters import __version__, __package__


def readme():
    with open('README.rst') as f:
        return f.read()


setup(
    name=__package__,
    version=__version__,
    description='Python API To Read Reuters Market Data file',
    author='Kapil Sharma',
    author_email='ksharma@dvtrading.co',
    packages=find_packages(),
    install_requires=[
        'pandas>=0.18',
        'numpy>=1.10',
        'pytables'
    ],
    entry_points={
        'console_scripts':
            ["reuters_download=pyreuters.bin.download:main"]
    },
    package_data={
        '': ['*.json']
    },
    zip_safe=False
)