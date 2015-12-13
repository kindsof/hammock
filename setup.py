#! /bin/python
import os
import setuptools


def read(fname):
    path = os.path.join(os.path.dirname(__file__), fname)
    return open(path).read() if os.path.exists(path) else ""


setuptools.setup(
    name="hammock",
    version="0.0.1",
    author="Eyal Posener",
    author_email="eyal@stratoscale.com",
    description=("a good place to REST"),
    license="Apache Software License",
    keywords="REST",
    url="http://packages.python.org/hammock",
    packages=setuptools.find_packages(exclude=['tests', 'tests.*']),
    long_description=read('README.md'),
    include_package_data=True,
)
