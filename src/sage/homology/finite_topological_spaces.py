r"""
Finite topological spaces

This module implements finite topological spaces and related concepts.

A *finite topological space* is a topological space with finitely many points and
a *finite preordered set* is a finite set with a transitive and reflexive relation.
Finite spaces and finite preordered sets are basically the same objects considered
from different perspectives. Given a finite topological space `X`, for every point
`x\in X` the *minimal open set* `U_x` as the intersection of all the open sets
which contain `x` (it is an open set since arbitrary intersections of open sets
in finite spaces are open). The minimal open sets constitute a basis for the topology
of `X`. Indeed, any open set `U` of `X` is the union of the sets `U_x` with `x\in U`.
This basis is called the *minimal basis of `X`*. A preorder on `X` by `x\leqslant y`
if `x\in U_y`.

If `X` is now a finite preordered set, one can define a topology on `X` given by
the basis `\lbrace y\in X\vert y\leqslant x\rbrace_{x\in X}`. Note that if `y\leqslant x`,
then `y` is contained in every basic set containing `x`, and therefore `y\in U_x`.
Conversely, if `y\in U_x`, then `y\in\lbrace z\in X\vert z\leqslant x\rbrace`.
Therefore `y\leqslant x` if and only if `y\in U_x`. This shows that these two
applications, relating topologies and preorders on a finite set, are mutually
inverse. This simple remark, made in first place by Alexandroff [1], allows us to study
finite spaces by combining Algebraic Topology with the combinatorics arising from
their intrinsic preorder structures. The antisymmetry of a finite preorder
corresponds exactly to the `T_0` separation axiom. Recall that a topological space
`X` is said to be *`T_0`* if for any pair of points in `X` there exists an open
set containing one and only one of them. Therefore finite `T_0`-spaces are in
correspondence with finite partially ordered sets (posets) [2].

Now, if `X = \lbrace x_1, x_2, \ldots , x_n\rbrace` is a finite space and for
each `i` the unique minimal open set containing `x_i` is denoted by `U_i`, a
*topogenous matrix* of the space is a `n \times n` matrix `A = \left[a_{ij}\right]`
defined by `a_{ij} = 1` if `x_i \in U_j` and `a_{ij} = 0` otherwise (this is the
transposed matrix of the Definition 1 in [3]). A finite space `X` is `T_0` if and
only if the topogenous matrix `A` defined above is similar (via a permutation matrix)
to a certain upper triangular matrix [3]. This is the reason one can assume that
the topogenous matrix of a finite `T_0`-space is upper triangular.


AUTHOR::

- Julián Cuevas-Rozo (2020): Initial version

REFERENCES::

- [1] Alexandroff P., *Diskrete Räume*, Mat. Sb. (N.S.) 2, 501--518 (1937).
- [2] Barmak, J.A., *Algebraic topology of finite topological spaces and applications*.
      Lecture Notes in Mathematics Vol. 2032 (2011).
- [3] Shiraki M., *On finite topological spaces*, Rep. Fac. Sci. Kagoshima Univ.
      1, 1--8 (1968).

"""
# ****************************************************************************
#       Copyright (C) 2020 Julián Cuevas-Rozo <jlcrozo@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  https://www.gnu.org/licenses/
# ****************************************************************************
from sage.structure.parent import Parent
from sage.matrix.constructor import matrix
from sage.matrix.matrix_integer_sparse import Matrix_integer_sparse
from sage.combinat.posets.posets import Poset


def dict_to_matrix(ordered_eltos, dictionary):
    r"""
    Return a matrix from the information given by ``dictionary``.    
    INPUT:

    - ``ordered_eltos`` -- a list.

    - ``dictionary`` -- a dict whose key list is ``ordered_eltos`` and its values
      are sets of elements in ``ordered_eltos``.

    OUTPUT::

    - A binary matrix whose `(i,j)` entry is equal to 1 if and only if ``ordered_eltos[i]``
      is in ``dictionary[ordered_eltos[j]]``.

    EXAMPLES::

        sage: from sage.homology.finite_topological_spaces import dict_to_matrix
        sage: ordered_eltos = ['a', 'b', 3, 4, 'e']
        sage: dictionary = {'a': set(), 'b': {3}, 3: {3, 4, 'a'}, 'e': {'a'}, 4: set()}
        sage: dict_to_matrix(ordered_eltos, dictionary)
        [0 0 1 0 1]
        [0 0 0 0 0]
        [0 1 1 0 0]
        [0 0 1 0 0]
        [0 0 0 0 0]
    """
    n = len(ordered_eltos)
    nonzero = {(ordered_eltos.index(x), j):1 for j in range(n) \
               for x in dictionary[ordered_eltos[j]]}
    return matrix(n, nonzero)

def FiniteSpace(data, elements=None, is_T0=False):
    r"""
    Construct a finite topological space from various forms of input data.

    INPUT:

    - ``data`` -- different input are accepted by this constructor:

      1. A dictionary representing the minimal basis of the space.

      2. A list or tuple of minimal open sets (in this case the elements of the 
         space are assumed to be ``range(n)`` where ``n`` is the length of ``data``).

      3. A topogenous matrix (assumed sparse). If ``elements=None``, the elements
         of the space are assumed to be ``range(n)`` where ``n`` is the dimension
         of the matrix.

      4. A finite poset (by now if ``poset._is_facade = False``, the methods are
         not completely tested).

    - ``elements`` -- it is ignored when data is of type 1, 2 or 4. When ``data``
      is a topogenous matrix, this parameter gives the underlying set of the space.

    EXAMPLES::

    A dictionary as ``data``::

        sage: from sage.homology.finite_topological_spaces import FiniteSpace
        sage: T = FiniteSpace({'a': {'a', 'c'}, 'b': {'b'}, 'c':{'a', 'c'}}) ; T
        Finite topological space of 3 points with minimal basis
         {'a': {'c', 'a'}, 'b': {'b'}, 'c': {'c', 'a'}}
        sage: type(T)
        <class 'sage.homology.finite_topological_spaces.FiniteTopologicalSpace'>
        sage: FiniteSpace({'a': {'a', 'b'}})
        Traceback (most recent call last)
        ...
        ValueError: The data does not correspond to a valid dictionary
        sage: FiniteSpace({'a': {'a', 'b'}, 'b': {'a', 'b'}, 'c': {'a', 'c'}})
        Traceback (most recent call last)
        ...
        ValueError: The introduced data does not define a topology

    When ``data`` is a tuple or a list, the elements are in ``range(n)`` where
    ``n`` is the lenght of ``data``::

        sage: from sage.homology.finite_topological_spaces import FiniteSpace
        sage: T = FiniteSpace([{0, 3}, {1, 3}, {2, 3}, {3}]) ; T
        Finite T0 topological space of 4 points with minimal basis
         {0: {0, 3}, 1: {1, 3}, 2: {2, 3}, 3: {3}}
        sage: type(T)
        <class 'sage.homology.finite_topological_spaces.FiniteTopologicalSpace_T0'>
        sage: T.elements()
        [3, 0, 1, 2]
        sage: FiniteSpace(({0, 2}, {0, 2}))
        Traceback (most recent call last)
        ...
        ValueError: This kind of data assume the elements are in range(2)

    If ``data`` is a topogenous matrix, the parameter ``elements``, when it is not
    ``None``, determines the list of elements of the space::

        sage: from sage.homology.finite_topological_spaces import FiniteSpace
        sage: mat_dict = {(0, 0): 1, (0, 3): 1, (0, 4): 1, (1, 1): 1, (1, 2): 1, (2, 1): 1, \
        ....:             (2, 2): 1, (3, 3): 1, (3, 4): 1, (4, 3): 1, (4, 4): 1}
        sage: mat = matrix(mat_dict) ; mat
        [1 0 0 1 1]
        [0 1 1 0 0]
        [0 1 1 0 0]
        [0 0 0 1 1]
        [0 0 0 1 1]
        sage: T = FiniteSpace(mat) ; T
        Finite topological space of 5 points with minimal basis
         {0: {0}, 1: {1, 2}, 2: {1, 2}, 3: {0, 3, 4}, 4: {0, 3, 4}}
        sage: T.elements()
        [0, 1, 2, 3, 4]
        sage: M = FiniteSpace(mat, elements=(5, 'e', 'h', 0, 'c')) ; M
        Finite topological space of 5 points with minimal basis
         {5: {5}, 'e': {'h', 'e'}, 'h': {'h', 'e'}, 0: {0, 'c', 5}, 'c': {0, 'c', 5}}
        sage: M.elements()
        [5, 'e', 'h', 0, 'c']
        sage: FiniteSpace(mat, elements=[5, 'e', 'h', 0, 0])
        Traceback (most recent call last)
        ...
        AssertionError: Not valid list of elements

    Finally, when ``data`` is a finite poset, the corresponding finite T0 space
    is constructed::

        sage: from sage.homology.finite_topological_spaces import FiniteSpace
        sage: P = Poset([[1, 2], [4], [3], [4], []])
        sage: T = FiniteSpace(P) ; T
        Finite T0 topological space of 5 points with minimal basis
         {0: {0}, 1: {0, 1}, 2: {0, 2}, 3: {0, 2, 3}, 4: {0, 1, 2, 3, 4}}
        sage: type(T)
        <class 'sage.homology.finite_topological_spaces.FiniteTopologicalSpace_T0'>
        sage: T.poset() == P
        True
    """
    if hasattr(data, '_hasse_diagram'): # isinstance(data, FinitePosets): # type 4
        minimal_basis = {x: set(data.order_ideal([x])) for x in data.list()}
        topogenous = data.lequal_matrix()
        return FiniteTopologicalSpace_T0(elements=data.list(), minimal_basis=minimal_basis,
                                         topogenous=topogenous, poset=data)

    topogenous = None

    if isinstance(data, dict): # type 1
        n = len(data)
        eltos = set()
        for B in data.values():
            eltos = eltos.union(B)
        if not eltos==set(data):
            raise ValueError("The data does not correspond to a valid dictionary")
        basis = data

    if isinstance(data, (list, tuple)): # type 2
        n = len(data)
        eltos = set()
        # In this case, the elements are assumed being range(n)
        for B in data:
            eltos = eltos.union(B)
        if not eltos==set(range(n)):
            raise ValueError("This kind of data assume the elements are in range({})" \
                             .format(n))
        basis = dict(zip(range(n), data))

    if isinstance(data, Matrix_integer_sparse): # type 3
        n = data.dimensions()[0]
        assert n==data.dimensions()[1], \
               "Topogenous matrices are square"
        assert set(data.dict().values())=={1}, \
               "Topogenous matrices must have entries in {0,1}"
        basis = {}
        # Extracting a minimal basis from the topogenous matrix info
        if elements:
            if not isinstance(elements, (list, tuple)):
                raise ValueError("Parameter 'elements' must be a list or a tuple")
            assert len(set(elements))==n, \
                   "Not valid list of elements"
            for j in range(n):
                Uj = set([elements[i] for i in data.nonzero_positions_in_column(j)])
                basis[elements[j]] = Uj
            eltos = elements
        else:
            for j in range(n):
                Uj = set(data.nonzero_positions_in_column(j))
                basis[j] = Uj
            eltos = range(n)
        topogenous = data

    # This fixes a topological sort (it guarantees an upper triangular topogenous matrix)
    eltos = list(eltos)
    eltos.sort(key = lambda x: len(basis[x]))

    # Now, check that 'basis' effectively defines a minimal basis for a topology
    if topogenous==None:
        topogenous = dict_to_matrix(eltos, basis)
    squared = topogenous*topogenous
    if not topogenous.nonzero_positions() == squared.nonzero_positions():
        raise ValueError("The introduced data does not define a topology")

    if is_T0:
        return FiniteTopologicalSpace_T0(elements=eltos, minimal_basis=basis,
                                         topogenous=topogenous)
    # Determine if the finite space is T0
    partition = []
    eltos2 = eltos.copy()
    while eltos2:
        x = eltos2.pop(0)
        Ux = basis[x] - set([x])
        equiv_class = set([x])
        for y in Ux:
            if x in basis[y]:
                equiv_class = equiv_class.union(set([y]))
                eltos2.remove(y)
        partition.append(equiv_class)

    if len(partition)==n:
        return FiniteTopologicalSpace_T0(elements=eltos, minimal_basis=basis,
                                         topogenous=topogenous)
    result = FiniteTopologicalSpace(elements=eltos, minimal_basis=basis,
                                    topogenous=topogenous)
    setattr(result, '_T0', partition)
    return result


class FiniteTopologicalSpace(Parent):
    r"""
    Finite topological spaces.

    Users should not call this directly, but instead use :func:`FiniteSpace`.
    See that function for more documentation.
    """
    def __init__(self, elements, minimal_basis, topogenous):
        r"""
        Define a finite topological space.

        INPUT:

        - ``elements`` -- list of the elements of the space. 

        - ``minimal_basis`` -- a dictionary where the values are sets representing
          the minimal open sets containing the respective key.

        - ``topogenous`` -- a topogenous matrix of the finite space corresponding
          to the order given by ``elements``.

        EXAMPLES::

            sage: from sage.homology.finite_topological_spaces import FiniteTopologicalSpace
            sage: elements = [1, 2, 'a', 3]
            sage: minimal_basis = {'a': {3, 'a'}, 3: {3, 'a'}, 2: {2, 1}, 1: {1}}
            sage: mat_dict = {(0, 0): 1, (0, 1): 1, (1, 1): 1, (2, 2): 1, \
            ....:             (2, 3): 1, (3, 2): 1, (3, 3): 1}
            sage: T = FiniteTopologicalSpace(elements, minimal_basis, matrix(mat_dict)) ; T
            Finite topological space of 4 points with minimal basis
             {'a': {3, 'a'}, 3: {3, 'a'}, 2: {1, 2}, 1: {1}}
            sage: T.topogenous_matrix() == matrix(mat_dict)
            True
        """
        # Assign attributes
        self._cardinality = len(elements)
        self._elements = elements
        self._minimal_basis = minimal_basis
        self._topogenous = topogenous

    def __repr__(self):
        r"""
        Print representation.

        EXAMPLES::

            sage: from sage.homology.finite_topological_spaces import FiniteSpace
            sage: FiniteSpace({0: {0, 1}, 1: {0, 1}})
            Finite topological space of 2 points with minimal basis
             {0: {0, 1}, 1: {0, 1}}
            sage: Q = Poset((divisors(120), attrcall("divides")), linear_extension=True)
            sage: FiniteSpace(Q)
            Finite T0 topological space of 16 points
        """
        n = self._cardinality
        if n < 10:
            return "Finite topological space of {} points with minimal basis \n {}" \
                   .format(n, self._minimal_basis)
        else:
            return "Finite topological space of {} points".format(n)

    def __contains__(self, x):
        r"""
        Return ``True`` if ``x`` is an element of the finite space.

        EXAMPLES::

            sage: from sage.homology.finite_topological_spaces import FiniteSpace
            sage: P = Poset((divisors(6), attrcall("divides")), linear_extension=True)
            sage: T = FiniteSpace(P)
            sage: 3 in T
            True
            sage: 4 in T
            False
        """
        return x in self._elements

    def elements(self):
        r"""
        Return the list of elements in the underlying set of the finite space.

        EXAMPLES::

            sage: from sage.homology.finite_topological_spaces import FiniteSpace
            sage: T = FiniteSpace(({0}, {1}, {2, 3}, {3}))
            sage: T.elements()
            [0, 1, 3, 2]
        """
        return self._elements
        
    def underlying_set(self):
        r"""
        Return the underlying set of the finite space.
        
        EXAMPLES::
        
            sage: from sage.homology.finite_topological_spaces import FiniteSpace
            sage: T = FiniteSpace(({0}, {1}, {2, 3}, {3}))
            sage: T.underlying_set()
            
        """
        return set(self._elements)

    def subspace(self, points=None, is_T0=False):
        r"""
        Return the subspace whose elements are in ``points``.

        INPUT:

        - ``points`` -- (default ``None``) A tuple, list or set contained in ``self.elements()``.

        - ``is_T0`` -- if it is known that the resulting subspace is T0, fix ``True``
          (default ``False``).

        EXAMPLES::

            sage: from sage.homology.finite_topological_spaces import FiniteSpace
            sage: T = FiniteSpace(({0}, {1, 3, 4}, {0, 2, 5}, {1, 3, 4}, {1, 3, 4}, {0, 2, 5}))
            sage: T.subspace((0, 3, 5))
            Finite T0 topological space of 3 points with minimal basis
             {0: {0}, 3: {3}, 5: {0, 5}}
            sage: T.subspace([4])
            Finite T0 topological space of 1 points with minimal basis
             {4: {4}}
            sage: T.subspace() == T
            True
        """
        if points==None:
            return self
        assert isinstance(points, (tuple, list, set)), \
               "Parameter must be of type tuple, list or set"
        points = set(points)
        assert points <= set(self._elements), \
               "There are points that are not in the space"
        if points==set(self._elements):
            return self
        minimal_basis = {x: self._minimal_basis[x] & points for x in points}
        return FiniteSpace(minimal_basis, is_T0=is_T0)

    def cardinality(self):
        r"""
        Return the number of elements in the finite space.

        EXAMPLES::

            sage: from sage.homology.finite_topological_spaces import FiniteSpace
            sage: P = Poset((divisors(360), attrcall("divides")), linear_extension=True)
            sage: T = FiniteSpace(P)
            sage: T.cardinality() == P.cardinality()
            True
        """
        return self._cardinality

    def minimal_basis(self):
        r"""
        Return the minimal basis that generates the topology of the finite space.

        OUTPUT:

        - A dictionary whose keys are the elements of the space and the values
          are the minimal open sets containing the respective element.

        EXAMPLES::
        
            sage: from sage.homology.finite_topological_spaces import FiniteSpace
            sage: T = FiniteSpace(({0}, {0, 1, 2}, {0, 1, 2}, {3, 4}, {3, 4}))
            sage: T.minimal_basis()
            {0: {0}, 1: {0, 1, 2}, 2: {0, 1, 2}, 3: {3, 4}, 4: {3, 4}}
            sage: M = T.equivalent_T0()
            sage: M.minimal_basis()
            {0: {0}, 1: {0, 1}, 3: {3}}
        """
        return self._minimal_basis

    def minimal_open_set(self, x):
        r"""
        Return the minimal open set containing ``x``.

        EXAMPLES::

            sage: from sage.homology.finite_topological_spaces import FiniteSpace
            sage: T = FiniteSpace(({0}, {0, 1, 2}, {0, 1, 2}, {3, 4}, {3, 4}))
            sage: T.minimal_open_set(1)
            {0, 1, 2}
            sage: T.Ux(4)
            {3, 4}
            sage: T.Ux(5)
            Traceback (most recent call last)
            ...
            ValueError: The point 5 is not an element of the space
        """
        if not x in self:
            raise ValueError("The point {} is not an element of the space".format(x))
        else:
            return self._minimal_basis[x]
            
    Ux = minimal_open_set # Notation extensively used in the literature

    def topogenous_matrix(self):
        r"""
        Return the topogenous matrix of the finite space.

        OUTPUT:

        - A binary matrix whose `(i,j)` entry is equal to 1 if and only if ``self._elements[i]``
          is in ``self._minimal_basis[self._elements[j]]``.

        EXAMPLES::

            sage: from sage.homology.finite_topological_spaces import FiniteSpace
            sage: T = FiniteSpace(({0}, {1, 3, 4}, {0, 2, 5}, {1, 3, 4}, {1, 3, 4}, {0, 2, 5}))
            sage: T.topogenous_matrix()
            [1 0 1 0 0 1]
            [0 1 0 1 1 0]
            [0 0 1 0 0 1]
            [0 1 0 1 1 0]
            [0 1 0 1 1 0]
            [0 0 1 0 0 1]
            sage: T0 = T.equivalent_T0()
            sage: T0.topogenous_matrix()
            [1 0 1]
            [0 1 0]
            [0 0 1]
        """
        return self._topogenous

    def is_T0(self):
        r"""
        Return ``True`` if the finite space satisfies the T0 separation axiom.

        EXAMPLES::

            sage: from sage.homology.finite_topological_spaces import FiniteSpace
            sage: T = FiniteSpace([{0}, {1}, {2, 3}, {2, 3}])
            sage: T.is_T0()
            False
            sage: T.equivalent_T0().is_T0()
            True
        """
        return isinstance(self, FiniteTopologicalSpace_T0)

    def equivalent_T0(self, points=None, check=True):
        r"""
        Return a finite T0 space homotopy equivalent to ``self``.

        INPUT:

        - ``points`` -- (default ``None``) a tuple, list or set of representatives
          elements of the equivalent classes induced by the partition ``self._T0``.

        - ``check`` -- if ``True`` (default), it is checked that ``points`` effectively
          defines a set of representatives of the partition ``self._T0``.

        EXAMPLES::

            sage: from sage.homology.finite_topological_spaces import FiniteSpace
            sage: T = FiniteSpace(({0}, {1, 3, 4}, {0, 2, 5}, {1, 3, 4}, {1, 3, 4}, {0, 2, 5}))
            sage: T.is_T0()
            False
            sage: T._T0
            [{0}, {1, 3, 4}, {2, 5}]
            sage: M1 = T.equivalent_T0()
            sage: M1.is_T0()
            True
            sage: M1.elements()
            [0, 1, 2]
            sage: M2 = T.equivalent_T0(points={0,4,5}, check=False)
            sage: M2.elements()
            [0, 4, 5]
            sage: T.equivalent_T0(points={0,3,4})
            Traceback (most recent call last):
            ...
            ValueError: Parameter 'points' is not a valid set of representatives
        """
        if self._T0==True:
            return self
        else:
            if points==None:
                points = [list(A)[0] for A in self._T0]
            elif check==True:
                assert isinstance(points, (tuple, list, set)), \
                       "Parameter 'points' must be of type tuple, list or set"
                assert len(points)==len(self._T0), \
                       "Parameter 'points' does not have a valid length"
                points2 = set(points.copy())
                partition = self._T0.copy()
                while points2:
                    x = points2.pop()
                    class_x = None
                    for k in range(len(partition)):
                        if x in partition[k]:
                            class_x = k
                            partition.pop(k)
                            break
                    if class_x==None:
                            raise ValueError("Parameter 'points' is not a valid set of representatives")
            return self.subspace(points, is_T0=True)

    def is_interior_point(self, x, E):
        r"""
        Return ``True`` if ``x`` is an interior point of ``E`` in the finite space.

        EXAMPLES::

            sage: from sage.homology.finite_topological_spaces import FiniteSpace
            sage: T = FiniteSpace([{0, 1}, {1}, {2, 3, 4}, {2, 3, 4}, {4}])
            sage: T.is_interior_point(1, {1, 2, 3})
            True
            sage: T.is_interior_point(2, {1, 2, 3})
            False
            sage: T.is_interior_point(1, set())
            False
            sage: T.is_interior_point(3, T.underlying_set())
            True
        """
        assert x in self.underlying_set() , "Parameter 'x' must be an element of the space"
        assert E <= self.underlying_set() , "Parameter 'E' must be a subset of the underlying set"
        if not x in E:
            return False
        return self._minimal_basis[x] <= E

    def interior(self, E):
        r"""
        Return the interior of a subset in the finite space.

        EXAMPLES::

            sage: from sage.homology.finite_topological_spaces import FiniteSpace
            sage: T = FiniteSpace([{0, 1}, {1}, {2, 3, 4}, {2, 3, 4}, {4}])
            sage: T.interior({1, 2, 3})
            {1}
            sage: T.interior({1, 2, 3, 4})
            {1, 2, 3, 4}
            sage: T.interior({2, 3})
            set()
            
        TESTS::
        
            sage: import random
            sage: T = FiniteSpace(posets.RandomPoset(30, 0.5))
            sage: X = T.underlying_set()
            sage: k = randint(0,len(X))
            sage: E = set(random.sample(X, k))
            sage: Int = T.interior(E)
            sage: T.is_open(Int)
            True
            sage: T.interior(Int) == Int
            True
            sage: Int == X - T.closure(X - E)
            True
            sage: m = randint(0,len(X))
            sage: M = set(random.sample(X, m))
            sage: T.interior(E & M) == Int & T.interior(M)
            True
        """
        X = self.underlying_set()
        if E == X or E == set():
            return E
        assert E < X , "The parameter must be a subset of the underlying set"
        return set([x for x in E if self.is_interior_point(x, E)])

    def is_open(self, E):
        r"""
        Return ``True`` if ``E`` is an open subset of the finite space.

        EXAMPLES::

            sage: from sage.homology.finite_topological_spaces import FiniteSpace
            sage: T = FiniteSpace([{0, 1}, {1}, {2, 3, 4}, {2, 3, 4}, {4}])
            sage: T.is_open({0})
            False
            sage: T.is_open({0, 1})
            True
            sage: T.is_open({0, 1, 4})
            True
            sage: T.is_open(set())
            True
        """
        return E == self.interior(E)

    def is_closed(self, E):
        r"""
        Return ``True`` if ``E`` is a closed subset of the finite space.

        EXAMPLES::

            sage: from sage.homology.finite_topological_spaces import FiniteSpace
            sage: T = FiniteSpace({'a':{'a','b'},'b':{'a','b'},'c':{'c','d'},'d':{'d'}})
            sage: T.is_closed({'a','b','c'})
            True
            sage: T.is_closed({'b'})
            False
        """
        X = self.underlying_set() 
        return self.is_open(X - E)

    def is_exterior_point(self, x, E):
        r"""
        Return ``True`` if ``x`` is an exterior point of ``E`` in the finite space.

        EXAMPLES::

            sage: from sage.homology.finite_topological_spaces import FiniteSpace
            sage: T = FiniteSpace([{0, 1}, {1}, {2, 3, 4}, {2, 3, 4}, {4}])
            sage: T.is_exterior_point(1, {2, 3})
            True
            sage: T.is_exterior_point(3, {0, 1, 2})
            False
        """
        return self._minimal_basis[x].isdisjoint(E)

    def exterior(self, E):
        r"""
        Return the exterior of a subset in the finite space.

        EXAMPLES::

            sage: from sage.homology.finite_topological_spaces import FiniteSpace
            sage: T = FiniteSpace([{0, 1}, {1}, {2, 3, 4}, {2, 3, 4}, {4}])
            sage: T.exterior({2})
            {0, 1, 4}
            sage: T.exterior({2, 4})
            {0, 1}

        TESTS::

            sage: import random
            sage: T = FiniteSpace(posets.RandomPoset(30, 0.5))
            sage: X = T.underlying_set()
            sage: k = randint(0,len(X))
            sage: E = set(random.sample(X, k))
            sage: Ext = T.exterior(E)
            sage: Ext.isdisjoint(E)
            True
            sage: Ext == T.interior(X - E)
            True
            sage: Ext == X - T.closure(E)
            True
            sage: T.interior(E) <= T.exterior(Ext)
            True
        """
        X = self.underlying_set()
        if E == X:
            return set()
        if E == set():
            return X
        assert E < X , "The parameter must be a subset of the underlying set"
        return set([x for x in X - E if self.is_exterior_point(x, E)])

    def is_boundary_point(self, x, E):
        r"""
        Return ``True`` if ``x`` is a boundary point of ``E`` in the finite space.

        EXAMPLES::

            sage: from sage.homology.finite_topological_spaces import FiniteSpace
            sage: T = FiniteSpace([{0, 1}, {1}, {2, 3, 4}, {2, 3, 4}, {4}])
            sage: T.is_boundary_point(0, {1, 2, 3})
            True
            sage: T.is_boundary_point(1, {2, 3, 4})
            False
        """
        Ux = self._minimal_basis[x]
        return bool(Ux & E) and not bool(Ux <= E)

    def boundary(self, E):
        r"""
        Return the boundary of a subset in the finite space.

        EXAMPLES::

            sage: from sage.homology.finite_topological_spaces import FiniteSpace
            sage: T = FiniteSpace([{0, 1}, {1}, {2, 3, 4}, {2, 3, 4}, {4}])
            sage: T.boundary({1})
            {0}
            sage: T.boundary({2, 3})
            {2, 3}

        TESTS::

            sage: import random
            sage: T = FiniteSpace(posets.RandomPoset(30, 0.5))
            sage: X = T.underlying_set()
            sage: k = randint(0,len(X))
            sage: E = set(random.sample(X, k))
            sage: Fr = T.boundary(E)
            sage: T.is_closed(Fr)
            True
            sage: Fr == T.boundary(X - E)
            True
            sage: Fr == T.closure(E) - T.interior(E)
            True
            sage: Fr == T.closure(E) & T.closure(X - E)
            True
            sage: T.interior(E) == E - Fr
            True
            sage: T.boundary(Fr) <= Fr
            True
            sage: T.boundary(T.boundary(Fr)) == T.boundary(Fr)
            True
            sage: X == Fr.union(T.interior(E), T.exterior(E))|||
            True
        """
        X = self.underlying_set()
        if E == X or E == set():
            return set()
        assert E < X , "The parameter must be a subset of the underlying set"
        return set([x for x in X if self.is_boundary_point(x, E)])

    def is_limit_point(self, x, E):
        r"""
        Return ``True`` if ``x`` is a limit point of ``E`` in the finite space.

        EXAMPLES::

            sage: from sage.homology.finite_topological_spaces import FiniteSpace
            sage: T = FiniteSpace([{0, 1}, {1}, {2, 3, 4}, {2, 3, 4}, {4}])
            sage: T.is_limit_point(0, {1})
            True
            sage: T.is_limit_point(1, {0, 1})
            False
        """
        Ux_minus_x = self._minimal_basis[x] - {x}
        return not Ux_minus_x.isdisjoint(E)

    def derived(self, E):
        r"""
        Return the derived set of a subset in the finite space.

        EXAMPLES::

            sage: from sage.homology.finite_topological_spaces import FiniteSpace
            sage: T = FiniteSpace([{0, 1}, {1}, {2, 3, 4}, {2, 3, 4}, {4}])
            sage: T.derived({0, 1, 2})
            {0, 3}
            sage: T.derived({3, 4})
            {2, 3}

        TESTS::

            sage: import random
            sage: T = FiniteSpace(posets.RandomPoset(30, 0.5))
            sage: X = T.underlying_set()
            sage: k = randint(0,len(X))
            sage: E = set(random.sample(X, k))
            sage: Der = T.derived(E)
            sage: T.derived(Der) <= E.union(Der)
            True
            sage: T.closure(E) == E.union(Der)
            True
        """
        X = self.underlying_set()
        if E == X or E == set():
            return E
        assert E < X , "The parameter must be a subset of the underlying set"
        return set([x for x in X if self.is_limit_point(x, E)])

    def is_closure_point(self, x, E):
        r"""
        Return ``True`` if ``x`` is a point of closure of ``E`` in the finite space.

        EXAMPLES::

            sage: from sage.homology.finite_topological_spaces import FiniteSpace
            sage: T = FiniteSpace([{0, 1}, {1}, {2, 3, 4}, {2, 3, 4}, {4}])
            
        """
        return not self._minimal_basis[x].isdisjoint(E)

    def closure(self, E):
        r"""
        Return the closure of a subset in the finite space.

        EXAMPLES::

            sage: from sage.homology.finite_topological_spaces import FiniteSpace
            sage: T = FiniteSpace([{0, 1}, {1}, {2, 3, 4}, {2, 3, 4}, {4}])
            sage: T.closure({0, 2})
            {0, 2, 3}
            sage: T.closure({0})
            {0}

        TESTS::
        
            sage: import random
            sage: T = FiniteSpace(posets.RandomPoset(30, 0.5))
            sage: X = T.underlying_set()
            sage: k = randint(0,len(X))
            sage: E = set(random.sample(X, k))
            sage: Cl = T.closure(E)
            sage: T.is_closed(Cl)
            True
            sage: T.closure(Cl) == Cl
            True
            sage: Cl == X - T.interior(X - E)
            True
            sage: T.interior(T.boundary(Cl)) == set()
            True
            sage: Cl == E.union(T.boundary(E))
            True
            sage: m = randint(0,len(X))
            sage: M = set(random.sample(X, m))
            sage: T.closure(E.union(M)) == Cl.union(T.closure(M))
            True
        """
        X = self.underlying_set()
        if E == X or E == set():
            return E
        assert E < X , "The parameter must be a subset of the underlying set"
        return E.union(set([x for x in X - E if self.is_closure_point(x, E)]))

    def is_dense(self, E):
        r"""
        Return ``True`` if ``E`` is dense in the finite space.

        EXAMPLES::

            sage: from sage.homology.finite_topological_spaces import FiniteSpace
            sage: T = FiniteSpace([{0, 1, 2}, {0, 1, 2}, {2}])
            sage: T.is_dense({2})
            True
            sage: T.is_dense({0, 1})
            False
        """
        return self.closure(E) == self.underlying_set()

    def is_isolated_point(self, x, E=None):
        r"""
        Return ``True`` if ``x`` is an isolated point of ``E`` in the finite space.
        If ``E`` is ``None``, return ``True`` if ``x`` is an isolated point of 
        the finite space.

        EXAMPLES::

            sage: from sage.homology.finite_topological_spaces import FiniteSpace
            sage: T = FiniteSpace([{0, 1}, {1}, {2, 3, 4}, {2, 3, 4}, {4}])
            sage: T.is_isolated_point(0)
            False
            sage: T.is_isolated_point(0, {0, 2, 3, 4})
            True
        """
        if E:
            return (self._minimal_basis[x] & E) == set([x])
        else:
            return self._minimal_basis[x] == set([x])
            
    def isolated_set(self, E=None):
        r"""
        Return the set of isolated points of a subset in the finite space.

        EXAMPLES::

            sage: from sage.homology.finite_topological_spaces import FiniteSpace
            sage: T = FiniteSpace([{0, 1}, {1}, {2, 3, 4}, {2, 3, 4}, {4}])
            sage: T.isolated_set()
            {1, 4}
            sage: T.isolated_set({0, 2, 3, 4})
            {0, 4}

        TESTS::

            sage: import random
            sage: T = FiniteSpace(posets.RandomPoset(30, 0.5))
            sage: X = T.underlying_set()
            sage: k = randint(0,len(X))
            sage: E = set(random.sample(X, k))
            sage: Iso = T.isolated_set(E)
            sage: T.closure(E) == Iso.union(T.derived(E))
            True
        """
        if E==None: 
            E = self.underlying_set()
        return set([x for x in E if self.is_isolated_point(x, E)])


class FiniteTopologicalSpace_T0(FiniteTopologicalSpace):
    r"""
    Finite topological spaces satisfying the T0 separation axiom (Kolmogorov spaces).

    Users should not call this directly, but instead use :func:`FiniteSpace`.
    See that function for more documentation.
    """
    def __init__(self, elements, minimal_basis, topogenous, poset=None):
        r"""
        Define a finite T0 topological space.

        INPUT:

        - ``elements`` -- list of the elements of the space. 

        - ``minimal_basis`` -- a dictionary where the values are sets representing
          the minimal open sets containing the respective key.

        - ``topogenous`` -- a topogenous matrix of the finite space corresponding
          to the order given by ``elements`` (it is assumed upper triangular).

        - ``poset`` -- a poset corresponding to the finite space (Alexandroff
          correspondence) (default ``None``).

        EXAMPLES::

            sage: from sage.homology.finite_topological_spaces import FiniteTopologicalSpace_T0
            sage: elements = [0, 1, 2, 3]
            sage: minimal_basis = {0: {0}, 1: {0, 1}, 2: {0, 1, 2}, 3: {0, 3}}
            sage: mat_dict = {(0, 0): 1, (0, 1): 1, (0, 2): 1, (0, 3): 1, \
            ....:             (1, 1): 1, (1, 3): 1, (2, 2): 1, (3, 3): 1}
            sage: T = FiniteTopologicalSpace_T0(elements, minimal_basis, matrix(mat_dict)); T
            Finite T0 topological space of 4 points with minimal basis
             {0: {0}, 1: {0, 1}, 2: {0, 1, 2}, 3: {0, 3}}
        """
        FiniteTopologicalSpace.__init__(self, elements, minimal_basis, topogenous)
        if poset:
            # isinstance(poset, FinitePosets)
            assert hasattr(poset, '_hasse_diagram'), \
                   "Parameter 'poset' must be a real poset!"
            # Verify the coherence of the parameters
            assert set(self._elements)==set(poset.list()), \
                   "Elements of poset and minimal_basis do not coincide"
            self._elements = poset.list()
        else:
            # Construir el poset
            elmts = self._elements
            f = lambda x, y: self._topogenous[elmts.index(x), elmts.index(y)]==1
            poset = Poset((elmts, f), linear_extension=True) 
        self._poset = poset
        self._T0 = True

    def __repr__(self):
        r"""
        Print representation.

        EXAMPLES::

            sage: from sage.homology.finite_topological_spaces import FiniteSpace
            sage: P = Poset((divisors(6), attrcall("divides")), linear_extension=True)
            sage: FiniteSpace(P)
            Finite T0 topological space of 4 points with minimal basis
             {1: {1}, 2: {1, 2}, 3: {1, 3}, 6: {1, 2, 3, 6}}
            sage: Q = Poset((divisors(120), attrcall("divides")), linear_extension=True)
            sage: FiniteSpace(Q)
            Finite T0 topological space of 16 points
        """
        n = self._cardinality
        if n < 10:
            return "Finite T0 topological space of {} points with minimal basis \n {}" \
                   .format(n, self._minimal_basis)
        else:
            return "Finite T0 topological space of {} points".format(n)

    def poset(self):
        r"""
        Return the corresponding poset of the finite space (Alexandroff correspondence).

        EXAMPLES::

            sage: from sage.homology.finite_topological_spaces import FiniteSpace
            sage: minimal_basis = ({0}, {0, 1}, {0, 1, 2}, {0, 3})
            sage: T = FiniteSpace(minimal_basis) ; T
            Finite T0 topological space of 4 points with minimal basis
             {0: {0}, 1: {0, 1}, 2: {0, 1, 2}, 3: {0, 3}}
            sage: T.poset()
            Finite poset containing 4 elements with distinguished linear extension

            sage: P = Poset((divisors(12), attrcall("divides")), linear_extension=True)
            sage: T = FiniteSpace(P)
            sage: T.poset() == P
            True
        """
        return self._poset
        
        
