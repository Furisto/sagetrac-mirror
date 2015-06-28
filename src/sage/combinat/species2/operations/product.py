# -*- coding: utf-8 -*-
"""
Product of species.

References
----------

 .. [BBL] Combinatorial species and tree-like structures,
 François Bergeron, Gilbert Labelle and Pierre Leroux,
 1998, Cambridge University Press

AUTHOR:

- Jean-Baptiste Priez (2015)
"""
# *****************************************************************************
#       Copyright (C) 2015 Jean-Baptiste Priez <jbp@kerios.fr>.
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#                  http://www.gnu.org/licenses/
# *****************************************************************************
from itertools import imap
import operator
from sage.categories.cycle_index_series import CycleIndexSeries
from sage.categories.species import Species
from sage.combinat.species2 import SpeciesDesign
from sage.combinat.species2.operations.add import Add
from sage.misc.lazy_import import LazyImport
from sage.combinat.subset import Subsets
from sage.functions.other import binomial
from sage.misc.classcall_metaclass import ClasscallMetaclass
from sage.structure.list_clone import ClonableArray
LazyImport("sage.combinat.species2.operations.derivative", "Derivative")


class ProdStructure(ClonableArray):

    def check(self):
        assert(all(s.parent() in Species() for s in self))


class Prod(SpeciesDesign):
    """
    Product of species `\cdot`.

    Let `F` and `G` be two species, we denote `H = F \cdot G` species which is the product of
    `F` and `G` defined by:

    MATH::

        (F \cdot G)[U] := \sum_{S \sqcup T = U} F[S] \times G[T]

    the disjoint sum being taken over all pairs `(S,T)` forming a decomposition of `U`.
    The transport along bijection `\sigma : U \to V` is carried out by setting, for any `(F + G)`-structures `s = (f,g)`
    on `[U]`,

    MATH::

        (F \cdot G)[\sigma](s) := (F[\sigma_{|S}](f), G[\sigma_{|T}](g))\,

    where `\sigma_{|S}` and `\sigma_{|T}` are the restrictions of `\sigma` on respectively `S` and `T`.

    The species `0` (..see :mod:`sage.combinat.species2.zero`) is the absorbing element for product:

    MATH::

        F \cdot 0 = 0 \cdot F = 0\,,

    and the species `1` (..see :mod:`sage.combinat.species2.one`) is the neutral element for product:

    MATH::

        F \cdot 1 = 1 \cdot F = F\,,

    for any species `F`.

    The operation of product is associative and commutative, up to isomorphism but
    in general `F \cdot G` and `G \cdot F` are not identical.

    The multiplication distributes over addition:

    MATH::

        F \cdot (G + H) = F \cdot G + F \cdot H\,.

    (section 1.3, _[BLL])

    TESTS::

        sage: from sage.combinat.species2.singletons import SingletonsSpecies
        sage: X = SingletonsSpecies()
        sage: from sage.combinat.species2.zero import ZeroSpecies
        sage: Z = ZeroSpecies()
        sage: X*Z
        `0`

        sage: from sage.combinat.species2.one import OneSpecies
        sage: O = OneSpecies()
        sage: X*O
        `X`

        sage: from sage.combinat.species2.elements import ElementsSpecies
        sage: e = ElementsSpecies()
        sage: from sage.combinat.species2.sets import SetsSpecies
        sage: E = SetsSpecies()
        sage: X * X * (e + E) * X
        `X`^2·`e`·`X` + `X`^2·`E`·`X`

        sage: E * (X * e) == (E * X) * e
        True

        sage: E * (E * Z)
        `0`

        sage: Sp = Species()
        sage: A = Sp.recursive_species('a')
        sage: B = Sp.recursive_species('b')
        sage: C = Sp.recursive_species('c')
        sage: (A+B)*C
        a·c + b·c

        sage: A^2*(B+C)
        a^2·c + a^2·b
        sage: (A^2 + B+B)*C^3
        2·b·c^3 + a^2·c^3

    """
    # FIXME: tests about associativity,commutativity and distributivity should be somewhere else.

    __metaclass__ = ClasscallMetaclass

    @staticmethod
    def __classcall_private__(cls, *args, **options):

        # # Test the species 0
        if Species().zero() in args:
            return Species().zero()

        # # Filter the species 1
        args = filter(lambda F: F != Species().one(), args)
        if len(args) == 0:
            return Species.one()
        elif len(args) == 1:
            return args[0]

        # # Distributivity F·(G + H)·I --> F·G·I + F·H·I
        for i in range(len(args)):
            F = args[i]
            if isinstance(F, Add):
                return Add(*tuple(Prod(*(args[:i] + (G,) + args[i+1:]))
                                  for G in F._species_))

        # # Associativity: `F · (G · H) --> F · G · H`
        nargs = []
        for F in args:
            if isinstance(F, cls): nargs.extend(F._species_)
            else:                  nargs.append(F)

        # # otherwise
        return super(Prod, cls).__classcall__(cls, *nargs, **options)

    def __init__(self, *species):
        """

        :param F: a sequence of species

        """
        SpeciesDesign.__init__(self)
        self._species_ = species

    def _repr_(self):

        r = ""
        Flast = self._species_[0]
        acc = 1
        for F in self._species_[1:]:
            if F == Flast:
                acc += 1
            else:
                r += ("" if r == "" else "·") + repr(Flast) + ("^%d" % acc if acc > 1 else "")
                acc = 1
            Flast = F
        r += ("" if r == "" else "·") + repr(Flast) + ("^%d" % acc if acc > 1 else "")

        return r

    def transport(self, sigma):
        def Fsigma(s):
            assert(isinstance(s, ProdStructure))
            return self._element_constructor_([t.parent().transport(sigma)(t)
                                               for t in s])

        return Fsigma

    def cycle_index_series(self):
        """
        The product of cycle index series

        MATH::

            Z_{F\cdotG}(p_1, p_2, \cdots) = Z_F(p_1, p_2, \cdots) Z_G(p_1, p_2, \cdots)\,.

        (section 1.3, Proposition 8, _[BBL])
        """
        return reduce(operator.mul, imap(lambda F: F.cycle_index_series(), self._species_),
                      CycleIndexSeries().one())

    def grading(self, s):
        assert(isinstance(s, ProdStructure))
        return sum(t.parent().grading(t) for t in s)

    def is_pointing(self):
        # TODO: overload this method for other operators...
        return self._species_[0] is Species().singletons() \
               and isinstance(self._species_[1], Derivative)

    def _element_constructor_(self, *args, **options):
        return self.element_class(self, *args, **options)

    class Structures(SpeciesDesign.Structures):

        def cardinality(self):
            """
            sage: from sage.combinat.species2.singletons import SingletonsSpecies
            sage: X = SingletonsSpecies()
            sage: f = X*X*X
            sage: [f.graded_component(n).cardinality() for n in range(10)]
            [0, 0, 0, 6, 0, 0, 0, 0, 0, 0]

            """
            def rec_card(n, species):
                if len(species) == 0:
                    if n == 0: return 1
                    return 0
                F = species[0]
                acc = 0
                for k in range(n+1):
                    acc += binomial(n, k) * \
                           F.graded_component(k).cardinality() * \
                           rec_card(n-k, species[1:])
                return acc
            return rec_card(self.grading(), self.ambient()._species_)

        def __iter__(self):
            """
            TESTS::

                sage: from sage.combinat.species2.singletons import SingletonsSpecies
                sage: X = SingletonsSpecies()
                sage: f = X*X*X
                sage: [f.graded_component(n).list() for n in range(10)]
                [[],
                 [],
                 [],
                 [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]],
                 [],
                 [],
                 [],
                 [],
                 [],
                 []]

            """
            def rec_iter(U, species):
                if len(species) == 0:
                    if U.cardinality() == 0:
                        yield()
                    return
                F = species[0]
                for k in range(F.valuation(), U.cardinality() + 1 - sum(map(lambda F: F.valuation(), species[1:]))):
                    # FIXME: it is more efficient to test if F[U] ≠ ∅ or to compute #F[U]??
                    for S in Subsets(U, k=k):
                        T = U.difference(S)
                        for fstruct in F.structures(S):
                            for tup in rec_iter(T, species[1:]):
                                yield (fstruct,) + tup

            val = self.ambient().valuation()
            if val > self.finite_set().cardinality(): return iter([])
            return imap(self._element_constructor_,
                        rec_iter(self.finite_set(), self.ambient()._species_)
                        )

    Element = ProdStructure
