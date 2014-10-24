r"""
Reduced permutations

A reduced (generalized) permutation is better suited to study strata of Abelian
(or quadratic) holomorphic forms on Riemann surfaces. The Rauzy diagram is an
invariant of such a component. Corentin Boissy proved the identification of
Rauzy diagrams with connected components of stratas. But the geometry of the
diagram and the relation with the strata is not yet totally understood.

AUTHORS:

- Vincent Delecroix (2009-09-29): initial version

TESTS::

    sage: from sage.dynamics.interval_exchanges.reduced import ReducedPermutationIET
    sage: ReducedPermutationIET([['a','b'],['b','a']])
    a b
    b a
    sage: ReducedPermutationIET([[1,2,3],[3,1,2]])
    1 2 3
    3 1 2
    sage: from sage.dynamics.interval_exchanges.reduced import ReducedPermutationLI
    sage: ReducedPermutationLI([[1,1],[2,2,3,3,4,4]])
    1 1
    2 2 3 3 4 4
    sage: ReducedPermutationLI([['a','a','b','b','c','c'],['d','d']])
    a a b b c c
    d d
    sage: from sage.dynamics.interval_exchanges.reduced import FlippedReducedPermutationIET
    sage: FlippedReducedPermutationIET([[1,2,3],[3,2,1]],flips=[1,2])
    -1 -2  3
     3 -2 -1
    sage: FlippedReducedPermutationIET([['a','b','c'],['b','c','a']],flips='b')
     a -b  c
    -b  c  a
    sage: from sage.dynamics.interval_exchanges.reduced import FlippedReducedPermutationLI
    sage: FlippedReducedPermutationLI([[1,1],[2,2,3,3,4,4]], flips=[1,4])
    -1 -1
     2  2  3  3 -4 -4
    sage: FlippedReducedPermutationLI([['a','a','b','b'],['c','c']],flips='ac')
    -a -a  b  b
    -c -c
    sage: from sage.dynamics.interval_exchanges.reduced import ReducedRauzyDiagram
    sage: p = ReducedPermutationIET([[1,2,3],[3,2,1]])
    sage: d = ReducedRauzyDiagram(p)
"""
#*****************************************************************************
#       Copyright (C) 2008 Vincent Delecroix <20100.delecroix@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from sage.structure.sage_object import SageObject

from copy import copy

from sage.combinat.words.alphabet import Alphabet
from sage.rings.integer import Integer

import time
import sage.dynamics.flat_surfaces.lekz as lekz   # the cython bindings

from template import OrientablePermutationIET, OrientablePermutationLI   # permutations
from template import FlippedPermutationIET, FlippedPermutationLI         # flipped permutations
from template import RauzyDiagram, FlippedRauzyDiagram

from template import interval_conversion, side_conversion


def mean_and_std_dev(l):
    r"""
    Return the mean and standard deviation of the floatting point numbers in
    the list l.

    The implementation is very naive and should not be used for large list
    (>1000) of numbers.

    .. NOTE::
    mean and std are implemented in Sage but are quite buggy!
    """
    from math import sqrt
    m = sum(l) / len(l)
    if len(l) == 1:
        d = 0
    else:
        d = sum((x-m)**2 for x in l) / (len(l)-1)
    return m,sqrt(d)



class ReducedPermutation(SageObject) :
    r"""
    Template for reduced objects.

    .. warning::

        Internal class! Do not use directly!
   """
    def __init__(self,intervals=None,alphabet=None):
        r"""
        INPUT:

        - ``intervals`` - a list of two lists of labels

        - ``alphabet`` - (default: None) alphabet

        TESTS::

            sage: from sage.dynamics.interval_exchanges.reduced import ReducedPermutationIET
            sage: p = ReducedPermutationIET()
            sage: loads(dumps(p)) == p
            True
            sage: p = ReducedPermutationIET([['a','b'],['b','a']])
            sage: loads(dumps(p)) == p
            True
            sage: from sage.dynamics.interval_exchanges.reduced import ReducedPermutationLI
            sage: p = ReducedPermutationLI()
            sage: loads(dumps(p)) == p
            True
            sage: p = ReducedPermutationLI([['a','a'],['b','b']])
            sage: loads(dumps(p)) == p
            True
        """
        self._hash = None

        if intervals is None:
            self._twin = [[],[]]
            self._alphabet = alphabet

        else:
            self._init_twin(intervals)

            if alphabet is None:
                self._init_alphabet(intervals)
            else:
                alphabet = Alphabet(alphabet)
                if alphabet.cardinality() < len(self):
                    raise TypeError("the alphabet is too short")
                self._alphabet = alphabet

    def __getitem__(self,i):
        r"""
        TESTS::

            sage: p = iet.Permutation('a b', 'b a', reduced=True)
            sage: print p[0]
            ['a', 'b']
            sage: print p[1]
            ['b', 'a']
            sage: p.alphabet([0,1])
            sage: print p[0]
            [0, 1]
            sage: print p[1]
            [1, 0]
        """
        return self.list().__getitem__(i)

    def label_double(self, label):
        r"""
        Test if the given label appears two times one the same line

        EXAMPLES:
        
            sage: p1 = iet.Permutation('1 2 3', '3 1 2', reduced=True)
            sage: p1.double()
            False
            sage: p2 = iet.GeneralizedPermutation('g o o', 'd d g', reduced=True)
            sage: p2.double()
            True
        """
        def double_line(i):
            k = 0
            while k < len(self[i]) and self[i][k] <> label:
                k += 1
            for aux in xrange(k + 1, len(self[i])):
                if self[i][aux] == label:
                    return True
            return False

        return double_line(0) or double_line(1)

    
    def lyapunov_exponents_H_plus(self, nb_vectors=None, nb_experiments=100,
                                  nb_iterations=32768, return_speed=False, verbose=False, output_file=None, lengths=None, sigma=None):
        r"""
        Compute the H^+ Lyapunov exponents in  the covering locus.

        It calls the C-library lyap_exp interfaced with Cython. The computation
        might be significantly faster if ``nb_vectors=1`` (or if it is not
        provided but genus is 1).

        INPUT:

        - ``nb_vectors`` -- the number of exponents to compute. The number of
          vectors must not exceed the dimension of the space!

         - ``nb_experiments`` -- the number of experiments to perform. It might
           be around 100 (default value) in order that the estimation of
           confidence interval is accurate enough.

         - ``nb_iterations`` -- the number of iteration of the Rauzy-Zorich
           algorithm to perform for each experiments. The default is 2^15=32768
           which is rather small but provide a good compromise between speed and
           quality of approximation.

        - ``verbose`` -- if ``True`` provide additional informations rather than
          returning only the Lyapunov exponents (i.e. ellapsed time, confidence
          intervals, ...)

        - ``output_file`` -- if provided (as a file object or a string) output
          the additional information in the given file rather than on the
          standard output.

        EXAMPLES::
            sage: R = cyclic_cover_iet(4, [1, 1, 1, 1])
            sage: R.lyapunov_exponents_H_plus()
            [0.9996553085103, 0.0007776980910571506, 0.00022201024035355403]

        """
        n = len(self)

        if nb_vectors is None:
            nb_vectors = self.stratum().genus()

        if output_file is None:
            from sys import stdout
            output_file = stdout
        elif isinstance(output_file, str):
            output_file = open(output_file, "w")

        if sigma == None or sigma == []: sigma = [0]*len(self)        #look at the trivial cover
        if isinstance(sigma, dict):
            sigma = map(lambda x : sigma[self._alphabet.unrank(x)], range(n))
        if isinstance(sigma, list) and isinstance(sigma[0], list):
            sigma = reduce(lambda x,y: x+y, sigma)


        nb_vectors = int(nb_vectors)
        nb_experiments = int(nb_experiments)
        nb_iterations = int(nb_iterations)

        if verbose:
            output_file.write("Stratum : " + str(self.stratum()))
            output_file.write("\n")

        if nb_vectors < 0 :     raise ValueError("the number of vectors must be positive")
        if nb_vectors == 0:     return []
        if nb_experiments <= 0: raise ValueError("the number of experiments must be positive")
        if nb_iterations <= 0 : raise ValueError("the number of iterations must be positive")
        if len(sigma) %n != 0 : raise ValueError("you must give a permutation for each interval")
        
        #Translate our structure to the C structure"
        k = len(self[0])
        def convert((i,j)):
            return(j + i*k)

        gp, twin = range(2*n), range(2*n)

        for i in range(2):
            for j in range(len(self[i])):
                gp[convert((i,j))] = int(self._alphabet.rank(self[i][j]))
                if isinstance(self._twin[i][j], int):
                       twin[convert((i,j))] = int(convert((1-i, self._twin[i][j])))
                else:
                       twin[convert((i,j))] = int(convert(self._twin[i][j]))


        if lengths != None:
            lengths = map(int, lengths)
        sigma = map(int, sigma)

        t0 = time.time()
        res = lekz.lyapunov_exponents_H_plus_cyclic_cover(
            gp, int(k), twin, sigma, int(len(sigma)/n), 
            nb_vectors, nb_experiments, nb_iterations)
        t1 = time.time()

        res_final = []

        m,d = mean_and_std_dev(res[0])
        lexp = m

        if verbose:
            from math import log, floor, sqrt
            output_file.write("sample of %d experiments\n"%nb_experiments)
            output_file.write("%d iterations (~2^%d)\n"%(
                    nb_iterations,
                    floor(log(nb_iterations) / log(2))))
            output_file.write("ellapsed time %s\n"%time.strftime("%H:%M:%S",time.gmtime(t1-t0)))
            output_file.write("Lexp Rauzy-Zorich: %f (std. dev. = %f, conf. rad. 0.01 = %f)\n"%(
                    m,d, 2.576*d/sqrt(nb_experiments)))
        for i in xrange(1,nb_vectors+1):
            m,d = mean_and_std_dev(res[i])
            if verbose:
                output_file.write("theta%d           : %f (std. dev. = %f, conf. rad. 0.01 = %f)\n"%(
                    i,m,d, 2.576*d/sqrt(nb_experiments)))
            res_final.append(m)

        if return_speed: return (lexp, res_final)
        else: return res_final




def ReducedPermutationsIET_iterator(
    nintervals=None,
    irreducible=True,
    alphabet=None):
    r"""
    Returns an iterator over reduced permutations

    INPUT:

    - ``nintervals`` - integer or None

    - ``irreducible`` - boolean

    - ``alphabet`` - something that should be converted to an alphabet
      of at least nintervals letters

    TESTS::

        sage: for p in iet.Permutations_iterator(3,reduced=True,alphabet="abc"):
        ...    print p  #indirect doctest
        a b c
        b c a
        a b c
        c a b
        a b c
        c b a
    """
    from itertools import imap,ifilter
    from sage.combinat.permutation import Permutations

    if irreducible is False:
        if nintervals is None:
            raise NotImplementedError, "choose a number of intervals"
        else:
            assert(isinstance(nintervals,(int,Integer)))
            assert(nintervals > 0)

            a0 = range(1,nintervals+1)
            f = lambda x: ReducedPermutationIET([a0,list(x)],
                alphabet=alphabet)
            return imap(f, Permutations(nintervals))
    else:
        return ifilter(lambda x: x.is_irreducible(),
        ReducedPermutationsIET_iterator(nintervals,False,alphabet))

class ReducedPermutationIET(ReducedPermutation, OrientablePermutationIET):
    """
    Reduced permutation from iet

    Permutation from iet without numerotation of intervals. For initialization,
    you should use GeneralizedPermutation which is the class factory for all
    permutation types.

    EXAMPLES:

    Equality testing (no equality of letters but just of ordering)::

        sage: p = iet.Permutation('a b c', 'c b a', reduced = True)
        sage: q = iet.Permutation('p q r', 'r q p', reduced = True)
        sage: p == q
        True

    Reducibility testing::

        sage: p = iet.Permutation('a b c', 'c b a', reduced = True)
        sage: p.is_irreducible()
        True

    ::

        sage: q = iet.Permutation('a b c d', 'b a d c', reduced = True)
        sage: q.is_irreducible()
        False


    Rauzy movability and Rauzy move::

        sage: p = iet.Permutation('a b c', 'c b a', reduced = True)
        sage: p.has_rauzy_move(1)
        True
        sage: print p.rauzy_move(1)
        a b c
        b c a

    Rauzy diagrams::

        sage: p = iet.Permutation('a b c d', 'd a b c')
        sage: p_red = iet.Permutation('a b c d', 'd a b c', reduced = True)
        sage: d = p.rauzy_diagram()
        sage: d_red = p_red.rauzy_diagram()
        sage: p.rauzy_move(0) in d
        True
        sage: print d.cardinality(), d_red.cardinality()
        12 6
    """
    def list(self):
        r"""
        Returns a list of two list that represents the permutation.

        EXAMPLES::

            sage: p = iet.GeneralizedPermutation('a b','b a',reduced=True)
            sage: p.list() == [['a', 'b'], ['b', 'a']]
            True
            sage: p = iet.GeneralizedPermutation('a a','b b',reduced=True)
            sage: p.list() == [['a', 'a'], ['b', 'b']]
            True
        """
        return [
            map(lambda x: self._alphabet.unrank(x), range(len(self._twin[0]))),
            map(lambda x: self._alphabet.unrank(x), self._twin[1])]

    def __hash__(self):
        r"""
        Returns a hash value (does not depends of the alphabet).

        TESTS::
            sage: p = iet.Permutation([1,2],[1,2], reduced=True)
            sage: q = iet.Permutation([1,2],[2,1], reduced=True)
            sage: r = iet.Permutation([2,1],[1,2], reduced=True)
            sage: hash(p) == hash(q)
            False
            sage: hash(q) == hash(r)
            True
        """
        if self._hash is None:
            self._hash = hash(tuple(self._twin[0]))
        return self._hash

    def __eq__(self,other):
        r"""
        Tests equality

        TESTS::

            sage: p1 = iet.Permutation('a b','a b',reduced=True,alphabet='ab')
            sage: p2 = iet.Permutation('a b','a b',reduced=True,alphabet='ba')
            sage: q1 = iet.Permutation('a b','b a',reduced=True,alphabet='ab')
            sage: q2 = iet.Permutation('a b','b a',reduced=True,alphabet='ba')
            sage: p1 == p2 and p2 == p1 and q1 == q2 and q2 == q1
            True
            sage: p1 == q1 or p2 == q1 or q1 == p1 or q1 == p2
            False
        """
        return self._twin == other._twin

    def __ne__(self, other):
        r"""
        Tests difference

        TESTS::

            sage: p1 = iet.Permutation('a b','a b',reduced=True,alphabet='ab')
            sage: p2 = iet.Permutation('a b','a b',reduced=True,alphabet='ba')
            sage: q1 = iet.Permutation('a b','b a',reduced=True,alphabet='ab')
            sage: q2 = iet.Permutation('a b','b a',reduced=True,alphabet='ba')
            sage: p1 != p2 or p2 != p1 or q1 != q2 or q2 != q1
            False
            sage: p1 != q1 and p2 != q1 and q1 != p1 and q1 != p2
            True
        """
        return self._twin != other._twin

    def __cmp__(self, other):
        r"""
        Defines a natural lexicographic order.

        TESTS::

            sage: p = iet.GeneralizedPermutation('a b','a b',reduced=True)
            sage: q = copy(p)
            sage: q.alphabet([0,1])
            sage: p == q
            True
            sage: p0 = iet.GeneralizedPermutation('a b', 'a b', reduced=True)
            sage: p1 = iet.GeneralizedPermutation('a b', 'b a', reduced=True)
            sage: p0 < p1 and p1 > p0
            True
            sage: q0 = iet.GeneralizedPermutation('a b c','a b c',reduced=True)
            sage: q1 = iet.GeneralizedPermutation('a b c','a c b',reduced=True)
            sage: q2 = iet.GeneralizedPermutation('a b c','b a c',reduced=True)
            sage: q3 = iet.GeneralizedPermutation('a b c','b c a',reduced=True)
            sage: q4 = iet.GeneralizedPermutation('a b c','c a b',reduced=True)
            sage: q5 = iet.GeneralizedPermutation('a b c','c b a',reduced=True)
            sage: p0 < q0 and q0 > p0 and p1 < q0 and q0 > p1
            True
            sage: q0 < q1 and q1 > q0
            True
            sage: q1 < q2 and q2 > q1
            True
            sage: q2 < q3 and q3 > q2
            True
            sage: q3 < q4 and q4 > q3
            True
            sage: q4 < q5 and q5 > q4
            True
        """
        if type(self) != type(other):
            raise ValueError, "Permutations must be of the same type"

        if len(self) > len(other):
            return 1
        elif len(self) < len(other):
            return -1

        n = len(self)
        j = 0
        while (j < n and self._twin[1][j] == other._twin[1][j]):
            j += 1

        if j != n:
            if self._twin[1][j] > other._twin[1][j]: return 1
            else: return -1

        return 0

    def rauzy_move_relabel(self, winner, side='right'):
        r"""
        Returns the relabelization obtained from this move.

        EXAMPLE::

            sage: p = iet.Permutation('a b c d','d c b a')
            sage: q = p.reduced()
            sage: p_t = p.rauzy_move('t')
            sage: q_t = q.rauzy_move('t')
            sage: s_t = q.rauzy_move_relabel('t')
            sage: print s_t
            a->a, b->b, c->c, d->d
            sage: map(s_t, p_t[0]) == map(Word, q_t[0])
            True
            sage: map(s_t, p_t[1]) == map(Word, q_t[1])
            True
            sage: p_b = p.rauzy_move('b')
            sage: q_b = q.rauzy_move('b')
            sage: s_b = q.rauzy_move_relabel('b')
            sage: print s_b
            a->a, b->d, c->b, d->c
            sage: map(s_b, q_b[0]) == map(Word, p_b[0])
            True
            sage: map(s_b, q_b[1]) == map(Word, p_b[1])
            True
        """
        from sage.dynamics.interval_exchanges.labelled import LabelledPermutationIET
        from sage.combinat.words.morphism import WordMorphism

        winner = interval_conversion(winner)
        side = side_conversion(side)

        p = LabelledPermutationIET(self.list())

        l0_q = p.rauzy_move(winner, side).list()[0]

        d = dict([(self._alphabet[i],l0_q[i]) for i in range(len(self))])

        return WordMorphism(d)

    def rauzy_diagram(self, **kargs):
        r"""
        Returns the associated Rauzy diagram.

        OUTPUT:

        A Rauzy diagram

        EXAMPLES:

        ::

            sage: p = iet.Permutation('a b c d', 'd a b c',reduced=True)
            sage: d = p.rauzy_diagram()
            sage: p.rauzy_move(0) in d
            True
            sage: p.rauzy_move(1) in d
            True

        For more information, try help RauzyDiagram
        """
        return ReducedRauzyDiagram(self, **kargs)

class ReducedPermutationLI(ReducedPermutation, OrientablePermutationLI):
    r"""
    Reduced quadratic (or generalized) permutation.

    EXAMPLES:

    Reducibility testing::

        sage: p = iet.GeneralizedPermutation('a b b', 'c c a', reduced = True)
        sage: p.is_irreducible()
        True

    ::

        sage: p = iet.GeneralizedPermutation('a b c a', 'b d d c', reduced = True)
        sage: p.is_irreducible()
        False
        sage: test, decomposition = p.is_irreducible(return_decomposition = True)
        sage: test
        False
        sage: decomposition
        (['a'], ['c', 'a'], [], ['c'])

    Rauzy movavability and Rauzy move::

        sage: p = iet.GeneralizedPermutation('a b b', 'c c a', reduced = True)
        sage: p.has_rauzy_move(0)
        True
        sage: p.rauzy_move(0)
        a a b b
        c c
        sage: p.rauzy_move(0).has_rauzy_move(0)
        False
        sage: p.rauzy_move(1)
        a b b
        c c a

    Rauzy diagrams::

        sage: p_red = iet.GeneralizedPermutation('a b b', 'c c a', reduced = True)
        sage: d_red = p_red.rauzy_diagram()
        sage: d_red.cardinality()
        4
    """
    def list(self) :
        r"""
        The permutations as a list of two lists.

        EXAMPLES::

            sage: p = iet.GeneralizedPermutation('a b b', 'c c a', reduced = True)
            sage: list(p)
            [['a', 'b', 'b'], ['c', 'c', 'a']]
        """
        i_a = 0
        l = [[False]*len(self._twin[0]),[False]*len(self._twin[1])]
        # False means empty here
        for i in range(2) :
            for j in range(len(l[i])) :
                if  l[i][j] is False :
                    l[i][j] = self._alphabet[i_a]
                    l[self._twin[i][j][0]][self._twin[i][j][1]] = self._alphabet[i_a]
                    i_a += 1
        return l

    def __eq__(self, other) :
        r"""
        Tests equality.

        Two reduced permutations are equal if they have the same order of
        apparition of intervals. Non necessarily the same alphabet.

        TESTS::

            sage: p = iet.GeneralizedPermutation('a b b', 'c c a', reduced = True)
            sage: q = iet.GeneralizedPermutation('b a a', 'c c b', reduced = True)
            sage: r = iet.GeneralizedPermutation('t s s', 'w w t', reduced = True)
            sage: p == q
            True
            sage: p == r
            True
        """
        return type(self) == type(other) and self._twin == other._twin

    def __ne__(self, other) :
        """
        Tests difference.

        TESTS::
            sage: p = iet.GeneralizedPermutation('a b b', 'c c a', reduced = True)
            sage: q = iet.GeneralizedPermutation('b b a', 'c c a', reduced = True)
            sage: r = iet.GeneralizedPermutation('i j j', 'k k i', reduced = True)
            sage: p != q
            True
            sage: p != r
            False
        """
        return type(self) != type(other) or (self._twin != other._twin)

    def rauzy_diagram(self, **kargs):
        r"""
        Returns the associated Rauzy diagram.

        The Rauzy diagram of a permutation corresponds to all permutations
        that we could obtain from this one by Rauzy move. The set obtained
        is a labelled Graph. The label of vertices being 0 or 1 depending
        on the type.

        OUTPUT:

        Rauzy diagram -- the graph of permutations obtained by rauzy induction

        EXAMPLES::

            sage: p = iet.Permutation('a b c d', 'd a b c')
            sage: d = p.rauzy_diagram()
        """
        return ReducedRauzyDiagram(self, **kargs)

def labelize_flip(couple):
    r"""
    Returns a string from a 2-uple couple of the form (name, flip).

    TESTS::

        sage: from sage.dynamics.interval_exchanges.reduced import labelize_flip
        sage: labelize_flip((4,1))
        ' 4'
        sage: labelize_flip(('a',-1))
        '-a'
    """
    if couple[1] == -1: return '-' + str(couple[0])
    return ' ' + str(couple[0])


class FlippedReducedPermutation(ReducedPermutation):
    r"""
    Flipped Reduced Permutation.

    .. warning::

        Internal class! Do not use directly!

    INPUT:

    - ``intervals`` - a list of two lists

    - ``flips`` - the flipped letters

    - ``alphabet`` - an alphabet
    """
    def __init__(self, intervals=None, flips=None, alphabet=None):
        r"""
        TESTS::

            sage: p = iet.Permutation('a b','b a',reduced=True,flips='a')
            sage: p == loads(dumps(p))
            True
            sage: p = iet.Permutation('a b','b a',reduced=True,flips='b')
            sage: p == loads(dumps(p))
            True
            sage: p = iet.Permutation('a b','b a',reduced=True,flips='ab')
            sage: p == loads(dumps(p))
            True
            sage: p = iet.GeneralizedPermutation('a a','b b',reduced=True,flips='a')
            sage: p == loads(dumps(p))
            True
            sage: p = iet.GeneralizedPermutation('a a','b b',reduced=True,flips='b')
            sage: p == loads(dumps(p))
            True
            sage: p = iet.GeneralizedPermutation('a a','b b',reduced=True,flips='ab')
            sage: p == loads(dumps(p))
            True
        """
        self._hash = None

        if intervals is None:
            self._twin = [[],[]]
            self._flips = [[],[]]
            self._alphabet = None

        else:
            if flips is None: flips = []

            if alphabet is None : self._init_alphabet(intervals)
            else : self._alphabet = Alphabet(alphabet)

            self._init_twin(intervals)
            self._init_flips(intervals, flips)

            self._hash = None



class FlippedReducedPermutationIET(
    FlippedReducedPermutation,
    FlippedPermutationIET,
    ReducedPermutationIET):
    r"""
    Flipped Reduced Permutation from iet

    EXAMPLES

    ::

        sage: p = iet.Permutation('a b c', 'c b a', flips=['a'], reduced=True)
        sage: p.rauzy_move(1)
        -a -b  c
        -a  c -b

    TESTS::

        sage: p = iet.Permutation('a b','b a',flips=['a'])
        sage: p == loads(dumps(p))
        True
    """
    def __eq__(self,other):
        r"""
        TESTS::

            sage: p = iet.Permutation('a b','a b',reduced=True,flips='a')
            sage: q = copy(p)
            sage: q.alphabet([0,1])
            sage: p == q
            True
            sage: l0 = ['a b','a b']
            sage: l1 = ['a b','b a']
            sage: l2 = ['b a', 'a b']
            sage: p0 = iet.Permutation(l0, reduced=True, flips='ab')
            sage: p1 = iet.Permutation(l1, reduced=True, flips='a')
            sage: p2 = iet.Permutation(l2, reduced=True, flips='b')
            sage: p3 = iet.Permutation(l1, reduced=True, flips='ab')
            sage: p4 = iet.Permutation(l2 ,reduced=True,flips='ab')
            sage: p0 == p1 or p0 == p2 or p0 == p3 or p0 == p4
            False
            sage: p1 == p2 and p3 == p4
            True
            sage: p1 == p3 or p1 == p4 or p2 == p3 or p2 == p4
            False
        """
        return (self._twin == other._twin) and (self._flips == other._flips)

    def __ne__(self, other):
        r"""
        TESTS::

            sage: p = iet.Permutation('a b','a b',reduced=True,flips='a')
            sage: q = copy(p)
            sage: q.alphabet([0,1])
            sage: p != q
            False
            sage: l0 = ['a b','a b']
            sage: l1 = ['a b','b a']
            sage: l2 = ['b a', 'a b']
            sage: p0 = iet.Permutation(l0, reduced=True, flips='ab')
            sage: p1 = iet.Permutation(l1, reduced=True, flips='a')
            sage: p2 = iet.Permutation(l2, reduced=True, flips='b')
            sage: p3 = iet.Permutation(l1, reduced=True, flips='ab')
            sage: p4 = iet.Permutation(l2 ,reduced=True,flips='ab')
            sage: p0 != p1 and p0 != p2 and p0 != p3 and p0 != p4
            True
            sage: p1 != p2 or p3 != p4
            False
            sage: p1 != p3 and p1 != p4 and p2 != p3 and p2 != p4
            True
        """
        return (self._twin != other._twin) or (self._flips != other._flips)

    def __cmp__(self, other):
        r"""
        Defines a natural lexicographic order.

        TESTS::

            sage: p = iet.Permutation('a b','a b',reduced=True,flips='a')
            sage: q = copy(p)
            sage: q.alphabet([0,1])
            sage: p == q
            True
            sage: l0 = ['a b','a b']
            sage: l1 = ['a b','b a']
            sage: p1 = iet.Permutation(l1,reduced=True, flips='a')
            sage: p2 = iet.Permutation(l1,reduced=True, flips='b')
            sage: p3 = iet.Permutation(l1,reduced=True, flips='ab')
            sage: p2 > p3 and p3 < p2
            True
            sage: p1 > p2 and p2 < p1
            True
            sage: p1 > p3 and p3 < p1
            True
            sage: q1 = iet.Permutation(l0, reduced=True, flips='a')
            sage: q2 = iet.Permutation(l0, reduced=True, flips='b')
            sage: q3 = iet.Permutation(l0, reduced=True, flips='ab')
            sage: q2 > q1 and q2 > q3 and q1 < q2 and q3 < q2
            True
            sage: q1 > q3
            True
            sage: q3 < q1
            True
            sage: r = iet.Permutation('a b c','a b c', reduced=True, flips='a')
            sage: r > p1 and r > p2 and r > p3
            True
            sage: p1 < r and p2 < r and p3 < r
            True
        """
        if type(self) != type(other):
            return -1

        if len(self) > len(other):
            return 1
        elif len(self) < len(other):
            return -1

        n = len(self)
        j = 0
        while (j < n and
            self._twin[1][j] == other._twin[1][j] and
            self._flips[1][j] == other._flips[1][j]):
            j += 1

        if j != n:
            if self._twin[1][j] > other._twin[1][j]: return 1
            elif self._twin[1][j] < other._twin[1][j]: return -1
            else: return self._flips[1][j]

        return 0

    def list(self, flips=False):
        r"""
        Returns a list representation of self.

        INPUT:

        - ``flips`` - boolean (default: False) if True the output contains
           2-uple of (label, flip)

        EXAMPLES:

        ::
            sage: p = iet.Permutation('a b','b a',reduced=True,flips='b')
            sage: p.list(flips=True)
            [[('a', 1), ('b', -1)], [('b', -1), ('a', 1)]]
            sage: p.list(flips=False)
            [['a', 'b'], ['b', 'a']]
            sage: p.alphabet([0,1])
            sage: p.list(flips=True)
            [[(0, 1), (1, -1)], [(1, -1), (0, 1)]]
            sage: p.list(flips=False)
            [[0, 1], [1, 0]]

        One can recover the initial permutation from this list::

            sage: p = iet.Permutation('a b','b a',reduced=True,flips='a')
            sage: iet.Permutation(p.list(), flips=p.flips(), reduced=True) == p
            True
        """
        if flips:
            a0 = zip(map(self.alphabet().unrank, range(0,len(self))), self._flips[0])
            a1 = zip(map(self.alphabet().unrank, self._twin[1]), self._flips[1])

        else:
            a0 = map(self.alphabet().unrank, range(0,len(self)))
            a1 = map(self.alphabet().unrank, self._twin[1])

        return [a0,a1]

    def rauzy_diagram(self, **kargs):
        r"""
        Returns the associated Rauzy diagram.

        EXAMPLES::

            sage: p = iet.Permutation('a b','b a',reduced=True,flips='a')
            sage: r = p.rauzy_diagram()
            sage: p in r
            True
        """
        return FlippedReducedRauzyDiagram(self, **kargs)

class FlippedReducedPermutationLI(
    FlippedReducedPermutation,
    FlippedPermutationLI,
    ReducedPermutationLI):
    r"""
    Flipped Reduced Permutation from li

    EXAMPLES:

    Creation using the GeneralizedPermutation function::

        sage: p = iet.GeneralizedPermutation('a a b', 'b c c', reduced=True, flips='a')
    """
    def list(self, flips=False):
        r"""
        Returns a list representation of self.

        INPUT:

        - ``flips`` - boolean (default: False) return the list with flips

        EXAMPLES:

        ::

            sage: p = iet.GeneralizedPermutation('a a','b b',reduced=True,flips='a')
            sage: p.list(flips=True)
            [[('a', -1), ('a', -1)], [('b', 1), ('b', 1)]]
            sage: p.list(flips=False)
            [['a', 'a'], ['b', 'b']]

            sage: p = iet.GeneralizedPermutation('a a b','b c c',reduced=True,flips='abc')
            sage: p.list(flips=True)
            [[('a', -1), ('a', -1), ('b', -1)], [('b', -1), ('c', -1), ('c', -1)]]
            sage: p.list(flips=False)
            [['a', 'a', 'b'], ['b', 'c', 'c']]

        one can rebuild the permutation from the list::

            sage: p = iet.GeneralizedPermutation('a a b','b c c',flips='a',reduced=True)
            sage: iet.GeneralizedPermutation(p.list(),flips=p.flips(),reduced=True) == p
            True
        """
        i_a = 0
        l = [[False]*len(self._twin[0]),[False]*len(self._twin[1])]

        if flips:
            for i in range(2):  # False means empty here
                for j in range(len(l[i])):
                   if  l[i][j] is False:
                        l[i][j] = (self._alphabet.unrank(i_a), self._flips[i][j])
                        l[self._twin[i][j][0]][self._twin[i][j][1]] = l[i][j]
                        i_a += 1

        else:
            for i in range(2):  # False means empty here
                for j in range(len(l[i])):
                   if  l[i][j] is False:
                        l[i][j] = self._alphabet.unrank(i_a)
                        l[self._twin[i][j][0]][self._twin[i][j][1]] = l[i][j]
                        i_a += 1
        return l

    def __eq__(self, other) :
        r"""
        TESTS::

            sage: a0 = [0,0,1]
            sage: a1 = [1,2,2]
            sage: p = iet.GeneralizedPermutation(a0,a1,reduced=True,flips=[0])
            sage: q = copy(p)
            sage: q.alphabet("abc")
            sage: p == q
            True
            sage: b0 = [1,0,0]
            sage: b1 = [2,2,1]
            sage: r = iet.GeneralizedPermutation(b0,b1,reduced=True,flips=[0])
            sage: p == r or q == r
            False
        """
        return (type(self) == type(other) and
            self._twin == other._twin and
            self._flips == other._flips)

    def __ne__(self, other) :
        r"""
        TESTS::

            sage: a0 = [0,0,1]
            sage: a1 = [1,2,2]
            sage: p = iet.GeneralizedPermutation(a0,a1,reduced=True,flips=[0])
            sage: q = copy(p)
            sage: q.alphabet("abc")
            sage: p != q
            False
            sage: b0 = [1,0,0]
            sage: b1 = [2,2,1]
            sage: r = iet.GeneralizedPermutation(b0,b1,reduced=True,flips=[0])
            sage: p != r and q != r
            True
        """
        return (type(self) != type(other) or
            self._twin != other._twin or
            self._flips != other._flips)

    def rauzy_diagram(self, **kargs):
        r"""
        Returns the associated Rauzy diagram.

        For more explanation and a list of arguments try help(iet.RauzyDiagram)

        EXAMPLES::

            sage: p = iet.GeneralizedPermutation('a a b','c c b',reduced=True)
            sage: r = p.rauzy_diagram()
            sage: p in r
            True
        """
        return FlippedReducedRauzyDiagram(self, **kargs)

class ReducedRauzyDiagram(RauzyDiagram):
    r"""
    Rauzy diagram of reduced permutations
    """
    def _permutation_to_vertex(self, p):
        r"""
        The necessary data to store the permutation.

        TESTS::


            sage: p = iet.Permutation('a b c','c b a',reduced=True)   #indirect doctest
            sage: r = p.rauzy_diagram()
            sage: p in r
            True
        """
        return (tuple(p._twin[0]), tuple(p._twin[1]))

    def _set_element(self, data=None):
        r"""
        Sets self._element with data.

        TESTS::

            sage: p = iet.Permutation('a b c','c b a',reduced=True)
            sage: r = p.rauzy_diagram()
            sage: p in r   #indirect doctest
            True
        """
        self._element._twin = [list(data[0]), list(data[1])]

class FlippedReducedRauzyDiagram(FlippedRauzyDiagram, ReducedRauzyDiagram):
    r"""
    Rauzy diagram of flipped reduced permutations.
    """
    def _permutation_to_vertex(self, p):
        r"""
        TESTS::

            sage: p = iet.GeneralizedPermutation('a b b','c c a',flips='a',reduced=True)
            sage: r = p.rauzy_diagram()
            sage: p in r   #indirect doctest
            True
        """
        return ((tuple(p._twin[0]), tuple(p._twin[1])),
                (tuple(p._flips[0]), tuple(p._flips[1])))

    def _set_element(self, data=None):
        r"""
        Sets self._element with data.
        TESTS::

            sage: r = iet.RauzyDiagram('a b c','c b a',flips='b',reduced=True)   #indirect doctest
        """
        self._element._twin = [list(data[0][0]), list(data[0][1])]
        self._element._flips = [list(data[1][0]), list(data[1][1])]

