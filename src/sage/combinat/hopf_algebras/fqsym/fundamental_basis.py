# -*- coding: utf-8 -*-
r"""
The fundamental basis of FQSym Hopf algebra.

F-basis of FQSym
"""
#*****************************************************************************
#       Copyright (C) 2013 Jean-Baptiste Priez <jbp@kerios.fr>.
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************
from sage.combinat.hopf_algebras import register_as_realization
from sage.combinat.hopf_algebras.fqsym import FreeQuasiSymmetricFunctions
from sage.combinat.permutation import to_standard
from sage.combinat.shuffle import ShuffleProduct


class Fundamental(FreeQuasiSymmetricFunctions.Bases.Base):
    '''
    This is the fundamental basis of ``FQSym``:

    EXAMPLES::

        sage: F = FQSym(QQ).F();F
        The combinatorial Hopf algebra of Free Quasi-Symmetric Functions over the Rational Field on the Fundamental basis

    .. MATH::

        \mathbb{F}_{\sigma} = \sum_{w\in \mathfrak{A}^*; std(w) =
        \sigma^{-1}} w

    where `\mathfrak A` is an infinite and totally ordered alphabet such
    that `\mathfrak A^*` is free monoid. (``FQSym`` defined as a
    sub-algebra of the free algebra `\mathbb{K} \\langle \mathfrak{A}
    \\rangle`.)

    The product of `(\mathbb{F}_\sigma)_{\sigma\in\mathfrak{G}}` is
    described by

    .. MATH::

        \mathbb{F}_{\sigma} \\times \mathbb{F}_{\mu} =
        \sum_{\gamma \in \sigma \Cup \mu} \mathbb{F}_{\gamma}

    where `\sigma \Cup \mu` is the shifted shuffle of `\sigma` and `\mu`
    with. We denote by `std` the standardization map which  associate to a
    word `w` a permutation `\sigma` (see ``Permutations``).

    EXAMPLES::

        sage: F[1,2] * F[2,1]
        F[1, 2, 4, 3] + F[1, 4, 2, 3] + F[1, 4, 3, 2] + F[4, 1, 2, 3] + F[4, 1, 3, 2] + F[4, 3, 1, 2]

    And the coproduct is described by

    .. MATH::

        \Delta(\mathbb{F}_{\sigma}) =
        \sum_{i\in [n]} \mathbb{F}_{\sigma_{\mid i[}} \otimes
        \mathbb{F}_{\sigma_{\mid [i}}

    where `[n] := [1,..,n]`, `i[` is the sub-interval of `[n]` defined by
    `[1,..,i-1]` and `[i` the sub-interval defined by `[i,..,n]`.

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
        The combinatorial Hopf algebra of Free Quasi-Symmetric Functions over the Rational Field on the Fundamental basis
        sage: TestSuite(F).run()
    '''

    _prefix = "F"

    def dual_basis(self):
        return self.realization_of().G()

    def build_morphisms(self):
        self.morph_F_FQSym_to_F_QSym()

    def morph_F_FQSym_to_F_QSym(self):
        '''
        TESTS::

            sage: FQ = QuasiSymmetricFunctions(QQ).F()
            sage: F = FQSym(QQ).F()
            sage: FQ(F[2,1,3])
            F[1, 2]
            sage: FQ(F[2,1,3] * F[1,2,3]) == FQ(F[2,1,3]) * FQ(F[1,2,3])
            True
            sage: FQ(F[2,1,3] + F[3,1,2])
            2*F[1, 2]
        '''
        ###############################################
        # ## F-basis of FQSym to F-basis of QSym the fundamental basis
        # ## (Gessel)
        from sage.combinat.ncsf_qsym.qsym import QuasiSymmetricFunctions
        F = QuasiSymmetricFunctions(self.base()).F()
        self.module_morphism(
            on_basis=lambda sigma: F(sigma.descents_composition()),
            codomain=F
        ).register_as_coercion()
        ###############################################

    def product_on_basis(self, sigma, mu):
        '''
        TESTS::

            sage: F = FQSym(QQ).F()
            sage: p = Permutations(6).random_element()
            sage: F(p) * F[[]] == F[[]] * F(p) == F(p)
            True
            sage: F[1]**2 == F.sum(F(sigma) for sigma in Permutations(2))
            True
            sage: F[1]**3 == F.sum(F(sigma) for sigma in Permutations(3))
            True
            sage: F[1] * F[2, 1, 3]
            F[1, 3, 2, 4] + F[3, 1, 2, 4] + F[3, 2, 1, 4] + F[3, 2, 4, 1]
            sage: F[1, 2] * F[2, 1]
            F[1, 2, 4, 3] + F[1, 4, 2, 3] + F[1, 4, 3, 2] + F[4, 1, 2, 3] + F[4, 1, 3, 2] + F[4, 3, 1, 2]
        '''
        return self.sum_of_monomials(sigma.shifted_shuffle(mu))

    def coproduct_on_basis(self, sigma):
        '''
        TESTS::

            sage: F = FQSym(ZZ).F()
            sage: F[[]].coproduct()
            F[] # F[]
            sage: F[1].coproduct()
            F[] # F[1] + F[1] # F[]
            sage: F[1, 2].coproduct()
            F[] # F[1, 2] + F[1] # F[1] + F[1, 2] # F[]
            sage: ( F[1, 2] - F[2, 1] ).coproduct()
            F[] # F[1, 2] - F[] # F[2, 1] + F[1, 2] # F[] - F[2, 1] # F[]
        '''
        return self.tensor_square().sum_of_monomials(
            (to_standard(sigma[:i]), to_standard(sigma[i:]))
                for i in range(len(sigma) + 1)
        )

    def left_product_on_basis(self, sigma, mu):
        '''
        TESTS::

            sage: F = FQSym(QQ).F()
            sage: F.left_product_on_basis([],[])
            0
            sage: F.left_product_on_basis([2,1],[])
            F[2, 1]
            sage: F.left_product_on_basis([],[1])
            0
            sage: F.left_product_on_basis([1,2],[1])
            F[1, 2, 3] + F[1, 3, 2]
            sage: F[1,2]<<F[1]
            F[1, 2, 3] + F[1, 3, 2]
            sage: F.left_product_on_basis([3,1,2],[2,1])
            F[3, 1, 2, 5, 4] + F[3, 1, 5, 2, 4] + F[3, 1, 5, 4, 2] + F[3, 5, 1, 2, 4] + F[3, 5, 1, 4, 2] + F[3, 5, 4, 1, 2]
            sage: F[3,1,2]<<F[2,1]
            F[3, 1, 2, 5, 4] + F[3, 1, 5, 2, 4] + F[3, 1, 5, 4, 2] + F[3, 5, 1, 2, 4] + F[3, 5, 1, 4, 2] + F[3, 5, 4, 1, 2]
        '''
        if len(sigma) < 1:
            return self(self.base_ring().zero())

        return self.sum_of_monomials(map(
            lambda gamma: self.basis().keys()([sigma[0]] + list(gamma)),
            ShuffleProduct(sigma[1:], [l + len(sigma) for l in mu], list)
        ))

    def right_product_on_basis(self, sigma, mu):
        '''
        TESTS::

            sage: F = FQSym(QQ).F()
            sage: F.right_product_on_basis([],[])
            0
            sage: F.right_product_on_basis([],[1])
            F[1]
            sage: F.right_product_on_basis([1],[])
            0
            sage: F.right_product_on_basis([1],[1])
            F[2, 1]
            sage: F[1]>>F[1]
            F[2, 1]
            sage: F.right_product_on_basis([1,2],[1])
            F[3, 1, 2]
            sage: F[1,2]>>F[1]
            F[3, 1, 2]
            sage: F.right_product_on_basis([1,2],[2,1])
            F[4, 1, 2, 3] + F[4, 1, 3, 2] + F[4, 3, 1, 2]
            sage: F[1,2]>>F[2,1]
            F[4, 1, 2, 3] + F[4, 1, 3, 2] + F[4, 3, 1, 2]
        '''
        if len(mu) < 1:
            return self(self.base_ring().zero())
        return self.sum_of_monomials(map(
            lambda gamma: self.basis().keys()(
                [mu[0] + len(sigma)] + list(gamma)),
            ShuffleProduct(sigma, [l + len(sigma) for l in mu[1:]], list)
        ))

    def left_coproduct_on_basis(self, sigma):
        '''
        TESTS::

            sage: F = FQSym(QQ).F()
            sage: F.left_coproduct_on_basis([])
            0
            sage: F.left_coproduct_on_basis([1])
            0
            sage: F.left_coproduct_on_basis([1,2])
            F[1] # F[1]
            sage: F.left_coproduct_on_basis([2,1])
            0
            sage: F.left_coproduct_on_basis([2,3,1])
            F[1] # F[2, 1]
            sage: F.left_coproduct_on_basis([2,4,3,1])
            F[1] # F[3, 2, 1]
            sage: F.left_coproduct_on_basis([2,4,5,3,1])
            F[1] # F[3, 4, 2, 1] + F[1, 2] # F[3, 2, 1]
            sage: F.left_coproduct_on_basis([5,2,4,3,1])
            0
        '''
        if len(sigma) < 2:
            return self(self.base_ring().zero())
        l, r = [], []
        current = l
        for i in sigma:
            if i == max(sigma):
                current = r
            current.append(i)
        return self.tensor_square().sum_of_monomials(
            [(to_standard(l[:i + 1]), to_standard(l[i + 1:] + r))
            for i in range(len(l))]
        )

    def right_coproduct_on_basis(self, sigma):
        '''
        TESTS::

            sage: F = FQSym(QQ).F()
            sage: F.right_coproduct_on_basis([1,2])
            0
            sage: F.right_coproduct_on_basis([2,1])
            F[1] # F[1]
            sage: F.right_coproduct_on_basis([1])
            0
            sage: F.right_coproduct_on_basis([])
            0
            sage: F.right_coproduct_on_basis([1,3,2])
            F[1, 2] # F[1]
            sage: F.right_coproduct_on_basis([3,1,2])
            F[1] # F[1, 2] + F[2, 1] # F[1]
            sage: F.right_coproduct_on_basis([3,1,2,4])
            0
            sage: F.right_coproduct_on_basis([3,1,4,2])
            F[2, 1, 3] # F[1]
        '''
        if len(sigma) < 2:
            return self(self.base_ring().zero())
        l, r = [], []
        current = l
        for i in sigma:
            current.append(i)
            if i == max(sigma):
                current = r
        return self.tensor_square().sum_of_monomials(
            [(to_standard(l + r[:i]), to_standard(r[i:]))
            for i in range(len(r))]
        )

    def internal_product_on_basis(self, sigma, mu):
        '''
        TESTS::

            sage: F = FQSym(QQ).F()
            sage: F[3,1,2].internal_product(F[1,2])
            F[3, 1, 2]
            sage: F[3,1,2].internal_product(F[3,1,2])
            F[2, 3, 1]
        '''
        return self(sigma * mu)

    def scalar_product_on_basis(self, sigma, mu):
        """
        TESTS::

            sage: F = FQSym(QQ).F()
            sage: sigma = Permutation([1,4,2,3])
            sage: F.scalar_product_on_basis(sigma, sigma.inverse())
            1
            sage: F.scalar_product_on_basis(sigma, sigma)
            0

        """
        if sigma == mu.inverse():
            return self.base_ring().one()
        else:
            return self.base_ring().zero()

register_as_realization(FreeQuasiSymmetricFunctions, Fundamental, "F")