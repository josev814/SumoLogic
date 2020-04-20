#!/usr/bin/env python3
# Built-in Libraries
from glob import glob
import sys
from os.path import join as ospj

# This requires pip to be installed to work
from distutils.core import setup

# Package Libraries
from SumoLogic.util import normalize_whitespace
from SumoLogic.version import VERSION


etcpath = "/etc/sumologic"
manpath = "/usr/share/man/man8"
libpath = "/usr/share/sumologic"
scriptspath = ospj("scripts", libpath)
pluginspath = ospj("plugins", libpath)
default_config = 'config'
sumologicman = 'sumologic.8'

if 'rpm' in sys.argv[1]:
    sumologicman += '.gz'

setup(
    name="SumoLogic",
    version=VERSION,
    description="SumoLogic is a utility to transfer log files to SumoLogic",
    author="Jose' Vargas",
    author_email="josev814@gmail.com",
    url="https://github.com/josev814/sumologic",
    scripts=['sumologic.py', 'sumologic-daemon'],
    package_dir={'SumoLogic': 'SumoLogic'},
    packages=["SumoLogic"],
    requires=['configparser', 'requests', 'pip',],
    data_files=[
        (etcpath, glob(default_config)),
        (manpath, glob(sumologicman)),
    ],
    license="GPL v2",
    long_description=normalize_whitespace(
        """
        SumoLogic is a python program that parses log files and sends them
        to defined SumoLogic endpoints.
        """
    ),
)
