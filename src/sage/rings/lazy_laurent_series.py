r"""
Lazy Laurent Series

A lazy Laurent series is a Laurent series whose coefficients are
computed on demand.  Therefore, unlike the usual Laurent series in
Sage, lazy Laurent series have infinite precision.

EXAMPLES:

Laurent series over the integer ring are particularly useful as
generating functions for sequences arising in combinatorics.::

    sage: L.<z> = LazyLaurentSeriesRing(ZZ)

The generating function of the Fibonacci sequence is::

    sage: f = 1 / (1 - z - z^2)
    sage: f
    1 + z + 2*z^2 + 3*z^3 + 5*z^4 + 8*z^5 + 13*z^6 + O(z^7)

In principle, we can now compute any coefficient of `f`::

    sage: f.coefficient(100)
    573147844013817084101

Which coefficients are actually computed depends on the type of
implementation.  For the sparse implementation, only the coefficients
that are needed are computed.::

    sage: s = L(lambda n: n); s
    z + 2*z^2 + 3*z^3 + 4*z^4 + 5*z^5 + 6*z^6 + O(z^7)
    sage: s.coefficient(10)
    10
    sage: s._coeff_stream._cache
    {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 10: 10}

Using the dense implementation, all coefficients up to the required
coefficient are computed.::

    sage: L.<x> = LazyLaurentSeriesRing(ZZ, sparse=False)
    sage: s = L(lambda n: n); s
    x + 2*x^2 + 3*x^3 + 4*x^4 + 5*x^5 + 6*x^6 + O(x^7)
    sage: s.coefficient(10)
    10
    sage: s._coeff_stream._cache
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

We can do arithmetic with lazy power series::

    sage: f
    1 + z + 2*z^2 + 3*z^3 + 5*z^4 + 8*z^5 + 13*z^6 + O(z^7)
    sage: f^-1
    1 - z - z^2 + O(z^7)
    sage: f + f^-1
    2 + z^2 + 3*z^3 + 5*z^4 + 8*z^5 + 13*z^6 + O(z^7)
    sage: g = (f + f^-1)*(f - f^-1); g
    4*z + 6*z^2 + 8*z^3 + 19*z^4 + 38*z^5 + 71*z^6 + O(z^7)

We can change the base ring::

    sage: h = g.change_ring(QQ)
    sage: h.parent()
    Lazy Laurent Series Ring in z over Rational Field
    sage: h
    4*z + 6*z^2 + 8*z^3 + 19*z^4 + 38*z^5 + 71*z^6 + O(z^7)
    sage: hinv = h^-1; hinv
    1/4*z^-1 - 3/8 + 1/16*z - 17/32*z^2 + 5/64*z^3 - 29/128*z^4 + 165/256*z^5 + O(z^6)
    sage: hinv.valuation()
    -1

AUTHORS:

- Kwankyu Lee (2019-02-24): initial version
- Tejasvi Chebrolu, Martin Rubey, Travis Scrimshaw (2021-08):
  refactored and expanded functionality

"""

# ****************************************************************************
#       Copyright (C) 2019 Kwankyu Lee <ekwankyu@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  https://www.gnu.org/licenses/
# ****************************************************************************


from sage.rings.infinity import infinity
from sage.structure.element import ModuleElement, RingElement
from sage.rings.integer_ring import ZZ
from sage.structure.richcmp import op_EQ, op_NE
from sage.arith.power import generic_power
from sage.rings.polynomial.laurent_polynomial_ring import LaurentPolynomialRing
from sage.data_structures.coefficient_stream import (
    CoefficientStream_add,
    CoefficientStream_cauchy_product,
    CoefficientStream_sub,
    CoefficientStream_composition,
    CoefficientStream_lmul,
    CoefficientStream_rmul,
    CoefficientStream_neg,
    CoefficientStream_cauchy_inverse,
    CoefficientStream_map_coefficients,
    CoefficientStream_zero,
    CoefficientStream_exact,
    CoefficientStream_uninitialized,
    CoefficientStream_coefficient_function,
    CoefficientStream_dirichlet_convolution,
    CoefficientStream_dirichlet_inv
)

class LazySequenceElement(ModuleElement):
    r"""
    An element of a lazy series.

    EXAMPLES::

        sage: L.<z> = LazyLaurentSeriesRing(ZZ)
        sage: f = 1/(1 - z)
        sage: f.parent()
        Lazy Laurent Series Ring in z over Integer Ring
        sage: f
        1 + z + z^2 + z^3 + z^4 + z^5 + z^6 + O(z^7)

        sage: L.<z> = LazyLaurentSeriesRing(ZZ, sparse=True)
        sage: f = 1/(1 - z)
        sage: f.parent()
        Lazy Laurent Series Ring in z over Integer Ring
        sage: f
        1 + z + z^2 + z^3 + z^4 + z^5 + z^6 + O(z^7)
    """
    def __init__(self, parent, coeff_stream):
        """
        Initialize the series.

        TESTS::

            sage: L.<z> = LazyLaurentSeriesRing(ZZ)
            sage: TestSuite(L.an_element()).run()

            sage: L = LazyDirichletSeriesRing(QQbar, 'z')
            sage: g = L(constant=1)
            sage: TestSuite(g).run()

        """
        ModuleElement.__init__(self, parent)
        self._coeff_stream = coeff_stream

    def finite_part(self, degree=None):
        r"""
        Return ``self`` truncated to ``degree`` as an element of an appropriate ring.

        INPUT:

        - ``degree`` -- ``None`` or an integer

        OUTPUT:

        If ``degree`` is not ``None``, the terms of the series of
        degree greater than ``degree`` are removed first. If
        ``degree`` is ``None`` and the series is not known to have
        only finitely many nonzero coefficients, a ``ValueError`` is
        raised.

        EXAMPLES::

            sage: L.<z> = LazyLaurentSeriesRing(ZZ)
            sage: f = L([1,0,0,2,0,0,0,3], valuation=-3); f.finite_part()
            z^-3 + 2 + 3*z^4
            sage: f.polynomial()
            z^-3 + 2 + 3*z^4

            sage: L = LazyDirichletSeriesRing(ZZ, "s")
            sage: f = L([1,0,0,2,0,0,0,3], valuation=2); f.finite_part()
            3/9^s + 2/5^s + 1/2^s

            sage: L.<x,y> = LazyTaylorSeriesRing(ZZ)
            sage: f = 1/(1+x+y^2); f.finite_part(3)
            -x^3 + 2*x*y^2 + x^2 - y^2 - x + 1
        """
        P = self.parent()
        L = P._laurent_poly_ring
        coeff_stream = self._coeff_stream
        if degree is None:
            if isinstance(coeff_stream, CoefficientStream_zero):
                return L.zero()
            elif isinstance(coeff_stream, CoefficientStream_exact) and not coeff_stream._constant:
                m = coeff_stream._degree
            else:
                raise ValueError("not a polynomial")
        else:
            m = degree + 1

        v = self.valuation()
        return L.sum(self[i]*P.monomial(1, i) for i in range(v, m))

    def __getitem__(self, n):
        """
        Return the coefficient of the term with exponent ``n`` of the series.

        INPUT:

        - ``n`` -- integer; the exponent

        EXAMPLES::

            sage: L.<z> = LazyLaurentSeriesRing(ZZ, sparse=False)
            sage: f = z / (1 - 2*z^3)
            sage: [f[n] for n in range(20)]
            [0, 1, 0, 0, 2, 0, 0, 4, 0, 0, 8, 0, 0, 16, 0, 0, 32, 0, 0, 64]
            sage: f[0:20]
            [0, 1, 0, 0, 2, 0, 0, 4, 0, 0, 8, 0, 0, 16, 0, 0, 32, 0, 0, 64]

            sage: M = L(lambda n: n)
            sage: [M[n] for n in range(20)]
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]

            sage: L.<z> = LazyLaurentSeriesRing(ZZ, sparse=True)
            sage: M = L(lambda n: n)
            sage: [M[n] for n in range(20)]
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]

        Similarly for Dirichlet series::

            sage: L = LazyDirichletSeriesRing(ZZ, "z")
            sage: f = L(lambda n: n)
            sage: [f[n] for n in range(1, 11)]
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            sage: f[1:11]
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

            sage: M = L(lambda n: n)
            sage: [M[n] for n in range(1, 11)]
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            sage: L = LazyDirichletSeriesRing(ZZ, "z", sparse=True)
            sage: M = L(lambda n: n)
            sage: [M[n] for n in range(1, 11)]
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        """
        R = self.parent()._coeff_ring
        if isinstance(n, slice):
            if n.stop is None:
                raise NotImplementedError("cannot list an infinite set")
            start = n.start if n.start is not None else self._coeff_stream._approximate_valuation
            step = n.step if n.step is not None else 1
            return [R(self._coeff_stream[k]) for k in range(start, n.stop, step)]
        return R(self._coeff_stream[n])

    coefficient = __getitem__

    def map_coefficients(self, func, ring=None):
        r"""
        Return the series with ``func`` applied to each nonzero
        coefficient of ``self``.

        INPUT:

        - ``func`` -- function that takes in a coefficient and returns
          a new coefficient

        EXAMPLES:

        Dense Implementation::

            sage: L.<z> = LazyLaurentSeriesRing(ZZ, sparse=False)
            sage: s = z/(1 - 2*z^2)
            sage: t = s.map_coefficients(lambda c: c + 1)
            sage: s
            z + 2*z^3 + 4*z^5 + 8*z^7 + O(z^8)
            sage: t
            2*z + 3*z^3 + 5*z^5 + 9*z^7 + O(z^8)
            sage: M = L(lambda n: n); M
            z + 2*z^2 + 3*z^3 + 4*z^4 + 5*z^5 + 6*z^6 + O(z^7)
            sage: N = M.map_coefficients(lambda c: c + 1); N
            2*z + 3*z^2 + 4*z^3 + 5*z^4 + 6*z^5 + 7*z^6 + O(z^7)

        Sparse Implementation::

            sage: L.<z> = LazyLaurentSeriesRing(ZZ, sparse=True)
            sage: M = L(lambda n: n); M
            z + 2*z^2 + 3*z^3 + 4*z^4 + 5*z^5 + 6*z^6 + O(z^7)
            sage: N = M.map_coefficients(lambda c: c + 1); N
            2*z + 3*z^2 + 4*z^3 + 5*z^4 + 6*z^5 + 7*z^6 + O(z^7)

        An example where the series is known to be exact::

            sage: f = z + z^2 + z^3
            sage: m = f.map_coefficients(lambda c: c + 1)
            sage: m
            2*z + 2*z^2 + 2*z^3

        Similarly for Dirichlet series::

            sage: L = LazyDirichletSeriesRing(ZZ, "z")
            sage: s = L(lambda n: n-1); s
            1/(2^z) + 2/3^z + 3/4^z + 4/5^z + 5/6^z + 6/7^z + ...
            sage: s = s.map_coefficients(lambda c: c + 1); s
            2/2^z + 3/3^z + 4/4^z + 5/5^z + 6/6^z + 7/7^z + ...

        """
        P = self.parent()
        coeff_stream = self._coeff_stream
        BR = P.base_ring()
        if isinstance(coeff_stream, CoefficientStream_exact):
            initial_coefficients = [func(i) if i else 0
                                    for i in coeff_stream._initial_coefficients]
            c = func(coeff_stream._constant) if coeff_stream._constant else 0
            if not any(initial_coefficients) and not c:
                return P.zero()
            coeff_stream = CoefficientStream_exact(initial_coefficients,
                                                   self._coeff_stream._is_sparse,
                                                   valuation=coeff_stream._approximate_valuation,
                                                   degree=coeff_stream._degree,
                                                   constant=BR(c))
            return P.element_class(P, coeff_stream)
        coeff_stream = CoefficientStream_map_coefficients(self._coeff_stream, func, P._coeff_ring)
        return P.element_class(P, coeff_stream)

    def truncate(self, d):
        r"""
        Return this series with its terms of degree >= ``d`` truncated.

        INPUT:

        - ``d`` -- integer; the degree from which the series is truncated

        EXAMPLES:

        Dense Implementation::

            sage: L.<z> = LazyLaurentSeriesRing(ZZ, sparse=False)
            sage: alpha = 1/(1-z)
            sage: alpha
            1 + z + z^2 + z^3 + z^4 + z^5 + z^6 + O(z^7)
            sage: beta = alpha.truncate(5)
            sage: beta
            1 + z + z^2 + z^3 + z^4
            sage: alpha - beta
            z^5 + z^6 + O(z^7)
            sage: M = L(lambda n: n); M
            z + 2*z^2 + 3*z^3 + 4*z^4 + 5*z^5 + 6*z^6 + O(z^7)
            sage: M.truncate(4)
            z + 2*z^2 + 3*z^3

        Sparse Implementation::

            sage: L.<z> = LazyLaurentSeriesRing(ZZ, sparse=True)
            sage: M = L(lambda n: n); M
            z + 2*z^2 + 3*z^3 + 4*z^4 + 5*z^5 + 6*z^6 + O(z^7)
            sage: M.truncate(4)
            z + 2*z^2 + 3*z^3

        Series which are known to be exact can also be truncated::

            sage: M = z + z^2 + z^3 + z^4
            sage: M.truncate(4)
            z + z^2 + z^3
        """
        P = self.parent()
        coeff_stream = self._coeff_stream
        v = coeff_stream._approximate_valuation
        initial_coefficients = [coeff_stream[i] for i in range(v, d)]
        return P.element_class(P, CoefficientStream_exact(initial_coefficients, P._sparse,
                                                          valuation=v))

    def prec(self):
        """
        Return the precision of the series, which is infinity.

        EXAMPLES::

            sage: L.<z> = LazyLaurentSeriesRing(ZZ)
            sage: f = 1/(1 - z)
            sage: f.prec()
            +Infinity
        """
        return infinity

    def valuation(self):
        r"""
        Return the valuation of ``self``.

        This method determines the valuation of the series by looking for a
        nonzero coefficient. Hence if the series happens to be zero, then it
        may run forever.

        EXAMPLES::

            sage: L.<z> = LazyLaurentSeriesRing(ZZ)
            sage: s = 1/(1 - z) - 1/(1 - 2*z)
            sage: s.valuation()
            1
            sage: t = z - z
            sage: t.valuation()
            +Infinity
            sage: M = L(lambda n: n^2, 0)
            sage: M.valuation()
            1
            sage: (M - M).valuation()
            +Infinity

        Similarly for Dirichlet series::

            sage: L = LazyDirichletSeriesRing(ZZ, "z")
            sage: mu = L(moebius); mu.valuation()
            1
            sage: (mu - mu).valuation()
            +Infinity
            sage: g = L(constant=1, valuation=2)
            sage: g.valuation()
            2
            sage: (g*g).valuation()
            4

        """
        return self._coeff_stream.valuation()

    def _richcmp_(self, other, op):
        r"""
        Compare ``self` with ``other`` with respect to the comparison
        operator ``op``.

        Equality is verified if the corresponding coefficients of both series
        can be checked for equality without computing coefficients
        indefinitely.  Otherwise an exception is raised to declare that
        equality is not decidable.

        Inequality is not defined for lazy Laurent series.

        INPUT:

        - ``other`` -- another Laurent series
        - ``op`` -- comparison operator

        EXAMPLES::

            sage: L.<z> = LazyLaurentSeriesRing(QQ)
            sage: z + z^2 == z^2 + z
            True
            sage: z + z^2 != z^2 + z
            False
            sage: z + z^2 > z^2 + z
            False
            sage: z + z^2 < z^2 + z
            False
        """
        if op is op_EQ:
            if isinstance(self._coeff_stream, CoefficientStream_zero):  # self == 0
                return isinstance(other._coeff_stream, CoefficientStream_zero)
            if isinstance(other._coeff_stream, CoefficientStream_zero):  # self != 0 but other == 0
                return False

            if (not isinstance(self._coeff_stream, CoefficientStream_exact)
                    or not isinstance(other._coeff_stream, CoefficientStream_exact)):
                # One of the lazy laurent series is not known to eventually be constant
                # Implement the checking of the caches here.
                n = min(self._coeff_stream._approximate_valuation, other._coeff_stream._approximate_valuation)
                m = max(self._coeff_stream._approximate_valuation, other._coeff_stream._approximate_valuation)
                for i in range(n, m):
                    if self[i] != other[i]:
                        return False
                if self._coeff_stream == other._coeff_stream:
                    return True
                raise ValueError("undecidable")

            # Both are CoefficientStream_exact, which implements a full check
            return self._coeff_stream == other._coeff_stream

        if op is op_NE:
            return not (self == other)

        return False

    def __hash__(self):
        """
        Return the hash of ``self``

        TESTS::

            sage: L = LazyLaurentSeriesRing(ZZ, 'z')
            sage: f = L([1,2,3,4], -5)
            sage: hash(f) == hash(f)
            True
            sage: g = (1 + f)/(1 - f)^2
            sage: {g: 1}
            {z^5 - 2*z^6 + z^7 + 5*z^9 - 11*z^10 + z^11 + O(z^12): 1}
        """
        return hash(self._coeff_stream)

    def __bool__(self):
        """
        Test whether ``self`` is not zero.

        TESTS::

            sage: L.<z> = LazyLaurentSeriesRing(GF(2))
            sage: bool(z-z)
            False
            sage: f = 1/(1 - z)
            sage: bool(f)
            True
            sage: M = L(lambda n: n, 0); M
            z + z^3 + z^5 + O(z^7)
            sage: M.is_zero()
            False
            sage: M = L(lambda n: 2*n if n < 10 else 1, 0); M
            O(z^7)
            sage: bool(M)
            Traceback (most recent call last):
            ...
            ValueError: undecidable as lazy Laurent series
            sage: M[15]
            1
            sage: bool(M)
            True

            sage: L.<z> = LazyLaurentSeriesRing(GF(2), sparse=True)
            sage: M = L(lambda n: 2*n if n < 10 else 1, 0); M
            O(z^7)
            sage: bool(M)
            Traceback (most recent call last):
            ...
            ValueError: undecidable as lazy Laurent series
            sage: M[15]
            1
            sage: bool(M)
            True
        """
        if isinstance(self._coeff_stream, CoefficientStream_zero):
            return False
        if isinstance(self._coeff_stream, CoefficientStream_exact):
            return True
        if self.parent()._sparse:
            cache = self._coeff_stream._cache
            if any(cache[a] for a in cache):
                return True
        else:
            if any(a for a in self._coeff_stream._cache):
                return True
        if self[self._coeff_stream._approximate_valuation]:
            return True
        raise ValueError("undecidable as lazy Laurent series")

    def define(self, s):
        r"""
        Define an equation by ``self = s``.

        INPUT:

        - ``s`` -- a Laurent polynomial

        EXAMPLES:

        We begin by constructing the Catalan numbers::

            sage: L.<z> = LazyLaurentSeriesRing(ZZ)
            sage: C = L(None)
            sage: C.define(1 + z*C^2)
            sage: C
            1 + z + 2*z^2 + 5*z^3 + 14*z^4 + 42*z^5 + 132*z^6 + O(z^7)

        The Catalan numbers but with a valuation 1::

            sage: B = L(None, 1)
            sage: B.define(z + B^2)
            sage: B
            z + z^2 + 2*z^3 + 5*z^4 + 14*z^5 + 42*z^6 + 132*z^7 + O(z^8)

        We can define multiple series that are linked::

            sage: s = L(None)
            sage: t = L(None)
            sage: s.define(1 + z*t^3)
            sage: t.define(1 + z*s^2)
            sage: s[:9]
            [1, 1, 3, 9, 34, 132, 546, 2327, 10191]
            sage: t[:9]
            [1, 1, 2, 7, 24, 95, 386, 1641, 7150]

        A bigger example::

            sage: L.<z> = LazyLaurentSeriesRing(ZZ)
            sage: A = L(None, 5)
            sage: B = L(None)
            sage: C = L(None, 2)
            sage: A.define(z^5 + B^2)
            sage: B.define(z^5 + C^2)
            sage: C.define(z^2 + C^2 + A^2)
            sage: A[0:15]
            [0, 0, 0, 0, 0, 1, 0, 0, 1, 2, 5, 4, 14, 10, 48]
            sage: B[0:15]
            [0, 0, 0, 0, 1, 1, 2, 0, 5, 0, 14, 0, 44, 0, 138]
            sage: C[0:15]
            [0, 0, 1, 0, 1, 0, 2, 0, 5, 0, 15, 0, 44, 2, 142]

        Counting binary trees::

            sage: L.<z> = LazyLaurentSeriesRing(QQ)
            sage: s = L(None, valuation=1)
            sage: s.define(z + (s^2+s(z^2))/2)
            sage: [s[i] for i in range(9)]
            [0, 1, 1, 1, 2, 3, 6, 11, 23]

        The `q`-Catalan numbers::

            sage: R.<q> = ZZ[]
            sage: L.<z> = LazyLaurentSeriesRing(R)
            sage: s = L(None)
            sage: s.define(1+z*s*s(q*z))
            sage: s
            1 + z + (q + 1)*z^2 + (q^3 + q^2 + 2*q + 1)*z^3
             + (q^6 + q^5 + 2*q^4 + 3*q^3 + 3*q^2 + 3*q + 1)*z^4
             + (q^10 + q^9 + 2*q^8 + 3*q^7 + 5*q^6 + 5*q^5 + 7*q^4 + 7*q^3 + 6*q^2 + 4*q + 1)*z^5
             + (q^15 + q^14 + 2*q^13 + 3*q^12 + 5*q^11 + 7*q^10 + 9*q^9 + 11*q^8
                + 14*q^7 + 16*q^6 + 16*q^5 + 17*q^4 + 14*q^3 + 10*q^2 + 5*q + 1)*z^6 + O(z^7)

        We count unlabeled ordered trees by total number of nodes
        and number of internal nodes::

            sage: R.<q> = QQ[]
            sage: Q.<z> = LazyLaurentSeriesRing(R)
            sage: leaf = z
            sage: internal_node = q * z
            sage: L = Q(constant=1, degree=1)
            sage: T = Q(None, 1)
            sage: T.define(leaf + internal_node * L(T))
            sage: [T[i] for i in range(6)]
            [0, 1, q, q^2 + q, q^3 + 3*q^2 + q, q^4 + 6*q^3 + 6*q^2 + q]

        Similarly for Dirichlet series::

            sage: L = LazyDirichletSeriesRing(ZZ, "z")
            sage: g = L(constant=1, valuation=2)
            sage: F = L(None); F.define(1 + g*F)
            sage: [F[i] for i in range(1, 16)]
            [1, 1, 1, 2, 1, 3, 1, 4, 2, 3, 1, 8, 1, 3, 3]
            sage: oeis(_)                                                       # optional, internet
            0: A002033: Number of perfect partitions of n.
            1: A074206: Kalmár's [Kalmar's] problem: number of ordered factorizations of n.
            ...

            sage: F = L(None); F.define(1 + g*F*F)
            sage: [F[i] for i in range(1, 16)]
            [1, 1, 1, 3, 1, 5, 1, 10, 3, 5, 1, 24, 1, 5, 5]

        TESTS::

            sage: L.<z> = LazyLaurentSeriesRing(ZZ, sparse=True)
            sage: s = L(None)
            sage: s.define(1 + z*s^3)
            sage: s[:10]
            [1, 1, 3, 12, 55, 273, 1428, 7752, 43263, 246675]

            sage: e = L(None)
            sage: e.define(1 + z*e)
            sage: e.define(1 + z*e)
            Traceback (most recent call last):
            ...
            ValueError: series already defined
            sage: z.define(1 + z^2)
            Traceback (most recent call last):
            ...
            ValueError: series already defined
        """
        if not isinstance(self._coeff_stream, CoefficientStream_uninitialized) or self._coeff_stream._target is not None:
            raise ValueError("series already defined")
        self._coeff_stream._target = s._coeff_stream


    def _repr_(self):
        r"""
        Return a string representation of ``self``.

        EXAMPLES::

            sage: L.<z> = LazyLaurentSeriesRing(ZZ)
            sage: z^-3 + z - 5
            z^-3 - 5 + z
            sage: -1/(1 + 2*z)
            -1 + 2*z - 4*z^2 + 8*z^3 - 16*z^4 + 32*z^5 - 64*z^6 + O(z^7)
            sage: -z^-7/(1 + 2*z)
            -z^-7 + 2*z^-6 - 4*z^-5 + 8*z^-4 - 16*z^-3 + 32*z^-2 - 64*z^-1 + O(1)
            sage: L([1,5,0,3], valuation=-1, degree=5, constant=2)
            z^-1 + 5 + 3*z^2 + 2*z^5 + 2*z^6 + 2*z^7 + O(z^8)
            sage: L(constant=5, valuation=2)
            5*z^2 + 5*z^3 + 5*z^4 + O(z^5)
            sage: L(constant=5, degree=-2)
            5*z^-2 + 5*z^-1 + 5 + O(z)
            sage: L(lambda x: x if x < 0 else 0, valuation=-2)
            -2*z^-2 - z^-1 + O(z^5)
            sage: L(lambda x: x if x < 0 else 0, valuation=2)
            O(z^9)
            sage: L(lambda x: x if x > 0 else 0, valuation=-2)
            z + 2*z^2 + 3*z^3 + 4*z^4 + O(z^5)
            sage: L(lambda x: x if x > 0 else 0, valuation=-10)
            O(z^-3)

            sage: L(None)
            Uninitialized Lazy Laurent Series
            sage: L(0)
            0

            sage: R.<x,y> = QQ[]
            sage: L.<z> = LazyLaurentSeriesRing(R)
            sage: z^-2 / (1 - (x-y)*z) + x^4*z^-3 + (1-y)*z^-4
            (-y + 1)*z^-4 + x^4*z^-3 + z^-2 + (x - y)*z^-1
             + (x^2 - 2*x*y + y^2) + (x^3 - 3*x^2*y + 3*x*y^2 - y^3)*z
             + (x^4 - 4*x^3*y + 6*x^2*y^2 - 4*x*y^3 + y^4)*z^2 + O(z^3)
        """
        if isinstance(self._coeff_stream, CoefficientStream_zero):
            return '0'
        if isinstance(self._coeff_stream, CoefficientStream_uninitialized) and self._coeff_stream._target is None:
            return 'Uninitialized Lazy Laurent Series'
        return self._format_series(repr)

    def _latex_(self):
        r"""
        Return a latex representation of ``self``.

        EXAMPLES::

            sage: L.<z> = LazyLaurentSeriesRing(ZZ)
            sage: latex(z^-3 + z - 5)
            \frac{1}{z^{3}} - 5 + z
            sage: latex(-1/(1 + 2*z))
            -1 + 2z - 4z^{2} + 8z^{3} - 16z^{4} + 32z^{5} - 64z^{6} + O(z^{7})
            sage: latex(-z^-7/(1 + 2*z))
            \frac{-1}{z^{7}} + \frac{2}{z^{6}} + \frac{-4}{z^{5}} + \frac{8}{z^{4}}
             + \frac{-16}{z^{3}} + \frac{32}{z^{2}} + \frac{-64}{z} + O(1)
            sage: latex(L([1,5,0,3], valuation=-1, degree=5, constant=2))
            \frac{1}{z} + 5 + 3z^{2} + 2z^{5} + 2z^{6} + 2z^{7} + O(z^{8})
            sage: latex(L(constant=5, valuation=2))
            5z^{2} + 5z^{3} + 5z^{4} + O(z^{5})
            sage: latex(L(constant=5, degree=-2))
            \frac{5}{z^{2}} + \frac{5}{z} + 5 + O(z)
            sage: latex(L(lambda x: x if x < 0 else 0, valuation=-2))
            \frac{-2}{z^{2}} + \frac{-1}{z} + O(z^{5})
            sage: latex(L(lambda x: x if x < 0 else 0, valuation=2))
            O(z^{9})
            sage: latex(L(lambda x: x if x > 0 else 0, valuation=-2))
            z + 2z^{2} + 3z^{3} + 4z^{4} + O(z^{5})
            sage: latex(L(lambda x: x if x > 0 else 0, valuation=-10))
            O(\frac{1}{z^{3}})

            sage: latex(L(None))
            \text{\texttt{Undef}}
            sage: latex(L(0))
            0

            sage: R.<x,y> = QQ[]
            sage: L.<z> = LazyLaurentSeriesRing(R)
            sage: latex(z^-2 / (1 - (x-y)*z) + x^4*z^-3 + (1-y)*z^-4)
            \frac{-y + 1}{z^{4}} + \frac{x^{4}}{z^{3}} + \frac{1}{z^{2}}
             + \frac{x - y}{z} + x^{2} - 2 x y + y^{2}
             + \left(x^{3} - 3 x^{2} y + 3 x y^{2} - y^{3}\right)z
             + \left(x^{4} - 4 x^{3} y + 6 x^{2} y^{2} - 4 x y^{3} + y^{4}\right)z^{2}
             + O(z^{3})
        """
        from sage.misc.latex import latex
        if isinstance(self._coeff_stream, CoefficientStream_zero):
            return latex('0')
        if isinstance(self._coeff_stream, CoefficientStream_uninitialized) and self._coeff_stream._target is None:
            return latex("Undef")
        return self._format_series(latex)

    def _ascii_art_(self):
        r"""
        Return an ascii art representation of ``self``.

        EXAMPLES::

            sage: e = SymmetricFunctions(QQ).e()
            sage: L.<z> = LazyLaurentSeriesRing(e)
            sage: L.options.display_length = 3
            sage: ascii_art(1 / (1 - e[1]*z))
            e[] + e[1]*z + e[1, 1]*z^2 + O(e[]*z^3)
            sage: L.options._reset()
        """
        from sage.typeset.ascii_art import ascii_art, AsciiArt
        if isinstance(self._coeff_stream, CoefficientStream_zero):
            return AsciiArt('0')
        if isinstance(self._coeff_stream, CoefficientStream_uninitialized) and self._coeff_stream._target is None:
            return AsciiArt('Uninitialized Lazy Laurent Series')
        return self._format_series(ascii_art, True)

    def _unicode_art_(self):
        r"""
        Return a unicode art representation of ``self``.

        EXAMPLES::

            sage: e = SymmetricFunctions(QQ).e()
            sage: L.<z> = LazyLaurentSeriesRing(e)
            sage: L.options.display_length = 3
            sage: unicode_art(1 / (1 - e[1]*z))
            e[] + e[1]*z + e[1, 1]*z^2 + O(e[]*z^3)
            sage: L.options._reset()
        """
        from sage.typeset.unicode_art import unicode_art, UnicodeArt
        if isinstance(self._coeff_stream, CoefficientStream_zero):
            return UnicodeArt('0')
        if isinstance(self._coeff_stream, CoefficientStream_uninitialized) and self._coeff_stream._target is None:
            return UnicodeArt('Uninitialized Lazy Laurent Series')
        return self._format_series(unicode_art, True)


class LazySequencesModuleElement(LazySequenceElement):
    r"""
    A lazy series where addition and scalar multiplication
    are done term-wise.

    INPUT:

    - ``parent`` -- the parent ring of the series
    - ``coeff_stream`` -- the stream of coefficients of the series

    EXAMPLES::

        sage: L.<z> = LazyLaurentSeriesRing(ZZ)
        sage: M = L(lambda n: n, valuation=0)
        sage: N = L(lambda n: 1, valuation=0)
        sage: M[:10]
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        sage: N[:10]
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

    Two sequences can be added::

        sage: O = M + N
        sage: O[0:10]
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    Two sequences can be subracted::

        sage: P = M - N
        sage: P[:10]
        [-1, 0, 1, 2, 3, 4, 5, 6, 7, 8]

    A sequence can be multiplied by a scalar::

        sage: Q = 2 * M
        sage: Q[:10]
        [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]

    The negation of a sequence can also be found::

        sage: R = -M
        sage: R[:10]
        [0, -1, -2, -3, -4, -5, -6, -7, -8, -9]
    """
    def _add_(self, other):
        """
        Return the sum of ``self`` and ``other``.

        INPUT:

        - ``other`` -- other series

        EXAMPLES:

        Dense series can be added::

            sage: L.<z> = LazyLaurentSeriesRing(ZZ)
            sage: M = L(lambda n: 1 + n, valuation=0)
            sage: N = L(lambda n: -n, valuation=0)
            sage: O = M + N
            sage: O[0:10]
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

        Sparse series can be added::

            sage: L.<z> = LazyLaurentSeriesRing(ZZ, sparse=True)
            sage: M = L(lambda n: 1 + n, valuation=0)
            sage: N = L(lambda n: -n, valuation=0)
            sage: O = M + N
            sage: O[0:10]
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

        Series which are known to be exact can be added::

            sage: M = L(1)
            sage: N = L([0, 1])
            sage: O = M + N
            sage: O[0:10]
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 0]

        Adding zero gives the same series::

            sage: M = L(lambda n: 1 + n, valuation=0)
            sage: M + 0 is 0 + M is M
            True

        Similarly for Dirichlet series::

            sage: L = LazyDirichletSeriesRing(ZZ, "z")
            sage: s = L(lambda n: n); s
            1 + 2/2^z + 3/3^z + 4/4^z + 5/5^z + 6/6^z + 7/7^z + ...
            sage: t = L(constant=1); t
            1 + 1/(2^z) + 1/(3^z) + ...
            sage: s + t
            2 + 3/2^z + 4/3^z + 5/4^z + 6/5^z + 7/6^z + 8/7^z + ...

            sage: r = L(constant=-1)
            sage: r + t
            0

            sage: r = L([1,2,3])
            sage: r + t
            2 + 3/2^z + 4/3^z + 1/(4^z) + 1/(5^z) + 1/(6^z) + ...

            sage: r = L([1,2,3], constant=-1)
            sage: r + t
            2 + 3/2^z + 4/3^z

        """
        P = self.parent()
        left = self._coeff_stream
        right = other._coeff_stream
        if isinstance(left, CoefficientStream_zero):
            return other
        if isinstance(right, CoefficientStream_zero):
            return self
        if (isinstance(left, CoefficientStream_exact)
            and isinstance(right, CoefficientStream_exact)):
            approximate_valuation = min(left.valuation(), right.valuation())
            degree = max(left._degree, right._degree)
            initial_coefficients = [left[i] + right[i] for i in range(approximate_valuation, degree)]
            constant = left._constant + right._constant
            if not any(initial_coefficients) and not constant:
                return P.zero()
            coeff_stream = CoefficientStream_exact(initial_coefficients, P._sparse,
                                                   constant=constant,
                                                   degree=degree,
                                                   valuation=approximate_valuation)
            return P.element_class(P, coeff_stream)
        return P.element_class(P, CoefficientStream_add(self._coeff_stream, other._coeff_stream))

    def _sub_(self, other):
        """
        Return the series of this series minus ``other`` series.

        INPUT:

        - ``other`` -- other series

        EXAMPLES:

        Dense series can be subtracted::

            sage: L.<z> = LazyLaurentSeriesRing(ZZ, sparse=False)
            sage: M = L(lambda n: 1 + n, valuation=0)
            sage: N = L(lambda n: -n, valuation=0)
            sage: O = M - N
            sage: O[0:10]
            [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]

        Sparse series can be subtracted::

            sage: L.<z> = LazyLaurentSeriesRing(ZZ, sparse=True)
            sage: M = L(lambda n: 1 + n, valuation=0)
            sage: N = L(lambda n: -n, valuation=0)
            sage: O = M - N
            sage: O[0:10]
            [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]

        Series which are known to be exact can be subtracted::

            sage: M = L.one()
            sage: N = L([0, 1])
            sage: O = M - N
            sage: O[0:10]
            [1, -1, 0, 0, 0, 0, 0, 0, 0, 0]

            sage: M = L([1, 0, 1])
            sage: N = L([0, 0, 1])
            sage: O = M - L.one() - N
            sage: O
            0

        Subtraction with 0::

            sage: M = L(lambda n: 1 + n, valuation=0)
            sage: M - 0 is M
            True
            sage: 0 - M == -M
            True
        """
        P = self.parent()
        left = self._coeff_stream
        right = other._coeff_stream
        if isinstance(left, CoefficientStream_zero):
            return P.element_class(P, CoefficientStream_neg(right))
        if isinstance(right, CoefficientStream_zero):
            return self
        if (isinstance(left, CoefficientStream_exact) and isinstance(right, CoefficientStream_exact)):
            approximate_valuation = min(left.valuation(), right.valuation())
            degree = max(left._degree, right._degree)
            initial_coefficients = [left[i] - right[i] for i in range(approximate_valuation, degree)]
            constant = left._constant - right._constant
            if not any(initial_coefficients) and not constant:
                return P.zero()
            coeff_stream = CoefficientStream_exact(initial_coefficients, P._sparse,
                                                   constant=constant,
                                                   degree=degree,
                                                   valuation=approximate_valuation)
            return P.element_class(P, coeff_stream)
        if left == right:
            return P.zero()
        return P.element_class(P, CoefficientStream_sub(self._coeff_stream, other._coeff_stream))

    def _lmul_(self, scalar):
        r"""
        Scalar multiplication for module elements with the module
        element on the left and the scalar on the right.

        INPUT:

        - ``scalar`` -- an element of the base ring

        EXAMPLES:

        Dense series can be multiplied with a scalar::

            sage: L.<z> = LazyLaurentSeriesRing(ZZ, sparse=False)
            sage: M = L(lambda n: 1 + n, valuation=0)
            sage: O = M * 2
            sage: O[0:10]
            [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
            sage: M * 1== M
            True
            sage: M * 0
            0

        Sparse series can be multiplied with a scalar::

            sage: L.<z> = LazyLaurentSeriesRing(ZZ, sparse=True)
            sage: M = L(lambda n: 1 + n, valuation=0)
            sage: O = M * 2
            sage: O[0:10]
            [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
            sage: M * 1== M
            True
            sage: M * 0
            0

        Series which are known to be exact can be multiplied with a scalar::

            sage: N = L([0, 1])
            sage: O = N * -1
            sage: O[0:10]
            [0, -1, 0, 0, 0, 0, 0, 0, 0, 0]
            sage: N * 1 == N
            True
            sage: N * 0
            0
        """
        P = self.parent()
        if not scalar:
            return P.zero()
        if scalar == 1:
            return self

        if isinstance(self._coeff_stream, CoefficientStream_exact):
            c = self._coeff_stream._constant * scalar
            v = self._coeff_stream.valuation()
            init_coeffs = self._coeff_stream._initial_coefficients
            initial_coefficients = [val * scalar for val in init_coeffs]
            return P.element_class(P, CoefficientStream_exact(initial_coefficients, P._sparse,
                                                              valuation=v, constant=c,
                                                              degree=self._coeff_stream._degree))
        return P.element_class(P, CoefficientStream_lmul(self._coeff_stream, scalar))

    def _rmul_(self, scalar):
        r"""
        Scalar multiplication for module elements with the module
        element on the right and the scalar on the left.

        INPUT:

        - ``scalar`` -- an element of the base ring

        EXAMPLES:

        Dense series can be multiplied with a scalar::

            sage: L.<z> = LazyLaurentSeriesRing(ZZ, sparse=False)
            sage: M = L(lambda n: 1 + n, valuation=0)
            sage: O = 2 * M
            sage: O[0:10]
            [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
            sage: 1 * M == M
            True
            sage: 0 * M
            0

        Sparse series can be multiplied with a scalar::

            sage: L.<z> = LazyLaurentSeriesRing(ZZ, sparse=True)
            sage: M = L(lambda n: 1 + n, valuation=0)
            sage: O = 2 * M
            sage: O[0:10]
            [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
            sage: 1 * M == M
            True
            sage: 0 * M
            0

        Series which are known to be exact can be multiplied with a scalar::

            sage: N = L([0, 1])
            sage: O = -1 * N
            sage: O[0:10]
            [0, -1, 0, 0, 0, 0, 0, 0, 0, 0]
            sage: 1 * N == N
            True
            sage: 0 * N
            0

        Similarly for Dirichlet series::

            sage: L = LazyDirichletSeriesRing(ZZ, "z")
            sage: g = L.gen(2)
            sage: 2 * g
            2/2^z
            sage: -1 * g
            -1/(2^z)
            sage: 0*g
            0
            sage: M = L(lambda n: n); M
            1 + 2/2^z + 3/3^z + 4/4^z + 5/5^z + 6/6^z + 7/7^z + O(1/(8^z))
            sage: 3 * M
            3 + 6/2^z + 9/3^z + 12/4^z + 15/5^z + 18/6^z + 21/7^z + O(1/(8^z))

            sage: 1 * M is M
            True

        We take care of noncommutative base rings::

            sage: M = MatrixSpace(ZZ, 2)
            sage: L.<t> = LazyTaylorSeriesRing(M)
            sage: m = M([[1, 1],[0, 1]])
            sage: n = M([[1, 0],[1, 1]])
            sage: a = L(lambda k: n^k)
            sage: (m*a - a*m)[3]
            [ 3  0]
            [ 0 -3]

        """
        P = self.parent()
        if not scalar:
            return P.zero()
        if scalar == 1:
            return self

        if isinstance(self._coeff_stream, CoefficientStream_exact):
            c = scalar * self._coeff_stream._constant
            v = self._coeff_stream.valuation()
            init_coeffs = self._coeff_stream._initial_coefficients
            initial_coefficients = [scalar * val for val in init_coeffs]
            return P.element_class(P, CoefficientStream_exact(initial_coefficients, P._sparse,
                                                              valuation=v, constant=c,
                                                              degree=self._coeff_stream._degree))
        if P.base_ring().is_commutative():
            return P.element_class(P, CoefficientStream_lmul(self._coeff_stream, scalar))
        return P.element_class(P, CoefficientStream_rmul(self._coeff_stream, scalar))

    def _neg_(self):
        """
        Return the negative of ``self``.

        EXAMPLES:

        Dense series can be negated::

            sage: L.<z> = LazyLaurentSeriesRing(ZZ, sparse=False)
            sage: M = L(lambda n: n, valuation=0)
            sage: N = L(lambda n: -n, valuation=0)
            sage: O = -N
            sage: O[0:10]
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
            sage: O = -M
            sage: O[0:10]
            [0, -1, -2, -3, -4, -5, -6, -7, -8, -9]
            sage: O = -(-M)
            sage: O[0:10]
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
            sage: O == M
            True

        Sparse series can be negated::

            sage: L.<z> = LazyLaurentSeriesRing(ZZ, sparse=True)
            sage: M = L(lambda n: n, valuation=0)
            sage: N = L(lambda n: -n, valuation=0)
            sage: O = -N
            sage: O[0:10]
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
            sage: O = -M
            sage: O[0:10]
            [0, -1, -2, -3, -4, -5, -6, -7, -8, -9]
            sage: O = -(-M)
            sage: O[0:10]
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
            sage: O == M
            True

        Series which are known to be exact can be negated::

            sage: M = L.one()
            sage: N = L([0, 1])
            sage: O = -N
            sage: O[0:10]
            [0, -1, 0, 0, 0, 0, 0, 0, 0, 0]
            sage: O = -M
            sage: O[0:10]
            [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            sage: O = -(-M)
            sage: O[0:10]
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            sage: O == M
            True
        """
        P = self.parent()
        coeff_stream = self._coeff_stream
        if isinstance(self._coeff_stream, CoefficientStream_exact):
            initial_coefficients = [-v for v in coeff_stream._initial_coefficients]
            constant = -coeff_stream._constant
            coeff_stream = CoefficientStream_exact(initial_coefficients, P._sparse,
                                                   constant=constant,
                                                   valuation=coeff_stream.valuation())
            return P.element_class(P, coeff_stream)
        # -(-f) = f
        if isinstance(coeff_stream, CoefficientStream_neg):
            return P.element_class(P, coeff_stream._series)
        return P.element_class(P, CoefficientStream_neg(coeff_stream))


class LazyCauchyProductSeries(RingElement):
    """
    A class for series where multiplication is the Cauchy product.
    """
    def __init__(self, parent):
        """
        Initialize.

        TESTS::

            sage: from sage.rings.lazy_laurent_series import LazyCauchyProductSeries
            sage: L.<z> = LazyLaurentSeriesRing(ZZ)
            sage: M = LazyCauchyProductSeries(L)
        """
        RingElement.__init__(self, parent)

    def _mul_(self, other):
        """
        Return the product of this series with ``other``.

        INPUT:

        - ``other`` -- other series

        TESTS::

            sage: L.<z> = LazyLaurentSeriesRing(ZZ, sparse=True)
            sage: (1 - z)*(1 - z)
            1 - 2*z + z^2
            sage: (1 - z)*(1 - z)*(1 - z)
            1 - 3*z + 3*z^2 - z^3
            sage: M = L(lambda n: n)
            sage: M
            z + 2*z^2 + 3*z^3 + 4*z^4 + 5*z^5 + 6*z^6 + ...
            sage: N = M * (1 - M)
            sage: N
            z + z^2 - z^3 - 6*z^4 - 15*z^5 - 29*z^6 + ...

            sage: p = (1 - z)*(1 + z^2)^3 * z^-2
            sage: p
            z^-2 - z^-1 + 3 - 3*z + 3*z^2 - 3*z^3 + z^4 - z^5
            sage: M = L(lambda n: n, valuation=-2, degree=5, constant=2)
            sage: M
            -2*z^-2 - z^-1 + z + 2*z^2 + 3*z^3 + 4*z^4 + 2*z^5 + 2*z^6 + 2*z^7 + O(z^8)
            sage: M * p
            -2*z^-4 + z^-3 - 5*z^-2 + 4*z^-1 - 2 + 7*z + 5*z^2 + 5*z^3
             + 7*z^4 - 2*z^5 + 4*z^6 - 5*z^7 + z^8 - 2*z^9
            sage: M * p == p * M
            True

            sage: q = (1 - 2*z)*(1 + z^2)^3 * z^-2
            sage: q * M
            -2*z^-4 + 3*z^-3 - 4*z^-2 + 10*z^-1 + 11*z + 2*z^2 - 3*z^3
             - 6*z^4 - 22*z^5 - 14*z^6 - 27*z^7 - 16*z^8 - 20*z^9
             - 16*z^10 - 16*z^11 - 16*z^12 + O(z^13)
            sage: q * M == M * q
            True

            sage: L.<z> = LazyLaurentSeriesRing(ZZ, sparse=False)
            sage: M = L(lambda n: n); M
            z + 2*z^2 + 3*z^3 + 4*z^4 + 5*z^5 + 6*z^6 + ...
            sage: N = L(lambda n: 1); N
            1 + z + z^2 + z^3 + z^4 + z^5 + z^6 + ...
            sage: M * N
            z + 3*z^2 + 6*z^3 + 10*z^4 + 15*z^5 + 21*z^6 + ...

            sage: L.one() * M is M
            True
            sage: M * L.one() is M
            True

        Similarly for Taylor series::

            sage: L.<x, y, z> = LazyTaylorSeriesRing(ZZ)
            sage: (1 - x)*(1 - y)
            1 + (-x-y) + x*y
            sage: (1 - x)*(1 - y)*(1 - z)
            1 + (-x-y-z) + (x*y+x*z+y*z) + (-x*y*z)

        We take care of noncommutative base rings::

            sage: M = MatrixSpace(ZZ, 2)
            sage: L.<t> = LazyTaylorSeriesRing(M)
            sage: m = M([[1, 1],[0, 1]])
            sage: n = M([[1, 0],[1, 1]])
            sage: a = 1/(1-m*t)
            sage: b = 1 + n*t
            sage: (b*a-a*b)[20]
            [-19   0]
            [  0  19]

        Multiplication of series with eventually constant
        coefficients may yield another such series::

            sage: L.<z> = LazyLaurentSeriesRing(SR)
            sage: var("a b c d e u v w")
            (a, b, c, d, e, u, v, w)
            sage: s = a/z^2 + b*z + c*z^2 + d*z^3 + e*z^4
            sage: t = L([u, v], constant=w, valuation=-1)
            sage: s1 = s.approximate_series(44)
            sage: t1 = t.approximate_series(44)
            sage: s1 * t1 - (s * t).approximate_series(42)
            O(z^42)

        Noncommutative::

            sage: M = MatrixSpace(ZZ, 2)
            sage: L.<t> = LazyTaylorSeriesRing(M)
            sage: a = L([m], degree=1)
            sage: b = n*~(1-t)
            sage: (a*b)[0]
            [2 1]
            [1 1]

        """
        P = self.parent()
        left = self._coeff_stream
        right = other._coeff_stream

        # Check some trivial products
        if isinstance(left, CoefficientStream_zero) or isinstance(right, CoefficientStream_zero):
            return P.zero()
        if isinstance(left, CoefficientStream_exact) and left._initial_coefficients == (P._coeff_ring.one(),) and left.valuation() == 0:
            return other  # self == 1
        if isinstance(right, CoefficientStream_exact) and right._initial_coefficients == (P._coeff_ring.one(),) and right.valuation() == 0:
            return self  # right == 1

        # the product is exact if and only if both of the factors are
        # exact, and one has eventually 0 coefficients:
        #   (p + a x^d/(1-x))(q + b x^e/(1-x))
        #   = p q + (a x^d q + b x^e p)/(1-x) + a b x^(d+e)/(1-x)^2
        if (isinstance(left, CoefficientStream_exact)
            and isinstance(right, CoefficientStream_exact)
            and not (left._constant and right._constant)):
            il = left._initial_coefficients
            ir = right._initial_coefficients
            initial_coefficients = [sum(il[k]*ir[n-k]
                                        for k in range(max(n - len(ir) + 1, 0),
                                                       min(len(il) - 1, n) + 1))
                                    for n in range(len(il) + len(ir) - 1)]
            lv = left.valuation()
            rv = right.valuation()
            # (a x^d q)/(1-x) has constant a q(1), and the initial
            # values are the cumulative sums of the coeffcients of q
            if right._constant:
                d = right._degree
                c = left._constant # this is zero
                # left._constant must be 0 and thus len(il) >= 1
                for k in range(len(il)-1):
                    c += il[k] * right._constant
                    initial_coefficients[d - rv + k] += c
                c += il[-1] * right._constant
            elif left._constant:
                d = left._degree
                c = right._constant # this is zero
                # left._constant must be 0 and thus len(il) >= 1
                for k in range(len(ir)-1):
                    c += left._constant * ir[k]
                    initial_coefficients[d - lv + k] += c
                c += left._constant * ir[-1]
            else:
                c = left._constant # this is zero
            coeff_stream = CoefficientStream_exact(initial_coefficients, P._sparse,
                                                   valuation=lv+rv, constant=c)
            return P.element_class(P, coeff_stream)

        return P.element_class(P, CoefficientStream_cauchy_product(left, right))

    def __invert__(self):
        """
        Return the multiplicative inverse of the element.

        EXAMPLES:

        Lazy Laurent series that have a dense implementation can be inverted::

            sage: L.<z> = LazyLaurentSeriesRing(ZZ, sparse=False)
            sage: ~(1 - z)
            1 + z + z^2 + O(z^3)
            sage: M = L(lambda n: n); M
            z + 2*z^2 + 3*z^3 + 4*z^4 + 5*z^5 + 6*z^6 + O(z^7)
            sage: P = ~M; P
            z^-1 - 2 + z + O(z^6)

        Lazy Laurent series that have a sparse implementation can be inverted::

            sage: L.<z> = LazyLaurentSeriesRing(ZZ, sparse=True)
            sage: M = L(lambda n: n); M
            z + 2*z^2 + 3*z^3 + 4*z^4 + 5*z^5 + 6*z^6 + O(z^7)
            sage: P = ~M; P
            z^-1 - 2 + z + O(z^6)

            sage: ~(~(1 - z))
            1 - z

        Lazy Laurent series that are known to be exact can be inverted::

            sage: ~z
            z^-1

        """
        P = self.parent()
        coeff_stream = self._coeff_stream
        # the inverse is exact if and only if coeff_stream corresponds to one of
        # cx^d/(1-x) ... (c, ...)
        # cx^d       ... (c, 0, ...)
        # cx^d (1-x) ... (c, -c, 0, ...)
        if isinstance(coeff_stream, CoefficientStream_exact):
            initial_coefficients = coeff_stream._initial_coefficients
            if not initial_coefficients:
                i = ~coeff_stream._constant
                v = -coeff_stream.valuation()
                c = P._coeff_ring.zero()
                coeff_stream = CoefficientStream_exact((i, -i), P._sparse,
                                                       valuation=v, constant=c)
                return P.element_class(P, coeff_stream)
            if len(initial_coefficients) == 1:
                i = ~initial_coefficients[0]
                v = -coeff_stream.valuation()
                c = P._coeff_ring.zero()
                coeff_stream = CoefficientStream_exact((i,), P._sparse,
                                                       valuation=v, constant=c)
                return P.element_class(P, coeff_stream)
            if len(initial_coefficients) == 2 and not (initial_coefficients[0] + initial_coefficients[1]):
                v = -coeff_stream.valuation()
                c = ~initial_coefficients[0]
                coeff_stream = CoefficientStream_exact((), P._sparse,
                                                       valuation=v, constant=c)
                return P.element_class(P, coeff_stream)

        # (f^-1)^-1 = f
        if isinstance(coeff_stream, CoefficientStream_cauchy_inverse):
            return P.element_class(P, coeff_stream._series)
        return P.element_class(P, CoefficientStream_cauchy_inverse(coeff_stream))

    def _div_(self, other):
        r"""
        Return ``self`` divided by ``other``.

        INPUT:

        - ``other`` -- nonzero series

        EXAMPLES:

        Lazy Laurent series that have a dense implementation can be divided::

            sage: L.<z> = LazyLaurentSeriesRing(ZZ, sparse=False)
            sage: z/(1 - z)
            z + z^2 + z^3 + z^4 + z^5 + z^6 + z^7 + O(z^8)
            sage: M = L(lambda n: n); M
            z + 2*z^2 + 3*z^3 + 4*z^4 + 5*z^5 + 6*z^6 + O(z^7)
            sage: N = L(lambda n: 1); N
            1 + z + z^2 + z^3 + z^4 + z^5 + z^6 + O(z^7)
            sage: P = M / N; P
            z + z^2 + z^3 + z^4 + z^5 + z^6 + O(z^7)

        Lazy Laurent series that have a sparse implementation can be divided::

            sage: L.<z> = LazyLaurentSeriesRing(ZZ, sparse=True)
            sage: M = L(lambda n: n); M
            z + 2*z^2 + 3*z^3 + 4*z^4 + 5*z^5 + 6*z^6 + O(z^7)
            sage: N = L(lambda n: 1); N
            1 + z + z^2 + z^3 + z^4 + z^5 + z^6 + O(z^7)
            sage: P = M / N; P
            z + z^2 + z^3 + z^4 + z^5 + z^6 + O(z^7)

        Lazy Laurent series that are known to be exact can be divided::

            M = z^2 + 2*z + 1
            N = z + 1
            O = M / N; O
            z + 1

        An example over the ring of symmetric functions::

            sage: e = SymmetricFunctions(QQ).e()
            sage: R.<z> = LazyLaurentSeriesRing(e)
            sage: 1 / (1 - e[1]*z)
            e[] + e[1]*z + e[1, 1]*z^2 + e[1, 1, 1]*z^3 + e[1, 1, 1, 1]*z^4
             + e[1, 1, 1, 1, 1]*z^5 + e[1, 1, 1, 1, 1, 1]*z^6 + O(e[]*z^7)
        """
        if isinstance(other._coeff_stream, CoefficientStream_zero):
            raise ZeroDivisionError("cannot divide by 0")

        P = self.parent()
        left = self._coeff_stream
        if isinstance(left, CoefficientStream_zero):
            return P.zero()
        right = other._coeff_stream
        if (isinstance(left, CoefficientStream_exact)
            and isinstance(right, CoefficientStream_exact)):
            if not left._constant and not right._constant:
                R = P._laurent_poly_ring
                # pl = left.polynomial_part(R)
                # pr = right.polynomial_part(R)
                pl = self.finite_part()
                pr = other.finite_part()
                try:
                    ret = pl / pr
                    ret = P._laurent_poly_ring(ret)
                    return P(ret)
                    # ret = pl / pr
                    # ret = P._laurent_poly_ring(ret)
                    # initial_coefficients = [ret[i] for i in range(ret.valuation(), ret.degree() + 1)]
                    # return P.element_class(P, CoefficientStream_exact(initial_coefficients, P._sparse,
                    #          valuation=ret.valuation(), constant=left._constant))
                except (TypeError, ValueError, NotImplementedError):
                    # We cannot divide the polynomials, so the result must be a series
                    pass

        return P.element_class(P, CoefficientStream_cauchy_product(left, CoefficientStream_cauchy_inverse(right)))

    def __pow__(self, n):
        """
        Return the ``n``-th power of the series.

        INPUT:

        - ``n`` -- integer; the power to which to raise the series

        EXAMPLES:

        Lazy Laurent series that have a dense implementation can be
        raised to the power ``n``::

            sage: L.<z> = LazyLaurentSeriesRing(ZZ, sparse=False)
            sage: (1 - z)^-1
            1 + z + z^2 + O(z^3)
            sage: (1 - z)^0
            1
            sage: (1 - z)^3
            1 - 3*z + 3*z^2 - z^3
            sage: (1 - z)^-3
            1 + 3*z + 6*z^2 + 10*z^3 + 15*z^4 + 21*z^5 + 28*z^6 + O(z^7)
            sage: M = L(lambda n: n); M
            z + 2*z^2 + 3*z^3 + 4*z^4 + 5*z^5 + 6*z^6 + O(z^7)
            sage: M^2
            z^2 + 4*z^3 + 10*z^4 + 20*z^5 + 35*z^6 + O(z^7)

        We can create a really large power of a monomial, even with
        the dense implementation::

            sage: z^1000000
            z^1000000

        Lazy Laurent series that have a sparse implementation can be
        raised to the power ``n``::

            sage: L.<z> = LazyLaurentSeriesRing(ZZ, sparse=True)
            sage: M = L(lambda n: n); M
            z + 2*z^2 + 3*z^3 + 4*z^4 + 5*z^5 + 6*z^6 + O(z^7)
            sage: M^2
            z^2 + 4*z^3 + 10*z^4 + 20*z^5 + 35*z^6 + O(z^7)

        Lazy Laurent series that are known to be exact can be raised
        to the power ``n``::

            sage: z^2
            z^2
            sage: (1 - z)^2
            1 - 2*z + z^2
            sage: (1 + z)^2
            1 + 2*z + z^2
        """
        if n == 0:
            return self.parent().one()

        cs = self._coeff_stream
        if (isinstance(cs, CoefficientStream_exact)
            and not cs._constant and n in ZZ
            and (n > 0 or len(cs._initial_coefficients) == 1)):
            P = self.parent()
            return P(self.finite_part() ** ZZ(n))
            # ret = cs.polynomial_part(P._laurent_poly_ring) ** ZZ(n)
            # val = ret.valuation()
            # deg = ret.degree() + 1
            # initial_coefficients = [ret[i] for i in range(val, deg)]
            # return P.element_class(P, CoefficientStream_exact(initial_coefficients, P._sparse,
            #                 constant=cs._constant, degree=deg, valuation=val))

        return generic_power(self, n)


class LazyLaurentSeries(LazySequencesModuleElement, LazyCauchyProductSeries):
    r"""
    A Laurent series where the coefficients are computed lazily.

    EXAMPLES::

        sage: L.<z> = LazyLaurentSeriesRing(ZZ)
        sage: L(lambda i: i, valuation=-3, constant=(-1,3))
        -3*z^-3 - 2*z^-2 - z^-1 + z + 2*z^2 - z^3 - z^4 - z^5 + O(z^6)
        sage: L(lambda i: i, valuation=-3, constant=-1, degree=3)
        -3*z^-3 - 2*z^-2 - z^-1 + z + 2*z^2 - z^3 - z^4 - z^5 + O(z^6)

    ::

        sage: f = 1 / (1 - z - z^2); f
        1 + z + 2*z^2 + 3*z^3 + 5*z^4 + 8*z^5 + 13*z^6 + O(z^7)
        sage: f.coefficient(100)
        573147844013817084101

    Lazy Laurent series is picklable::

        sage: g = loads(dumps(f))
        sage: g
        1 + z + 2*z^2 + 3*z^3 + 5*z^4 + 8*z^5 + 13*z^6 + O(z^7)
        sage: g == f
        True
    """
    def change_ring(self, ring):
        r"""
        Return ``self`` with coefficients converted to elements of ``ring``.

        INPUT:

        - ``ring`` -- a ring

        EXAMPLES:

        Dense Implementation::

            sage: L.<z> = LazyLaurentSeriesRing(ZZ, sparse=False)
            sage: s = 2 + z
            sage: t = s.change_ring(QQ)
            sage: t^-1
            1/2 - 1/4*z + 1/8*z^2 - 1/16*z^3 + 1/32*z^4 - 1/64*z^5 + 1/128*z^6 + O(z^7)
            sage: M = L(lambda n: n); M
            z + 2*z^2 + 3*z^3 + 4*z^4 + 5*z^5 + 6*z^6 + O(z^7)
            sage: N = M.change_ring(QQ)
            sage: N.parent()
            Lazy Laurent Series Ring in z over Rational Field
            sage: M.parent()
            Lazy Laurent Series Ring in z over Integer Ring

        Sparse Implementation::

            sage: L.<z> = LazyLaurentSeriesRing(ZZ, sparse=True)
            sage: M = L(lambda n: n); M
            z + 2*z^2 + 3*z^3 + 4*z^4 + 5*z^5 + 6*z^6 + O(z^7)
            sage: M.parent()
            Lazy Laurent Series Ring in z over Integer Ring
            sage: N = M.change_ring(QQ)
            sage: N.parent()
            Lazy Laurent Series Ring in z over Rational Field
            sage: M ^-1
            z^-1 - 2 + z + O(z^6)
        """
        from .lazy_laurent_series_ring import LazyLaurentSeriesRing
        Q = LazyLaurentSeriesRing(ring, names=self.parent().variable_names())
        return Q.element_class(Q, self._coeff_stream)

    def __call__(self, g):
        r"""
        Return the composition of ``self`` with ``g``.

        Given two Laurent Series `f` and `g` over the same base ring, the
        composition `(f \circ g)(z) = f(g(z))` is defined if and only if:

        - `g = 0` and `val(f) >= 0`,
        - `g` is non-zero and `f` has only finitely many non-zero coefficients,
        - `g` is non-zero and `val(g) > 0`.

        INPUT:

        - ``g`` -- other series

        EXAMPLES::

            sage: L.<z> = LazyLaurentSeriesRing(QQ)
            sage: f = z^2 + 1 + z
            sage: f(0)
            1
            sage: f(L(0))
            1
            sage: f(f)
            3 + 3*z + 4*z^2 + 2*z^3 + z^4
            sage: g = z^-3/(1-2*z); g
            z^-3 + 2*z^-2 + 4*z^-1 + 8 + 16*z + 32*z^2 + 64*z^3 + O(z^4)
            sage: f(g)
            z^-6 + 4*z^-5 + 12*z^-4 + 33*z^-3 + 82*z^-2 + 196*z^-1 + 457 + O(z)
            sage: g^2 + 1 + g
            z^-6 + 4*z^-5 + 12*z^-4 + 33*z^-3 + 82*z^-2 + 196*z^-1 + 457 + O(z)

            sage: f = z^-2 + z + 4*z^3
            sage: f(f)
            4*z^-6 + 12*z^-3 + z^-2 + 48*z^-1 + 12 + O(z)
            sage: f^-2 + f + 4*f^3
            4*z^-6 + 12*z^-3 + z^-2 + 48*z^-1 + 12 + O(z)
            sage: f(g)
            4*z^-9 + 24*z^-8 + 96*z^-7 + 320*z^-6 + 960*z^-5 + 2688*z^-4 + 7169*z^-3 + O(z^-2)
            sage: g^-2 + g + 4*g^3
            4*z^-9 + 24*z^-8 + 96*z^-7 + 320*z^-6 + 960*z^-5 + 2688*z^-4 + 7169*z^-3 + O(z^-2)

            sage: f = z^-3 + z^-2 + 1 / (1 + z^2); f
            z^-3 + z^-2 + 1 - z^2 + O(z^4)
            sage: g = z^3 / (1 + z - z^3); g
            z^3 - z^4 + z^5 - z^7 + 2*z^8 - 2*z^9 + O(z^10)
            sage: f(g)
            z^-9 + 3*z^-8 + 3*z^-7 - z^-6 - 4*z^-5 - 2*z^-4 + z^-3 + O(z^-2)
            sage: g^-3 + g^-2 + 1 / (1 + g^2)
            z^-9 + 3*z^-8 + 3*z^-7 - z^-6 - 4*z^-5 - 2*z^-4 + z^-3 + O(z^-2)

            sage: f = z^-3; g = z^-2 + z^-1;
            sage: g^(-3)
            z^6 - 3*z^7 + 6*z^8 - 10*z^9 + 15*z^10 - 21*z^11 + 28*z^12 + O(z^13)
            sage: f(g)
            z^6 - 3*z^7 + 6*z^8 - 10*z^9 + 15*z^10 - 21*z^11 + 28*z^12 + O(z^13)

            sage: f = L(lambda n: n); f
            z + 2*z^2 + 3*z^3 + 4*z^4 + 5*z^5 + 6*z^6 + O(z^7)
            sage: f(z^2)
            z^2 + 2*z^4 + 3*z^6 + O(z^7)

            sage: f = L(lambda n: n, -2); f
            -2*z^-2 - z^-1 + z + 2*z^2 + 3*z^3 + 4*z^4 + O(z^5)
            sage: f3 = f(z^3); f3
            -2*z^-6 - z^-3 + O(z)
            sage: [f3[i] for i in range(-6,13)]
            [-2, 0, 0, -1, 0, 0, 0, 0, 0, 1, 0, 0, 2, 0, 0, 3, 0, 0, 4]

        We compose a Laurent polynomial with a generic element::

            sage: R.<x> = QQ[]
            sage: f = z^2 + 1 + z^-1
            sage: g = x^2 + x + 3
            sage: f(g)
            (x^6 + 3*x^5 + 12*x^4 + 19*x^3 + 37*x^2 + 28*x + 31)/(x^2 + x + 3)
            sage: f(g) == g^2 + 1 + g^-1
            True

        We compose with another lazy Laurent series::

            sage: LS.<y> = LazyLaurentSeriesRing(QQ)
            sage: f = z^2 + 1 + z^-1
            sage: fy = f(y); fy
            y^-1 + 1 + y^2
            sage: fy.parent() is LS
            True
            sage: g = y - y
            sage: f(g)
            Traceback (most recent call last):
            ...
            ZeroDivisionError: the valuation of the series must be nonnegative

            sage: g = 1 - y
            sage: f(g)
            3 - y + 2*y^2 + y^3 + y^4 + y^5 + O(y^6)
            sage: g^2 + 1 + g^-1
            3 - y + 2*y^2 + y^3 + y^4 + y^5 + O(y^6)

            sage: f = L(lambda n: n, 0); f
            z + 2*z^2 + 3*z^3 + 4*z^4 + 5*z^5 + 6*z^6 + O(z^7)
            sage: f(0)
            0
            sage: f(y)
            y + 2*y^2 + 3*y^3 + 4*y^4 + 5*y^5 + 6*y^6 + O(y^7)
            sage: fp = f(y - y)
            sage: fp == 0
            True
            sage: fp.parent() is LS
            True

            sage: f = z^2 + 3 + z
            sage: f(y - y)
            3

        With both of them sparse::

            sage: L.<z> = LazyLaurentSeriesRing(QQ, sparse=True)
            sage: LS.<y> = LazyLaurentSeriesRing(QQ, sparse=True)
            sage: f = L(lambda n: 1); f
            1 + z + z^2 + z^3 + z^4 + z^5 + z^6 + O(z^7)
            sage: f(y^2)
            1 + y^2 + y^4 + y^6 + O(y^7)

            sage: fp = f - 1 + z^-2; fp
            z^-2 + z + z^2 + z^3 + z^4 + O(z^5)
            sage: fpy = fp(y^2); fpy
            y^-4 + y^2 + O(y^3)
            sage: fpy.parent() is LS
            True
            sage: [fpy[i] for i in range(-4,11)]
            [1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1]

            sage: g = LS(valuation=2, constant=1); g
            y^2 + y^3 + y^4 + O(y^5)
            sage: fg = f(g); fg
            1 + y^2 + y^3 + 2*y^4 + 3*y^5 + 5*y^6 + O(y^7)
            sage: 1 + g + g^2 + g^3 + g^4 + g^5 + g^6
            1 + y^2 + y^3 + 2*y^4 + 3*y^5 + 5*y^6 + O(y^7)

            sage: h = LS(lambda n: 1 if n % 2 else 0, 2); h
            y^3 + y^5 + y^7 + O(y^9)
            sage: fgh = fg(h); fgh
            1 + y^6 + O(y^7)
            sage: [fgh[i] for i in range(0, 15)]
            [1, 0, 0, 0, 0, 0, 1, 0, 2, 1, 3, 3, 6, 6, 13]
            sage: t = 1 + h^2 + h^3 + 2*h^4 + 3*h^5 + 5*h^6
            sage: [t[i] for i in range(0, 15)]
            [1, 0, 0, 0, 0, 0, 1, 0, 2, 1, 3, 3, 6, 6, 13]

        We look at mixing the sparse and the dense::

            sage: L.<z> = LazyLaurentSeriesRing(QQ)
            sage: f = L(lambda n: 1); f
            1 + z + z^2 + z^3 + z^4 + z^5 + z^6 + O(z^7)
            sage: g = LS(lambda n: 1, 1); g
            y + y^2 + y^3 + y^4 + y^5 + y^6 + y^7 + O(y^8)
            sage: f(g)
            1 + y + 2*y^2 + 4*y^3 + 8*y^4 + 16*y^5 + 32*y^6 + O(y^7)

            sage: f = z^-2 + 1 + z
            sage: g = 1/(y*(1-y)); g
            y^-1 + 1 + y + y^2 + y^3 + y^4 + y^5 + O(y^6)
            sage: f(g)
            y^-1 + 2 + y + 2*y^2 - y^3 + 2*y^4 + y^5 + O(y^6)
            sage: g^-2 + 1 + g
            y^-1 + 2 + y + 2*y^2 - y^3 + 2*y^4 + y^5 + O(y^6)

            sage: f = z^-3 + z^-2 + 1
            sage: g = 1/(y^2*(1-y)); g
            y^-2 + y^-1 + 1 + y + y^2 + y^3 + y^4 + O(y^5)
            sage: f(g)
            1 + y^4 - 2*y^5 + 2*y^6 + O(y^7)
            sage: g^-3 + g^-2 + 1
            1 + y^4 - 2*y^5 + 2*y^6 + O(y^7)
            sage: z(y)
            y

        We look at cases where the composition does not exist.
        `g = 0` and `val(f) < 0`::

            sage: g = L(0)
            sage: f = z^-1 + z^-2
            sage: f.valuation() < 0
            True
            sage: f(g)
            Traceback (most recent call last):
            ...
            ZeroDivisionError: the valuation of the series must be nonnegative

        `g \neq 0` and `val(g) \leq 0` and `f` has infinitely many
        non-zero coefficients`::

            sage: g = z^-1 + z^-2
            sage: g.valuation() <= 0
            True
            sage: f = L(lambda n: n, 0)
            sage: f(g)
            Traceback (most recent call last):
            ...
            ValueError: can only compose with a positive valuation series

        We cannot compose if `g` has a negative valuation::

            sage: f = L(lambda n: n, 1)
            sage: g = 1 + z
            sage: f(g)
            Traceback (most recent call last):
            ...
            ValueError: can only compose with a positive valuation series
        """
        # f = self and compute f(g)
        P = g.parent()

        # g = 0 case
        if ((not isinstance(g, LazyLaurentSeries) and not g)
            or (isinstance(g, LazyLaurentSeries)
                and isinstance(g._coeff_stream, CoefficientStream_zero))):
            if self._coeff_stream._approximate_valuation >= 0:
                return P(self[0])
            # Perhaps we just don't yet know if the valuation is non-negative
            if any(self._coeff_stream[i] for i in range(self._coeff_stream._approximate_valuation, 0)):
                raise ZeroDivisionError("the valuation of the series must be nonnegative")
            self._coeff_stream._approximate_valuation = 0
            return P(self[0])

        # f has finite length
        if isinstance(self._coeff_stream, CoefficientStream_zero):  # constant 0
            return self
        if isinstance(self._coeff_stream, CoefficientStream_exact) and not self._coeff_stream._constant:
            # constant polynomial
            R = self.parent()._laurent_poly_ring
            poly = self._coeff_stream.polynomial_part(R)
            if poly.is_constant():
                return self
            if not isinstance(g, LazyLaurentSeries):
                return poly(g)
            # g also has finite length, compose the polynomials
            if isinstance(g._coeff_stream, CoefficientStream_exact) and not g._coeff_stream._constant:
                R = P._laurent_poly_ring
                g_poly = g._coeff_stream.polynomial_part(R)
                try:
                    ret = poly(g_poly)
                except (ValueError, TypeError):  # the result is not a Laurent polynomial
                    ret = None
                if ret is not None and ret.parent() is R:
                    val = ret.valuation()
                    deg = ret.degree() + 1
                    initial_coefficients = [ret[i] for i in range(val, deg)]
                    coeff_stream = CoefficientStream_exact(initial_coefficients,
                             self._coeff_stream._is_sparse, constant=P.base_ring().zero(),
                             degree=deg, valuation=val)
                    return P.element_class(P, coeff_stream)

            # Return the sum since g is not known to be finite or we do not get a Laurent polynomial
            # TODO: Optimize when f has positive valuation
            ret = P.zero()
            gp = P.one()
            # We build this iteratively so each power can benefit from the caching
            # Equivalent to P.sum(poly[i] * g**i for i in range(poly.valuation(), poly.degree()+1))
            # We could just do "return poly(g)" if we don't care about speed
            d = poly.degree()
            if d >= 0:
                for i in range(d):
                    ret += poly[i] * gp
                    gp *= g
                ret += poly[d] * gp
            v = poly.valuation()
            if v < 0:
                gi = ~g
                gp = P.one()
                for i in range(-1, v-1, -1):
                    gp *= gi
                    ret += poly[i] * gp
            return ret

        # g != 0 and val(g) > 0
        if not isinstance(g, LazyLaurentSeries):
            try:
                g = self.parent()(g)
            except (TypeError, ValueError):
                raise NotImplementedError("can only compose with a lazy Laurent series")
        # Perhaps we just don't yet know if the valuation is positive
        if g._coeff_stream._approximate_valuation <= 0:
            if any(g._coeff_stream[i] for i in range(g._coeff_stream._approximate_valuation, 1)):
                raise ValueError("can only compose with a positive valuation series")
            g._coeff_stream._approximate_valuation = 1

        return P.element_class(P, CoefficientStream_composition(self._coeff_stream, g._coeff_stream))

    def revert(self):
        r"""
        Return the compositional inverse of ``self``.

        EXAMPLES::

            sage: L.<z> = LazyLaurentSeriesRing(ZZ)
            sage: z.revert()
            z + O(z^8)
            sage: (1/z).revert()
            z^-1 + O(z^6)

            sage: (z-z^2).revert()
            z + z^2 + 2*z^3 + 5*z^4 + 14*z^5 + 42*z^6 + 132*z^7 + O(z^8)

        """
        P = self.parent()
        z = P.gen()
        if self._coeff_stream._approximate_valuation == 1:
            g = self
        else:
            g = self * z**(1 - self._coeff_stream._approximate_valuation)
        f = P(None, valuation=1)
        f.define(z/((g/z)(f)))
        if self._coeff_stream._approximate_valuation == 1:
            return f
        else:
            return f / z**(1 - self._coeff_stream._approximate_valuation)

    def approximate_series(self, prec, name=None):
        """
        Return the Laurent series with absolute precision ``prec`` approximated
        from this series.

        INPUT:

        - ``prec`` -- an integer
        - ``name`` -- name of the variable; if it is ``None``, the name of
          the variable of the series is used

        OUTPUT: a Laurent series with absolute precision ``prec``

        EXAMPLES::

            sage: L = LazyLaurentSeriesRing(ZZ, 'z')
            sage: z = L.gen()
            sage: f = (z - 2*z^3)^5/(1 - 2*z)
            sage: f
            z^5 + 2*z^6 - 6*z^7 - 12*z^8 + 16*z^9 + 32*z^10 - 16*z^11 + O(z^12)
            sage: g = f.approximate_series(10)
            sage: g
            z^5 + 2*z^6 - 6*z^7 - 12*z^8 + 16*z^9 + O(z^10)
            sage: g.parent()
            Power Series Ring in z over Integer Ring
            sage: h = (f^-1).approximate_series(3)
            sage: h
            z^-5 - 2*z^-4 + 10*z^-3 - 20*z^-2 + 60*z^-1 - 120 + 280*z - 560*z^2 + O(z^3)
            sage: h.parent()
            Laurent Series Ring in z over Integer Ring
        """
        S = self.parent()

        if name is None:
            name = S.variable_name()

        if self.valuation() < 0:
            from sage.rings.all import LaurentSeriesRing
            R = LaurentSeriesRing(S.base_ring(), name=name)
            n = self.valuation()
            return R([self[i] for i in range(n, prec)], n).add_bigoh(prec)
        else:
            from sage.rings.all import PowerSeriesRing
            R = PowerSeriesRing(S.base_ring(), name=name)
            return R([self[i] for i in range(prec)]).add_bigoh(prec)

    def polynomial(self, degree=None, name=None):
        r"""
        Return ``self`` as a Laurent polynomial if ``self`` is actually so.

        INPUT:

        - ``degree`` -- ``None`` or an integer
        - ``name`` -- name of the variable; if it is ``None``, the name of
          the variable of the series is used

        OUTPUT:

        A Laurent polynomial if the valuation of the series is negative or
        a polynomial otherwise.

        If ``degree`` is not ``None``, the terms of the series of degree
        greater than ``degree`` are truncated first. If ``degree`` is ``None``
        and the series is not a polynomial or a Laurent polynomial, a
        ``ValueError`` is raised.

        EXAMPLES::

            sage: L.<z> = LazyLaurentSeriesRing(ZZ)
            sage: f = L([1,0,0,2,0,0,0,3], 5); f
            z^5 + 2*z^8 + 3*z^12
            sage: f.polynomial()
            3*z^12 + 2*z^8 + z^5

        TESTS::

            sage: g = L([1,0,0,2,0,0,0,3], -5); g
            z^-5 + 2*z^-2 + 3*z^2
            sage: g.polynomial()
            z^-5 + 2*z^-2 + 3*z^2
            sage: z = L.gen()
            sage: f = (1 + z)/(z^3 - z^5)
            sage: f
            z^-3 + z^-2 + z^-1 + 1 + z + z^2 + z^3 + O(z^4)
            sage: f.polynomial(5)
            z^-3 + z^-2 + z^-1 + 1 + z + z^2 + z^3 + z^4 + z^5
            sage: f.polynomial(0)
            z^-3 + z^-2 + z^-1 + 1
            sage: f.polynomial(-5)
            0
            sage: M = L(lambda n: n^2, 0)
            sage: M.polynomial(3)
            9*z^3 + 4*z^2 + z
            sage: M = L(lambda n: n^2, 0)
            sage: M.polynomial(5)
            25*z^5 + 16*z^4 + 9*z^3 + 4*z^2 + z

            sage: f = 1/(1 + z)
            sage: f.polynomial()
            Traceback (most recent call last):
            ...
            ValueError: not a polynomial

            sage: L.zero().polynomial()
            0
        """
        S = self.parent()

        if degree is None:
            if isinstance(self._coeff_stream, CoefficientStream_zero):
                from sage.rings.all import PolynomialRing
                return PolynomialRing(S.base_ring(), name=name).zero()
            elif isinstance(self._coeff_stream, CoefficientStream_exact) and not self._coeff_stream._constant:
                m = self._coeff_stream._degree
            else:
                raise ValueError("not a polynomial")
        else:
            m = degree + 1

        if name is None:
            name = S.variable_name()

        if self.valuation() < 0:
            R = LaurentPolynomialRing(S.base_ring(), name=name)
            n = self.valuation()
            return R([self[i] for i in range(n, m)]).shift(n)
        else:
            from sage.rings.all import PolynomialRing
            R = PolynomialRing(S.base_ring(), name=name)
            return R([self[i] for i in range(m)])

    def _format_series(self, formatter, format_strings=False):
        """
        Return ``self`` formatted by ``formatter``.

        TESTS::

            sage: L.<z> = LazyLaurentSeriesRing(QQ)
            sage: f = 1 / (2 - z^2)
            sage: f._format_series(ascii_art, True)
            1/2 + 1/4*z^2 + 1/8*z^4 + 1/16*z^6 + O(z^7)
        """
        P = self.parent()
        R = P._laurent_poly_ring
        z = R.gen()
        cs = self._coeff_stream
        v = cs._approximate_valuation
        if format_strings:
            strformat = formatter
        else:
            strformat = lambda x: x

        if isinstance(cs, CoefficientStream_exact):
            poly = cs.polynomial_part(R)
            if not cs._constant:
                return formatter(poly)
            m = cs._degree + P.options.constant_length
            poly += sum([cs._constant * z**k for k in range(cs._degree, m)])
            return formatter(poly) + strformat(" + O({})".format(formatter(z**m)))

        # This is an inexact series
        m = v + P.options.display_length

        # Use the polynomial printing
        poly = R([self._coeff_stream[i] for i in range(v, m)]).shift(v)
        if not poly:
            return strformat("O({})".format(formatter(z**m)))
        return formatter(poly) + strformat(" + O({})".format(formatter(z**m)))


class LazyTaylorSeries(LazySequencesModuleElement, LazyCauchyProductSeries):
    r"""
    A Taylor series where the coefficients are computed lazily.

    EXAMPLES::

        sage: L.<x, y> = LazyTaylorSeriesRing(ZZ)
        sage: f = 1 / (1 - x^2 + y^3); f
        1 + x^2 + (-y^3) + x^4 + (-2*x^2*y^3) + (x^6+y^6) + O(x,y)^7
        sage: P.<x, y> = PowerSeriesRing(ZZ, default_prec=101)
        sage: g = 1 / (1 - x^2 + y^3); f[100] - g[100]
        0

    Lazy Taylor series is picklable::

        sage: g = loads(dumps(f))
        sage: g
        1 + x^2 + (-y^3) + x^4 + (-2*x^2*y^3) + (x^6+y^6) + O(x,y)^7
        sage: g == f
        True
    """
    def __call__(self, *g):
        r"""Return the composition of ``self`` with ``g``.

        The arity of ``self`` must be equal to the number of
        arguments provided.

        Given two Taylor Series `f` and `g` over the same base ring, the
        composition `(f \circ g)(z) = f(g(z))` is defined if and only if:

        - `g = 0` and `val(f) >= 0`,
        - `g` is non-zero and `f` has only finitely many non-zero coefficients,
        - `g` is non-zero and `val(g) > 0`.

        INPUT:

        - ``g`` -- other series, all of the same parent.

        EXAMPLES::

            sage: L.<x, y, z> = LazyTaylorSeriesRing(QQ)
            sage: M.<a, b> = LazyTaylorSeriesRing(ZZ)
            sage: g1 = 1/(1-x); g2 = x+y^2
            sage: p = a^2 + b + 1
            sage: p(g1, g2) - g1^2 - g2 - 1
            O(x,y,z)^7

            sage: L.<x, y, z> = LazyTaylorSeriesRing(QQ)
            sage: M.<a> = LazyTaylorSeriesRing(QQ)

        The number of mappings from a set with `m` elements to a set
        with `n` elements::

            sage: Ea = M(lambda n: 1/factorial(n))
            sage: Ex = L(lambda n: 1/factorial(n)*x^n)
            sage: Ea(Ex*y)[5]
            1/24*x^4*y + 2/3*x^3*y^2 + 3/4*x^2*y^3 + 1/6*x*y^4 + 1/120*y^5

        So, there are `3! 2! 2/3 = 8` mappings from a three element
        set to a two element set.

        TESTS::

            sage: L.<x,y> = LazyTaylorSeriesRing(ZZ)
            sage: f = 1/(1-x-y)
            sage: f(f)
            Traceback (most recent call last):
            ...
            ValueError: arity of must be equal to the number of arguments provided

        """
        if len(g) != len(self.parent().variable_names()):
            raise ValueError("arity of must be equal to the number of arguments provided")

        # f has finite length
        if isinstance(self._coeff_stream, CoefficientStream_exact) and not self._coeff_stream._constant:
            # constant polynomial
            poly = self.finite_part()
            if poly.is_constant():
                return self
            return poly(g)

        g0 = g[0]
        P = g0.parent()
        R = P._coeff_ring
        if len(g) == 1:
            # we assume that the valuation of self[i](g) is at least i
            def coefficient(n):
                r = R(0)
                for i in range(n+1):
                    r += self[i]*(g0 ** i)[n]
                return r
        else:
            def coefficient(n):
                r = R(0)
                for i in range(n+1):
                    r += self[i](g)[n]
                return r
        coeff_stream = CoefficientStream_coefficient_function(coefficient, P._coeff_ring, P._sparse, 0)
        return P.element_class(P, coeff_stream)

    def change_ring(self, ring):
        """
        Return this series with coefficients converted to elements of ``ring``.

        INPUT:

        - ``ring`` -- a ring

        EXAMPLES::

            sage: L.<z> = LazyTaylorSeriesRing(ZZ)
            sage: s = 2 + z
            sage: t = s.change_ring(QQ)
            sage: t^-1
            1/2 - 1/4*z + 1/8*z^2 - 1/16*z^3 + 1/32*z^4 - 1/64*z^5 + 1/128*z^6 + O(z^7)
            sage: t.parent()
            Lazy Taylor Series Ring in z over Rational Field

        """
        from .lazy_laurent_series_ring import LazyTaylorSeriesRing
        Q = LazyTaylorSeriesRing(ring, names=self.parent().variable_names())
        return Q.element_class(Q, self._coeff_stream)

    def _format_series(self, formatter, format_strings=False):
        """
        Return nonzero ``self`` formatted by ``formatter``.

        TESTS::

            sage: L.<x, y> = LazyTaylorSeriesRing(QQ)
            sage: f = 1 / (2 - x^2 + y)
            sage: f._format_series(repr)
            '1/2 + (-1/4*y) + (1/4*x^2+1/8*y^2) + (-1/4*x^2*y-1/16*y^3) + (1/8*x^4+3/16*x^2*y^2+1/32*y^4) + (-3/16*x^4*y-1/8*x^2*y^3-1/64*y^5) + (1/16*x^6+3/16*x^4*y^2+5/64*x^2*y^4+1/128*y^6) + O(x,y)^7'

            sage: f = (2 - x^2 + y)
            sage: f._format_series(repr)
            '2 + y + (-x^2)'
        """
        P = self.parent()
        cs = self._coeff_stream
        v = cs._approximate_valuation
        if isinstance(cs, CoefficientStream_exact):
            if not cs._constant:
                m = cs._degree
            else:
                m = cs._degree + P.options.constant_length
        else:
            m = v + P.options.display_length

        atomic_repr = P._coeff_ring._repr_option('element_is_atomic')
        mons = [P.monomial(self[i], i) for i in range(v, m) if self[i]]
        if not isinstance(cs, CoefficientStream_exact) or cs._constant:
            if P._coeff_ring is P.base_ring():
                bigO = ["O(%s)" % P.monomial(1, m)]
            else:
                bigO = ["O(%s)^%s" % (', '.join(str(g) for g in P._names), m)]
        else:
            bigO = []

        from sage.misc.latex import latex
        from sage.typeset.unicode_art import unicode_art
        from sage.typeset.ascii_art import ascii_art
        from sage.misc.repr import repr_lincomb
        from sage.typeset.symbols import ascii_left_parenthesis, ascii_right_parenthesis
        from sage.typeset.symbols import unicode_left_parenthesis, unicode_right_parenthesis
        if formatter == repr:
            poly = repr_lincomb([(1, m) for m in mons + bigO], strip_one=True)
        elif formatter == latex:
            poly = repr_lincomb([(1, m) for m in mons + bigO], is_latex=True, strip_one=True)
        elif formatter == ascii_art:
            if atomic_repr:
                poly = ascii_art(*(mons + bigO), sep = " + ")
            else:
                def parenthesize(m):
                    a = ascii_art(m)
                    h = a.height()
                    return ascii_art(ascii_left_parenthesis.character_art(h),
                                     a, ascii_right_parenthesis.character_art(h))
                poly = ascii_art(*([parenthesize(m) for m in mons] + bigO), sep = " + ")
        elif formatter == unicode_art:
            if atomic_repr:
                poly = unicode_art(*(mons + bigO), sep = " + ")
            else:
                def parenthesize(m):
                    a = unicode_art(m)
                    h = a.height()
                    return unicode_art(unicode_left_parenthesis.character_art(h),
                                       a, unicode_right_parenthesis.character_art(h))
                poly = unicode_art(*([parenthesize(m) for m in mons] + bigO), sep = " + ")

        return poly


class LazyDirichletSeries(LazySequencesModuleElement):
    r"""
    A Dirichlet series where the coefficients are computed lazily.

    INPUT:

    - ``parent`` -- The base ring for the series

    - ``coeff_stream`` -- The auxiliary class that handles the coefficient stream

    EXAMPLES::

        sage: L = LazyDirichletSeriesRing(ZZ, "z")
        sage: f = L(constant=1)^2; f
        1 + 2/2^z + 2/3^z + 3/4^z + 2/5^z + 4/6^z + 2/7^z + ...
        sage: f.coefficient(100) == number_of_divisors(100)
        True

    Lazy Dirichlet series is picklable::

        sage: g = loads(dumps(f))
        sage: g
        1 + 2/2^z + 2/3^z + 3/4^z + 2/5^z + 4/6^z + 2/7^z + ...
        sage: g == f
        True
    """
    def _mul_(self, other):
        """
        Return the product of this series with ``other``.

        INPUT:

        - ``other`` -- other series

        TESTS::

            sage: L = LazyDirichletSeriesRing(ZZ, "z")
            sage: g = L(constant=1); g
            1 + 1/(2^z) + 1/(3^z) + O(1/(4^z))
            sage: g*g
            1 + 2/2^z + 2/3^z + 3/4^z + 2/5^z + 4/6^z + 2/7^z + O(1/(8^z))
            sage: [number_of_divisors(n) for n in range(1, 8)]
            [1, 2, 2, 3, 2, 4, 2]

            sage: mu = L(moebius); mu
            1 - 1/(2^z) - 1/(3^z) - 1/(5^z) + 1/(6^z) - 1/(7^z) + O(1/(8^z))
            sage: g*mu
            1 + O(1/(8^z))
            sage: L.one() * mu is mu
            True
            sage: mu * L.one() is mu
            True
        """
        P = self.parent()
        left = self._coeff_stream
        right = other._coeff_stream
        if (isinstance(left, CoefficientStream_exact)
            and left._initial_coefficients == (P._coeff_ring.one(),)
            and left.valuation() == 1):
            return other  # self == 1
        if (isinstance(right, CoefficientStream_exact)
            and right._initial_coefficients == (P._coeff_ring.one(),)
            and right.valuation() == 1):
            return self

        coeff = CoefficientStream_dirichlet_convolution(left, right)
        return P.element_class(P, coeff)

    def __invert__(self):
        """
        Return the multiplicative inverse of the element.

        TESTS::

            sage: L = LazyDirichletSeriesRing(ZZ, "z", sparse=False)
            sage: ~L(constant=1) - L(moebius)
            O(1/(8^z))
            sage: L = LazyDirichletSeriesRing(ZZ, "z", sparse=True)
            sage: ~L(constant=1) - L(moebius)
            O(1/(8^z))

        """
        P = self.parent()
        return P.element_class(P, CoefficientStream_dirichlet_inv(self._coeff_stream))

    def change_ring(self, ring):
        """
        Return this series with coefficients converted to elements of ``ring``.

        INPUT:

        - ``ring`` -- a ring

        TESTS::

            sage: L = LazyDirichletSeriesRing(ZZ, "z", sparse=False)
        """
        from .lazy_laurent_series_ring import LazyDirichletSeriesRing
        Q = LazyDirichletSeriesRing(ring, names=self.parent().variable_names())
        return Q.element_class(Q, self._coeff_stream)

    def __pow__(self, n):
        """
        Return the ``n``-th power of the series.

        INPUT:

        - ``n`` -- integer, the power to which to raise the series

        TESTS::

            sage: L = LazyDirichletSeriesRing(ZZ, "z")
        """
        if n == 0:
            return self.parent().one()

        return generic_power(self, n)

    def _format_series(self, formatter, format_strings=False):
        """
        Return nonzero ``self`` formatted by ``formatter``.

        TESTS::

            sage: L = LazyDirichletSeriesRing(QQ, "s")
            sage: f = L(constant=1)
            sage: f._format_series(repr)
            '1 + 1/(2^s) + 1/(3^s) + O(1/(4^s))'

            sage: L([1,-1,1])._format_series(repr)
            '1 - 1/(2^s) + 1/(3^s)'

            sage: L([1,-1,1])._format_series(ascii_art)
                  -s    -s
            1 + -2   + 3

        """
        P = self.parent()
        cs = self._coeff_stream
        v = cs._approximate_valuation
        if isinstance(cs, CoefficientStream_exact):
            if not cs._constant:
                m = cs._degree
            else:
                m = cs._degree + P.options.constant_length
        else:
            m = v + P.options.display_length

        atomic_repr = P._coeff_ring._repr_option('element_is_atomic')
        mons = [P.monomial(self[i], i) for i in range(v, m) if self[i]]
        if not isinstance(cs, CoefficientStream_exact) or cs._constant:
            if P._coeff_ring is P.base_ring():
                bigO = ["O(%s)" % P.monomial(1, m)]
            else:
                bigO = ["O(%s)^%s" % (', '.join(str(g) for g in P._names), m)]
        else:
            bigO = []

        from sage.misc.latex import latex
        from sage.typeset.unicode_art import unicode_art
        from sage.typeset.ascii_art import ascii_art
        from sage.misc.repr import repr_lincomb
        from sage.typeset.symbols import ascii_left_parenthesis, ascii_right_parenthesis
        from sage.typeset.symbols import unicode_left_parenthesis, unicode_right_parenthesis
        if formatter == repr:
            poly = repr_lincomb([(1, m) for m in mons + bigO], strip_one=True)
        elif formatter == latex:
            poly = repr_lincomb([(1, m) for m in mons + bigO], is_latex=True, strip_one=True)
        elif formatter == ascii_art:
            if atomic_repr:
                poly = ascii_art(*(mons + bigO), sep = " + ")
            else:
                def parenthesize(m):
                    a = ascii_art(m)
                    h = a.height()
                    return ascii_art(ascii_left_parenthesis.character_art(h),
                                     a, ascii_right_parenthesis.character_art(h))
                poly = ascii_art(*([parenthesize(m) for m in mons] + bigO), sep = " + ")
        elif formatter == unicode_art:
            if atomic_repr:
                poly = unicode_art(*(mons + bigO), sep = " + ")
            else:
                def parenthesize(m):
                    a = unicode_art(m)
                    h = a.height()
                    return unicode_art(unicode_left_parenthesis.character_art(h),
                                       a, unicode_right_parenthesis.character_art(h))
                poly = unicode_art(*([parenthesize(m) for m in mons] + bigO), sep = " + ")

        return poly
