"""
Orthogonal arrays

This module gathers anything related to orthogonal arrays, and, incidentally,
to transversal designs.

.. TODO::

    Implement an improvement of Wilson's construction for u=1,2 in [CD96]_

REFERENCES:

.. [CD96] Making the MOLS table
  Charles Colbourn and Jeffrey Dinitz
  Computational and constructive design theory
  vol 368,pages 67-134
  1996

Functions
---------
"""
from sage.misc.cachefunc import cached_function

def transversal_design(k,n,check=True,availability=False, who_asked=tuple()):
    r"""
    Return a transversal design of parameters `k,n`.

    A transversal design of parameters `k, n` is a collection `\mathcal{S}` of
    subsets of `V = V_1 \cup \cdots \cup V_k` (where the *groups* `V_i` are
    disjoint and have cardinality `n`) such that:

    * Any `S \in \mathcal{S}` has cardinality `k` and intersects each group on
      exactly one element.

    * Any two elements from distincts groups are contained in exactly one
      element of `\mathcal{S}`.

    More general definitions sometimes involve a `\lambda` parameter, and we
    assume here that `\lambda=1`.

    For more information on transversal designs, see
    `<http://mathworld.wolfram.com/TransversalDesign.html>`_.

    INPUT:

    - `n,k` -- integers.

    - ``check`` -- (boolean) Whether to check that output is correct before
      returning it. As this is expected to be useless (but we are cautious
      guys), you may want to disable it whenever you want speed. Set to
      ``True`` by default.

    - ``availability`` (boolean) -- if ``availability`` is set to ``True``, the
      function only returns boolean answers according to whether Sage knows how
      to build such a design. This should be much faster than actually building
      it.

    - ``who_asked`` (internal use only) -- because of the equivalence between
      OA/TD/MOLS, each of the three constructors calls the others. We must keep
      track of who calls who in order to avoid infinite loops. ``who_asked`` is
      the tuple of the other functions that were called before this one on the
      same input `k,n`.

    .. NOTE::

        This function returns transversal designs with
        `V_1=\{0,\dots,n-1\},\dots,V_k=\{(k-1)n,\dots,kn-1\}`.

    .. SEEALSO::

        :func:`orthogonal_array` -- a tranversal design is an orthogonal array
        with `t=2`.

    EXAMPLES::

        sage: designs.transversal_design(5,5)
        [[0, 5, 10, 15, 20], [0, 6, 12, 18, 24], [0, 7, 14, 16, 23],
         [0, 8, 11, 19, 22], [0, 9, 13, 17, 21], [1, 6, 11, 16, 21],
         [1, 7, 13, 19, 20], [1, 8, 10, 17, 24], [1, 9, 12, 15, 23],
         [1, 5, 14, 18, 22], [2, 7, 12, 17, 22], [2, 8, 14, 15, 21],
         [2, 9, 11, 18, 20], [2, 5, 13, 16, 24], [2, 6, 10, 19, 23],
         [3, 8, 13, 18, 23], [3, 9, 10, 16, 22], [3, 5, 12, 19, 21],
         [3, 6, 14, 17, 20], [3, 7, 11, 15, 24], [4, 9, 14, 19, 24],
         [4, 5, 11, 17, 23], [4, 6, 13, 15, 22], [4, 7, 10, 18, 21],
         [4, 8, 12, 16, 20]]

    Some examples of the maximal number of transversals Sage is able to build
    (we test all integers that are not prime powers up to `n=20`)::

        sage: TD_3_6 = designs.transversal_design(3, 6)
        sage: designs.transversal_design(4, 6, availability=True)
        False

        sage: TD_3_10 = designs.transversal_design(3, 10)
        sage: designs.transversal_design(4, 10, availability=True)
        False

        sage: TD_6_12 = designs.transversal_design(6, 12)
        sage: designs.transversal_design(7, 12, availability=True)
        False

        sage: TD_3_14 = designs.transversal_design(3, 14)
        sage: designs.transversal_design(4, 14, availability=True)
        False

        sage: TD_4_15 = designs.transversal_design(4, 15)
        sage: designs.transversal_design(5, 15, availability=True)
        False

        sage: TD_4_18 = designs.transversal_design(4, 18)
        sage: designs.transversal_design(5, 18, availability=True)
        False

        sage: TD_5_20 = designs.transversal_design(5, 20)
        sage: designs.transversal_design(6, 20, availability=True)
        False

    For prime powers, there is an explicit construction which gives a
    `TD(n+1,n)`::

        sage: for n in [2,3,5,7,9,11,13,16,17,19]:
        ....:     _ = designs.transversal_design(n+1, n)

    TESTS:

    Obtained through Wilson's decomposition::

        sage: _ = designs.transversal_design(4,38)

    Obtained through product decomposition::

        sage: _ = designs.transversal_design(6,60)
        sage: _ = designs.transversal_design(5,60) # checks some tricky divisibility error

    Availability, non availability::

        sage: designs.transversal_design(3,6,availability=True)
        True
        sage: _ = designs.transversal_design(3,6)
        sage: designs.transversal_design(5,6,availability=True)
        False
        sage: _ = designs.transversal_design(5,6)
        Traceback (most recent call last):
        ...
        NotImplementedError: I don't know how to build this Transversal Design!
    """
    if k >= n+2:
        if availability:
            return False
        from sage.categories.sets_cat import EmptySetError
        raise EmptySetError("No Transversal Design exists when k>=n+2")

    if n == 12 and k <= 6:
        TD = [l[:k] for l in TD6_12()]

    elif TD_find_product_decomposition(k,n):
        if availability:
            return True
        n1,n2 = TD_find_product_decomposition(k,n)
        TD1 = transversal_design(k,n1, check = False)
        TD2 = transversal_design(k,n2, check = False)
        TD = TD_product(k,TD1,n1,TD2,n2, check = False)

    elif find_wilson_decomposition(k,n):
        if availability:
            return True
        TD = wilson_construction(*find_wilson_decomposition(k,n), check = False)

    # Section 6.6 of [Stinson2004]
    elif (orthogonal_array not in who_asked and
          orthogonal_array(k, n, availability=True, who_asked = who_asked + (transversal_design,))):
        if availability:
            return True
        OA = orthogonal_array(k,n, check = False, who_asked = who_asked + (transversal_design,))
        TD = [[i*n+c for i,c in enumerate(l)] for l in OA]

    else:
        if availability:
            return False
        raise NotImplementedError("I don't know how to build this Transversal Design!")

    if check:
        assert is_transversal_design(TD,k,n)

    return TD

def is_transversal_design(B,k,n, verbose=False):
    r"""
    Check that a given set of blocks ``B`` is a transversal design.

    See :func:`~sage.combinat.designs.orthogonal_arrays.transversal_design`
    for a definition.

    INPUT:

    - ``B`` -- the list of blocks

    - ``k, n`` -- integers

    - ``verbose`` (boolean) -- whether to display information about what is
      going wrong.

    .. NOTE::

        The tranversal design must have `\{0, \ldots, kn-1\}` as a ground set,
        partitioned as `k` sets of size `n`: `\{0, \ldots, k-1\} \sqcup
        \{k, \ldots, 2k-1\} \sqcup \cdots \sqcup \{k(n-1), \ldots, kn-1\}`.

    EXAMPLES::

        sage: TD = designs.transversal_design(5, 5, check=True) # indirect doctest
        sage: from sage.combinat.designs.orthogonal_arrays import is_transversal_design
        sage: is_transversal_design(TD, 5, 5)
        True
        sage: is_transversal_design(TD, 4, 4)
        False
    """
    from sage.graphs.generators.basic import CompleteGraph
    from itertools import combinations
    g = k*CompleteGraph(n)
    m = g.size()
    for X in B:
        if len(X) != k:
            if verbose:
                print "A set has wrong size"
            return False
        g.add_edges(list(combinations(X,2)))
        if g.size() != m+(len(X)*(len(X)-1))/2:
            if verbose:
                print "A pair appears twice"
            return False
        m = g.size()

    if not g.is_clique():
        if verbose:
            print "A pair did not appear"
        return False

    return True

@cached_function
def find_wilson_decomposition(k,n):
    r"""
    Finds a wilson decomposition of `n`

    This method looks for possible integers `m,t,u` satisfying that `mt+u=n` and
    such that Sage knows how to build a `TD(k,m), TD(k,m+1),TD(k+1,t)` and a
    `TD(k,u)`. These can then be used to feed :func:`wilson_construction`.

    INPUT:

    - `k,n` (integers)

    OUTPUT:

    Returns a 4-tuple `(n, m, t, u)` if it is found, and ``False`` otherwise.

    EXAMPLES::

        sage: from sage.combinat.designs.orthogonal_arrays import find_wilson_decomposition
        sage: find_wilson_decomposition(4,38)
        (4, 7, 5, 3)
        sage: find_wilson_decomposition(4,20)
        False
    """
    # If there exists a TD(k+1,t) then k+1 < t+2, i.e. k <= t
    for t in range(max(1,k),n-1):
        u = n%t
        # We ensure that 1<=u, and that there can exists a TD(k,u), i.e k<u+2
        if u == 0 or k >= u+2:
            continue

        m = n//t
        # If there exists a TD(k,m) then k<m+2
        if k >= m+2:
            break

        if (transversal_design(k  ,m  , availability=True) and
            transversal_design(k  ,m+1, availability=True) and
            transversal_design(k+1,t  , availability=True) and
            transversal_design(k  ,u  , availability=True)):
            return k,m,t,u

    return False

def TD6_12():
    r"""
    Returns a `TD(6,12)` as build in [Hanani75]_.

    This design is Lemma 3.21 from [Hanani75]_.

    EXAMPLE::

        sage: from sage.combinat.designs.orthogonal_arrays import TD6_12
        sage: _ = TD6_12()

    REFERENCES:

    .. [Hanani75] Haim Hanani,
      Balanced incomplete block designs and related designs,
      http://dx.doi.org/10.1016/0012-365X(75)90040-0,
      Discrete Mathematics, Volume 11, Issue 3, 1975, Pages 255-369.
    """
    from sage.groups.additive_abelian.additive_abelian_group import AdditiveAbelianGroup
    G = AdditiveAbelianGroup([2,6])
    d = [[(0,0),(0,0),(0,0),(0,0),(0,0),(0,0)],
         [(0,0),(0,1),(1,0),(0,3),(1,2),(0,4)],
         [(0,0),(0,2),(1,2),(1,0),(0,1),(1,5)],
         [(0,0),(0,3),(0,2),(0,1),(1,5),(1,4)],
         [(0,0),(0,4),(1,1),(1,3),(0,5),(0,2)],
         [(0,0),(0,5),(0,1),(1,5),(1,3),(1,1)],
         [(0,0),(1,0),(1,3),(0,2),(0,3),(1,2)],
         [(0,0),(1,1),(1,5),(1,2),(1,4),(1,0)],
         [(0,0),(1,2),(0,4),(0,5),(0,2),(1,3)],
         [(0,0),(1,3),(1,4),(0,4),(1,1),(0,1)],
         [(0,0),(1,4),(0,5),(1,1),(1,0),(0,3)],
         [(0,0),(1,5),(0,3),(1,4),(0,4),(0,5)]]

    r = lambda x : int(x[0])*6+int(x[1])
    TD = [[i*12+r(G(x)+g) for i,x in enumerate(X)] for X in d for g in G]
    for x in TD: x.sort()

    return TD

def wilson_construction(k,m,t,u, check = True):
    r"""
    Returns a `TD(k,mt+u)` by Wilson's construction.

    Wilson's construction builds a `TD(k,mt+u)` from the following designs :

    * A `TD(k,m)`
    * A `TD(k,m+1)`
    * A `TD(k+1,t)`
    * A `TD(k,u)`

    For more information, see page 147 of [Stinson2004]_.

    INPUT:

    - ``k,m,t,u`` -- integers with `k\geq 2` and `1\leq u\leq t`.

    - ``check`` (boolean) -- whether to check that output is correct before
      returning it. As this is expected to be useless (but we are cautious
      guys), you may want to disable it whenever you want speed. Set to ``True``
      by default.

    EXAMPLES::

        sage: from sage.combinat.designs.orthogonal_arrays import wilson_construction
        sage: from sage.combinat.designs.orthogonal_arrays import find_wilson_decomposition
        sage: total = 0
        sage: for k in range(3,8):
        ....:    for n in range(1,30):
        ....:        if find_wilson_decomposition(k,n):
        ....:            total += 1
        ....:            k,m,t,u = find_wilson_decomposition(k,n)
        ....:            _ = wilson_construction(k,m,t,u, check=True)
        sage: print total
        32
    """
    # Raises a NotImplementedError if one of them does not exist.
    TDkm = transversal_design(k,m,check=False)
    TDkm1 = transversal_design(k,m+1,check=False)
    TDk1t = transversal_design(k+1,t,check=False)
    TDku = transversal_design(k,u,check=False)

    # Truncaed TDk1t
    truncated_TDk1t = [[x for x in B if x<k*t+u] for B in TDk1t]

    # Making sure that [(i,m) for i in range(k)] is a block of TDkm1
    B0 = sorted(TDkm1[0])
    TDkm1 = [[x+m-(x%(m+1)) if x in B0 else
              x-bool(B0[x//(m+1)] <= x)
             for x in B]
             for B in TDkm1]

    # Remove first block
    TDkm1.pop(0)

    TD = []
    for A in truncated_TDk1t:
        # Case 1, |A|=k
        if len(A) == k:
            for B in TDkm:
                BB = []
                for x in B:
                    # x//m is the group of x in TDkm
                    # x%m is the element of x in its group
                    ai = A[x//m]
                    i = ai//t
                    BB.append(i*(m*t+u)+(ai%t)*m+x%m)
                TD.append(BB)

        # Case 2, |A|=k+1
        else:
            A.sort()
            a_k1 = A.pop(-1)
            for B in TDkm1:
                BB = []
                for x in B:
                    # x//(m+1) is the group of x in TDkm1
                    # x%(m+1) is the element of x in its group
                    ai = A[x//(m+1)]
                    i = ai//t
                    if (x+1)%(m+1) == 0:
                        BB.append(i*(m*t+u)+m*t+(a_k1%t))
                    else:
                        BB.append(i*(m*t+u)+(ai%t)*m+x%(m+1))
                TD.append(BB)

    # "Finally, there exists [...]"
    for A in TDku:
        TD.append([(m*t+u)*(x//u)+m*t+x%u for x in A])

    if check:
        assert is_transversal_design(TD,k,m*t+u, verbose=True)

    return TD

@cached_function
def TD_find_product_decomposition(k,n):
    r"""
    Attempts to find a factorization of `n` in order to build a `TD(k,n)`.

    If Sage can build a `TD(k,n_1)` and a `TD(k,n_2)` such that `n=n_1\times
    n_2` then a `TD(k,n)` can be built (from the function
    :func:`transversal_design`). This method returns such a pair of integers if
    it exists, and ``None`` otherwise.

    INPUT:

    - ``k,n`` (integers) -- see above.

    .. SEEALSO::

        :func:`TD_product` that actually build a product

    EXAMPLES::

        sage: from sage.combinat.designs.orthogonal_arrays import TD_find_product_decomposition
        sage: TD_find_product_decomposition(6, 84)
        (7, 12)

        sage: TD1 = designs.transversal_design(6, 7)
        sage: TD2 = designs.transversal_design(6, 12)
        sage: from sage.combinat.designs.orthogonal_arrays import TD_product
        sage: TD = TD_product(6, TD1, 7, TD2, 12)
    """
    from sage.rings.arith import divisors
    for n1 in divisors(n)[1:-1]: # we ignore 1 and n
        n2 = n//n1
        if transversal_design(k, n1, availability = True) and transversal_design(k, n2, availability = True):
            return n1,n2
    return None

def TD_product(k,TD1,n1,TD2,n2, check=True):
    r"""
    Returns the product of two transversal designs.

    From a transversal design `TD_1` of parameters `k,n_1` and a transversal
    design `TD_2` of parameters `k,n_2`, this function returns a transversal
    design of parameters `k,n` where `n=n_1\times n_2`.

    Formally, if the groups of `TD_1` are `V^1_1,\dots,V^1_k` and the groups of
    `TD_2` are `V^2_1,\dots,V^2_k`, the groups of the product design are
    `V^1_1\times V^2_1,\dots,V^1_k\times V^2_k` and its blocks are the
    `\{(x^1_1,x^2_1),\dots,(x^1_k,x^2_k)\}` where `\{x^1_1,\dots,x^1_k\}` is a
    block of `TD_1` and `\{x^2_1,\dots,x^2_k\}` is a block of `TD_2`.

    INPUT:

    - ``TD1, TD2`` -- transversal designs.

    - ``k,n1,n2`` (integers) -- see above.

    - ``check`` (boolean) -- Whether to check that output is correct before
      returning it. As this is expected to be useless (but we are cautious
      guys), you may want to disable it whenever you want speed. Set to ``True``
      by default.

    .. SEEALSO::

        :func:`TD_find_product_decomposition`

    .. NOTE::

        This function uses transversal designs with
        `V_1=\{0,\dots,n-1\},\dots,V_k=\{(k-1)n,\dots,kn-1\}` both as input and
        ouptut.

    EXAMPLES::

        sage: from sage.combinat.designs.orthogonal_arrays import TD_product
        sage: TD1 = designs.transversal_design(6,7)
        sage: TD2 = designs.transversal_design(6,12)
        sage: TD6_84 = TD_product(6,TD1,7,TD2,12)
    """
    N = n1*n2
    TD = []
    for X1 in TD1:
        for X2 in TD2:
            TD.append([x1*n2+(x2%n2) for x1,x2 in zip(X1,X2)])
    if check:
        assert is_transversal_design(TD,k,N)

    return TD

def orthogonal_array(k,n,t=2,check=True,availability=False,who_asked=tuple()):
    r"""
    Return an orthogonal array of parameters `k,n,t`.

    An orthogonal array of parameters `k,n,t` is a matrix with `k` columns
    filled with integers from `[n]` in such a way that for any `t` columns, each
    of the `n^t` possible rows occurs exactly once. In
    particular, the matrix has `n^t` rows.

    More general definitions sometimes involve a `\lambda` parameter, and we
    assume here that `\lambda=1`.

    For more information on orthogonal arrays, see
    :wikipedia:`Orthogonal_array`.

    INPUT:

    - ``k`` -- (integer) number of columns

    - ``n`` -- (integer) number of symbols

    - ``t`` -- (integer; default: 2) -- strength of the array

    - ``check`` -- (boolean) Whether to check that output is correct before
      returning it. As this is expected to be useless (but we are cautious
      guys), you may want to disable it whenever you want speed. Set to
      ``True`` by default.

    - ``availability`` (boolean) -- if ``availability`` is set to ``True``, the
      function only returns boolean answers according to whether Sage knows how
      to build such an array. This should be much faster than actually building
      it.

    - ``who_asked`` (internal use only) -- because of the equivalence between
      OA/TD/MOLS, each of the three constructors calls the others. We must keep
      track of who calls who in order to avoid infinite loops. ``who_asked`` is
      the tuple of the other functions that were called before this one on the
      same input `k,n`.

    For more information on orthogonal arrays, see
    :wikipedia:`Orthogonal_array`.

    .. NOTE::

        This method implements theorems from [Stinson2004]_. See the code's
        documentation for details.

    .. SEEALSO::

        When `t=2` an orthogonal array is also a transversal design (see
        :func:`transversal_design`) and a family of mutually orthogonal latin
        squares (see
        :func:`~sage.combinat.designs.latin_squares.mutually_orthogonal_latin_squares`).

    EXAMPLES::

        sage: designs.orthogonal_array(5,5)
        [[0, 0, 0, 0, 0], [0, 1, 2, 3, 4], [0, 2, 4, 1, 3], [0, 3, 1, 4, 2],
         [0, 4, 3, 2, 1], [1, 1, 1, 1, 1], [1, 2, 3, 4, 0], [1, 3, 0, 2, 4],
         [1, 4, 2, 0, 3], [1, 0, 4, 3, 2], [2, 2, 2, 2, 2], [2, 3, 4, 0, 1],
         [2, 4, 1, 3, 0], [2, 0, 3, 1, 4], [2, 1, 0, 4, 3], [3, 3, 3, 3, 3],
         [3, 4, 0, 1, 2], [3, 0, 2, 4, 1], [3, 1, 4, 2, 0], [3, 2, 1, 0, 4],
         [4, 4, 4, 4, 4], [4, 0, 1, 2, 3], [4, 1, 3, 0, 2], [4, 2, 0, 3, 1],
         [4, 3, 2, 1, 0]]

    TESTS::

        sage: designs.orthogonal_array(3,2)
        [[0, 1, 0], [0, 0, 1], [1, 0, 0], [1, 1, 1]]
        sage: designs.orthogonal_array(4,2)
        Traceback (most recent call last):
        ...
        EmptySetError: No Orthogonal Array exists when k>=n+t
    """
    from sage.rings.arith import is_prime_power
    from sage.rings.finite_rings.constructor import FiniteField
    from latin_squares import mutually_orthogonal_latin_squares

    if k < 2:
        raise ValueError("undefined for k less than 2")

    elif k >= n+t:
        if availability:
            return False

        from sage.categories.sets_cat import EmptySetError
        # When t=2 then k<n+t as it is equivalent to the existence of n-1 MOLS.
        # When t>2 the submatrix defined by the rows whose first t-2 elements
        # are 0s yields a OA with t=2 and k-(t-2) columns. Thus k-(t-2) < n+2,
        # i.e. k<n+t.
        raise EmptySetError("No Orthogonal Array exists when k>=n+t")

    elif k == t:
        if availability:
            return True

        from itertools import product
        OA = map(list, product(range(n), repeat=k))

    # Theorem 6.39 from [Stinson2004]
    elif t == 2 and 2 <= k and k <= n and is_prime_power(n):
        if availability:
            return True

        M = []
        Fp = FiniteField(n,'x')
        vv = list(Fp)[:k]
        relabel = {x:i for i,x in enumerate(Fp)}
        for i in Fp:
            for j in Fp:
                M.append([relabel[i+j*v] for v in vv])

        OA = M

    # Theorem 6.40 from [Stinson2004]
    elif t == 2 and k == n+1 and is_prime_power(n):
        if availability:
            return True

        if n == 2:
            OA = [[0,1,0],[0,0,1],[1,0,0],[1,1,1]]
        else:
            M = orthogonal_array(n,n, check=False)
            for i,l in enumerate(M):
                l.append(i%n)
            OA = M

    elif (t == 2 and transversal_design not in who_asked and
          transversal_design(k,n,availability=True, who_asked=who_asked+(orthogonal_array,))):
        if availability:
            return True
        TD = transversal_design(k,n,check=False,who_asked=who_asked+(orthogonal_array,))
        OA = [[x%n for x in R] for R in TD]

    # Section 6.5.1 from [Stinson2004]
    elif (t == 2 and mutually_orthogonal_latin_squares not in who_asked and
          mutually_orthogonal_latin_squares(n,k-2, availability=True,who_asked=who_asked+(orthogonal_array,))):
        if availability:
            return True

        mols = mutually_orthogonal_latin_squares(n,k-2,who_asked=who_asked+(orthogonal_array,))
        OA = [[i,j]+[m[i,j] for m in mols]
              for i in range(n) for j in range(n)]

    else:
        if availability:
            return False
        raise NotImplementedError("I don't know how to build this orthogonal array!")

    if check:
        assert is_orthogonal_array(OA,k,n,t)

    return OA

def is_orthogonal_array(M,k,n,t,verbose=False):
    r"""
    Check that the integer matrix `M` is an `OA(k,n,t)`.

    See :func:`~sage.combinat.designs.orthogonal_arrays.orthogonal_array`
    for a definition.

    INPUT:

    - ``M`` -- an integer matrix of size `k^t \times n`

    - ``k, n, t`` -- integers

    - ``verbose`` -- boolean, if ``True`` provide an information on where ``M``
      fails to be an `OA(k,n,t)`.

    EXAMPLES::

        sage: OA = designs.orthogonal_array(5,9,check=True) # indirect doctest
        sage: from sage.combinat.designs.orthogonal_arrays import is_orthogonal_array
        sage: is_orthogonal_array(OA, 5, 9, 2)
        True
        sage: is_orthogonal_array(OA, 4, 5, 2)
        False
    """
    if t != 2:
        raise NotImplementedError("only implemented for t=2")

    if any(len(l) != k for l in M):
        if verbose:
            print "a block has the wrong size"
        return False

    from itertools import combinations
    for S in combinations(range(k),2):
        fs = frozenset([tuple([l[i] for i in S]) for l in M])
        if len(fs) != n**2:
            if verbose:
                print "for the choice %s of columns we do not get all tuples"%(S,)
            return False

    return True

