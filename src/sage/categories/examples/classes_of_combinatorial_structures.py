# -*- coding: utf-8 -*-
"""
Example of classes of combinatorial structures
--------------------------------------------------------------

This module implements a simple version of the class of compositions of integer.

"[..] a composition of an integer `n` is a way of writing `n` as the sum of a
sequence of (strictly) positive integers." Wikipedia

This module provides a light implementation to rapid use. This example uses the
following pattern::

   from sage.combinat.structures import Structures, Structure


   class MyStructure(Structure):

        def check(self):
            # a way to check if the structure is correct

        @lazy_class_attribute
        def _auto_parent_(self):
            # my default parent
            return ClassOfStructures()

        ## + specific design of my structure

   class MyGradedComponent(Structures.GradedComponent):

        def __iter__(self):
            # an iterator of the objets of the graded component

   class ClassOfStructures(Structures):

        def grading(self, obj):
            # a way to way the grading of the graded component which contains
            # the obj

        # we specify the class which defines the graded components
        GradedComponent = MyGradedComponent


AUTHOR:

- Jean-Baptiste Priez (2014)
"""
#*****************************************************************************
#       Copyright (C) 2014 Jean-Baptiste Priez <jbp@kerios.fr>.
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************
from itertools import imap
from sage.combinat.structures import StructuresClass, Structure
from sage.misc.lazy_attribute import lazy_class_attribute
from sage.rings.integer import Integer
from sage.structure.list_clone import ClonableIntArray
from sage.sets.positive_integers import PositiveIntegers


class Composition(Structure, ClonableIntArray):
    """
    A composition could be represented as a vector of integers so one use
    *ClonableIntArray* to implement our structures.

    In that example, we choose to use a more general structures:
    *ElementWrapper*

    The class *Structure* is a simple class use to not (re)define a classcall
    method. Usually, the classcall is use on elements to avoid explicit parent
    in argument::

        Composition([3,1,2], parent=Compositions())

    TESTS::

        sage: from sage.categories.examples.\
              classes_of_combinatorial_structures import Composition
        sage: I = Composition([2,1,3]); I
        [2, 1, 3]
        sage: I.parent()
        Compositions of integers
        sage: I.grade()
        6

    """

    def check(self):
        """
        The check has to be given to specify the structure

        TESTS::

        sage: from sage.categories.examples.\
              classes_of_combinatorial_structures import Composition
        sage: _ = Composition([2,1,3])
        sage: Composition([0,1])
        Traceback (most recent call last):
        ...
        AssertionError

        """
        assert(all(i in PositiveIntegers() for i in self))

    @lazy_class_attribute
    def _auto_parent_(self):
        """
        I use this trick to not call a Composition with an explicit parent.

        (It is a lazy class attribute to avoid to conflict with *Compositions*)

        TESTS::

            sage: from sage.categories.examples.\
                  classes_of_combinatorial_structures import Composition
            sage: Composition._auto_parent_
            Compositions of integers

        """
        return Compositions()


class Compositions(StructuresClass):
    """
    TESTS::

        sage: C = ClassesOfCombinatorialStructures().example(); C
        Compositions of integers
        sage: TestSuite(C).run()

    """

    def grading(self, I):
        """
        TESTS::

            sage: from sage.categories.examples.\
                  classes_of_combinatorial_structures import Composition,\
                                                             Compositions
            sage: I = Composition([2,1,3]); I
            [2, 1, 3]
            sage: I.parent().grading(I)
            6
            sage: Compositions().grading(I)
            6

        """
        return sum(I)

    def _repr_(self):
        """
        TESTS::

            sage: ClassesOfCombinatorialStructures().example()
            Compositions of integers

        """
        return "Compositions of integers"

    # I have to specify *Compositions* is the parent of the elements
    # *Composition*.
    Element = Composition

    class GradedComponent(StructuresClass.GradedComponent):
        """
        TESTS::

            sage: C = ClassesOfCombinatorialStructures().example()
            sage: C42 = C.graded_component(42)
            sage: TestSuite(C42).run()

        """

        def cardinality(self):
            """
            TESTS::

                sage: ClassesOfCombinatorialStructures().example()\
                      .graded_component(10).cardinality()
                512

            """
            return Integer(2)**(max(0, self.grade()-1))

        def __iter__(self):
            """
            TESTS::

                sage: ClassesOfCombinatorialStructures().example()\
                      .graded_component(4).list()
                [[4], [1, 3], [2, 2], [1, 1, 2], [3, 1], [1, 2, 1],
                 [2, 1, 1], [1, 1, 1, 1]]

            """
            # FIXME: this function is more efficient than the current one (Compositions_n.__iter__).
            def nested(k):
                # little trick to avoid to create too many object *Composition*:
                ## That avoid the trip: Composition(... list(Composition(list(Composition([1])) + [2])) + ...)
                if k == 0: yield ()
                else:
                    for i in range(k):
                        for I in nested(i):
                            yield I + (k-i,)

            return imap(self._element_constructor_, nested(self.grade()))

Example = Compositions