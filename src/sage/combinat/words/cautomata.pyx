# coding=utf8
"""
Finite state machines using C

AUTHORS:

- Paul Mercat
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
from cysignals.signals cimport sig_on, sig_off

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

#    Automaton NewAutomaton (int n, int na)
#    void FreeAutomaton (Automaton *a)
    int hashAutomaton(Automaton a)
    void FreeNAutomaton(NAutomaton *a)
    Automaton CopyAutomaton(Automaton a, int nalloc, int naalloc)
    Automaton PieceAutomaton(Automaton a, int *w, int n, int e)
    void init(Automaton *a)
    void printAutomaton(Automaton a)
    void plotTikZ(Automaton a, const char **labels, const char *graph_name, double sx, double sy, const char **vlabels, bool verb)
    void NplotTikZ(NAutomaton a, const char **labels, const char *graph_name, double sx, double sy)
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
    # print "d=%s, A=%s"%(d,A)
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
    # print d1
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


def TestAutomaton(a):
    """
    Test automaton print vertices and alphabet

    INPUT:

    - ``a`` automaton to test

    EXAMPLES::

        sage: a = DiGraph({a: [1,2,3], 1: [0,2], 2: [3], 3: [4], 4: [0,5], 5: [1]})
        sage: fa = FastAutomaton(a)
        ['(0,3)', '(2,3)', '(0,2)', '(1,2)', '(0,1)', '(4,5)', '(1,0)', '(4,0)', '(3,4)', '(5,1)']
        sage: TestAutomaton(fa)

    """
    cdef Automaton r
    # d = {}
    # da = {}
    r = getAutomaton(a)  # , d, da)
    printAutomaton(r)
    # print d, da, a.vertices(),
    print(list(a.Alphabet()))


def TestProduct(a1, a2, di):
    """
    Test and print the product of automaton

    INPUT:

    - ``a1`` first automaton term of product

    - ``a2`` second automaton term of product

    - ``di`` alphabet dictionnary

    """
    cdef Automaton a, b, c
    a = getAutomaton(a1)
    b = getAutomaton(a2)
    printAutomaton(a)
    print(a1.vertices(), a1.Alphabet())
    printAutomaton(b)
    print(a2.vertices(), a2.Alphabet())
    cdef Dict d
    d = getProductDict(di, list(a1.Alphabet()), list(a2.Alphabet()))
    print("product dictionnary :")  # "dictionnaire du produit :"
    printDict(d)
    c = Product(a, b, d, False)
    print("result :")  # "résultat :"
    printAutomaton(c)

#def TestDeterminise (a, d, noempty=True, verb=True):
#    cdef Dict di = getDict(d, a.Alphabet())
#    cdef Automaton au = getAutomaton(a)
#    if verb:
#        printDict(di)
#    if verb:
#        printAutomaton(au)
#    cdef Automaton r = Determinise(au, di, noempty, verb)
#    printAutomaton(r)

#def TestDeterminiseEmonde (a, d, noempty=True, verb=True):
#    cdef Dict di = getDict(d, a.Alphabet())
#    cdef Automaton au = getAutomaton(a)
#    if verb:
#        printDict(di)
#    if verb:
#        printAutomaton(au)
#    cdef Automaton r = Determinise(au, di, noempty, verb)
#    print "Avant émondation :"
#    printAutomaton(r)
#    cdef Automaton r2 = emonde_inf(r)
#    print "Après émondation :"
#    printAutomaton(r2)
#    if equalsAutomaton(r, r2):
#        print "equals !"
#    else:
#        print "differents !"


def TestEmonde(a, noempty=True, verb=True):
    cdef Automaton au = getAutomaton(a)
    if verb:
        print("bebore mondation :")  # Avant émondation :"
        printAutomaton(au)
    cdef Automaton r = emonde_inf(au, verb)
    if verb:
        print("After montation  :")
        printAutomaton(r)
    if equalsAutomaton(r, au):
        print("equal !")
    else:
        print("different !")
    return AutomatonGet(r)


cdef Automaton getAutomaton(a, initial=None, F=None, A=None):
    print("ds getAutomaton")
    sig_on()
    d = {}
    da = {}
    if F is None:
        if not hasattr(a, 'F'):
            F = a.vertices()
        else:
            F = a.F
    cdef Automaton r
    print("ds getAutomaton 2")
    if A is None:
        A = list(a.Alphabet())
    V = list(a.vertices())
    cdef int n = len(V)
    cdef int na = len(A)
    r = NewAutomaton(n, na)
    print("ds getAutomaton 3")
    init(&r)
    for i in range(na):
        da[A[i]] = i
    for i in range(n):
        r.e[i].final = 0
        d[V[i]] = i
    for v in F:
        if not d.has_key(v):
            FreeAutomaton(&r)
            r = NewAutomaton(0,0)
            print("Error : Incorrect set of final states.")
            return r
        r.e[d[v]].final = 1
    print("ds getAutomaton 4")
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
    print("ds getAutomaton 5")
    for e, f, l in a.edges():
        r.e[d[e]].f[da[l]] = d[f]
    print("ds getAutomaton 6")
    sig_off()
    return r

cdef AutomatonGet(Automaton a, A=None):
    from sage.combinat.words.automata import Automaton
    r = Automaton(multiedges=True, loops=True)
    cdef int i, j
    r.F = []
    if A is None:
        A = [i for i in range(a.na)]
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

    #   cdef NAutomaton* a
    #    cdef list A

    def __cinit__(self):
        # print "cinit"
        self.a = <NAutomaton *>malloc(sizeof(NAutomaton))
        # initialise
        self.a.e = NULL
        self.a.n = 0
        self.a.na = 0
        self.A = []

    def __init__(self, a, I=None, F=None, A=None):
        # print "init"
        cdef NAutomaton r
        if a is None:
            return
        else:
            if type(a) == FastAutomaton:
                self = a.copyn()
            else:
                raise ValueError("Cannot construct directly a NFastAutomaton for the moment, except from a deterministic one.")

    def __dealloc__(self):
        # print "free"
        FreeNAutomaton(self.a)
        free(self.a)

    def __repr__(self):
        return "NFastAutomaton with %d states and an alphabet of %d letters"%(self.a.n, self.a.na)

    def n_states(self):
        return self.a.n

    def n_succs(self, int i):
        """
        INPUT:

        -``i`` int successor number
        """
        if i >= self.a.n or i < 0:
            raise ValueError("There is no state %s !"%i)
        return self.a.e[i].n

    # give the state at end of the jth edge of the state i
    def succ(self, int i, int j):
        """
        Give the state at end of the jth edge of the state i

        INPUT:

        -``i`` int state number

        -``j`` int edge number
        """

        if i >= self.a.n or i < 0:
            raise ValueError("There is no state %s !"%i)
        if j >= self.a.e[i].n or j < 0:
            raise ValueError("The state %s has no edge number %s !"%(i,j))
        return self.a.e[i].a[j].e

    # give the label of the jth edge of the state i
    def label(self, int i, int j):
        """
        Give the label of the jth edge of the state i

        INPUT:

        -``i`` int state number

        -``j`` int edge number
        """
        if i >= self.a.n or i < 0:
            raise ValueError("There is no state %s !" % i)
        if j >= self.a.e[i].n or j < 0:
            raise ValueError("The state %s has no edge number %s !" % (i, j))
        return self.a.e[i].a[j].l

    def is_final(self, int i):
        """
        Return True/False if i state  is/or not  final

        INPUT:

        -``i`` int state number
        """
        if i >= self.a.n or i < 0:
            raise ValueError("There is no state %s !" % i)
        return self.a.e[i].final

    def is_initial(self, int i):
        """
        Return True/False if i state  is/or not  initial

        INPUT:

        -``i`` int state number
        """
        if i >= self.a.n or i < 0:
            raise ValueError("There is no state %s !" % i)
        return self.a.e[i].initial

    def initial_states(self):
        l = []
        for i in range(self.a.n):
            if self.a.e[i].initial:
                l.append(i)
        return l

    def final_states(self):
        l = []
        for i in range(self.a.n):
            if self.a.e[i].final:
                l.append(i)
        return l

    def Alphabet(self):
        return self.A

    def set_initial(self, int e, bool initial=True):
        if e < 0 or e >= self.a.n:
            raise ValueError("There is no state %s !" % e)
        self.a.e[e].initial = initial

    def add_edge(self, e, f, l):
        sig_on()
        AddEdgeN(self.a, e, f, l)
        sig_off()

    def add_state(self, bool final):
        raise NotImplemented()

    def add_path(self, int e, int f, list li, verb=False):
        sig_on()
        cdef int *l = <int *>malloc(sizeof(int)*len(li));
        for i in range(len(li)):
            l[i] = li[i]
        AddPathN(self.a, e, f, l, len(li), verb)
        sig_off()

    def determinise(self, puits=False, verb=0):
        cdef Automaton a
        sig_on()
        r = FastAutomaton(None)
        a = DeterminiseN(self.a[0], puits, verb)
        r.a[0] = a
        r.A = self.A
        sig_off()
        return r

    def plot(self, int sx=10, int sy=8):
        sig_on()
        cdef char** ll
        ll = <char **>malloc(sizeof(char*) * self.a.na)
        cdef int i
        strA = []
        for i in range(self.a.na):
            strA.append(str(self.A[i]))
            ll[i] = strA[i]
        NplotTikZ(self.a[0], ll, "Automaton", sx, sy)
        free(ll)
        sig_off()

# cdef set_FastAutomaton (FastAutomaton a, Automaton a2):
#    a.a[0] = a2

cdef class FastAutomaton:

#    cdef Automaton* a
#    cdef list A

    def __cinit__(self):
        # print "cinit"
        self.a = <Automaton *>malloc(sizeof(Automaton))
        # initialise
        self.a.e = NULL
        self.a.n = 0
        self.a.na = 0
        self.a.i = -1
        self.A = []

    def __init__(self, a, i=None, final_states=None, A=None):
        # print "init"
        if a is None:
            return
        from sage.graphs.digraph import DiGraph
        if isinstance(a, list):
            a = DiGraph(a, multiedges=True, loops=True)
        if isinstance(a, DiGraph):
            if A is None:
                if hasattr(a, 'A'):
                    A = list(a.A)
                else:
                    A = list(set(a.edge_labels()))
            self.A = A
            print("ds FA A:")
            print(A)
            sig_on()
            self.a[0] = getAutomaton(a, initial=i, F=final_states, A=self.A)
            sig_off()
        else:
            raise ValueError("Cannot convert the input to FastAutomaton.")

    def __dealloc__(self):
        # print "free (%s etats) "%self.a.n
        sig_on()
        FreeAutomaton(self.a)
        # print "free self.a"
        free(self.a)
        sig_off()

    def __repr__ (self):
        return "FastAutomaton with %d states and an alphabet of %d letters"%(self.a.n, self.a.na)

    def __hash__(self):
        h = 3
        for a in self.A:
            h += hash(a)
            h = (h*19) % 1000000007
        h += hashAutomaton(self.a[0])
        # print "hash=%s"%h
        return h

    #######
    #def __richcmp__(left, right, int op):
    #######

    def __cmp__(self, FastAutomaton other):
        # if type(other) != FastAutomaton:
        #    return 1
        cdef int r
        sig_on()
        r = equalsAutomaton(self.a[0], other.a[0]) and self.A == other.A
        sig_off()
        # print "cmp %s"%r
        return (r == 0)

    def Automaton(self):
        return AutomatonGet(self.a[0], self.A)

    cdef set_a(self, Automaton a):
        self.a[0] = a

    # give a FastAutomaton recognizing the full language over A.
    def full(self, list A):
        cdef Automaton a
        sig_on()
        r = FastAutomaton(None)
        a = NewAutomaton(1, len(A))
        for i in range(len(A)):
            a.e[0].f[i] = 0
        a.e[0].final = True
        a.i = 0
        r.a[0] = a
        r.A = A
        sig_off()
        return r

    def plot(self, int sx=10, int sy=8, vlabels=None, html=False, verb=False):
        sig_on()
        cdef char** ll #labels of edges
        cdef char** vl #labels of vertices
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
        plotTikZ(self.a[0], ll, "Automaton", sx, sy, vl, verb)
        if verb:
            print("free...plot")
        free(ll)
        if vlabels is not None:
            free(vl)
        sig_off()
        # self.Automaton().plot2()

    def Alphabet(self):
        return self.A

    def setAlphabet(self, list A):
        self.A = A
        self.a[0].na = len(A)

    def initial_state(self):
        return self.a.i

    def set_initial_state(self, int i):
        self.a.i = i

    def final_states(self):
        l = []
        for i in range(self.a.n):
            if self.a.e[i].final:
                l.append(i)
        return l

    def states(self):
        return range(self.a.n)

    def set_final_states(self, lf):
        cdef int f
        for f in range(self.a.n):
            self.a.e[f].final = 0
        for f in lf:
            if f < 0 or f >= self.a.n:
                raise ValueError("%d is not a state !" % f)
            self.a.e[f].final = 1

    def is_final(self, int e):
        if e >= 0 and e < self.a.n:
            return Bool(self.a.e[e].final)
        else:
            return False

    def set_final_state(self, int e, final=True):
        self.a.e[e].final = final

    def succ(self, int i, int j):
        if i < 0 or i >= self.a.n or j < 0 or j >= self.a.na:
            return -1
        return self.a.e[i].f[j]

    # donne les fils de l'état i
    def succs(self, int i):
#        if i is None:
#            i = self.a.i
#        el
        if i < 0 or i > self.a.n:
            return []
        return [j for j in range(self.a.na) if self.a.e[i].f[j] != -1]

    # suit le chemin étiqueté par l et rend l'état atteint
    def path(self, list l, i=None):
        if i is None:
            i = self.a.i
        for j in l:
            i = self.succ(i, j)
        return i

    def set_succ(self, int i, int j, int k):
        if i < 0 or i >= self.a.n or j < 0 or j >= self.a.na:
            raise ValueError("set_succ(%s, %s) : index out of bounds !" % (i, j))
        self.a.e[i].f[j] = k

    def zero_completeOP(self, verb=False):
        sig_on()
        ZeroComplete(self.a, list(self.A).index(0), verb)
        sig_off()

    def zero_complete2(self, etat_puits=False, verb=False):
        sig_on()
        cdef Automaton a
        r = FastAutomaton(None)
        a = ZeroComplete2(self.a, list(self.A).index(0), etat_puits, verb)
        r.a[0] = a
        r.A = self.A
        sig_off()
        return r.emonde().minimise()

    def zero_inv(self, z=0):
        sig_on()
        cdef Automaton a
        r = FastAutomaton(None)
        a = ZeroInv(self.a, list(self.A).index(z))
        r.a[0] = a
        r.A = self.A
        sig_off()
        return r.emonde().minimise()

    # change the final states of the automaton
    # new final states are the one in a strongly connected component containing a final state, others states are not final
    # this function can be accelerated
    def emonde_inf2OP(self, verb=False):
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
        sig_on()
        cdef Automaton a
        r = FastAutomaton(None)
        a = emonde_inf(self.a[0], verb)
        r.a[0] = a
        r.A = self.A
        sig_off()
        return r

    def emonde_i(self, verb=False):
        sig_on()
        cdef Automaton a
        r = FastAutomaton(None)
        a = emondeI(self.a[0], verb)
        r.a[0] = a
        r.A = self.A
        sig_off()
        return r

    def emonde(self, verb=False):
        sig_on()
        cdef Automaton a
        r = FastAutomaton(None)
        a = emonde(self.a[0], verb)
        r.a[0] = a
        r.A = self.A
        sig_off()
        return r

#    def equals (self, FastAutomaton b):
#        return Bool(equalsAutomaton(self.a[0], b.a[0]))

    # assume that the dictionnary d is injective !!!
    def product(self, FastAutomaton b, dict d=None, verb=False):
        if d is None:
            d = {}
            for la in self.A:
                for lb in b.A:
                    d[(la, lb)] = (la, lb)
            if verb:
                print(d)
        sig_on()
        cdef Automaton a
        cdef Dict dC
        r = FastAutomaton(None)
        Av = []
        dv = imagProductDict(d, self.A, b.A, Av=Av)
        if verb:
            print("Av=%s" % Av)
            print("dv=%s" % dv)
        dC = getProductDict(d, self.A, b.A, dv=dv, verb=verb)
        if verb:
            print("dC=")
            printDict(dC)
        a = Product(self.a[0], b.a[0], dC, verb)
        FreeDict(&dC)
        r.a[0] = a
        r.A = Av
        sig_off()
        return r

    def intersection(self, FastAutomaton a, verb=False, simplify=True):
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
        sig_on()
        res = IsCompleteAutomaton(self.a[0])
        sig_off()
        return Bool(res)

    # give a complete automaton (i.e. with his hole state)
    def complete(self):
        sig_on()
        res = CompleteAutomaton(self.a)
        sig_off()
        return Bool(res)

    # give the smallest language stable by prefix containing the language of self
    # i.e. every states begin finals
    def prefix_closure(self):
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
                ap.e[i+n1*j].final = self.a.e[i].final or a.a.e[j].final

        r.a[0] = ap
        r.A = Av
        #if verb:
        #    print r
        #r = r.emonde()
        #r = r.minimise()
        if simplify:
            return r.emonde().minimise()
        else:
            return r

    # split the automaton with respect to a  FastAutomaton
    def split(self, FastAutomaton a, verb=False):
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
            print("Av=%s" %Av)
            print("dv=%s" %dv)
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
        ap2 = CopyAutomaton(ap, ap.n, ap.na)
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
        if self.a.i != -1:
            self.a.i = self.a.e[self.a.i].f[a]

    # modify the automaton to recognize the langage shifted by a (letter given by its index)
    def shiftOP(self, a, int np, verb=False):
        for i in range(np):
            if self.a.i != -1:
                self.a.i = self.a.e[self.a.i].f[a]

    def unshift1(self, a, final=False):
        r = FastAutomaton(None)
        sig_on()
        cdef Automaton aut
        aut = CopyAutomaton(self.a[0], self.a.n+1, self.a.na)
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
        a = self
        l.reverse()
        for i in l:
            a = a.unshift1(i)
        l.reverse()
        return a

    def unshift(self, int a, int np, final=None):
        if np == 0:
            return self
        if final is None:
            if self.a.i == -1:
                r = FastAutomaton(None)
                r.A = self.A
                return r
            final = self.a.e[self.a.i].final
        r = FastAutomaton(None)
        sig_on()
        cdef Automaton aut
        aut = CopyAutomaton(self.a[0], self.a.n+np, self.a.na)
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

    def copyn(self, verb=False):
        sig_on()
        cdef NAutomaton a
        r = NFastAutomaton(None)
        a = CopyN(self.a[0], verb)
        r.a[0] = a
        r.A = self.A
        sig_off()
        return r

    def concat(self, FastAutomaton b, det=True, verb=False):
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
            print("a=%s (A=%s)\nb=%s (A=%s)" %(a, a.A, b, b.A))
        sig_on()
        cdef NAutomaton na
        r = NFastAutomaton(None)
        na = Concat(a.a[0], b.a[0], verb)
        r.a[0] = na
        r.A = A
        sig_off()
        if det:
            if verb:
                print("Determinist and simplified...")  # "Determinise et simplifie...")
            return r.determinise().emonde().minimise()
        else:
            return r

    def proj(self, dict d, det=True, verb=False):
        sig_on()
        cdef NAutomaton a
        cdef Dict dC
        r = NFastAutomaton(None)
        A2 = []
        d1 = imagDict(d, self.A, A2=A2)
        if verb:
            print("d1=%s, A2=%s"%(d1, A2))
        dC = getDict(d, self.A, d1=d1)
        a = Proj(self.a[0], dC, verb)
        FreeDict(&dC)
        r.a[0] = a
        r.A = A2
        sig_off()
        if det:
            return r.determinise().emonde().minimise()
        else:
            return r

    def proji(self, int i, det=True, verb=False):
        d = {}
        for l in self.A:
            d[l] = l[i]
        return self.proj(d, det=det, verb=verb)

    def determinise_proj(self, d, noempty=True,
                         onlyfinals=False, nof=False, verb=False):
        cdef Automaton a
        cdef Dict dC
        if noempty and not onlyfinals and not nof:
            return self.proj(d=d, verb=verb)
        else:
            sig_on()
            r = FastAutomaton(None)
            A2 = []
            d1 = imagDict(d, self.A, A2=A2)
            if verb:
                print("d1=%s, A2=%s" % (d1, A2))
            dC = getDict(d, self.A, d1=d1)
            a = Determinise(self.a[0], dC, noempty, onlyfinals, nof, verb)
            FreeDict(&dC)
            # FreeAutomaton(self.a[0])
            r.a[0] = a
            r.A = A2
            sig_off()
            return r

    # change les lettres selon d, en dupliquant les arêtes si nécessaire
    # the result is assumed deterministic !!!
    def duplicate(self, d, verb=False):
        sig_on()
        cdef Automaton a
        cdef InvertDict dC
        r = FastAutomaton(None)
        A2 = []
        d1 = imagDict2(d, self.A, A2=A2)
        if verb:
            print("d1=%s, A2=%s" %(d1, A2))
        dC = getDict2(d, self.A, d1=d1)
        if verb:
            printInvertDict(dC)
        a = Duplicate(self.a[0], dC, len(A2), verb)
        if verb:
            print("end...")
        FreeInvertDict(dC)
        r.a[0] = a
        r.A = A2
        sig_off()
        return r

    # change les lettres
    # le dictionnaire est supposé bijectif de A dans le nouvel alphabet
    # opération sur place !
    def relabel(self, d):
        self.A = [d[c] for c in self.A] 

    # permute les lettres
    # A = liste des lettres dans le nouvel ordre (il peut y en avoir moins)
    def permut(self, list A, verb=False):
        if verb:
            print("A=%s" % A)
        sig_on()
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
                l[i] = d[c] #l gives the old index from the new one
        if verb:
            str = "l=["
            for i in range(len(A)):
                str += " %s" % l[i]
            str += " ]"
            print(str)
        a = Permut(self.a[0], l, len(A), verb)
        free(l)
        r.a[0] = a
        r.A = A
        sig_off()
        return r

    # permute les lettres SUR PLACE
    # A = liste des lettres dans le nouvel ordre (il peut y en avoir moins)
    def permut_op(self, list A, verb=False):
        if verb:
            print("A=%s" % A)
        sig_on()
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
        PermutOP(self.a[0], l, len(A), verb)
        free(l)
        self.A = A
        sig_off()

    # Compute the transposition, assuming it is deterministic
    def transpose_det(self):
        sig_on()
        r = FastAutomaton(None)
        r.a[0] = TransposeDet(self.a[0])
        r.A = self.A
        sig_off()
        return r

    def transpose(self):
        sig_on()
        r = NFastAutomaton(None)
        r.a[0] = Transpose(self.a[0])
        r.A = self.A
        sig_off()
        return r

    def strongly_connected_components(self, no_trivials=False):
        sig_on()
        cdef int* l = <int*>malloc(sizeof(int) * self.a.n)
        cdef int ncc = StronglyConnectedComponents(self.a[0], l)
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
                        l2.pop(i) # on retire cette composante qui est triviale
        free(l)
        sig_off()
        return l2.values()

    def acc_and_coacc(self):
        sig_on()
        cdef int* l = <int*>malloc(sizeof(int) * self.a.n)
        AccCoAcc(self.a, l)
        sig_off()
        return [i for i in range(self.a.n) if l[i] == 1]

    def coaccessible_states(self):
        sig_on()
        cdef int* l = <int*>malloc(sizeof(int) * self.a.n)
        CoAcc(self.a, l)
        sig_off()
        return [i for i in range(self.a.n) if l[i] == 1]

    def sub_automaton(self, l, verb=False):
        sig_on()
        r = FastAutomaton(None)
        r.a[0] = SubAutomaton(self.a[0], list_to_Dict(l), verb)
        r.A = self.A
        sig_off()
        return r

    def minimise(self, verb=False):
        sig_on()
        r = FastAutomaton(None)
        r.a[0] = Minimise(self.a[0], verb)
        r.A = self.A
        sig_off()
        return r

    def adjacency_matrix(self, sparse=None):
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
        sig_on()
        r = FastAutomaton(None)
        r.a[0] = DeleteVertex(self.a[0], i)
        r.A = self.A
        sig_off()
        return r

    def delete_vertex_op(self, int i):
        sig_on()
        DeleteVertexOP(self.a, i)
        sig_off()

    def spectral_radius(self, only_non_trivial=False, verb=False):
        sig_on()
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
                    print("component with %s states..."%len(c))
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
        sig_off()
        return r

    def test(self):
        Test()

    def copy(self):
        sig_on()
        r = FastAutomaton(None)
        r.a[0] = CopyAutomaton(self.a[0], self.a.n, self.a.na)
        r.A = self.A
        sig_off()
        return r

    def has_empty_langage(self):
        sig_on()
        res = emptyLangage(self.a[0])
        sig_off()
        return Bool(res)

    def equals_langages(self, FastAutomaton a2, minimized=False, emonded=False, verb=False):
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
#            print "Av=%s"%Av
#            print "dv=%s"%dv
#        dC = getProductDict(d, self.A, a2.A, dv=dv, verb=verb)
#        if verb:
#            print "dC="
#            printDict(dC)
#        res = EmptyProduct(self.a[0], a2.a[0], dC, verb)
#        sig_off()
#        return Bool(res)

    def intersect(self, FastAutomaton a2, bool verb=False):
        """
        Compute if the  ``FastAutomaton`` element  intersert
        ``FastAutomaton``  ``a2``

        INPUT:

        -  ``a2`` Fastautomaton to intersect

        - ``verb`` - boolean (default: ``False``) True to active 
          the verbose mode

        OUTPUT:

        Return ``True`` if the both ``FastAutomaton`` has
        intersection ``False`` if not
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
#                    if verb: print "%d -> %d"%(i, j)
#                    break
#        if verb:
#            printDict(d)
#        res = intersectLangage(self.a, a2.a, d, emonded, verb)
#        sig_off()
#        return Bool(res)

    def find_word(self, bool verb=False):
        sig_on()
        cdef Dict w
        res = findWord(self.a[0], &w, verb)
        sig_off()
        if not res:
            return None
        r = []
        for i in range(w.n):
            r.append(self.A[w.e[i]])
        FreeDict(&w)
        return r

    def shortest_word(self, i=None, f=None, bool verb=False):
        sig_on()
        cdef Dict w
        if i is None:
            i = self.a.i
        if f is None:
            f = -1
        res = shortestWord(self.a[0], &w, i, f, verb)
        sig_off()
        if not res:
            return None
        r = []
        for i in range(w.n):
            r.append(self.A[w.e[i]])
        FreeDict(&w)
        return r

    def shortest_words(self, i=None, verb=False):
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
            FreeDict(&w[j])
        free(w)
        return rt

    # determine if the word is recognized by the automaton or not
    def rec_word2(self, list w):
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
        sig_on()
        AddEtat(self.a, final)
        sig_off()
        return self.a.n-1

    def add_edge(self, int i, l, int j):
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

    def n_states(self):
        return self.a.n

    def bigger_alphabet(self, nA):
        cdef Dict d
        d = NewDict(self.a.na)
        for i in range(self.a.na):
            d.e[i] = nA.index(self.A[i])
        r = FastAutomaton(None)
        sig_on()
        r.a[0] = BiggerAlphabet(self.a[0], d, len(nA))
        sig_off()
        r.A = nA
        return r

    def complementaryOP(self):
        self.complete()
        cdef i
        for i in range(self.a.n):
            self.a.e[i].final = not self.a.e[i].final

    def complementary(self):
        a = self.copy()
        a.complementaryOP()
        return a

    def included(self, FastAutomaton a, bool verb=False, emonded=False):
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
#            print "d=%s"%d
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
    def is_empty(self, ext=False):
        return (self.find_word() is None)
        #if ext:
        #    return self.emonde().emonde_inf().n_states() == 0
        #else:
        #    return self.emonde().n_states() == 0

    # determine if the languages intersect
    # def intersect (self, FastAutomaton b, ext=False):
    #    return not self.intersection(b).is_empty(ext)

    def random_word(self, nmin=-1, nmax=100):
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
