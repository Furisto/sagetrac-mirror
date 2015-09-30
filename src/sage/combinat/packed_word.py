# -*- coding: utf-8 -*-
"""
Packed Words

References:
-----------

.. [NoTh06] Polynomial realizations of some trialgebras,
    J.-C. Novelli and J.-Y. Thibon.

.. [BerZab] The Hopf algebras of symmetric functions and quasi-symmetric
            functions in non-commutative variables are free and co-free},
    N. Bergeron, and M. Zabrocki.

AUTHOR:

- Jean-Baptiste Priez
"""
#*****************************************************************************
#       Copyright (C) 2014 Jean-Baptiste Priez <jbp@kerios.fr>,
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************
import itertools
from itertools import imap
from sage.combinat.combinatorial_map import combinatorial_map
from sage.combinat.shuffle import ShuffleProduct
from sage.combinat.structures import ElementStructure, ParentStructure
from sage.combinat.tools import transitive_ideal
from sage.misc.classcall_metaclass import typecall
from sage.misc.lazy_attribute import lazy_class_attribute
from sage.structure.list_clone import ClonableIntArray
from sage.sets.set import Set
from sage.combinat.set_partition_ordered import OrderedSetPartitions, OrderedSetPartition
from sage.misc.misc import uniq
from sage.combinat.composition import Composition


def to_pack(li):
    """
    The analogue map of the *standardization* (..see
    :func:`sage.combinat.permutation.to_standard`) for *packed words*.

    .. see _[NoTh06] §2. The Hopf algebra WQSym


    TESTS::

        sage: from sage.combinat.packed_word import to_pack
        sage: to_pack([])
        []
        sage: to_pack([3,1])
        [2, 1]
        sage: to_pack([1, 0, 0])
        [2, 1, 1]
        sage: to_pack([3,1,55])
        [2, 1, 3]
        sage: to_pack([11,4,1,55])
        [3, 2, 1, 4]
        sage: to_pack([11,4,1,11,4])
        [3, 2, 1, 3, 2]

    """
    l = uniq(li)
    return PackedWord([l.index(i) + 1 for i in li])


class PackedWord(ElementStructure, ClonableIntArray):
    """
    The class of packed words

    TESTS::

        sage: PackedWord()
        []

    """

    def __init__(self, parent, li=None):
        """
        TESTS::

            sage: p = PackedWord(); p
            []
            sage: p == PackedWord([])
            True

        """
        if li is None:
            li = []
        ClonableIntArray.__init__(self, parent, li)

    @lazy_class_attribute
    def _auto_parent_(cls):
        """
        TESTS::

            sage: PackedWord([1,1]).parent()
            Packed words

        """
        return PackedWords()

    def check(self):
        """
        Checks that ``self`` is a packed word

        TESTS::

            sage: PackedWord([3,3,2,1])
            [3, 3, 2, 1]

            sage: PackedWord([2,2,1,0,4])
            Traceback (most recent call last):
            ...
            AssertionError: This is not a packed word `[2, 2, 1, 0, 4]`

        """
        s = uniq(self)
        assert(len(s) == 0 or (max(s) == len(s) and min(s) == 1)
            ), "This is not a packed word `%s`" % str(self)

    def to_ordered_set_partition(self):
        """
        This method build an *ordered partition sets* associated to *self*.

        TESTS::

            sage: pw = PackedWords(6).random_element()
            sage: pw.to_ordered_set_partition().to_packed_word() == pw
            True
            sage: PackedWord([1,2,3,1,1,3]).to_ordered_set_partition()
            [{1, 4, 5}, {2}, {3, 6}]

        """
        import collections
        d = collections.defaultdict(list)
        for i in range(len(self)):
            d[self[i]].append(i + 1)
        return OrderedSetPartition([Set(d[k]) for k in sorted(d.keys())])

    def succ_zabrocki_bergeron(self):
        """
        see _[BerZab] and
        :meth:`sage.combinat.set_partition_ordered.OrderedSetPartition.succ_zabrocki_bergeron`.

        TESTS::

            sage: PackedWord([1,2,3]).succ_zabrocki_bergeron()
            [[1, 1, 2], [1, 2, 2]]
        """
        return map(
            _to_packed_word,
            self.to_ordered_set_partition().succ_zabrocki_bergeron())

    def greater_zabrocki_bergeron(self):
        """
        see _[BerZab] and
        :meth:`sage.combinat.set_partition_ordered.OrderedSetPartition.greater_zabrocki_bergeron`

        TESTS::

            sage: PackedWord([1,2,3]).greater_zabrocki_bergeron()
            [[1, 1, 1], [1, 1, 2], [1, 2, 2], [1, 2, 3]]
        """
        return transitive_ideal(PackedWord.succ_zabrocki_bergeron, self)

    def bruhat_succ(self, side="left"):
        """
        TESTS::

            sage: list(PackedWord([1,1,2,3]).bruhat_succ())
            [[2, 2, 1, 3], [1, 1, 3, 2]]
            sage: list(PackedWord([1,1,2,3]).bruhat_succ(side="right"))
            [[1, 2, 1, 3], [1, 1, 3, 2]]

        """
        # TODO make documentation with Yannik
        if side == "left":
            return imap(_to_packed_word,
                    self.to_ordered_set_partition()._bruhat_left_succ()
            )
        else:
            return self._bruhat_right_succ()

    def bruhat_greater(self, side="left"):
        """
        TESTS::

            sage: list(PackedWord([1,1,2,3]).bruhat_greater())
            [[3, 3, 2, 1],
             [2, 2, 3, 1],
             [3, 3, 1, 2],
             [1, 1, 3, 2],
             [2, 2, 1, 3],
             [1, 1, 2, 3]]
            sage: list(PackedWord([1,1,2,3]).bruhat_greater(side="right"))
            [[1, 1, 2, 3],
             [1, 1, 3, 2],
             [1, 2, 1, 3],
             [1, 2, 3, 1],
             [1, 3, 1, 2],
             [1, 3, 2, 1],
             [2, 1, 1, 3],
             [2, 1, 3, 1],
             [2, 3, 1, 1],
             [3, 1, 1, 2],
             [3, 1, 2, 1],
             [3, 2, 1, 1]]
        """
        # TODO make documentation with Yannik
        if side == "left":
            return map(_to_packed_word,
                        self.to_ordered_set_partition().bruhat_greater())
        else:
            return transitive_ideal(PackedWord._bruhat_right_succ, self)

    def _bruhat_right_succ(self):
        """
        TESTS::

            sage: list(PackedWord([1,1,2,3]).bruhat_succ(side="right")) # indirect doctest
            [[1, 2, 1, 3], [1, 1, 3, 2]]
        """
        # TODO make documentation with Yannik
        for i in range(len(self)-1):
            if self[i] < self[i+1]:
                yield self.parent()(self[:i] + [self[i+1], self[i]] + self[i+2:])

    @combinatorial_map(name='to composition')
    def to_composition(self):
        """
        Compute a *composition* associated to the parikh vector of *self*.

        TESTS::

            sage: PackedWord([1,2,3,1,1,3]).to_composition()
            [3, 1, 2]
            sage: PackedWord([1,2,3,1,1,3]).to_ordered_set_partition().to_composition()
            [3, 1, 2]
            sage: for pw in PackedWords(4):
            ....:     assert(pw.to_composition() == pw.to_ordered_set_partition().to_composition())
        """

        if len(self) == 0:
            return Composition([])
        li = list(self)
        return Composition([li.count(i) for i in set(self)])

    def shifted_shuffle(self, other):
        """
        The analogue map of the *shifted_shuffle* (..see
        :meth:`sage.combinat.permutation.Permutation_class.shifted_shuffle`)
        for *packed words*:

        MATH::

            p_1\dots p_k \Cup q_1\dots q_l[m] := p_1 \dot (p_2 \dots p_k \Cup (q_1 \dots q_l)[m])
                + (q_1 + m) \dot (p_1 \dots p_k \Cup (q_2 \dots q_l)[m])\,.

        with `m := \max(p_1 \dots p_k)`.

        .. see _[NoTh06] §2. The Hopf algebra WQSym

        TESTS::

            sage: PW = PackedWord
            sage: list(PW([1,1]).shifted_shuffle(PW([1,2])))
            [[1, 1, 2, 3], [2, 1, 1, 3], [1, 2, 1, 3], [2, 3, 1, 1],
             [2, 1, 3, 1], [1, 2, 3, 1]]
            sage: list(PW([1,1]).shifted_shuffle(PW([])))
            [[1, 1]]
            sage: list(PW([]).shifted_shuffle(PW([1,2])))
            [[1, 2]]
        """
        assert(other in self.parent())
        if self.is_empty():
            return iter([other])
        shift = max(self)
        return iter(ShuffleProduct(self, [i + shift for i in other]))

    def shifted_concatenation(self, other, side='right'):
        """
        The analogue map of the *shifted_concatenation* (..see
        :meth:`sage.combinat.permutation.Permutation_class.shifted_concatenation`)
        for *packed words*:

        MATH::

            p_1\dots p_k \bullet q_1\dots q_l[m] :=
                p_1 \dots p_k \dot (q_1 + m) \dots (q_l + m)\,.

        with `m := \max(p_1 \dots p_k)`.

        TESTS::

            sage: PackedWord([1,1,2]).shifted_concatenation([1,3,2,2])
            [1, 1, 2, 3, 5, 4, 4]
            sage: PackedWord([1,1,2]).shifted_concatenation([1,3,2,2], side='right')
            [1, 1, 2, 3, 5, 4, 4]
            sage: PackedWord([1,1,2]).shifted_concatenation([1,3,2,2], side='left')
            [3, 5, 4, 4, 1, 1, 2]
            sage: PackedWord([1,1,2]).shifted_concatenation([1,3,2,2], side='toto')
            Traceback (most recent call last):
            ...
            ValueError: toto must be "left" or "right"
            sage: PackedWord([]).shifted_concatenation([1])
            [1]
        """
        assert(other in self.parent())
        PW = self.parent()._element_constructor

        if self.is_empty():
            return other

        shift = max(self)
        if side == "right" :
            return PW(list(self) + [a + shift for a in other])
        elif side == "left" :
            return PW([a + shift for a in other] + list(self))
        else :
            raise ValueError, "%s must be \"left\" or \"right\"" %(side)

    def is_empty(self):
        """
        Returns whether ``self`` is the empty word.

        EXAMPLES::

            sage: PackedWord([]).is_empty()
            True
            sage: PackedWord([2,1,2]).is_empty()
            False
        """
        return not self

    def _latex_(self):
        """
        TESTS::

            sage: latex(PackedWord([1,2,3,1,1,3]))
            123113
            sage: latex(PackedWord(range(1,11)))
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        """
        if max(self) >= 10:
            return str(list(self))
        return str(list(self)).replace(
            '[', '').replace(
            ']', '').replace(
            ', ', '')

    def pseudo_permutohedron_succ(self):
        r"""
        Iterate the successor of the packed word ``self``.

        ..see _[NoTh06] §2.6 The pseudo-permutohedron

        TESTS::

            sage: PW = PackedWord
            sage: list(PW([1,2,3]).pseudo_permutohedron_succ())
            [[1, 1, 2], [1, 2, 2]]
            sage: list(_[1].pseudo_permutohedron_succ())
            [[1, 1, 1], [1, 3, 2]]

        """
        return itertools.imap(
            _to_packed_word,
            self.to_ordered_set_partition().pseudo_permutohedron_succ()
        )

    def pseudo_permutohedron_pred(self):
        r"""
        Iterate the predecessor of the packed word ``self``.

        ..see _[NoTh06] §2.6 The pseudo-permutohedron

        TESTS::

            sage: PW = PackedWord
            sage: list(PW([3,2,1]).pseudo_permutohedron_pred())
            [[2, 1, 1], [2, 2, 1]]
            sage: list(_[1].pseudo_permutohedron_pred())
            [[2, 3, 1], [1, 1, 1]]
        """
        return itertools.imap(
            _to_packed_word,
            self.to_ordered_set_partition().pseudo_permutohedron_pred()
        )

    def pseudo_permutohedron_smaller(self):
        """
        Iterate through a list of packed words smaller than or equal to ``p``
        in the pseudo-permutohedron order.

        ..see _[NoTh06] §2.6 The pseudo-permutohedron

        TESTS::

            sage: set(PackedWord([3,2,1]).pseudo_permutohedron_smaller()) == \
                    set(PackedWords(3))
            True
        """
        return itertools.imap(
            _to_packed_word,
            self.to_ordered_set_partition().pseudo_permutohedron_smaller()
        )

    def pseudo_permutohedron_greater(self):
        """
        Iterate through a list of packed words greater than or equal to ``p``
        in the pseudo-permutohedron order.

        ..see _[NoTh06] §2.6 The pseudo-permutohedron

        TESTS::

            sage: set(PackedWord([1,2,3]).pseudo_permutohedron_greater()) == \
                    set(PackedWords(3))
            True
        """
        return itertools.imap(
            _to_packed_word,
            self.to_ordered_set_partition().pseudo_permutohedron_greater()
        )

    def half_inversions(self):
        """
        Return a list of the half inversions of ``self``.

        ..see: :meth:`sage.combinat.set_partition_ordered.OrderedSetPartition.half_inversions`.

        ..see _[NoTh06] §2.6 The pseudo-permutohedron

        TESTS::

            sage: PW = PackedWord
            sage: PW([1,1,2]).half_inversions()
            [(1, 2)]
            sage: PW([1,2,1]).half_inversions()
            [(1, 3)]
        """
        return self.to_ordered_set_partition().half_inversions()

    def inversions(self):
        """
        Return a list of the inversions of ``self``.

        An inversion of a packed word `p` is a pair `(i, j)` such that
        `i < j` and `p(i) > p(j)`.

        (The definition is same to inversions for permutations)

        ..see _[NoTh06] §2.6 The pseudo-permutohedron

        TESTS::

            sage: PW = PackedWord
            sage: PW([1,1,2]).inversions()
            []
            sage: PW([2,1,2]).inversions()
            [(1, 2)]
            sage: PW([2, 3, 2, 1, 1, 3, 3, 4]).inversions()
            [(1, 4), (1, 5), (2, 3), (2, 4), (2, 5), (3, 4), (3, 5)]
        """
        n = len(self)
        return [(i + 1, j + 1) for i in range(n - 1)
                               for j in range(i + 1, n)
                    if self[i] > self[j]]

    def is_smaller_than(self, other):
        """
        ``self`` is smaller than ``other`` if the value of the
        inversion (i, j) in the table of inversions of ``self``
        is smaller than or equal to its value in the table of inversions
        of ``other``, for all (i, j).

        The table of inversion of ``p`` is given by the set of
        inversion ``p.inversions()`` with weight `1` and
        the set of half inversion with weight `1/2`.

        ..see _[NoTh06] §2.6 The pseudo-permutohedron

        TESTS::

            sage: PW = PackedWord
            sage: pw = PW([1,2,3])
            sage: forall(PackedWords(3), pw.is_smaller_than)
            (True, None)
            sage: PW([4,4,2,5,3,3,1,3]).is_smaller_than(PW([3,3,2,4,2,2,1,2]))
            True
        """
        assert(other in self.parent())
        invO = Set(other.inversions())
        for inv in self.inversions():
            if inv not in invO:
                return False
        halfO = Set(other.half_inversions())
        for half in self.half_inversions():
            if half not in invO and half not in halfO:
                return False
        return True


class PackedWords(ParentStructure):
    """
    Factory class for packed words.

    INPUT:

    - ``size`` -- (optional) an integer

    OUTPUT:

    - the set of all packed words (of ``size`` (if specified))

    TESTS::

        sage: TestSuite(PackedWords()).run()

    EXAMPLES::

        sage: PackedWords()
        Packed words
        sage: PackedWords(4)
        Packed words of degree 4

    """

    @staticmethod
    def __classcall_private__(cls, size=None, *args, **opts):
        F = super(PackedWords, cls).__classcall__(cls, *args, **opts)
        if size is not None:
            return F.graded_component(size)
        return F

    Element = PackedWord

    def grading(self, pw):
        """
        TESTS::

            sage: PackedWord([1,2,1,1]).grade()
            4
            sage: PackedWords().grading(PackedWord([1,1,2]))
            3
        """
        return len(pw)

    def __contains__(self, item):
        """
        TESTS::

            sage: [1,1,1] in PackedWords()
            True
            sage: [2,1,1] in PackedWords()
            True
            sage: [2,'2',1] in PackedWords()
            False
        """
        if isinstance(item, self.element_class):
            return True
        try:
            self._element_constructor_(item)
            return True
        except:
            return False

    def permutation_to_packed_word(self, sigma):
        """
        TESTS::

            sage: PW = PackedWords()
            sage: PW.permutation_to_packed_word(Permutation([3,1,2,4]))
            [[2, 1, 1, 2], [2, 1, 1, 3], [3, 1, 2, 3], [3, 1, 2, 4]]
            sage: PW.permutation_to_packed_word(Permutation([1,2,3]))
            [[1, 1, 1], [1, 1, 2], [1, 2, 2], [1, 2, 3]]
        """
        return self.graded_component(len(sigma)).permutation_to_packed_word(sigma)

    def _repr_(self):
        """
        TESTS::

            sage: PackedWords()
            Packed words
        """
        return "Packed words"

    class GradedComponent(ParentStructure.GradedComponent):

        def cardinality(self):
            """
            Stirling number ???

            TESTS::

                sage: PackedWords(0).cardinality()
                1
                sage: PackedWords(1).cardinality()
                1
                sage: PackedWords(2).cardinality()
                3
                sage: PackedWords(3).cardinality()
                13
            """
            return OrderedSetPartitions(self.grade()).cardinality()

        def __iter__(self):
            """
            TESTS::

                sage: PackedWords(0).list()
                [[]]
                sage: PackedWords(1).list()
                [[1]]
                sage: PackedWords(2).list()
                [[1, 2], [2, 1], [1, 1]]
                sage: PackedWords().graded_component(3).list()
                [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1],
                 [1, 2, 2], [2, 1, 2], [2, 2, 1], [1, 1, 2], [1, 2, 1], [2, 1, 1],
                 [1, 1, 1]]
            """
            n = self.grade()
            for osp in OrderedSetPartitions(n):
                yield osp.to_packed_word()

        def permutation_to_packed_word(self, sigma):
            """
            Compute all packed words which give *sigma* by standardization.

            TESTS::

                sage: PW = PackedWords()
                sage: PW.permutation_to_packed_word(Permutation([3,1,2,4]))
                [[2, 1, 1, 2], [2, 1, 1, 3], [3, 1, 2, 3], [3, 1, 2, 4]]
                sage: PW.permutation_to_packed_word(Permutation([1,2,3]))
                [[1, 1, 1], [1, 1, 2], [1, 2, 2], [1, 2, 3]]
            """
            n = self.grade()
            if n <= 1:
                if n == 0:
                    return [self._element_constructor_([])]
                if n == 1:
                    return [self._element_constructor_([1])]
            li = [({sigma.index(1):1}, sigma.index(1))]
            for i in range(2, n):
                index_i = sigma.index(i)
                tmp = []
                for (pw, l_index) in li:
                    if l_index < index_i:
                        pw[index_i] = pw[l_index]
                        tmp.append((dict(pw), index_i))
                    pw[index_i] = pw[l_index] + 1
                    tmp.append((dict(pw), index_i))
                li = tmp
            index_i = sigma.index(n)
            res = []
            for (pw, l_index) in li:
                if l_index < index_i:
                    pw[index_i] = pw[l_index]
                    res.append(self._element_constructor_(pw.values()))
                pw[index_i] = pw[l_index] + 1
                res.append(self._element_constructor_(pw.values()))
            return res

def _to_packed_word(osp):
    return osp.to_packed_word()
