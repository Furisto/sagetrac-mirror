r"""
A minimal implementation of the divided power algebra as a graded Hopf
algebra with basis.

AUTHOR:

- Bruce Westbury
"""
#*****************************************************************************
#  Copyright (C) 2011 Bruce W. Westbury <brucewestbury@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#******************************************************************************
from sage.misc.cachefunc import cached_method
from sage.sets.family import Family
from sage.categories.all import GradedHopfAlgebrasWithBasis
from sage.combinat.free_module import CombinatorialFreeModule
from sage.categories.rings import Rings
from sage.sets.non_negative_integers import NonNegativeIntegers
from sage.rings.arith import binomial
from sage.rings.integer import Integer


class DividedPowerAlgebra(CombinatorialFreeModule):
    r"""
    An example of a graded Hopf algebra with basis: the divided power algebra
    in one variable.

    This class illustrates a minimal implementation of the divided
    power algebra.
    """
    def __init__(self, R):
        if not R in Rings():
            raise ValueError('R is not a ring')
        GHWBR = GradedHopfAlgebrasWithBasis(R)
        CombinatorialFreeModule.__init__(self, R, NonNegativeIntegers(),
                                         category=GHWBR)

    def _repr_(self):
        return "The divided power algebra over %s" % (self.base_ring())

    @cached_method
    def one(self):
        """
        Return the unit of the algebra
        as per :meth:`AlgebrasWithBasis.ParentMethods.one_basis`.

        EXAMPLES::

            sage: from sage.algebras.all import DividedPowerAlgebra
            sage: A = DividedPowerAlgebra(ZZ)
            sage: A.one()
            B[0]
        """
        u = NonNegativeIntegers.from_integer(0)
        return self.monomial(u)

    def product_on_basis(self, left, right):
        r"""
        Product, on basis elements

        As per :meth:`AlgebrasWithBasis.ParentMethods.product_on_basis`.

        INPUT:

        - ``left``, ``right`` - non-negative integers determining
          monomials (as the exponents of the generators) in this
          algebra

        OUTPUT:

        the product of the two corresponding monomials, as an element
        of ``self``.

        EXAMPLES::

            sage: from sage.algebras.all import DividedPowerAlgebra
            sage: B = DividedPowerAlgebra(ZZ).basis()
            sage: B[3]*B[4]
            35*B[7]
        """
        return self.term(left + right, binomial(left + right, left))

    def coproduct_on_basis(self, t):
        r"""
        Coproduct, on basis elements.

        EXAMPLES::

            sage: from sage.algebras.all import DividedPowerAlgebra
            sage: A = DividedPowerAlgebra(ZZ)
            sage: B = A.basis()
            sage: A.coproduct(B[4])
            B[0] # B[4] + B[1] # B[3] + B[2] # B[2] + B[3] # B[1] + B[4] # B[0]
            sage: A.coproduct(B[0])
            B[0] # B[0]
        """
        AA = self.tensor(self)
        return AA.sum_of_monomials(((k, t - k)
                                    for k in range(t + 1)))

    def counit_on_basis(self, t):
        """
        Counit, on basis elements.

        EXAMPLES::

            sage: from sage.algebras.all import DividedPowerAlgebra
            sage: A = DividedPowerAlgebra(ZZ)
            sage: B = A.basis()
            sage: A.counit(B[3])
            0
            sage: A.counit(B[0])
            1
        """
        if t == 0:
            return self.base_ring().one()

        return self.base_ring().zero()

    def antipode_on_basis(self, t):
        """
        Antipode, on basis elements.

        EXAMPLES::

            sage: from sage.algebras.all import DividedPowerAlgebra
            sage: A = DividedPowerAlgebra(ZZ)
            sage: B = A.basis()
            sage: A.antipode(B[4]+B[5])
            B[4] - B[5]
        """
        if t % 2 == 0:
            return self.monomial(t)

        return self.term(t, -1)

    def degree_on_basis(self, t):
        """
        The degree of the element determined by the integer ``t`` in
        this graded module.

        INPUT:

        - ``t`` -- the index of an element of the basis of this module,
          i.e. a non-negative integer

        OUTPUT:

        an integer, the degree of the corresponding basis element

        EXAMPLES::

            sage: from sage.algebras.all import DividedPowerAlgebra
            sage: A = DividedPowerAlgebra(ZZ)
            sage: A.degree_on_basis(3)
            3
            sage: type(A.degree_on_basis(2))
            <type 'sage.rings.integer.Integer'>
        """
        return Integer(t)

    @cached_method
    def algebra_generators(self):
        r"""
        The generators of this algebra

        As per :meth:`Algebras.ParentMethods.algebra_generators`.

        EXAMPLES::

            sage: from sage.algebras.all import DividedPowerAlgebra
            sage: A = DividedPowerAlgebra(ZZ)
            sage: A.algebra_generators()
            Family (Non negative integers)
        """
        return Family(NonNegativeIntegers())
