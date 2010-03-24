##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
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
"""Resource Library Expression Type

$Id: tal.py 3268 2005-08-22 23:31:27Z benji $
"""
from zope.tales.expressions import StringExpr
from zc.resourcelibrary import resourcelibrary

class ResourceLibraryExpression(StringExpr):
    """Resource library expression handler class"""

    def __call__(self, econtext):
        resourcelibrary.need(self._expr)
        return ''
