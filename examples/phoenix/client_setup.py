#! /usr/bin/env python
"""Phoenix client setup, used to create the client's RPM"""
import setuptools


setuptools.setup(
    name='phoenix-client',
    version='0.0.1',
    author='Stratoscale',
    author_email='stratoscale@stratoscale.com',
    description=('Disaster Recovery Client'),
    keywords='phoenix disaster recovery client',
    url='http://packages.python.org/phoenix',
    packages=['phoenix_client', ],
)
