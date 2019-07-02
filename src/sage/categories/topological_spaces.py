r"""
Topological Spaces
"""
#*****************************************************************************
#  Copyright (C) 2015 Travis Scrimshaw <tscrim at ucdavis.edu>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#******************************************************************************

from sage.misc.cachefunc import cached_method
from sage.categories.category_with_axiom import CategoryWithAxiom
from sage.categories.covariant_functorial_construction import RegressiveCovariantConstructionCategory
from sage.categories.sets_cat import Sets

class TopologicalSpacesCategory(RegressiveCovariantConstructionCategory):

    _functor_category = "Topological"

    def _repr_object_names(self):
        """
        EXAMPLES::

            sage: Groups().Topological()  # indirect doctest
            Category of topological groups
        """
        return "topological {}".format(self.base_category()._repr_object_names())

class TopologicalSpaces(TopologicalSpacesCategory):
    """
    The category of topological spaces.

    EXAMPLES::

        sage: Sets().Topological()
        Category of topological spaces
        sage: Sets().Topological().super_categories()
        [Category of sets]

    The category of topological spaces defines the topological structure,
    which shall be preserved by morphisms::

        sage: Sets().Topological().additional_structure()
        Category of topological spaces

    TESTS::

        sage: TestSuite(Sets().Topological()).run()
    """
    # We must override the general object because the names don't match
    _base_category_class = (Sets,)

    def _repr_object_names(self):
        """
        EXAMPLES::

            sage: Sets().Topological()  # indirect doctest
            Category of topological spaces
        """
        return "topological spaces"

    class SubcategoryMethods:
        @cached_method
        def Connected(self):
            """
            Return the full subcategory of the connected objects of ``self``.

            EXAMPLES::

                sage: Sets().Topological().Connected()
                Category of connected topological spaces

            TESTS::

                sage: Sets().Topological().Connected.__module__
                'sage.categories.topological_spaces'
                sage: TestSuite(Sets().Topological().Connected()).run()
            """
            return self._with_axiom('Connected')

        @cached_method
        def Compact(self):
            """
            Return the subcategory of the compact objects of ``self``.

            EXAMPLES::

                sage: Sets().Topological().Compact()
                Category of compact topological spaces

            TESTS::

                sage: Sets().Topological().Compact.__module__
                'sage.categories.topological_spaces'
                sage: TestSuite(Sets().Topological().Compact()).run()
            """
            return self._with_axiom('Compact')

    class Connected(CategoryWithAxiom):
        """
        The category of connected topological spaces.
        """

    class Compact(CategoryWithAxiom):
        """
        The category of compact topological spaces.
        """

