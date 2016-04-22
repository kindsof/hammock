#! /usr/bin/env python


import os
import setuptools


def read(fname):
    path = os.path.join(os.path.dirname(__file__), fname)
    return open(path).read() if os.path.exists(path) else ''


setuptools.setup(
    name='hammock-rest',
    version='0.0.1',
    author='Eyal Posener',
    author_email='eyal@stratoscale.com',
    description='A good place to REST',
    license='Apache License 2.0',
    keywords='REST',
    url='http://github.com/stratoscale/hammock.git',
    packages=setuptools.find_packages(exclude=['tests']),
    long_description=read('README.md'),
    include_package_data=True,
    install_requires=[
        'falcon==0.3.0',
        'requests==2.7.0',
        'ujson==1.33',
        'six==1.9.0',
        'munch==2.0.3',
        'decorator==4.0.6',
        'oslo.policy==0.11.0',
        'jinja2==2.8',

        # TODO: The following should be moved to extras_requires['client']
        'cliff==1.15.0',
        'coloredlogs==5.0',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
    ],
)
