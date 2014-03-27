# -*- coding: utf-8 -*-
r"""
Quasi-shuffle product of lists of elements.

For any sequences `(a_n), (b_m)` of element of `X` and any
associative operations `\star`, the quasi-shuffle could be defined inductively by:

FIXME:: update the documentation...
MATH::

    (a_n)_{n \geqslant 0} \Cup (b_m)_{m \geqslant 0} =
        a_0 \cdot \left((a_n)_{n \geqslant 1} \Cup (b_m)_{m \geqslant 0}
        + b_0 \cdot \left((a_n)_{n \geqslant 0} \Cup (b_m)_{m \geqslant 1}\right)
        + a_0 \star b_0 \cdot \left((a_n)_{n \geqslant 1} \Cup (b_m)_{m \geqslant 1}\right)

for `\star` an associative operation extended by linearity.

EXAMPLES::

    sage: from sage.combinat.quasi_shuffle import QuasiShuffleProduct
    sage: list(QuasiShuffleProduct([3],[1,2], reducer=lambda l,r: [l+r, l-r]))
    [[3, 1, 2], [1, 3, 2], [1, 2, 3], [1, 5], [1, 1], [4, 2], [2, 2]]

    sage: list(QuasiShuffleProduct([3],[1,2]))
    [[3, 1, 2], [1, 3, 2], [1, 2, 3], [1, 5], [4, 2]]

    sage: list(QuasiShuffleProduct([(3,)],[(1,2)]))
    [[(3,), (1, 2)], [(1, 2), (3,)], [(3, 1, 2)]]

    sage: from sage.combinat.shuffle import ShuffleProduct
    sage: list(QuasiShuffleProduct([(3,)],[(1,2)], reducer=ShuffleProduct))
    [[(3,), (1, 2)], [(1, 2), (3,)], [[3, 1, 2]], [[1, 3, 2]], [[1, 2, 3]]]

AUTHOR:

- Jean-Baptiste Priez
"""
#*****************************************************************************
#  Copyright (C) 2014   Jean-Baptiste Priez <jbp@kerios.fr>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#******************************************************************************
import itertools, collections
from sage.structure.parent import Parent


class QuasiShuffleProduct(Parent):

    """

    Quasi-shuffle product of lists of elements.

    For any sequences `(a_n), (b_m)` of element of `X` and any
    associative operations `\star`, the quasi-shuffle could be defined inductively by:

    MATH::

        (a_n)_{n \geqslant 0} \Cup (b_m)_{m \geqslant 0} =
            a_0 \cdot \left((a_n)_{n \geqslant 1} \Cup (b_m)_{m \geqslant 0}
            + b_0 \cdot \left((a_n)_{n \geqslant 0} \Cup (b_m)_{m \geqslant 1}\right)
            + a_0 \star b_0 \cdot \left((a_n)_{n \geqslant 1} \Cup (b_m)_{m \geqslant 1}\right)

    for `\star` an associative operation extended by linearity.

    TESTS::

        sage: from sage.combinat.quasi_shuffle import QuasiShuffleProduct
        sage: TestSuite(QuasiShuffleProduct).run()

    """
    def __init__(self, l1, l2, elem_constructor=None, reducer=lambda l, r: [l + r]):
        """
        Quasi-shuffle product of two iterable.

        INPUT:

            - *l1*, *l2* both are iterable
            - *elem_constructor* a constructor use to define the ouput objects
                (by default that constructor is deduced from *l1*)
            - *reducer* must be an associative operation which return a list of object
                (the output of *reducer* must be coherent with the type of the element of *l1*, *l2*)

        TESTS::

                sage: from sage.combinat.quasi_shuffle import QuasiShuffleProduct
                sage: list(QuasiShuffleProduct([(3,)],[(1,2)])) # equivalent with *reducer=lambda l, r: [l+r]*
                [[(3,), (1, 2)], [(1, 2), (3,)], [(3, 1, 2)]]

                sage: from sage.combinat.shuffle import ShuffleProduct
                sage: list(QuasiShuffleProduct([(3,)],[(1,2)], reducer=ShuffleProduct))
                [[(3,), (1, 2)], [(1, 2), (3,)], [[3, 1, 2]], [[1, 3, 2]], [[1, 2, 3]]]
        """
        assert(isinstance(l1, collections.Iterable) and
               isinstance(l2, collections.Iterable)
        )
        self._l1 = list(l1)
        self._l2 = list(l2)

        if not elem_constructor:
            if hasattr(l1, "parent") and hasattr(l1.parent(), "_element_constructor"):
                self._element_constructor = l1.parent()._element_constructor_
            else:
                self._element_constructor = list
        else:
            self._element_constructor = elem_constructor

        self._reducer = reducer

    def _repr_(self):
        """
        TESTS::

            sage: from sage.combinat.quasi_shuffle import QuasiShuffleProduct
            sage: QuasiShuffleProduct([(3,)],[(1,2)])
            Quasi shuffle product of [(3,)] and [(1, 2)]
        """
        return "Quasi shuffle product of %s and %s" % (self._l1, self._l2)

    def __contains__(self, X):
        # FIXME: that seems not possible to test if something is contained...
        ### for example if reducer is a product... then we need the dual operation to test that.
        raise NotImplemented

    def an_element(self):
        return self._element_constructor(self._l1 + self._l2)

    def cardinality(self):
        """
        That method compute the number of terms when "reducer" produces 
        only one terms.
        
        A008288: Square array of Delannoy numbers 
                 D(i,j) (i >= 0, j >= 0) read by antidiagonals.
                 
        MATH::
        
            \begin{align}
            D(n, k) &= D(n, k-1) + D(n-1, k-1) + D(n-1, k)\,,\\
                    &= \sum_{d = 0}^{\max(n,k)} \binomial{k}{d}\binomial{n+k-d}{k}\,,\\ 
                    &= \sum_{d=0}^{\max(n,k)} 2^d \binomial{n}{d}\binomial{k}{d}\,.
            \end{align}

        TESTS::

            sage: from sage.combinat.quasi_shuffle import \
                     QuasiShuffleProduct
            sage: qs3x3 = QuasiShuffleProduct([3,1,2],[1,2,3])
            sage: qs3x3.cardinality()
            63
            sage: len(list(qs3x3))
            63  
            sage: qs4x3 = QuasiShuffleProduct([1,2,3,4],[1,2,3])
            sage: len(list(qs4x3))
            129
            sage: qs4x3.cardinality()
            129
            sage: qs4x7 = QuasiShuffleProduct([1,2,3,4],[1,2,3,4,5,6,7])
            sage: qs4x7.cardinality()
            2241
            sage: len(list(qs4x7))
            2241
            sage: qs7x4 = QuasiShuffleProduct([1,2,3,4,5,6,7],[1,2,3,4])
            sage: qs7x4.cardinality()
            2241
            sage: len(list(qs7x4))
            2241
        """
        # FIXME compute the cardinality if and only if `\star` produces an unique element!
        # D(n, k) = Sum_{d} binomial(k, d)*binomial(n+k-d, k) 
        #         = Sum_{d} 2^d*binomial(n, d)*binomial(k, d).
        from sage.rings.arith import binomial
        n = len(self._l1)
        k = len(self._l2)
        return sum([binomial(k, d) * binomial(n+k-d, k) 
                    for d in range(max(n, k) + 1)])
        raise NotImplemented

    def __iter__(self):
        """
        TESTS::

            sage: from sage.combinat.quasi_shuffle import QuasiShuffleProduct
            sage: list(QuasiShuffleProduct([[1,2]], [[3]]))
            [[[1, 2], [3]], [[3], [1, 2]], [[1, 2, 3]]]
            sage: list(QuasiShuffleProduct([[]], [[]], elem_constructor=lambda osp: osp + [3]))
            [[[], [], 3], [[], [], 3], [[], 3]]
            sage: list(QuasiShuffleProduct([], [], elem_constructor=lambda osp: osp + [3]))
            [[3]]
        """
        def recursive_generator(l1, l2):
            # {a}S::{b}S' = {a} (S::{b}S') + {b} ({a}S::S') + {a,b} (S::S')
            if len(l1) == 0:
                return iter([l2])
            if len(l2) == 0:
                return iter([l1])

            # # {a} (S::{b}S')
            it1 = itertools.imap(
                lambda l: [l1[0]] + l,
                recursive_generator(l1[1:], l2)
            )
            # # {b} ({a}S::S')
            it2 = itertools.imap(
                lambda l: [l2[0]] + l,
                recursive_generator(l1, l2[1:])
            )
            # # {a,b} (S::S')
            it3 = itertools.imap(
                lambda (l, r): [l] + r,
                itertools.product(
                    self._reducer(l1[0], l2[0]),
                    recursive_generator(l1[1:], l2[1:])
            ))
            return itertools.chain(it1, it2, it3)

        if len(self._l1) == 0:
            yield self._element_constructor(self._l2)
        elif len(self._l2) == 0:
            yield self._element_constructor(self._l1)
        else:
            for l in recursive_generator(self._l1, self._l2):
                yield self._element_constructor(l)

