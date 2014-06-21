"""
Lie Algebras

AUTHORS:

- Travis Scrimshaw (2013-05-03): Initial version
"""

#*****************************************************************************
#  Copyright (C) 2013 Travis Scrimshaw <tscrim@ucdavis.edu>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#    This code is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty
#    of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  See the GNU General Public License for more details; the full text
#  is available at:
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from copy import copy
from sage.misc.cachefunc import cached_method
from sage.misc.lazy_attribute import lazy_attribute
from sage.structure.indexed_generators import IndexedGenerators
from sage.structure.parent import Parent
from sage.structure.unique_representation import UniqueRepresentation
from sage.structure.element_wrapper import ElementWrapper

from sage.categories.algebras import Algebras
from sage.categories.lie_algebras import LieAlgebras
from sage.categories.rings import Rings
from sage.categories.morphism import Morphism, SetMorphism
from sage.categories.map import Map
from sage.categories.homset import Hom

from sage.algebras.free_algebra import FreeAlgebra
from sage.algebras.lie_algebras.lie_algebra_element import LieGenerator, \
    LieBracket, LieAlgebraElement, LieAlgebraElementWrapper
from sage.rings.all import ZZ
from sage.rings.ring import Ring
from sage.rings.integer import Integer
from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing
from sage.rings.infinity import infinity
from sage.matrix.matrix_space import MatrixSpace
from sage.matrix.constructor import matrix
from sage.modules.free_module_element import vector
from sage.modules.free_module import FreeModule, span
from sage.combinat.root_system.cartan_type import CartanType, CartanType_abstract
from sage.sets.family import Family
from sage.sets.finite_enumerated_set import FiniteEnumeratedSet

class LieAlgebra(Parent, UniqueRepresentation): # IndexedGenerators):
    r"""
    A Lie algebra `L` over a base ring `R`.

    A Lie algebra is an algebra with a bilinear operation called Lie bracket
    `[\cdot, \cdot] : L \times L \to L` such that `[x, x] = 0` and
    the following relation holds:

    .. MATH::

        \bigl[x, [y, z] \bigr] + \bigl[ y, [z, x] \bigr]
        + \bigl[ z, [x, y] \bigr] = 0.

    This relation is known as the *Jacobi identity* (or sometimes the Jacobi
    relation). We note that from `[x, x] = 0`, we have `[x + y, x + y] = 0`.
    Next from bilinearity, we see that

    .. MATH::

        0 = [x + y, x + y] = [x, x] + [x, y] + [y, x] + [y, y]
        = [x, y] + [y, x],

    thus `[x, y] = -[y, x]` and the Lie bracket is antisymmetric.

    Lie algebras are closely related to Lie groups. Let `G` be a Lie group
    and fix some `g \in G`, we can construct the Lie algebra `L` of `G` by
    considering the tangent space at `g`. We can also (partially) recover `G`
    from `L` by using what is known as the exponential map.

    Given any associative algebra `A`, we can construct a Lie algebra `L` by
    defining the Lie bracket to be the commutator `[a, b] = ab - ba`. We call
    an associative algebra `A` which contains `L` in this fashion an
    *enveloping algebra*. We can the embedding which sends the Lie bracket to
    the commutator a Lie embedding. Now if we are given a Lie algebra `L`, we
    can construct an enveloping algebra `U_L` with Lie embedding `h : L \to
    U_L` which has the following universal property: for any enveloping
    algebra `A` with Lie embedding `f : L \to A`, there exists a unique unital
    algebra homomorphism `g : U_L \to A` such that `f = g \circ h`. The
    algebra `U_L` is known as the *universal enveloping algebra*.

    EXAMPLES:

    We can also create abelian Lie algebras using the ``abelian`` keyword::

        sage: L.<x,y,z> = LieAlgebra(QQ, abelian=True); L
        Abelian Lie algebra on 3 generators (x, y, z) over Rational Field

    We can also input a set of structure coefficients. For example, we want
    to create the Lie algebra of `\QQ^3` under the Lie bracket of `\times`
    (cross-product)::

        sage: L.<x,y,z> = LieAlgebra(QQ, {('x','y'):{'z':1}, ('y','z'):{'x':1}, ('z','x'):{'y':1}})
        sage: L
        Lie algebra on 3 generators (x, y, z) over Rational Field

    We also have classical Lie algebras and can represent them both in the
    Chevalley basis and as matrices. To create the Lie alegrbra given a
    Cartan type, use the argument ``cartan_type``. The default representation
    is in the Chevalley basis, and to use the representation as matrices,
    use ``representation='matrix'``. ::

        sage: L = LieAlgebra(QQ, cartan_type=['A', 2]); L
        Lie algebra of ['A', 2] in the Chevalley basis
        sage: L.basis()
        (h1, h2, e1, e2, e3, f1, f2, f3)
        sage: L = LieAlgebra(QQ, cartan_type=['A', 2], representation='matrix'); L
        Special linear Lie algebra of rank 3 over Rational Field
        sage: L.gens()
        (
        [0 1 0]  [0 0 0]  [0 0 0]  [0 0 0]  [ 1  0  0]  [ 0  0  0]
        [0 0 0]  [0 0 1]  [1 0 0]  [0 0 0]  [ 0 -1  0]  [ 0  1  0]
        [0 0 0], [0 0 0], [0 0 0], [0 1 0], [ 0  0  0], [ 0  0 -1]
        )

    To get an untwisted affine Lie algebra of a classical Lie algebra,
    there are two options. The first is to pass in an affine Cartan type,
    and the other is to use the keyword ``affine=True``. ::

        sage: L = LieAlgebra(QQ, cartan_type=['A', 2, 1]); L
        Affine Lie algebra of ['A', 2] in the Chevalley basis
        sage: L2 = LieAlgebra(QQ, cartan_type=['A', 2], affine=True); L2
        Affine Lie algebra of ['A', 2] in the Chevalley basis
        sage: L is L2
        True
        sage: L.gens()
        ((h1, 0), (h2, 0), (e1, 0), (e2, 0), (e3, 0),
         (f1, 0), (f2, 0), (f3, 0), (f3, 1), (e3, -1), c)

    To get the additional Lie derivative generator to make it a Kac--Moody
    algebra, use the additional keyword ``kac_moody=True``::

        sage: L = LieAlgebra(QQ, cartan_type=['A', 2, 1], kac_moody=True); L
        Affine Kac-Moody algebra of ['A', 2] in the Chevalley basis
        sage: L.gens()
        ((h1, 0), (h2, 0), (e1, 0), (e2, 0), (e3, 0),
         (f1, 0), (f2, 0), (f3, 0), (f3, 1), (e3, -1), c, d)

    To compute the Lie backet of two objects, you cannot use the ``*``.
    This will automatically lift up to the universal enveloping algebra.
    To get elements in the Lie algebra, you must use :meth:`bracket`::

        sage: L = LieAlgebra(QQ, cartan_type=['A',1])
        sage: h,e,f = L.gens()
        sage: L.bracket(h, e)
        2*e1
        sage: elt = h*e; elt
        h1*e1
        sage: elt.parent()
        Noncommutative Multivariate Polynomial Ring in h1, e1, f1 over Rational Field,
         nc-relations: {f1*e1: e1*f1 - h1, e1*h1: h1*e1 - 2*e1, f1*h1: h1*f1 + 2*f1}

    For convienence, there is are two shorthand notations for computing
    Lie backets::

        sage: h,e,f = L.gens()
        sage: L([h,e])
        2*e1
        sage: L([h,[e,f]])
        0
        sage: L([[h,e],[e,f]])
        -4*e1
        sage: L[h, e]
        2*e1
        sage: L[h, L[e, f]]
        0

    .. WARNING::

        Because this is a modified (abused) version of python syntax, it
        does **NOT** work with addition. For example ``L([e + [h, f], h])``
        or ``L[e + [h, f], h]`` will both raise errors. Instead you must
        use ``L[e + L[h, f], h]``.

    Now we construct a free Lie algebra in a few different ways. There are
    two primary representations, as brackets and as polynomials::

        sage: L = LieAlgebra(QQ, 'x,y,z'); L # not tested
        Free Lie algebra generated by (x, y, z) over Rational Field
        sage: P.<a,b,c> = LieAlgebra(QQ, representation="polynomial"); P
        Lie algebra on 3 generators (a, b, c) over Rational Field

    Using brackets, there are two different bases for the free Lie algebra,
    the Hall basis and Lyndon basis. We need to specify which basis we want
    to use before being able to construct elements. Each of these can be
    accessed as follows::

        sage: Hall = L.Hall(); Hall # not tested
        Free Lie algebra generated by (x, y, z) over Rational Field in the Hall basis
        sage: Lyndon = L.Lyndon(); Lyndon # not tested
        Free Lie algebra generated by (x, y, z) over Rational Field in the Lyndon basis

    As a convience, we include generators for the Lie algebra as being
    elements using the Hall basis. The primary difference between these two
    bases is just the canonical form for elements. ::

        sage: L.<x,y,z> = LieAlgebra(QQ); L # not tested
        Free Lie algebra generated by (x, y, z) over Rational Field

    However this does not hold for the polynomial representation, which we
    can think of the variables as being a free algebra and the Lie bracket
    is the commutator::

        sage: P.bracket(a, b) + P.bracket(a - c, b + 3*c)
        2*a*b + 3*a*c - 2*b*a + b*c - 3*c*a - c*b

    REFERENCES:

    .. [deGraaf] Willem A. de Graaf. *Lie Algebras: Theory and Algorithms*.
       North-Holland Mathemtaical Library. (2000). Elsevier Science B.V.

    - Victor Kac. *Infinite Dimensional Lie Algebras*.

    - :wikipedia:`Lie_algebra`
    """
    @staticmethod
    def __classcall_private__(cls, R, arg0=None, arg1=None, names=None,
                              index_set=None, **kwds):
        """
        Select the correct parent based upon input.
        """
        # Check if we need to swap the arguments
        if arg0 in ZZ or arg1 in Algebras(R):
            arg0, arg1 = arg1, arg0

        # Check if a Cartan type was passed, if so, set that to be the first arg
        if "cartan_type" in kwds:
            arg0 = CartanType(kwds["cartan_type"])

        # Parse the first argument
        # -----

        if isinstance(arg0, dict):
            if len(arg0) == 0:
                from sage.algebras.lie_algebras.structure_coefficients import AbelianLieAlgebra
                return AbelianLieAlebra(R, names, index_set)
            elif isinstance(arg0.keys()[0], (list,tuple)):
                # We assume it is some structure coefficients
                arg1, arg0 = arg0, arg1
            else:
                # It is generated by elements of an associative algebra
                index_set = arg0.keys()
                gens = arg0.values()
                A = gens[0].parent()
                return LieAlgebraFromAssociative(R, A, gens, names, index_set)

        if isinstance(arg0, (Ring, MatrixSpace)) or arg0 in Rings():
            if arg1 is None:
                gens = arg0.gens()
                if names is None:
                    names = arg0.variable_names()
            elif isinstance(arg1, str):
                names = arg1
                gens = arg0.gens()
            else:
                gens = arg1

            if names is not None:
                if isinstance(names, str):
                    names = tuple(names.split(','))
                if len(names) != len(gens):
                    raise ValueError("the number of names must equal the number of generators")
            return LieAlgebraFromAssociative(R, arg0, gens, names, index_set)

        if isinstance(arg0, CartanType_abstract):
            if arg0.is_affine():
                if not arg0.is_untwisted_affine():
                    raise NotImplementedError("only implemented for untwisted affine types")
                kwds["affine"] = True
                arg0 = arg0.classical()
            rep = kwds.get("representation", "basis")
            if rep == "matrix":
                from sage.algebras.lie_algebras.classical_lie_algebra import ClassicalMatrixLieAlgebra
                ret = ClassicalMatrixLieAlgebra(R, arg0)
            elif rep == "basis":
                from sage.algebras.lie_algebras.classical_lie_algebra import LieAlgebraChevalleyBasis
                ret = LieAlgebraChevalleyBasis(R, arg0)
            if kwds.get("affine", False):
                from sage.algebras.lie_algebras.affine_lie_algebras import AffineLieAlgebra
                ret = AffineLieAlgebra(ret, kwds.get("kac_moody", False))
            return ret

        if isinstance(arg0, (list, tuple)):
            if all(isinstance(x, str) for x in arg0):
                # If they are all strings, then it is a list of variables
                names = tuple(arg0)
            else:
                # Otherwise assume they are elements of an assoc alg
                A = arg0[0].parent()
                if isinstance(arg1, str):
                    names = tuple(arg1.split(','))
                    if len(names) == 1 and len(arg0) != 1:
                        names = ['{}{}'.format(names[0], i) for i in xrange(len(arg0))]
                elif isinstance(arg1, (tuple, list)):
                    names = tuple(arg1)
                    if len(names) != len(arg0):
                        raise ValueError("the number of names must equal the number of generators")
                return LieAlgebraFromAssociative(R, A, arg0, names, index_set)

        if isinstance(arg0, str):
            names = tuple(arg0.split(','))

        # Parse the second argument

        if isinstance(arg1, dict):
            if isinstance(names, str):
                names = tuple(names.split(','))
            # Assume it is some structure coefficients
            from sage.algebras.lie_algebras.structure_coefficients import LieAlgebraWithStructureCoefficients
            return LieAlgebraWithStructureCoefficients(R, arg1, names, index_set)

        # Otherwise it must be either a free or abelian Lie algebra

        if arg1 in ZZ:
            if isinstance(arg0, str):
                names = arg0
            if names is None:
                index_set = range(arg1)
            else:
                if isinstance(names, str):
                    names = tuple(names.split(','))
                    if arg1 != 1 and len(names) == 1:
                        names = tuple('{}{}'.format(names[0],i) for i in xrange(arg1))
                if arg1 != len(names):
                    raise ValueError("the number of names must equal the number of generators")

        if kwds.get("abelian", False):
            from sage.algebras.lie_algebras.structure_coefficients import AbelianLieAlgebra
            return AbelianLieAlgebra(R, names, index_set)

        rep = kwds.get("representation", "bracket")
        if rep == "polynomial":
            # Construct the free Lie algebra from polynomials in the
            #   free (associative unital) algebra
            # TODO: Change this to accept an index set once FreeAlgebra accepts one
            F = FreeAlgebra(R, names, len(names))
            return LieAlgebraFromAssociative(R, F, F.gens(), names, index_set)

        from sage.algebras.lie_algebras.free_lie_algebra import FreeLieAlgebra
        ret = FreeLieAlgebra(R, names, index_set)
        if rep == "Hall":
            return ret.Hall()
        if rep == "Lyndon":
            return ret.Lyndon()
        return ret

    def __init__(self, R, names=None, index_set=None, category=None):
        """
        The Lie algebra.

        INPUT:

        - ``R`` -- the base ring

        - ``names`` -- (optional) the names of the generators

        - ``index_set`` -- (optional) the indexing set

        - ``category`` -- the category of the Lie algebra; the default is the
          category of Lie algebras over ``R``

        EXAMPLES::

            sage: L.<x,y> = LieAlgebra(QQ, abelian=True)
            sage: L.category()
            Category of finite dimensional lie algebras with basis over Rational Field
        """
        category = LieAlgebras(R).or_subcategory(category)
        if index_set is None:
            if names is None:
                raise ValueError("either the names of the generators"
                                 " or the index set must be specified")
            index_set = tuple(names)

        if isinstance(index_set, (tuple, list)):
            index_set = FiniteEnumeratedSet(index_set)

        #if names is None and index_set.cardinality() < infinity \
        #        and all(isinstance(i, str) for i in index_set):
        #    names = index_set

        self._indices = index_set
        Parent.__init__(self, base=R, names=names, category=category)

    def _element_constructor_(self, x):
        """
        Convert ``x`` into ``self``.

        EXAMPLES::

            sage: L.<x,y> = LieAlgebra(QQ)
            sage: elt = L([x, y]); elt
            [x, y]
            sage: elt.parent() is L.Hall()
            True
        """
        if isinstance(x, list) and len(x) == 2:
            return self.bracket(self(x[0]), self(x[1]))
        if isinstance(x, self.element_class) and x.parent() is self:
            return x
        if x in self.base_ring():
            if x != 0:
                raise ValueError("can only convert the scalar 0 into a Lie algebra element")
            return self.zero()
        return self.element_class(self, x)

    def __getitem__(self, x):
        """
        If `x` is a pair `(a, b)`, return the Lie bracket `(a, b)`. Otherwise
        try to return the `x`-th element of ``self``.

        EXAMPLES::

            sage: L.<x, y> = LieAlgebra(QQ)
            sage: H = L.Hall()
            sage: H[x, [y, x]]
            -[x, [x, y]]
        """
        if isinstance(x, tuple) and len(x) == 2:
            return self(x[0])._bracket_(self(x[1]))
        return super(LieAlgebra, self).__getitem__(x)

    def _coerce_map_from_(self, R):
        """
        Return ``True`` if there is a coercion from ``R`` into ``self`` and
        ``False`` otherwise.

        The things that coerce into ``self`` are:

        - Lie algebras in the same variables over a base with a coercion
          map into ``self.base_ring()``.

        - A module which coerces into the base vector space of ``self``.

        TESTS::
        """
        if not isinstance(R, LieAlgebra):
            # Should be moved to LieAlgebrasWithBasis somehow since it is a generic coercion
            if self.free_module() is not NotImplemented:
                return self.free_module().has_coerce_map_from(R)
            return False

        # We check if it is a subalgebra of something that can coerce into ``self``
        from sage.algebras.lie_algebras.subalgebra import LieSubalgebra
        if isinstance(R, LieSubalgebra) and self.has_coerce_map_from(R._ambient):
            return R.ambient_lift

        # Lie algebras in the same indices over any base that coerces in
        if R._indices != self._indices:
            return False

        return self.base_ring().has_coerce_map_from(R.base_ring())

    @lazy_attribute
    def _ordered_indices(self):
        """
        Return the index set of ``self`` in order.
        """
        return tuple(sorted(self._indices))

    def _an_element_(self):
        """
        Return an element of ``self``.
        """
        return self.sum(self.lie_algebra_generators())

    @cached_method
    def zero(self):
        """
        Return the element `0`.
        """
        return self.element_class(self, {})

    zero_element = zero

    # TODO: find a better place for this method
    def indices(self):
        """
        Return the indices of the basis of ``self``.
        """
        return self._indices

    # The following methods should belong to LieAlgebrasWithBasis once created
    def _from_dict(self, d, coerce=False, remove_zeros=True):
        """
        Construct an element of ``self`` from an ``{index: coefficient}``
        dictionary.

        INPUT:

        - ``d`` -- a dictionary ``{index: coeff}`` where each ``index`` is the
          index of a basis element and each ``coeff`` belongs to the
          coefficient ring ``self.base_ring()``

        - ``coerce`` -- a boolean (default: ``False``), whether to coerce the
          ``coeff``s to the coefficient ring

        - ``remove_zeros`` -- a boolean (default: ``True``), if some
          ``coeff``s may be zero and should therefore be removed

        EXAMPLES::

            sage: e = SymmetricFunctions(QQ).elementary()
            sage: s = SymmetricFunctions(QQ).schur()
            sage: a = e([2,1]) + e([1,1,1]); a
            e[1, 1, 1] + e[2, 1]
            sage: s._from_dict(a.monomial_coefficients())
            s[1, 1, 1] + s[2, 1]

        If the optional argument ``coerce`` is ``True``, then the
        coefficients are coerced into the base ring of ``self``::

            sage: part = Partition([2,1])
            sage: d = {part:1}
            sage: a = s._from_dict(d,coerce=True); a
            s[2, 1]
            sage: a.coefficient(part).parent()
            Rational Field

        With ``remove_zeros=True``, zero coefficients are removed::

            sage: s._from_dict({part:0})
            0

        .. WARNING::

            With ``remove_zeros=False``, it is assumed that no
            coefficient of the dictionary is zero. Otherwise, this may
            lead to illegal results::

                sage: list(s._from_dict({part:0}, remove_zeros=False))
                [([2, 1], 0)]
        """
        assert isinstance(d, dict)
        if coerce:
            R = self.base_ring()
            d = dict((key, R(coeff)) for key,coeff in d.iteritems())
        if remove_zeros:
            d = dict((key, coeff) for key, coeff in d.iteritems() if coeff)
        return self.element_class(self, d)

    def monomial(self, i):
        """
        Return the monomial indexed by ``i``.
        """
        return self.element_class(self, {i: self.base_ring().one()})

    def term(self, i, c=None):
        """
        Return the term indexed by ``i`` with coefficient ``c``.
        """
        if c is None:
            c = self.base_ring().one()
        else:
            c = self.base_ring()(c)
        return self.element_class(self, {i: c})

    def lie_algebra_generators(self):
        """
        Return the Lie algebra generators of ``self``.
        """
        return Family(self._indices, self.monomial, name="monomial map")

class FinitelyGeneratedLieAlgebra(LieAlgebra):
    """
    An fintely generated Lie algebra.

    INPUT:

    - ``R`` -- the base ring

    - ``names`` -- the names of the generators

    - ``index_set`` -- the index set of the generators

    - ``category`` -- the category of the Lie algebra
    """
    def __init__(self, R, names=None, index_set=None, category=None):
        """
        Initialize ``self``.

        EXAMPLES::

            sage: L.<x,y> = LieAlgebra(QQ, abelian=True)
            sage: L.category()
            Category of finite dimensional lie algebras with basis over Rational Field
        """
        LieAlgebra.__init__(self, R, names, index_set, category)
        self.__ngens = len(self._indices)

    def _repr_(self):
        """
        Return a string representation of ``self``.

        EXAMPLES::

            sage: F.<x,y> = LieAlgebra(QQ, {('x','y'): {'x': 1}})
            sage: F
            Lie algebra on 2 generators (x, y) over Rational Field
        """
        if self.__ngens == 1:
            return "Lie algebra on the generator {0} over {1}".format(
                    self.gens()[0], self.base_ring())
        return "Lie algebra on {0} generators {1} over {2}".format(
                self.__ngens, self.gens(), self.base_ring())

    def gen(self, i):
        """
        The ``i``-th generator of the Lie algebra.

        EXAMPLES::
        """
        return self.element_class(self, self.monomial(self._indices[i]))

    @cached_method
    def gens(self):
        """
        Return a tuple whose entries are the generators for this
        object, in some order.

        EXAMPLES::
        """
        return tuple( self.lie_algebra_generators().values() )

class InfinitelyGeneratedLieAlgebra(LieAlgebra):
    r"""
    An infinitely generated Lie algebra.
    """
    def _an_element_(self):
        """
        Return an element of ``self``.
        """
        return self.lie_algebra_generators()[self._indices.an_element()]

    def dimension(self):
        r"""
        Return the dimension of ``self``, which is `\infty`.

        EXAMPLES::

            sage: L = lie_algebras.Heisenberg(QQ, oo)
            sage: L.dimension()
            +Infinity
        """
        return infinity

    def gens(self):
        """
        Return a ``NotImplementedError`` since there are an infinite number
        of generators.

        EXAMPLES::

            sage: L = lie_algebras.Heisenberg(QQ, oo)
            sage: L.gens()
            Traceback (most recent call last):
            ...
            NotImplementedError: infinite list
        """
        raise NotImplementedError("infinite list")

class LieAlgebraFromAssociative(LieAlgebra):
    """
    A Lie algebra whose elements are from an associative algebra and whose
    bracket is the commutator.

    .. WARNING::

        The returned universal enveloping algebra is too large in general.
        To fix this, we need subalgebras implemented.

    .. TODO::

        Return the subalgebra generated by the basis
        elements of ``self`` for the universal enveloping algebra.

    EXAMPLES:

    We create a simple example with a commutative algebra as the base algebra.
    Note that the bracket of everything will be 0::

        sage: R.<a,b> = PolynomialRing(QQ)
        sage: L.<x,y> = LieAlgebra(QQ, R)
        sage: L.bracket(x, y)
        0

    Next we use a free algebra and do some simple computations::

        sage: R.<a,b> = FreeAlgebra(QQ, 2)
        sage: L.<x,y> = LieAlgebra(QQ, R)
        sage: x-y
        a - b
        sage: L.bracket(x-y, x)
        a*b - b*a
        sage: L.bracket(x-y, L.bracket(x,y))
        a^2*b - 2*a*b*a + a*b^2 + b*a^2 - 2*b*a*b + b^2*a

    We can also use a subset of the generators to use in our Lie algebra::

        sage: R.<a,b,c> = FreeAlgebra(QQ, 3)
        sage: L.<x,y> = LieAlgebra(QQ, R, [a,b])

    Now for a more complicated example using the group ring of `S_3` as our
    base algebra::

        sage: G = SymmetricGroup(3)
        sage: S = GroupAlgebra(G, QQ)
        sage: L.<x,y> = LieAlgebra(QQ, S)
        sage: L.bracket(x, y)
        (2,3) - (1,3)
        sage: L.bracket(x, y-x)
        (2,3) - (1,3)
        sage: L.bracket(L.bracket(x, y), y)
        2*(1,2,3) - 2*(1,3,2)
        sage: L.bracket(x, L.bracket(x, y))
        (2,3) - 2*(1,2) + (1,3)
        sage: L.bracket(x, L.bracket(L.bracket(x, y), y))
        0

    Here is an example using matrices::

        sage: MS = MatrixSpace(QQ,2)
        sage: m1 = MS([[0, -1], [1, 0]])
        sage: m2 = MS([[-1, 4], [3, 2]])
        sage: L.<x,y> = LieAlgebra(QQ, MS, [m1, m2])
        sage: x
        [ 0 -1]
        [ 1  0]
        sage: y
        [-1  4]
        [ 3  2]
        sage: L.bracket(x,y)
        [-7 -3]
        [-3  7]
        sage: L.bracket(y,y)
        [0 0]
        [0 0]
        sage: L.bracket(y,x)
        [ 7  3]
        [ 3 -7]
        sage: L.bracket(x, L.bracket(y,x))
        [-6 14]
        [14  6]

    If we use a subset of the generators to construct our Lie algebra,
    the result of :meth:`universal_enveloping_algebra()` can be too large::

        sage: R.<a,b,c> = FreeAlgebra(QQ, 3)
        sage: L = LieAlgebra(QQ, R, [a,b])
        sage: L.universal_enveloping_algebra() is R
        True
    """
    @staticmethod
    def __classcall_private__(cls, R, A, gens, names=None, index_set=None, category=None):
        """
        Normalize input to ensure a unique representation.

        EXAMPLES::

            sage: G = SymmetricGroup(3)
            sage: S = GroupAlgebra(G, QQ)
            sage: L = LieAlgebra(QQ, S, 'x,y')
            sage: L2 = LieAlgebra(QQ, S, [G((1,2,3)), G((1,2))], 'x,y')
            sage: L is L2
            True
        """
        gens = map(A, gens)
        try:
            # Try to make things, such as matrices, immutable (since we need to hash them)
            gens = map(lambda x: x.set_immutable(), gens)
        except AttributeError:
            pass

        return super(LieAlgebraFromAssociative, cls).__classcall__(cls,
                    R, A, tuple(gens), tuple(names), index_set)

    def __init__(self, R, assoc, gens, names=None, index_set=None, category=None):
        """
        Initialize ``self``.

        EXAMPLES::

            sage: G = SymmetricGroup(3)
            sage: S = GroupAlgebra(G, QQ)
            sage: L.<x,y> = LieAlgebra(QQ, S)
            sage: TestSuite(L).run()
        """
        self._assoc = assoc
        # TODO: We should strip axioms from the category of the base ring,
        #   such as FiniteDimensional, WithBasis
        FinitelyGeneratedLieAlgebra.__init__(self, R, names, index_set, category)
        # We register the coercion here since the UEA already exists
        self.lift.register_as_coercion()
        self.__gens = Family(self._indices, lambda i: gens[i])

    def _repr_option(self, key):
        """
        Metadata about the :meth:`_repr_` output.

        See :meth:`sage.structure.parent._repr_option` for details.

        EXAMPLES::

            sage: MS = MatrixSpace(QQ,2)
            sage: L.<x> = LieAlgebra(QQ, MS, [MS.one()])
            sage: L._repr_option('element_ascii_art')
            True
        """
        return self._assoc._repr_option(key)

    def _element_constructor_(self, x):
        """
        Convert ``x`` into ``self``.

        EXAMPLES::

            sage: G = SymmetricGroup(3)
            sage: S = GroupAlgebra(G, QQ)
            sage: L.<x,y> = LieAlgebra(QQ, S)
            sage: elt = L(x - y); elt
            -(1,2) + (1,2,3)
            sage: elt.parent() is L
            True
        """
        if isinstance(x, LieAlgebraElement) and x.parent() is self:
            return x
        return self.element_class(self, self._assoc(x))

    def _construct_UEA(self):
        """
        Construct the universal enveloping algebra of ``self``.

        EXAMPLES::

            sage: G = SymmetricGroup(3)
            sage: S = GroupAlgebra(G, QQ)
            sage: L.<x,y> = LieAlgebra(QQ, S)
            sage: L._construct_UEA() is S
            True
        """
        return self._assoc

    universal_enveloping_algebra = _construct_UEA

    def gen(self, i):
        """
        Return the ``i``-th generator of ``self``.

        EXAMPLES::

            sage: G = SymmetricGroup(3)
            sage: S = GroupAlgebra(G, QQ)
            sage: L.<x,y> = LieAlgebra(QQ, S)
            sage: L.gen(0)
            (1,2,3)
        """
        return self.element_class(self, self.__gens[i])

    def gens(self):
        """
        Return the generators of ``self``.

        EXAMPLES::

            sage: G = SymmetricGroup(3)
            sage: S = GroupAlgebra(G, QQ)
            sage: L.<x,y> = LieAlgebra(QQ, S)
            sage: L.gens()
            ((1,2,3), (1,2))
        """
        return self.__gens

    def monomial(self, i):
        """
        Return the monomial indexed by ``i``.
        """
        if i in self._indices:
            i = self.__gens[i]
        else:
            raise ValueError("not an index")
        return LieAlgebra.monomial(self, i)

    def term(self, i, c=None):
        """
        Return the term indexed by ``i`` with coefficient ``c``.
        """
        if i in self._indices:
            i = self.__gens[i]
        else:
            raise ValueError("not an index")
        return LieAlgebra.term(self, i, c)

    @cached_method
    def zero_element(self):
        """
        Return `0`.

        EXAMPLES::

            sage: G = SymmetricGroup(3)
            sage: S = GroupAlgebra(G, QQ)
            sage: L.<x,y> = LieAlgebra(QQ, S)
            sage: L.zero_element()
            0
        """
        return self.element_class(self, self._assoc.zero())

    zero = zero_element

    def is_abelian(self):
        """
        Return ``True`` if ``self`` is abelian.

        EXAMPLES::

            sage: R = FreeAlgebra(QQ, 2, 'x,y')
            sage: L.<x,y> = LieAlgebra(QQ, R)
            sage: L.is_abelian()
            False
            sage: R = PolynomialRing(QQ, 'x,y')
            sage: L.<x,y> = LieAlgebra(QQ, R)
            sage: L.is_abelian()
            True

        An example with a Lie algebra from the group algebra::

            sage: G = SymmetricGroup(3)
            sage: S = GroupAlgebra(G, QQ)
            sage: L.<x,y> = LieAlgebra(QQ, S)
            sage: L.is_abelian()
            False

        Now we construct a Lie algebra from commuting elements in the group
        algebra::

            sage: G = SymmetricGroup(5)
            sage: S = GroupAlgebra(G, QQ)
            sage: gens = [G((1, 2)), G((3, 4))]
            sage: L.<x,y> = LieAlgebra(QQ, gens, S)
            sage: L.is_abelian()
            True
        """
        if self._assoc.is_commutative():
            return True
        return super(LieAlgebraFromAssociative, self).is_abelian()

    class Element(LieAlgebraElementWrapper):
        def _bracket_(self, rhs):
            """
            Return the bracket ``[self, rhs]``.

            EXAMPLES::

                sage: R = FreeAlgebra(QQ, 3, 'x,y,z')
                sage: L.<x,y,z> = LieAlgebra(QQ, R)
                sage: L.bracket(x, y)
                x*y - y*x

                sage: G = SymmetricGroup(3)
                sage: S = GroupAlgebra(G, QQ)
                sage: L.<x,y> = LieAlgebra(QQ, S)
                sage: L.bracket(x, y)
                (2,3) - (1,3)

                sage: L = LieAlgebra(QQ, cartan_type=['A',2], representation='matrix')
                sage: L.bracket(L.gen(0), L.gen(1))
                [0 0 1]
                [0 0 0]
                [0 0 0]
            """
            return self.__class__(self.parent(), self.value*rhs.value - rhs.value*self.value)

        def lift(self):
            """
            Lift ``self`` to the universal enveloping algebra.

            EXAMPLES::

                sage: R = FreeAlgebra(QQ, 3, 'x,y,z')
                sage: L.<x,y,z> = LieAlgebra(QQ, R)
                sage: x.lift()
                x
                sage: x.lift().parent()
                Free Algebra on 3 generators (x, y, z) over Rational Field
            """
            return self.value

