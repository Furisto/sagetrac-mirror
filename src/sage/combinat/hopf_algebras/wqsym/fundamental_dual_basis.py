# -*- coding: utf-8 -*-
r"""
The fundamental dual basis of WQSym Hopf algebra.

M-basis of WQSym
"""
#*****************************************************************************
#       Copyright (C) 2014 Jean-Baptiste Priez <jbp@kerios.fr>.
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************
import itertools
from sage.combinat.hopf_algebras.wqsym import WordQuasiSymmetricFunctions
from sage.combinat.packed_word import to_pack
from sage.combinat.quasi_shuffle import QuasiShuffleProduct
from sage.combinat.set_partition_ordered import OrderedSetPartition
from sage.misc.misc_c import prod


def _restriction(self, w, i):
        r""" Restriction of intervalle [min, i] and [i+1, max]

        TESTS::

            sage: M = WQSym(QQ).M()
            sage: M[1,1].coproduct() # indirect doctest
            M[] # M[1, 1] + M[1, 1] # M[]

        """
        left = []
        right = []
        for l in w:
            if l >= i + 1:
                right.append(l)
            else:
                left.append(l)
        return (self.basis().keys()(left), to_pack(right))

class FundamentalDual(WordQuasiSymmetricFunctions._Basis):
    """
    This is the fundamental dual basis `(M_u)` of ``WQSym``:

    MATH::

        \mathbb{M}_u (A) := \sum_{pack(w) = u} w

    EXAMPLES::

        sage: M = WQSym(QQ).M()
        sage: M[1,1].expand_to_polynomial(4)
        a1^2 + a2^2 + a3^2 + a4^2
        sage: M[1,2].expand_to_polynomial(4)
        a1*a2 + a1*a3 + a1*a4 + a2*a3 + a2*a4 + a3*a4
        sage: M[1,2,1].expand_to_polynomial(4)
        a1*a2*a1 + a1*a3*a1 + a1*a4*a1 + a2*a3*a2 + a2*a4*a2 + a3*a4*a3

    The product of `(\mathbb{M}_u)_{u\in\mathfsf{PW}}` is
    described by the quasi shuffle product of ordered set partitions
    (..see: :meth:`sage.combinat.set_partition_ordered.OrderedSetPartition.shifted_quasi_shuffle`)

    EXAMPLES::

        sage: M[1,2,1] * M[1]
        M[1, 2, 1, 1] + M[1, 2, 1, 2] + M[1, 2, 1, 3] + M[1, 3, 1, 2] + M[2, 3, 2, 1]

    And the coproduct is described by the unshuffling and
    packization (of the right member).

    EXAMPLES::

        sage: M[3,1,2,1].coproduct()
        M[] # M[3, 1, 2, 1] + M[1, 1] # M[2, 1] + M[1, 2, 1] # M[1] + M[3, 1, 2, 1] # M[]
    """
    _prefix_ = "M"

    def _morphisms_(self):
        self._M_to_Monomial_of_QSym()
        self._G_of_FQSym_to_M()

    def _G_of_FQSym_to_M(self):
        """
        TESTS::

            sage: G = FQSym(QQ).G()
            sage: M = WQSym(QQ).M()
            sage: M(G[1,2])
            M[1, 1] + M[1, 2]
            sage: M(G[3,1,2])
            M[2, 1, 1] + M[3, 1, 2]
            sage: M(G[2,3,4,1])
            M[2, 2, 2, 1] + M[2, 2, 3, 1] + M[2, 3, 3, 1] + M[2, 3, 4, 1]
        """
        from sage.combinat.hopf_algebras.all import FQSym
        G = FQSym(self.base()).G()
        G.module_morphism(
            on_basis=lambda sigma: self.sum_of_monomials(
                self.basis().keys().permutation_to_packed_word(sigma)),
            codomain=self
        ).register_as_coercion()

    def _M_to_Monomial_of_QSym(self):
        """

        TESTS::

            sage: M = WQSym(QQ).M()
            sage: Mon = QuasiSymmetricFunctions(QQ).M()
            sage: Mon(M[2,1,2])
            M[1, 2]
            sage: Mon(M[1]**2)
            2*M[1, 1] + M[2]
            sage: Mon(M[2,1,2]**2)
            4*M[1, 1, 2, 2] + 2*M[1, 1, 4] + 2*M[1, 2, 1, 2] + 2*M[1, 3, 2] + 2*M[2, 2, 2] + M[2, 4]
        """
        from sage.combinat.ncsf_qsym.qsym import QuasiSymmetricFunctions
        Mo = QuasiSymmetricFunctions(self.base()).M()
        self.module_morphism(
            on_basis=lambda pw: Mo(pw.to_composition()),
            codomain=Mo
        ).register_as_coercion()

    def dual_basis(self):
        return self.realization_of().S()

    def expand_to_polynomial_on_basis(self, pw, k):
        """
        TESTS::

            sage: M = WQSym(QQ).M()
            sage: M[1,1].expand_to_polynomial(4)
            a1^2 + a2^2 + a3^2 + a4^2
            sage: M[1,2].expand_to_polynomial(4)
            a1*a2 + a1*a3 + a1*a4 + a2*a3 + a2*a4 + a3*a4
            sage: M[1,2,1].expand_to_polynomial(4)
            a1*a2*a1 + a1*a3*a1 + a1*a4*a1 + a2*a3*a2 + a2*a4*a2 + a3*a4*a3
        """
        from sage.algebras.free_algebra import FreeAlgebra
        FA = FreeAlgebra(self.base_ring(), ["a%d"%i for i in range(1, k+1)])

        def gen_osp_real(osp, letters):
            if len(osp) > len(letters) or len(osp) == 0:
                yield []
                return

            for i in range(len(letters) - len(osp) + 1):
                #print "ii::", i, letters[i]
                for osp_real in gen_osp_real(osp[1:], letters[i+1:]):

                    yield [letters[i]] + osp_real

        def build_word(osp_real):
            d = {pos:osp_real[i] for i, sset in enumerate(osp) for pos in sset}
            return prod(FA.gens()[d[k]] for k in d)

        osp = pw.to_ordered_set_partition()
        return sum(itertools.imap(build_word, gen_osp_real(osp, range(k))))

    def product_on_basis(self, pw1, pw2):
        """
        TESTS::

            sage: M = WQSym(QQ).M()
            sage: M[1,1]*M[1]
            M[1, 1, 1] + M[1, 1, 2] + M[2, 2, 1]
        """
        return self.sum_of_monomials(
            osp.to_packed_word()
            for osp in pw1.to_ordered_set_partition()\
                .shifted_quasi_shuffle(pw2.to_ordered_set_partition())
        )

    def coproduct_on_basis(self, e):
        """
        TESTS::

            sage: M = WQSym(QQ).M()
            sage: M[1,1].coproduct()
            M[] # M[1, 1] + M[1, 1] # M[]
            sage: M[[]].coproduct()
            M[] # M[]
            sage: M[2,1,2,1,4,3].coproduct()
            M[] # M[2, 1, 2, 1, 4, 3] + M[1, 1] # M[1, 1, 3, 2] + M[2, 1, 2, 1] # M[2, 1] + M[2, 1, 2, 1, 3] # M[1] + M[2, 1, 2, 1, 4, 3] # M[]
        """
        return self.tensor_square().sum_of_monomials(
            _restriction(self, e, i)
            for i in set([-1] + list(e)))

    # TODO:: looking for the definition of the internal product of WQSym _[NovThi06]
    def internal_product_on_basis(self, pw1, pw2):
        """
        TESTS::

            sage: M = WQSym(QQ).M()
            sage: M[2,2,1].internal_product(M[1,2,2])
            M[2, 3, 1]
            sage: M[2,2,1].internal_product(M[3,2,1])
            M[3, 2, 1]
            sage: M[4,5,3,2,2,3,5,1,5].internal_product(M[4,3,3,4,4,2,2,1,4])
            M[5, 7, 4, 2, 2, 3, 6, 1, 8]
        """
        return self.monomial(
            (pw1.to_ordered_set_partition() * pw2.to_ordered_set_partition()).\
                to_packed_word()
        )


    def diese_linear_operator_on_basis(self, k, sigma):
        """
        TESTS::

            sage: M = WQSym(QQ).M()
            sage: M[1,2,1].diese_product(M[1,2])
            M[1, 2, 1, 2] + M[1, 2, 1, 3] + M[1, 3, 1, 2]

        """
        if sigma[k] == sigma[k - 1]:
            return self.monomial(to_pack(sigma[:k] + sigma[k + 1:]))
        else:
            return self.zero()

    def tri_left_product_on_basis(self, pw1, pw2):
        """
        The tri-dendriform left product.
        That is also the dendriform left product.

        TESTS::

            sage: M = WQSym(QQ).M()
            sage: M[1] << M[1]
            M[2, 1]
            sage: M[1] << M[1,1]
            M[2, 1, 1]
            sage: M[2,1] << M[1,1]
            M[2, 1, 1, 1] + M[3, 1, 2, 2] + M[3, 2, 1, 1]
            sage: G = FQSym(QQ).G()
            sage: sig, mu = G.monomial(Permutations(4).random_element()), G.monomial(Permutations(3).random_element())
            sage: M(sig) << M(mu) == M(sig << mu)
            True

        """
        # max from left
        if len(pw1) < 1:
            return self(self.base_ring().zero())

        osp1 = pw1.to_ordered_set_partition()
        k = len(pw1)
        return self.sum_of_monomials(QuasiShuffleProduct(
                osp1[:-1], [[i + k for i in s] for s in pw2.to_ordered_set_partition()],
                elem_constructor=lambda osp: OrderedSetPartition(osp + [osp1[-1]]).to_packed_word(),
                reducer=lambda l, r: [list(l) + r]
        ))

    def tri_right_product_on_basis(self, pw1, pw2):
        """
        The tri-dendriform right product.

        TESTS::

            sage: M = WQSym(QQ).M()
            sage: M.tri_right_product_on_basis(PackedWord([1]), PackedWord([1]))
            M[1, 2]
        """
        # max from right
        if len(pw1) < 1:
            return self(self.base_ring().zero())

        osp2 = pw2.to_ordered_set_partition()
        k = len(pw1)
        last = [[i + k for i in osp2[-1]]]
        return self.sum_of_monomials(QuasiShuffleProduct(
            pw1.to_ordered_set_partition(),
            [[i + k for i in s] for s in osp2[:-1]],
            elem_constructor=lambda osp: OrderedSetPartition(osp + last).to_packed_word(),
            reducer=lambda l, r: [list(l) + r]
        ))

    def tri_middle_product_on_basis(self, pw1, pw2):
        """
        The tri-dendriform middle product.

        TESTS::

            sage: M = WQSym(QQ).M()
            sage: M.tri_middle_product_on_basis(PackedWord([1]), PackedWord([1]))
            M[1, 1]
        """
        if len(pw1) < 1 and len(pw2) < 1:
            return self(self.base_ring().zero())

        osp1 = pw1.to_ordered_set_partition()
        osp2 = pw2.to_ordered_set_partition()
        k = len(pw1)
        last = [list(osp1[-1]) + [i + k for i in osp2[-1]]]
        return self.sum_of_monomials(QuasiShuffleProduct(
            osp1[:-1], [[i + k for i in s] for s in osp2[:-1]],
            elem_constructor=lambda osp: OrderedSetPartition(osp + last).to_packed_word(),
            reducer=lambda l, r: [list(l) + list(r)]
        ))

    left_product_on_basis = tri_left_product_on_basis

    def right_product_on_basis(self, pw1, pw2):
        """
        The dendriform right product.

        TESTS::

            sage: M = WQSym(QQ).M()
            sage: M[1,1] >> M[1]
            M[1, 1, 1] + M[1, 1, 2]
            sage: a = M.monomial(PackedWords(5).random_element())
            sage: b = M.monomial(PackedWords(4).random_element())
            sage: a * b == (a << b) + (a >> b)
            True
            sage: G = FQSym(QQ).G()
            sage: sig, mu = G.monomial(Permutations(4).random_element()), G.monomial(Permutations(6).random_element())
            sage: M(sig) >> M(mu) == M(sig >> mu)
            True

        """
        return self.tri_middle_product_on_basis(pw1, pw2) + \
               self.tri_right_product_on_basis(pw1, pw2)

    def left_coproduct_on_basis(self, sigma):
        """
        The dendriform left coproduct


        Left dendriform coproduct defines as the un-shuffling-packization
        of ``sigma``such that the (last) maximum of `\sigma` is "left" on the left
        of the tensor.

        TESTS::

            sage: M = WQSym(QQ).M()
            sage: M[3,1,2].left_coproduct()
            M[1, 2] # M[1]
            sage: M[2,1,2].left_coproduct()
            0
            sage: M[2,1,3,2].left_coproduct()
            M[2, 1, 2] # M[1]
            sage: G = FQSym(QQ).G()
            sage: a = G.monomial(Permutations(4).random_element())
            sage: G.tensor_square()(a.left_coproduct()) == G(a).left_coproduct()
            True

        """
        last = sigma[-1]
        return self.tensor_square().sum_of_monomials(
            _restriction(self, sigma, i)
            for i in set(range(last, max(sigma))))


    def right_coproduct_on_basis(self, sigma):
        """
        The dendriform right coproduct

        Right dendriform coproduct defines as the un-shuffling-packization
        of ``sigma``such that the (last) maximum of `\sigma` is "left" on the left
        of the tensor.

        TESTS::

            sage: M = WQSym(QQ).M()
            sage: M[1,3,2].right_coproduct()
            M[1] # M[2, 1]
            sage: M[1,3,2,3].right_coproduct()
            M[1] # M[2, 1, 2] + M[1, 2] # M[1, 1]
            sage: G = FQSym(QQ).G()
            sage: a = G.monomial(Permutations(4).random_element())
            sage: G.tensor_square()(a.right_coproduct()) == G(a).right_coproduct()
            True

        """
        last = sigma[-1]
        return self.tensor_square().sum_of_monomials(
            _restriction(self, sigma, i)
            for i in set(range(1, last)))
