# -*- coding: utf-8 -*-
r"""
just another horrible python file

will some possible problems for detection by the patchbot

starting with unicode hé hö ù 羊

but with unicode declaration, so that it should be ok

but with pdf errors : `\QQ` is good but `\Q` is not good
"""


def blob(n):
    """
    use of python2-specific .next method of iterators
    """
    return enumerate(['a', 'b', 'c']).next()


def plaf():
    """
    bad use of xrange and cmp and print (python2 only)
    """
    print "yikes"
    if cmp(0, 1):
        return False
    return xrange(33)
