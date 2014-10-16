r"""
Generating Series

This file makes a number of extensions to lazy power series by
endowing them with some semantic content for how they're to be
interpreted.

This code is based on the work of Ralf Hemmecke and Martin Rubey's
Aldor-Combinat, which can be found at
http://www.risc.uni-linz.ac.at/people/hemmecke/aldor/combinat/index.html.
In particular, the relevant section for this file can be found at
http://www.risc.uni-linz.ac.at/people/hemmecke/AldorCombinat/combinatse10.html.
One notable difference is that we use power-sum symmetric functions
as the coefficients of our cycle index series.

TESTS::

    sage: from sage.combinat.species.generating_series import CycleIndexSeriesRing
    sage: p = SymmetricFunctions(QQ).power()
    sage: CIS = CycleIndexSeriesRing(QQ)

::

    sage: geo1 = CIS((p([1])^i  for i in NN))
    sage: geo2 = CIS((p([2])^i  for i in NN))
    sage: s = geo1 * geo2
    sage: s[0]
    p[]
    sage: s[1]
    p[1] + p[2]
    sage: s[2]
    p[1, 1] + p[2, 1] + p[2, 2]
    sage: s[3]
    p[1, 1, 1] + p[2, 1, 1] + p[2, 2, 1] + p[2, 2, 2]

Whereas the coefficients of the above test are homogeneous with
respect to total degree, the following test groups with respect to
weighted degree where each variable x_i has weight i.

::

    sage: def g():
    ....:     for i in NN:
    ....:         yield p([2])^i
    ....:         yield p(0)
    sage: geo1 = CIS((p([1])^i  for i in NN))
    sage: geo2 = CIS(g())
    sage: s = geo1 * geo2
    sage: s[0]
    p[]
    sage: s[1]
    p[1]
    sage: s[2]
    p[1, 1] + p[2]
    sage: s[3]
    p[1, 1, 1] + p[2, 1]
    sage: s[4]
    p[1, 1, 1, 1] + p[2, 1, 1] + p[2, 2]
"""
#*****************************************************************************
#       Copyright (C) 2008 Mike Hansen <mhansen@gmail.com>,
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#    This code is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    General Public License for more details.
#
#  The full text of the GPL is available at:
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************
from series import (LazyPowerSeriesRing, LazyPowerSeries)
from series_stream import (SeriesStream, PowerStream, SumGeneratorStream,
                           ListSumStream, TermStream, SeriesStreamFromIterator)
from sage.rings.all import ZZ, Integer, moebius, lcm, divisors, gcd, NN
from sage.combinat.sf.sf import SymmetricFunctions
from sage.misc.cachefunc import cached_function
from sage.combinat.partition import Partition, Partitions
from sage.structure.element import coerce_binop


class OrdinaryGeneratingSeriesRing(LazyPowerSeriesRing):
    def __init__(self, R):
        """
        Return the ring of ordinary generating series.

        Note that is is
        just a LazyPowerSeriesRing whose elements have some extra methods.

        EXAMPLES::

            sage: from sage.combinat.species.generating_series import OrdinaryGeneratingSeriesRing
            sage: R = OrdinaryGeneratingSeriesRing(QQ); R
            Lazy Power Series Ring over Rational Field
            sage: R([1]).coefficients(4)
            [1, 1, 1, 1]
            sage: R([1]).counts(4)
            [1, 1, 1, 1]

        TESTS::

            sage: TestSuite(R).run()
        """
        LazyPowerSeriesRing.__init__(self, R, element_class=OrdinaryGeneratingSeries)

# Backward-compatibility
OrdinaryGeneratingSeriesRing_class = OrdinaryGeneratingSeriesRing


class OrdinaryGeneratingSeries(LazyPowerSeries):
    def count(self, n):
        """
        Return the number of structures on a set of size n.

        EXAMPLES::

            sage: from sage.combinat.species.generating_series import OrdinaryGeneratingSeriesRing
            sage: R = OrdinaryGeneratingSeriesRing(QQ)
            sage: f = R(range(20))
            sage: f.count(10)
            10
        """
        return self.coefficient(n)

    def counts(self, n):
        """
        Return the number of structures on a set for size i for i in
        range(n).

        EXAMPLES::

            sage: from sage.combinat.species.generating_series import OrdinaryGeneratingSeriesRing
            sage: R = OrdinaryGeneratingSeriesRing(QQ)
            sage: f = R(range(20))
            sage: f.counts(10)
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        """
        return [self.count(i) for i in range(n)]


class ExponentialGeneratingSeriesRing(LazyPowerSeriesRing):
    def __init__(self, R):
        """
        Return the ring of ordinary generating series. Note that is is
        just a LazyPowerSeriesRing whose elements have some extra methods.

        EXAMPLES::

            sage: from sage.combinat.species.generating_series import ExponentialGeneratingSeriesRing
            sage: R = ExponentialGeneratingSeriesRing(QQ); R
            Lazy Power Series Ring over Rational Field
            sage: R([1]).coefficients(4)
            [1, 1, 1, 1]
            sage: R([1]).counts(4)
            [1, 1, 2, 6]

        TESTS::

            sage: TestSuite(R).run()
        """
        LazyPowerSeriesRing.__init__(self, R, element_class=ExponentialGeneratingSeries)

# Backward compatibility
ExponentialGeneratingSeriesRing_class = ExponentialGeneratingSeriesRing

class ExponentialGeneratingSeries(LazyPowerSeries):
    def count(self, n):
        """
        Return the number of structures of size n.

        EXAMPLES::

            sage: from sage.combinat.species.generating_series import ExponentialGeneratingSeriesRing
            sage: R = ExponentialGeneratingSeriesRing(QQ)
            sage: f = R([1])
            sage: [f.count(i) for i in range(7)]
            [1, 1, 2, 6, 24, 120, 720]
        """
        return factorial_stream[n] * self.coefficient(n)

    def counts(self, n):
        """
        Return the number of structures on a set for size i for i in
        range(n).

        EXAMPLES::

            sage: from sage.combinat.species.generating_series import ExponentialGeneratingSeriesRing
            sage: R = ExponentialGeneratingSeriesRing(QQ)
            sage: f = R(range(20))
            sage: f.counts(5)
            [0, 1, 4, 18, 96]
        """
        return [self.count(i) for i in range(n)]


    class FunctorialCompositionStream(SeriesStream):
        def __init__(self, outer_series, inner_series, **kwds):
            """
            A class for the stream of coefficients of the functorial
            composition of two exponential generating series.

            EXAMPLES::

                sage: E = species.SetSpecies()
                sage: E2 = E.restricted(min=2, max=3)
                sage: WP = species.SubsetSpecies()
                sage: P2 = E2*E
                sage: g1 = WP.generating_series()
                sage: g2 = P2.generating_series()
                sage: s = g1.FunctorialCompositionStream(g1, g2, base_ring=g1.base_ring())
                sage: [s[i] for i in range(10)]
                [1, 1, 1, 4/3, 8/3, 128/15, 2048/45, 131072/315, 2097152/315, 536870912/2835]
            """
            self._outer = outer_series
            self._inner = inner_series
            super(ExponentialGeneratingSeries.FunctorialCompositionStream, self).__init__(**kwds)

        def compute(self, n):
            """
            Computes the $n^{th}$ coefficient of this functorial
            composition series.

            EXAMPLES::

                sage: E = species.SetSpecies()
                sage: E2 = E.restricted(min=2, max=3)
                sage: WP = species.SubsetSpecies()
                sage: P2 = E2*E
                sage: g1 = WP.generating_series()
                sage: g2 = P2.generating_series()
                sage: g = g1.functorial_composition(g2)
                sage: [g._stream.compute(i) for i in range(10)]
                [1, 1, 1, 4/3, 8/3, 128/15, 2048/45, 131072/315, 2097152/315, 536870912/2835]
            """
            return self._outer.count(self._inner.count(n)) / factorial_stream[n]

    def functorial_composition(self, y):
        r"""
        Return the exponential generating series which is the functorial
        composition of self with y.

        If `f = \sum_{n=0}^{\infty} f_n \frac{x^n}{n!}` and
        `g = \sum_{n=0}^{\infty} f_n \frac{x^n}{n!}`, then
        functorial composition `f \Box g` is defined as

        .. math::

             f \Box g = \sum_{n=0}^{\infty} f_{g_n} \frac{x^n}{n!}

        REFERENCES:

        - Section 2.2 of [BLL]_.

        EXAMPLES::

            sage: G = species.SimpleGraphSpecies()
            sage: g = G.generating_series()  # indirect doctest
            sage: g._stream
            <class 'sage.combinat.species.generating_series.FunctorialCompositionStream'>
            sage: g.coefficients(10)
            [1, 1, 1, 4/3, 8/3, 128/15, 2048/45, 131072/315, 2097152/315, 536870912/2835]
        """
        return self._new(self.FunctorialCompositionStream, self, y)


def factorial_gen():
    """
    A generator for the factorials starting at 0.

    EXAMPLES::

        sage: from sage.combinat.species.generating_series import factorial_gen
        sage: g = factorial_gen()
        sage: [g.next() for i in range(5)]
        [1, 1, 2, 6, 24]
    """
    z = Integer(1)
    yield z
    yield z
    n = Integer(2)
    while True:
        z *= n
        yield z
        n += 1

factorial_stream = SeriesStreamFromIterator(iterator=factorial_gen(), base_ring=ZZ)


class CycleIndexSeriesRing(LazyPowerSeriesRing):
    def __init__(self, R):
        """
        Return the ring of cycle index series. Note that is is just a
        LazyPowerSeriesRing whose elements have some extra methods.

        EXAMPLES::

            sage: from sage.combinat.species.generating_series import CycleIndexSeriesRing
            sage: R = CycleIndexSeriesRing(QQ); R
            Cycle Index Series Ring over Symmetric Functions over Rational Field in the powersum basis
            sage: R([1]).coefficients(4)
            [p[], p[], p[], p[]]

        TESTS::


            sage: TestSuite(R).run()
        """
        R = SymmetricFunctions(R).power()
        LazyPowerSeriesRing.__init__(self, R, element_class=CycleIndexSeries)

    def _repr_(self):
        """
        EXAMPLES::

            sage: from sage.combinat.species.generating_series import CycleIndexSeriesRing
            sage: CycleIndexSeriesRing(QQ)
            Cycle Index Series Ring over Symmetric Functions over Rational Field in the powersum basis
        """
        return "Cycle Index Series Ring over %s"%self.base_ring()

# Backward compatibility
CycleIndexSeriesRing_class = CycleIndexSeriesRing

class CycleIndexSeries(LazyPowerSeries):
    def count(self, t):
        """
        Return the number of structures corresponding to a certain cycle
        type.

        EXAMPLES::

            sage: from sage.combinat.species.generating_series import CycleIndexSeriesRing
            sage: p = SymmetricFunctions(QQ).power()
            sage: CIS = CycleIndexSeriesRing(QQ)
            sage: f = CIS([0, p([1]), 2*p([1,1]),3*p([2,1])])
            sage: f.count([1])
            1
            sage: f.count([1,1])
            4
            sage: f.count([2,1])
            6
        """
        t = Partition(t)
        return t.aut() * self.coefficient_cycle_type(t)

    def coefficient_cycle_type(self, t):
        """
        Return the coefficient of a cycle type t.

        EXAMPLES::

            sage: from sage.combinat.species.generating_series import CycleIndexSeriesRing
            sage: p = SymmetricFunctions(QQ).power()
            sage: CIS = CycleIndexSeriesRing(QQ)
            sage: f = CIS([0, p([1]), 2*p([1,1]),3*p([2,1])])
            sage: f.coefficient_cycle_type([1])
            1
            sage: f.coefficient_cycle_type([1,1])
            2
            sage: f.coefficient_cycle_type([2,1])
            3
        """
        t = Partition(t)
        p = self.coefficient(t.size())
        return p.coefficient(t)


    class StretchStream(SeriesStream):
        def __init__(self, stream, k, **kwds):
            """
            A class for the coefficients of a "stretched" cycle index
            series. See
            :meth:`sage.combinat.species.generating_series.CycleIndexSeries.stretch`
            for a definition.

            EXAMPLES::

                sage: from sage.combinat.species.generating_series import CycleIndexSeriesRing
                sage: p = SymmetricFunctions(QQ).power()
                sage: CIS = CycleIndexSeriesRing(QQ)
                sage: f = CIS([0, p([1]), 2*p([1,1]),3*p([2,1]), 0])
                sage: s = f.StretchStream(f._stream, 2, base_ring=f.base_ring())
                sage: [s[i] for i in range(10)]
                [0, 0, p[2], 0, 2*p[2, 2], 0, 3*p[4, 2], 0, 0, 0]
            """
            self._stream = stream
            self._k = k
            super(CycleIndexSeries.StretchStream, self).__init__(children=[stream], **kwds)

        def order_operation(self, a):
            """
            The order of a :class:`CycleIndexSeries.StretchStream` is
            ``self._k`` times the order of the underlying stream.

            EXAMPLES::

                sage: from sage.combinat.species.generating_series import CycleIndexSeriesRing
                sage: p = SymmetricFunctions(QQ).power()
                sage: CIS = CycleIndexSeriesRing(QQ)
                sage: f = CIS([0, p([1])])
                sage: g = f.stretch(2)
                sage: f.get_order()
                1
                sage: s = g._stream
                sage: s.order_operation(f.get_order())
                2
            """
            return a * self._k

        def compute(self, n):
            """
            Computes the $n^{th}$ coefficient of the stretched stream.
            
            EXAMPLES::

                sage: from sage.combinat.species.generating_series import CycleIndexSeriesRing
                sage: p = SymmetricFunctions(QQ).power()
                sage: CIS = CycleIndexSeriesRing(QQ)
                sage: f = CIS([p([1])])
                sage: g = f.stretch(2)
                sage: [g._stream.compute(i) for i in range(10)]
                [p[2], 0, p[2], 0, p[2], 0, p[2], 0, p[2], 0]
            """
            quo, rem = Integer(n).quo_rem(self._k)
            if rem == 0:
                return self._stream[quo].map_support(self.stretch_partition)
            else:
                return self._zero

        def stretch_partition(self, p):
            """
            Return the partition ``p`` "stretched" by ``self._k``;
            that is, each component of ``p`` is scaled by ``self._k``.

            EXAMPLES::

                sage: from sage.combinat.species.generating_series import CycleIndexSeriesRing
                sage: p = SymmetricFunctions(QQ).power()
                sage: CIS = CycleIndexSeriesRing(QQ)
                sage: f = CIS([p([1])])
                sage: g = f.stretch(2)
                sage: s = g._stream; s
                <class 'sage.combinat.species.generating_series.StretchStream'>
                sage: s.stretch_partition([3,2,1])
                [6, 4, 2]
            """
            return Partition([self._k*i for i in p])

    def stretch(self, k):
        r"""
        Return the stretch of a cycle index series by a positive integer
        `k`.

        If

        .. math::

           f = \sum_{n=0}^{\infty} f_n(x_1, x_2, \ldots, x_n),

        then the stretch `g` of `f` by `k` is

        .. math::

           g = \sum_{n=0}^{\infty} f_n(x_k, x_{2k}, \ldots, x_{nk}).

        EXAMPLES::

            sage: from sage.combinat.species.generating_series import CycleIndexSeriesRing
            sage: p = SymmetricFunctions(QQ).power()
            sage: CIS = CycleIndexSeriesRing(QQ)
            sage: f = CIS([p([1])])
            sage: f.stretch(3).coefficients(10)
            [p[3], 0, 0, p[3], 0, 0, p[3], 0, 0, p[3]]
        """
        if k == 1:
            return self
        else:
            return self._new(self.StretchStream, self._stream, k)

    class IsotypeGeneratingSeriesStream(SeriesStream):
        def __init__(self, stream, **kwds):
            """
            A class for the coefficients of the isotype generating
            series given the corresponding cycle index series.

            EXAMPLES::

                sage: P = species.PermutationSpecies()
                sage: cis = P.cycle_index_series()
                sage: g = cis.IsotypeGeneratingSeriesStream(cis._stream, base_ring=cis.base_ring().base_ring())
                sage: [g[i] for i in range(5)]
                [1, 1, 2, 3, 5]
                sage: itgs = cis.isotype_generating_series()
                sage: [itgs[i] for i in range(5)]
                [1, 1, 2, 3, 5]
            """
            self._stream = stream
            super(CycleIndexSeries.IsotypeGeneratingSeriesStream, self).__init__(children=[stream],
                                                                                 **kwds)

        def order_operation(self, a):
            """
            Return the order of this stream which is the same as the
            cycle index series stream.

            EXAMPLES::

                sage: P = species.PermutationSpecies()
                sage: cis = P.cycle_index_series()
                sage: g = cis.isotype_generating_series()
                sage: g.coefficients(4)
                [1, 1, 2, 3]
                sage: s = g._stream; s
                <class 'sage.combinat.species.generating_series.IsotypeGeneratingSeriesStream'>
                sage: s.order_operation(cis.get_order())
                0
            """
            return a

        def compute(self, n):
            """
            Return a generator for the coefficients of the ordinary generating
            series obtained from a cycle index series.

            EXAMPLES::

                sage: P = species.PermutationSpecies()
                sage: cis = P.cycle_index_series()
                sage: g = cis.isotype_generating_series()
                sage: [g._stream.compute(i) for i in range(10)]
                [1, 1, 2, 3, 5, 7, 11, 15, 22, 30]
            """
            return sum(self._stream[n].coefficients(), self._zero)

    def isotype_generating_series(self):
        """
        EXAMPLES::

            sage: P = species.PermutationSpecies()
            sage: cis = P.cycle_index_series()
            sage: f = cis.isotype_generating_series()
            sage: f.coefficients(10)
            [1, 1, 2, 3, 5, 7, 11, 15, 22, 30]
        """
        R = self.base_ring().base_ring()
        OGS = OrdinaryGeneratingSeriesRing(R)()
        return OGS._new(self.IsotypeGeneratingSeriesStream, self._stream)

    def expand_as_sf(self, n, alphabet='x'):
        """
        Return the expansion of a cycle index series as a symmetric function in
        ``n`` variables.

        Specifically, this returns a :class:`~sage.combinat.species.series.LazyPowerSeries` whose
        ith term is obtained by calling :meth:`~sage.combinat.sf.sfa.SymmetricFunctionAlgebra_generic_Element.expand`
        on the ith term of ``self``.

        This relies on the (standard) interpretation of a cycle index series as a symmetric function
        in the power sum basis.

        INPUT:

        - ``self`` -- a cycle index series

        - ``n`` -- a positive integer

        - ``alphabet`` -- a variable for the expansion (default: `x`)

        EXAMPLES::

            sage: from sage.combinat.species.set_species import SetSpecies
            sage: SetSpecies().cycle_index_series().expand_as_sf(2).coefficients(4)
            [1, x0 + x1, x0^2 + x0*x1 + x1^2, x0^3 + x0^2*x1 + x0*x1^2 + x1^3]

        """
        expanded_poly_ring = self.coefficient(0).expand(n, alphabet).parent()
        LPSR = LazyPowerSeriesRing(expanded_poly_ring)

        expander_gen = (LPSR.term(self.coefficient(i).expand(n, alphabet), i) for i in NN)

        return LPSR.sum_generator(expander_gen)

    class GeneratingSeriesStream(SeriesStream):
        def __init__(self, cis_stream, **kwds):
            """
            A stream for the generating series of a species derived
            from the cycle index series.

            EXAMPLES::

                sage: P = species.PermutationSpecies()
                sage: cis = P.cycle_index_series()
                sage: g = cis.generating_series()
                sage: s = g._stream; s
                <class 'sage.combinat.species.generating_series.GeneratingSeriesStream'>
                sage: s._stream is cis._stream
                True
            """
            self._stream = cis_stream
            super(CycleIndexSeries.GeneratingSeriesStream, self).__init__(children=[cis_stream], **kwds)

        def order_operation(self, a):
            """
            Return the order of this stream which is the same as the
            cycle index series stream.

            EXAMPLES::

                sage: P = species.PermutationSpecies()
                sage: cis = P.cycle_index_series()
                sage: g = cis.generating_series()
                sage: g.coefficients(4)
                [1, 1, 1, 1]
                sage: s = g._stream; s
                <class 'sage.combinat.species.generating_series.GeneratingSeriesStream'>
                sage: s.order_operation(cis.get_order())
                0
            """
            return a

        def compute(self, n):
            """
            Return a generator for the coefficients of the exponential
            generating series obtained from a cycle index series.

            EXAMPLES::

                sage: P = species.PermutationSpecies()
                sage: cis = P.cycle_index_series()
                sage: g = cis.generating_series()
                sage: [g._stream.compute(i) for i in range(10)]
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
            """
            return self._stream[n].coefficient([1]*n)
        
    def generating_series(self):
        """
        EXAMPLES::

            sage: P = species.PartitionSpecies()
            sage: cis = P.cycle_index_series()
            sage: f = cis.generating_series()
            sage: f.coefficients(5)
            [1, 1, 1, 5/6, 5/8]
        """
        R = self.base_ring().base_ring()
        EGS = ExponentialGeneratingSeriesRing(R)()
        return EGS._new(self.GeneratingSeriesStream, self._stream)

    def __invert__(self):
        """
        Return the multiplicative inverse of self.

        This algorithm is derived from [BLL]_.

        EXAMPLES::

            sage: E = species.SetSpecies().cycle_index_series()
            sage: E.__invert__().coefficients(4)
            [p[], -p[1], 1/2*p[1, 1] - 1/2*p[2], -1/6*p[1, 1, 1] + 1/2*p[2, 1] - 1/3*p[3]]

        The defining characteristic of the multiplicative inverse `F^{-1}` of a cycle index series `F`
        is that `F \cdot F^{-1} = F^{-1} \cdot F = 1` (that is, both products with `F` yield the multiplicative identity `1`)::

            sage: E = species.SetSpecies().cycle_index_series()
            sage: (E * ~E).coefficients(6)
            [p[], 0, 0, 0, 0, 0]

        REFERENCES:

        .. [BLL] F. Bergeron, G. Labelle, and P. Leroux. "Combinatorial species and tree-like structures". Encyclopedia of Mathematics and its Applications, vol. 67, Cambridge Univ. Press. 1998.

        AUTHORS:

        - Andrew Gainer-Dewar
        """
        if self.coefficient(0) == 0:
            raise ValueError("Constant term must be non-zero")

        def multinv_builder(i):
            return self.coefficient(0)**(-i-1) * (self.coefficient(0) + (-1)*self)**i

        return self.parent().sum_generator(multinv_builder(i) for i in NN)

    @coerce_binop
    def __div__(self, y):
        """
        Division between two cycle index series.
        
        TESTS::

            sage: E = species.SetSpecies().cycle_index_series()
            sage: (E / E).coefficients(6)
            [p[], 0, 0, 0, 0, 0]
        """
        return self*(~y)

    class FunctorialCompositionStream(SeriesStream):
        def __init__(self, outer_series, inner_series, **kwds):
            """
            A class for the coefficients of a cycle index series of a
            functorial composition between two species.

            EXAMPLES::
            
                sage: E = species.SetSpecies()
                sage: E2 = species.SetSpecies(size=2)
                sage: WP = species.SubsetSpecies()
                sage: P2 = E2*E
                sage: P2_cis = P2.cycle_index_series()
                sage: WP_cis = WP.cycle_index_series()
                sage: s = WP_cis.FunctorialCompositionStream(WP_cis, P2_cis, base_ring=WP_cis.base_ring())
                sage: [s[i] for i in range(4)]
                [p[], p[1], p[1, 1] + p[2], 4/3*p[1, 1, 1] + 2*p[2, 1] + 2/3*p[3]]
                sage: species.SimpleGraphSpecies().cycle_index_series().coefficients(4)
                [p[], p[1], p[1, 1] + p[2], 4/3*p[1, 1, 1] + 2*p[2, 1] + 2/3*p[3]]
            """
            self._outer = outer_series
            self._inner = inner_series
            super(CycleIndexSeries.FunctorialCompositionStream, self).__init__(**kwds)

        def compute(self, n):
            """
            Return s generator for the coefficients of the functorial
            composition of self with g.

            EXAMPLES::

                sage: E = species.SetSpecies()
                sage: E2 = species.SetSpecies(size=2)
                sage: WP = species.SubsetSpecies()
                sage: P2 = E2*E
                sage: P2_cis = P2.cycle_index_series()
                sage: WP_cis = WP.cycle_index_series()
                sage: g = WP_cis.functorial_composition(P2_cis)
                sage: [g._stream.compute(i) for i in range(5)]
                [p[],
                 p[1],
                 p[1, 1] + p[2],
                 4/3*p[1, 1, 1] + 2*p[2, 1] + 2/3*p[3],
                 8/3*p[1, 1, 1, 1] + 4*p[2, 1, 1] + 2*p[2, 2] + 4/3*p[3, 1] + p[4]]
            """
            res = self._zero
            for s in Partitions(n):
                t = self._inner._cycle_type(s)
                q = self._outer.count(t) / s.aut()
                res += q*self._base_ring(s)
            return res
        
    def functorial_composition(self, g):
        r"""
        Return the functorial composition of self and g.

        If `F` and `G` are species, their functorial composition is the species
        `F \Box G` obtained by setting `(F \Box G) [A] = F[ G[A] ]`.
        
        In other words, an `(F \Box G)`-structure on a set `A` of labels is an
        `F`-structure whose labels are the set of all `G`-structures on `A`.

        It can be shown (as in section 2.2 of [BLL]_) that there is a
        corresponding operation on cycle indices:

        .. math::

            Z_{F} \Box Z_{G} = \sum_{n \geq 0} \frac{1}{n!} \sum_{\sigma \in \mathfrak{S}_{n}} \operatorname{fix} F[ (G[\sigma])_{1}, (G[\sigma])_{2}, \dots ] \, p_{1}^{\sigma_{1}} p_{2}^{\sigma_{2}} \dots.

        This method implements that operation on cycle index series.

        EXAMPLES:

        The species `G` of simple graphs can be expressed in terms of a functorial
        composition: `G = \mathfrak{p} \Box \mathfrak{p}_{2}`, where
        `\mathfrak{p}` is the :class:`~sage.combinat.species.subset_species.SubsetSpecies`.
        This is how it is implemented in :meth:`~sage.combinat.species.library.SimpleGraphSpecies`::

            sage: S = species.SimpleGraphSpecies()
            sage: cis = S.cycle_index_series()  # indirect doctest
            sage: cis._stream
            <class 'sage.combinat.species.generating_series.FunctorialCompositionStream'>
            sage: cis.coefficients(5)
            [p[],
             p[1],
             p[1, 1] + p[2],
             4/3*p[1, 1, 1] + 2*p[2, 1] + 2/3*p[3],
             8/3*p[1, 1, 1, 1] + 4*p[2, 1, 1] + 2*p[2, 2] + 4/3*p[3, 1] + p[4]]
        """
        return self._new(self.FunctorialCompositionStream, self, g)

    def arithmetic_product(self, g, check_input = True):
        """
        Return the arithmetic product of ``self`` with ``g``.

        For species `M` and `N` such that `M[\\varnothing] = N[\\varnothing] = \\varnothing`,
        their arithmetic product is the species `M \\boxdot N` of "`M`-assemblies of cloned `N`-structures".
        This operation is defined and several examples are given in [MM]_.

        The cycle index series for `M \\boxdot N` can be computed in terms of the component series `Z_M` and `Z_N`,
        as implemented in this method.

        INPUT:

        - ``g`` -- a cycle index series having the same parent as ``self``.

        - ``check_input`` -- (default: ``True``) a Boolean which, when set
          to ``False``, will cause input checks to be skipped.

        OUTPUT:

        The arithmetic product of ``self`` with ``g``. This is a cycle
        index series defined in terms of ``self`` and ``g`` such that
        if ``self`` and ``g`` are the cycle index series of two species
        `M` and `N`, their arithmetic product is the cycle index series
        of the species `M \\boxdot N`.

        EXAMPLES:

        For `C` the species of (oriented) cycles and `L_{+}` the species of nonempty linear orders, `C \\boxdot L_{+}` corresponds
        to the species of "regular octopuses"; a `(C \\boxdot L_{+})`-structure is a cycle of some length, each of whose elements
        is an ordered list of a length which is consistent for all the lists in the structure. ::

            sage: C = species.CycleSpecies().cycle_index_series()
            sage: Lplus = species.LinearOrderSpecies(min=1).cycle_index_series()
            sage: RegularOctopuses = C.arithmetic_product(Lplus)
            sage: RegOctSpeciesSeq = RegularOctopuses.generating_series().counts(8)
            sage: RegOctSpeciesSeq
            [0, 1, 3, 8, 42, 144, 1440, 5760]

        It is shown in [MM]_ that the exponential generating function for regular octopuses satisfies
        `(C \\boxdot L_{+}) (x) = \\sum_{n \geq 1} \\sigma (n) (n - 1)! \\frac{x^{n}}{n!}` (where `\\sigma (n)` is
        the sum of the divisors of `n`). ::

            sage: RegOctDirectSeq = [0] + [sum(divisors(i))*factorial(i-1) for i in range(1,8)]
            sage: RegOctDirectSeq == RegOctSpeciesSeq
            True

        AUTHORS:

        - Andrew Gainer-Dewar (2013)

        REFERENCES:

        .. [MM] M. Maia and M. Mendez. "On the arithmetic product of combinatorial species".
           Discrete Mathematics, vol. 308, issue 23, 2008, pp. 5407-5427.
           :arXiv:`math/0503436v2`.

        """
        from itertools import product, repeat, chain

        p = self.base_ring()

        if check_input:
            assert self.coefficient(0) == p.zero()
            assert g.coefficient(0) == p.zero()

        # We first define an operation `\\boxtimes` on partitions as in Lemma 2.1 of [MM]_.
        def arith_prod_of_partitions(l1, l2):
            # Given two partitions `l_1` and `l_2`, we construct a new partition `l_1 \\boxtimes l_2` by
            # the following procedure: each pair of parts `a \\in l_1` and `b \\in l_2` contributes
            # `\\gcd (a, b)`` parts of size `\\lcm (a, b)` to `l_1 \\boxtimes l_2`. If `l_1` and `l_2`
            # are partitions of integers `n` and `m`, respectively, then `l_1 \\boxtimes l_2` is a
            # partition of `nm`.
            term_iterable = chain.from_iterable( repeat(lcm(pair), times=gcd(pair)) for pair in product(l1, l2) )
            term_list = sorted(term_iterable, reverse=True)
            res = Partition(term_list)
            return res

        # We then extend this to an operation on symmetric functions as per eq. (52) of [MM]_.
        # (Maia and Mendez, in [MM]_, are talking about polynomials instead of symmetric
        # functions, but this boils down to the same: Their x_i corresponds to the i-th power
        # sum symmetric function.)
        def arith_prod_sf(x, y):
            ap_sf_wrapper = lambda l1, l2: p(arith_prod_of_partitions(l1, l2))
            return p._apply_multi_module_morphism(x, y, ap_sf_wrapper)

        # Sage stores cycle index series by degree.
        # Thus, to compute the arithmetic product `Z_M \\boxdot Z_N` it is useful
        # to compute all terms of a given degree `n` at once.
        def arith_prod_coeff(n):
            if n == 0:
                res = p.zero()
            else:
                index_set = ((d, n // d) for d in divisors(n))
                res = sum(arith_prod_sf(self.coefficient(i), g.coefficient(j)) for i,j in index_set)

            # Build a list which has res in the `n`th slot and 0's before and after
            # to feed to sum_generator
            res_in_seq = [p.zero()]*n + [res, p.zero()]

            return self.parent(res_in_seq)

        # Finally, we use the sum_generator method to assemble these results into a single
        # LazyPowerSeries object.
        return self.parent().sum_generator(arith_prod_coeff(n) for n in NN)

    def _cycle_type(self, s):
        """
        EXAMPLES::

            sage: cis = species.PartitionSpecies().cycle_index_series()
            sage: [cis._cycle_type(p) for p in Partitions(3)]
            [[3, 1, 1], [2, 1, 1, 1], [1, 1, 1, 1, 1]]
            sage: cis = species.PermutationSpecies().cycle_index_series()
            sage: [cis._cycle_type(p) for p in Partitions(3)]
            [[3, 1, 1, 1], [2, 2, 1, 1], [1, 1, 1, 1, 1, 1]]
            sage: cis = species.SetSpecies().cycle_index_series()
            sage: [cis._cycle_type(p) for p in Partitions(3)]
            [[1], [1], [1]]
        """
        if s == []:
            return self._card(0)
        res = []
        for k in range(1, self._upper_bound_for_longest_cycle(s)+1):
            e = 0
            for d in divisors(k):
                m = moebius(d)
                if m == 0:
                    continue
                u = s.power(k/d)
                e += m*self.count(u)
            res.extend([k]*int(e/k))
        res.reverse()
        return Partition(res)


    def _upper_bound_for_longest_cycle(self, s):
        """
        EXAMPLES::

            sage: cis = species.PartitionSpecies().cycle_index_series()
            sage: cis._upper_bound_for_longest_cycle([4])
            4
            sage: cis._upper_bound_for_longest_cycle([3,1])
            3
            sage: cis._upper_bound_for_longest_cycle([2,2])
            2
            sage: cis._upper_bound_for_longest_cycle([2,1,1])
            2
            sage: cis._upper_bound_for_longest_cycle([1,1,1,1])
            1
        """
        if s == []:
            return 1
        return min(self._card(sum(s)), lcm(list(s)))

    def _card(self, n):
        """
        Return the number of structures on an underlying set of size n for
        the species associated with self. This is just n! times the
        coefficient of p[1]n in self.

        EXAMPLES::

            sage: cis = species.PartitionSpecies().cycle_index_series()
            sage: cis._card(4)
            15
        """
        p = self.coefficient(n)
        return factorial_stream[n]*p.coefficient([1]*n)


    class CompositionStream(LazyPowerSeries.CompositionStream):
        def __init__(self, *args ,**kwds):
            """
            A class for the coefficients of the composition of two
            cycle index series.

            EXAMPLES::

                sage: E = species.SetSpecies(); C = species.CycleSpecies()
                sage: E_cis = E.cycle_index_series()
                sage: g = E_cis(C.cycle_index_series())
                sage: [g[i] for i in range(4)]
                [p[], p[1], p[1, 1] + p[2], p[1, 1, 1] + p[2, 1] + p[3]]
            """
            super(CycleIndexSeries.CompositionStream, self).__init__(*args, **kwds)
            self._y_powers = PowerStream(self._inner)

        def tail_stream(self):
            """
            Return a stream whose tail is equal to the tail of this
            composition stream.

            EXAMPLES::
            
                sage: E = species.SetSpecies(); C = species.CycleSpecies()
                sage: E_cis = E.cycle_index_series()
                sage: g = E_cis(C.cycle_index_series())
                sage: s = g._stream; s
                <class 'sage.combinat.species.generating_series.CompositionStream'>
                sage: g.coefficients(4)
                [p[], p[1], p[1, 1] + p[2], p[1, 1, 1] + p[2, 1] + p[3]]
                sage: res = s.tail_stream()
                sage: [res[i] for i in range(1, 4)]
                [p[1], p[1, 1] + p[2], p[1, 1, 1] + p[2, 1] + p[3]]
            """
            g = (self._compose_term(self._outer[i], self._y_powers)
                 for i in NN)
            res = SumGeneratorStream(g, base_ring=self._base_ring)
            return res

        def _compose_term(self, p, y_powers):
            """
            Return the composition of one term in the outer series
            with the inner series.

            INPUT:

            -  ``p`` - a term in self

            -  ``y_powers`` - a stream for the powers of y
               starting with y

            EXAMPLES::

                sage: E = species.SetSpecies(); C = species.CycleSpecies()
                sage: E_cis = E.cycle_index_series()
                sage: C_cis = C.cycle_index_series()
                sage: S = E_cis(C_cis)
                sage: p2 = E_cis.coefficient(2); p2
                1/2*p[1, 1] + 1/2*p[2]
                sage: t = S._stream._compose_term(p2, S._stream._y_powers)
                sage: [t[i] for i in range(4)]
                [0, 0, 1/2*p[1, 1] + 1/2*p[2], 1/2*p[1, 1, 1] + 1/2*p[2, 1]]
            """
            if p == 0:
                return TermStream(n=0, value=self._zero, base_ring=self._base_ring)

            res = []
            #Go through all the partition, coefficient pairs in the term p
            for m, c in p:
                res_t = TermStream(n=0, value=c, base_ring=self._base_ring)
                for e,v in enumerate(m.to_exp()):
                    if v == 0:
                        continue
                    stretched = CycleIndexSeries.StretchStream(y_powers[v-1], e + 1,
                                                               base_ring=self._base_ring)
                    res_t = res_t * stretched
                res.append(res_t)
                
            return ListSumStream(res, base_ring=self._base_ring)

    class WeightedCompositionStream(LazyPowerSeries.CompositionStream):
        def __init__(self, outer, inner, inner_species, **kwds):
            """
            A class for the coefficients of the composition of a
            cycle index series and the cycle index series of the
            weighted species.

            EXAMPLES::

                sage: E = species.SetSpecies(); C = species.CycleSpecies()
                sage: E_cis = E.cycle_index_series()
                sage: g = E_cis.weighted_composition(C)
                sage: [g[i] for i in range(4)]
                [p[], p[1], p[1, 1] + p[2], p[1, 1, 1] + p[2, 1] + p[3]]
            """
            self._inner_species = inner_species
            super(CycleIndexSeries.WeightedCompositionStream, self).__init__(outer, inner, **kwds)

        def tail_stream(self):
            """
            Return a stream whose tail is equal to the tail of this
            composition stream.

            EXAMPLES::

                sage: E = species.SetSpecies(); C = species.CycleSpecies()
                sage: E_cis = E.cycle_index_series()
                sage: g = E_cis.weighted_composition(C)._stream
                sage: [g[i] for i in range(1, 4)]
                [p[1], p[1, 1] + p[2], p[1, 1, 1] + p[2, 1] + p[3]]
                sage: tail = g.tail_stream()
                sage: [tail[i] for i in range(1, 4)]
                [p[1], p[1, 1] + p[2], p[1, 1, 1] + p[2, 1] + p[3]]
            """
            g = (self._weighted_compose_term(self._outer[i], self._inner_species)
                 for i in NN)
            return SumGeneratorStream(g, base_ring=self._base_ring)

        def _weighted_compose_term(self, p, y_species):
            """
            Return the weighted composition of one term in self with y.

            INPUT:

            -  ``p`` - a term in self

            -  ``y_species`` - a species

            EXAMPLES::

                sage: E = species.SetSpecies(); C = species.CycleSpecies()
                sage: E_cis = E.cycle_index_series()
                sage: S = E_cis.weighted_composition(C)
                sage: p2 = E_cis.coefficient(2); p2
                1/2*p[1, 1] + 1/2*p[2]
                sage: t = S._stream._weighted_compose_term(p2, C)
                sage: [t[i] for i in range(4)]
                [0, 0, 1/2*p[1, 1] + 1/2*p[2], 1/2*p[1, 1, 1] + 1/2*p[2, 1]]
            """
            if p == 0:
                return TermStream(n=0, value=self._zero, base_ring=self._base_ring)

            base_ring = self._base_ring.base_ring()

            res = []
            #Go through all the partition, coefficient pairs in the term p
            for m, c in p:
                res_t = TermStream(n=0, value=c, base_ring=self._base_ring)
                for e,v in enumerate(m.to_exp()):
                    if v == 0:
                        continue
                    series = (y_species.weighted(y_species._weight**(e+1)).cycle_index_series(base_ring)**v).stretch(e+1)
                    res_t = res_t * series._stream
                res.append(res_t)

            return ListSumStream(res, base_ring=self._base_ring)
        
    def weighted_composition(self, y_species):
        """
        Return the composition of this cycle index series with the cycle
        index series of y_species where y_species is a weighted species.

        Note that this is basically the same algorithm as composition
        except we can not use the optimization that the powering of cycle
        index series commutes with 'stretching'.

        EXAMPLES::

            sage: E = species.SetSpecies(); C = species.CycleSpecies()
            sage: E_cis = E.cycle_index_series()
            sage: E_cis.weighted_composition(C).coefficients(4)
            [p[], p[1], p[1, 1] + p[2], p[1, 1, 1] + p[2, 1] + p[3]]
            sage: E(C).cycle_index_series().coefficients(4)
            [p[], p[1], p[1, 1] + p[2], p[1, 1, 1] + p[2, 1] + p[3]]
        """
        base_ring = self.base_ring()
        y = y_species.cycle_index_series(base_ring)
        assert y.coefficient(0) == 0
        return self._new(self.WeightedCompositionStream, self._stream, y._stream, y_species)

    def _weighted_compose_gen(self, y_species, ao):
        """
        Return an iterator for the composition of this cycle index series
        and the cycle index series of the weighted species y_species.

        EXAMPLES::

            sage: E = species.SetSpecies(); C = species.CycleSpecies()
            sage: E_cis = E.cycle_index_series()
            sage: g = E_cis._weighted_compose_gen(C,0)
            sage: [g.next() for i in range(4)]
            [p[], p[1], p[1, 1] + p[2], p[1, 1, 1] + p[2, 1] + p[3]]
        """
        parent = self.parent()
        res =  parent.sum_generator(self._weighted_compose_term(self.coefficient(i), y_species)
                                    for i in _integers_from(0))

        for i in _integers_from(0):
            yield res.coefficient(i)

    def _weighted_compose_term(self, p, y_species):
        """
        Return the weighted composition of one term in self with y.

        INPUT:

        -  ``p`` - a term in self

        -  ``y_species`` - a species

        EXAMPLES::

            sage: E = species.SetSpecies(); C = species.CycleSpecies()
            sage: E_cis = E.cycle_index_series()
            sage: p2 = E_cis.coefficient(2); p2
            1/2*p[1, 1] + 1/2*p[2]
            sage: E_cis._weighted_compose_term(p2, C).coefficients(4)
            [0, 0, 1/2*p[1, 1] + 1/2*p[2], 1/2*p[1, 1, 1] + 1/2*p[2, 1]]
        """
        parent = self.parent()
        if p == 0:
            return parent(0)

        base_ring = self.base_ring().base_ring()

        res = []
        #Go through all the partition, coefficient pairs in the term p
        for m, c in p:
            res_t = parent.term(c, 0)

            for e,v in enumerate(m.to_exp()):
                if v == 0:
                    continue
                res_t = res_t * (y_species.weighted(y_species._weight**(e+1)).cycle_index_series(base_ring)**v).stretch(e+1)
            res.append(res_t)

        return parent.sum(res)

    def compositional_inverse(self):
        r"""
        Return the compositional inverse of ``self`` if possible.

        (Specifically, if ``self`` is of the form `0 + p_{1} + \dots`.)

        The compositional inverse is the inverse with respect to
        plethystic substitution. This is the operation on cycle index
        series which corresponds to substitution, a.k.a. partitional
        composition, on the level of species. See Section 2.2 of
        [BLL]_ for a definition of this operation.

        EXAMPLES::

            sage: Eplus = species.SetSpecies(min=1).cycle_index_series()
            sage: Eplus(Eplus.compositional_inverse()).coefficients(8)
            [0, p[1], 0, 0, 0, 0, 0, 0]

        TESTS::

            sage: Eplus = species.SetSpecies(min=2).cycle_index_series()
            sage: Eplus.compositional_inverse()
            Traceback (most recent call last):
            ...
            ValueError: not an invertible series

        ALGORITHM:

        Let `F` be a species satisfying `F = 0 + X + F_2 + F_3 + \dots` for `X` the species of singletons.
        (Equivalently, `\lvert F[\varnothing] \rvert = 0` and `\lvert F[\{1\}] \rvert = 1`.)
        Then there exists a (virtual) species `G` satisfying `F \circ G = G \circ F = X`.

        It follows that `(F - X) \circ G = F \circ G - X \circ G = X - G`.
        Rearranging, we obtain the recursive equation `G = X - (F - X) \circ G`, which can be
        solved using iterative methods.
        
        .. WARNING::
        
            This algorithm is functional but can be very slow.
            Use with caution!

        .. SEEALSO::
        
            The compositional inverse `\Omega` of the species `E_{+}`
            of nonempty sets can be handled much more efficiently
            using specialized methods. These are implemented in
            :class:`~sage.combinat.species.combinatorial_logarithm.CombinatorialLogarithmSeries`.

        AUTHORS:

        - Andrew Gainer-Dewar
        """
        cisr = self.parent()
        sfa = cisr._base

        X = cisr([0, sfa([1]), 0])

        if self.coefficients(2) != X.coefficients(2):
            raise ValueError('not an invertible series')

        res = cisr()
        res.define(X - (self - X).compose(res))

        return res

