"""
Smash product of algebras

Author: Mark Shimozono
"""
#*****************************************************************************
#  Copyright (C) 2014 Mark Shimozono <mshimo at math.vt.edu>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from functools import partial
from sage.misc.cachefunc import cached_method
from sage.structure.unique_representation import UniqueRepresentation
from sage.structure.parent import Parent
from sage.categories.all import AlgebrasWithBasis, ModulesWithBasis
from sage.categories.category import Category
from sage.categories.morphism import SetMorphism
from sage.categories.tensor import tensor
from sage.categories.homset import Hom
from sage.combinat.free_module import CombinatorialFreeModule, CombinatorialFreeModule_Tensor, \
CombinatorialFreeModule_TensorGrouped, CartesianProductWithFlattening, CartesianProductWithUnflattening

class SmashProductAlgebraElement(CombinatorialFreeModule.Element):
    r"""
    Element class for :class:`SmashProductAlgebra`.
    """
    def to_opposite(self):
        r"""
        Map ``self`` to the smash product with factors in opposite order.

        This uses coercion.

        In the following example, `A` is the polynomial ring in one variable (realized by a free monoid),
        which represents the fundamental weight in the weight lattice of `SL_2` and `B` is the 
        Weyl group of `SL_2`, which is the symmetric group on two letters. The reflection acts on the
        fundamental weight by negation.

        EXAMPLES::
        
            sage: F = FreeMonoid(n=1, names=['a'])
            sage: A = F.algebra(ZZ); A.rename("A")
            sage: A._print_options['prefix'] = 'A'
            sage: W = WeylGroup("A1",prefix="s")
            sage: B = W.algebra(ZZ); B.rename("B")
            sage: cat = ModulesWithBasis(ZZ)
            sage: AB = tensor([A,B],category=cat)
            sage: BA = tensor([B,A],category=cat)
            sage: def twist_func(x):
            ...       if x[0] != x[0].parent().one() and mod(x[1].to_word().length(),2) == 1:
            ...           return -AB.monomial((x[1],x[0]))
            ...       return AB.monomial((x[1],x[0]))
            sage: twist = BA.module_morphism(on_basis=twist_func, codomain=AB, category=cat)
            sage: def untwist_func(x):
            ...       if x[1] != x[1].parent().one() and mod(x[0].to_word().length(),2) == 1:
            ...           return -BA.monomial((x[1],x[0]))
            ...       return BA.monomial((x[1],x[0]))
            sage: untwist = AB.module_morphism(on_basis=untwist_func, codomain=BA, category=cat)

            sage: ASB = SmashProductAlgebra(A, B, twist)
            sage: BSA = SmashProductAlgebra(B, A, untwist)
            sage: ASB.register_opposite(BSA)
            sage: ab = ASB.an_element(); ab
            2*A[a] B[s1] + 2*A[a]
            sage: BSA = ASB.opposite()
            sage: ba = BSA(ab); ba
            -2*B[s1] A[a] + 2*A[a]
            sage: ASB(ba) == ab
            True
            sage: ASB == BSA.opposite()
            True
            sage: ba == ab.to_opposite()
            True
            sage: A._print_options['prefix'] = 'B'

        """
        return self.parent().opposite()(self)

class SmashProductAlgebra(CombinatorialFreeModule_TensorGrouped):
    r"""
    Smash products of algebras.

    INPUT:

        - ``A`` and ``B`` -- algebras with basis over the same commutative ring
        - ``twist`` -- a module homomorphism from `B` tensor `A` to `A` tensor `B`
        - ``category`` -- optional (default: None) category for resulting algebra. This should be a subcategory of
          :class:`AlgebrasWithBasis(R).TensorProducts()` where `R` is the base ring.
        - ``suppress_ones`` -- optional (default: None) The default printing of tensor monomials
          will suppress tensor factors of the identity.

    Returns the smash product `S(A,B,twist)`. As a module it is `A` tensor `B`.
    The product is determined by a module homomorphism ``twist`` from `B` tensor `A`
    to `A` tensor `B` as described below.

    Particular rings that are realized as smash products are the cohomological and K-theoretic nilHecke rings
    of Kostant and Kumar, the affine Hecke algebra, and the double affine Hecke algebra. These all come from actions
    of one algebra on another. Another class of examples comes from quasi-triangular Hopf algebras and the R-matrix.

    ..RUBRIC::

    Let `R` be the common base ring of `A` and `B`. All tensor products are taken over `R`.
    A smash product `(A,B,twist)` is an `R`-algebra structure imposed on `A` tensor `B` such that
    `A` and `B` are subalgebras in the natural way, whose multiplication is defined
    via an `R`-module homomorphism ``twist`` from `B` tensor `A` to `A` tensor `B` 
    as follows. Let `I_A` be the identity map on `A` and `m_A` be the multiplication map from
    `A` tensor `A` to `A`. Form the map from `A` tensor `B` tensor `A` tensor `B` to
    `A` tensor `B` by the composition

    ..MATH::

        m = (m_A tensor m_B) \circ (I_A tensor twist tensor I_B)

    The reference [CIMZ]_ gives necessary and sufficient conditions on ``twist`` for `m` to
    define an `R`-algebra structure on `A` tensor `B`.

    REFERENCE:

        .. [CIMZ] Caenepeel, S.; Ion, Bogdan; Militaru, G.; Zhu, Shenglin. The factorization problem
          and the smash biproduct of algebras and coalgebras. Algebr. Represent. Theory 3 (2000),
          no. 1, 19--42. 

    If `B` has a left action on `A` by algebra endomorphisms, defining `twist(b tensor a) = (b . a) tensor b`
    makes `m` into an algebra multiplication map. Similarly if `A` has a right action on `B` by algebra
    endomorphisms, then one may use `twist(b tensor a) = a tensor (b . a)`.

    In the following example both `A` and `B` are the group algebra of the symmetric group `S_3` over the integers,
    and `B` has a left action on `A` induced by conjugation of symmetric group elements.

    EXAMPLES::

        sage: W = WeylGroup(CartanType(['A',2]),prefix="s")
        sage: r = W.from_reduced_word
        sage: A = W.algebra(ZZ); A.rename("A")
        sage: AA = tensor([A,A], category=ModulesWithBasis(ZZ))
        sage: twist = AA.module_morphism(on_basis=lambda x: AA.monomial((x[0]*x[1]*x[0]**(-1),x[0])),codomain=AA)
        sage: ba = AA.monomial((r([1]),r([2]))); ba
        B[s1] # B[s2]
        sage: ab = twist(ba); ab
        B[s1*s2*s1] # B[s1]
        sage: C = SmashProductAlgebra(A, A, twist, suppress_ones=False); C
        Smash product of A and A
        sage: c = A.monomial(A.basis().keys().an_element()); c
        B[s1*s2]
        sage: d = A.an_element(); d
        B[s1*s2*s1] + 3*B[s1*s2] + 3*B[s2*s1]
        sage: cd = C.from_direct_product((c,d)); cd
        B[s1*s2] # B[s1*s2*s1] + 3*B[s1*s2] # B[s1*s2] + 3*B[s1*s2] # B[s2*s1]
        sage: cd * cd
        9*B[s2*s1] # B[s1*s2] + 9*B[s2*s1] # B[s2*s1] + 3*B[s2*s1] # B[s1] + 3*B[s2*s1] # B[s2] + 18*B[s2*s1] # B[1] + 3*B[1] # B[s1] + 3*B[1] # B[s2] + B[1] # B[1]

    ..RUBRIC:: Opposite order smash product

    If the map ``twist`` has an inverse ``untwist``, then ``untwist`` is an algebra isomorphism from
    `S(A,B,twist)` to `S(B,A,untwist)`. To set up coercions between these two algebras, first create both algebras
    (call them ``ASB`` and ``BSA`` for short), and then invoke `ASB.register_opposite(BSA)`.

    ..IMPLEMENTATION:: The smash product is the flattened tensor product of `A` and `B`. However it knows its
    tensor factors. Coercion is immediately allowed between this underlying flattened tensor product module and the smash product,
    with no additional definitions. Intentionally, the coercion registration is made entirely separate from the creation of the
    algebras, for convenience of use by algebras with realizations which carry additional category information and use both
    forms of the smash product.

    """

    def __init__(self, A, B, twist, category=None, suppress_ones=None):
        """
        EXAMPLES::

            sage: W = WeylGroup("A2",prefix="s")
            sage: A = W.algebra(ZZ); A.rename("A")
            sage: B = A
            sage: BA = tensor([B,A],category=ModulesWithBasis(ZZ))
            sage: AB = BA
            sage: def t_map(x):
            ...       return AB.monomial((x[1],x[0]))
            sage: twist = BA.module_morphism(on_basis=t_map, codomain=AB, category=ModulesWithBasis(ZZ))
            sage: C = SmashProductAlgebra(A,B,twist); C # indirect doctest
            Smash product of A and A

        """
        R = A.base_ring()
        module_category = ModulesWithBasis(R)
        algebra_category = AlgebrasWithBasis(R)
        tensor_category = module_category.TensorProducts()
        if R != B.base_ring():
            raise TypeError, "%s and %s must have the same base ring"%(A,B)
        if A not in algebra_category or B not in algebra_category:
            raise TypeError, "Tensor factors should be AlgebrasWithBasis over %s"%(R)
        if not twist.category().is_subcategory(module_category.hom_category()):
            raise TypeError, "twist should be a module morphism"
        AB = tensor([A,B], category=module_category)
        BA = tensor([B,A], category=module_category)
        if twist.codomain() != AB or twist.domain() != BA:
            raise TypeError, "Domain or codomain of twist is incorrect"

        default_category = AlgebrasWithBasis(R).TensorProducts()
        if not category:
            category = default_category
        elif not category.is_subcategory(default_category):
            raise TypeError, "Category %s is not a subcategory of %s"%(category, default_category)
        self._category = category

        if suppress_ones is None:
            self._suppress_ones = True
        elif suppress_ones not in (True,False):
            raise ValueError, "%s should be True or False"%suppress_ones
        else:
            self._suppress_ones = suppress_ones

        CombinatorialFreeModule_TensorGrouped.__init__(self, (A,B), category=category)
        self._twist = twist
        self._has_opposite = False # default: no "opposite" smash product has been registered
        # Define the product morphism using twist
        ItwistI = tensor([A._identity_map(), twist, B._identity_map()], category=module_category)
        mAmB = tensor([A._product_morphism(),B._product_morphism()], category=module_category)
        self._product_morphism_map = SetMorphism(Hom(ItwistI.domain(), mAmB.codomain(), category=module_category), mAmB * ItwistI)

    def _repr_(self):
        r"""
        EXAMPLES::

            sage: W = WeylGroup("A2",prefix="s")
            sage: A = W.algebra(ZZ)
            sage: B = A
            sage: BA = tensor([B,A],category=ModulesWithBasis(ZZ))
            sage: AB = BA
            sage: def t_map(x):
            ...       return AB.monomial((x[1],x[0]))
            sage: twist = BA.module_morphism(on_basis=t_map, codomain=AB, category=ModulesWithBasis(ZZ))
            sage: C = SmashProductAlgebra(A,B,twist); C
            Smash product of A and A

            Question: Should this name include twist?

        """
        return "Smash product of %s and %s"%(self.factor(0), self.factor(1))

    def _repr_term(self, term):
        r"""
        A string for a term.
        """
        if self._suppress_ones:
            if term[0] == self.factor(0).one_basis():
                if term[1] == self.factor(1).one_basis():
                    return "1"
                return self.factor(1)._repr_term(term[1])
            if term[1] == self.factor(1).one_basis():
                return self.factor(0)._repr_term(term[0])
            symb = " "
        else:
            from sage.categories.tensor import tensor
            symb = self._print_options['tensor_symbol']
            if symb is None:
                symb = tensor.symbol
        return symb.join(algebra._repr_term(t) for (algebra, t) in zip(self.factors(), term))

    def twist(self):
        r"""
        The map that defines the smash product structure.

        EXAMPLES::

            sage: W = WeylGroup("A2",prefix="s")
            sage: A = W.algebra(ZZ); A.rename("A")
            sage: AA = tensor([A,A],category=ModulesWithBasis(ZZ))
            sage: def t_map(x):
            ...       return AA.monomial((x[1],x[0]))
            sage: twist = AA.module_morphism(on_basis=t_map, codomain=AA, category=ModulesWithBasis(ZZ))
            sage: C = SmashProductAlgebra(A,A,twist)
            sage: C.twist()
            Generic endomorphism of A # A

        """
        return self._twist

    def _product_morphism(self):
        r"""
        The multiplication map on the smash product.

        This is a module homomorphism from the twofold tensor product of ``self``, to ``self``.
        """
        return self._product_morphism_map

    def product_on_basis(self, p1, p2):
        r"""
        The product of basis elements indexed by `p1` and `p2`.

        EXAMPLES::

            sage: W = WeylGroup(CartanType(['A',2]),prefix="s")
            sage: r = W.from_reduced_word
            sage: A = W.algebra(ZZ); A.rename("A")
            sage: AA = tensor([A,A], category=ModulesWithBasis(ZZ))
            sage: twist = AA.module_morphism(on_basis=lambda x: AA.monomial((x[0]*x[1]*x[0]**(-1),x[0])),codomain=AA)
            sage: C = SmashProductAlgebra(A, A, twist,suppress_ones=False)
            sage: p1 = (r([1]),r([1,2]))
            sage: p2 = (r([1,2,1]),r([2]))
            sage: C.product_on_basis(p1,p2)
            B[1] # B[s1]
            sage: C2 = tensor([C,C])
            sage: p = C2.indices_to_index()(p1,p2); p
            (s1, s1*s2, s1*s2*s1, s2)
            sage: C2.product_on_basis(p,p)
            B[s1*s2] # B[s2*s1] # B[s1*s2] # B[1]

        """
        mult = self._product_morphism()
        return self(mult(mult.domain().monomial(p1+p2)))

    def _the_coercion_map(self, other_algebra_module, twist, x):
        return self(twist(other_algebra_module(x)))

    def register_opposite(self, other_algebra):
        if not isinstance(other_algebra, SmashProductAlgebra):
            raise TypeError, "%s is not a smash product"
        if not other_algebra.factor(0) == self.factor(1) or not other_algebra.factor(1) == self.factor(0):
            raise TypeError, "Factors are not opposite"
        twist = self.twist()
        untwist = other_algebra.twist()
        ABmod = twist.codomain()
        BAmod = twist.domain()
        if untwist.domain() != ABmod or untwist.codomain() != BAmod:
            raise TypeError, "Twists are not inverse"
        self._opposite_product = other_algebra
        other_algebra._opposite_product = self
        self._has_opposite = True
        other_algebra._has_opposite = True

        # set up coercions between ASB and BSA

        module_category=ModulesWithBasis(self.base_ring())

        other_to_self = SetMorphism(Hom(other_algebra, self, category=module_category), partial(self._the_coercion_map, BAmod, twist))
        other_to_self.register_as_coercion()

        self_to_other = SetMorphism(Hom(self, other_algebra, category=module_category), partial(other_algebra._the_coercion_map, ABmod, untwist))
        self_to_other.register_as_coercion()

    def opposite(self):
        r"""
        The smash product based on the other ordering of tensor factors.

        For a doctest, see :meth:`SmashProductAlgebraElement.to_opposite`
        """
        if not self._has_opposite:
            raise NotImplementedError, "Opposite smash product is not defined"
        return self._opposite_product

SmashProductAlgebra.Element = SmashProductAlgebraElement

