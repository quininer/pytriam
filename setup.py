#!/usr/bin/env python
# encoding: utf-8

from distutils.core import setup
from os import path

setup(
    name='pytriam',
    version='0.1',
    description='PyTox API wrapper.',
    author='quininer kel',
    author_email='quininer@live.com',
    url='https://github.com/quininer/pytriam',
    license='GPLv3',
    long_description=open(path.join(
        path.split(path.abspath(__file__))[0],
        'README.md'
    )).read(),
    packages=['pytriam'],
    requires=['pytox']
)
