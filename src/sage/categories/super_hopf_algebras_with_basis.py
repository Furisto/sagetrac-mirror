r"""
Super Hopf algebras with basis
"""
#*****************************************************************************
#  Copyright (C) 2015 Travis Scrimshaw <tscrim at ucdavis.edu>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#******************************************************************************

from sage.categories.super_modules import SuperModulesCategory

class SuperHopfAlgebrasWithBasis(SuperModulesCategory):
    """
    The category of super Hopf algebras with a distinguished basis.

    EXAMPLES::

        sage: C = HopfAlgebras(ZZ).WithBasis().Super(); C
        Category of super hopf algebras with basis over Integer Ring
        sage: sorted(C.super_categories(), key=str)
        [Category of graded hopf algebras with basis over Integer Ring,
         Category of super algebras with basis over Integer Ring,
         Category of super coalgebras with basis over Integer Ring,
         Category of super hopf algebras over Integer Ring]

    TESTS::

        sage: TestSuite(C).run()
    """
    def extra_super_categories(self):
        """
        EXAMPLES::

            sage: from sage.categories.super_hopf_algebras_with_basis import SuperHopfAlgebrasWithBasis
            sage: SuperHopfAlgebrasWithBasis(QQ).extra_super_categories()
            [Category of graded hopf algebras with basis over Rational Field]
        """
        return [self.base_category().Graded()]

    class ParentMethods:

        def _test_antipode(self, **options):
            r"""
            Test the antipode.

            An *antipode* `S` of a (super) Hopf algebra is a linear
            endomorphism of the Hopf algebra that satisfies the
            following conditions (see :wikipedia:`HopfAlgebra`).

            - If `\mu` and `\Delta` denote the product and coproduct of the
              Hopf algebra, respectively, then `S` satisfies

              .. MATH::

                  \mu \circ (S \tensor 1) \circ \Delta = unit \circ counit
                  \mu \circ (1 \tensor S) \circ \Delta = unit \circ counit

            - `S` is an *anti*-homomorphism:

               .. MATH::

                   S(ab) = (-1)^{\deg a \deg b} S(b) S(a)

               for homogeneous `a` and `b`.

            These properties are tested on :meth:`some_elements`.

            TESTS::

                sage: A = SteenrodAlgebra(7)
                sage: A._test_antipode()
            """
            tester = self._tester(**options)

            S = self.antipode

            IS = lambda x: self.sum(c * self.monomial(t1) * S(self.monomial(t2))
                                for ((t1, t2), c) in x.coproduct())

            SI = lambda x: self.sum(c * S(self.monomial(t1)) * self.monomial(t2)
                                for ((t1, t2), c) in x.coproduct())

            for x in tester.some_elements():
                x_even = x.even_component()
                x_odd = x.odd_component()
                for y in tester.some_elements():
                    y_even = y.even_component()
                    y_odd = y.odd_component()

                    # The antipode is a graded anti-homomorphism.
                    tester.assertTrue(S(x_even) * S(y_even) == S(y_even * x_even))
                    tester.assertTrue(S(x_even) * S(y_odd) == S(y_odd * x_even))
                    tester.assertTrue(S(x_odd) * S(y_even) == S(y_even * x_odd))
                    tester.assertTrue(S(x_odd) * S(y_odd) == -S(y_odd * x_odd))

                # mu * (S # I) * delta == counit * unit
                tester.assertTrue(SI(x) == self.counit(x) * self.one())

                # mu * (I # S) * delta == counit * unit
                tester.assertTrue(IS(x) == self.counit(x) * self.one())

