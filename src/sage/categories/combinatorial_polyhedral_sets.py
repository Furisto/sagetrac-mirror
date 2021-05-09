r"""
Category of sets of combinatorial polyhedra
"""

# ****************************************************************************
#       Copyright (C) 2021 Matthias Koeppe <mkoeppe@math.ucdavis.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  https://www.gnu.org/licenses/
# ****************************************************************************

from sage.misc.cachefunc import cached_method
from .category_singleton import Category_singleton
from .sets_cat import Sets

class CombinatorialPolyhedralSets(Category_singleton):
    r"""
    The category of sets of combinatorial polyhedra.

    A set of combinatorial polyhedra, finite or infinite, is a parent.

    A combinatorial polyhedron is an element.

    EXAMPLES::

        sage: from sage.categories.combinatorial_polyhedral_sets import CombinatorialPolyhedralSets
        sage: C = CombinatorialPolyhedralSets(); C
        Category of combinatorial polyhedral sets

    TESTS::

        sage: TestSuite(C).run()
    """

    @cached_method
    def super_categories(self):
        """
        Return the super categories of ``self``.

        EXAMPLES::

            sage: from sage.categories.combinatorial_polyhedral_sets import CombinatorialPolyhedralSets
            sage: CombinatorialPolyhedralSets().super_categories()
            [Category of sets]
        """
        return [Sets()]
