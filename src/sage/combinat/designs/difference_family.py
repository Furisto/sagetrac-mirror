r"""
Difference families

This module gathers everything related to difference families. One can build a
difference family (or check that it can be built) with :func:`difference_family`::

    sage: G,F = designs.difference_family(13,4,1)

It defines the following functions:

.. csv-table::
    :class: contentstable
    :widths: 30, 70
    :delim: |

    :func:`is_difference_family` | Return a (``k``, ``l``)-difference family on an Abelian group of size ``v``.
    :func:`singer_difference_set` | Return a difference set associated to hyperplanes in a projective space.
    :func:`difference_family` | Return a (``k``, ``l``)-difference family on an Abelian group of size ``v``.

REFERENCES:

.. [Wi72] R. M. Wilson "Cyclotomy and difference families in elementary Abelian
   groups", J. of Num. Th., 4 (1972), pp. 17-47.

Functions
---------
"""
#*****************************************************************************
#       Copyright (C) 2014 Vincent Delecroix <20100.delecroix@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#  as published by the Free Software Foundation; either version 2 of
#  the License, or (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from sage.categories.sets_cat import EmptySetError
import sage.rings.arith as arith
from sage.misc.unknown import Unknown
from sage.rings.integer import Integer

def group_law(G):
    r"""
    Return a triple ``(identity, operation, inverse)`` that define the
    operations on the group ``G``.

    EXAMPLES::

        sage: from sage.combinat.designs.difference_family import group_law
        sage: group_law(Zmod(3))
        (0, <built-in function add>, <built-in function neg>)
        sage: group_law(SymmetricGroup(5))
        ((), <built-in function mul>, <built-in function inv>)
        sage: group_law(VectorSpace(QQ,3))
        ((0, 0, 0), <built-in function add>, <built-in function neg>)
    """
    import operator
    from sage.categories.groups import Groups
    from sage.categories.additive_groups import AdditiveGroups

    if G in Groups():            # multiplicative groups
        return (G.one(), operator.mul, operator.inv)
    elif G in AdditiveGroups():  # additive groups
        return (G.zero(), operator.add, operator.neg)
    else:
        raise ValueError("%s does not seem to be a group"%G)

def block_stabilizer(G, B):
    r"""
    Compute the stabilizer of the block ``B`` in the group additive group ``G``.

    EXAMPLES::

        sage: from sage.combinat.designs.difference_family import block_stabilizer

        sage: Z8 = Zmod(8)
        sage: block_stabilizer(Z8, [Z8(0),Z8(2),Z8(4),Z8(6)])
        [0, 2, 4, 6]
        sage: block_stabilizer(Z8, [Z8(0),Z8(2)])
        [0]

        sage: C = cartesian_product([Zmod(4),Zmod(3)])
        sage: block_stabilizer(C, [C((0,0)),C((2,0)),C((0,1)),C((2,1))])
        [(0, 0), (2, 0)]

        sage: b = map(Zmod(45),[1, 3, 7, 10, 22, 25, 30, 35, 37, 38, 44])
        sage: block_stabilizer(Zmod(45),b)
        [0]
    """
    b0 = -B[0]
    S = []
    for b in B:
        # fun: if we replace +(-b) with -b it completely fails!!
        if all(b + b0 + c in B for c in B):
            S.append(b+b0)
    return S

def orbit_representatives(G,B):
    r"""
    Return the orbits of the additive group ``G`` that intersects the set ``B``.

    EXAMPLES::

        sage: from sage.combinat.designs.difference_family import (
        ....:    block_stabilizer, orbit_representatives)

        sage: Z8 = Zmod(8)
        sage: b = map(Z8, [0,2,4,6])
        sage: S = block_stabilizer(Z8,b)
        sage: orbit_representatives(S, b)
        [0]

        sage: b = map(Z8, [0,1,4,5])
        sage: S = block_stabilizer(Z8,b)
        sage: orbit_representatives(S, b)
        [0, 1]

        sage: C = cartesian_product([Zmod(4),Zmod(3)])
        sage: b = [C((0,0)),C((2,0)),C((0,1)),C((2,1))]
        sage: S = block_stabilizer(C,b)
        sage: orbit_representatives(S, b)
        [(0, 1), (2, 0)]
    """
    if len(G) == 1:
        return B

    o = []
    B = set(B)
    while B:
        b = B.pop()
        o.append(b)
        for g in G:
            if not g.is_zero():
                B.remove(g+b)
    return o

def partial_differences(G, B):
    r"""
    Compute the partial differences of the block ``B``.

    EXAMPLES::

        sage: from sage.combinat.designs.difference_family import partial_differences

        sage: b = map(Zmod(8),[0,2,4,6])
        sage: partial_differences(Zmod(8),b)
        [2, 4, 6]

        sage: b = map(Zmod(8),[0,1,4,5])
        sage: partial_differences(Zmod(8),b)
        [1, 3, 4, 4, 5, 7]

        sage: b = [1, 3, 7, 10, 22, 25, 30, 35, 37, 38, 44]
        sage: b = map(Zmod(45),b)
        sage: d = partial_differences(Zmod(45),b)
        sage: len(d)
        110
    """
    stab = block_stabilizer(G,B)
    o = orbit_representatives(stab,B)
    return sorted(b + (-c) + g for b in o for c in o for g in stab if b+g != c)

def is_difference_family(G, D, v=None, k=None, l=None, short_blocks=True, verbose=False):
    r"""
    Check wether ``D`` forms a difference family in the additive Abelian group ``G``.

    INPUT:

    - ``G`` - Additive Abelian group of cardinality ``v``

    - ``D`` - a set of ``k``-subsets of ``G``

    - ``v``, ``k`` and ``l`` - optional parameters of the difference family

    - ``short_blocks`` - whether short blocks are allowed (default is ``True``)

    - ``verbose`` - whether to print additional information

    .. SEEALSO::

        :func:`difference_family`

    EXAMPLES::

        sage: from sage.combinat.designs.difference_family import is_difference_family
        sage: G = Zmod(21)
        sage: D = [[0,1,4,14,16]]
        sage: is_difference_family(G, D, 21, 5)
        True

        sage: G = Zmod(41)
        sage: D = [[0,1,4,11,29],[0,2,8,17,21]]
        sage: is_difference_family(G, D, verbose=True)
        Too less:
          5 is obtained 0 times in blocks []
          14 is obtained 0 times in blocks []
          27 is obtained 0 times in blocks []
          36 is obtained 0 times in blocks []
        Too much:
          4 is obtained 2 times in blocks [0, 1]
          13 is obtained 2 times in blocks [0, 1]
          28 is obtained 2 times in blocks [0, 1]
          37 is obtained 2 times in blocks [0, 1]
        False
        sage: D = [[0,1,4,11,29],[0,2,8,17,22]]
        sage: is_difference_family(G, D)
        True

        sage: G = Zmod(61)
        sage: D = [[0,1,3,13,34],[0,4,9,23,45],[0,6,17,24,32]]
        sage: is_difference_family(G, D)
        True

        sage: G = AdditiveAbelianGroup([3]*4)
        sage: a,b,c,d = G.gens()
        sage: D = [[d, -a+d, -c+d, a-b-d, b+c+d],
        ....:      [c, a+b-d, -b+c, a-b+d, a+b+c],
        ....:      [-a-b+c+d, a-b-c-d, -a+c-d, b-c+d, a+b],
        ....:      [-b-d, a+b+d, a-b+c-d, a-b+c, -b+c+d]]
        sage: is_difference_family(G, D)
        True

    An example with a short block (i.e. considering restricted difference when a
    block has a non trivial stabilizer)::

        sage: G = Zmod(15)
        sage: D = [[0,1,4],[0,2,9],[0,5,10]]
        sage: is_difference_family(G,D,verbose=True)
        It is a (15,3,1)-difference family
        True
        sage: is_difference_family(G,D,short_blocks=False,verbose=True)
        bk(k-1) is not 0 mod (v-1)
        False

    The function also supports multiplicative groups (non necessarily Abelian).
    In that case, the argument ``short_blocks`` must be set to ``False``::

        sage: G = DihedralGroup(8)
        sage: x,y = G.gens()
        sage: D1 = [[1,x,x^4], [1,x^2, y*x], [1,x^5,y], [1,x^6,y*x^2], [1,x^7,y*x^5]]
        sage: is_difference_family(G, D1, 16, 3, 2, short_blocks=False)
        True
        sage: is_difference_family(G, D1, 16, 3, 2)
        Traceback (most recent call last):
        ...
        ValueError: short blocks are meaningful only for Abelian group that we assume
        to be additive
    """
    import operator

    identity, mul, inv = group_law(G)
    if short_blocks and not (mul is operator.add or inv is operator.neg):
        raise ValueError("short blocks are meaningful only for Abelian group that we assume to be additive")

    Glist = list(G)

    if v is None:
        v = len(Glist)
    else:
        v = int(v)
        if len(Glist) != v:
            if verbose:
                print "G must have cardinality v (=%d)"%v
            return False

    if k is None:
        k = len(D[0])
    else:
        k = int(k)

    b = len(D)

    for d in D:
        if len(d) != k:
            if verbose:
                print "the block {} does not have length {}".format(d,k)
            return False

    if short_blocks:
        nb_diff = 0
        stab_sizes = []
        for d in D:
            s = len(block_stabilizer(G,map(G,d)))
            stab_sizes.append(s)
            nb_diff += k*(k-1) / s
        if l is None:
            if nb_diff % (v-1) != 0:
                if verbose:
                    print "sum(1/s_i) k*(k-1) = {} is not a multiple of (v-1) = {} (stabilizer sizes {})".format(
                            nb_diff, v-1, stab_sizes)
                return False
            l = nb_diff // (v-1)
        else:
            if nb_diff != l*(v-1):
                if verbose:
                    print ("the relation sum(1/s_i) *k*(k-1) == l*(v-1) is not "
                    "satisfied (where the s_i are the cardinality of the stabilizer "
                    "for each blocks)")
                return False

    else:
        if l is None:
            if (b*k*(k-1)) % (v-1) != 0:
                if verbose:
                    print "bk(k-1) is not 0 mod (v-1)"
                return False
            l = b*k*(k-1) // (v-1)
        else:
            l = int(l)
            if b*k*(k-1) != l*(v-1):
                if verbose:
                    print "the relation bk(k-1) == l(v-1) is not satisfied with b=%d, k=%d, l=%d, v=%d"%(b,k,l,v)
                return False

    # now we check that every non-identity element of G occurs exactly l-time
    # as a difference
    counter = {g: 0 for g in Glist}
    where   = {g: [] for g in Glist}
    del counter[identity]

    if short_blocks:
        for i,d in enumerate(D):
            dd = map(G,d)
            for g in partial_differences(G,dd):
                if g.is_zero():
                    if verbose:
                        print "two identical elements in block {}".format(dd)
                    return False
                where[g].append(i)
                counter[g] += 1
    else:
        for i,d in enumerate(D):
            dd = map(G,d)
            for ix,x in enumerate(dd):
                for iy,y in enumerate(dd):
                    if ix == iy:
                        continue
                    if x == y:
                        if verbose:
                            print "two identical elements in block {}".format(dd)
                        return False
                    g = mul(x,inv(y))
                    where[g].append(i)
                    counter[g] += 1

    too_less = []
    too_much = []
    for g in Glist:
        if g == identity:
            continue
        if counter[g] < l:
            if verbose:
                too_less.append(g)
            else:
                return False
        if counter[g] > l:
            if verbose:
                too_much.append(g)
            else:
                return False

    if too_less:
        print "Too less:"
        for g in too_less:
            print "  {} is obtained {} times in blocks {}".format(
                        g,counter[g],where[g])
    if too_much:
        print "Too much:"
        for g  in too_much:
            print "  {} is obtained {} times in blocks {}".format(
                        g,counter[g],where[g])
    if too_less or too_much:
        return False

    if verbose:
        print "It is a ({},{},{})-difference family".format(v,k,l)
    return True

def singer_difference_set(q,d):
    r"""
    Return a difference set associated to the set of hyperplanes in a projective
    space of dimension `d` over `GF(q)`.

    A Singer difference set has parameters:

    .. MATH::

        v = \frac{q^{d+1}-1}{q-1}, \quad
        k = \frac{q^d-1}{q-1}, \quad
        \lambda = \frac{q^{d-1}-1}{q-1}.

    The idea of the construction is as follows. One consider the finite field
    `GF(q^{d+1})` as a vector space of dimension `d+1` over `GF(q)`. The set of
    `GF(q)`-lines in `GF(q^{d+1})` is a projective plane and its set of
    hyperplanes form a balanced incomplete block design.

    Now, considering a multiplicative generator `z` of `GF(q^{d+1})`, we get a
    transitive action of a cyclic group on our projective plane from which it is
    possible to build a difference set.

    The construction is given in details in [Stinson2004]_, section 3.3.

    EXAMPLES::

        sage: from sage.combinat.designs.difference_family import singer_difference_set, is_difference_family
        sage: G,D = singer_difference_set(3,2)
        sage: is_difference_family(G,D,verbose=True)
        It is a (13,4,1)-difference family
        True

        sage: G,D = singer_difference_set(4,2)
        sage: is_difference_family(G,D,verbose=True)
        It is a (21,5,1)-difference family
        True

        sage: G,D = singer_difference_set(3,3)
        sage: is_difference_family(G,D,verbose=True)
        It is a (40,13,4)-difference family
        True

        sage: G,D = singer_difference_set(9,3)
        sage: is_difference_family(G,D,verbose=True)
        It is a (820,91,10)-difference family
        True
    """
    q = Integer(q)
    assert q.is_prime_power()
    assert d >= 2

    from sage.rings.finite_rings.constructor import GF
    from sage.rings.finite_rings.conway_polynomials import conway_polynomial
    from sage.rings.finite_rings.integer_mod_ring import Zmod

    # build a polynomial c over GF(q) such that GF(q)[x] / (c(x)) is a
    # GF(q**(d+1)) and such that x is a multiplicative generator.
    p,e = q.factor()[0]
    c = conway_polynomial(p,e*(d+1))
    if e != 1:  # i.e. q is not a prime, so we factorize c over GF(q) and pick
                # one of its factor
        K = GF(q,'z')
        c = c.change_ring(K).factor()[0][0]
    else:
        K = GF(q)
    z = c.parent().gen()

    # Now we consider the GF(q)-subspace V spanned by (1,z,z^2,...,z^(d-1)) inside
    # GF(q^(d+1)). The multiplication by z is an automorphism of the
    # GF(q)-projective space built from GF(q^(d+1)). The difference family is
    # obtained by taking the integers i such that z^i belong to V.
    powers = [0]
    i = 1
    x = z
    k = (q**d-1)//(q-1)
    while len(powers) < k:
        if x.degree() <= (d-1):
            powers.append(i)
        x = (x*z).mod(c)
        i += 1

    return Zmod((q**(d+1)-1)//(q-1)), [powers]

def difference_family(v, k, l=1, short_blocks=True, existence=False, check=True):
    r"""
    Return a (``k``, ``l``)-difference family on an Abelian group of cardinality ``v``.

    Let `G` be a finite Abelian group. For a given subset `D` of `G`, we define
    `\Delta D` to be the multi-set of differences `\Delta D = \{x - y; x \in D,
    y \in D, x \not= y\}`. A `(G,k,\lambda)`-*difference family* is a collection
    of `k`-subsets of `G`, `D = \{D_1, D_2, \ldots, D_b\}` such that the union
    of the difference sets `\Delta D_i` for `i=1,...b`, seen as a multi-set,
    contains each element of `G \backslash \{0\}` exactly `\lambda`-times.

    When there is only one block, i.e. `\lambda(v - 1) = k(k-1)`, then a
    `(G,k,\lambda)`-difference family is also called a *difference set*.

    See also :wikipedia:`Difference_set`.

    If there is no such difference family, an ``EmptySetError`` is raised and if
    there is no construction at the moment ``NotImplementedError`` is raised.

    EXAMPLES::

        sage: K,D = designs.difference_family(73,4)
        sage: D
        [[0, 1, 8, 64],
         [0, 25, 54, 67],
         [0, 41, 36, 69],
         [0, 3, 24, 46],
         [0, 2, 16, 55],
         [0, 50, 35, 61]]

        sage: K,D = designs.difference_family(337,7)
        sage: D
        [[1, 175, 295, 64, 79, 8, 52],
         [326, 97, 125, 307, 142, 249, 102],
         [121, 281, 310, 330, 123, 294, 226],
         [17, 279, 297, 77, 332, 136, 210],
         [150, 301, 103, 164, 55, 189, 49],
         [35, 59, 215, 218, 69, 280, 135],
         [289, 25, 331, 298, 252, 290, 200],
         [191, 62, 66, 92, 261, 180, 159]]

    For `k=6,7` we look at the set of small prime powers for which a
    construction is available::

        sage: def prime_power_mod(r,m):
        ....:     k = m+r
        ....:     while True:
        ....:         if is_prime_power(k):
        ....:             yield k
        ....:         k += m

        sage: from itertools import islice
        sage: l6 = {True:[], False: [], Unknown: []}
        sage: for q in islice(prime_power_mod(1,30), 60):
        ....:     l6[designs.difference_family(q,6,existence=True)].append(q)
        sage: l6[True]
        [31, 121, 151, 181, 211, ...,  3061, 3121, 3181]
        sage: l6[Unknown]
        [61]
        sage: l6[False]
        []

        sage: l7 = {True: [], False: [], Unknown: []}
        sage: for q in islice(prime_power_mod(1,42), 60):
        ....:     l7[designs.difference_family(q,7,existence=True)].append(q)
        sage: l7[True]
        [337, 421, 463, 883, 1723, 3067, 3319, 3529, 3823, 3907, 4621, 4957, 5167]
        sage: l7[Unknown]
        [43, 127, 169, 211, ..., 4999, 5041, 5209]
        sage: l7[False]
        []

    Other constructions for `\lambda > 1`::

        sage: for v in xrange(2,100):
        ....:     constructions = []
        ....:     for k in xrange(2,10):
        ....:         for l in xrange(2,10):
        ....:             if designs.difference_family(v,k,l,existence=True):
        ....:                 constructions.append((k,l))
        ....:                 _ = designs.difference_family(v,k,l)
        ....:     if constructions:
        ....:         print "%2d: %s"%(v, ', '.join('(%d,%d)'%(k,l) for k,l in constructions))
         2: (3,2), (4,3), (5,4), (6,5), (7,6), (8,7), (9,8)
         3: (3,2), (4,3), (5,4), (6,5), (7,6), (8,7), (9,8)
         4: (3,2), (4,3), (5,4), (6,5), (7,6), (8,7), (9,8)
         5: (3,2), (4,3), (5,4), (6,5), (7,6), (8,7), (9,8)
         7: (3,2), (4,3), (5,4), (6,5), (7,6), (8,7), (9,8)
         8: (3,2), (4,3), (5,4), (6,5), (7,6), (8,7), (9,8)
         9: (3,2), (4,3), (5,4), (6,5), (7,6), (8,7), (9,8)
        11: (3,2), (4,3), (4,6), (5,2), (5,3), (5,4), (6,5), (7,6), (8,7), (9,8)
        13: (3,2), (4,3), (5,4), (5,5), (6,5), (7,6), (8,7), (9,8)
        15: (4,6), (5,6), (7,3)
        16: (3,2), (4,3), (5,4), (6,5), (7,6), (8,7), (9,8)
        17: (3,2), (4,3), (5,4), (5,5), (6,5), (7,6), (8,7), (9,8)
        19: (3,2), (4,2), (4,3), (5,4), (6,5), (7,6), (8,7), (9,4), (9,5), (9,6), (9,7), (9,8)
        21: (4,3), (6,3), (6,5)
        22: (4,2), (6,5), (7,4), (8,8)
        23: (3,2), (4,3), (5,4), (6,5), (7,6), (8,7), (9,8)
        25: (3,2), (4,3), (5,4), (6,5), (7,6), (7,7), (8,7), (9,8)
        27: (3,2), (4,3), (5,4), (6,5), (7,6), (8,7), (9,8)
        28: (3,2), (6,5)
        29: (3,2), (4,3), (5,4), (6,5), (7,3), (7,6), (8,4), (8,6), (8,7), (9,8)
        31: (3,2), (4,2), (4,3), (5,2), (5,4), (6,5), (7,6), (8,7), (9,8)
        32: (3,2), (4,3), (5,4), (6,5), (7,6), (8,7), (9,8)
        33: (5,5), (6,5)
        34: (4,2)
        35: (5,2), (8,4)
        37: (3,2), (4,3), (5,4), (6,5), (7,6), (8,7), (9,2), (9,3), (9,8)
        39: (6,5)
        40: (3,2)
        41: (3,2), (4,3), (5,4), (6,3), (6,5), (7,6), (8,7), (9,8)
        43: (3,2), (4,2), (4,3), (5,4), (6,5), (7,2), (7,3), (7,6), (8,4), (8,7), (9,8)
        46: (4,2), (6,2)
        47: (3,2), (4,3), (5,4), (6,5), (7,6), (8,7), (9,8)
        49: (3,2), (4,3), (5,4), (6,5), (7,6), (8,7), (9,3), (9,8)
        51: (5,2), (6,3)
        53: (3,2), (4,3), (5,4), (6,5), (7,6), (8,7), (9,8)
        55: (9,4)
        57: (7,3)
        59: (3,2), (4,3), (5,4), (6,5), (7,6), (8,7), (9,8)
        61: (3,2), (4,3), (5,4), (6,2), (6,3), (6,5), (7,6), (8,7), (9,8)
        64: (3,2), (4,3), (5,4), (6,5), (7,2), (7,6), (8,7), (9,8)
        67: (3,2), (4,3), (5,4), (6,5), (7,6), (8,7), (9,8)
        71: (3,2), (4,3), (5,2), (5,4), (6,5), (7,3), (7,6), (8,4), (8,7), (9,8)
        73: (3,2), (4,3), (5,4), (6,5), (7,6), (8,7), (9,8)
        75: (5,2)
        79: (3,2), (4,3), (5,4), (6,5), (7,6), (8,7), (9,8)
        81: (3,2), (4,3), (5,4), (6,5), (7,6), (8,7), (9,8)
        83: (3,2), (4,3), (5,4), (6,5), (7,6), (8,7), (9,8)
        85: (7,2), (7,3), (8,2)
        89: (3,2), (4,3), (5,4), (6,5), (7,6), (8,7), (9,8)
        97: (3,2), (4,3), (5,4), (6,5), (7,6), (8,7), (9,3), (9,8)

    TESTS:

    Check more of the Wilson constructions from [Wi72]_::

        sage: Q5 = [241, 281,421,601,641, 661, 701, 821,881]
        sage: Q9 = [73, 1153, 1873, 2017]
        sage: Q15 = [76231]
        sage: Q4 = [13, 73, 97, 109, 181, 229, 241, 277, 337, 409, 421, 457]
        sage: Q8 = [1009, 3137, 3697]
        sage: for Q,k in [(Q4,4),(Q5,5),(Q8,8),(Q9,9),(Q15,15)]:
        ....:     for q in Q:
        ....:         assert designs.difference_family(q,k,1,existence=True) is True
        ....:         _ = designs.difference_family(q,k,1)

    Check Singer difference sets::

        sage: sgp = lambda q,d: ((q**(d+1)-1)//(q-1), (q**d-1)//(q-1), (q**(d-1)-1)//(q-1))

        sage: for q in range(2,10):
        ....:     if is_prime_power(q):
        ....:         for d in [2,3,4]:
        ....:           v,k,l = sgp(q,d)
        ....:           assert designs.difference_family(v,k,l,existence=True) is True
        ....:           _ = designs.difference_family(v,k,l)

    .. TODO::

        Implement recursive constructions from Buratti "Recursive for difference
        matrices and relative difference families" (1998) and Jungnickel
        "Composition theorems for difference families and regular planes" (1978)
    """
    if not short_blocks and (l*(v-1)) % (k*(k-1)) != 0:
        if existence:
            return False
        raise EmptySetError("A (v,%d,%d)-difference family may exist only if %d*(v-1) = mod %d"%(k,l,l,k*(k-1)))

    from block_design import are_hyperplanes_in_projective_geometry_parameters
    from database import DF_from_database

    G_df = DF_from_database(v,k,l,short_blocks=short_blocks)
    if G_df:
        if existence:
            return True
        return G_df

    e = k*(k-1)
    t = l*(v-1) // e  # number of blocks

    D = None

    if arith.is_prime_power(v):
        from sage.rings.finite_rings.constructor import GF
        G = K = GF(v,'z')
        x = K.multiplicative_generator()

        if l == (k-1):
            if existence:
                return True
            return K, K.cyclotomic_cosets(x**((v-1)//k))[1:]

        if t == 1:
            # some of the difference set constructions VI.18.48 from the
            # Handbook of combinatorial designs
            # q = 3 mod 4
            if v%4 == 3 and k == (v-1)//2:
                if existence:
                    return True
                D = K.cyclotomic_cosets(x**2, [1])

            # q = 4t^2 + 1, t odd
            elif v%8 == 5 and k == (v-1)//4 and arith.is_square((v-1)//4):
                if existence:
                    return True
                D = K.cyclotomic_cosets(x**4, [1])

            # q = 4t^2 + 9, t odd
            elif v%8 == 5 and k == (v+3)//4 and arith.is_square((v-9)//4):
                if existence:
                    return True
                D = K.cyclotomic_cosets(x**4, [1])
                D[0].insert(0,K.zero())

        if D is None and l == 1:
            one = K.one()

            # Wilson (1972), Theorem 9
            if k%2 == 1:
                m = (k-1) // 2
                xx = x**m
                to_coset = {x**i * xx**j: i for i in xrange(m) for j in xrange((v-1)/m)}
                r = x ** ((v-1) // k)  # primitive k-th root of unity
                if len(set(to_coset[r**j-one] for j in xrange(1,m+1))) == m:
                    if existence:
                        return True
                    B = [r**j for j in xrange(k)]  # = H^((k-1)t) whose difference is
                                                   # H^(mt) (r^i - 1, i=1,..,m)
                    # Now pick representatives a translate of R for by a set of
                    # representatives of H^m / H^(mt)
                    D = [[x**(i*m) * b for b in B] for i in xrange(t)]

            # Wilson (1972), Theorem 10
            else:
                m = k//2
                xx = x**m
                to_coset = {x**i * xx**j: i for i in xrange(m) for j in xrange((v-1)/m)}
                r = x ** ((v-1) // (k-1))  # primitive (k-1)-th root of unity
                if (all(to_coset[r**j-one] != 0 for j in xrange(1,m)) and
                    len(set(to_coset[r**j-one] for j in xrange(1,m))) == m-1):
                    if existence:
                        return True
                    B = [K.zero()] + [r**j for j in xrange(k-1)]
                    D = [[x**(i*m) * b for b in B] for i in xrange(t)]

            # Wilson (1972), Theorem 11
            if D is None and k == 6:
                r = x**((v-1)//3)  # primitive cube root of unity
                r2 = r*r
                xx = x**5
                to_coset = {x**i * xx**j: i for i in xrange(5) for j in xrange((v-1)/5)}
                for c in to_coset:
                    if c == 1 or c == r or c == r2:
                        continue
                    if len(set(to_coset[elt] for elt in (r-1, c*(r-1), c-1, c-r, c-r**2))) == 5:
                        if existence:
                            return True
                        B = [one,r,r**2,c,c*r,c*r**2]
                        D = [[x**(i*5) * b for b in B] for i in xrange(t)]
                        break

    if D is None and are_hyperplanes_in_projective_geometry_parameters(v,k,l):
        _, (q,d) = are_hyperplanes_in_projective_geometry_parameters(v,k,l,True)
        if existence:
            return True
        else:
            G,D = singer_difference_set(q,d)

    if D is None:
        if existence:
            return Unknown
        raise NotImplementedError("No constructions for these parameters")

    if check and not is_difference_family(G,D,short_blocks=short_blocks,verbose=False):
        raise RuntimeError

    return G, D
