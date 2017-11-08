"""
To make release:
    python setup.py sdist
Installation:
    python setup.py install
"""
import sys
from distutils.core import setup
from setuptools import find_packages


setup(
    name='pcsv',
    version='2.0',
    packages=find_packages(),
    license="Free",
    long_description=open('README.md').read(),
    scripts=['bin/pcsv'],
)
