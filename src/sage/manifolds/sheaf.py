r"""
Presheaves and Sheaves over Manifolds

AUTHORS:

- Michael Jung (2021): initial version

"""

#******************************************************************************
#       Copyright (C) 2021 Michael Jung <m.jung at vu.nl>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#  as published by the Free Software Foundation; either version 2 of
#  the License, or (at your option) any later version.
#                  http://www.gnu.org/licenses/
#******************************************************************************

from sage.structure.sage_object import SageObject
from sage.misc.abstract_method import abstract_method
from .manifold import TopologicalManifold

class Presheaf(SageObject):
    r"""

    """
    def __init__(self, manifold, section_set_constructor):
        r"""

        EXAMPLES::

            sage: from sage.manifolds.sheaf import Presheaf
            sage: M = Manifold(2, 'M')
            sage: F = Presheaf(M, lambda d: d.scalar_field_algebra()); F
            Presheaf of sections constructed by <function <lambda> at 0x7f4d179cbaf0>
             on the 2-dimensional differentiable manifold M
            sage: U = M.open_subset('U')
            sage: F(U)
            Algebra of differentiable scalar fields on the Open subset U of the
             2-dimensional differentiable manifold M

        """
        if not isinstance(manifold, TopologicalManifold):
            raise ValueError(f'{manifold} must be an instance of {TopologicalManifold}')
        self._manifold = manifold
        self._section_set_constructor = section_set_constructor

    def _repr_name_(self):
        r"""

        """
        return 'Presheaf'

    def _repr_(self):
        r"""
        Return the string representation of ``self``.

        """
        repr = f'{self._repr_name_()} of sections constructed '
        repr += f'by {self._section_set_constructor} on the {self._manifold}'
        return repr

    def __call__(self, open_subset):
        r"""
        Return the set of sections of ``self`` w.r.t. ``open_subset``.

        """
        if not open_subset.is_subset(self._manifold) or not open_subset.is_open():
            raise ValueError(f'{open_subset} must be an open subset of {self._manifold}')
        return self._section_set_constructor(open_subset)

    def section_set(self, open_subset):
        r"""
        Return the set of sections of ``self`` w.r.t. ``open_subset``.

        """
        return self(open_subset)

    def restriction_morphism(self, from_open_subset, to_open_subset):
        r"""
        Return the restriction morphism from ``from_open_subset`` to
        ``to_open_subset``.

        EXAMPLES::

            sage: from sage.manifolds.sheaf import Presheaf
            sage: M = Manifold(2, 'M')
            sage: F = Presheaf(M, lambda d: d.scalar_field_algebra())
            sage: U = M.open_subset('U')
            sage: F.restriction_morphism(M, U)
            Generic morphism:
              From: Algebra of differentiable scalar fields on the 2-dimensional differentiable manifold M
              To:   Algebra of differentiable scalar fields on the Open subset U of the 2-dimensional differentiable manifold M

        """
        if not from_open_subset.is_subset(self._manifold) or not from_open_subset.is_open():
            raise ValueError(f'{from_open_subset} must be an open subset of {self._manifold}')
        if not to_open_subset.is_subset(self._manifold) or not to_open_subset.is_open():
            raise ValueError(f'{to_open_subset} must be an open subset of {self._manifold}')
        from sage.categories.morphism import SetMorphism
        from sage.categories.homset import Hom
        from sage.categories.sets_cat import Sets
        sec_dom = self(from_open_subset)
        sec_codom = self(to_open_subset)
        return SetMorphism(Hom(sec_dom, sec_codom, Sets()),
                           lambda x: x.restrict(to_open_subset))

class Sheaf(Presheaf):
    r"""

    """
    def concatenation(self, *args, **kwargs):
        r"""
        Return the concatenation of a list of sections each defined on an open
        subset of an open covering of ``open_subset``.

        INPUT:

        - ``open_subset`` -- (default: ``None``) op

        """
        open_subset = kwargs.pop('open_subset', self._manifold)
        # compatibility check
        # ...
        # construct section from parts
        # ...
        pass

    def _repr_name_(self):
        r"""

        """
        return 'Sheaf'

class PresheafSection(SageObject):
    r"""

    """
    def __init__(self, domain):
        r"""

        """
        self._domain = domain

    def restrict(self, subdomain):
        r"""
        Return the restriction of ``self`` to ``subdomain``.

        """
        # try to get restriction from restriction graph
        # ...
        # if that fails, create restriction from scratch
        return self._construct_restriction_(subdomain)

    @abstract_method
    def _construct_restriction_(self, subdomain):
        r"""
        Construct a restriction of ``self`` to ``subdomain`` from scratch.

        """

class SheafSection(PresheafSection):
    r"""

    """
    def __eq__(self, other):
        r"""

        """
        if self is other:
            return True
        if self._domain != other._domain:
            return False
        # compare on open covers until hitting a subdomain on which the
        # sections are actually comparable (e.g. parallelizable subdomains for
        # tensor fields)
        return all(self.restrict(subdom) == other.restrict(subdom)
                   for subdom in self._domain.open_covers(trivial=False))