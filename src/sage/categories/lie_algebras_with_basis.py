r"""
Lie Algebras With Basis

AUTHORS:

- Travis Scrimshaw (07-15-2013): Initial implementation
"""
#*****************************************************************************
#  Copyright (C) 2013 Travis Scrimshaw <tscrim at ucdavis.edu>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#******************************************************************************

from sage.misc.abstract_method import abstract_method
from sage.misc.cachefunc import cached_method
from sage.categories.category_with_axiom import CategoryWithAxiom_over_base_ring
from sage.categories.lie_algebras import LieAlgebras
from sage.algebras.lie_algebras.lie_algebra_element import LieBracket

class LieAlgebrasWithBasis(CategoryWithAxiom_over_base_ring):
    """
    Category of Lie algebras with a basis.
    """
    _base_category_class_and_axiom = [LieAlgebras, "WithBasis"]

    class ParentMethods:
        def _basis_cmp(self, x, y):
            """
            Compare two basis element indices. The default is to call ``cmp``.
            """
            return cmp(x, y)

        @abstract_method(optional=True)
        def bracket_on_basis(self, x, y):
            """
            Return the bracket of basis elements indexed by ``x`` and ``y``
            where ``x < y``. If this is not implemented, then the method
            ``_bracket_()`` for the elements must be overwritten.
            """

        def pbw_basis(self, basis_indices=None, basis_cmp=None, **kwds):
            """
            Return the Poincare-Birkhoff-Witt basis of the universal
            enveloping algebra corresponding to ``self``.

            .. TODO::

                Check that this works in the infinite dimensional case.
            """
            if basis_cmp is None:
                basis_cmp = self._basis_cmp
            from sage.algebras.lie_algebras.poincare_birkhoff_witt \
                import PoincareBirkhoffWittBasis
            return PoincareBirkhoffWittBasis(self, basis_indices, basis_cmp, **kwds)

        poincare_birkhoff_witt_basis = pbw_basis

        _construct_UEA = pbw_basis

        def free_module(self):
            """
            Return ``self`` as a free module.
            """
            from sage.combinat.free_module import CombinatorialFreeModule
            try:
                # Try to see if it has an indexing set
                return CombinatorialFreeModule(self.base_ring(), self.basis().keys())
            except AttributeError:
                # Otherwise just index by the basis of ``self`` as a fallback
                return CombinatorialFreeModule(self.base_ring(), self.basis())

    class ElementMethods:
        def _bracket_(self, y):
            """
            Return the Lie bracket of ``[self, y]``.
            """
            P = self.parent()
            def term(ml,mr):
                comp = P._basis_cmp(ml,mr)
                if comp == 0:
                    return P.zero()
                if comp < 0:
                    return P.bracket_on_basis(ml, mr)
                return -P.bracket_on_basis(mr, ml)
            return P.sum(cl*cr * term(ml,mr) for ml,cl in self for mr,cr in y)

