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

"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    with open(os.path.join(os.path.dirname(__file__), *rnames)) as f:
        return f.read()

setup(name='zc.resourcelibrary',
      version='2.1.0',
      author='Zope Foundation and Contributors',
      author_email='zope-dev@zope.org',
      description='Post-rendering Resource Inclusion',
      long_description=(
          read('README.rst')
          + '\n\n.. contents::\n\n' +
          read('src', 'zc', 'resourcelibrary', 'README.rst')
          + '\n\n' +
          read('CHANGES.rst')
      ),
      keywords="zope3 resource javascript css inclusion",
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Programming Language :: Python',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: Implementation :: CPython',
          'Programming Language :: Python :: Implementation :: PyPy',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: Zope :: 3',
      ],
      url='http://github.com/zopefoundation/zc.resourcelibrary',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['zc'],
      extras_require={
          'test': [
              'webtest',
              'zope.app.appsetup >= 4.0.0',
              'zope.app.basicskin >= 4.0.0',
              'zope.app.http >= 4.0.1',
              'zope.app.publication >= 4.2.1',
              'zope.app.security >= 4.0.0',
              'zope.app.wsgi >= 4.1.0',
              'zope.pagetemplate',
              'zope.principalregistry',
              'zope.securitypolicy',
              'zope.testbrowser',
              'zope.testing',
              'zope.testrunner',
          ]
      },
      install_requires=[
          'setuptools',
          'zope.browserpage',
          'zope.browserresource',
          'zope.component',
          'zope.configuration',
          'zope.interface',
          'zope.publisher',
          'zope.security',
          'zope.site',
          'zope.tales',
          'zope.traversing',
      ],
      include_package_data=True,
      zip_safe=False,
)
