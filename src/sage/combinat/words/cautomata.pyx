# coding=utf8
"""
Fast automaton of Finite state machines using C
FastAutomaton for determinist automata and NFastAutomaton for non determinist


AUTHORS:

- Paul Mercat (2013) initial version
- Dominique Benielli (2018)
  AMU Aix-Marseille Universite - Integration in SageMath

REFERENCES:

.. [Hopcroft] "Around Hopcroft’s Algorithm"  Manuel of BACLET and
    Claire PAGETTI.

"""

#*****************************************************************************
#       Copyright (C) 2014 Paul Mercat <mercatp@icloud.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#    This code is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    General Public License for more details.
#
#  The full text of the GPL is available at:
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************
from __future__ import print_function
from libc.stdlib cimport malloc, free

cimport sage.combinat.words.cautomata

from cysignals.signals cimport sig_on, sig_off, sig_check

#ctypedef Automate Automaton

cdef extern from "automataC.h":
    ctypedef Automate Automaton
    ctypedef NAutomate NAutomaton
    cdef cppclass Dict:
        int* e
        int n
    cdef cppclass InvertDict:
        Dict* d
        int n

    bool DotExists ()
    #    Automaton NewAutomaton (int n, int na)
    #    void FreeAutomaton (Automaton *a)
    int hashAutomaton(Automaton a)
    void FreeNAutomaton(NAutomaton *a)
    Automaton CopyAutomaton(Automaton a, int nalloc, int naalloc)
    Automaton PieceAutomaton(Automaton a, int *w, int n, int e)
    void init(Automaton *a)
    void printAutomaton(Automaton a)
    void plotDot(const char *file, Automaton a, const char **labels, const char *graph_name, double sx, double sy, const char **vlabels, bool verb, bool run_dot)
    void NplotDot (const char *file, NAutomaton a, const char **labels, const char *graph_name, double sx, double sy, bool run_dot)
    Automaton Product(Automaton a1, Automaton a2, Dict d, bool verb)
    Automaton Determinise(Automaton a, Dict d, bool noempty, bool onlyfinals, bool nof, bool verb)
    Automaton DeterminiseN(NAutomaton a, bool puits, int verb)
    NAutomaton Concat(Automaton a, Automaton b, bool verb)
    NAutomaton CopyN(Automaton a, bool verb)
    void AddEdgeN(NAutomaton *a, int e, int f, int l)
    void AddPathN(NAutomaton *a, int e, int f, int *l, int len, bool verb)
    NAutomaton Proj(Automaton a, Dict d, bool verb)
    void ZeroComplete(Automaton *a, int l0, bool verb)
    Automaton ZeroComplete2(Automaton *a, int l0, bool etat_puits, bool verb)
    Automaton ZeroInv(Automaton *a, int l0)
    Automaton emonde_inf(Automaton a, bool verb)
    Automaton emonde(Automaton a, bool verb)
    Automaton emondeI(Automaton a, bool verb)
    void AccCoAcc(Automaton *a, int *coa)
    void CoAcc(Automaton *a, int *coa)
    bool equalsAutomaton(Automaton a1, Automaton a2)
    Dict NewDict(int n)
    void FreeDict(Dict *d)
    void printDict(Dict d)
    InvertDict NewInvertDict(int n)
    void FreeInvertDict(InvertDict id)
    void printInvertDict(InvertDict id)
    Automaton Duplicate(Automaton a, InvertDict id, int na2, bool verb)
    Automaton TransposeDet(Automaton a)
    NAutomaton Transpose(Automaton a)
    int StronglyConnectedComponents(Automaton a, int *res)
    Automaton SubAutomaton(Automaton a, Dict d, bool verb)
    Automaton Permut(Automaton a, int *l, int na, bool verb)
    void PermutOP(Automaton a, int *l, int na, bool verb)
    Automaton Minimise(Automaton a, bool verb)
    void DeleteVertexOP(Automaton* a, int e)
    Automaton DeleteVertex(Automaton a, int e)
    bool equalsLangages(Automaton *a1, Automaton *a2, Dict a1toa2, bool minimized, bool emonded, bool verb)
    bool Intersect(Automaton a1, Automaton a2, bool verb)
    bool Included(Automaton a1, Automaton a2, bool emonded, bool verb)
    # bool intersectLangage (Automaton *a1, Automaton *a2, Dict a1toa2, bool emonded, bool verb)
    bool emptyLangage(Automaton a)
    void AddEtat(Automaton *a, bool final)
    bool IsCompleteAutomaton(Automaton a)
    bool CompleteAutomaton(Automaton *a)
    Automaton BiggerAlphabet(Automaton a, Dict d, int nna) #copy the automaton with a new bigger alphabet
    bool findWord(Automaton a, Dict *w, bool verb)
    bool shortestWord(Automaton a, Dict *w, int i, int f, bool verb)
    bool shortestWords(Automaton a, Dict *w, int i, bool verb)
    bool rec_word(Automaton a, Dict d)
    void Test()

# dictionnaire numérotant l'alphabet projeté
cdef imagDict(dict d, list A, list A2=[]):
    """
    Dictionary which is numbering projected alphabet
    """
    d1 = {}
    i = 0
    for a in A:
        if d.has_key(a):
            if not d1.has_key(d[a]):
                d1[d[a]] = i
                A2.append(d[a])
                i += 1
    return d1

# dictionnaire numérotant le nouvel alphabet
cdef imagDict2(dict d, list A, list A2=[]):
    """
    Dictionary which is numbering a new alphabet
    """
    # print("d=%s, A=%s"%(d,A))
    d1 = {}
    i = 0
    for a in A:
        if d.has_key(a):
            for v in d[a]:
                if not d1.has_key(v):
                    d1[v] = i
                    A2.append(v)
                    i += 1
    return d1

cdef Dict getDict(dict d, list A, dict d1=None):
    A = list(A)
    cdef Dict r
    r = NewDict(len(A))
    cdef int i
    if d1 is None:
        d1 = imagDict(d, A)
    # print d1
    for i in range(r.n):
        if d.has_key(A[i]):
            r.e[i] = d1[d[A[i]]]
        else:
            r.e[i] = -1
    return r

cdef Dict list_to_Dict(list l):
    cdef Dict d = NewDict(len(l))
    cdef int i
    for i in range(len(l)):
        d.e[i] = l[i]
    return d

cdef InvertDict getDict2(dict d, list A, dict d1=None):
    A = list(A)
    cdef InvertDict r
    r = NewInvertDict(len(A))
    cdef int i
    if d1 is None:
        d1 = imagDict2(d, A)
    # print(d1)
    for i in range(r.n):
        if d.has_key(A[i]):
            r.d[i] = NewDict(len(d[A[i]]))
            for j in range(r.d[i].n):
                r.d[i].e[j] = d1[d[A[i]][j]]
        else:
            r.d[i].n = 0
    return r

# dictionnaire numérotant l'alphabet projeté
cdef imagProductDict(dict d, list A1, list A2, list Av=[]):
    """
    Dictionary which is numbering the prjeted alphabet
    """
    dv = {}
    i = 0
    for a1 in A1:
        for a2 in A2:
            if d.has_key((a1,a2)):
                if not dv.has_key(d[(a1,a2)]):
                    dv[d[(a1, a2)]] = i
                    Av.append(d[(a1, a2)])
                    i += 1
    return dv

cdef Dict getProductDict(dict d, list A1, list A2, dict dv=None, verb=True):
    cdef Dict r
    d1 = {}
    d2 = {}
    cdef int i, n1, n2
    n1 = len(A1)
    for i in range(n1):
        d1[A1[i]] = i
    if verb:
        print(d1)
    n2 = len(A2)
    for i in range(n2):
        d2[A2[i]] = i
    if verb:
        print(d2)
    if dv is None:
        dv = imagProductDict(d, A1, A2)
    r = NewDict(n1*n2)
    Keys = d.keys()
    if verb:
        print("Keys=%s" % Keys)
    for (a1, a2) in Keys:
        if d1.has_key(a1) and d2.has_key(a2):
            r.e[d1[a1]+d2[a2]*n1] = dv[d[(a1, a2)]]
    return r


# def TestAutomaton(a):
#     """
#     Test automaton print vertices and alphabet
# 
#     INPUT:
# 
#     - ``a`` automaton to test
# 
#     EXAMPLES::
# 
#         sage: a = DiGraph({0: [1,2,3], 1: [0,2], 2: [3], 3: [4], 4: [0,5], 5: [1]})
#         sage: fa = FastAutomaton(a)
#         ['(0,3)', '(2,3)', '(0,2)', '(1,2)', '(0,1)', '(4,5)', '(1,0)', '(4,0)', '(3,4)', '(5,1)']
#         sage: TestAutomaton(fa)
# 
#     """
#     cdef Automaton r
#     # d = {}
#     # da = {}
#     r = getAutomaton(a)  # , d, da)
#     printAutomaton(r)
#     # print d, da, a.vertices(),
#     print( a.vertices(), list(a.Alphabet))


# def TestProduct(a1, a2, di):
#     """
#     Test and print the product of automaton
# 
#     INPUT:
# 
#     - ``a1`` first automaton term of product
# 
#     - ``a2`` second automaton term of product
# 
#     - ``di`` alphabet dictionnary
# 
#     """
#     cdef Automaton a, b, c
#     a = getAutomaton(a1)
#     b = getAutomaton(a2)
#     printAutomaton(a)
#     print(a1.vertices(), a1.Alphabet)
#     printAutomaton(b)
#     print(a2.vertices(), a2.Alphabet)
#     cdef Dict d
#     d = getProductDict(di, list(a1.Alphabet), list(a2.Alphabet))
#     print("product dictionnary :")  # "dictionnaire du produit :"
#     printDict(d)
#     c = Product(a, b, d, False)
#     print("result :")  # "résultat :"
#     printAutomaton(c)

#def TestDeterminise (a, d, noempty=True, verb=True):
#    cdef Dict di = getDict(d, a.Alphabet)
#    cdef Automaton au = getAutomaton(a)
#    if verb:
#        printDict(di)
#    if verb:
#        printAutomaton(au)
#    cdef Automaton r = Determinise(au, di, noempty, verb)
#    printAutomaton(r)

#def TestDeterminiseEmonde (a, d, noempty=True, verb=True):
#    cdef Dict di = getDict(d, a.Alphabet)
#    cdef Automaton au = getAutomaton(a)
#    if verb:
#        printDict(di)
#    if verb:
#        printAutomaton(au)
#    cdef Automaton r = Determinise(au, di, noempty, verb)
#    print("Avant émondation :"
#    printAutomaton(r)
#    cdef Automaton r2 = emonde_inf(r)
#    print("Après émondation :"
#    printAutomaton(r2)
#    if equalsAutomaton(r, r2):
#        print("equals !"
#    else:
#        print("differents !"


# def TestEmonde(a, noempty=True, verb=True):
#     cdef Automaton au = getAutomaton(a)
#     if verb:
#         print("bebore mondation :")  # Avant émondation :"
#         printAutomaton(au)
#     cdef Automaton r = emonde_inf(au, verb)
#     if verb:
#         print("After montation  :")
#         printAutomaton(r)
#     if equalsAutomaton(r, au):
#         print("equal !")
#     else:
#         print("different !")
#     return AutomatonGet(r)


cdef Automaton getAutomaton(a, initial=None, F=None, A=None):
    d = {}
    da = {}
    if F is None:
        if not hasattr(a, 'F'):
            F = a.vertices()
        else:
            F = a.F
    cdef Automaton r

    if A is None:
        A = list(a.Alphabet)
    V = list(a.vertices())
    cdef int n = len(V)
    cdef int na = len(A)

    sig_on()
    r = NewAutomaton(n, na)
    init(&r)
    sig_off()
    for i in range(na):
        da[A[i]] = i
    for i in range(n):
        r.e[i].final = 0
        d[V[i]] = i
    for v in F:
        if not d.has_key(v):
            sig_on()
            FreeAutomaton(&r)
            r = NewAutomaton(0,0)
            sig_off()
            print("Error : Incorrect set of final states.")
            return r
        r.e[d[v]].final = 1

    if initial is None:
        if not hasattr(a, 'I'):
            I = []
            # raise ValueError("I must be defined !")
        else:
            I = list(a.I)
        if len(I) > 1:
            # L'automate doit être déterministe !
            print("The automata must be determist (I=%s)" % a.I)
        if len(I) >= 1:
            r.i = d[I[0]]
        else:
            r.i = -1
    else:
        r.i = initial

    for e, f, l in a.edges():
        r.e[d[e]].f[da[l]] = d[f]
    return r

cdef AutomatonGet(Automaton a, A):
    """
    Tranform a Automaton a with a alphabet A to a DiGraph
    """
    from sage.graphs.digraph import DiGraph
    r = DiGraph(multiedges=True, loops=True)
    cdef int i, j
    r.F = []
    for i in range(a.n):
        for j in range(a.na):
            if a.e[i].f[j] != -1:
                r.add_edge((i, a.e[i].f[j], A[j]))
        if a.e[i].final:
            r.F.append(i)
    r.I = [a.i]
    return r

# cdef initFA (Automaton *a):
#    *a = NewAutomaton(1,1)

cdef Bool(int x):
    if x:
        return True
    return False

cdef class NFastAutomaton:
    """
    Class :class:`NFastAutomaton`, this class encapsulates a C structure for Automata and 
    implement methods to manipulate non-determinist automata.

    INPUT:

    - ``a`` -- automaton must be a :class:`FastAutomaton`

    OUTPUT:

    Return a instance of :class:`NFastAutomaton`.

    EXAMPLES::

        sage: a = FastAutomaton([(0,1,'a') ,(2,3,'b')])
        sage: b = NFastAutomaton(a)
        sage: b
        NFastAutomaton with 4 states and an alphabet of 2 letters

    """
    def __cinit__(self):
        # print("cinit")
        self.a = <NAutomaton *>malloc(sizeof(NAutomaton))
        # initialise
        self.a.e = NULL
        self.a.n = 0
        self.a.na = 0
        self.A = []

    def _initialise_automaton(self, a):
        """
        Transform a determinist  :class:`FastAutomaton` to a non determinist
        :class:`NFastAutomaton`

        INPUT:

        - ``a`` -- automaton must be a :class:`FastAutomaton`

        OUTPUT:

        Return a instance of :class:`NFastAutomaton` initialized with ``a``

        EXAMPLES::
                sage: a = FastAutomaton([(0,1,'a') ,(2,3,'b')])
                sage: b = NFastAutomaton(a)
                sage: b
                NFastAutomaton with 4 states and an alphabet of 2 letters
        """
        if type(a) == FastAutomaton:
            a.copyn(self)
        else:
            raise ValueError("Cannot construct directly a NFastAutomaton for the moment, except from a deterministic one.")    
        return self

    def __init__(self, a): # TO DO i=None, final_states=None, A=None
        """
        TESTS::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=1)
            sage: b = NFastAutomaton(a)

        """
        #  print("init"

        if a is None:
            pass
        else:
            self = self._initialise_automaton(a)

    def __dealloc__(self):
        # print("free"
        FreeNAutomaton(self.a)
        free(self.a)

    def __repr__(self):
        return "NFastAutomaton with %d states and an alphabet of %d letters"%(self.a.n, self.a.na)

    def _latex_(self):
        r"""
        Return a latex representation of the automaton.

        TESTS::

            sage: a = FastAutomaton([(0,1,'a') ,(2,3,'b')])
            sage: b = NFastAutomaton(a)
            sage: latex(b) #  random

            \documentclass{article}
            \usepackage[x11names, rgb]{xcolor}
            \usepackage[utf8]{inputenc}
            \usepackage{tikz}
            \usetikzlibrary{snakes,arrows,shapes}
            \usepackage{amsmath}
            %
            %

            %

            %

            \begin{document}
            \pagestyle{empty}
            %
            %
            %

            \enlargethispage{100cm}
            % Start of code
            % \begin{tikzpicture}[anchor=mid,>=latex',line join=bevel,]
            \begin{tikzpicture}[>=latex',line join=bevel,]
              \pgfsetlinewidth{1bp}
            %%
            \pgfsetcolor{black}
            %
            \end{tikzpicture}
            % End of code

            %
            \end{document}
            %

        """
        sx = 800
        sy = 600
        from sage.misc.latex import LatexExpr
        cdef char *file
        from sage.misc.temporary_file import tmp_filename
        file_name = tmp_filename()+".dot"
        file = file_name
        try:
            from dot2tex import dot2tex
        except ImportError:
            print("dot2tex must be installed in order to have the LaTeX representation of the NFastAutomaton.")
            print("You can install it by doing './sage -i dot2tex' in a shell in the sage directory, or by doing 'install_package(package='dot2tex')' in the notebook.")
            return None
        cdef char** ll
        ll = <char **>malloc(sizeof(char*) * self.a.na)
        cdef int i
        strA = []
        for i in range(self.a.na):
            strA.append(str(self.A[i]))
            ll[i] = strA[i]
        sig_on()
        NplotDot(file, self.a[0], ll, "Automaton", sx, sy, False)
        sig_off()
        dotfile = open(file_name)
        return LatexExpr(dot2tex(dotfile.read()))

    @property
    def n_states(self):
        """
        return the numbers of states

        OUTPUT:

        return the numbers of states

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: b = NFastAutomaton(a)
            sage: b.n_states
            4
        """
        return self.a.n

    def n_succs(self, int i):
        """
        INPUT:

        -``i`` -- int successor number

        OUTPUT:

        return the numbers of succussor of state ``i``

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: b = NFastAutomaton(a)
            sage: b.n_succs(0)
            1
        """
        if i >= self.a.n or i < 0:
            raise ValueError("There is no state %s !" % i)
        return self.a.e[i].n

    # give the state at end of the jth edge of the state i
    def succ(self, int i, int j):
        """
        Give the state at end of the ``j``th edge of the state ``i``

        INPUT:

        -``i`` int state number
        -``j`` int edge number

        OUTPUT:

        return the state at end of the ``j``th edge of the state ``i``

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'),(1, 2, 'c'), (2, 3, 'b')], i=0)
            sage: b = NFastAutomaton(a)
            sage: b.succ(1, 0)
            2        
        """
        if i >= self.a.n or i < 0:
            raise ValueError("There is no state %s !"%i)
        if j >= self.a.e[i].n or j < 0:
            raise ValueError("The state %s has no edge number %s !"%(i,j))
        return self.a.e[i].a[j].e

    # give the label of the jth edge of the state i
    def label(self, int i, int j):
        """
        Give the label of the ``j``th edge of the state ``i``

        INPUT:

        -``i`` -- int state number
        -``j`` -- int edge number

        OUTPUT:

        return the label index of the ``j``th edge of the state ``i``

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'),(1, 2, 'c'), (2, 3, 'b')], i=0)
            sage: b = NFastAutomaton(a)
            sage: b.label(1, 0)
            1
        """
        if i >= self.a.n or i < 0:
            raise ValueError("There is no state %s !" % i)
        if j >= self.a.e[i].n or j < 0:
            raise ValueError("The state %s has no edge number %s !" % (i, j))
        return self.a.e[i].a[j].l

    def is_final(self, int i):
        """
        Return ``True``/``False`` if ``i`` state  is/or not  final

        INPUT:

        -``i`` -- int state number

        OUTPUT:

        Return ``True``/``False`` if ``i`` state  is/or not  final

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'),(1, 2, 'c'), (2, 3, 'b')], i=0)
            sage: b = NFastAutomaton(a)
            sage: b.is_final(1)
            True
        """
        if i >= self.a.n or i < 0:
            raise ValueError("There is no state %s !" % i)
        return Bool(self.a.e[i].final)

    def is_initial(self, int i):
        """
        Return `True``/``False`` if ``i`` state  is/or not  initial

        INPUT:

        -``i`` -- int state number

        OUTPUT:

        Return ``True``/``False`` if ``i`` state  is/or not  initial

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'),(1, 2, 'c'), (2, 3, 'b')], i=0)
            sage: b = NFastAutomaton(a)
            sage: b.is_initial(1)
            False
        """
        if i >= self.a.n or i < 0:
            raise ValueError("There is no state %s !" % i)
        return Bool(self.a.e[i].initial)

    @property
    def initial_states(self):
        """
        Get the initial state :class:`NFastAutomaton` attribut

        OUTPUT:

        Return the initial state ``i``  of  :class:`NFastAutomaton`

        EXAMPLES::

            sage: a = FastAutomaton([(0,1,'a') ,(2,3,'b')])
            sage: b = NFastAutomaton(a)
            sage: b.initial_states
            []
            sage: a = FastAutomaton([(0,1,'a') ,(2,3,'b')], i=2)
            sage: b = NFastAutomaton(a)
            sage: b.initial_states
            [2]
        """
        l = []
        for i in range(self.a.n):
            if self.a.e[i].initial:
                l.append(i)
        return l

    def final_states(self):
        """
        Indicate all final states

        OUTPUT:

        Return the list of final states

        EXAMPLES::

            sage: a = FastAutomaton([(0,1,'a') ,(2,3,'b')])
            sage: b = NFastAutomaton(a)
            sage: b.final_states()
            [0, 1, 2, 3]
            sage: a = FastAutomaton([(0,1,'a') ,(2,3,'b')], )
            sage: b = NFastAutomaton(a)
            sage: b.final_states()
            [0, 1, 2, 3]
            sage: a = FastAutomaton([(0,1,'a') ,(2,3,'b')], final_states=[0,3])
            sage: b = NFastAutomaton(a)
            sage: b.final_states()
            [0, 3]
        """
        l = []
        for i in range(self.a.n):
            if self.a.e[i].final:
                l.append(i)
        return l

    @property
    def Alphabet(self):
        """
        To get the :class:`NFastAutomaton` attribut Alphabet

        OUTPUT:

        Return a the alphabet ``A`` of  :class:`NFastAutomaton`

        EXAMPLES::

            sage: a = FastAutomaton([(0,1,'a') ,(2,3,'b')])
            sage: b = NFastAutomaton(a)
            sage: b.Alphabet
            ['a', 'b']

        """
        return self.A

    def set_initial_state(self, int i, bool initial=True):
        """
        Set the initial state.

        INPUT:

        - ``i` -- int the initial state of the automaton
        - ``initial`` -- (default: ``True``) in the case is initial

        EXAMPLES::

            sage: a = FastAutomaton([(0,1,'a') ,(2,3,'b')])
            sage: b = NFastAutomaton(a)
            sage: b.set_initial_state(2)
            sage: b.initial_states
            [2]
            sage: b.set_initial_state(6)
            Traceback (most recent call last):
            ...
            ValueError: initial state must be a current state : 6 not in [-1, 3]

        """
        if i < 0 or i >= self.a.n:
            raise ValueError("initial state must be a current state : " +
                             "%d not in [-1, %d]" % (i, self.a.n - 1))
        self.a.e[i].initial = initial

    def add_edge(self, i, l, f):
        """
        Add a edge in the automaton

        INPUT:

        - ``i`` -- the first state
        - ``l`` -- the label of edge
        - ``f`` -- the second state


        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: b = NFastAutomaton(a)
            sage: b.add_edge(2,'a',1)
            sage: b.add_edge(2,'v',1)
            Traceback (most recent call last):
            ...
            ValueError: The letter v doesn't exist.
            sage: b.add_edge(2,'v',6)
            Traceback (most recent call last):
            ValueError: The state  6 doesn't exist.
            sage: b.add_edge(5,'v',6)
            Traceback (most recent call last):
            ValueError: The state  5 doesn't exist.

        """
        if i >= self.a.n:
            raise ValueError("The state %s doesn't exist." % i)
        if f >= self.a.n:
            raise ValueError("The state  %s doesn't exist." % f)
        try:
            k = self.A.index(l)
        except:
            # La lettre %s n'existe pas.
            raise ValueError("The letter %s doesn't exist." % l)

        sig_on()
        AddEdgeN(self.a, i, f, k)
        sig_off()

    def add_state(self, bool final):
        """
        Add a state in the automaton

        INPUT:

        - ``final`` -- boolean indicate if the added state is final

        OUTPUT:

        return the numbers of states

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: b = NFastAutomaton(a)
            sage: b.add_state(True)  # not implemented
            TypeError                                 Traceback (most recent call last)
            ...
            TypeError: 'NotImplementedType' object is not callable
        """
        raise NotImplemented()

    def add_path(self, int e, int f, list li, verb=False):
        """
        Add a path between states ``e`` and ``f``
        of :class:`NFastAutomaton` following ``li``

        INPUT:

        - ``e`` -- int the input state
        - ``f`` -- int the final state 
        - ``li`` -- list of states
        - ``verb`` -- boolean (default: ``False``) fix
          to ``True`` for activation the verbose mode


        EXAMPLES::

            sage: a = FastAutomaton([(0,1,'a'), (2,3,'b')], i=2)
            sage: b = NFastAutomaton(a)
            sage: b.add_path(1, 2, [1])

        """
        cdef int *l = <int *>malloc(sizeof(int)*len(li));
        for i in range(len(li)):
            l[i] = li[i]
        sig_on()
        AddPathN(self.a, e, f, l, len(li), verb)
        sig_off()

    def determinise(self, puits=False, verb=0):
        """
        Determines a non determinist automaton with the same alphabet of ``self``

        INPUT:

        - ``puits``  -- (default: ``False``)
        - ``verb`` -- boolean (default: ``False``) fix
          to ``True`` for activation the verbose mode

        OUTPUT:

        Return a non determinist automaton  :class:`NFastAutomaton`

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: b = NFastAutomaton(a)
            sage: b.determinise()
            FastAutomaton with 2 states and an alphabet of 2 letters
        """
        cdef Automaton a
        sig_on()
        r = FastAutomaton(None)
        a = DeterminiseN(self.a[0], puits, verb)
        sig_off()
        r.a[0] = a
        r.A = self.A
        return r

    def plot(self, int sx=10, int sy=8, verb=False):
        """
        plot a representation of the :class:`FastAutomaton`.

        INPUT:

        - ``sx`` -- int (default: 10)
        - ``sy`` -- int (default: 8)
        - ``verb`` -- boolean (default: ``False``) fix
          to ``True`` for activation the verbose mode

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: b = NFastAutomaton(a)
            sage: g = b.plot().show()

        .. PLOT::

            a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            b = NFastAutomaton(a)
            sphinx_plot(b)

        """
        cdef char** ll
        cdef int i
        cdef char *file
        if DotExists ():
            ll = <char **>malloc(sizeof(char*) * self.a.na)
            strA = []
            for i in range(self.a.na):
                strA.append(str(self.A[i]))
                ll[i] = strA[i]
            from sage.misc.temporary_file import tmp_filename
            file_name = tmp_filename()
            file = file_name
            if verb:
                print("file=%s" % file_name)
            sig_on()
            NplotDot(file, self.a[0], ll, "Automaton", sx, sy, True)
            free(ll)
            sig_off()
            from PIL import Image
            return Image.open(file_name+'.png')
        else:
            raise NotImplementedError("You cannot plot the NFastAutomaton without dot. Install the dot command of the GraphViz package.")

# cdef set_FastAutomaton (FastAutomaton a, Automaton a2):
#    a.a[0] = a2

cdef class FastAutomaton:
    """
    Class :class:`FastAutomaton`, this class encapsulates a C structure for Automata and 
    implement methods to manipulate determinist automata.

    INPUT:

    - ``i`` -- (default None) initial state

    - ``final_states`` -- (default None) list of final states

    OUTPUT:

    Return a instance of :class:`FastAutomaton`.

    EXAMPLES::

        sage: a = FastAutomaton([(0,1,'a') ,(2,3,'b')])
        sage: a
        FastAutomaton with 4 states and an alphabet of 2 letters
        sage: d = DiGraph({0: [1,2,3], 1: [0,2]})
        sage: a = FastAutomaton(d)
        sage: a
        FastAutomaton with 4 states and an alphabet of 1 letters
        sage: g = DiGraph({0:{1:'x',2:'z',3:'a'}, 2:{5:'o'}})
        sage: a = FastAutomaton(g)
        sage: a
        FastAutomaton with 5 states and an alphabet of 4 letters
        sage: a = FastAutomaton([(0, 1,'a') ,(2, 3,'b')], i = 2)
        sage: a
        FastAutomaton with 4 states and an alphabet of 2 letters
        sage: a = FastAutomaton([(0,1,'a') ,(2,3,'b')], final_states=[0,3])
        sage: a
        FastAutomaton with 4 states and an alphabet of 2 letters
    """

#    cdef Automaton* a
#    cdef list A

    def __cinit__(self):

        """

        """
        # print "cinit"
        # print("cinit"
        self.a = <Automaton *>malloc(sizeof(Automaton))
        # initialise
        self.a.e = NULL
        self.a.n = 0
        self.a.na = 0
        self.a.i = -1
        self.A = []

    def __init__(self, a, i=None, final_states=None, A=None):
        """
        TESTS:

            sage: a = FastAutomaton([(0,1,'a') ,(2,3,'b')])
            sage: a
            FastAutomaton with 4 states and an alphabet of 2 letters
        """
        # print "init"

        # print("init"
        if a is None:
            return
        from sage.graphs.digraph import DiGraph
        if isinstance(a, list):
            a = DiGraph(a, multiedges=True, loops=True)
        if isinstance(a, DiGraph):
            if A is None:
                #   if hasattr(a, 'A'):
                #       A = list(a.A)
                #   else:
                A = list(set(a.edge_labels()))
            self.A = A
            self.a[0] = getAutomaton(a, initial=i, F=final_states, A=self.A)
        elif isinstance(a, FastAutomaton):
            self = a
        else:
            raise ValueError("Cannot convert the input to FastAutomaton.")

    def __dealloc__(self):
        """
        Desalloc  Automaton  Overwrite built-in function

        TESTS::

        """
        # print("free (%s etats) "%self.a.n)
        sig_on()
        FreeAutomaton(self.a)
        # print("free self.a")
        free(self.a)
        sig_off()

    def __repr__(self):
        """
        Return a representation of automaton,  Overwrite built-in function

        OUTPUT:

        Return a representation of automaton

        TESTS:

            sage: a = FastAutomaton([(0,1,'a') ,(2,3,'b')])
            sage: repr(a)
            'FastAutomaton with 4 states and an alphabet of 2 letters'

        """
        return "FastAutomaton with %d states and an alphabet of %d letters" % (self.a.n, self.a.na)

    def _latex_(self):
        r"""
        Return a latex representation of the automaton.

        OUTPUT:

        Return a latex representation of the automaton.

        EXAMPLES::

            sage: a = FastAutomaton([(0,1,'a') ,(2,3,'b')])
            sage: latex(a)  # indirect doctest
            \documentclass{article}
            \usepackage[x11names, rgb]{xcolor}
            \usepackage[utf8]{inputenc}
            \usepackage{tikz}
            \usetikzlibrary{snakes,arrows,shapes}
            \usepackage{amsmath}
            %
            %
            <BLANKLINE>
            %
            <BLANKLINE>
            %
            <BLANKLINE>
            \begin{document}
            \pagestyle{empty}
            %
            %
            %
            <BLANKLINE>
            \enlargethispage{100cm}
            % Start of code
            % \begin{tikzpicture}[anchor=mid,>=latex',line join=bevel,]
            \begin{tikzpicture}[>=latex',line join=bevel,]
              \pgfsetlinewidth{1bp}
            %%
            \pgfsetcolor{black}
              % Edge: 0 -> 1
              \draw [-stealth'] (44.302bp,22.0bp) .. controls (54.895bp,22.0bp) and (67.905bp,22.0bp)  .. (89.894bp,22.0bp);
              \definecolor{strokecol}{rgb}{0.0,0.0,0.0};
              \pgfsetstrokecolor{strokecol}
              \draw (67.0bp,33.0bp) node {a};
              % Edge: 2 -> 3
              \draw [-stealth'] (44.302bp,80.0bp) .. controls (54.895bp,80.0bp) and (67.905bp,80.0bp)  .. (89.894bp,80.0bp);
              \draw (67.0bp,91.0bp) node {b};
              % Node: 1
            \begin{scope}
              \definecolor{strokecol}{rgb}{0.0,0.0,0.0};
              \pgfsetstrokecolor{strokecol}
              \draw [solid] (112.0bp,22.0bp) ellipse (18.0bp and 18.0bp);
              \draw [solid] (112.0bp,22.0bp) ellipse (22.0bp and 22.0bp);
              \draw (112.0bp,22.0bp) node {1};
            \end{scope}
              % Node: 0
            \begin{scope}
              \definecolor{strokecol}{rgb}{0.0,0.0,0.0};
              \pgfsetstrokecolor{strokecol}
              \draw [solid] (22.0bp,22.0bp) ellipse (18.0bp and 18.0bp);
              \draw [solid] (22.0bp,22.0bp) ellipse (22.0bp and 22.0bp);
              \draw (22.0bp,22.0bp) node {0};
            \end{scope}
              % Node: 3
            \begin{scope}
              \definecolor{strokecol}{rgb}{0.0,0.0,0.0};
              \pgfsetstrokecolor{strokecol}
              \draw [solid] (112.0bp,80.0bp) ellipse (18.0bp and 18.0bp);
              \draw [solid] (112.0bp,80.0bp) ellipse (22.0bp and 22.0bp);
              \draw (112.0bp,80.0bp) node {3};
            \end{scope}
              % Node: 2
            \begin{scope}
              \definecolor{strokecol}{rgb}{0.0,0.0,0.0};
              \pgfsetstrokecolor{strokecol}
              \draw [solid] (22.0bp,80.0bp) ellipse (18.0bp and 18.0bp);
              \draw [solid] (22.0bp,80.0bp) ellipse (22.0bp and 22.0bp);
              \draw (22.0bp,80.0bp) node {2};
            \end{scope}
            %
            \end{tikzpicture}
            % End of code
            <BLANKLINE>
            %
            \end{document}
            %
            <BLANKLINE>
            <BLANKLINE>
            <BLANKLINE>
        """
        sx = 800
        sy = 600
        vlabels = None
        html = False
        verb = False
        from sage.misc.latex import LatexExpr
        cdef char *file
        from sage.misc.temporary_file import tmp_filename
        file_name = tmp_filename()+".dot"
        file = file_name
        try:
            from dot2tex import dot2tex
        except ImportError:
            print("dot2tex must be installed in order to have the LaTeX representation of the FastAutomaton.")
            print("You can install it by doing './sage -i dot2tex' in a shell in the sage directory, or by doing 'install_package(package='dot2tex')' in the notebook.")
            return None
        cdef char** ll # labels of edges
        cdef char** vl # labels of vertices
        cdef int i
        ll = <char **>malloc(sizeof(char*) * self.a.na)
        if vlabels is None:
            vl = NULL
        else:
            if verb:
                print("alloc %s..."%self.a.n)
            vl = <char **>malloc(sizeof(char*) * self.a.n)
            strV = []
            if verb:
                print("len %s %s" % (self.a.n, len(vlabels)))
            for i in range(self.a.n):
                if html:
                    strV.append("<" + vlabels[i] + ">")
                else:
                    strV.append("\"" + vlabels[i] + "\"")
                if verb:
                    print(strV[i])
                vl[i] = strV[i]
                if verb:
                    print("i=%s : %s" % (i, vl[i]))
        strA = []
        for i in range(self.a.na):
            strA.append(str(self.A[i]))
            ll[i] = strA[i]
        if verb:
            for i in range(self.a.n):
                print("i=%s : %s" % (i, vl[i]))
        if verb:
            print("plot...")
        sig_on()
        plotDot(file, self.a[0], ll, "Automaton", sx, sy, vl, verb, False)
        sig_off()
        if verb:
            print("free...plot")
        free(ll)
        if vlabels is not None:
            free(vl)
        dotfile = open(file_name)
        return LatexExpr(dot2tex(dotfile.read()))

    def __hash__(self):
        """
        Hash automaton,  Overwrite built-in function

        OUTPUT:

        Return the hash code of the automaton

        TESTS::

            sage: a = FastAutomaton([(0,1,'a') ,(2,3,'b')])
            sage: hash(a)
            731776466
        """
        h = 3
        for a in self.A:
            h += hash(a)
            h = (h*19) % 1000000007
        h += hashAutomaton(self.a[0])
        # print "hash=%s"%h
        return h

    def __cmp__(self, FastAutomaton other):
        """
        Compare function, Overwrite built-in function

        INPUT:

        - ``other`` -- other :class:`FastAutomaton` to compare

        OUTPUT:

        Return the result of test (``True`` or ``False``)

        TESTS::

            sage: a = FastAutomaton([(0,1,'a') ,(2,3,'b')])
            sage: b = FastAutomaton([(0, 1, 'a'),(1,2,'c')], i=0)
            sage: a > b  # indirect doctest
            True
            sage: a < b  # indirect doctest
            False
            sage: a == b  # indirect doctest
            False
        """
        # if type(other) != FastAutomaton:
        #    return 1
        cdef int r
        sig_on()
        r = equalsAutomaton(self.a[0], other.a[0]) and self.A == other.A
        sig_off()
        # print "cmp %s"%r
        return (r == 0)

#     def Automaton(self):
#         return AutomatonGet(self.a[0], self.A)

#    cdef set_a(self, Automaton a):
#        self.a[0] = a

    # give a FastAutomaton recognizing the full language over A.
    def full(self, list A):
        """
        Give a :class:`FastAutomaton` recognizing the full language over A.

        INPUT:

        - ``A`` -- list of letters of alphabet

        OUTPUT:

        Return a :class:`FastAutomaton` recognizing the full language over A.

        EXAMPLES::

            sage: a = FastAutomaton([(0,1,'a') ,(2,3,'b')])
            sage: a
            FastAutomaton with 4 states and an alphabet of 2 letters
            sage: a.full(['a'])
            FastAutomaton with 1 states and an alphabet of 1 letters
            sage: a.full(['a','b'])
            FastAutomaton with 1 states and an alphabet of 2 letters
            sage: a.full(['a','b','c'])
            FastAutomaton with 1 states and an alphabet of 3 letters
        """
        cdef Automaton a
        r = FastAutomaton(None)
        sig_on()
        a = NewAutomaton(1, len(A))
        sig_off()
        for i in range(len(A)):
            a.e[0].f[i] = 0
        a.e[0].final = True
        a.i = 0
        r.a[0] = a
        r.A = A

        return r

    def plot(self, int sx=10, int sy=8, vlabels=None, html=False, verb=False):
        """
        Plot the :class:`FastAutomaton`. realise a a dot plotting if dot is installed on the platform

        INPUT:

        - ``sx`` -- int (default: 10)
        - ``sy`` -- int (default: 8)
        - ``vlabels`` -- (default: None)
        - ``html`` -- (default: ``False``)
        - ``verb`` -- (default: ``False``) fix
          to ``True`` for activation the verbose mode

        TESTS::

            sage: a = FastAutomaton([(0,1,'a') ,(2,3,'b')])
            sage: a.plot()  # random
            <PIL.PngImagePlugin.PngImageFile image mode=RGBA size=189x147 at 0x7FD4B6D94390>

        EXAMPLES::

            sage: a = FastAutomaton([(0,1,'a') ,(2,3,'b')])
            sage: a.plot().show()

        .. PLOT::

            a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sphinx_plot(a)
        """
        cdef char *file
        cdef char** ll # labels of edges
        cdef char** vl # labels of vertices
        cdef int i
        if DotExists():
            from sage.misc.temporary_file import tmp_filename
            file_name = tmp_filename()+".dot"
            file = file_name
            ll = <char **>malloc(sizeof(char*) * self.a.na)
            if vlabels is None:
                vl = NULL
            else:
                if verb:
                    print("alloc %s..." % self.a.n)
                vl = <char **>malloc(sizeof(char*) * self.a.n)
                strV = []
                if verb:
                    print("len %s %s" % (self.a.n, len(vlabels)))
                for i in range(self.a.n):
                    if html:
                        strV.append("<" + vlabels[i] + ">")
                    else:
                        strV.append("\"" + vlabels[i] + "\"")
                    if verb:
                        print(strV[i])
                    vl[i] = strV[i]
                    if verb:
                        print("i=%s : %s" % (i, vl[i]))
            strA = []
            for i in range(self.a.na):
                strA.append(str(self.A[i]))
                ll[i] = strA[i]
            if verb:
                for i in range(self.a.n):
                    print("i=%s : %s" % (i, vl[i]))
            if verb:
                print("plot...")
            sig_on()
            plotDot(file, self.a[0], ll, "Automaton", sx, sy, vl, verb, True)
            sig_off()
            if verb:
                print("free...plot")
            free(ll)
            if vlabels is not None:
                free(vl)
            from PIL import Image
            return Image.open(file_name+'.png')
        else:
            raise NotImplementedError("You cannot plot the FastAutomaton without dot. Install the dot command of the GraphViz package.")

    @property
    def Alphabet(self):
        """
        To get the :class:`FastAutomaton` attribut Alphabet

        OUTPUT:

        Return a the alphabet ``A`` of  :class:`FastAutomaton`

        EXAMPLES::

            sage: a = FastAutomaton([(0,1,'a') ,(2,3,'b')])
            sage: a.Alphabet
            ['a', 'b']
        """
        return self.A

    def setAlphabet(self, list A):
        """
        Set the alphabet

        INPUT:

        - ``A`` -- list of letters of alphabet

        EXAMPLES::

            sage: a = FastAutomaton([(0,1,'a') ,(2,3,'b')])
            sage: a.setAlphabet(['a', 'b', 'c'])
            sage: a.Alphabet
            ['a', 'b', 'c']
            sage: a = FastAutomaton([(0,1,'a') ,(2,3,'b')])
            sage: a.setAlphabet(['a','e'])
            sage: a.Alphabet
            ['a', 'e']
        """
        self.A = A
        self.a[0].na = len(A)

    @property
    def initial_state(self):
        """
        Get the initial state :class:`FastAutomaton` attribut

        OUTPUT:

        Return the initial state ``i``  of  :class:`FastAutomaton`

        EXAMPLES::

            sage: a = FastAutomaton([(0,1,'a') ,(2,3,'b')])
            sage: a.initial_state
            -1
            sage: a = FastAutomaton([(0,1,'a') ,(2,3,'b')], i=2)
            sage: a.initial_state
            2
        """
        return self.a.i

    def set_initial_state(self, int i):
        """
        Set the initial state.

        INPUT:

        - ``i`` -- int the initial state of the automaton

        EXAMPLES::

            sage: a = FastAutomaton([(0,1,'a') ,(2,3,'b')])
            sage: a.set_initial_state(2)
            sage: a.initial_state
            2
            sage: a.set_initial_state(6)
            Traceback (most recent call last):
            ...
            ValueError: initial state must be a current state : 6 not in [-1, 3]
        """
        if i < self.a.n and i >= -1:
            self.a.i = i
        else:
            raise ValueError("initial state must be a current state : " +
                             "%d not in [-1, %d]" % (i, self.a.n - 1))

    def final_states(self):
        """
        Indicate all final states

        OUTPUT:

        Return the list of final states

        EXAMPLES::

            sage: a = FastAutomaton([(0,1,'a') ,(2,3,'b')])
            sage: a.final_states()
            [0, 1, 2, 3]
            sage: a = FastAutomaton([(0,1,'a') ,(2,3,'b')], )
            sage: a.final_states()
            [0, 1, 2, 3]
            sage: a = FastAutomaton([(0,1,'a') ,(2,3,'b')], final_states=[0,3])
            sage: a.final_states()
            [0, 3]
        """
        l = []
        for i in range(self.a.n):
            if self.a.e[i].final:
                l.append(i)
        return l

    def states(self):
        """
        Indicate all states of the automaton

        OUTPUT:

        Return the list of states

        EXAMPLES::

            sage: a = FastAutomaton([(0,1,'a') ,(2,3,'b')])
            sage: a.states()
            [0, 1, 2, 3]
        """
        return range(self.a.n)

    def set_final_states(self, lf):
        """
        Set the final states.

         INPUT:

        - ``lf`` -- list of states to set as final

        EXAMPLES::

            sage: a = FastAutomaton([(0,1,'a') ,(2,3,'b')])
            sage: a.set_final_states([0,3])
            sage: a.final_states()
            [0, 3]
            sage: a.set_final_states([0,4])
            Traceback (most recent call last):
            ...
            ValueError: 4 is not a state !

        """
        cdef int f
        for f in range(self.a.n):
            self.a.e[f].final = 0
        for f in lf:
            if f < 0 or f >= self.a.n:
                raise ValueError("%d is not a state !" % f)
            self.a.e[f].final = 1

    def is_final(self, int e):
        """
        Indicate if the state is final

         INPUT:

        - ``e`` -- int input state to examine as final

        OUTPUT:

        ``True`` if the state ``e`` is final (i.e. ``False`` in the other case)

        EXAMPLES::

            sage: a = FastAutomaton([(0,1,'a') ,(2,3,'b')])
            sage: a.is_final(3)
            True
            sage: a.is_final(4)
            False
            sage: a = FastAutomaton([(0,1,'a') ,(2,3,'b')], final_states=[0,3])
            sage: a.is_final(2)
            False
        """
        if e >= 0 and e < self.a.n:
            return Bool(self.a.e[e].final)
        else:
            return False

    def set_final_state(self, int e, final=True):
        """
        Set the final state.

         INPUT:

        - ``e`` -- int state to set as final
        - ``final`` -- (default: ``True``) in the case is final

        EXAMPLES::

            sage: a = FastAutomaton([(0,1,'a') ,(2,3,'b')])
            sage: a.set_final_state(3)
            sage: a.final_states()
            [0, 1, 2, 3]
            sage: a.set_final_state(4)
            Traceback (most recent call last):
            ...
            ValueError: 4 is not a state !
        """
        if e >= 0 and e < self.a.n:
            self.a.e[e].final = final
        else:
            raise ValueError("%d is not a state !" % e)

    def succ(self, int i, int j):
        """
        return the successor of state.

        INPUT:

        - ``i`` -- int the input state
        - ``j`` -- int the output state

        OUTPUT:

        return successor of state

        EXAMPLES::

            sage: a = FastAutomaton([(0,1,'a'), (2,3,'b')])
            sage: a.succ(0, 1)
            -1
            sage: a.succ(2,1)
            3

        """
        if i < 0 or i >= self.a.n or j < 0 or j >= self.a.na:
            return -1
        return self.a.e[i].f[j]

    # donne les fils de l'état i
    def succs(self, int i):
        """
        return lines of state ``i``.

        INPUT:

        - ``i`` -- int the input state

        OUTPUT:

        return lines of state ``i``

        EXAMPLES::

            sage: a = FastAutomaton([(0,1,'a'), (2,3,'b')])
            sage: a.succs(2)
            [1]
            sage: a.succs(4)
            []

        """
#        if i is None:
#            i = self.a.i
#        el
        if i < 0 or i >= self.a.n:
            return []
        return [j for j in range(self.a.na) if self.a.e[i].f[j] != -1]

    # suit le chemin étiqueté par l et rend l'état atteint
    def path(self, list l, i=None):
        """
        Follows the path labeled by ``l`` and return the reached state

        INPUT:

        - ``l`` -- list indicate the  way label
        - ``i`` -- (default: ``None``) the initial state

        OUTPUT:

        return the state reached after the following way

        EXAMPLES::

            sage: a = FastAutomaton([(0,1,'a'), (2,3,'b')], i=2)
            sage: a.path([1])
            3
            sage: a.path([0, 2])
            -1
        """
        if i is None:
            i = self.a.i
        for j in l:
            i = self.succ(i, j)
        return i

    def set_succ(self, int i, int j, int k):
        """
        Set the successor state

        INPUT:

        - ``i`` -- int the input state
        - ``j`` -- int the output state

        EXAMPLES::

            sage: a = FastAutomaton([(0,1,'a'), (2, 3,'b')], i=2)
            sage: a.set_succ(0, 1, 2)
            sage: a.succs(0)
            [0, 1]
            sage: a.set_succ(0, 4, 2)
            Traceback (most recent call last):
            ...
            ValueError: set_succ(0, 4) : index out of bounds !

        """
        if i < 0 or i >= self.a.n or j < 0 or j >= self.a.na:
            raise ValueError("set_succ(%s, %s) : index out of bounds !" % (i, j))
        self.a.e[i].f[j] = k

    def zero_completeOP(self, verb=False):
        """
        zero-complete automaton

        INPUT:

        - ``verb`` -- (default: ``False``) fix
          to ``True`` for activation the verbose mode

        OUTPUT:

        Return the zero-complete :class:`FastAutomaton`.

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (0, 3, 'b')], i=0)
            sage: a.zero_completeOP(True)
            l0 = 0
            state 0 ..
            state 1 ..
            state 2 ..
        """
        sig_on()
        ZeroComplete(self.a, list(self.A).index(self.A[0]), verb)
        sig_off()

    def zero_complete2(self, etat_puits=False, verb=False):
        """
        zero-complete automaton in the other way

        INPUT:

        - ``etat_puits`` --  (default: ``False``)
        - ``verb`` -- (default: ``False``) fix
          to ``True`` for activation the verbose mode

        OUTPUT:

        Return the zero-complete :class:`FastAutomaton`.

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (0, 3, 'b')], i=0)
            sage: a.zero_complete2(True)
            FastAutomaton with 2 states and an alphabet of 2 letters

        """
        cdef Automaton a
        r = FastAutomaton(None)
        sig_on()
        a = ZeroComplete2(self.a, list(self.A).index(self.A[0]), etat_puits, verb)
        sig_off()
        r.a[0] = a
        r.A = self.A

        return r.emonde().minimise()

    def zero_inv(self, z=0):
        """
        Inverse automaton

        INPUT:

        - ``z`` --  (default: 0) index of alphabet letter to begin

        OUTPUT:

        Return the inversed :class:`FastAutomaton`.

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (0, 3, 'b')], i=0)
            sage: a.zero_inv(0)
            FastAutomaton with 2 states and an alphabet of 2 letters
            sage: a.zero_inv(1)
            FastAutomaton with 2 states and an alphabet of 2 letters
        """
        cdef Automaton a
        r = FastAutomaton(None)
        sig_on()
        a = ZeroInv(self.a, list(self.A).index(self.A[z]))
        sig_off()
        r.a[0] = a
        r.A = self.A
        return r.emonde().minimise()

    # change the final states of the automaton
    # new final states are the one in a strongly connected component containing a final state, others states are not final
    # this function can be accelerated
    def emonde_inf2OP(self, verb=False):
        """
        Compute the emondation of the automaton
        change the final states of the automaton
        new final states are the one in a strongly
        connected component containing a final state,
        others states are not final
        this function can be accelerated

        INPUT:

        - ``verb`` -- boolean (default: ``False``) fix
          to ``True`` for activation the verbose mode

        OUTPUT:

        Return the emonded :class:`FastAutomaton`.

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (0, 3, 'b')], i=0)
            sage: a.emonde_inf2OP(True)
            sage: a
            FastAutomaton with 3 states and an alphabet of 2 letters
        """
        cc = self.strongly_connected_components()
        f = []
        for c in cc:
            # test que l'on peut boucler dans cette composante
            ok = False
            for i in range(self.a.na):
                if self.a.e[c[0]].f[i] in c:
                    ok = True
                    break
            if not ok:
                continue
            for i in c:
                if self.a.e[i].final:
                    f += c
                    break
        self.set_final_states(f)

    # new final states are the ones in strongly connected components
    def emonde_inf(self, verb=False):
        """
        Compute the emondation of the automaton
        remove all states from which there no infinite way

        INPUT:

        - ``verb`` -- boolean (default: ``False``) fix
          to ``True`` for activation the verbose mode

        OUTPUT:

        Return the emonded :class:`FastAutomaton`.

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (0, 3, 'b')], i=0)
            sage: a.emonde_inf(True)
            recurrence...
            States counter = 0
            count...
            cpt = 0
            final states...
            FastAutomaton with 0 states and an alphabet of 2 letters

        """
        cdef Automaton a
        r = FastAutomaton(None)
        sig_on()
        a = emonde_inf(self.a[0], verb)
        sig_off()
        r.a[0] = a
        r.A = self.A
        return r

    def emonde_i(self, verb=False):
        """
        Compute the emondation of the automaton
        remove all not accessible states

        INPUT:

        - ``verb`` -- boolean (default: ``False``) fix
          to ``True`` for activation the verbose mode

        OUTPUT:

        Return the emonded :class:`FastAutomaton`.

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (0, 3, 'b'), (0, 3, 'b')], i=0)
            sage: a.emonde_i(True)
            deleted States : [ ]
            FastAutomaton with 3 states and an alphabet of 2 letters
            sage: a = FastAutomaton([(0, 1, 'a'), (0, 3, 'b'), (0, 3, 'b')])
            sage: a.emonde_i(True)
            FastAutomaton with 0 states and an alphabet of 2 letters
        """
        if self.initial_state == -1:
            empty = FastAutomaton([])
            empty.setAlphabet(self.Alphabet)
            return empty
        cdef Automaton a
        r = FastAutomaton(None)
        sig_on()
        a = emondeI(self.a[0], verb)
        sig_off()
        r.a[0] = a
        r.A = self.A
        return r

    def emonde(self, verb=False):
        """
        Compute the emondation of the automaton
        remove all not accessible and not co-accessible states

        INPUT:

        - ``verb`` -- boolean (default: ``False``) fix
          to ``True`` for activation the verbose mode

        OUTPUT:

        Return the emonded :class:`FastAutomaton`.

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: a.emonde(True)
            4 components : [ 1 0 3 2 ]
            0 : [ 1 ]
            1 : [ 0 ]
            2 : [ 3 ]
            3 : [ 2 ]
            0 co-acc
            1 co-acc
            2 co-acc
            3 co-acc
            rec...
            l : [ 0(7) 1(7) -1(5) -1(5) ]
            create the new automaton 2 2...
            pass 2
            pass 3
            deleted States : [ 2( non-acc ) 3( non-acc ) ]
            FastAutomaton with 2 states and an alphabet of 2 letters
        """
        cdef Automaton a
        r = FastAutomaton(None)
        sig_on()
        a = emonde(self.a[0], verb)
        sig_off()
        r.a[0] = a
        r.A = self.A
        return r

#    def equals (self, FastAutomaton b):
#        return Bool(equalsAutomaton(self.a[0], b.a[0]))

    # assume that the dictionnary d is injective !!!
    def product(self, FastAutomaton b, dict d=None, verb=False):
        """
        Give the product of the :class:`FastAutomaton` and ``a`` an other
        ``FastAutomaton``.

        INPUT:

        - ``a`` -- :class:`FastAutomaton` to multiply
        - ``d`` -- dict (default: ``None``) dictionary to translate
          language of automaton
        - ``verb`` -- boolean (default: ``False``) fix
          to ``True`` for activation the verbose mode

        OUTPUT:

        Return the product as a :class:`FastAutomaton`.

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: b = FastAutomaton([(3, 2, 'c'), (1, 2, 'd')], i=2)
            sage: a.product(b)
            FastAutomaton with 12 states and an alphabet of 4 letters
            sage: a.product(b, verb =True)
            {('b', 'c'): ('b', 'c'), ('a', 'd'): ('a', 'd'), ('a', 'c'): ('a', 'c'), ('b', 'd'): ('b', 'd')}
            Av=[('a', 'c'), ('a', 'd'), ('b', 'c'), ('b', 'd')]
            dv={('b', 'c'): 2, ('a', 'd'): 1, ('a', 'c'): 0, ('b', 'd'): 3}
            {'a': 0, 'b': 1}
            {'c': 0, 'd': 1}
            Keys=[('b', 'c'), ('a', 'd'), ('a', 'c'), ('b', 'd')]
            dC=
            [ 0 2 1 3 ]
            Automaton with 4 states, 2 letters.
            0 --0--> 1
            2 --1--> 3
            initial State 0.
            Automaton with 3 states, 2 letters.
            0 --1--> 1
            2 --0--> 1
            initial State 2.
            FastAutomaton with 12 states and an alphabet of 4 letters
        """
        if d is None:
            d = {}
            for la in self.A:
                for lb in b.A:
                    d[(la, lb)] = (la, lb)
            if verb:
                print(d)
        cdef Automaton a
        cdef Dict dC
        r = FastAutomaton(None)
        Av = []
        sig_on()
        dv = imagProductDict(d, self.A, b.A, Av=Av)
        sig_off()
        if verb:
            print("Av=%s" % Av)
            print("dv=%s" % dv)
        sig_on()
        dC = getProductDict(d, self.A, b.A, dv=dv, verb=verb)
        sig_off()
        if verb:
            print("dC=")
            printDict(dC)
        sig_on()
        a = Product(self.a[0], b.a[0], dC, verb)
        FreeDict(&dC)
        sig_off()
        r.a[0] = a
        r.A = Av

        return r

    def intersection(self, FastAutomaton a, verb=False, simplify=True):
        """
        Give the intersection of the :class:`FastAutomaton` and ``a`` an other
        :class:`FastAutomaton`.

        INPUT:

        - ``a`` -- :class:`FastAutomaton` to intersect
        - ``verb`` -- boolean (default: ``False``) fix
          to ``True`` for activation the verbose mode
        - ``simplify`` --  (default: ``True``) if simplification
          is required

        OUTPUT:

        Return the intersected :class:`FastAutomaton`.

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: b = FastAutomaton([(3, 2, 'c'), (1, 2, 'd')], i=2)
            sage: a.intersection(b)
            FastAutomaton with 1 states and an alphabet of 0 letters
            sage: a.intersection(b, simplify=False)
            FastAutomaton with 12 states and an alphabet of 0 letters
        """
        d = {}
        for l in self.A:
            if l in a.A:
                d[(l, l)] = l
        if verb:
            print("d=%s" % d)
        p = self.product(a, d, verb=verb)
        if simplify:
            return p.emonde().minimise()
        else:
            return p

    # determine if the automaton is complete (i.e. with his hole state)
    def is_complete(self):
        """
        Determine if the automaton is complete (i.e. with his hole state)

        OUTPUT:

        Return ``True`` if the automaton is complete (i.e. ``False`` if not)

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: a.is_complete()
            False
            sage: a = FastAutomaton([(0, 0, 'a')])
            sage: a.is_complete()
            True
        """
        sig_on()
        res = IsCompleteAutomaton(self.a[0])
        sig_off()
        return Bool(res)

    # give a complete automaton (i.e. with his hole state)
    def complete(self):
        """
        Give the complete automaton (i.e. with his hole state)

        OUTPUT:

        Return ``True`` if the automaton is complete (i.e. ``False`` if not)

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: a.complete()
            True
        """
        sig_on()
        res = CompleteAutomaton(self.a)
        sig_off()
        return Bool(res)

    # give the smallest language stable by prefix containing the language of self
    # i.e. every states begin finals
    def prefix_closure(self):
        """
        give the smallest language stable by prefix containing the language of self
        i.e. every states begin finals

        OUTPUT:

        Return the smallest language :class:`FastAutomaton`

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: a.prefix_closure()
            FastAutomaton with 2 states and an alphabet of 2 letters
        """
        cdef int i
        cdef Automaton a
        r = FastAutomaton(None)
        sig_on()
        a = emonde(self.a[0], False)
        sig_off()
        r.a[0] = a
        r.A = self.A
        for i in range(a.n):
            a.e[i].final = True
        return r

    # FastAutomaton
    def union(self, FastAutomaton a, simplify=True, verb=False):
        """
        re-union :class:`FastAutomaton`

        INPUT:

        - ``a`` -- :class:`FastAutomaton` to union
        - ``simplify`` --  (default: ``True``) if simplification
          is required
        - ``verb`` -- boolean (default: ``False``) fix
          to ``True`` for activation the verbose mode

        OUTPUT:

        Return the union :class:`FastAutomaton`

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: b = FastAutomaton([(3, 2, 'a'), (1, 2, 'd')], i=2)
            sage: a.union(b, verb=True)
            Av=['a']
            dv={'a': 0}
            {'a': 0, 'b': 1}
            {'a': 0, 'd': 1}
            Keys=[('a', 'a')]
            dC=
            [ 0 -1 -1 -1 ]
            Automaton with 5 states, 2 letters.
            0 --0--> 1
            0 --1--> 4
            1 --0--> 4
            1 --1--> 4
            2 --0--> 4
            2 --1--> 3
            3 --0--> 4
            3 --1--> 4
            4 --0--> 4
            4 --1--> 4
            initial State 0.
            Automaton with 4 states, 2 letters.
            0 --0--> 3
            0 --1--> 1
            1 --0--> 3
            1 --1--> 3
            2 --0--> 1
            2 --1--> 3
            3 --0--> 3
            3 --1--> 3
            initial State 2.
            FastAutomaton with 2 states and an alphabet of 1 letters
            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: b = FastAutomaton([(3, 2, 'a'), (1, 2, 'd')], i=2)
            sage: a.union(b, simplify=True)
            FastAutomaton with 2 states and an alphabet of 1 letters

        """
        # complete the automata
        sig_on()
        CompleteAutomaton(self.a)
        CompleteAutomaton(a.a)
        sig_off()

        # make the product
        d = {}
        for l in self.A:
            if l in a.A:
                d[(l, l)] = l

        cdef Automaton ap
        cdef Dict dC
        r = FastAutomaton(None)
        Av = []
        sig_on()
        dv = imagProductDict(d, self.A, a.A, Av=Av)
        sig_off()
        if verb:
            print("Av=%s" % Av)
            print("dv=%s" % dv)
        sig_on()
        dC = getProductDict(d, self.A, a.A, dv=dv, verb=verb)
        sig_off()
        if verb:
            print("dC=")
            printDict(dC)
        sig_on()
        ap = Product(self.a[0], a.a[0], dC, verb)
        FreeDict(&dC)
        sig_off()
        # set final states
        cdef int i, j
        cdef n1 = self.a.n
        for i in range(n1):
            for j in range(a.a.n):
                ap.e[i + n1 * j].final = self.a.e[i].final or a.a.e[j].final

        r.a[0] = ap
        r.A = Av
        # if verb:
        #    print r
        # r = r.emonde()
        # r = r.minimise()
        if simplify:
            return r.emonde().minimise()
        else:
            return r

    # split the automaton with respect to a  FastAutomaton
    def split(self, FastAutomaton a, verb=False):
        """
        Split the automaton with respect to ``a`` a :class:`FastAutomaton`

        INPUT:

        - ``a`` -- :class:`FastAutomaton` in respect to split

        OUTPUT:

        Return tuple of two splited automaton

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: b = FastAutomaton([(3, 2, 'a'), (1, 2, 'd')], i=2)
            sage: a.split(b, verb=True)
            Av=['a']
            dv={'a': 0}
            {'a': 0, 'b': 1}
            {'a': 0, 'd': 1}
            Keys=[('a', 'a')]
            dC=
            [ 0 -1 -1 -1 ]
            Automaton with 4 states, 2 letters.
            0 --0--> 1
            2 --1--> 3
            initial State 0.
            Automaton with 4 states, 2 letters.
            0 --0--> 3
            0 --1--> 1
            1 --0--> 3
            1 --1--> 3
            2 --0--> 1
            2 --1--> 3
            3 --0--> 3
            3 --1--> 3
            initial State 2.
            [FastAutomaton with 2 states and an alphabet of 1 letters,
             FastAutomaton with 1 states and an alphabet of 1 letters]

        """
        # complete the automaton a
        sig_on()
        CompleteAutomaton(a.a)
        sig_off()
        # make the product
        d = {}
        for l in self.A:
            if l in a.A:
                d[(l, l)] = l

        cdef Automaton ap
        cdef Dict dC
        r = FastAutomaton(None)
        r2 = FastAutomaton(None)
        Av = []
        sig_on()
        dv = imagProductDict(d, self.A, a.A, Av=Av)
        sig_off()
        if verb:
            print("Av=%s" % Av)
            print("dv=%s" % dv)
        sig_on()
        dC = getProductDict(d, self.A, a.A, dv=dv, verb=verb)
        sig_off()
        if verb:
            print("dC=")
            printDict(dC)
        sig_on()
        ap = Product(self.a[0], a.a[0], dC, verb)
        FreeDict(&dC)
        sig_off()
        # set final states for the intersection
        cdef int i, j
        cdef n1 = self.a.n
        for i in range(n1):
            for j in range(a.a.n):
                ap.e[i+n1*j].final = self.a.e[i].final and a.a.e[j].final

        # complementary of a in self
        cdef Automaton ap2
        sig_on()
        ap2 = CopyAutomaton(ap, ap.n, ap.na)
        sig_off()
        # set final states
        for i in range(n1):
            for j in range(a.a.n):
                ap2.e[i+n1*j].final = self.a.e[i].final and not a.a.e[j].final

        r.a[0] = ap
        r.A = Av
        r2.a[0] = ap2
        r2.A = Av
        return [r.emonde().minimise(), r2.emonde().minimise()]

    # modify the automaton to recognize the langage shifted by a (letter given by its index)
    def shift1OP(self, int a, verb=False):
        """
        Shift the automaton to recognize the language shifted
        by ``a`` (letter given by its index)

        INPUT:

        - ``a`` -- int  index of letter to shift
        - ``verb`` -- boolean (default: ``False``) fix
          to ``True`` for activation the verbose mode

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: a.initial_state
            0
            sage: a.shift1OP(0, verb=True)
            sage: a.initial_state
            1
        """
        if self.a.i != -1:
            self.a.i = self.a.e[self.a.i].f[a]

    # modify the automaton to recognize the langage shifted by a (letter given by its index)
    def shiftOP(self, a, int np, verb=False):
        """
        Shift the automaton to recognize the language shifted ``np``
        by a (letter given by its index)

        INPUT:

        - ``a`` -- int  index of letter to shift
        - ``np`` -- int  number of shift
        - ``verb`` -- boolean (default: ``False``) fix
          to ``True`` for activation the verbose mode

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: a.initial_state
            0
            sage: a.shiftOP(0, 2)
            sage: a.initial_state
            -1
        """
        for i in range(np):
            if self.a.i != -1:
                self.a.i = self.a.e[self.a.i].f[a]

    def unshift1(self, a, final=False):
        """
        Unshift the automaton to recognize the language shifted
        by ``a`` (letter given by its index)

        INPUT:

        - ``a`` -- int  index of letter to shift
        - ``verb`` -- boolean (default: ``False``) fix
          to ``True`` for activation the verbose mode

        OUTPUT:

        Return a unshifted :class:`FastAutomaton`

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: a.initial_state
            0
            sage: a.unshift1(1)
            FastAutomaton with 5 states and an alphabet of 2 letters
        """
        r = FastAutomaton(None)
        cdef Automaton aut
        sig_on()
        aut = CopyAutomaton(self.a[0], self.a.n+1, self.a.na)
        sig_off()
        cdef int i
        cdef int ne = self.a.n
        for i in range(aut.na):
            aut.e[ne].f[i] = -1
        aut.e[ne].f[a] = self.a.i
        aut.e[ne].final = final
        aut.i = ne
        r.a[0] = aut
        r.A = self.A
        return r

    # this function could be written in a more efficient way
    def unshiftl(self, l):
        """

        INPUT:

        - ``l`` -- list  of index of letter to shift

        OUTPUT:

        Return a unshifted  :class:`FastAutomaton`

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: a.initial_state
            0
            sage: a.shiftOP(0, 2)
            sage: a.unshiftl([0, 1])
            FastAutomaton with 6 states and an alphabet of 2 letters
        """
        a = self
        l.reverse()
        for i in l:
            a = a.unshift1(i)
        l.reverse()
        return a

    def unshift(self, int a, int np, final=None):
        """
        Unshift :class:`FastAutomaton`

        INPUT:

        - ``a`` -- int  
        - ``np``  --  int  
        - ``final`` -- (default: ``None``) if final or not

        OUTPUT:

        Return a unshifted :class:`FastAutomaton`

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: a.unshift(0, 2)
            FastAutomaton with 6 states and an alphabet of 2 letters
        """
        if np == 0:
            return self
        if final is None:
            if self.a.i == -1:
                r = FastAutomaton(None)
                r.A = self.A
                return r
            final = self.a.e[self.a.i].final
        r = FastAutomaton(None)
        cdef Automaton aut
        sig_on()
        aut = CopyAutomaton(self.a[0], self.a.n+np, self.a.na)
        sig_off()
        cdef int i
        cdef int ne = self.a.n
        for j in range(np):
            for i in range(aut.na):
                aut.e[ne+j].f[i] = -1
            if j > 0:
                aut.e[ne+j].f[a] = ne+j-1
            else:
                aut.e[ne+j].f[a] = self.a.i
            aut.e[ne+j].final = final
        aut.i = ne+np-1
        r.a[0] = aut
        r.A = self.A
        return r

    def copyn(self, NFastAutomaton r, verb=False):
        """
        Convert  a determinist automaton :class:`FastAutomaton` to
        a non determinist automaton :class:`NFastAutomaton`

        INPUT:

        - ``verb`` -- boolean (default: ``False``) fix
          to ``True`` for activation the verbose mode
        - ``r`` -- :class:`NFastAutomaton` to replace

        OUTPUT:

        Return the :class:`NFastAutomaton` copy like of the :class:`FastAutomaton`

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: b = NFastAutomaton(a)
            sage: a.copyn(b)
            NFastAutomaton with 4 states and an alphabet of 2 letters
        """
        cdef NAutomaton a
        sig_on()
        a = CopyN(self.a[0], verb)
        sig_off()
        r.a[0] = a
        r.A = self.A
        return r

    def concat(self, FastAutomaton b, det=True, verb=False):
        """
        Concatenates :class:`FastAutomaton`, ``b``

        INPUT:

        - ``b`` -- :class:`FastAutomaton`  to concatenate
        - ``det``  -- (default: ``true``) determinist flag
          for return automaton
        - ``verb`` -- boolean (default: ``False``) fix
          to ``True`` for activation the verbose mode

        OUTPUT:

        Return a concatenated :class:`NFastAutomaton` (``det``=``False``)
        or  :class:`FastAutomaton` (``det``=``True``)

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: b = FastAutomaton([(3, 2, 'a'), (1, 2, 'd')], i=2)
            sage: a.concat(b)
            FastAutomaton with 3 states and an alphabet of 3 letters
            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: a.concat(b, det=False)
            NFastAutomaton with 7 states and an alphabet of 3 letters
        """
        cdef FastAutomaton a
        if self.A != b.A:
            A = list(set(self.A).union(set(b.A)))
            if verb:
                print("Alphabet Changing (%s, %s -> %s)..." %(self.A, b.A, A))
            a = self.bigger_alphabet(A)
            b = b.bigger_alphabet(A)
            # raise ValueError("Error : concatenation of automaton having differents alphabets.")
        else:
            a = self
            A = self.A
        if verb:
            print("a=%s (A=%s)\nb=%s (A=%s)" % (a, a.A, b, b.A))
        cdef NAutomaton na
        r = NFastAutomaton(None)
        sig_on()
        na = Concat(a.a[0], b.a[0], verb)
        sig_off()
        r.a[0] = na
        r.A = A

        if det:
            # "Determinise et simplifie...")
            if verb:
                print("Determinist and simplified...")
            return r.determinise().emonde().minimise()
        else:
            return r

    def proj(self, dict d, det=True, verb=False):
        """
        Projection following the image of dictionary ``d``

        INPUT:

        - ``d`` -- dictionary to determine projection
        - ``det``  --  (default: ``true``) determinist flag
          for return automaton
        - ``verb`` -- boolean (default: ``False``) fix
          to ``True`` for activation the verbose mode

        OUTPUT:

        Return a new projected :class:`NFastAutomaton` (``det``=``False``)
        or  :class:`FastAutomaton` (``det``=``True``)

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: d = { 'a' : 'a', 'b': 'c', 'c':'c', 'd':'b'}
            sage: a.proj(d)
            FastAutomaton with 2 states and an alphabet of 2 letters
        """
        cdef NAutomaton a
        cdef Dict dC
        r = NFastAutomaton(None)
        A2 = []
        sig_on()
        d1 = imagDict(d, self.A, A2=A2)
        sig_off()
        if verb:
            print("d1=%s, A2=%s" % (d1, A2))
        sig_on()
        dC = getDict(d, self.A, d1=d1)
        a = Proj(self.a[0], dC, verb)
        FreeDict(&dC)
        sig_off()
        r.a[0] = a
        r.A = A2
        if det:
            return r.determinise().emonde().minimise()
        else:
            return r

    def proji(self, int i, det=True, verb=False):
        """
        Projection on one letter of the alphabet label.

        INPUT:

        - ``i`` -- int index of the label projection
        - ``det``  --  (default: ``true``) determinist flag
          for return automaton
        - ``verb`` -- boolean (default: ``False``) fix
          to ``True`` for activation the verbose mode

        OUTPUT:

        Return a new projected :class:`NFastAutomaton` (``det``=``False``)
        or  :class:`FastAutomaton` (``det``=``True``)


        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: a.proji(0)
            FastAutomaton with 2 states and an alphabet of 2 letters
        """
        d = {}
        for l in self.A:
            if i < len(l):
                d[l] = l[i]
            else:
                raise ValueError("index i %d must be smaller then label size  %d" % (i, len(l)))
        return self.proj(d, det=det, verb=verb)

    def determinise_proj(self, d, noempty=True,
                         onlyfinals=False, nof=False, verb=False):
        """
        Projection following the image of dictonary ``d``

        INPUT:

        - ``d`` -- dictionary to determine projection
        - ``noempty``  -- (default: ``True``)
        - ``onlyfinals``  -- (default: ``False``)
        - ``nof``  -- (default: ``False``)
        - ``verb`` -- boolean (default: ``False``) fix
          to ``True`` for activation the verbose mode

        OUTPUT:

        Return a new projected  :class:`FastAutomaton`

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: d = { 'a' : 'a', 'b': 'c', 'c':'c', 'd':'b'}
            sage: a.determinise_proj(d)
            FastAutomaton with 2 states and an alphabet of 2 letters
        """
        cdef Automaton a
        cdef Dict dC
        if noempty and not onlyfinals and not nof:
            return self.proj(d=d, verb=verb)
        else:
            r = FastAutomaton(None)
            A2 = []
            sig_on()
            d1 = imagDict(d, self.A, A2=A2)
            if verb:
                print("d1=%s, A2=%s" % (d1, A2))
            dC = getDict(d, self.A, d1=d1)
            a = Determinise(self.a[0], dC, noempty, onlyfinals, nof, verb)
            FreeDict(&dC)
            sig_off()
            # FreeAutomaton(self.a[0])
            r.a[0] = a
            r.A = A2
            return r

    # change les lettres selon d, en dupliquant les arêtes si nécessaire
    # the result is assumed deterministic !!!
    def duplicate(self, d, verb=False):
        """
        Change letters according to dictionnary ``d``, with duplication of edge
        if necessary, the result is assumed deterministic !!!

        INPUT:

        - ``d``  -- dictionary for relabel
        - ``verb`` -- boolean (default: ``False``) fix to ``True`` for activation
          the verbose mode

        OUTPUT:

        Return a new :class:`FastAutomaton` with new letters

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: d = { 'a' : 'a', 'b': 'c', 'c':'c', 'd':'b'}
            sage: b = a.duplicate(d)
            sage: b.Alphabet
            ['a', 'c']
        """
        cdef Automaton a
        cdef InvertDict dC
        r = FastAutomaton(None)
        A2 = []
        sig_on()
        d1 = imagDict2(d, self.A, A2=A2)
        if verb:
            print("d1=%s, A2=%s" % (d1, A2))
        dC = getDict2(d, self.A, d1=d1)
        if verb:
            printInvertDict(dC)
        a = Duplicate(self.a[0], dC, len(A2), verb)
        if verb:
            print("end...")
        FreeInvertDict(dC)
        sig_off()
        r.a[0] = a
        r.A = A2
        return r

    # change les lettres
    # le dictionnaire est supposé bijectif de A dans le nouvel alphabet
    # opération sur place !
    def relabel(self, d):
        """
        Change letters of the :class:`FastAutomaton`, the dictionary is assumed to be bijectif form A
        to the new alphabet

        INPUT:

         - ``d``  -- dictionary for relabel

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: d = { 'a' : 'a', 'b': 'c', 'c':'b', 'd':'b'}
            sage: a.relabel(d)
            sage: a.Alphabet
            ['a', 'c']
        """
        self.A = [d[c] for c in self.A]

    # permute les lettres
    # A = liste des lettres dans le nouvel ordre (il peut y en avoir moins)
    def permut(self, list A, verb=False):
        """
        Permutes letters and return permuted new :class:`FastAutomaton`

        INPUT:

         - ``A``  -- list of letters in the new order (number can be less to the Alphabet)
         - ``verb`` -- boolean (default: ``False``) fix to ``True`` for activation
           the verbose mode

        OUTPUT:

        Return permuted new :class:`FastAutomaton`

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: l = [ 'b', 'c', 'a']
            sage: b = a.permut(l, verb=True)
            A=['b', 'c', 'a']
            l=[ 1 -1 0 ]
            l = [ 1 -1 0 ]
            sage: b.Alphabet
            ['b', 'c', 'a']

        """
        if verb:
            print("A=%s" % A)
        cdef Automaton a
        r = FastAutomaton(None)
        cdef int *l = <int*>malloc(sizeof(int) * len(A))
        cdef int i
        for i in range(self.a.na):
            l[i] = -1
        d = {}
        for i, c in enumerate(self.A):
            d[c] = i
        for i, c in enumerate(A):
            if d.has_key(c):
                l[i] = d[c]  # l gives the old index from the new one
        if verb:
            str = "l=["
            for i in range(len(A)):
                str += " %s" % l[i]
            str += " ]"
            print(str)
        sig_on()
        a = Permut(self.a[0], l, len(A), verb)
        sig_off()
        free(l)
        r.a[0] = a
        r.A = A

        return r

    # permute les lettres SUR PLACE
    # A = liste des lettres dans le nouvel ordre (il peut y en avoir moins)
    def permut_op(self, list A, verb=False):
        """
        Permute letters on the :class:`FastAutomaton`

        INPUT:

         - ``A``  -- list of letters in the new order (number can be less to the Alphabet)
         - ``verb`` -- boolean (default: ``False``) fix to ``True`` for activation
           the verbose mode

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: a.Alphabet
            ['a', 'b']
            sage: l = [ 'b', 'c', 'a']
            sage: a.permut_op(l, verb=True)
            A=['b', 'c', 'a']
            l=[ 1 -1 0 ]
            l = [ 1 -1 0 ]
            sage: a.Alphabet
            ['b', 'c', 'a']

        """
        if verb:
            print("A=%s" % A)
        cdef int *l = <int*>malloc(sizeof(int) * len(A))
        cdef int i
        for i in range(self.a.na):
            l[i] = -1
        d = {}
        for i, c in enumerate(self.A):
            d[c] = i
        for i, c in enumerate(A):
            if d.has_key(c):
                l[i] = d[c]  # l gives the old index from the new one
        if verb:
            str = "l=["
            for i in range(len(A)):
                str += " %s" % l[i]
            str += " ]"
            print(str)
        sig_on()
        PermutOP(self.a[0], l, len(A), verb)
        free(l)
        sig_off()
        self.A = A

    # Compute the transposition, assuming it is deterministic
    def transpose_det(self):
        """
        Transposes :class:`FastAutomaton` and  assumes it is deterministic

        OUTPUT:

        Return the transposed :class:`FastAutomaton`

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: a.transpose_det()
            FastAutomaton with 4 states and an alphabet of 2 letters

        """
        r = FastAutomaton(None)
        sig_on()
        r.a[0] = TransposeDet(self.a[0])
        r.A = self.A
        sig_off()
        return r

    def transpose(self):
        """
        Transpose :class:`FastAutomaton` and return a ``NFastAutomaton``

        OUTPUT:

        Return the transposed :class:`NFastAutomaton`

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: a.transpose()
            NFastAutomaton with 4 states and an alphabet of 2 letters
        """
        r = NFastAutomaton(None)
        sig_on()
        r.a[0] = Transpose(self.a[0])
        r.A = self.A
        sig_off()
        return r

    def strongly_connected_components(self, no_trivials=False):
        """
        Determine strongly connected components

        INPUT:

        - ``no_trivials`` -- (default: ``False``) if  components
          are strongly connected by non trivial links

        OUTPUT:

        Return list of list of strongly connected components

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: a.strongly_connected_components()
            [[1], [0], [3], [2]]
        """
        cdef int* l = <int*>malloc(sizeof(int) * self.a.n)
        sig_on()
        cdef int ncc = StronglyConnectedComponents(self.a[0], l)
        sig_off()
        # inverse la liste
        l2 = {}
        cdef int i
        for i in range(self.a.n):
            if not l2.has_key(l[i]):
                l2[l[i]] = []
            l2[l[i]].append(i)
        if no_trivials:
            for i in l2.keys():
                if len(l2[i]) == 1:
                    trivial = True
                    for j in range(len(self.A)):
                        if self.a.e[l2[i][0]].f[j] == l2[i][0]:
                            trivial = False
                            break
                    if trivial:
                        # on retire cette composante qui est triviale
                        l2.pop(i)
        free(l)
        return l2.values()

    def acc_and_coacc(self):
        """
        Determine accessible and coaccessible states

        OUTPUT:

        Return list accessible and coaccessible states

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: a.acc_and_coacc()
            [0, 1]
        """
        sig_on()
        cdef int* l = <int*>malloc(sizeof(int) * self.a.n)
        AccCoAcc(self.a, l)
        sig_off()
        return [i for i in range(self.a.n) if l[i] == 1]

    def coaccessible_states(self):
        """
        Compute the co-accessible states of the :class:`FastAutomaton`

        OUTPUT:

        Return list of  co-accessible states of the :class:`FastAutomaton`

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: a.coaccessible_states()
            [0, 1, 2, 3]
        """
        sig_on()
        cdef int* l = <int*>malloc(sizeof(int) * self.a.n)
        CoAcc(self.a, l)
        sig_off()
        return [i for i in range(self.a.n) if l[i] == 1]

    def sub_automaton(self, l, verb=False):
        """
        Compute a sub automaton

        INPUT:

         - ``l``  -- list of states to keep
         - ``verb`` -- boolean (default: ``False``) fix to ``True`` for activation
          the verbose mode

        OUTPUT:

        Return a  :class:`FastAutomaton` sub automaton

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: l = [0, 1]
            sage: a.sub_automaton(l)
            FastAutomaton with 2 states and an alphabet of 2 letters
            sage: a
            FastAutomaton with 4 states and an alphabet of 2 letters
        """
        sig_on()
        r = FastAutomaton(None)
        r.a[0] = SubAutomaton(self.a[0], list_to_Dict(l), verb)
        r.A = self.A
        sig_off()
        return r

    def minimise(self, verb=False):
        """
        Compute a minimized automaton
        minimisation by Hopcroft's algorithm
        see [Hopcroft]

        INPUT:

         - ``verb`` -- boolean (default: ``False``) fix to ``True`` for activation
           the verbose mode


        OUTPUT:

        Return a minimized :class:`FastAutomaton` automaton

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: a.minimise(True)
            transition i[0][0] = [ ]
            transition i[0][1] = [ ]
            transition i[1][0] = [ 0 ]
            transition i[1][1] = [ ]
            transition i[2][0] = [ ]
            transition i[2][1] = [ ]
            transition i[3][0] = [ ]
            transition i[3][1] = [ 2 ]
            transition i[4][0] = [ 1 2 3 4 ]
            transition i[4][1] = [ 0 1 3 4 ]
            partition = [ 0 1 2 3 4 ]
            partitioni = [ 0 1 2 3 4 ]
            Initial partition :
            class 0 : 0 1 2 3
            class 1 : 4
            split 1 0...
            new visited class : 0 (1 parent of 4)
            re-visited class : 0 (2 parent of 4)
            re-visited class : 0 (3 parent of 4)
            new visited class : 1 (4 parent of 4)
            class 0 : 1 2 3 0
            class 1 : 4
            2 class encountered
            class 0 : l = 0 3 4 = h
            class 1 : l = 4 5 5 = h
            split 1 1...
            new visited class : 2 (0 parent of 4)
            new visited class : 0 (1 parent of 4)
            re-visited class : 0 (3 parent of 4)
            new visited class : 1 (4 parent of 4)
            class 0 : 1 3 2
            class 1 : 4
            class 2 : 0
            3 class encountered
            class 2 : l = 3 4 4 = h
            class 0 : l = 0 2 3 = h
            class 1 : l = 4 5 5 = h
            split 3 0...
            class 0 : 1 3
            class 1 : 4
            class 2 : 0
            class 3 : 2
            0 class encountered
            split 3 1...
            class 0 : 1 3
            class 1 : 4
            class 2 : 0
            class 3 : 2
            0 class encountered
            split 2 0...
            class 0 : 1 3
            class 1 : 4
            class 2 : 0
            class 3 : 2
            0 class encountered
            split 2 1...
            class 0 : 1 3
            class 1 : 4
            class 2 : 0
            class 3 : 2
            0 class encountered
            Final partition :
            class 0 : 1 3
            class 1 : 4
            class 2 : 0
            class 3 : 2
            a.i = 0 class 2
            removes the hole state  1...
            FastAutomaton with 3 states and an alphabet of 2 letters
        """
        sig_on()
        r = FastAutomaton(None)
        r.a[0] = Minimise(self.a[0], verb)
        r.A = self.A
        sig_off()
        return r

    def adjacency_matrix(self, sparse=None):
        """
        Compute the corresponded adjacency matrix

        INPUT:

        - ``sparse`` -- indicate if the return matrix is sparse or not
          if ``sparse``

        OUTPUT:

        Return the corresponded adjacency matrix

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: a.adjacency_matrix()
            [0 1 0 0]
            [0 0 0 0]
            [0 0 0 1]
            [0 0 0 0]
        """
        if sparse is None:
            if self.a.n <= 128:
                sparse = False
            else:
                sparse = True

        d = {}
        cdef int i, j, f
        for i in range(self.a.n):
            for j in range(self.a.na):
                f = self.a.e[i].f[j]
                if f != -1:
                    if d.has_key((i,f)):
                        d[(i, f)] += 1
                    else:
                        d[(i, f)] = 1
        from sage.matrix.constructor import matrix
        from sage.rings.integer_ring import IntegerRing
        return matrix(IntegerRing(), self.a.n, self.a.n, d, sparse=sparse)

    def delete_vertex(self, int i):
        """
        Delete vertex with copy

        INPUT:

        - ``i``  -- int number of vertex to remove

        OUTPUT:

        Return a copy of :class:`FastAutomaton` with deleted vertex

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: a.delete_vertex(2)
            FastAutomaton with 3 states and an alphabet of 2 letters

        """
        sig_on()
        r = FastAutomaton(None)
        r.a[0] = DeleteVertex(self.a[0], i)
        r.A = self.A
        sig_off()
        return r

    def delete_vertex_op(self, int i):
        """
        Delete vertex

        INPUT:

        - ``i``  -- int number of vertex to remove

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: a.delete_vertex_op(2)
            sage: a
            FastAutomaton with 3 states and an alphabet of 2 letters

        """
        sig_on()
        DeleteVertexOP(self.a, i)
        sig_off()

    def spectral_radius(self, only_non_trivial=False, verb=False):
        """
        Return spectral radius of strongly connex component

        INPUT:

        - ``only_non_trivial``  -- (default: ``False``) if non trivial spectral
          radius is required
        - ``verb`` -- boolean (default: ``False``) fix to ``True`` for activation
          the verbose mode

        OUTPUT:

        Return spectral radius of strongly connex component

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: a.spectral_radius(only_non_trivial=False, verb=True)
            minimal Automata : FastAutomaton with 3 states and an alphabet of 2 letters
            3 component strongly connex.
            component with 1 states...
            x
            (x, 1)
            component with 1 states...
            x
            (x, 1)
            component with 1 states...
            x
            (x, 1)
            0

        """
        a = self.minimise()
        if verb:
            print("minimal Automata : %s" % a)
        l = a.strongly_connected_components()
        if verb:
            print("%s component strongly connex." % len(l))
        r = 0 # valeur propre maximale trouvée
        for c in l:
            if not only_non_trivial or len(c) > 1:
                if verb:
                    print("component with %s states..." % len(c))
                b = a.sub_automaton(c)
                m = b.adjacency_matrix()
                cp = m.charpoly()
                fs = cp.factor()
                if verb:
                    print(fs)
                for f in fs:
                    if verb:
                        print(f)
                    from sage.functions.other import real_part
                    from sage.rings.qqbar import AlgebraicRealField
                    r = max([ro[0] for ro in f[0].roots(ring=AlgebraicRealField())] + [r])
        return r

    def test(self):
        """
        Test size of automaton structure

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: a.test()
            sizeof(Automaton)=24

        """
        sig_on()
        Test()
        sig_off()

    def copy(self):
        """
        Do a copy of the :class:`FastAutomaton`.

        OUTPUT:

        Return a copy of the :class:`FastAutomaton`

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: a.copy()
            FastAutomaton with 4 states and an alphabet of 2 letters

        """
        r = FastAutomaton(None)
        sig_on()
        r.a[0] = CopyAutomaton(self.a[0], self.a.n, self.a.na)
        sig_off()
        r.A = self.A
        return r

    def has_empty_langage(self):
        """
        Test if the  :class:`FastAutomaton` has a empty language

        OUTPUT:

        Return ``True`` the :class:`FastAutomaton` has a empty language
        ``False`` if not

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: a.has_empty_langage()
            False

        """
        sig_on()
        res = emptyLangage(self.a[0])
        sig_off()
        return Bool(res)

    def equals_langages(self, FastAutomaton a2, minimized=False, emonded=False, verb=False):
        """
        Test if the  :class:`FastAutomaton` language are equal or not to
        :class:`FastAutomaton`  ``a2``

        INPUT:

        - ``a2``  -- the :class:`Fastautomaton` to compare
        - ``minimized``  -- (default: ``False``) if minimization is
          required or not
        - ``emonded``  -- (default: ``False``) if emaondation if require or not
        - ``verb`` -- boolean (default: ``False``) fix to ``True`` for activation
          the verbose mode

        OUTPUT:

        Return ``True`` if the both :class:`FastAutomaton` have
        the same language ``False`` if not

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: b = FastAutomaton([(3, 2, 'a'), (1, 2, 'd')], i=2)
            sage: c = FastAutomaton([(3, 2, 'd'), (1, 2, 'c')], i=2)
            sage: a.equals_langages(b)
            True
            sage: a.equals_langages(c)
            False
        """
        sig_on()
        cdef Dict d = NewDict(self.a.na)
        cdef int i, j
        for i in range(self.a.na):
            for j in range(a2.a.na):
                if self.A[i] == a2.A[j]:
                    d.e[i] = j
                    if verb:
                        print("%d -> %d"%(i, j))
                    break
        if verb:
            printDict(d)
        res = equalsLangages(self.a, a2.a, d, minimized, emonded, verb)
        sig_off()
        return Bool(res)

#    def empty_product (self, FastAutomaton a2, d=None, verb=False):
#        if d is None:
#            return self.has_empty_langage() or a2.has_empty_langage()
#        sig_on()
#        cdef Dict dC
#        Av = []
#        dv = imagProductDict(d, self.A, a2.A, Av=Av)
#        if verb:
#            print("Av=%s"%Av
#            print("dv=%s"%dv
#        dC = getProductDict(d, self.A, a2.A, dv=dv, verb=verb)
#        if verb:
#            print("dC="
#            printDict(dC)
#        res = EmptyProduct(self.a[0], a2.a[0], dC, verb)
#        sig_off()
#        return Bool(res)

    def intersect(self, FastAutomaton a2, bool verb=False):
        """
        Compute if the  :class:`FastAutomaton` element  intersert
        :class:`FastAutomaton` ``a2``

        INPUT:

        -  ``a2``  -- the :class:`Fastautomaton` to intersect
        - ``verb`` -- boolean (default: ``False``) True to active
          the verbose mode

        OUTPUT:

        Return ``True`` if the both :class:`FastAutomaton` have
        intersection ``False`` if not

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: b = FastAutomaton([(3, 2, 'a'), (1, 2, 'd')], i=2)
            sage: a.intersect(b)
            True
        """
        sig_on()
        res = Intersect(self.a[0], a2.a[0], verb)
        sig_off()
        return Bool(res)

#    def intersect (self, FastAutomaton a2, emonded=False, verb=False):
#        sig_on()
#        cdef Dict d = NewDict(self.a.na)
#        cdef int i,j
#        for i in range(self.a.na):
#            for j in range(a2.a.na):
#                if self.A[i] == a2.A[j]:
#                    d.e[i] = j
#                    if verb: print("%d -> %d"%(i, j))
#                    break
#        if verb:
#            printDict(d)
#        res = intersectLangage(self.a, a2.a, d, emonded, verb)
#        sig_off()
#        return Bool(res)

    def find_word(self, bool verb=False):
        """
        Find a word of the language of the automaton

        INPUT:

        - ``verb`` -- (default: ``False``)  the verbose parameter

        OUTPUT:

        return a word of the language of Automaton  as list of word

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: a.find_word()
            []
        """
        sig_on()
        cdef Dict w
        res = findWord(self.a[0], &w, verb)
        sig_off()
        if not res:
            return None
        r = []
        for i in range(w.n):
            r.append(self.A[w.e[i]])
        sig_on()
        FreeDict(&w)
        sig_off()
        return r

    def shortest_word(self, i=None, f=None, bool verb=False):
        """
        Compute the shortest words of the automaton

        INPUT:

        - ``i`` -- (default: None)  the initial state
        - ``f`` -- (default: None)  the final state
        - ``verb`` -- (default: False)  the verbose parameter

        OUTPUT:

        return a list of word

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: a.shortest_word(i=2, f=1)
            []
        """
        cdef Dict w
        if i is None:
            i = self.a.i
        if f is None:
            f = -1
        sig_on()
        res = shortestWord(self.a[0], &w, i, f, verb)
        sig_off()
        if not res:
            return None
        r = []
        for i in range(w.n):
            r.append(self.A[w.e[i]])
        sig_on()
        FreeDict(&w)
        sig_off()
        return r

    def shortest_words(self, i=None, verb=False):
        """
        Compute the shortest words of the automaton

        INPUT:

        - ``i`` -- (default: None)  the initial state
        - ``verb`` -- (default: False)  the verbose parameter

        OUTPUT:

        return 1 if the word is recognized (i.e. 0)

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: a.shortest_words()
            [[], ['a'], [], []]

        """
        cdef Dict* w = <Dict*>malloc(sizeof(Dict) * self.a.n)
        if i is None:
            i = self.a.i
        sig_on()
        res = shortestWords(self.a[0], w, i, verb)
        sig_off()
        if not res:
            return None
        rt = []
        for j in range(self.a.n):
            r = []
            for i in range(w[j].n):
                r.append(self.A[w[j].e[i]])
            rt.append(r)
            sig_on()
            FreeDict(&w[j])
            sig_off()
        free(w)
        return rt

    # determine if the word is recognized by the automaton or not
    def rec_word2(self, list w):
        """
        Determine if the word ``w`` is recognized or nor not by the automaton

        INPUT:

        - ``w`` -- a list of letters

        OUTPUT:

        return 1 if the word is recognized (i.e. 0)

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: w = ['a', 'b', 'b']
            sage: a.rec_word2(w)
            0

        """
        rd = {}
        for i, a in enumerate(self.A):
            rd[a] = i
        sig_on()
        cdef Dict d = NewDict(len(w))
        cdef bool res
        for i, a in enumerate(w):
            d.e[i] = rd[a]
        res = rec_word(self.a[0], d)
        sig_off()
        return res

    # determine if the word is recognized by the automaton or not
    def rec_word(self, list w):
        """
        Determine if the word ``w`` is recognized or nor not by the automaton

        INPUT:

        - ``w`` -- a list of letters

        OUTPUT:

        return ``True`` if the word is recognized (i.e. ``False``)

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: w = ['a', 'b', 'b']
            sage: a.rec_word(w)
            False


        """
        cdef int e = self.a.i
        if e == -1:
            return False
        d = {}
        for i, a in enumerate(self.A):
            d[a] = i
        for a in w:
            e = self.a.e[e].f[d[a]]
            if e == -1:
                return False
        return Bool(self.a.e[e].final)

    def add_state(self, bool final):
        """
        Add a state in the automaton

        INPUT:

        - ``final`` -- boolean indicate if the added state is final

        OUTPUT:

        return the numbers of states

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: a.add_state(True)
            4
            sage: a.add_state(False)
            5
        """
        sig_on()
        AddEtat(self.a, final)
        sig_off()
        return self.a.n-1

    def add_edge(self, int i, l, int j):
        """
        Add a edge in the automaton

        INPUT:

        - ``i`` -- int the first state
        - ``l`` -- the label of edge
        - ``j`` -- int  the second state

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: a.add_edge(2,'a',1)

            sage: a.add_edge(2,'v',1)
            Traceback (most recent call last):
            ...
            ValueError: The letter v doesn't exist.
            sage: a.add_edge(2,'v',6)
            Traceback (most recent call last):
            ...
            ValueError: The state  6 doesn't exist.
            sage: a.add_edge(5,'v',6)
            Traceback (most recent call last):
            ...
            ValueError: The state  5 doesn't exist.
        """
        if i >= self.a.n:
            raise ValueError("The state %s doesn't exist."% i)
        if j >= self.a.n:
            raise ValueError("The state  %s doesn't exist."%j)
        try:
            k = self.A.index(l)
        except:
            # La lettre %s n'existe pas.
            raise ValueError("The letter %s doesn't exist." % l)
        self.a.e[i].f[k] = j

    @property
    def n_states(self):
        """
        return the numbers of states

        OUTPUT:

        return the numbers of states

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: a.n_states
            4
        """
        return self.a.n

    def bigger_alphabet(self, nA):
        """
        Computes new automaton :class:`FastAutomaton` with a bigger alphabet

        INPUT:

        - ``na`` --  number of letter for the new automaton

        OUTPUT:

        return a :class:`FastAutomaton` with a bigger alphabet of ``nA`` letters

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: a.bigger_alphabet(['a','b','c'])
            FastAutomaton with 4 states and an alphabet of 3 letters
        """
        cdef Dict d
        r = FastAutomaton(None)
        sig_on()
        d = NewDict(self.a.na)
        for i in range(self.a.na):
            d.e[i] = nA.index(self.A[i])
        r.a[0] = BiggerAlphabet(self.a[0], d, len(nA))
        sig_off()
        r.A = nA
        return r

    def complementaryOP(self):
        """
        Return the complementary automaton (with no copy erase ``self``).

        OUTPUT:

        return  a new automaton complementary of ``seff``

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: a.complementaryOP()

        """
        self.complete()
        cdef i
        for i in range(self.a.n):
            self.a.e[i].final = not self.a.e[i].final

    def complementary(self):
        """
        Computes the complementary automaton with copy.

        OUTPUT:

        return  a new automaton complementary of ``seff``

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: a.complementary()
            FastAutomaton with 5 states and an alphabet of 2 letters
        """
        a = self.copy()
        a.complementaryOP()
        return a

    def included(self, FastAutomaton a, bool verb=False, emonded=False):
        """
        test if automaton ``a`` is included

        INPUT:

        - ``a`` --  a :class:`FastAutomaton` to test
        - ``verb`` -- (default: False) verbose parameter
        - ``emonded`` -- (default: False) emandation parameter

        OUTPUT:

        return  ``True`` if automaton ``a`` is included (i.e. ``False`` if not)

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: a.complementaryOP()

        """
        cdef FastAutomaton b
        if self.A != a.A:
            b = self.bigger_alphabet(a.A)
        else:
            b = self
        sig_on()
        res = Included(b.a[0], a.a[0], emonded, verb)
        sig_off()
        return Bool(res)

#        d = {}
#        for l in self.A:
#            if l in a.A:
#                d[(l,l)] = l
#        if verb:
#            print("d=%s"%d)
#        a.complete()
#        cdef FastAutomaton p = self.product(a, d, verb=verb)
#
#        #set final states
#        cdef int i,j
#        cdef n1 = self.a.n
#        for i in range(n1):
#            for j in range(a.a.n):
#                p.a.e[i+n1*j].final = self.a.e[i].final and not a.a.e[j].final
#
#        if step == 1:
#            return p;
#
#        return p.has_empty_langage()

    # donne un automate reconnaissant w(w^(-1)L) où L est le langage
    # de a partant de e
    def piece(self, w, e=None):
        """
        return a automaton recognizing ``w`` as :math:`w (w^{-1}L)` where ``L``
        is the language of automaton a from e entry state

        INPUT:

        - ``w`` --  word
        - ``e`` -- (default: None) the entry state

        OUTPUT:

        return  a automaton recognizing ``w``

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: a.piece([1])
            FastAutomaton with 0 states and an alphabet of 2 letters

        """
        cdef int* l = <int*>malloc(sizeof(int)*self.a.n)
        cdef int i
        if type(w) != list:
            w = [int(w)]
        for i in range(len(w)):
            l[i] = w[i]
        if e is None:
            e = self.a.i
        r = FastAutomaton(None)
        sig_on()
        r.a[0] = PieceAutomaton(self.a[0], l, len(w), e)
        sig_off()
        free(l)
        r.A = self.A
        return r

    # tell if the language of the automaton is empty
    # (this function is not very efficient)
    def is_empty(self):
        """
        Examines if the language of the automaton is empty

        OUTPUT:

        return ``True``  if automaton is empty or ``False`` is not

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
            sage: a.is_empty()
            False

        """
        return (self.find_word() is None)

    def random_word(self, nmin=-1, nmax=100):
        """
        return a random word

        INPUT:

        - ``nmin`` -- (default: -1) n min value
        - ``nmax`` -- (default: 100) n max value

        OUTPUT:

        return a random word

        EXAMPLES::

            sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b'), (0, 3, 'c')], i=0)
            sage: a.random_word() # random
            ['a']


        """
        cdef int i = self.a.i
        w = []
        na = len(self.A)
        if nmin < 0:
            nmin = 1
        from sage.misc.prandom import random
        for j in range(nmin):
            li = [l for l in range(na) if self.succ(i, l) != -1]
            l = li[(int)(random() * len(li))]
            w.append(self.A[l])
            i = self.succ(i, l)
        # continue the word to get into a final state
        for j in range(nmax-nmin):
            if self.a.e[i].final:
                break
            li = [l for l in range(na) if self.succ(i, l) != -1]
            l = li[(int)(random() * len(li))]
            w.append(self.A[l])
            i = self.succ(i, l)
        if not self.a.e[i].final:
            print("word not found !")  # "Mot non trouvé !"
        return w
