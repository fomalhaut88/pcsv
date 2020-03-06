"""
To make release:
    python setup.py sdist
Installation:
    python setup.py install
"""
import sys
from distutils.core import setup
from setuptools import find_packages

from pcsv import __version__


scripts = ['bin/pcsv-script.py']
if sys.platform == 'win32':
    scripts.append('bin/pcsv.cmd')
else:
    scripts.append('bin/pcsv')

setup(
    name='pcsv',
    version=__version__,
    packages=find_packages(),
    license="Free",
    long_description=open('README.md').read(),
    scripts=scripts,
)
