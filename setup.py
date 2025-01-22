""" 
Libra: Dynamic Schema Management in Python
"""

from setuptools import setup

with open('README.md') as readme:
    long_description = readme.read()

doclines = __doc__.split("\n")

setup(
    name = 'libra',
    version = '0.0.1',
    description = 'Dynamic Schema Management in Python',
    long_description_content_type = 'text/markdown',
    author = 'Brady Spears',
    author_email = 'bspears@lanl.gov',
    packages = ['libra'],
    url = 'https://github.com/LANL-Seismoacoustics/libra',
    download_url = 'https://github.com/LANL-Seismoacoustics/pisces/tarball/0.0.1',
    keywords = ['schema', 'database', 'sql'],
    install_requires = ['sqlalchemy>=2.0'],
    license = 'LANL-MIT',
    platforms = ['MAC OS X', 'Linux/Unix']
)