##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Setup for zc.resourcelibrary package

$Id: setup.py 81038 2007-10-24 14:34:17Z srichter $
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='zc.resourcelibrary',
      version='1.3.4',
      author='Zope Foundation and Contributors',
      author_email='zope-dev@zope.org',
      description='Post-rendering Resource Inclusion',
      long_description=(
          read('README.txt')
          + '\n\n.. contents::\n\n' +
          read('src', 'zc', 'resourcelibrary', 'README.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      keywords = "zope3 resource javascript css inclusion",
      classifiers = [
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Programming Language :: Python',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: Zope3'],
      url='http://pypi.python.org/pypi/zc.resourcelibrary',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zc'],
      extras_require=dict(
          test=['zope.app.testing',
                'zope.app.zcmlfiles',
                'zope.pagetemplate',
                'zope.securitypolicy',
                'zope.testbrowser',
                'zope.testing',
                ]),
      install_requires=['setuptools',
                        'zope.app.publication',
                        'zope.browserpage',
                        'zope.browserresource',
                        'zope.component',
                        'zope.configuration',
                        'zope.interface',
                        'zope.publisher',
                        'zope.security',
                        'zope.tales',
                        'zope.traversing',
                        ],
      include_package_data = True,
      zip_safe = False,
      )
