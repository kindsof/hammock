#! /usr/bin/env python
"""The centre of all activity in building, distributing, and installing the modules."""
import os
import setuptools
import phoenix.__main__ as phoenix_main

# Define the config dir path according to the user.
config_dir_path = phoenix_main.CONFIG_DIR_PATHS[0] if os.getuid() != 0 else phoenix_main.CONFIG_DIR_PATHS[1]

# Define the data files path according to the user.
data_files = [(config_dir_path, ['etc/uwsgi.yml']), ]
if os.getuid() == 0:
    data_files.append(('/usr/lib/systemd/system', ['etc/phoenix.service']))

setuptools.setup(
    name='phoenix',
    version='0.0.1',
    author='Stratoscale',
    author_email='stratoscale@stratoscale.com',
    description=('Disaster Recovery'),
    keywords='phoenix disaster recovery',
    url='http://packages.python.org/phoenix',
    packages=setuptools.find_packages(exclude=['tests', 'tests.*']),
    entry_points={'console_scripts': ['phoenix = phoenix.__main__:main', ], },
    install_requires=['falcon>=0.3', 'uwsgi>=2.0.11.2', ],
    include_package_data=True,
    data_files=data_files,
)
