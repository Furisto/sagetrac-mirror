"""
Affine Lie Algebras

AUTHORS:

- Travis Scrimshaw (2013-05-03): Initial version

EXAMPLES::
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

from sage.misc.cachefunc import cached_method
from sage.misc.misc import repr_lincomb
from sage.structure.element import RingElement
from sage.categories.lie_algebras import LieAlgebras

from sage.algebras.lie_algebras.lie_algebra import FinitelyGeneratedLieAlgebra
from sage.algebras.lie_algebras.lie_algebra_element import LieAlgebraElement
from sage.combinat.root_system.cartan_type import CartanType
from sage.combinat.root_system.cartan_matrix import CartanMatrix
from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing
from sage.sets.family import Family

class AffineLieAlgebra(FinitelyGeneratedLieAlgebra):
    r"""
    An (untwisted) affine Lie algebra.

    Given a finite dimensional simple Lie algebra `\mathfrak{g}` over `R`,
    we construct an affine Lie algebra `\widehat{\mathfrak{g}}^{\prime}` as

    .. MATH::

        \widehat{\mathfrak{g}}^{\prime} = \left( \mathfrak{g} \otimes
        R[t, t^{-1}] \right) \oplus R c

    where `c` is the canonical central element and `R[t, t^{-1}]` is the
    Laurent polynomial ring over `R`. We define the Lie bracket as

    .. MATH::

        [a \otimes t^n + \alpha c, b \otimes t^m + \beta c] =
        [a, b] \otimes t^{n+m} + \delta_{n+m,0} ( a | b ) n c

    where `( a | b )` is the Killing form on `\mathfrak{g}`.

    There is a canonical derivative on `\widehat{\mathfrak{g}}^{\prime}`
    which is known as the *Lie derivative* and is denoted by `\delta`.
    The Lie derivative is defined as

    .. MATH::

        \delta(a \otimes t^m + \alpha c) = a \otimes m t^m,

    or equivalently by `\delta = t \frac{d}{dt}`.

    We can form the affine Kac-Moody algebra `\widehat{\mathfrak{g}}`
    by adding the additional generator `d` such that `[d, x] = \delta(x)`
    where `\delta` is the Lie derivative. We note that the derived subalgebra
    of the Kac-Moody algebra is the affine Lie algebra.
    """
    @staticmethod
    def __classcall_private__(cls, arg0, kac_moody=False, cartan_type=None):
        """
        Parse input to ensure a unique representation.

        INPUT:

        - ``arg0`` -- a simple Lie algebra or a base ring
        - ``cartan_type`` -- a Cartan type

        EXAMPLES::

            sage: from sage.algebras.lie_algebras.classical_lie_algebra import ClassicalMatrixLieAlgebra
            sage: ClassicalMatrixLieAlgebra(QQ, ['A', 4])
            Special linear Lie algebra of rank 5 over Rational Field
            sage: ClassicalMatrixLieAlgebra(QQ, CartanType(['B',4]))
            Special orthogonal Lie algebra of rank 9 over Rational Field
            sage: ClassicalMatrixLieAlgebra(QQ, 'C4')
            Symplectic Lie algebra of rank 8 over Rational Field
            sage: ClassicalMatrixLieAlgebra(QQ, cartan_type=['D',4])
            Special orthogonal Lie algebra of rank 8 over Rational Field
        """
        if isinstance(arg0, LieAlgebra):
            ct = arg0.cartan_type()
            if not ct.is_finite():
                raise ValueError("the base Lie algebra is not simple")
            cartan_type = ct.affine()
            g = arg0
        else:
            cartan_type = CartanType(cartan_type)
            if not ct.is_affine():
                raise ValueError("the Cartan type must be affine")
            g = LieAlgebra(arg0, cartan_type=cartan_type.classical())

        if not cartan_type.is_untwisted_affine():
            raise NotImplementedError("only currently implemented for untwisted affine types")
        return super(AffineLieAlgebra, self).__classcall__(self, g, cartan_type, kac_moody)

    def __init__(self, g, cartan_type, kac_moody):
        """
        Initalize ``self``.
        """
        self._g = g
        self._cartan_type = cartan_type
        R = g.base_ring()
        names = list(g.variable_names()) + ['e0', 'f0', 'c']
        if kac_moody:
            names += ['d']
        self._kac_moody = kac_moody
        FinitelyGeneratedLieAlgebra.__init__(self, R, names, LieAlgebras(R))#.WithBasis())

    def _repr_(self):
        """
        Return a string representation of ``self``.
        """
        base = "Affine "
        rep = repr(self._g)
        if self._kac_moody:
            old_len = len(rep)
            rep = rep.replace("Lie", "Kac-Moody")
            if len(rep) == old_len: # We did not replace anything
                base += "Kac-Moody "
        return base + rep

    def derived_subalgebra(self):
        """
        Return the derived subalgebra of ``self``.
        """
        if self._kac_moody:
            return AffineLieAlgebra(self._g, False)
        raise NotImplementedError # I think this is self...

    def cartan_type(self):
        """
        Return the Cartan type of ``self``.
        """
        return self._cartan_type

    def classical(self):
        """
        Return the classical Lie algebra of ``self``.
        """
        return self._g

    def _construct_UEA(self):
        """
        Construct the universal enveloping algebra of ``self``.
        """
        # These are placeholders and will require something more complex
        if self._kac_moody:
            PolynomialRing(self._g.universal_enveloping_algebra(), 't,c,d')
        return PolynomialRing(self._g.universal_enveloping_algebra(), 't,c')

    def gen(self, i):
        """
        Return the `i`-th generator of ``self``.
        """
        n = self.ngens()
        if self._kac_moody:
            if i == n - 1:
                return self.element_class(self, {'d': 1})
            n -= 1
        # If it is a standard generator
        if i < n - 3:
            return self.element_class(self, {(self._g.gen(i), 0): 1})

        if i == n - 3: # e_0 = f_{\theta} t
            return self.element_class(self, {(self._g.highest_root_basis_elt(False), 1):1})
        if i == n - 2: # f_0 = e_{\theta} t^-1
            return self.element_class(self, {(self._g.highest_root_basis_elt(True), -1):1})

        if i == n - 1: # c
            return self.element_class(self, {'c': 1})
        raise ValueError("i is too large")

    # A summand is either pairs (a, i) where a is an element in the classical
    #   Lie algebra and i is in ZZ representing the power of t, or it's 'c'
    #   for the canonical central element.
    class Element(LieAlgebraElement):
        """
        Element of an affine Lie algebra.
        """
        def _bracket_(self, y):
            """
            Return the Lie bracket ``[self, y]``.
            """
            s_mon = sorted(self.list())
            y_mon = sorted(y.list())
            if not self or not y or s_mon == y_mon:
                return self.parent().zero()
            d = {}
            gd = self.parent()._g.gens_dict()
            for ml,cl in sorted(s_mon): # The left monomials
                for mr,cr in sorted(y_mon): # The right monomials
                    if ml == mr or ml == 'c' or mr == 'c':
                        continue
                    if ml == 'd' and mr != 'd' and mr[1] != 0:
                        d[mr] = cr * mr[1]
                        continue
                    if mr == 'd' and ml[1] != 0:
                        d[ml] = -cl * ml[1]
                        continue
                    gl,tl = ml
                    gr,tr = mr
                    b = gl._bracket_(gr)
                    if b:
                        for m, c in b:
                            d[(gd[m], tl+tr)] = cl * cr * c
                    if tl != 0 and tr + tl == 0:
                        d['c'] = gl.killing_form(gr) * cl * cr * tl
            if len(d) == 0:
                return self.parent().zero()
            return self.__class__(self.parent(), d)

        def lie_derivative(self):
            r"""
            Return the Lie derivative `\delta` applied to ``self``.

            The Lie derivative `\delta` is defined as

            .. MATH::

                \delta(a \otimes t^m + \alpha c) = a \otimes m t^m.

            Another formulation is by `\delta = t \frac{d}{dt}`.
            """
            d = {}
            for m, c in self.list():
                if m != 'c' and m[1] != 0:
                    d[m] = c*m[1]
            return self.__class__(self.parent(), d)

