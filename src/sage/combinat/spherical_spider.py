# -*- coding: utf-8 -*-
r"""
### Introduction
This is an implementation of finitely generated free spiders.
The account below is intended as an extended introduction.
There are technical details which I skate over and which need to
be dealt with in the implementation.

This is intended to be the first phase of a project to implement
the Bendix-Knuth completion algorithm discussed in [5]_. This algorithm starts
with a finite presentation and iteratively constructs new relations.
If it terminates the final presentation is confluent.

### Spiders

The notion of spiders was introduced in [3]_.
A spider consists of a set (or vector space) with the operations of rotate, join and stitch.
There are axioms for these operations and a spider is equivalent to a strict pivotal
category or, with an extra axiom, to a strict spherical category. The motivation was
to study the category of finite dimensional representations of a quantum group.
These categories give examples of spiders and the main result of the paper was to
give finite confluent presentations for the rank two examples, A2, B2=C2, G2, (the rank one example
was known previously as the skein relation approach to the Jones polynomial).
A rank three example is given in [6]_.

It has been an open problem since then to construct finite confluent presentations
for higher rank examples. It is known (unpublished) that these examples are finitely
generated but not that these are finitely presented. A finite confuent presentation
would give algorithms for computing link polynomials and for doing the caculations
in [1]_.

### Webs.

The first phase of working with finite presentations is to understand the free objects.
The elements of a free spider are called webs.

The data for a free spider is first a (finite) set X with an involution x. Then the objects of
the free strict spherical category with be the free monoid on X with antiinvolution given on the
generators by x.

The usual approach to webs is to define a web as a planar graph with oriented edges labelled by X.
Here the graph is embedded in a disc and the embedding is taken up to isotopy. The benefit of
this approach is that these pictures can be drawn on a blackboard (or similar). However this
approach gives the misleading idea that this is a branch of topology and, more importantly,
is not suitable for a computer implementation.
Here we represent a web by a combinatorial structure (essentially a ribbon graph, constellation)
but we need to allow the web to have boundary points. Our basic operations are rotate and glue.
It is clear that this is equivalent to rotate, join and stitch.

### Operations

Since a spider is a set with operations and we have defined these operations for webs,
it is clear that we have constructed a spider (assuming we have checked that the operations
satisfy the axioms). However we have not explained the sense in which this is a free spider.

One general theory of algebraic theories is given by monads. In this setting we have
an underlying functor which has a left adjoint. In the theory of groups the underlying functor
gives a set and applying the left adjoint to a set gives a free group and we call the original
set the generators of the group.

This is one-dimensional is the sense that free objects are constructed in terms of words.
These are lists of generators and are written on a line. Spiders and webs are two-dimensional
since webs have to be drawn as two dimensional.

In our setting, the set of objects of a spherical category has more structure; namely
the rotation map. Here the set of objects is the free monoid on a set of generators
which is given by a list of generators. Then rotation is rotation of this list.
The underlying functor takes the set of webs, the set of words and the boundary map.
We fix the set of words with rotation. Then this underlying functor gives a set with
rotation together with an equivariant map to words. In order to construct the left adjoint
we start with an object in the underlying category. These are called generators. Then
we take all webs such that every vertex is a generator. Then to justify calling this an
algebraic theory, we need to check that this is the functor of a monad.

To see that this is a monad we change perspective on webs. We take the diagram of a web.
Then we can cut out a small disc around each vertex. This picture has no vertices but
is now a disc with a hole punched out for each vertex. Each of these pictures defines
an operation. Given a spider, we assign an object to each punched out hole so that the
boundaries match. Then we fill in each hole by attaching the object. For example,
glueing has two punched out holes corresponding to the two inputs of the glueing operation.
However we could also fill in a punched out hole by the picture of an operation.
This gives the picture of some operation. This means that these operations have the structure
of an operad. In fact this is a cyclic operad as defined in [2]_ and [4]_. Furthermore a spider
is a cyclic algebra for this cyclic operad. Taking the glueing operation as basic and
building up operations is the componential approach to cyclic operads given in [4]_.

### Implemented

This file has two main classes: the Element class :class:`SphericalWeb` and the Parent class
:class:`SphericalSpider`. Then :meth:`vertex` is the basic construction of a web. Then
:meth:`glue` has input two webs and an integer and output a web; and :meth:`polygon`
has input a list of webs and output a web. These operations build more complicated webs
starting with vertices. Once you have constructed a web you can see a picture using
:meth:`plot`. This takes the combinatorial data for a web and outputs a graphics object.


REFERENCES:

.. [1] Predrag Cvitanović
Group Theory: Birdtracks, Lie's, and Exceptional Groups
Princeton University Press, 2008
ISBN    0691118361, 9780691118369

.. [2] E Getzler, MM Kapranov
Cyclic operads and cyclic homology
http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.146.2678&rep=rep1&type=pdf

.. [3] G.Kuperberg
Spiders for rank 2 Lie algebras
Commun.Math. Phys. 180, 109–151 (1996)
:arxiv:`q-alg/9712003`

.. [4] Jovana Obradovic
Monoid-like definitions of cyclic operad
Theory and Applications of Categories, Vol. 32, (2017), No. 12, pp 396-436.
http://www.tac.mta.ca/tac/volumes/32/12/32-12.pdf

.. [5] Adam S Sikora and Bruce W Westbury
Confluence theory for graphs
Algebraic & Geometric Topology,
Vol. 7, (2007), pp 439–478
:arxiv:`math/0609832`


.. [6] Bruce W. Westbury
Invariant tensors for the spin representation of so(7)
Mathematical Proceedings of the Cambridge Philosophical Society,
Vol. 144, (2008), pp 217-240
:arxiv:`math/0601209`

AUTHORS:

- Bruce Westbury (2021): initial version

"""

#*****************************************************************************
#       Copyright (C) 2021 Bruce Westbury bruce.westbury@gmail.com
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from sage.misc.cachefunc import cached_method
from sage.structure.parent import Parent
from sage.structure.element import Element
from sage.structure.unique_representation import UniqueRepresentation
from sage.misc.classcall_metaclass import ClasscallMetaclass
from sage.graphs.graph import Graph
from sage.combinat.permutation import Permutation
from sage.combinat.baxter_permutations import BaxterPermutations
from sage.structure.richcmp import richcmp, op_EQ, op_NE
from typing import NamedTuple
from copy import copy

class Strand(NamedTuple):
    """
    Record the information used to draw an edge.

    EXAMPLES::

        sage: Strand(1,'black',False)
        Strand(oriented=1, colour='black', crossing=False)
    """
    oriented: int
    colour: str
    crossing: bool

    def dual(self):
        """
        Return the dual of ``self``.

        EXAMPLES::

            sage: Strand(1,'black',False).dual()
            Strand(oriented=-1, colour='black', crossing=False)
        """
        return Strand(-self.oriented, self.colour, self.crossing)

class halfedge():
    """
    The class of half edges in a surface graph.

    This should probably be an attribute either of SphericalWeb or SphericalSpider
    """
    def __init__(self, st=Strand(0,'black',False)):
        """
        EXAMPLES::

            sage: halfedge()
            <sage.combinat.spherical_spider.halfedge object at ...>
        """
        self.strand = st

    def __hash__(self):
        return hash(self.strand)

    def _repr_(self):
        """
        Return a string representation of ``self``.

        EXAMPLES::

        sage: halfedge() # indirect test
        <sage.combinat.spherical_spider.halfedge object at ...>
        """
        return f"({self.strand.oriented},{self.strand.colour},{self.strand.crossing})"

    def dual(self):
        """
        Construct the dual halfedge.

        EXAMPLES::

            sage: halfedge().dual()
            <sage.combinat.spherical_spider.halfedge object at ...>
        """
        return halfedge(self.strand.dual())

class SphericalWeb(Element):
    r"""The class of webs.

    This consists of
    * a set of half-edges
    * a bijection `c` on the set of half-edges with no fixed points
    * an involution `e` on a subset of the half-edges

    The half-edges for which `e` is undefined are the boundary half-edges.
    This set has a total order.

    The only orbits of `c` of order two have both half-edges in the boundary
    or are a loop.
    """

    def __init__(self, c:  dict, e: dict, b: list, check=True):
        r"""
        Initialise an instance of :class`SphericalWeb`.

        INPUT:

            * `c` a bijection of the set of half-edges
            * `e` a partial involution of the set of half-edges
            * `b` the ordered list of boundary edges

        EXAMPLES::

            sage: b = [halfedge(),halfedge()]
            sage: c = {b[0]:b[1], b[1]:b[0]}
            sage: SphericalWeb(c,{},b)
            The plain spherical web with c = (1, 0) and e = ().
        """

        bd = tuple([a.strand for a in b])
        parent = SphericalSpider(bd)
        Element.__init__(self, parent)

        self.cp = c
        self.e = e
        self.b = b
        self.boundary = tuple(b)
        self.normalize()
        if check:
            self.check()

    def __copy__(self):
        r"""
        Implement the abstract method :meth:`__copy__` of :class:`ClonableElement`.

        EXAMPLES::

            #sage: SphericalSpider('plain').vertex(3).__copy__()
            The plain spherical web with c = (1, 2, 0) and e = ().
        """
        D = {a:halfedge(a.strand) for a in self.cp}
        c = {D[a]:D[self.cp[a]] for a in self.cp}
        e = {D[a]:D[self.e[a]] for a in self.e}
        b = [D[a] for a in self.boundary]
        return SphericalWeb(c, e, b)

    def check(self):
        r"""
        Implement the abstract method :meth:`check` of :class:`ClonableElement`.

        Check ``self`` is a valid web.

        EXAMPLES::

            sage: a = halfedge()
            sage: SphericalWeb({a:a}, dict(), [a], check=False)
            The plain spherical web with c = (0,) and e = ().
            sage: SphericalWeb({a:a}, dict(), [a])
            Traceback (most recent call last):
            ...
            ValueError: the mapping c has at least one fixed point
        """
        c = self.cp
        e = self.e
        b = self.b
        h = set(c)
        if not all(isinstance(a,halfedge) for a in h):
            raise ValueError("every element must be a half-edge")
        if set(c.values()) != h:
            raise ValueError("the map c is required to be a bijection")
        if any(e[e[a]] != a for a in e):
            raise ValueError("the map e must be an involution")
        if any(c[a] == a for a in c):
            raise ValueError("the mapping c has at least one fixed point")
        if any(e[a] == a for a in e):
            raise ValueError("the mapping e has at least one fixed point")
        if not set(e.keys()).issubset(h):
            raise ValueError("the domain of e must be a subset of the domain of c")
        if not set(b).issubset(h):
            raise ValueError("the boundary must be a subset of the domain of c")
        if not set(e.keys()).isdisjoint(set(b)):
            raise ValueError("the domain of e must not intersect the boundary")
        #for i,a in enumerate(b):
        #    u = a
        #    while c[u] in e:
        #        u = e[c[u]]
        #    j = b.index(c[u])
        #    if 0 < j < i:
        #       raise ValueError("boundary is inconsistent")

    def normalize(self):
        r"""
        This removes nearly all vertices of degree two.

        EXAMPLES::

            sage: h = [halfedge() for i in range(4)]
            sage: c = {h[0]:h[1], h[1]:h[0], h[2]:h[3], h[3]:h[2]}
            sage: e = {h[1]:h[2],h[2]:h[1]}
            sage: b = [h[0],h[3]]
            sage: SphericalWeb(c, e, b) # indirect doctest
            The plain spherical web with c = (1, 0) and e = ().

        TESTS::

        This should not ever happen.

            #sage: SphericalSpider('plain').vertex(2) # indirect doctest
            The plain spherical web with c = (1, 0) and e = ().

        Check loops are not removed.

            #sage: SphericalSpider('plain').loop() # indirect doctest
            A closed plain spherical web with 1 edges.
        """
        flag = True
        while flag :
            flag = False
            c = self.cp
            e = self.e
            rm = [a for a in e if c[c[a]] == a]
            if len(rm) != 0:
                x = rm[0]
                z = e[x]
                y = c[x]
                if y in e and z != y:
                    flag = True
                    e[z] = e[y]
                    e[e[y]] = z
                    c.pop(x)
                    c.pop(y)
                    e.pop(x)
                    e.pop(y)
                elif y in self.parent().boundary:
                    flag = True
                    c[y] = c[z]
                    w = [a for a in c if c[a] == z][0]
                    c[w] = y
                    c.pop(x)
                    c.pop(z)
                    e.pop(x)
                    e.pop(z)

    def _repr_(self):
        r"""
        Overload default implementation.

        EXAMPLES::

            ##sage: S = SphericalSpider('plain')
            #sage: u = S.vertex(3)
            #sage: S.polygon([u,u,u])._repr_()
            'The plain spherical web with c = (3, 5, 7, 4, 0, 6, 1, 8, 2) and e = (6, 7, 8, 3, 4, 5).'
        """
        if len(self.b) > 0:
            cn, en = self.canonical()
            return f"The spherical web with c = {cn} and e = {en}."
        else:
            return f"A closed spherical web with {int(len(self.e)/2)} edges."

    @cached_method
    def canonical(self):
        r"""
        A canonical labelling of the elements of ``self``.

        This returns two lists of integers such that ``self``
        can be recovered, up to isomorphism, from these two sequences.

        Let ``self`` have `n` elements and `k` boundary elements.
        Then the first list is a bijection on [0,1,...,n-1] and
        the second list is an involution on [k,k+1,...,n-1].

        EXAMPLES::

            #sage: S = SphericalSpider('plain')
            #sage: u = S.vertex(3)
            #sage: cn, en = S.polygon([u,u,u,u]).canonical()
            #sage: cn
            (4, 6, 8, 10, 5, 0, 7, 1, 9, 2, 11, 3)
            #sage: en
            (7, 10, 9, 4, 11, 6, 5, 8)
        """
        b = self.parent().boundary
        c = self.cp
        e = self.e
        k = len(b)
        gen = self._traversal(b)
        gl = list(gen) # This defeats the purpose of using a generator.
        Dp = {a:i for i,a in enumerate(b)}
        Dp.update({a:(k+i) for i,a in enumerate(gl)})
        cn = tuple([Dp[c[a]] for a in b]+[Dp[c[a]] for a in gl])
        en = tuple([Dp[e[a]] for a in gl])
        return cn, en

    def __hash__(self):
        r"""
        Overload the :method:`__hash__`.

        This is needed to put a :class:`SphericalWeb` into a :class:`set`
        or to use it as a key in a :class:`dict'.

        EXAMPLES::

            #sage: S = SphericalSpider('plain')
            #sage: u = S.vertex(3)
            #sage: v = S.polygon([u,u,u,u])
            #sage: v.__hash__()  # random

            #sage: hash(v) # random

            #sage: w = SphericalSpider('plain').vertex(3)
            #sage: set([u,w]) # indirect doctest
            {The plain spherical web with c = (1, 2, 0) and e = ().}
        """
        return hash((self.parent(),*self.canonical()))

    def _richcmp_(self, other, op):
        """
        Overload :meth:`__eq__` and :meth:`__ne__`.

        EXAMPLES::

            #sage: S = SphericalSpider('plain')
            #sage: u = S.polygon([S.vertex(3)]*4)
            #sage: v = S.polygon([S.vertex(3)]*4)
            #sage: u is v, u == v, u != v # indirect doctest
            (False, True, False)
            #sage: u < v # indirect doctest
            Traceback (most recent call last):
            ...
            TypeError: '<' not supported between ... and 'SphericalWeb'

        TODO::

            This should take the parent and/or type into account.
        """
        if op == op_EQ or op == op_NE:
            return richcmp(self.canonical(), other.canonical(), op)
        else:
            raise NotImplementedError

#### End of underscore methods ####

#### Start of methods for working with webs ####

    def _traversal(self, initial):
        """
        A generator for the elements of ``self`` connected to the
        elements in ``initial``.

        EXAMPLES::

            #sage: w = SphericalSpider('plain').vertex(3)
            #sage: w._traversal(w.boundary)
            <generator object SphericalWeb._traversal at ...>
            #sage: w._traversal(w.boundary[0])
            <generator object SphericalWeb._traversal at ...>
        """
        if isinstance(initial,halfedge):
            initial = tuple([initial])
        else:
            initial = tuple(initial)
        if not set(initial).issubset(self.cp):
            raise ValueError("initial must be a subset of the set of elements")

        c = self.cp
        e = self.e

        visited = list(initial)
        new = list()
        flag = True
        while flag:
            flag = False
            for a in visited:
                b = c[a]
                while b not in visited:
                    new.append(b)
                    yield b
                    flag = True
                    b = c[b]
            visited += new
            for a in visited:
                if a in e:
                    b = e[a]
                    if b not in visited:
                        new.append(b)
                        yield b
                        flag = True
            visited += new
            new = list()
        return

    @staticmethod
    def _stitch(c, e, x, y):
        """
        Connect `x` and `y`.

        This is a low level method that is not intended to be called directly.
        It was written to comply with the DRY principle.

        EXAMPLES::

            #sage: S = SphericalSpider('plain')
            #sage: u = S.vertex(3)
            #sage: c,e = u._stitch(u.cp,u.e,u.boundary[0],u.boundary[-1])
            #sage: len(c),len(e)
            (5, 4)
        """
        if x.strand.dual() != y.strand:
            raise ValueError(f"{x.strand} and {y.strand} must be dual")

        u = halfedge(x.strand.dual())
        v = halfedge(y.strand.dual())
        c[u] = v
        c[v] = u
        e[x] = u
        e[u] = x
        e[y] = v
        e[v] = y

        return c, e

    def rotate(self, k):
        r"""Rotate the boundary anticlockwise `k` steps.

        EXAMPLES::

            #sage: S = SphericalSpider('plain')
            #sage: u = S.polygon([S.vertex(3)]*5)
            #sage: u.rotate(3)
            The plain spherical web with c = (5, 7, 9, 11, 13, 6, 0, 8, 1, 10, 2, 12, 3, 14, 4) and e = (8, 13, 10, 5, 12, 7, 14, 9, 6, 11).
            #sage: u.rotate(-1)
            The plain spherical web with c = (5, 7, 9, 11, 13, 6, 0, 8, 1, 10, 2, 12, 3, 14, 4) and e = (8, 13, 10, 5, 12, 7, 14, 9, 6, 11).
        """
        result = self.__copy__()
        b = result.boundary
        result.boundary = b[k:]+b[:k]
        return result

    def glue(self, other, n):
        r"""Glue two ribbon graphs together.

        EXAMPLES::

            #sage: u = SphericalSpider('plain').vertex(3)
            #sage: v = SphericalSpider('plain').vertex(3)
            #sage: u.glue(v,1)
            The plain spherical web with c = (1, 4, 3, 5, 0, 2) and e = (5, 4).
            #sage: u.glue(v,0)
            The plain spherical web with c = (1, 2, 0, 4, 5, 3) and e = ().
        """
        if n < 0:
            raise ValueError(f"n={n} cannot be negative")
        parent = self.parent()
        if parent != other.parent():
            raise ValueError(f"the two parents {self.parent()} and {other.parent()} are different")
        if n > len(self.boundary) or n > len(other.boundary):
            raise ValueError(f"n={n} is too large")

        ns = self.__copy__()
        no = other.__copy__()

        bs = ns.boundary
        bo = no.boundary
        if n == 0:
            b = bs+bo
        else:
            b = bs[:-n]+bo[n:]

        c = {**ns.cp, **no.cp}
        e = {**ns.e, **no.e}

        for x,y in zip(reversed(bs[-n:]),bo[:n]):
            c, e =  self._stitch(c,e,x,y)

        return SphericalWeb(parent, c, e, b)

    def mirror_image(self):
        r"""
        Construct the mirror image of ``self``.

        EXAMPLES::

            #sage: S = SphericalSpider('plain')
            #sage: u = S.vertex(3)
            #sage: u.glue(S.vertex(4),1).mirror_image()
            The plain spherical web with c = (1, 2, 5, 4, 6, 0, 3) and e = (6, 5).

            #sage: v = u.glue(u,1).glue(S.vertex(4),1)
            #sage: v == v.mirror_image()
            False
        """
        D =  {a:halfedge() for a in self.cp}
        cn = {D[self.cp[a]]:D[a] for a in D}
        en = {D[a]:D[self.e[a]] for a in self.e}
        bn = reversed([D[a] for a in self.boundary])
        return SphericalWeb(self.parent(), cn, en, bn)

    def vertices(self):
        """
        Find the vertices of ``self``.

        These are the orbits of `c`.

        EXAMPLES::

            #sage: S = SphericalSpider('plain')
            #sage: u = S.polygon([S.vertex(3)]*4)
            #sage: [len(a) for a in u.vertices()]
            [3, 3, 3, 3]
        """
        c = self.cp
        he = set(c.keys())
        result = set()
        while len(he) != 0:
            a = he.pop()
            vertex = [a]
            b = c[a]
            while b != a:
                vertex.append(b)
                he.discard(b)
                b = c[b]
            result.add(tuple(vertex))
        return result

    def faces(self):
        """
        Find the faces of ``self``.

        EXAMPLES::

            #sage: S = SphericalSpider('plain')
            #sage: len(S.vertex(3).faces())
            3
            #sage: len(S.vertex(4).faces())
            4
            #sage: u = SphericalSpider('plain').vertex(3)
            #sage: v = SphericalSpider('plain').vertex(3)
            #sage: len(u.glue(v,0).faces())
            6
        """
        c = self.cp
        e = self.e
        he = set(c.keys())
        result = set()

        # First find the external faces.
        for a in self.boundary:
            u = a
            face = [a]
            he.discard(a)
            while c[u] in e:
                u = e[c[u]]
                face.append(u)
                he.discard(u)
            result.add(tuple(face))

        # Now find the internal faces.
        while len(he) != 0:
            a = he.pop()
            face = [a]
            u = e[c[a]]
            while u != a:
                face.append(u)
                he.discard(u)
                u = e[c[u]]
            result.add(tuple(face))

        return result

    def is_closed(self):
        """
        Return ``True`` if ``self`` is closed.

        Note that this means that the boundary is empty.

        EXAMPLES::

            #sage: SphericalSpider('plain').vertex(3).is_closed()
            False
            #sage: SphericalSpider('plain').loop().is_closed()
            True
        """
        return len(self.boundary) == 0

    def is_connected(self):
        """
        Return ``True`` if ``self`` is connected.

        Note that this means that the diagram including the boundary
        is connected.

        EXAMPLES::

            #sage: SphericalSpider('plain').vertex(3).is_connected()
            True
            #sage: SphericalSpider('plain').loop().is_connected()
            False
            #sage: u = SphericalSpider('plain').vertex(3)
            #sage: v = SphericalSpider('plain').vertex(3)
            #sage: u.glue(v,0).is_connected()
            True
        """
        return len(self.cp) == len(self.canonical()[0])

    def components(self):
        """
        Return the closed components of ``self``.

        This is the complement of the connected component of the boundary.

        EXAMPLES::

            #sage: u = SphericalSpider('plain').vertex(3)
            #sage: u.components()
            (The plain spherical web with c = (1, 2, 0) and e = ().,
            A closed plain spherical web with 0 edges.)
            #sage: u.glue(u,0)
            The plain spherical web with c = (1, 2, 0, 4, 5, 3) and e = ().
            #sage: u.glue(u,0).components()
            (The plain spherical web with c = (1, 2, 0, 4, 5, 3) and e = ().,
            A closed plain spherical web with 0 edges.)
        """
        Dn = {a:halfedge(a.strand) for a in self.boundary}
        for a in self._traversal(self.boundary[0]):
            Dn[a] = halfedge(a.strand)

        cn = {Dn[a]:Dn[self.cp[a]] for a in self.cp}
        en = {Dn[a]:Dn[self.e[a]] for a in self.e}
        bn = [Dn[a] for a in self.boundary]
        wb = SphericalWeb(self.parent(), cn, en, bn)

        Dc = {a:halfedge(a.strand) for a in self.cp if not a in Dn}
        cc = {Dc[a]:Dc[self.cp[a]] for a in Dc}
        ec = {Dc[a]:Dc[self.e[a]] for a in Dc}
        wc = SphericalWeb(self.parent(), cc, ec, [])

        return wb, wc

    def is_decomposable(self):
        """
        Return True if ``self`` is decomposable.

        A web `w` is decomposable if it can be written as `w = u.glue(v,0)`
        where `u` and `v` are non-empty.

        Note that this means that the diagram excluding the boundary
        is connected.

        EXAMPLES::

            #sage: u = SphericalSpider('plain').vertex(3)
            #sage: u.is_decomposable()
            False
            #sage: u.glue(u,0).is_decomposable()
            True
        """
        if len(self.boundary) == 0:
            raise ValueError("not implemented for a closed web")
        return len(self.cp) != len(list(self._traversal(self.boundary[0])))+1

    def is_separable(self):
        r"""
        Return ``True`` if ``self`` is separable.

        This means each face has distinct vertices.
        Including the boundary faces.

        EXAMPLES::

            #sage: S = SphericalSpider('plain')
            #sage: S.vertex(4).glue(S.vertex(2),2).is_separable()
            True
        """
        from itertools import product
        for v,f in product(self.vertices(),self.faces()):
            if len(set(v).intersection(set(f))) > 1:
                return True
        return False

    def is_simple(self):
        """
        Return ``True`` if ``self`` is a simple graph.

        EXAMPLES::

            #sage: S = SphericalSpider('plain')
            #sage: S.vertex(4).glue(S.vertex(2),2).is_simple()
            False
            #sage: S.vertex(4).glue(S.vertex(4),2).is_simple()
            False
        """
        return all(len(x)>2 for x in self.faces())

    def to_graph(self):
        r"""
        Construct the graph of ``self``.

        EXAMPLES::

            #sage: S = SphericalSpider('plain')
            #sage: S.vertex(3).to_graph()
            Graph on 3 vertices
            #sage: S.polygon([S.vertex(3)]*3).to_graph()
            Graph on 9 vertices
        """
        c = self.cp
        e = self.e
        G = Graph({a:[c[a]] for a in c})
        # This adds each edge twice.
        for a in e:
            G.add_edge(a,e[a],'e')
        return G

    def show(self):
        r"""Show the web ``self``.

        EXAMPLES::

            #sage: SphericalSpider('plain').vertex(3).show()
            Graphics object consisting of 4 graphics primitives
        """
        return self.to_graph().plot(vertex_labels=False)

    def _layout(self):
        r"""
        Layout the planar map.

        This uses the barycentric layout. The boundary points are the vertices of
        a regular polygon. Then the vertices are positioned so that each vertex
        is at the centre of mass of its neighbours.

        EXAMPLES::

            #sage: S = SphericalSpider('plain')
            #sage: len(S.polygon([S.vertex(3)]*3)._layout())
            6

            #sage: u = S.vertex(3)
            #sage: len(u.glue(u,1)._layout())
            5

            If the graph is not simple the diagram will degenerate.

            #sage: len(S.vertex(4).glue(S.vertex(2),2)._layout())
            2

            If there are no boundary points only the boundary circle is drawn.

            #sage: S.loop()._layout()
            set()
        """
        from sage.matrix.all import matrix
        from sage.functions.trig import sin, cos
        from sage.all import pi

        vt = list(self.vertices())
        nv = len(vt)
        d = len(self.boundary)
        M = matrix(nv,nv)
        for i,u in enumerate(vt):
            M[i,i] = len(u)
            x = set(self.e[a] for a in u if a in self.e)
            for j,v in enumerate(vt):
                if i != j:
                    M[i,j] = -len(x.intersection(set(v)))

        U = matrix(nv,1,0.0)
        for i,b in enumerate(self.boundary):
            x = cos(2*pi*i/d).n()
            for j,v in enumerate(vt):
                if b in v:
                    U[j,0] = U[j,0] + x

        V = matrix(nv,1,0.0)
        for i,b in enumerate(self.boundary):
            y = sin(2*pi*i/d).n()
            for j,v in enumerate(vt):
                if b in v:
                    V[j,0] = V[j,0] + y

        Mi = M.inverse()
        pos = [(r[0],s[0]) for r,s in zip(Mi*U, Mi*V)]

        result = set()
        for i,u in enumerate(vt):
            for j,b in enumerate(self.boundary):
                if self.cp[b] in u:
                    x = cos(2*pi*j/d).n()
                    y = sin(2*pi*j/d).n()
                    result.add(((x,y),pos[i],))
            x = set(self.e[a] for a in u if a in self.e)
            for j,v in enumerate(vt):
                if i < j:
                    if any(r in v for r in x):
                        result.add((pos[i],pos[j],))

        return result

    def plot(self):
        r"""
        Plot the planar map.

        EXAMPLES::

            #sage: S = SphericalSpider('plain')
            #sage: S.polygon([S.vertex(3)]*3).plot()
            Graphics object consisting of 7 graphics primitives

            #sage: S = SphericalSpider('plain')
            #sage: u = S.vertex(3)
            #sage: u.glue(u,1).plot()
            Graphics object consisting of 6 graphics primitives

            If the graph is not simple the diagram will degenerate.

            #sage: S = SphericalSpider('plain')
            #sage: S.vertex(4).glue(S.vertex(2),2).plot()
            Graphics object consisting of 3 graphics primitives

            If there are no boundary points only the boundary circle is drawn.

            #sage: S.loop().plot()
            Graphics object consisting of 1 graphics primitive

        TODO::

        Add colour, direction, under crossing.
        """
        from sage.plot.circle import circle
        from sage.plot.line import line

        lines = self._layout()
        G = circle((0,0),1)
        for a in lines:
                G += line(a,thickness=2,rgbcolor=(1,0,0))
        G.set_aspect_ratio(1)
        G.axes(False)
        return G

    def _latex_(self):
        """
        Return a LaTeX representation of ``self``.

        EXAMPLES::

            #sage: S = SphericalSpider('plain')
            #sage: u = S.vertex(3)
            #sage: S.polygon([u]*3)._latex_()
            ...
            #sage: u.glue(u,1)._latex_()
            ...

            If the graph is not simple the diagram will degenerate.

            #sage: S.vertex(4).glue(S.vertex(2),2)._latex_()
            '\\begin{tikzpicture}\n\\draw (0,0) circle (1cm);\n\\draw (-1.00000000000000,0.0) -- (0.0,0.0);\n\\draw (1.00000000000000,0.0) -- (0.0,0.0);\n\\end{tikzpicture}\n'

            If there are no boundary points only the boundary circle is drawn.

            #sage: S.loop()._latex_()
            '\\begin{tikzpicture}\n\\draw (0,0) circle (1cm);\n\\end{tikzpicture}\n'

        TODO::

            Add colour, direction, under crossing.
        """
        lines = self._layout()

        result = "\\begin{tikzpicture}\n"
        result += "\\draw (0,0) circle (1cm);\n"
        for a in lines:
            result += "\\draw ({},{}) -- ({},{});\n".format(a[0][0],a[1][0],a[1][0],a[1][1])
        result += "\\end{tikzpicture}\n"

        return result

#### End of methods for working with webs ####

#### Start of methods for rewriting ####

    def search(self, h):
        r"""
        Find copies of h in ``self``

        EXAMPLES::

            #sage: S = SphericalSpider('plain')
            #sage: u = S.vertex(3)
            #sage: len(list(S.polygon([u]*4).search(u)))
            12

        TODO::

            This should be rewritten to use :meth:``_traversal``.
        """
        if self.parent() != h.parent():
            raise ValueError(f"the two parents {self.parent()} and {h.parent()} are different")

        def test(x):
            flag = True
            while flag:
                flag = False
                newD = dict()
                for a in Dm:
                    while not (c[a] in Dm):
                        if a in Dm:
                            newD[c[a]] = self.cp[Dm[a]]
                        elif a in newD:
                            newD[c[a]] = self.cp[newD[a]]
                        a = c[a]
                for a in Dm:
                    if a in e:
                        if not (e[a] in Dm):
                            if not Dm[a] in self.e:
                                return False
                            newD[e[a]] = self.e[Dm[a]]
                if len(newD) != 0:
                    Dm.update(newD)
                    flag = True
                for a in Dm:
                    if c[a] in Dm:
                        if Dm[c[a]] != self.cp[Dm[a]]:
                            return False
                    if a in e:
                        if e[a] in Dm:
                            if not Dm[a] in self.e:
                                return False
                            if Dm[e[a]] != self.e[Dm[a]]:
                                return False
            return True

        c = h.cp
        e = h.e
        for x in self.cp:
            Dm = {h.boundary[0]:x}
            if test(x):
                assert [ a for a in c if not (a in Dm) ] == [], "Mapping is not fully defined."
                if len(set(Dm.values())) == len(Dm):
                    yield Dm

    def replace(self, k, D, h):
        r"""
        Replace image of map D:h -> ``self`` by k

        EXAMPLES::

            #sage: S = SphericalSpider('plain')
            #sage: h = S.vertex(3)
            #sage: g = S.polygon([h]*3)
            #sage: D = next(g.search(h))
            #sage: g.replace(g,D,h)
            The plain spherical web with c = (3, 5, ... 12, 9) and e = (9, 10, ... 14, 13).
        """
        parent = self.parent()
        if parent != k.parent():
            raise ValueError(f"the two parents {self.parent()} and {k.parent()} are different")
        if parent != h.parent():
            raise ValueError(f"the two parents {self.parent()} and {h.parent()} are different")

        hb = [a.strand for a in h.boundary]
        kb = [a.strand.dual() for a in k.boundary]
        if hb != kb:
            raise ValueError(f"boundaries of {k} and {h} must match")

        Ds = {a:halfedge(a.strand) for a in self.cp if not a in D.values()}
        Dk = {a:halfedge(a.strand) for a in k.cp}
        c = {Ds[a]:Ds[self.cp[a]] for a in Ds}
        c.update({Dk[a]:Dk[k.cp[a]] for a in Dk})

        e = {Ds[a]:Ds[self.e[a]] for a in Ds if a in self.e and self.e[a] in Ds}
        e.update({Dk[a]:Dk[k.e[a]] for a in k.e})

        Db = {x:y for x,y in zip(h.boundary,k.boundary)}
        b = [None]*len(self.boundary)
        for i,a in enumerate(self.boundary):
            if a in Ds:
                b[i] = Ds[a]

        for a in h.boundary:
            if D[a] in self.e:
                x = Ds[self.e[D[a]]]
                y = Dk[Db[a]]
                c, e = self._stitch(c,e,x,y)
            else:
                i = self.boundary.index(D[a])
                b[i] = Dk[Db[a]]

        return SphericalWeb(parent, c, e, b)

#### End  of methods for rewriting ####

#### Start of Parent ####

class SphericalSpider(UniqueRepresentation, Parent):
    r"""
    The Parent class for SphericalWeb.

    EXAMPLES::

        sage: SphericalSpider(tuple([Strand(0,'black',False),Strand(0,'black',False)]))
        The spherical spider with boundary (Strand(oriented=0, colour='black', crossing=False), ...).
        sage: SphericalSpider(tuple([]))
        The spherical spider with boundary ().
    """
    def __init__(self, boundary):
        r"""
        Initialise an instance of this class.

        EXAMPLES::

            sage: SphericalSpider(tuple([Strand(0,'black',False),Strand(0,'black',False)]))
            The spherical spider with boundary (Strand(oriented=0, colour='black', crossing=False), ...).
        """

        self.boundary = tuple(boundary)

        Parent.__init__(self)

    def _repr_(self):
        r"""
        Overload the default method.

        EXAMPLES::

            sage: P = SphericalSpider(tuple([Strand(0,'black',False)]*3))
            sage: P._repr_()
            "The spherical spider with boundary (Strand(oriented=0, colour='black', crossing=False),  ...)."
        """
        return f"The spherical spider with boundary {self.boundary}."

    Element = SphericalWeb

    def vertex(self):
        r"""
        Construct a single vertex.

        EXAMPLES::

            sage: SphericalSpider(tuple([Strand(0,'black',False)]*4)).vertex()
            The plain spherical web with c = (1, 2, 3, 0) and e = ().
        """
        bd = self.boundary
        n = len(bd)
        if n<2:
            raise ValueError(f"n={n} must be at least 2")

        b = [None]*n
        for i, a in enumerate(bd):
            b[i] = halfedge(a)
        c = {b[i-1]:b[i] for i in range(n)}
        e = dict([])
        return SphericalWeb(c,e,b)

#### End of Parent ####

def loop(st: Strand):
    r"""
    Construct a loop.

    EXAMPLES::

        sage: sage.combinat.spherical_spider.loop(Strand(0,'black',False))
        A closed spherical web with 1 edges.
    """

    h = [halfedge(st),halfedge(st)]
    c = {h[0]:h[1], h[1]:h[0]}
    e = {h[0]:h[1], h[1]:h[0]}
    return SphericalWeb(c,e,[])

def empty():
    """
    Construct the empty diagram.

    EXAMPLES::

        sage: sage.combinat.spherical_spider.empty()
        A closed spherical web with 0 edges.
    """

    return SphericalWeb({},{},[])

def polygon(corners):
    """
    Construct a polygon from a list of webs.

    EXAMPLES::

        #sage: S = SphericalSpider('plain')
        #sage: u = S.vertex(3)
        #sage: S.polygon([u,u,u])
        The plain spherical web with c = (3, 5, 7, 4, 0, 6, 1, 8, 2) and e = (6, 7, 8, 3, 4, 5).
        #sage: S.polygon([])
        A closed plain spherical web with 0 edges.
    """
    from functools import reduce

    if len(corners) == 0:
        return sage.combinat.spherical_spider.empty()

    # Avoid duplicates.
    cn = copy(corners)
    for i,u in enumerate(corners):
        for v in corners[:i]:
            if u == v:
                cn[i] = copy(u)
    corners = cn

    c = reduce(lambda r, s: {**r, **s}, [a.cp for a in corners])
    e = reduce(lambda r, s: {**r, **s}, [a.e for a in corners])

    for u,v in zip(corners,corners[1:]):
        x = u.boundary[-1]
        y = v.boundary[0]
        c,e = SphericalWeb._stitch(c,e,x,y)

    x = corners[-1].boundary[-1]
    y = corners[0].boundary[0]
    c,e = SphericalWeb._stitch(c,e,x,y)

    b = sum([list(a.boundary[1:-1]) for a in corners],[])
    return SphericalWeb(c, e, b)

def from_permutation(pi, baxter=True):
    r"""
    Construct a planar map from a two stack sorted permutation.

    This implements the algorithm in :arxiv:`math/0805.4180`.
    This algorithm is designed to apply to Baxter permutations.

    EXAMPLES::

        sage: from sage.combinat.spherical_spider import from_permutation
        sage: pi = Permutation([5,3,4,9,7,8,10,6,1,2])
        sage: from_permutation(pi)
        The plain spherical web with c = (1, 3, 6, 4, 5, 0, 7, 2, 10, 8, 9) and e = (7, 8, 9, 10, 3, 4, 5, 6).

        sage: pi = Permutation([2,4,1,3])
        sage: from_permutation(pi)
        Traceback (most recent call last):
        ...
        ValueError: [2, 4, 1, 3] is not a Baxter permutation
        sage: from_permutation(pi,baxter=False)
        The plain spherical web with c = (1, 0) and e = ().
    """
    if baxter:
        if not pi in BaxterPermutations():
            raise ValueError(f"{pi} is not a Baxter permutation")
    black = set((i+1,a) for i, a in enumerate(pi))
    n = len(pi)
    white = set([(1/2,1/2),(n+1/2,n+1/2)])
    ascents = [i+1 for i,a in enumerate(zip(pi,pi[1:])) if a[0] < a[1]]
    for a in ascents:
        l = max(pi[i] for i in range(a) if pi[i] < pi[a])
        white.add((a+1/2,l+1/2))

    Dup = {}
    Ddn = {}
    e = {}
    for a in black:
        w = [c for c in white if c[0]>a[0] and c[1]>a[1]]
        w.sort(key=lambda a: a[0]+a[1])
        r = halfedge()
        Dup[(w[0],a)] = r
        w = [c for c in white if c[0]<a[0] and c[1]<a[1]]
        w.sort(key=lambda a: a[0]+a[1])
        s = halfedge()
        Ddn[(w[-1],a)] = s
        e[r] = s
        e[s] = r

    c = {}
    for g in white:
        inco = [a for (w,a) in Ddn if w == g]
        inco.sort(key=lambda t: t[1]-t[0])
        outg = [a for (w,a) in Dup if w == g]
        outg.sort(key=lambda t: t[0]-t[1])
        #inco.reverse()
        for x,y in zip(inco,inco[1:]):
            c[Ddn[(g,x)]] = Ddn[(g,y)]
        for x,y in zip(outg,outg[1:]):
            c[Dup[(g,x)]] = Dup[(g,y)]
        if len(inco) > 0 and len(outg) > 0:
            c[Ddn[(g,inco[-1])]] = Dup[(g,outg[0])]
            c[Dup[(g,outg[-1])]] = Ddn[(g,inco[0])]
        elif len(inco) == 0 and len(outg) > 0:
            c[Dup[(g,outg[-1])]] = Dup[(g,outg[0])]
        elif len(inco) > 0 and len(outg) == 0:
            c[Ddn[(g,inco[-1])]] = Ddn[(g,inco[0])]
        else:
            raise RuntimeError("this can't happen")

    g = (1/2,1/2)
    inco = [a for (w,a) in Ddn if w == g]
    inco.sort(key=lambda t: t[0]-t[1])
    b =  [e[Ddn[(g,x)]] for x in inco]
    for a in inco:
        x = Ddn[(g,a)]
        e.pop(e[x])
        #c.pop(e[x])
        e.pop(x)
        c.pop(x)

    return SphericalWeb(c,e,b)


