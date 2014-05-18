r"""
Other miscellaneous arithmetic implemented in C for speed.

AUTHORS:

- Vincent Delecroix (2014): implementation of sum of squares (:trac:`16374`)
"""
#*****************************************************************************
#       Copyright (C) 2014 Vincent Delecroix <20100.delecroix@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#  as published by the Free Software Foundation; either version 3 of
#  the License, or (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************

cdef extern from "math.h":
    double sqrt(double)

cimport integer
import integer

zero = integer.smallInteger(0)

cdef int two_squares_c(unsigned int n, unsigned int res[2]):
    r"""
    Return ``1`` if ``n`` is a sum of two squares and ``0`` otherwise.

    If ``1`` is returned, the the value of ``res[0]`` and ``res[1]`` are set to the
    lexicographically smallest solution of `a^2 + b^2 = n`.
    """
    cdef unsigned int fac,i,ii,j,jj,nn

    if n == 0:
        res[0] = res[1] = 0
        return 1

    # if n = 0 mod 4 then i and j must be even
    # hence, we first remove the maximum power of 4 from n and will then
    # multiply by the corresponding power of 2 the solution
    fac = 0
    while n%4 == 0:
        n >>= 2
        fac += 1

    # now, n is congruent to 1,2 or 3 mod 4.
    # As a square is congruent to 0,1 mod 4, a sum of square is congruent to
    # 0,1,2 mod 4.
    if n%4 == 3:
        return 0

    # if n=1 mod 4 then exactly one of i or j must be even
    # if n=2 mod 4 then i and j must be odd
    if n%4 == 1:
        i = ii = 0
        j = <unsigned int> sqrt(n) + 1 # (rounding is toward zero)
        jj = j*j
        while ii <= n/2:
            nn = n - ii
            while jj > nn:
                j -= 1
                # strangely enough, the 1-by-1 decreasing above is much faster
                # than integer Newton iteration:
                # j = (j+nn/j)/2
                jj = j*j
            if jj == nn:
                res[0] = i<<fac; res[1] = j<<fac
                return 1
            i += 1
            ii = i*i
    else: # n mod 4 = 2
        i = ii = 1
        j = <unsigned int> sqrt(n) # (rounding is toward zero)
        j += 1 - j%2
        jj = j*j
        while ii <= n/2:
            nn = n - ii
            while jj > nn:
                j -= 2
                # strangely enough, the 2-by-2 decreasing above is much faster
                # than integer Newton iteration:
                # j = (j+nn/j)/2
                jj = j*j
            if jj == nn:
                res[0] = i<<fac; res[1] = j<<fac
                return 1
            i += 2
            ii = i*i

    return 0


cdef int three_squares_c(unsigned int n, unsigned int res[3]):
    r"""
    Return ``1`` if ``n`` is a sum of three squares and ``0`` otherwise.

    If ``1`` is returned, the the value of ``res[0]``, ``res[1]`` and ``res[2]``
    are set to the lexicographically smallest solution of `a^2 + b^2 + c^2 = n`.
    """
    cdef unsigned int i,fac
    cdef unsigned int j[2]

    if n == 0:
        res[0] = res[1] = res[2] = 0
        return 1

    # if n == 0 mod 4 then i,j,k must be even
    # hence we remove from n the maximum power of 4 and at the very end we
    # multiply each term of the solution by the appropriate power of 2
    fac = 0
    while n%4 == 0:
        n >>= 2
        fac += 1

    # Legendre's three-square theorem: n is a sum of three squares if and only
    # if it is not of the form 4^a(8b + 7)
    if n%8 == 7:
        return 0

    i = 0
    while not two_squares_c(n-i*i, j):
        i += 1

    res[0] = i<<fac; res[1] = (j[0])<<fac; res[2] = (j[1])<<fac
    return 1

def two_squares_pyx(unsigned int n):
    r"""
    Return the lexicographically smallest pair of non-negative integers
    ``(i,j)`` such that `i^2 + j^2 = n`.

    If ``n`` is not a sum of two squares, a ``ValueError`` is raised.

    .. NOTE::

        The algorithm used here is relatively naive and only has interest for
        small values of ``n``. For that reason, the input must fit into an
        ``unsigned int`` (whose limit might be  `2^{32}-1=4294967295` or
        `2^{64}-1=18446744073709551615` depending on your computer and operating
        system).

    .. SEEALSO::

        :func:`~sage.arith.two_squares` is much more suited for large inputs

    EXAMPLES::

        sage: from sage.rings.arith_pyx import two_squares_pyx
        sage: two_squares_pyx(0)
        (0, 0)
        sage: two_squares_pyx(1)
        (0, 1)
        sage: two_squares_pyx(2)
        (1, 1)
        sage: two_squares_pyx(3)
        Traceback (most recent call last):
        ...
        ValueError: 3 is not a sum of 2 squares
        sage: two_squares_pyx(106)
        (5, 9)

    TESTS::

        sage: s = lambda (x,y) : x**2+y**2
        sage: for ij in Subsets(Subsets(10000,15).random_element(),2):
        ....:     if s(two_squares_pyx(s(ij))) != s(ij):
        ....:         print "hey"
    """
    cdef unsigned int i[2]

    if two_squares_c(n, i):
        return (integer.smallInteger(i[0]), integer.smallInteger(i[1]))

    raise ValueError("%d is not a sum of 2 squares"%n)

def three_squares_pyx(unsigned int n):
    r"""
    If ``n`` is a sum of three squares return a 3-tuple ``(i,j,k)`` of Sage integers
    so that `i^2 + j^2 + k^2 = n`. Otherwise raise a ``ValueError``.

    .. NOTE::

        The algorithm used is relatively naive and only has interest for small
        values of ``n``. For that reason, the input must fit into an ``unsigned
        int`` (whose limit might be  `2^{32}-1=4294967295` or
        `2^{64}-1=18446744073709551615` depending on your plateform).

    .. SEEALSO::

        :func:`~sage.arith.three_squares` is much more suited for large input

    EXAMPLES::

        sage: from sage.rings.arith_pyx import three_squares_pyx
        sage: three_squares_pyx(0)
        (0, 0, 0)
        sage: three_squares_pyx(1)
        (0, 0, 1)
        sage: three_squares_pyx(2)
        (0, 1, 1)
        sage: three_squares_pyx(3)
        (1, 1, 1)
        sage: three_squares_pyx(4)
        (0, 0, 2)
        sage: three_squares_pyx(5)
        (0, 1, 2)
        sage: three_squares_pyx(6)
        (1, 1, 2)
        sage: three_squares_pyx(7)
        Traceback (most recent call last):
        ...
        ValueError: 7 is not a sum of 3 squares
        sage: three_squares_pyx(107)
        (1, 5, 9)

    TESTS::

        sage: s = lambda (x,y,z) : x**2+y**2+z**2
        sage: for ijk in Subsets(Subsets(10000,15).random_element(),3):
        ....:     if s(three_squares_pyx(s(ijk))) != s(ijk):
        ....:         print "hey"

    """
    cdef unsigned int i[3]

    if three_squares_c(n, i):
        return (integer.smallInteger(i[0]), integer.smallInteger(i[1]), integer.smallInteger(i[2]))

    raise ValueError("%d is not a sum of 3 squares"%n)

def four_squares_pyx(unsigned int n):
    r"""
    Return a 4-tuple of non-negative integers ``(i,j,k,l)`` such that `i^2 + j^2
    + k^2 + l^2 = n`.

    .. NOTE::

        The algorithm used here is relatively naive and only has interest for
        small values of ``n``. For that reason, the input must fit into an
        ``unsigned int`` (whose limit might be  `2^{32}-1=4294967295` or
        `2^{64}-1=18446744073709551615` depending on your plateform).

    .. SEEALSO::

        :func:`~sage.arith.four_squares` is much more suited for large input

    EXAMPLES::

        sage: from sage.rings.arith_pyx import four_squares_pyx
        sage: four_squares_pyx(15447)
        (1, 11, 14, 123)
        sage: 1^2 + 11^2 + 14^2 + 123^2
        15447

        sage: four_squares_pyx(523439)
        (1, 15, 22, 723)
        sage: 1^2 + 15^2 + 22^2 + 723^2
        523439

    TESTS::

        sage: all(sum(i**2 for i in four_squares_pyx(n)) == n for n in xrange(500,1000))
        True
    """
    cdef unsigned int i[3]
    cdef unsigned int j, nn

    if n == 0:
        return (zero, zero, zero, zero)

    # we pick the largest square we can for j
    j = (<unsigned int> sqrt(<double> n)) + 1 # (rounding is toward zero)
    while j*j > n:
        j -= 1

    nn = n - j*j
    while not three_squares_c(nn, i):
        j = j-1
        nn = n - j*j

    return (integer.smallInteger(i[0]), integer.smallInteger(i[1]),
            integer.smallInteger(i[2]), integer.smallInteger(j))
