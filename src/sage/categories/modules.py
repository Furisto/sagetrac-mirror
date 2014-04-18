r"""
Modules
"""
#*****************************************************************************
#  Copyright (C) 2005      David Kohel <kohel@maths.usyd.edu>
#                          William Stein <wstein@math.ucsd.edu>
#                2008      Teresa Gomez-Diaz (CNRS) <Teresa.Gomez-Diaz@univ-mlv.fr>
#                2008-2011 Nicolas M. Thiery <nthiery at users.sf.net>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#******************************************************************************

from sage.misc.cachefunc import cached_method
from sage.misc.lazy_import import LazyImport
from sage.categories.category_with_axiom import CategoryWithAxiom_over_base_ring
from sage.categories.category import HomCategory
from category import JoinCategory
from category_types import Category_module, Category_over_base_ring
from tensor import TensorProductsCategory
from dual import DualObjectsCategory
from sage.categories.sets_cat import Sets
from sage.categories.bimodules import Bimodules
from sage.categories.fields import Fields
_Fields = Fields()

class Modules(Category_module):
    r"""
    The category of all modules over a base ring `R`

    A `R`-module `M` is a left and right `R`-module over a commutative
    ring `R` such that:

    .. math::  r*(x*s) = (r*x)*s \qquad  \forall r,s \in R \text{ and } x\in M

    INPUT:

      - ``base_ring`` -- a ring `R`
      - ``dispatch`` -- a boolean (for internal use; default: ``True``)

    When the base ring is a field, the category of vector spaces is
    returned instead (unless ``dispatch == False``).

    EXAMPLES::

        sage: Modules(ZZ)
        Category of modules over Integer Ring
        sage: Modules(QQ)
        Category of vector spaces over Rational Field

        sage: Modules(Integers(9))
        Category of modules over Ring of integers modulo 9

        sage: Modules(Integers(9)).super_categories()
        [Category of bimodules over Ring of integers modulo 9 on the left and Ring of integers modulo 9 on the right]

        sage: Modules(ZZ).super_categories()
        [Category of bimodules over Integer Ring on the left and Integer Ring on the right]

        sage: Modules == RingModules
        True

        sage: Modules(ZZ[x]).is_abelian()   # see #6081
        True

    TESTS::

        sage: TestSuite(Modules(ZZ)).run()

    TODO:

     - Implement a FreeModules(R) category, when so prompted by a concrete use case
    """

    @staticmethod
    def __classcall_private__(cls, base_ring, dispatch = True):
        """
        This method implements the default behavior of dispatching
        ``Modules(field)`` to ``VectorSpaces(field)``. This feature
        will later be extended to modules over a principal ideal
        domain/ring or over a semiring.

        TESTS::

            sage: C = Modules(ZZ); C
            Category of modules over Integer Ring
            sage: C is Modules(ZZ, dispatch = False)
            True
            sage: C is Modules(ZZ, dispatch = True)
            True
            sage: C._reduction
            (<class 'sage.categories.modules.Modules'>, (Integer Ring,), {'dispatch': False})
            sage: TestSuite(C).run()

            sage: Modules(QQ) is VectorSpaces(QQ)
            True
            sage: Modules(QQ, dispatch = True) is VectorSpaces(QQ)
            True

            sage: C = Modules(NonNegativeIntegers()); C   # todo: not implemented
            Category of semiring modules over Non negative integers

            sage: C = Modules(QQ, dispatch = False); C
            Category of modules over Rational Field
            sage: C._reduction
            (<class 'sage.categories.modules.Modules'>, (Rational Field,), {'dispatch': False})
            sage: TestSuite(C).run()

        """
        if dispatch:
            if base_ring in _Fields:
                from vector_spaces import VectorSpaces
                return VectorSpaces(base_ring, check=False)
        result = super(Modules, cls).__classcall__(cls, base_ring)
        result._reduction[2]['dispatch'] = False
        return result

    def super_categories(self):
        """
        EXAMPLES::

            sage: Modules(ZZ).super_categories()
            [Category of bimodules over Integer Ring on the left and Integer Ring on the right]

        Nota bene::

            sage: Modules(QQ)
            Category of vector spaces over Rational Field
            sage: Modules(QQ).super_categories()
            [Category of modules over Rational Field]
        """
        R = self.base_ring()
        return [Bimodules(R,R)]

    class SubcategoryMethods:

        @cached_method
        def base_ring(self):
            """
            Return the base ring for ``self``.

            This implements a ``base_ring`` method for join categories
            which are subcategories of some ``Modules(K)``.

            .. NOTE::

                - This uses the fact that join categories are
                  flattened; thus some direct subcategory of
                  ``self`` should be a category over a base ring.
                - Generalize this to any :class:`Category_over_base_ring`.
                - Should this code be in :class:`JoinCategory`?
                - This assumes that a subcategory of a
                  :class`~.category_types.Category_over_base_ring` is a
                  :class:`~.category.JoinCategory` or a
                  :class`~.category_types.Category_over_base_ring`.

            EXAMPLES::

                sage: C = Modules(QQ) & Semigroups(); C
                Join of Category of semigroups and Category of vector spaces over Rational Field
                sage: C.base_ring()
                Rational Field
                sage: C.base_ring.__module__
                'sage.categories.modules'
            """
            assert isinstance(self, JoinCategory)
            for x in self.super_categories():
                if isinstance(x, Category_over_base_ring):
                    return x.base_ring()
            assert False, "some subcategory of %s should be a category over base ring"%self

        def TensorProducts(self):
            r"""
            Return the full subcategory of objects of ``self`` constructed as tensor products.

            .. SEEALSO::

                - :class:`.tensor.TensorProductsCategory`
                - :class:`~.covariant_functorial_construction.RegressiveCovariantFunctorialConstruction`.

            EXAMPLES::

                sage: ModulesWithBasis(QQ).TensorProducts()
                Category of tensor products of modules with basis over Rational Field
            """
            return TensorProductsCategory.category_of(self)

        @cached_method
        def DualObjects(self):
            r"""
            Return the category of duals of objects of ``self``.

            The dual of a vector space `V` is the space consisting of
            all linear functionals on `V` (see :wikipedia:`Dual_space`).
            Additional structure on `V` can endow its dual with
            additional structure; e.g. if `V` is an algebra, then its
            dual is a coalgebra.

            This returns the category of dual of spaces in ``self`` endowed
            with the appropriate additional structure.

            .. SEEALSO::

                - :class:`.dual.DualObjectsCategory`
                - :class:`~.covariant_functorial_construction.CovariantFunctorialConstruction`.

            .. TODO:: add support for graded duals.

            EXAMPLES::

                sage: VectorSpaces(QQ).DualObjects()
                Category of duals of vector spaces over Rational Field

            The dual of a vector space is a vector space::

                sage: VectorSpaces(QQ).DualObjects().super_categories()
                [Category of vector spaces over Rational Field]

            The dual of an algebra is a coalgebra::

                sage: sorted(Algebras(QQ).DualObjects().super_categories(), key=str)
                [Category of coalgebras over Rational Field,
                 Category of duals of vector spaces over Rational Field]

            The dual of a coalgebra is an algebra::

                sage: sorted(Coalgebras(QQ).DualObjects().super_categories(), key=str)
                [Category of algebras over Rational Field,
                 Category of duals of vector spaces over Rational Field]

            As a shorthand, this category can be accessed with the
            :meth:`~Modules.SubcategoryMethods.dual` method::

                sage: VectorSpaces(QQ).dual()
                Category of duals of vector spaces over Rational Field

            TESTS::

                sage: C = VectorSpaces(QQ).DualObjects()
                sage: C.base_category()
                Category of vector spaces over Rational Field
                sage: C.super_categories()
                [Category of vector spaces over Rational Field]
                sage: latex(C)
                \mathbf{DualObjects}(\mathbf{VectorSpaces}_{\Bold{Q}})
                sage: TestSuite(C).run()
            """
            return DualObjectsCategory.category_of(self)

        dual = DualObjects

        @cached_method
        def FiniteDimensional(self):
            r"""
            Return the full subcategory of the finite dimensional objects of ``self``.

            EXAMPLES::

                sage: Modules(ZZ).FiniteDimensional()
                Category of finite dimensional modules over Integer Ring
                sage: Coalgebras(QQ).FiniteDimensional()
                Category of finite dimensional coalgebras over Rational Field
                sage: AlgebrasWithBasis(QQ).FiniteDimensional()
                Category of finite dimensional algebras with basis over Rational Field

            TESTS::

                sage: TestSuite(Modules(ZZ).FiniteDimensional()).run()
                sage: Coalgebras(QQ).FiniteDimensional.__module__
                'sage.categories.modules'
            """
            return self._with_axiom("FiniteDimensional")

        @cached_method
        def Graded(self, base_ring=None):
            r"""
            Return the subcategory of the graded objects of ``self``.

            INPUT::

            - ``base_ring`` -- this is ignored

            EXAMPLES::

                sage: Modules(ZZ).Graded()
                Category of graded modules over Integer Ring

                sage: Coalgebras(QQ).Graded()
                Join of Category of graded modules over Rational Field and Category of coalgebras over Rational Field

                sage: AlgebrasWithBasis(QQ).Graded()
                Category of graded algebras with basis over Rational Field

            .. TODO::

                - Explain why this does not commute with :meth:`WithBasis`
                - Improve the support for covariant functorial
                  constructions categories over a base ring so as to
                  get rid of the ``base_ring`` argument.

            TESTS::

                sage: Coalgebras(QQ).Graded.__module__
                'sage.categories.modules'
            """
            assert base_ring is None or base_ring is self.base_ring()
            from sage.categories.graded_modules import GradedModulesCategory
            return GradedModulesCategory.category_of(self)

        @cached_method
        def WithBasis(self):
            r"""
            Return the full subcategory of the finite dimensional objects of ``self``.

            EXAMPLES::

                sage: Modules(ZZ).WithBasis()
                Category of modules with basis over Integer Ring
                sage: Coalgebras(QQ).WithBasis()
                Category of coalgebras with basis over Rational Field
                sage: AlgebrasWithBasis(QQ).WithBasis()
                Category of algebras with basis over Rational Field

            TESTS::

                sage: TestSuite(Modules(ZZ).WithBasis()).run()
                sage: Coalgebras(QQ).WithBasis.__module__
                'sage.categories.modules'
            """
            return self._with_axiom("WithBasis")

    class FiniteDimensional(CategoryWithAxiom_over_base_ring):

        def extra_super_categories(self):
            """
            Implements the fact that a finite dimensional module over a finite ring is finite

            EXAMPLES::

                sage: Modules(IntegerModRing(4)).FiniteDimensional().extra_super_categories()
                [Category of finite sets]
                sage: Modules(ZZ).FiniteDimensional().extra_super_categories()
                []
                sage: Modules(GF(5)).FiniteDimensional().is_subcategory(Sets().Finite())
                True
                sage: Modules(ZZ).FiniteDimensional().is_subcategory(Sets().Finite())
                False
            """
            if self.base_ring() in Sets().Finite():
                return [Sets().Finite()]
            else:
                return []

    Graded = LazyImport('sage.categories.graded_modules', 'GradedModules')
    WithBasis = LazyImport('sage.categories.modules_with_basis', 'ModulesWithBasis')

    class ParentMethods:
        pass

    class ElementMethods:

        def __mul__(left, right):
            """
            TESTS::

                sage: F = CombinatorialFreeModule(QQ, ["a", "b"])
                sage: x = F.monomial("a")
                sage: x * int(2)
                2*B['a']

            TODO: make a better unit test once Modules().example() is implemented
            """
            from sage.structure.element import get_coercion_model
            import operator
            return get_coercion_model().bin_op(left, right, operator.mul)

        def __rmul__(right, left):
            """
            TESTS::

                sage: F = CombinatorialFreeModule(QQ, ["a", "b"])
                sage: x = F.monomial("a")
                sage: int(2) * x
                2*B['a']

            TODO: make a better unit test once Modules().example() is implemented
            """
            from sage.structure.element import get_coercion_model
            import operator
            return get_coercion_model().bin_op(left, right, operator.mul)


    class HomCategory(HomCategory):
        """
        The category of homomorphisms sets `\hom(X,Y)` for `X`, `Y` modules
        """

        def extra_super_categories(self):
            """
            EXAMPLES::

                sage: Modules(ZZ).hom_category().extra_super_categories()
                [Category of modules over Integer Ring]
            """
            return [Modules(self.base_category.base_ring())]

        class ParentMethods:

            @cached_method
            def zero(self):
                """
                EXAMPLES::

                    sage: E = CombinatorialFreeModule(ZZ, [1,2,3])
                    sage: F = CombinatorialFreeModule(ZZ, [2,3,4])
                    sage: H = Hom(E, F)
                    sage: f = H.zero()
                    sage: f
                    Generic morphism:
                      From: Free module generated by {1, 2, 3} over Integer Ring
                      To:   Free module generated by {2, 3, 4} over Integer Ring
                    sage: f(E.monomial(2))
                    0
                    sage: f(E.monomial(3)) == F.zero()
                    True

                TESTS:

                We check that ``H.zero()`` is picklable::

                    sage: loads(dumps(f.parent().zero()))
                    Generic morphism:
                      From: Free module generated by {1, 2, 3} over Integer Ring
                      To:   Free module generated by {2, 3, 4} over Integer Ring
                """
                from sage.misc.constant_function import ConstantFunction
                return self(ConstantFunction(self.codomain().zero()))

    class EndCategory(HomCategory):
        """
        The category of endomorphisms sets `End(X)` for `X` module (this is
        not used yet)
        """

        def extra_super_categories(self):
            """
            EXAMPLES::

                sage: Hom(ZZ^3, ZZ^3).category().extra_super_categories() # todo: not implemented
                [Category of algebras over Integer Ring]
            """
            from algebras import Algebras
            return [Algebras(self.base_category.base_ring())]
