#! /bin/python
import os
import setuptools


def read(fname):
    path = os.path.join(os.path.dirname(__file__), fname)
    return open(path).read() if os.path.exists(path) else ""


setuptools.setup(
    name="hammock",
    version="0.0.1",
    author="Stratoscale",
    author_email="stratoscale@stratoscale.com",
    description=("a good place to REST"),
    license="BSD",
    keywords="REST",
    url="http://packages.python.org/hammock",
    packages=['hammock', 'hammock.testing'],
    long_description=read('README.md'),
)
