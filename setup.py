import os
from distutils.core import setup, Extension
from pkg_resources import require, DistributionNotFound

author = 'Ole Streicher'
email = 'ole@aip.de'
license_ = 'GPL'
pkgversion = '0.0'
description = 'Implementation of a MUSE pixtable'
long_description = '''Implementation of a MUSE pixtable
'''

pkgname = 'muse_pixtable'
baseurl = 'http://pypi.python.org/packages/source/%s/%s' % (pkgname[0], pkgname)
classifiers = '''Development Status :: 4 - Beta
Intended Audience :: Science/Research
License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)
Operating System :: MacOS :: MacOS X
Operating System :: POSIX
Operating System :: Unix
Programming Language :: Python
Programming Language :: Python :: 2
Programming Language :: Python :: 3
Topic :: Scientific/Engineering :: Astronomy
'''.splitlines()

def create_version_file(pkgversion = pkgversion):
    with open(os.path.join('muse_pixtable', 'version.py'), 'w') as vfile:
        vfile.write("version = %s\n" % repr(pkgversion))
        vfile.write("author = %s\n" % repr(author))
        vfile.write("email = %s\n" % repr(email))
        vfile.write("license_ = %s\n" % repr(license_))

try:
    create_version_file()
except IOError:
    pass

setup(
    name = pkgname,
    version = pkgversion,
    author = author,
    author_email = email,
    description = description,
    long_description = long_description,
    license = license_,
    url = 'https://pypi.python.org/pypi/%s/%s' % (pkgname, pkgversion),
    download_url = '%s/%s-%s.tar.gz' % (baseurl, pkgname, pkgversion),
    classifiers = classifiers,
    requires = [ 'astropy' ],
    provides = ['muse_pixtable'],
    packages = ['muse_pixtable']
    )
