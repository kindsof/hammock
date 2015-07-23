#! /bin/python
import os
import setuptools


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setuptools.setup(
    name = "hammock",
    version = "0.0.1",
    author = "Stratoscale",
    author_email = "stratoscale@stratoscale.com",
    description = ("a good place to REST"),
    license = "BSD",
    keywords = "REST",
    url = "http://packages.python.org/hammock",
    packages=['hammock', 'hammock.testing'],
    long_description=read('README.md'),
)
