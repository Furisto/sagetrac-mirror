# -*- coding: utf-8 -*-
r"""
The fundamental basis of PBT Hopf algebra.
"""
#*****************************************************************************
#       Copyright (C) 2012 Jean-Baptiste Priez <jbp@kerios.fr>.
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#    This code is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    General Public License for more details.
#
#  The full text of the GPL is available at:
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************
from sage.combinat.cha.pbt import PlanarBinaryTreeFunctions
from tree_shuffle_product import TreeShuffleProduct


class Fundamental(PlanarBinaryTreeFunctions.Bases.Base):
        '''
        This is the fundamental basis of ``PBT``

        EXAMPLES::

            sage: P = PBT(QQ).P()
            The combinatorial Hopf algebra of Free Quasi-Symmetric Functions over the Rational Field in the realization Fundamental

        .. MATH::

            \mathbf{P}_{T} =
            \sum_{\sigma\in \mathfrak{S}; BST(\sigma) = T} \mathbf{F}_\sigma

        where `(\mathbf{F}_\sigma)` is the fundamental basis of ``FQSym``.

        The product of `(\mathbf{P}_T)_{T}` is described by

        .. MATH::

            \mathbf{P}_{T'} \\times \mathbf{P}_{T''} =
            \sum_{T\in T' \bullet T''} \mathbf{F}_{\gamma}

        where `T' \bullet T''` is the shuffle of trees:

        .. MATH::

            T' \bullet T'' := T_1' \wedge (T_2' \bullet T'') +
            (T' \bullet T_1'') \wedge T_2''

        with `T' := T_1' \wedge T_2'` and `T'' := T_1'' \wedge T_2''`.

        EXAMPLES::

            P  *  P    = P      + P     + P      + P        + P      + P
             o       o    o        o         o        o          o           o
              \     /      \        \         \      /          /           /
               o   o        o        o         o    o          o          _o_
                    \        \      /         /      \          \        /   \
                     o        o    o         o        o          o      o     o
                             /      \       / \        \        / \      \
                            o        o     o   o        o      o   o      o
                             \        \                   \
                              o        o                   o

        And the coproduct is described by

        .. MATH::

            \Delta(\mathbf{P}_{T}) =
            \sum_{i\in [n]} \mathbb{F}_{\sigma_{\mid i[}} \otimes
            \mathbb{F}_{\sigma_{\mid [i}}

        where `[n] := [1,..,n]`, `i[` is the sub-interval of `[n]` defined
        by `[1,..,i-1]` and `[i` the sub-interval defined by `[i,..,n]`.

        EXAMPLES::

            sage: F[3,1,2,4].coproduct()
            F[] # F[3, 1, 2, 4] + F[1] # F[1, 2, 3] + F[2, 1] # F[1, 2] + F[3, 1, 2] # F[1] + F[3, 1, 2, 4] # F[]

        (See [MalReut]_ and [NCSF-VI]_.)

        EXAMPLES::

            sage: F().antipode()
            0
            sage: F[[]].antipode()
            F[]
            sage: F[1].antipode()
            -F[1]
            sage: F[1, 2].antipode()
            F[2, 1]
            sage: F[2, 1].antipode()
            F[1, 2]

        TESTS::

            sage: F = FQSym(QQ).F(); F
            Hopf algebra of Free Quasi-Symmetric Functions over the Rational Field in the Fundamental basis
            sage: TestSuite(F).run()
        '''
        _prefix = "P"

        def build_morphisms(self):
            self.morph_P_to_F_FQSym()

        def morph_P_to_F_FQSym(self):
            '''
            TEST::

                sage: P = PBT(QQ).P()
                sage: F = FQSym(QQ).F()
                sage: F(P[3,1,2])
                F[1, 3, 2] + F[3, 1, 2]
            '''
            from sage.combinat.cha.all import FQSym

            # fundamental basis of PBT to fundamental basis of FQSym
            F = FQSym(self.base()).F()
            self.module_morphism(
                on_basis=lambda bt: F.sum_of_monomials(
                    self.realization_of().sylvester_class(bt)
                ), codomain=F
            ).register_as_coercion()

        def dual_basis(self):
            return self.realization_of().Q()

        def product_on_basis(self, bt1, bt2):
            r"""
            The product of the P basis : shuffle of tree

            TESTS::

                sage: P = PBT(QQ).P()
                sage: P[4,2,1,3]*P[3,1,2]
                P[2, 1, 5, 7, 6, 4, 3] + P[2, 1, 5, 4, 7, 6, 3] + P[2, 1, 4, 5, 7, 6, 3] + P[2, 1, 5, 4, 3, 7, 6] + P[2, 1, 4, 5, 3, 7, 6] + P[2, 1, 4, 3, 5, 7, 6]

            """
            return self.sum_of_monomials(
                bt for bt in TreeShuffleProduct(bt1, bt2))

        def coproduct_on_basis(self, bt):
            r"""
            The coproduct of the P basis : deconcatenation of tree

            TESTS::

                sage: P = PBT(QQ).P()
                sage: P[[]].coproduct()
                P[] # P[]
                sage: P[1].coproduct()
                P[] # P[1] + P[1] # P[]
                sage: P[1,3,2].coproduct()
                P[] # P[1, 3, 2] + P[1] # P[2, 1] + P[1] # P[1, 2] + P[2, 1] # P[1] + P[1, 2] # P[1] + P[1, 3, 2] # P[]

            EXAMPLES::

                sage: P = PBT(QQ).P()
                sage: P[4,2,1,3].coproduct()
                P[] # P[2, 1, 4, 3] + P[1] # P[1, 3, 2] + P[1] # P[2, 1, 3] + P[2, 1] # P[2, 1] + P[2, 1] # P[1, 2] + P[3, 2, 1] # P[1] + P[2, 3, 1] # P[1] + P[1, 2] # P[1, 2] + P[2, 1, 3] # P[1] + P[2, 1, 4, 3] # P[]
            """
            from sage.categories.tensor import tensor

            def extract_sub_tree_from_root(bt):
                B = self.indices()
                if bt.is_empty():
                    yield ([], bt)
                    return
                yield ([bt], B())
                for (l0, b0) in extract_sub_tree_from_root(bt[0]):
                    for (l1, b1) in extract_sub_tree_from_root(bt[1]):
                        yield (l0 + l1, B([b0, b1]))
            return self.tensor_square().sum(
                map(lambda (li, bt): tensor(
                    [self.prod(map(self.monomial, li)),
                     self.monomial(bt)]),
                    extract_sub_tree_from_root(bt)))

        def left_product_on_basis(self, t1, t2):
            '''
            TESTS::

                sage: P = PBT(QQ).P()
                sage: P[1] << P[1]
                P[1, 2]
                sage: P[1] << P[[]]
                P[1]
                sage: P[[]] << P[1]
                0
                sage: b1 = BinaryTrees(4).random_element()
                sage: b2 = BinaryTrees(7).random_element()
                sage: (P(b1)<<P(b2)) + (P(b1)>>P(b2)) == P(b1) * P(b2)
                True
            '''
            if t1.is_empty():
                return self.zero()
            if t2.is_empty():
                return self.monomial(t1)

            B = self.basis().keys()
            return self.sum_of_monomials(
                B([t1[0], t]) for t in TreeShuffleProduct(t1[1], t2)
            )

        def right_product_on_basis(self, t1, t2):
            '''
            TESTS::

                sage: P = PBT(QQ).P()
                sage: P[1] >> P[1]
                P[1, 2]
                sage: P[1] >> P[[]]
                0
                sage: P[[]] >> P[1]
                P[1]
                sage: b1 = BinaryTrees(4).random_element()
                sage: b2 = BinaryTrees(7).random_element()
                sage: (P(b1)<<P(b2)) + (P(b1)>>P(b2)) == P(b1) * P(b2)
                True
            '''
            if t1.is_empty():
                return self.monomial(t2)
            if t2.is_empty():
                return self.zero()

            B = self.basis().keys()
            return self.sum_of_monomials(
                B([t, t2[1]]) for t in TreeShuffleProduct(t1, t2[0])
            )

        def left_coproduct_on_basis(self, t):
            pass

        def right_coproduct_on_basis(self, t):
            pass
