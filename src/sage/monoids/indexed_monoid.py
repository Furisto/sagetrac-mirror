"""
Indexed Monoids

AUTHORS:

- Travis Scrimshaw (2013-10-15)
"""

#*****************************************************************************
#  Copyright (C) 2013 Travis Scrimshaw <tscrim at ucdavis.edu>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from copy import copy
from sage.misc.abstract_method import abstract_method
from sage.misc.cachefunc import cached_method
from sage.misc.indexed_generators import IndexedGenerators
from sage.structure.parent import Parent
from sage.structure.unique_representation import UniqueRepresentation
from sage.structure.element import MonoidElement

from sage.categories.monoids import Monoids
from sage.categories.poor_man_map import PoorManMap
from sage.rings.integer import Integer
from sage.rings.infinity import infinity
from sage.sets.finite_enumerated_set import FiniteEnumeratedSet
from sage.sets.family import Family

class IndexedMonoidElement(MonoidElement):
    """
    An element of an indexed monoid.
    """
    def __init__(self, F, x):
        """
        Create the element ``x`` of an indexed free abelian monoid ``F``.
        
        EXAMPLES::
        
            sage: F = IndexedFreeAbelianMonoid(ZZ)
            sage: F(1)
            1
            sage: a,b,c,d,e = [F.gen(i) for i in range(5)]
            sage: x = a^2 * b^3 * a^2 * b^4; x
            F[0]^4*F[1]^7
            sage: TestSuite(x).run()

            sage: F = IndexedFreeMonoid('abcde')
            sage: a,b,c,d,e = F.gens()
            sage: a in F
            True
            sage: a*b in F
            True
            sage: TestSuite(a*d^2*e*c*a).run()
        """
        MonoidElement.__init__(self, F)
        self._monomial = x

    @abstract_method
    def _sorted_items(self):
        """
        Return the items (i.e terms) of ``self``, sorted for printing.

        EXAMPLES::

            sage: F = IndexedFreeMonoid(ZZ)
            sage: a,b,c,d,e = [F.gen(i) for i in range(5)]
            sage: x = a*b^2*e*d
            sage: x._sorted_items()
            ((0, 1), (1, 2), (4, 1), (3, 1))

        .. SEEALSO::

            :meth:`_repr_`, :meth:`_latex_`, :meth:`print_options`
        """
                                        
    def _repr_(self):
        """
        Return a string representation of ``self``.

        EXAMPLES::

            sage: F = IndexedFreeAbelianMonoid(ZZ)
            sage: a,b,c,d,e = [F.gen(i) for i in range(5)]
            sage: a*b^2*e*d
            F[0]*F[1]^2*F[3]*F[4]
        """
        if not self._monomial:
            return '1'

        monomial = self._sorted_items()
        P = self.parent()

        scalar_mult = P._print_options['scalar_mult']

        exp = lambda v: '^{}'.format(v) if v != 1 else ''
        return scalar_mult.join(P._repr_generator(g) + exp(v) for g,v in monomial)

    def _ascii_art_(self):
        r"""
        Return an ASCII art representation of ``self``.

        EXAMPLES::

            sage: F = IndexedFreeAbelianMonoid(ZZ)
            sage: a,b,c,d,e = [F.gen(i) for i in range(5)]
            sage: ascii_art(a*e*d)
            F *F *F
             0  3  4
            sage: ascii_art(a*b^2*e*d)
                2
            F *F *F *F
             0  1  3  4
        """
        from sage.misc.ascii_art import AsciiArt, ascii_art, empty_ascii_art

        if not self._monomial:
            return AsciiArt(["1"])

        monomial = self._sorted_items()
        P = self.parent()
        scalar_mult = P._print_options['scalar_mult']

        if all(x[1] == 1 for x in monomial):
            ascii_art_gen = lambda m: P._ascii_art_generator(m[0])
        else:
            pref = AsciiArt([P.prefix()])
            def ascii_art_gen(m):
                if m[1] != 1:
                    r = (AsciiArt([" "**Integer(len(pref))]) + ascii_art(m[1]))
                else:
                    r = empty_ascii_art
                r = r * P._ascii_art_generator(m[0])
                r._baseline = r._h - 2
                return r
        b = ascii_art_gen(monomial[0])
        for x in monomial[1:]:
            b = b + AsciiArt([scalar_mult]) + ascii_art_gen(x)
        return b

    def _latex_(self):
        r"""
        Return a `\LaTeX` representation of ``self``.

        EXAMPLES::

            sage: F = IndexedFreeAbelianMonoid(ZZ)
            sage: a,b,c,d,e = [F.gen(i) for i in range(5)]
            sage: latex(a*b^2*e*d)
            F_{0} F_{1}^{2} F_{3} F_{4}
        """
        if not self._monomial:
            return '1'

        monomial = self._sorted_items()
        P = self.parent()

        scalar_mult = P._print_options['latex_scalar_mult']
        if scalar_mult is None:
            scalar_mult = P._print_options['scalar_mult']
            if scalar_mult == "*":
                scalar_mult = " "

        exp = lambda v: '^{{{}}}'.format(v) if v != 1 else ''
        return scalar_mult.join(P._latex_generator(g) + exp(v) for g,v in monomial)

    def __iter__(self):
        """
        Iterate over ``self``.

        EXAMPLES::

            sage: F = IndexedFreeMonoid(ZZ)
            sage: a,b,c,d,e = [F.gen(i) for i in range(5)]
            sage: list(b*a*c^3*b)
            [(F[1], 1), (F[0], 1), (F[2], 3), (F[1], 1)]

        ::

            sage: F = IndexedFreeAbelianMonoid(ZZ)
            sage: a,b,c,d,e = [F.gen(i) for i in range(5)]
            sage: list(b*c^3*a)
            [(F[0], 1), (F[1], 1), (F[2], 3)]
        """
        return ((self.parent().gen(index), exp) for (index,exp) in self._sorted_items())

    def __eq__(self, y):
        """
        Check equality.

        EXAMPLES::

            sage: F = IndexedFreeMonoid(ZZ)
            sage: a,b,c,d,e = [F.gen(i) for i in range(5)]
            sage: a == a
            True
            sage: a*e == a*e
            True
            sage: a*b*c^3*b*d == (a*b*c)*(c^2*b*d)
            True

            sage: F = IndexedFreeAbelianMonoid(ZZ)
            sage: a,b,c,d,e = [F.gen(i) for i in range(5)]
            sage: a == a
            True
            sage: a*e == e*a
            True
            sage: a*b*c^3*b*d == a*d*(b^2*c^2)*c
            True
        """
        if not isinstance(y, IndexedMonoidElement):
            return y == 1 and not self._monomial
        return y.parent() is self.parent() and y._monomial == self._monomial

    def __ne__(self, y):
        """
        Check inequality.

        EXAMPLES::

            sage: F = IndexedFreeMonoid(ZZ)
            sage: a,b,c,d,e = [F.gen(i) for i in range(5)]
            sage: a != b
            True
            sage: a*b != b*a
            True
            sage: a*b*c^3*b*d != (a*b*c)*(c^2*b*d)
            False

            sage: F = IndexedFreeAbelianMonoid(ZZ)
            sage: a,b,c,d,e = [F.gen(i) for i in range(5)]
            sage: a != b
            True
            sage: a*b != a*a
            True
            sage: a*b*c^3*b*d != a*d*(b^2*c^2)*c
            False
        """
        return not self.__eq__(y)

    def __len__(self):
        """
        Return the length of ``self``.

        EXAMPLES::

            sage: F = IndexedFreeMonoid(ZZ)
            sage: a,b,c,d,e = [F.gen(i) for i in range(5)]
            sage: elt = a*c^3*b^2*a
            sage: elt.length()
            7
            sage: len(elt)
            7

            sage: F = IndexedFreeAbelianMonoid(ZZ)
            sage: a,b,c,d,e = [F.gen(i) for i in range(5)]
            sage: elt = a*c^3*b^2*a
            sage: elt.length()
            7
            sage: len(elt)
            7
        """
        return sum(exp for gen,exp in self._sorted_items())

    length = __len__

    def support(self):
        """
        Return a list of the objects indexing ``self`` with
        non-zero exponents.

        EXAMPLES::

            sage: F = IndexedFreeMonoid(ZZ)
            sage: a,b,c,d,e = [F.gen(i) for i in range(5)]
            sage: (b*a*c^3*b).support()
            [0, 1, 2]

        ::

            sage: F = IndexedFreeAbelianMonoid(ZZ)
            sage: a,b,c,d,e = [F.gen(i) for i in range(5)]
            sage: (a*c^3).support()
            [0, 2]
        """
        supp = set([key for key, exp in self._sorted_items() if exp != 0])
        return sorted(supp)

    def leading_support(self):
        """
        Return the support of the leading generator of ``self``.

        EXAMPLES::

            sage: F = IndexedFreeMonoid(ZZ)
            sage: a,b,c,d,e = [F.gen(i) for i in range(5)]
            sage: (b*a*c^3*a).leading_support()
            1

        ::

            sage: F = IndexedFreeAbelianMonoid(ZZ)
            sage: a,b,c,d,e = [F.gen(i) for i in range(5)]
            sage: (b*c^3*a).leading_support()
            0
        """
        if not self:
            return None
        return self._sorted_items()[0][0]

    def trailing_support(self):
        """
        Return the support of the trailing generator of ``self``.

        EXAMPLES::

            sage: F = IndexedFreeMonoid(ZZ)
            sage: a,b,c,d,e = [F.gen(i) for i in range(5)]
            sage: (b*a*c^3*a).trailing_support()
            0

        ::

            sage: F = IndexedFreeAbelianMonoid(ZZ)
            sage: a,b,c,d,e = [F.gen(i) for i in range(5)]
            sage: (b*c^3*a).trailing_support()
            2
        """
        if not self:
            return None
        return self._sorted_items()[-1][0]

class IndexedFreeMonoidElement(IndexedMonoidElement):
    """
    An element of an indexed free abelian monoid.
    """
    def _sorted_items(self):
        """
        Returns the items (i.e terms) of ``self``, sorted for printing

        EXAMPLES::

            sage: F = IndexedFreeMonoid(ZZ)
            sage: a,b,c,d,e = [F.gen(i) for i in range(5)]
            sage: x = a*b^2*e*d
            sage: x._sorted_items()
            ((0, 1), (1, 2), (4, 1), (3, 1))
            sage: F.print_options(monomial_cmp = lambda x,y: -cmp(x,y))
            sage: x._sorted_items()
            ((0, 1), (1, 2), (4, 1), (3, 1))
            sage: F.print_options(monomial_cmp=cmp) # reset to original state

        .. SEEALSO::

            :meth:`_repr_`, :meth:`_latex_`, :meth:`print_options`
        """
        return self._monomial

    def _mul_(self, y):
        """
        Multiply ``self`` by ``y``.

        EXAMPLES::

            sage: F = IndexedFreeMonoid(ZZ)
            sage: a,b,c,d,e = [F.gen(i) for i in range(5)]
            sage: a*b^2*e*d
            F[0]*F[1]^2*F[4]*F[3]
            sage: (a*b^2*d^2) * (d^4*b*e)
            F[0]*F[1]^2*F[3]^6*F[1]*F[4]
        """
        if len(self._monomial) == 0:
            return y
        if len(y._monomial) == 0:
            return self

        ret = list(self._monomial)
        rhs = list(y._monomial)
        if ret[-1][0] == rhs[0][0]:
            rhs[0] = (rhs[0][0], rhs[0][1] + ret.pop()[1])
        ret += rhs
        return self.__class__(self.parent(), tuple(ret))

    def __pow__(self, n):
        """
        Raise ``self`` to the power of ``n``.

        EXAMPLES::

            sage: F = IndexedFreeMonoid(ZZ)
            sage: a,b,c,d,e = [F.gen(i) for i in range(5)]
            sage: x = a*b^2*e*d*a; x
            F[0]*F[1]^2*F[4]*F[3]*F[0]
            sage: x^3
            F[0]*F[1]^2*F[4]*F[3]*F[0]^2*F[1]^2*F[4]*F[3]*F[0]^2*F[1]^2*F[4]*F[3]*F[0]
            sage: x^0
            1
        """
        if not isinstance(n, (int, long, Integer)):
            raise TypeError("Argument n (= {}) must be an integer".format(n))
        if n < 0: 
            raise ValueError("Argument n (= {}) must be positive".format(n))
        if n == 1:
            return self
        if n == 0:
            return self.parent().one()
        if len(self._monomial) == 1:
            gen,exp = self._monomial[0]
            return self.__class__(self.parent(), ((gen, exp*n),))
        ret = self
        for i in range(n-1):
            ret *= self
        return ret

class IndexedFreeAbelianMonoidElement(IndexedMonoidElement):
    """
    An element of an indexed free abelian monoid.
    """
    def _sorted_items(self):
        """
        Return the items (i.e syllables) of ``self``, sorted for printing.

        EXAMPLES::

            sage: F = IndexedFreeAbelianMonoid(ZZ)
            sage: a,b,c,d,e = [F.gen(i) for i in range(5)]
            sage: x = a*b^2*e*d
            sage: x._sorted_items()
            [(0, 1), (1, 2), (3, 1), (4, 1)]
            sage: F.print_options(monomial_cmp = lambda x,y: -cmp(x,y))
            sage: x._sorted_items()
            [(4, 1), (3, 1), (1, 2), (0, 1)]
            sage: F.print_options(monomial_cmp=cmp) # reset to original state

        .. SEEALSO::

            :meth:`_repr_`, :meth:`_latex_`, :meth:`print_options`
        """
        print_options = self.parent().print_options()
        v = self._monomial.items()
        try:
            v.sort(cmp = print_options['monomial_cmp'])
        except StandardError: # Sorting the output is a plus, but if we can't, no big deal
            pass
        return v

    def _mul_(self, y):
        """
        Multiply ``self`` by ``y``.

        EXAMPLES::

            sage: F = IndexedFreeAbelianMonoid(ZZ)
            sage: a,b,c,d,e = [F.gen(i) for i in range(5)]
            sage: a*b^2*e*d
            F[0]*F[1]^2*F[3]*F[4]
        """
        ret = copy(self._monomial)
        for k,v in y._monomial.iteritems():
            ret[k] = ret.get(k, 0) + v
        return self.__class__(self.parent(), ret)

    def __pow__(self, n):
        """
        Raise ``self`` to the power of ``n``.

        EXAMPLES::

            sage: F = IndexedFreeAbelianMonoid(ZZ)
            sage: a,b,c,d,e = [F.gen(i) for i in range(5)]
            sage: x = a*b^2*e*d; x
            F[0]*F[1]^2*F[3]*F[4]
            sage: x^3
            F[0]^3*F[1]^6*F[3]^3*F[4]^3
            sage: x^0
            1
        """
        if not isinstance(n, (int, long, Integer)):
            raise TypeError("Argument n (= {}) must be an integer".format(n))
        if n < 0: 
            raise ValueError("Argument n (= {}) must be positive".format(n))
        if n == 1:
            return self
        if n == 0:
            return self.parent().one()
        return self.__class__(self.parent(), {k:v*n for k,v in self._monomial.iteritems()})

    def dict(self):
        """
        Return ``self`` as a dictionary.

        EXAMPLES::
        
            sage: F = IndexedFreeAbelianMonoid(ZZ)
            sage: a,b,c,d,e = [F.gen(i) for i in range(5)]
            sage: (a*c^3).dict()
            {0: 1, 2: 3}
        """
        return copy(self._monomial)

    def cancel(self, elt):
        """
        Cancel the element ``elt`` out of ``self``.

        EXAMPLES::
        
            sage: F = IndexedFreeAbelianMonoid(ZZ)
            sage: a,b,c,d,e = [F.gen(i) for i in range(5)]
            sage: elt = a*b*c^3*d^2; elt
            F[0]*F[1]*F[2]^3*F[3]^2
            sage: elt.cancel(a)
            F[1]*F[2]^3*F[3]^2
            sage: elt.cancel(c)
            F[0]*F[1]*F[2]^2*F[3]^2
            sage: elt.cancel(a*b*d^2)
            F[2]^3
        """
        d = copy(self._monomial)
        for k,v in elt._monomial.iteritems():
            d[k] -= v
        for k,v in d.items():
            if v < 0:
                raise ValueError("invalid cancellation")
            if v == 0:
                del d[k]
        return self.__class__(self.parent(), d)

class IndexedMonoid(Parent, IndexedGenerators, UniqueRepresentation):
    """
    Base class for monoids with an indexed set of generators.

    INPUT:

    - ``indices`` -- the indices for the generators

    For the optional arguments that control the printing, see
    :class:`~sage.misc.indexed_generators.IndexedGenerators`.
    """
    @staticmethod
    def __classcall__(cls, indices, prefix="F", **kwds):
        """
        TESTS::

            sage: F = IndexedFreeAbelianMonoid(['a','b','c'])
            sage: G = IndexedFreeAbelianMonoid(('a','b','c'))
            sage: H = IndexedFreeAbelianMonoid('abc')
            sage: F is G and F is H
            True

            sage: F = IndexedFreeAbelianMonoid(['a','b','c'], latex_bracket=['LEFT', 'RIGHT'])
            sage: F.print_options()['latex_bracket']
            ('LEFT', 'RIGHT')
            sage: F is G
            False
        """
        if isinstance(indices, str):
            indices = FiniteEnumeratedSet(list(indices))
        elif isinstance(indices, (list, tuple)):
            indices = FiniteEnumeratedSet(indices)

        # bracket or latex_bracket might be lists, so convert
        # them to tuples so that they're hashable.
        bracket = kwds.get('bracket', None)
        if isinstance(bracket, list):
            kwds['bracket'] = tuple(bracket)
        latex_bracket = kwds.get('latex_bracket', None)
        if isinstance(latex_bracket, list):
            kwds['latex_bracket'] = tuple(latex_bracket)
        return super(IndexedMonoid, cls).__classcall__(cls, indices, prefix, **kwds)

    def __init__(self, indices, prefix, category=None, **kwds):
        """
        Initialize ``self``.

        EXAMPLES::

            sage: F = IndexedFreeAbelianMonoid(ZZ)
            sage: TestSuite(F).run()
            sage: F = IndexedFreeAbelianMonoid('abcde')
            sage: TestSuite(F).run()
        """
        self._indices = indices
        category = Monoids().or_subcategory(category)
        Parent.__init__(self, category=category)

        # ignore the optional 'key' since it only affects CachedRepresentation
        kwds.pop('key', None)
        IndexedGenerators.__init__(self, indices, prefix, **kwds)

    def _element_constructor_(self, x=None):
        """
        Create an element of this abelian monoid from ``x``.

        EXAMPLES::

            sage: F = IndexedFreeAbelianMonoid(ZZ)
            sage: F(F.gen(2))
            F[2]
            sage: F(-5)
            F[-5]
            sage: F(1)
            1
            sage: F([[1, 3], [-2, 12]])
            F[-2]^12*F[1]^3
        """
        if x is None or x == 1:
            return self.one()
        if isinstance(x, IndexedFreeAbelianMonoidElement) and x.parent() is self:
            return x
        if x in self._indices:
            return self.gens()[x]
        return self.element_class(self, x)

    def _an_element_(self):
        """
        Return an element of ``self``.

        EXAMPLES::

            sage: G = IndexedFreeAbelianMonoid(ZZ)
            sage: G.an_element()
            F[1]
            sage: G = IndexedFreeMonoid('abc')
            sage: G.an_element()
            F['a']*F['b']*F['c']
        """
        if self._indices.cardinality() != infinity:
            return self.prod(self.gens())
        return self.gen(self._indices.an_element())

    def __contains__(self, x):
        r"""
        Return ``True`` if `x` is an element of ``self``.

        EXAMPLES::

            sage: F = IndexedFreeAbelianMonoid(ZZ)
            sage: F.gen(2)*F.gen(3) in F
            True

        Note that a monoid on `\NN` generators is not considered a
        submonoid of one on `\ZZ` generators::

            sage: IndexedFreeAbelianMonoid(NN).gen(2) in F
            False
        """
        return isinstance(x, self.element_class) and x.parent() is self

    def gens(self):
        """
        Return the generators of ``self``.

        EXAMPLES::

            sage: F = IndexedFreeAbelianMonoid(ZZ)
            sage: F.gens()
            Lazy family (Generator map from Integer Ring to
             Free abelian monoid indexed by Integer Ring(i))_{i in Integer Ring}
            sage: F = IndexedFreeAbelianMonoid('abcde')
            sage: F.gens()
            Finite family {'a': F['a'], 'c': F['c'], 'b': F['b'], 'e': F['e'], 'd': F['d']}
        """
        if self._indices.cardinality() == infinity:
            gen = PoorManMap(self.gen, domain=self._indices, codomain=self, name="Generator map")
            return Family(self._indices, gen)
        return Family(self._indices, self.gen)

    def ngens(self):
        """
        The number of free generators of ``self``.

        EXAMPLES::

            sage: F = IndexedFreeAbelianMonoid(ZZ)
            sage: F.ngens()
            +Infinity
            sage: F = IndexedFreeAbelianMonoid('abcde')
            sage: F.ngens()
            5
        """
        return self._indices.cardinality()

class IndexedFreeMonoid(IndexedMonoid):
    """
    Free monoid with an indexed set of generators.

    INPUT:

    - ``indices`` -- the indices for the generators

    For the optional arguments that control the printing, see
    :class:`~sage.misc.indexed_generators.IndexedGenerators`.

    .. NOTE::

        If there is ambiguity with `1`, we construct the identity in
        the monoid instead of the generator::

            sage: F = IndexedFreeMonoid(ZZ)
            sage: F(1)
            1
            sage: F.gen(1)
            F[1]

    EXAMPLES::

        sage: F = IndexedFreeMonoid(ZZ)
        sage: F.gen(15)^3 * F.gen(2) * F.gen(15)
        F[15]^3*F[2]*F[15]

    Now we examine some of the printing options::

        sage: F = IndexedFreeMonoid(ZZ, prefix='X', bracket=['|','>'])
        sage: F.gen(2) * F.gen(12)
        X|2>*X|12>
        sage: F = IndexedFreeAbelianMonoid(Partitions(), prefix='A', bracket=False, scalar_mult='%')
        sage: F.gen([3,1,1]) * F.gen([2,2])
        A[2, 2]%A[3, 1, 1]
    """
    def _repr_(self):
        """
        Return a string representation of ``self``.

        EXAMPLES::

            sage: IndexedFreeMonoid(ZZ)
            Free monoid indexed by Integer Ring
        """
        return "Free monoid indexed by {}".format(self._indices)

    Element = IndexedFreeMonoidElement

    @cached_method
    def one(self):
        """
        Return the identity element of ``self``.

        EXAMPLES::

            sage: F = IndexedFreeMonoid(ZZ)
            sage: F.one()
            1
        """
        return self.element_class(self, ())

    def gen(self, x):
        """
        The generator indexed by ``x`` of ``self``.

        EXAMPLES::

            sage: F = IndexedFreeMonoid(ZZ)
            sage: F.gen(0)
            F[0]
            sage: F.gen(2)
            F[2]
        """
        if x not in self._indices:
            raise IndexError("{} is not in the index set".format(x))
        try:
            return self.element_class(self, ((self._indices(x),1),))
        except TypeError: # Backup (if it is a string)
            return self.element_class(self, ((x,1),))

class IndexedFreeAbelianMonoid(IndexedMonoid):
    """
    Free abelian monoid with an indexed set of generators.

    INPUT:

    - ``indices`` -- the indices for the generators

    For the optional arguments that control the printing, see
    :class:`~sage.misc.indexed_generators.IndexedGenerators`.

    .. NOTE::

        If there is ambiguity with `1`, we construct the identity in
        the monoid instead of the generator::

            sage: F = IndexedFreeAbelianMonoid(ZZ)
            sage: F(1)
            1
            sage: F.gen(1)
            F[1]

    EXAMPLES::

        sage: F = IndexedFreeAbelianMonoid(ZZ)
        sage: F.gen(15)^3 * F.gen(2) * F.gen(15)
        F[2]*F[15]^4

    Now we examine some of the printing options::

        sage: F = IndexedFreeAbelianMonoid(ZZ, prefix='X', bracket=['|','>'])
        sage: F.gen(2) * F.gen(12)
        X|2>*X|12>
        sage: F = IndexedFreeAbelianMonoid(Partitions(), prefix='A', bracket=False, scalar_mult='%')
        sage: F.gen([3,1,1]) * F.gen([2,2])
        A[2, 2]%A[3, 1, 1]
    """
    def _repr_(self):
        """
        Return a string representation of ``self``.

        EXAMPLES::

            sage: IndexedFreeAbelianMonoid(ZZ)
            Free abelian monoid indexed by Integer Ring
        """
        return "Free abelian monoid indexed by {}".format(self._indices)

    def _element_constructor_(self, x=None):
        """
        Create an element of this abelian monoid from ``x``.

        EXAMPLES::

            sage: F = IndexedFreeAbelianMonoid(ZZ)
            sage: F(F.gen(2))
            F[2]
            sage: F(-5)
            F[-5]
            sage: F(1)
            1
            sage: F([[1, 3], [-2, 12]])
            F[-2]^12*F[1]^3
        """
        if isinstance(x, (list, tuple)):
            x = dict(x)
        return IndexedMonoid._element_constructor_(self, x)

    Element = IndexedFreeAbelianMonoidElement

    @cached_method
    def one(self):
        """
        Return the identity element of ``self``.

        EXAMPLES::

            sage: F = IndexedFreeAbelianMonoid(ZZ)
            sage: F.one()
            1
        """
        return self.element_class(self, {})

    def gen(self, x):
        """
        The generator indexed by ``x`` of ``self``.

        EXAMPLES::

            sage: F = IndexedFreeAbelianMonoid(ZZ)
            sage: F.gen(0)
            F[0]
            sage: F.gen(2)
            F[2]
        """
        if x not in self._indices:
            raise IndexError("{} is not in the index set".format(x))
        try:
            return self.element_class(self, {self._indices(x):1})
        except TypeError: # Backup (if it is a string)
            return self.element_class(self, {x:1})

