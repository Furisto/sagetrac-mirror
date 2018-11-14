# coding=utf8
r"""
Beta-adic tools.

Beta-adic is a way to write numbers in the form

    - :math:`\sum_{i=0}^\infty \beta^i c_i`

where :math:`beta` is a element of a field (for example a complex number),
and the :math:`c_i` are varying in a finite set of digits.
The possible finite sequences of digits are given by a deterministic automaton.

AUTHORS:

- Paul Mercat (2013) -  I2M AMU Aix-Marseille Universite -initial version
- Dominique Benielli (2018) - Labex Archimede - I2M -
  AMU Aix-Marseille Universite - Integration in SageMath

EXAMPLES::

    sage: pi = x^3-x^2-x-1 # Tribonacci
    sage: b = pi.roots(ring=QQbar)[1][0]
    sage: a = DetAutomaton(
    sage: m = BetaAdicSet(b, {0,1})
    sage: print(m)
    Monoid of b-adic expansion with b root of x^3 - x^2 - x - 1 and numerals set {0, 1}
    sage: pp = m.b.parent().places()[0]
    sage: print(pp)
    Ring morphism:
      From: Number Field in b with defining polynomial x^3 - x^2 - x - 1
      To:   Real Field with 106 bits of precision
      Defn: b |--> 1.839286755214161132551852564671
    sage: pm = m.b.parent().places()[1]
    sage: print(pm)
    Ring morphism:
      From: Number Field in b with defining polynomial x^3 - x^2 - x - 1
      To:   Complex Field with 53 bits of precision
      Defn: b |--> -0.419643377607080 + 0.606290729207199*I
    sage: ared = m.reduced_words_automaton2()
    sage: print(ared)
    DetAutomaton with 4 states and an alphabet of 2 letters
"""

# *****************************************************************************
#  Copyright (C) 2013 Paul Mercat <mercatp@icloud.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#    This code is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty
#    of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  See the GNU General Public License for more details; the full text
#  is available at:
#
#                  http://www.gnu.org/licenses/
# *****************************************************************************
from sage.sets.set import Set
from sage.rings.qqbar import QQbar
# from sage.rings.padics.all import *
from sage.rings.padics.factory import Qp
from libc.stdlib cimport malloc, free
from math import pi as pi_number
# from sage.structure.factory import UniqueFactory
# from sage.misc.cachefunc import cached_method
from cysignals.signals cimport sig_on, sig_off
cimport sage.combinat.words.cautomata
from sage.combinat.words.cautomata cimport DetAutomaton, FreeAutomaton
from sage.combinat.words.cautomata_generators import DetAutomatonGenerators
from sage.rings.integer import Integer
from sage.combinat.words.morphism import WordMorphism
#from sage.rings.number_field.all import *
from sage.rings.number_field.number_field import NumberField
# from sage.structure.parent_gens import normalize_names
# from free_monoid_element import FreeMonoidElement


# from sage.combinat.words.automata import Automaton
# from sage.combinat.words.cautomata import DetAutomaton

# from sage.structure.factory import UniqueFactory
# from sage.misc.cachefunc import cached_method
from cysignals.signals cimport sig_on, sig_off


# garde la composante fortement connexe de 0
# def prune(a, K):
#     """
#     Return the strongly connex component
#
#     INPUT:
#
#     - ``a`` a tree
#     - ``K``
#
#     OUTPUT:
#
#     the the strongly  connex component of a which
#     correspond the the K zeros
#
#     EXAMPLES::
#
#         sage:
#         sage: prune()
#     """
#     for s in a.strongly_connected_components_subgraphs():
#         if K.zero() in s:
#             return s

cdef extern from "complex.h":
    cdef cppclass Complexe:
        double x, y

cdef extern from "Automaton.h":
    ctypedef char bool
    cdef cppclass State:
        int* f
        bool final

    cdef cppclass Automaton:
        State* e  # states
        int n   # number of states
        int na  # number of letters
        int i  # initial state

    cdef cppclass Transition:
        int l  # label
        int e  # arrival state

    cdef cppclass NState:
        Transition* a
        int n
        bool final
        bool initial

    cdef cppclass NAutomaton:
        NState* e  # states
        int n   # number of states
        int na  # number of letters

    Automaton CopyAutomaton (Automaton a, int nalloc, int naalloc)

cdef extern from "relations.h":
    cdef cppclass Element:
        int *c  # liste des n coeffs

    cdef cppclass PlaceArch:
        Complexe *c  # 1, b, b^2, ... pour cette place

    # structure contenant les infos nécessaires pour calculer l'automate des relations
    cdef cppclass InfoBetaAdic:
        int n         # degre
        Element bn    # expression of b^n as a polynome in b of degree < n
        Element b1    # expression of 1/b as a polynome in b of degree < n
        Element *c    # list of figures used for the calculation of  relations' automaton
        int nc        # number of figures
        int ncmax     # number of allocated figures
        PlaceArch *p  # list of na places
        double *cM    # square of valeurs absolues max
        int na        # number of va

    Element NewElement(int n)
    void FreeElement(Element e)
    InfoBetaAdic allocInfoBetaAdic(int n, int na, int ncmax, int nhash, bool verb)
    void freeInfoBetaAdic(InfoBetaAdic *iba)
    Automaton RelationsAutomatonT(InfoBetaAdic *iba2, Element t, bool isvide, bool ext, bool verb)

cdef extern from "numpy/arrayobject.h":
    ctypedef int intp
    ctypedef extern class numpy.ndarray [object PyArrayObject]:
        cdef char *data
        cdef int nd
        cdef intp *dimensions
        cdef intp *strides
        cdef int flags

cimport numpy

from libc.stdint cimport uint8_t, uint32_t
from libc.math cimport log
from libc.math cimport ceil
from libc.math cimport floor
from libc.math cimport round
from libc.math cimport fabs

cdef extern from "draw.h":
    ctypedef unsigned char uint8
    cdef cppclass Color:
        uint8 r
        uint8 g
        uint8 b
        uint8 a
    cdef cppclass Surface:
        Color **pix
        int sx, sy
    cdef cppclass Complexe:
        double x
        double y
    cdef cppclass BetaAdic:
        Complexe b
        Complexe* t  # liste des translations
        int n        # nombre de translations
        Automaton a
    cdef cppclass BetaAdic2:
        Complexe b
        Complexe* t  # liste des translations
        int n        # nombre de translations
        Automaton* a
        int na
    ctypedef Color* ColorList
    #    cdef cppclass SDLImage:
    #        void *img

    void* OpenImage(const char *file_name)
    bool InImage(void* img, int x, int y)
    int ImageWidth(void *img)
    int ImageHeight(void *img)
    void CloseImage(void* img)
    void *GetSDL_SurfaceFromNumpy (numpy.ndarray na)
    void SurfaceToNumpy (Surface *s, numpy.ndarray na)
    void SDL_SurfaceToNumpy (void *ss, numpy.ndarray na)
    void TestSDL()
    Surface NewSurface(int sx, int sy)
    void FreeSurface(Surface s)
    ColorList NewColorList(int n)
    void FreeColorList(ColorList l)
    Color randColor(int a)
    #    Automate NewAutomate (int n, int na)
    #    void FreeAutomate(Automate a)
    void FreeAutomatons(Automaton* a, int n)
    BetaAdic NewBetaAdic(int n)
    void FreeBetaAdic(BetaAdic b)
    BetaAdic2 NewBetaAdic2(int n, int na)
    void FreeBetaAdic2(BetaAdic2 b)
    int *DrawZoom(BetaAdic b, int sx, int sy, int n, int ajust, Color col, int nprec, double sp, int verb)
    Automaton UserDraw(BetaAdic b, int sx, int sy, int n, int ajust, Color col, double sp, int verb)
    #  void WordZone (BetaAdic b, int *word, int nmax)
    int *Draw(BetaAdic b, Surface s, int n, int ajust, Color col, int nprec, double sp, int verb)
    void Draw2(BetaAdic b, Surface s, int n, int ajust, Color col, double sp, int verb)
    void DrawList(BetaAdic2 b, Surface s, int n, int ajust, ColorList lc, double alpha, double sp, int nprec, int verb)
    void print_word(BetaAdic b, int n, int etat)


cdef uint32_t moy(uint32_t a, uint32_t b, float ratio):
    return <uint32_t><uint8_t>((a%256)*(1.-ratio) + (b%256)*ratio) | \
           (<uint32_t>(<uint8_t>(((a>>8)%256)*(1.-ratio) + ((b>>8)%256)*ratio)))<<8 | \
           (<uint32_t>(<uint8_t>(((a>>16)%256)*(1.-ratio) + ((b>>16)%256)*ratio)))<<16 | \
           (<uint32_t>(<uint8_t>((a>>24)*(1.-ratio) + (b>>24)*ratio)))<<24;


cdef double fmax(double a, double b):
    if a < b:
        return b
    return a

# plot the Rauzy fractal corresponding to the direction vector d,
# for the C-adic system given by the Cassaigne's algorithm
def plot_Cadic(numpy.ndarray dv, int sx=800, int sy=600,
               float mx=-2, float my=-2, float Mx=2, float My=2,
               int n=1000, int nptsmin=50000, int nptsmax=60000,
               bool verb=False, bool printl=True, bool get_ndarray=False):
    """
    plot the Rauzy fractal corresponding to the direction vector ``dv``
    for the C-adic system given by the Cassaigne's algorithm

    INPUT:

        - ``dv``- ndarray array , direction vector

        - ``sx`` int -- (default 800) size of Image direction x

        - ``sy`` int -- (default 60) size of Image direction y

        - ``mx`` float -- (default -2)

        - ``my`` float -- (default -2)

        - ``Mx``  float -- (default 2)

        - ``My`` float  -- (default 2)

        - ``n`` int -- (default 1000)

        - ``nptsmin`` int -- (default 50000)

        - ``nptsmax`` int -- (default 60000)

        - ``verb`` bool -- (default ''False'')

        - ``printl`` bool -- (default ''False'')


        OUTPUT:

        Plot Rauzy fractal corresponding to the direction vector dv

        EXAMPLES::

            sage: e = QQbar(1/(1+I))
            sage: m = BetaAdicSet(e, dag.AnyWord([0,1]))
            sage: m.plot_Cadic(dv=)

    """
    cdef numpy.ndarray l, d, im
    cdef int i, j, k, u, nA, i0, e, e0, npts, su, rsu
    cdef uint32_t x, y
    cdef uint32_t color
    cdef float fx, fy

    npts = 0
    color = 255 << 24
    colors = [255 | 255 << 24, 255 << 8 | 255 << 24, 255 << 16 | 255 << 24]

    import numpy as np
    d = np.empty(3, dtype=np.float)
    d[0] = <float>dv[0]
    d[1] = <float>dv[1]
    d[2] = <float>dv[2]
    from sage.combinat.words.morphism import WordMorphism
    s = WordMorphism('a->a,b->ac,c->b')
    t = WordMorphism('a->b,b->ac,c->c')
    auts = s.DumontThomas(proj=False)
    autt = t.DumontThomas(proj=False)
    aut = [auts, autt]
    A = [np.array(a) for a in auts.alphabet]
    nA = len(A)
    #if autt.alphabet != A:
    #    raise RuntimeError("The two Dumont-Thomas automata must have the same alphabet !")
    ms = s.incidence_matrix()
    mt = t.incidence_matrix()
    if verb:
        print("ms=%s"%ms)
        print("mt=%s"%mt)
    msi = (ms**(-1)).numpy()
    mti = (mt**(-1)).numpy()
    if verb:
        print("msi=%s"%msi)
        print("mti=%s"%mti)
    lm = [ms.numpy(), mt.numpy()]
    # compute an orthonormal basis
    v1 = np.array([1, -1, 0])
    v2 = np.array([1, 0, -1])
    v1 = v1 - v1.dot(d)/d.dot(d)*d
    v2 = v2 - v2.dot(d)/d.dot(d)*d
    from sage.functions.other import sqrt
    v1 = v1/sqrt(v1.dot(v1))
    v2 = v2/sqrt(v2.dot(v2))
    v2 = v2 - v1.dot(v2)*v1
    # Cassaigne's algorithm
    l = np.empty(n, dtype=np.int8)
    m = np.identity(3, dtype=np.int)
    v0 = np.zeros(3, dtype=np.int)
    v0[0] = 1
    su = 0
    for i in range(n):
        if d[0] > d[2]:
            d = msi.dot(d)
            l[i] = 0
        else:
            d = mti.dot(d)
            l[i] = 1
        m = m.dot(lm[l[i]])
        rsu = su
        su = sum(m.dot(v0))
        if rsu > nptsmin:
            n = i
            break
        if su > nptsmax:
            n = i
            break
        d = d/sum(d)
        if verb:
            print("d=%s" % d)
    if verb or printl:
        print("n=%s, l=%s"%(n, l[:n]))
    # Draw the Rauzy fractal
    im = np.empty([sy, sx], dtype=np.dtype(
        (np.uint32, {'r': (np.uint8, 0), 'g': (np.uint8, 1),
                     'b': (np.uint8, 2), 'a': (np.uint8, 3)})))
    # im.fill(0) #fill the image with transparent
    im.fill(255 | 255 << 8 | 255 << 16 | 255 << 24)  # fill with white

    if verb:
        print("A=%s" % A)
        print("nA=%s" % nA)

    p = [(np.zeros(3, dtype=np.int), 0, 0)]
    while len(p) > 0:
        k = len(p)-1
        u = l[n-k-1]
        # print("k=%s"%k)
        t, i, e = p[-1]
        # print("t=%s, i=%s, e=%s"%(t, i, e))
        if k == n:
            # we draw the point t
            # print(t)
            fx = (t.dot(v1) - mx)*sx/(Mx-mx)
            fy = (t.dot(v2) - my)*sy/(My-my)
            x = <uint32_t> fx
            y = <uint32_t> fy
            if verb:
                print(t)
                print(fx, fy)
                print(x, y)
                # print("")
            if x < sx and y < sy:
                if x+1 < sx and y+1 < sy:
                    im[y, x] = moy(im[y, x], colors[e], (1.-fx+x)*(1.-fy+y))
                    im[y, x+1] = moy(im[y, x+1], colors[e], (fx-x)*(1.-fy+y))
                    im[y+1, x] = moy(im[y+1, x], colors[e], (1.-fx+x)*(fy-y))
                    im[y+1, x+1] = moy(im[y+1, x+1], colors[e], (fx-x)*(fy-y))
                else:
                    im[y, x] = colors[e]
            npts += 1
            # increment
            # print("increment...")
            while True:
                t, i, e = p.pop()
                k = len(p)
                if k == 0:
                    break
                t0, i0, e0 = p[-1]
                u = l[n-k]
                # print("k=%s, u=%s, t=%s, i=%s, e=%s"%(k, u, t, i, e))
                while True:
                    i0 += 1
                    if i0 == nA or aut[u].succ(e0, i0) != -1:
                        break
                # print("i=%s"%i)
                if i0 != nA:
                    p[-1] = (t0, i0, e0)
                    p.append((lm[u].dot(t0)+A[i0], 0, aut[u].succ(e0, i0)))
                    break
        else:
            i = 0
            while i < nA and aut[u].succ(e, i) == -1:
                i += 1
            # print("starting i=%s k=%s u=%s t=%s e=%s"%(i, k, u, t, e))
            p[-1] = (t, i, e)
            p.append((lm[u].dot(t)+A[i], 0, aut[u].succ(e, i)))
        #for j2, (m2, t2, i2, e2) in enumerate(p):
            #print("%s : m=%s, t=%s, i=%s, e=%s"%(j2, m2, t2, i2, e2))
    if printl:
        print("%s pts computed."%npts)
    if get_ndarray:
        return im
    from PIL import Image
    return Image.fromarray(im, 'RGBA')


# plot the Rauzy fractal corresponding to the direction vector d,
# for the C-adic system given by the Cassaigne's algorithm
def plot_Cadic2(numpy.ndarray dv, int sx=800, int sy=600,
                float mx=-2, float my=-2, float Mx=2, float My=2,
                int n=40, bool verb=False, bool printl=True):
    cdef numpy.ndarray l, d, im
    cdef int i, j, k, u, nA, i0, e, e0, npts
    cdef uint32_t x, y
    cdef uint32_t color
    cdef float fx, fy

    npts = 0
    color = 255 << 24
    import numpy as np
    d = np.empty(3, dtype=np.float)
    d[0] = <float>dv[0]
    d[1] = <float>dv[1]
    d[2] = <float>dv[2]
    from sage.combinat.words.morphism import WordMorphism
    s = WordMorphism('a->a,b->ac,c->b')
    t = WordMorphism('a->b,b->ac,c->c')
    auts = s.DumontThomas(proj=False).mirror()
    autt = t.DumontThomas(proj=False).mirror()
    aut = [auts, autt]
    A = [np.array(a) for a in auts.alphabet]
    nA = len(A)
    # if autt.alphabet != A:
    #    raise RuntimeError("The two Dumont-Thomas automata must have the same alphabet !")
    ms = s.incidence_matrix()
    mt = t.incidence_matrix()
    if verb:
        print("ms=%s" % ms)
        print("mt=%s" % mt)
    msi = (ms**(-1)).numpy()
    mti = (mt**(-1)).numpy()
    if verb:
        print("msi=%s" % msi)
        print("mti=%s" % mti)
    lm = [ms.numpy(), mt.numpy()]
    # compute an orthonormal basis
    v1 = np.array([1,-1,0])
    v2 = np.array([1,0,-1])
    v1 = v1 - v1.dot(d)/d.dot(d)*d
    v2 = v2 - v2.dot(d)/d.dot(d)*d
    from sage.functions.other import sqrt
    v1 = v1/sqrt(v1.dot(v1))
    v2 = v2/sqrt(v2.dot(v2))
    v2 = v2 - v1.dot(v2)*v1
    # Cassaigne's algorithm
    l = np.empty(n, dtype=np.int8)
    for i in range(n):
        if d[0] > d[2]:
            d = msi.dot(d)
            l[i] = 0
        else:
            d = mti.dot(d)
            l[i] = 1
        d = d/sum(d)
        if verb:
            print("d=%s" % d)
    if verb or printl:
        print("l=%s" % l)
    # Draw the Rauzy fractal
    im = np.empty([sy, sx], dtype=np.dtype(
        (np.uint32, {'r': (np.uint8, 0), 'g': (np.uint8, 1),
                     'b': (np.uint8, 2), 'a': (np.uint8, 3)})))
    # im.fill(0) #fill the image with transparent
    im.fill(255 | 255 << 8 | 255 << 16 | 255 << 24)  # fill with white

    if verb:
        print("A=%s" % A)
        print("nA=%s" % nA)

    p = [(np.identity(3, dtype=np.int), np.zeros(3, dtype=np.int), 0, 0)]
    while len(p) > 0:
        k = len(p)-1
        u = l[k]
        #print("k=%s"%k)
        m, t, i, e = p[-1]
        #print("t=%s, i=%s, e=%s"%(t, i, e))
        if k == n-1:
            #we draw the point t
            #print(t)
            fx = (t.dot(v1) - mx)*sx/(Mx-mx)
            fy = (t.dot(v2) - my)*sy/(My-my)
            x = <uint32_t>fx
            y = <uint32_t>fy
            if verb:
                print(t)
                print(fx,fy)
                print(x,y)
                #print("")
            if x < sx and y < sy:
                #if x+1 < sx and y+1 < sy:
                #    im[y,x] = moy(im[y,x], color, (1.-fx+x)*(1.-fy+y))
                #    im[y,x+1] = moy(im[y,x+1], color, (fx-x)*(1.-fy+y))
                #    im[y+1,x] = moy(im[y+1,x], color, (1.-fx+x)*(fy-y))
                #    im[y+1,x+1] = moy(im[y+1,x+1], color, (fx-x)*(fy-y))
                #else:
                im[y,x] = color
            npts += 1
            #increment
            #print("increment...")
            while True:
                m, t, i, e = p.pop()
                k = len(p)
                if k == 0:
                    break
                m0, t0, i0, e0 = p[-1]
                u = l[k-1]
                nA = aut[u].n_succs(e0)
                # print("k=%s, u=%s, t=%s, i=%s, e=%s"%(k, u, t, i, e))
                while True:
                    i0 += 1
                    if i0 == nA or aut[u].succ(e0, i0) != -1:
                        break
                # print("i=%s"%i)
                if i0 != nA:
                    p[-1] = (m0, t0, i0, e0)
                    p.append((m, t0+m0.dot(A[i0]), 0, aut[u].succ(e0, i0)))
                    break
        else:
            i = 0
            nA = aut[u].n_succs(e)
            while i < nA and aut[u].succ(e, i) == -1:
                i += 1
            # print("starting i=%s k=%s u=%s t=%s e=%s"%(i, k, u, t, e))
            p[-1] = (m, t, i, e)
            p.append((m.dot(lm[u]), lm[u].dot(t)+A[i], 0, aut[u].succ(e, i)))
        # for j2, (m2, t2, i2, e2) in enumerate(p):
            # print("%s : m=%s, t=%s, i=%s, e=%s"%(j2, m2, t2, i2, e2))
    print("%s pts computed." % npts)
    from PIL import Image
    return Image.fromarray(im, 'RGBA')


# calcul de la valeur absolue p-adique
def absp(c, p, d):
    """
    Computation of the p-adic absolute value.

    INPUT:

    - ``c`` -- the algebraic number for which we compute the absolute value

    - ``p`` -- the prime number

    - ``d`` -- the degree

    OUTPUT:

    The p-adic absolute value.

    TESTS:

        sage: absp(1, 2, 3) # not implemented

    """
    return ((c.polynomial())(p).norm().abs())**(1/d)


cdef getElement(e, Element r, int n):
    cdef j
    p = e.lift()
    for j in range(n):
        r.c[j] = p[j]

cdef InfoBetaAdic initInfoBetaAdic(self,
                                   Ad=None, plus=True, nhash=1000003,
                                   verb=False) except *:
    b = self.b
    K = b.parent()
    A = self.a.alphabet
    if verb:
        print("A = %s" % A)

    if verb:
        print(K)

    # détermine les places qu'il faut considérer
    parch = []
    for p in K.places():  # places archimédiennes
        if plus:
            if p(b).abs() > 1:
                parch += [p]
        else:
            if p(b).abs() < 1:
                parch += [p]
    pi = K.defining_polynomial()
    from sage.arith.misc import gcd
    # rend le polynôme à coefficients entiers et de contenu 1
    pi = pi / gcd(pi.list())
    if verb:
        print("pi=%s" % pi)
    # liste des nombres premiers concernés
    lp = (Integer(pi.list()[0])).prime_divisors()
    if verb:
        print("lp=%s" % lp)
    # liste des place  s ultramétriques considérées
    pultra = []
    for p in lp:
        # détermine toutes les places au dessus de p dans le corps de nombres K
        k = Qp(p)
        Kp = k['a']
        a = Kp.gen()
        for f in pi(a).factor():
            kp = f[0].root_field('e')
            if kp == k:
                c = f[0].roots(kp)[0][0]
            else:
                c = kp.gen()
            if verb:
                print("c=%s (abs=%s)" % (c, (c.norm().abs())**(1/f[0].degree())))
            if plus:
                if (c.norm().abs())**(1/f[0].degree()) > 1:
                    pultra += [(c, f[0].degree())]
            else:
                if (c.norm().abs())**(1/f[0].degree()) < 1:
                    pultra += [(c, f[0].degree())]

    if verb:
        print("spaces: ")
        print(parch)
        print(pultra)

    if (len(pultra) > 0):
        raise ValueError("Not implemented for b algebraic non-integer.")
    # calcule les bornes max pour chaque valeur absolue
    if Ad is None:
        Ad = Set([c-c2 for c in A for c2 in A])
    Ad = [K(c) for c in Ad]
    if verb:
        print("Ad = %s" % Ad)

    n = K.degree()
    na = len(parch)
    ncmax = len(Ad)
    cdef InfoBetaAdic i
    if verb:
        print("alloc...")
    sig_on()
    i = allocInfoBetaAdic(n, na, ncmax, nhash, verb)
    sig_off()
    cdef int j
    # initialise bn
    if verb:
        print("init bn...")
    getElement(b**n, i.bn, n)
    # initialise b1
    if verb:
        print("init b1...")
    getElement(1/b, i.b1, n)
    # initialise les places
    if verb:
        print("init places...")
    for k in range(na):
        for j in range(n):
            i.p[k].c[j] = complex(parch[k](b**j))
    # initialise les chiffres et bornes
    if verb:
        print("init chiffres...")
    initCdInfoBetaAdic(self, &i, Ad=Ad, parch=parch, verb=verb)
    return i

cdef initCdInfoBetaAdic(self, InfoBetaAdic *i, list Ad, list parch, verb=False):
    if verb:
        print("initCdInfoBetaAdic Ad = %s" % Ad)
    m = dict([])
    for p in parch:
        m[p] = max([p(c).abs() for c in Ad])/abs(1-p(self.b).abs())
    if verb:
        print("bounds : %s" % m)
    # conversion to C
    i.nc = len(Ad)
    if i.nc > i.ncmax:
        raise ValueError("Too much decimals : %d > %d max (initialize BetaAdicSet with more digits)."%(i.nc, i.ncmax))
    for j, c in enumerate(Ad):
        getElement(c, i.c[j], i.n)
    for j, p in enumerate(parch):
        i.cM[j] = m[p]**2

cdef Complexe complex(c):
    cdef Complexe r
    r.x = c.real()
    r.y = c.imag()
    return r

cdef Color getColor(c):
    if len(c) < 4:
        raise ValueError("Colors must be defined by 4 float numbers between 0 and 1.")
    cdef Color r
    r.r = c[0] * 255
    r.g = c[1] * 255
    r.b = c[2] * 255
    r.a = c[3] * 255
    return r

cdef surface_to_img(Surface s):
    # print("surface_to_img %s, %s..."%(s.sx, s.sy))
    import numpy as np
    from PIL import Image
    # arr = np.empty([s.sy, s.sx], dtype=['uint8', 'uint8', 'uint8', 'uint8'])
    # arr = np.empty([s.sy, s.sx], dtype=[('r', 'uint8'), ('g', 'uint8'),('b', 'uint8'), ('a', 'uint8')])
    # arr = np.zeros([s.sy, s.sx], dtype=[('r', 'uint8'), ('g', 'uint8'),('b', 'uint8'), ('a', 'uint8')])
    arr = np.empty([s.sy, s.sx], dtype=np.dtype((np.uint32, {'r':(np.uint8,0), 'g':(np.uint8,1), 'b':(np.uint8,2), 'a':(np.uint8,3)})))

#    cdef int x, y
#    cdef Color c
#    for x in range(s.sx):
#        for y in range(s.sy):
#            c = s.pix[x][s.sy - y - 1]
#            #arr[y, x]['r'] = c.r
#            #arr[y, x]['g'] = c.g
#            #arr[y, x]['b'] = c.b
#            arr[y, x] = c.r | c.g << 8 | c.b << 16 | c.a<<24;
    #print("Surface to numpy...")
    sig_on()
    SurfaceToNumpy (&s, arr)
    sig_off()
    #print("...done !")
    return Image.fromarray(arr, 'RGBA')
    # img.save("/Users/mercat/Desktop/output.png")
    # img.save(file)

cdef Automaton getAutomaton(DetAutomaton a, list A, verb=False):
    cdef int i
    if verb:
        print("getAutomaton %s..." % a)
    cdef DetAutomaton fa
    cdef Automaton aut
    #if isinstance(a, DetAutomaton):
    if set(A).issubset(a.A):
        fa = a.permut(A, verb=verb)
    else:
        fa = a.bigger_alphabet(A)
    aut = fa.a[0]
    # free(fa.a)
    # fa.a = NULL
    aut = CopyAutomaton(aut, aut.n, aut.na);
    return aut
    # else:
    #    raise ValueError("DetAutomaton expected.")


def mahler(pi):
    from sage.rings.qqbar import AA
    pi = pi/pi.denominator()
    rr = pi.roots(ring=QQbar)
    p = pi.leading_coefficient()
    for r in rr:
        if r[0] not in AA:
            rr.remove((r[0].conjugate(), r[1]))
        p *= abs(r[0])
    return p


cdef BetaAdic getBetaAdic(m, prec=53, mirror=False, verb=False):
    from sage.rings.complex_field import ComplexField
    CC = ComplexField(prec)
    cdef BetaAdic b
    a = m.a
    if mirror:
        a = a.mirror().determinize().minimize()
    A = a.alphabet
    nA = a.n_letters

    b = NewBetaAdic(nA)
    b.b = complex(CC(m.b))
    for i, c in zip(range(b.n), A):
        b.t[i] = complex(CC(c))
    b.a = getAutomaton(a, A=A, verb=verb)
    return b

cdef BetaAdic2 getBetaAdic2(BetaAdicSet self, la=None,
                            prec=53, mirror=False, verb=False):
    if verb:
        print("getBetaAdic %s" % self)
    from sage.rings.complex_field import ComplexField
    CC = ComplexField(prec)
    cdef BetaAdic2 b
    if la is None:
        la = self.get_la(verb=verb)

    # check that every element of la is a DetAutomaton or convert it
    la = [getDetAutomaton(self, a) for a in la]

    # add the automaton of self as first element
    la = [self.a]+la

    if mirror:
        la = [a.mirror().determinize().minimize() for a in la]

    if verb:
        print("la=%s" % la)

    A = set()
    for a in la:
        A.update(a.alphabet)
    A = list(A)
    if verb:
        print("A=%s" % A)

    b = NewBetaAdic2(len(A), len(la))
    b.b = complex(CC(self.b))
    d = {}
    for i, c in zip(range(b.n), A):
        b.t[i] = complex(CC(c))
        d[c] = i
    # automata
    for i in range(len(la)):
        b.a[i] = getAutomaton(getDetAutomaton(self, la[i]), A=A, verb=verb)
    return b


def PrintWord(m, n):
    """
    Print of beta adic 

    INPUT:

    - ``m`` first word argument

    - ``n`` second word argument


    OUTPUT:

    Print the word

    TESTS:

        sage:import sage.monoids.beta_adic_monoid as mn

    """
    b = getBetaAdic(m, prec=53, mirror=False, verb=False)
    print_word(b, n, b.a.i)


# ##used by compute_substitution()
# gives the list of sleeves of the sub-tree starting at e
def fils(tree, e):
    """
    Return the list of sheet's sub-tree  starting at e.

    INPUT:

    - ``tree`` the tree.
    - ``e`` the starting node.

    OUTPUT:

    list of ``tree`` sheet's sub-tree  starting on e.

    """
    if tree[e] == []:  # e is a
        return [e]
    r = []
    for f in tree[e]:
        r += fils(tree, f)
    return r


# teste si a est inclus dans un des morceaux de l ou pas
def included(a, l, lm):
    """
    Return the index of

    INPUT:

    - ``a`` word to find in ``l``.

    - ``l`` including word to test

    OUTPUT:

    - the word in ``l`` if a is present

    - ``True`` if the automata is empty

    - ``None``

    """
    # teste vite fait si l'on est inclus dans un morceau ou pas
    incl = False
    w = a.find_word()
    if w is None:
        print("Error : empty automata!")
        return True
    lr = []
    for j in l:
        a2 = lm[j][0]
        if a2.rec_word(w):
            if a.included(a2):
                return j
            else:
                return None
    print("******* Error : word %s is conconize by any automata ! *********" % w)
    return None


# split a1 selon ba (rend un couple (a11, a12) avec a11 la partie
# dans ba et a12 celle disjointe de ba)
def split_ba(i, tr, np, lm, m, aa, ap, verb=False):
    b = m.b
    a1 = lm[i][0]
    # teste l'intersection avec ba
    # at = m.move2(t=(b**(-np))*tr, a=aoc)
    # TODO : utiliser les automates des relations précalculés
    # pour les translations de l'échange
    at = m.Proj(aa, ap, t=(b**(-np))*tr)
    if at.intersect(a1):
        ar = at.intersection(a1)
        # détermine si l'on est inclus dans ba
        ar.zero_completeOP()
        if ar.equals_langages(a1):
            return (a1, None)
        else:
            # on subdivise en deux
            ar2 = a1.intersection(ar.complementary())
            ar2.zero_completeOP()
            return (ar, ar2)
    else:
        return (None, a1)


# split a1 selon baoc (rend un couple (a11, a12) avec a11 la partie dans baoc
# et a12 celle disjointe de baoc)
def split_baoc(i, tr, np, lm, m, aoc, verb=False):
    b = m.b
    a1 = lm[i][0]
    # teste l'intersection avec baoc
    at = m.move2(t=(b**(-np))*tr, a=aoc)
    # TODO : utiliser les automates des relations précalculés
    # pour les translations de l'échange
    if at.intersect(a1):
        ar = at.intersection(a1)
        # détermine si l'on est inclus dans baoc
        ar.zero_completeOP()
        if ar.equals_langages(a1):
            return (a1, None)
        else:
            # on subdivise en deux
            return (ar, a1.intersection(ar.complementary()))
    else:
        return (None, a1)


cdef class ImageIn:
    cdef void** s

    def __cinit__(self):
        self.s = <void **>malloc(sizeof(void*))

    def __init__(self, file_name):
        self.s[0] = OpenImage(file_name)

    def __dealloc__(self):
        CloseImage(self.s[0])
        free(self.s)

    def __repr__(self):
        w = ImageWidth(self.s[0])
        h = ImageHeight(self.s[0])
        return "Image of size %sx%s" % (w, h)

    def __contains__(self, p):
        from sage.rings.complex_field import ComplexField
        CC = ComplexField(53)
        if p in CC:
            return InImage(self.s[0], p.real(), p.imag())
        else:
            return InImage(self.s[0], p[0], p[1])

    def width(self):
        return ImageWidth(self.s[0])

    def height(self):
        return ImageHeight(self.s[0])


def getDetAutomaton(self, a):
    if type(a) is BetaAdicSet:
        if self.b != a.b:
            raise ValueError("The two beta-adic sets must have the same" +
                             "b (here %s != %s).", self.b, a.b)
        a = a.a
    elif type(a) is not DetAutomaton:
        try:
            a = DetAutomaton(a)
        except Exception:
            raise ValueError("The argument a must be a BetaAdicSet or an automaton.")
    return a


cdef getBetaAdicSet(BetaAdicSet self, a):
    if type(a) is BetaAdicSet:
        if self.b != a.b:
            raise ValueError("The two beta-adic sets must have the same b (here %s != %s).", self.b, a.b)
    elif type(a) is not DetAutomaton:
        try:
            a = DetAutomaton(a)
        except Exception:
            raise ValueError("The argument a must be a BetaAdicSet or an automaton.")
        a = BetaAdicSet(self.b, a)
    return a

cdef class BetaAdicSet:
    r"""
    Define a numeration in base b, i.e. set of numbers of the form

        :math:`\sum_{i=0}^\infty \beta^i c_i`

    where :math:`beta` is a element of a field (for example a complex number),
    and the :math:`c_i` form a word recognized by a deterministic automaton ``a``.

    INPUT:

    - ``b`` -- number, base of the numeration.

    - ``a`` -- DetAutomaton, giving the allowed sequence of digits.


    EXAMPLES::

        sage: from sage.combinat.words.cautomata_generators import dag
        sage: m1 = BetaAdicSet(3, dag.AnyWord([0, 1, 3]))
        sage: print(m1)
        b-adic set with b root of x - 3, and an automaton of 1 states and 3 letters.
        sage: m2 = BetaAdicSet((1 + sqrt(5)) / 2, dag.AnyWord([0, 1]))
        sage: print(m2)
        b-adic set with b root of x^2 - x - 1, and an automaton of 1 states and 2 letters.
        sage: b = (x^3-x-1).roots(ring=QQbar)[0][0]
        sage: m3 = BetaAdicSet(b, dag.AnyWord([0, 1]))
        sage: print(m3)
        b-adic set with b root of x^3 - x - 1, and an automaton of 1 states and 2 letters.

    """
    def __init__(self, b, a):
        r"""
        Construction of the b-adic with base ``b`` and automaton ``a``.

        EXAMPLES::

            sage: from sage.combinat.words.cautomata_generators import dag
            sage: m1 = BetaAdicSet(3, dag.AnyWord([0, 1, 3]))
            sage: m1
            b-adic set with b root of x - 3, and an automaton of 1 states and 3 letters.
            sage: c = Automaton({0:{1:'0',2:'1',3:'2'}, 2:{5:'1'}},initial_states=[0])
            sage: b = m1.b
            m3 = BetaAdicSet(b, c)
            sage: m3
            b-adic set with b root of x - 3, and an automaton of 5 states and 3 letters.
            sage: m = BetaAdicSet(x^3-x^2-x-1, [0,1])
            sage: m
            b-adic set with b root of x^3 - x^2 - x - 1, and an automaton of 1 states and 2 letters.
            sage: m1 = BetaAdicSet(3,[0,1])
            sage: m1
            b-adic set with b root of x - 3, and an automaton of 1 states and 2 letters.

        """
        cdef int i, j
        from sage.rings.complex_field import ComplexField
        CC = ComplexField()
        if b not in CC:
            # raise ValueError("b must be a number.")
            from sage.rings.qqbar import QQ
            from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing
            K = PolynomialRing(QQ, 'x')
            try:
                pi = K(b)
                rr = [r[0] for r in pi.roots(ring=QQbar)]
                rrm = [r for r in rr if abs(r) < 1]
                if len(rrm) > 0:
                    b = rrm[0]
                else:
                    b = rr[0]
            except Exception:
                raise ValueError("b must be a number, or a polynomial over QQ")
        try:
            b = QQbar(b)
            pi = QQbar(b).minpoly()
            K = NumberField(pi, 'b', embedding=b)
            self.b = K.gen()
        except Exception:
            self.b = b

        if type(a) != DetAutomaton:
            try:
                a = DetAutomaton(a)
            except Exception:
                try:
                    a = list(a)
                except Exception:
                    raise ValueError("a must be an automaton or an iterable.")
                from sage.combinat.words.cautomata_generators import dag
                a = dag.AnyWord(a)
        self.a = a

        # test if letters of a are in K
        try:
            K = self.b.parent()
            self.a.A = [K(c) for c in self.a.A]
        except Exception:
            raise ValueError("Alphabet %s of the automaton is not in the field %s of b !"%(self.a.A, self.b.parent()))

    def __repr__(self):
        r"""
        Returns the string representation of the beta-adic monoid.

        EXAMPLES::

            sage: from sage.combinat.words.cautomata_generators import dag
            sage: BetaAdicSet((1+sqrt(5))/2, dag.AnyWord([0, 1]))
            b-adic set with b root of x^2 - x - 1, and an automaton of 1 states and 2 letters.
            sage: BetaAdicSet(3, dag.AnyWord([0, 1, 3]))
            b-adic set with b root of x - 3, and an automaton of 1 states and 3 letters.


        TESTS::

            sage: from sage.combinat.words.cautomata_generators import dag
            sage: m = BetaAdicSet(3/sqrt(2), dag.AnyWord([0, 1]))
            sage: repr(m)
            'b-adic set with b root of x^2 - 9/2, and an automaton of 1 states and 2 letters.'

        """

        from sage.rings.qqbar import QQbar
        if self.b not in QQbar:
            return "(%s)-adic set with an automaton of %s states and %s letters." % (self.b, self.a.n_states, self.a.n_letters)
        else:
            K = self.b.parent()
            from sage.rings.rational_field import QQ
            if K.base_field() == QQ:
                return "b-adic set with b root of %s, and an automaton of %s states and %s letters." % (self.b.minpoly(), self.a.n_states, self.a.n_letters)
            else:
                if K.characteristic() != 0:
                    return "b-adic set with b root of %s (in characteristic %s), and an automaton of %s states and %s letters."%(self.b.minpoly(), K.characteristic(), self.a.n_states, self.a.n_letters)
                else:
                    return "b-adic set with b root of %s, an automaton of %s states and %s letters."%(K.modulus(), self.a.n_states, self.a.n_letters)

    def string(self):
        r"""
        Return a string that can be evaluated to recover the BetaAdicSet

        OUTPUT:
        Return a string to define a BetaAdicSet, this set can be obtained by the ``use_draw`` method

        EXAMPLES::

            sage: m1 = BetaAdicSet(3,[0,1])
            sage: m1.string()
            'BetaAdicSet((x - 3).roots(ring=QQbar)[0][0], DetAutomaton([[0, 1], [(0, 0, 0), (0, 0, 1)]], i=0, final_states=[0]))'
            sage: m = BetaAdicSet(x^3-x^2-x-1, [0,1])
            sage: m.string()
            'BetaAdicSet((x^3 - x^2 - x - 1).roots(ring=QQbar)[1][0], DetAutomaton([[0, 1], [(0, 0, 0), (0, 0, 1)]], i=0, final_states=[0]))'

        """
        pi = self.b.minpoly()
        from sage.rings.qqbar import QQbar
        rr = pi.roots(ring=QQbar)
        for i, r in enumerate(rr):
            if r[0] == self.b:
                break
        return "BetaAdicSet((%s).roots(ring=QQbar)[%s][0], %s)"%(pi, i, self.a.string())

    @property
    def a(self):
        """
        Get the ``DetAutomaton`` ``a`` of the ``BetaAdicSet``

        OUTPUT:

        ``DetAutomaton`` ``a`` attribut

        EXAMPLES::

            sage: from sage.combinat.words.cautomata_generators import dag
            sage: m = BetaAdicSet((1+sqrt(5))/2, dag.AnyWord([0, 1]))
            sage: m.a
            DetAutomaton with 1 states and an alphabet of 2 letters

        """
        return self.a

    @property
    def b(self):
        """
        Get the number ``b`` of the ``BetaAdicSet``

        OUTPUT:

        number ``b`` attribut

        EXAMPLES::

            sage: m = BetaAdicSet((1+sqrt(5))/2, dag.AnyWord([0, 1]))
            sage: m.b
            b

        """
        return self.b

    def copy(self):
        """
        return a copy of  the ``BetaAdicSet``

        OUTPUT:

        a ``BetaAdicSet``

        EXAMPLES::

            sage: from sage.combinat.words.cautomata_generators import dag
            sage: m = BetaAdicSet((1+sqrt(5))/2, dag.AnyWord([0, 1]))
            sage: m.copy()
            b-adic set with b root of x^2 - x - 1, and an automaton of 1 states and 2 letters.

        """

        return BetaAdicSet(self.b, self.a.copy())

    def mirror(self):
        """
        Return the beta-adic set with the mirror automaton.

        OUTPUT:

        a ``BetaAdicSet`` with the mirror a automaton as attribuet ``a``

        EXAMPLES::

            sage: from sage.combinat.words.cautomata_generators import dag
            sage: m = BetaAdicSet((1+sqrt(5))/2, dag.AnyWord([0, 1]))
            sage: m.mirror()
            b-adic set with b root of x^2 - x - 1, and an automaton of 1 states and 2 letters.

        """
        return BetaAdicSet(self.b, self.a.mirror())

    def is_included(self, a, verb=False):
        """
        Determine if the BetaAdicSet is included in the BetaAdicSet given by a.

        INPUT:

        - ``a`` - ``BetaAdicSet`` to compare
        - ``verb`` - Boolean (default: False) Display informations for debug.

        OUTPUT:

        ``True``  if the BetaAdicSet is included in the BetaAdicSet given
        by a  ``False`` otherwise


        EXAMPLES::

            sage: m = BetaAdicSet(x^3-x^2-x-1, [0,1])
            sage: m1 = BetaAdicSet(x^3-x^2-x-1, [0,1,2])
            sage: m1.is_included(m)
            True

        """
        a = getDetAutomaton(self, a)
        if verb:
            print("a=%s"%a)
        b = self.a.zero_complete2()
        b.zero_completeOP()
        if verb:
            print("b=%s"%b)
        m = BetaAdicSet(self.b, a)
        ap = m.proj(b, aut=True)
        if verb:
            print("ap=%s"%ap)
        return ap.equal_languages(b)

    def is_equal(self, a):
        """
        Determine if the ``BetaAdicSet`` is equal to the given``BetaAdicSet``.

        INPUT:

        - ``a`` - ``BetaAdicSet`` to compare

        OUTPUT:

        ``True``  if the BetaAdicSet is equal in the BetaAdicSet given
        by a  ``False`` otherwise
 

        EXAMPLES::

            sage: m = BetaAdicSet(x^3-x^2-x-1, [0,1])
            sage: m1 = BetaAdicSet(x^3-x^2-x-1, [0,1,2])
            sage: m1.is_equal(m)
            True


        """
        a = getBetaAdicSet(self, a)
        return self.is_included(a) and a.is_included(self)

    def is_empty(self):
        """
        Tell if the BetaAdicSet is empty.

        OUTPUT:

        ``True``  if the BetaAdicSet is empty in the BetaAdicSet given
        by a  ``False`` otherwise
 

        EXAMPLES::

            sage: m = BetaAdicSet(x^3-x^2-x-1, [0,1])
            sage: m.is_empty()
            False
            sage: m = BetaAdicSet(3, [])
            sage: m.is_empty()
            True

        """
        return self.a.is_empty()

    def _testSDL(self):
        """
        Open a window to test the SDL library used for graphical representation.

        TESTS::

            sage: m3 = BetaAdicSet(1/(1+I), dag.AnyWord([0, 1]))
            sage: m3._testSDL()
            Video Mode: 800x600 32 bits/pixel
        """
        sig_on()
        TestSDL()
        sig_off()

    def get_la(self, verb=False):
        """
        Return a list of automata corresponding to each final state of the automaton.

        INPUT:

        -``verb`` -- (default ''False'') set to ''True'' for verbose mode

        OUTPUT:
        Return a list of automata.

        EXAMPLES::

            sage: m=BetaAdicSet((1+sqrt(5))/2, dag.AnyWord([0, 1]))
            sage: m.get_la()
            [DetAutomaton with 1 states and an alphabet of 2 letters]
        """
        cdef DetAutomaton a = self.a.copy()
        # compute la
        la = []
        for v in a.states:
            a.set_final_states([v])
            la.append(a.copy())
        return la

#    def points_exact(self, n=None, i=None):
#        r"""
#        Returns a set of exacts values (in the number field of b)
#        corresponding to points of the b-adic set for words of length at most ``n``.
#
#        INPUT:
#
#        - ``n`` - integer (default: ``None``)
#          The number of iterations used to plot the fractal.
#          Default values: between ``5`` and ``16`` depending on the number
#          of generators.
#
#        - ``i`` - integer (default: ``None``)
#          State of the automaton of self taken as the initial state .
#
#        OUTPUT:
#
#            List of numbers, given with exact values.
#
#        EXAMPLES::
#
#            #. The dragon fractal::
#            sage: e = QQbar(1/(1+I))
#            sage: m=BetaAdicSet(e, dag.AnyWord([0, 1]))
#            sage: print(m)
#            b-adic set with b root of x^2 - x + 1/2, and an automaton of 1 states and 2 letters.
#            sage: P = m.points_exact()
#            age: len(P)
#            65536
#            sage: P = m.points_exact(i=0)
#            sage: len(P)
#            65536
#        """
#        K = self.K
#        b = self.b
#        a = self.a
#        A = a.alphabet
#        ng = a.n_letters
#
#        if i is None:
#            i = a.initial_state
#
#        if n is None:
#            if ng == 2:
#                n = 16
#            elif ng == 3:
#                n = 9
#            else:
#                n = 5
#
#        if n == 0:
#            return [0]
#        else:
#            orbit_points = set()
#            V = set([v for c in A for v in [a.succ(i, c)] if v != -1])
#            orbit_points0 = dict()
#            for v in V:
#                orbit_points0[v] = self.points_exact(n=n-1, i=v)
#            for c in A:
#                v = a.succ(i, c)
#                if v is not None:
#                    orbit_points.update([b*p+c for p in orbit_points0[v]])
#        return orbit_points

    def user_draw(self, n=None,
                  sx=800, sy=600, ajust=True, prec=53, color=(0, 0, 0, 255),
                  method=0, simplify=True, mirror=False, only_aut=False, verb=False):
        r"""
        Display a window where the user can draw a b-adic set based on the current b-adic set.
        Use keyboard p to reduce the size of the pen and the keyboard m to increse.
        Draw the figure with the the mouse and click to record the shape.

        INPUT:

        - ``n`` - integer (default: ``None``)
          The number of iterations used to plot the fractal.
          Default values: between ``5`` and ``16`` depending on the number
          of generators.

        - ``sx`` -- integer (default 800) width of the window

        - ``sy`` -- integer (default 600) height of the window

        - ``ajust``  -- boolean (default ``True``) If True, change the zoom in order to fit the window.

        - ``prec`` -- integer (default: ``53``) precision of computed values

        - ``color`` tuple of color in RGB values -- (default: (0, 0, 0, 255))

        - ``method`` -- (default: ``0``) For futur implementations, must be 0 for the moment.

        - ``simplify`` -- (default: ``True``) If True, minimize the result

        - ``only_aut`` -- (default: ``False``) If True return a DetAutomaton, otherwise return a BetaAdicSet

        - ``verb`` -- (default ``False``) set to ``True`` for verbose mod

        OUTPUT:

        A b-adic set, corresponding to what has been drawn by the user. Or only the automaton if only_aut was True.

        EXAMPLES::

            #. The dragon fractal::

                sage: e = QQbar(1/(1+I))
                sage: m = BetaAdicSet(e, dag.AnyWord([0, 1]))
                # sage: P = m.user_draw()     # long time (360 s)
                # sage: P.string()   # random
                # 'BetaAdicSet((x^2 - x + 1/2).roots(ring=QQbar)[0][0], DetAutomaton([[0, 1], [(0, 0, 0), (0, 0, 1), (1, 17, 1), (2, 0, 0), (2, 0, 1), (3, 0, 0), (3, 13, 1), (4, 0, 1), (5, 4, 1), (6, 5, 0), (7, 6, 0), (8, 7, 0), (9, 8, 1), (10, 9, 0), (11, 10, 1), (12, 1, 0), (12, 11, 1), (13, 15, 0), (13, 12, 1), (14, 0, 0), (15, 2, 0), (15, 14, 1), (16, 2, 0), (17, 16, 0), (18, 16, 1)]], i=3, final_states=[0]))'


        """
        cdef BetaAdic b
        cdef Automaton a
        cdef DetAutomaton r
        b = getBetaAdic(self, prec=prec, mirror=mirror, verb=verb)
        # if verb:
        #    printAutomaton(b.a)
        # dessin
        cdef Color col
        col.r = color[0]
        col.g = color[1]
        col.b = color[2]
        col.a = color[3]
        if n is None:
            n = -1
        if method == 0:
            sig_on()
            a = UserDraw(b, sx, sy, n, ajust, col, self.a.spectral_radius(), verb)
            sig_off()
        elif method == 1:
            print("Not implemented !")
            return
        r = DetAutomaton(None)
        r.a[0] = a
        r.A = self.a.A
        r.S = range(a.n)
        if simplify:
            r = r.minimize()
        if only_aut:
            return r
        else:
            return BetaAdicSet(self.b, r)

    def draw_zoom(self, n=None, int sx=800, int sy=600,
                  bool ajust=True, int prec=53, color=(0, 0, 0, 255),
                  int method=0, int nprec=4, bool mirror=False, bool verb=False):
        r"""
        Display the BetaAdicSet in a window, with possibility for the user to zoom in.
        Use 'p' to zoom in, 'm' to zoom out, the arrows to translate the view, and 'Esc' to quit.
        You can also select a zone to zoom in with the mouse.

        INPUT:

        - ``n`` - integer (default: ``None``)
          The number of iterations used to plot the fractal.
          Default values: between ``5`` and ``16`` depending on the number
          of generators.

        - ``sx``  -- (default 800)

        - ``sy``  -- (default 600)

        - ``ajust``  -- (default ``True``)

        - ``prec``  precision of returned values -- (default: ``53``)

        - ``color`` tuple of color in RGB values -- (default: (0, 0, 0, 255))

        - ``method`` int -- (default 0)

        - ``nprec`` int -- (default 4) - additional iterations for the drawing (if ``n`` is None).

        - ``mirror`` bool -- (default ``False) st to ``True`` to to the mirror

        - ``verb`` -- (default ``False``) set ti ``True`` for verbose mod

        OUTPUT:

        A word that corresponds to the place where we draw.

        EXAMPLES::

            #. The dragon fractal::

                sage: m = BetaAdicSet(1/(1+I), [0, 1])
                sage: P = m.draw_zoom()     # not tested
            
            #. Zoom in a complicated Rauzy fractal

                sage: s = WordMorphism('1->2,2->3,3->12')
                sage: m = s.DumontThomas().mirror(); m
                sage: m.draw_zoom()         # not tested

        """
        cdef BetaAdic b
        b = getBetaAdic(self, prec=prec, mirror=mirror, verb=verb)
        # dessin
        cdef int *word
        cdef Color col
        cdef int i
        col.r = color[0]
        col.g = color[1]
        col.b = color[2]
        col.a = color[3]
        if n is None:
            n = -1
        if method == 0:
            sig_on()
            word = DrawZoom(b, sx, sy, n, ajust, col, nprec, self.a.spectral_radius(), verb)
            sig_off()
            res = []
            if word is not NULL:
                for i in xrange(1024):
                    if word[i] < 0:
                        break
                    res.append(self.a.alphabet[word[i]])
                res.reverse()
            return res
        elif method == 1:
            print("Not implemented !")
            return None

    def plot(self, n=None, sx=800, sy=600,
             ajust=True, prec=53, color=(0, 0, 0, 255),
             method=0, nprec=4, mirror=False, verb=False):
        r"""
        Draw the beta-adic set.

        INPUT:

        - ``n`` - integer (default: ``None``)
          The number of iterations used to plot the fractal.
          Default values: between ``5`` and ``16`` depending on the
          number of generators.

        - ``place`` - place of the number field of beta (default: ``None``)
          The place used to evaluate elements of the number field.

        - ``sx`` -- (default: 800) dimensions of the resulting in x dimension

        - ``sy`` -- (default : 600) dimensions of the resulting
          in y dimension image

        - ``ajust`` boll - (default: ``True``) adapt the drawing
          to fill all the image,
          with ratio 1 (default: ``True``)

        - ``prec`` - precision of returned values (default: ``53``)

        - ``color`` - list of three integer between 0
          and 255 (default: ``(0,0,255,255)``) Color of the drawing.

        - ``method`` int -- (default : 0)

        - ``mirror`` bool -- (default ``False) st to ``True`` to to the mirror

        - ``nprec`` int -- (default 4) - additionnal iterations

        - ``verb`` - bool (default: ``False``)
          Print informations for debugging.

        OUTPUT:

            A Graphics object.

        EXAMPLES::

        #. The dragon fractal::

            sage: m = BetaAdicSet(1/(1+I), dag.AnyWord([0,1]))
            sage: m.plot()

        #. Another dragon fractal::

            sage: b = (2*x^2+x+1).roots(ring=CC)[0][0]
            sage: m = BetaAdicSet(b, dag.AnyWord([0,1]))
            sage: m.plot()
            <PIL.Image.Image image mode=RGBA size=800x600 at 0x7FABDBBDCC90>

        #. The Rauzy fractal of the Tribonacci substitution::

            sage: s = WordMorphism('1->12,2->13,3->1')
            sage: m = s.DumontThomas()
            sage: m.plot()
            <PIL.Image.Image image mode=RGBA size=800x600 at 0x7FABDC35B1D0>


        #. The Rauzy fractal of the flipped Tribonacci substitution::

            sage: s = WordMorphism('1->12,2->31,3->1')
            sage: m = s.DumontThomas()
            sage: m.plot()

        #. A non-Pisot Rauzy fractal::

            sage: s = WordMorphism({1:[3,2], 2:[3,3], 3:[4], 4:[1]})
            sage: m = s.DumontThomas()
            sage: m.plot()
            sage: m = BetaAdicSet(1/m.b, m.a)
            sage: m.plot()

        #. A part of the boundary of the dragon fractal::

            sage: m = BetaAdicSet(1/(1+I), dag.AnyWord([0,1]))
            sage: mi = m.intersection_words(w1=[0], w2=[1])
            sage: mi.plot(nprec=6)

        #. A part of the boundary of the "Hokkaido" fractal::

            sage: s = WordMorphism('a->ab,b->c,c->d,d->e,e->a')
            sage: m = s.DumontThomas()
            sage: mi = m.intersection_words(w1=[0], w2=[1])
            sage: mi.plot()

        #. A limit set that look like a tiling but with holes::

            sage: P=x^4 + x^3 - x + 1
            sage: b = P.roots(ring=QQbar)[2][0]
            sage: m = BetaAdicSet(b, dag.AnyWord([0,1]))
            sage: m.plot()

        """
        cdef Surface s
        cdef BetaAdic b
        cdef Automaton aut
        cdef int i,j
        sig_on()
        s = NewSurface(sx, sy)
        sig_off()
        sig_on()
        b = getBetaAdic(self, prec=prec, mirror=mirror, verb=verb)
        sig_off()
        if verb:
            print("b=%s+%s*I", b.b.x, b.b.y)
            print("n=%s" % b.n)
            for i in range(b.n):
                print("t[%s] = %s+%s*I" % (i, b.t[i].x, b.t[i].y))
            # print("a=%s"%b.a)
            for i in range(b.a.n):
                if b.a.e[i].final:
                    print("(%s) " % i)
                else:
                    print("%s " % i)
            aut = b.a;
            for i in range(aut.n):
                for j in range(aut.na):
                    print("%s -%s-> %s\n" % (i, j, aut.e[i].f[j]))
        cdef Color col
        col.r = color[0]
        col.g = color[1]
        col.b = color[2]
        col.a = color[3]
        if n is None:
            n = -1
        if method == 0:
            sig_on()
            Draw(b, s, n, ajust, col, nprec, self.a.spectral_radius(), verb)
            sig_off()
        elif method == 1:
            raise NotImplementedError("Method 1 not implemented !")
        sig_on()
        im = surface_to_img(s)
        sig_off()
        if verb:
            print("Free...")
        sig_on()
        FreeSurface(s)
        FreeBetaAdic(b)
        sig_off()
        return im

    def plot_list(self, list la=None, n=None,
                  sx=800, sy=600, ajust=True, prec=53, colormap='hsv',
                  backcolor=None, opacity=1., mirror=False,
                  nprec=4, verb=False):
        r"""
        Draw the beta-adic sets with color according to the list of automata given.

        INPUT:

        - ``la``- list (default: ``None``)
          List of automata or BetaAdicSet.

        - ``n`` - integer (default: ``None``)
          The number of iterations used to plot the fractal.
          Default values: between ``5`` and ``16`` depending on the number of generators.

        - ``sx`` -- (default: 800) dimensions of the resulting in x dimension

        - ``sy`` -- (default : 600) dimensions of the resulting
          in y dimension image

        - ``ajust`` bool - (default: ``True``) adapt the drawing to fill all the image, with
          ratio 1 (default: ``True``)

        - ``prec`` - precision of returned values (default: ``53``)

        - ``colormap`` - list of colors (default: ``hsv``)
          Colors of the drawing.

        - ``backcolor`` - (default: ``None``) list of three integer between 0
          and 255  .

        - ``opacity`` float - (default: ``1.``)
          Transparency of the drawing coefficient.

        - ``mirror`` bool -- (default ``False) st to ``True`` to to the mirror

        - ``nprec`` int -- (default 4) - additionnal iterations

        - ``verb`` - bool (default: ``False``)
          Print informations for debugging.

        OUTPUT:

            A Graphics object.

        EXAMPLES::

        #. The Rauzy fractal of the Tribonacci substitution::

            sage: s = WordMorphism('1->12,2->13,3->1')
            sage: m = s.DumontThomas()
            sage: m.plot_list(mirror=True)

        #. A non-Pisot Rauzy fractal::

            sage: s = WordMorphism({1:[3,2], 2:[3,3], 3:[4], 4:[1]})
            sage: m = s.DumontThomas()
            sage: m = BetaAdicSet(1/m.b, m.a)
            sage: m.plot_list(mirror=True)
            sage: m = BetaAdicSet(m.b, m.a.mirror())
            sage: m.plot_list(mirror=True)

        #. The dragon fractal and its boundary::

            sage: m = BetaAdicSet(1/(1+I), dag.AnyWord([0,1]))
            sage: mi = m.intersection_words(w1=[0], w2=[1])
            sage: m.plot_list(la=[mi.a], n=19, colormap=[(.5,.5,.5,.5), (0,0,0,1.)])  # long time

        #. The "Hokkaido" fractal and its boundary::

            sage: s = WordMorphism('a->ab,b->c,c->d,d->e,e->a')
            sage: m = s.DumontThomas()
            sage: mi = m.intersection_words(w1=[0], w2=[1])                # long time
            sage: m.plot_list(la=[mi.a], n=45, colormap='gist_rainbow')  # long time

        #. A limit set that look like a tiling::

            sage: P = x^4 + x^3 - x + 1
            sage: b = P.roots(ring=QQbar)[2][0]
            sage: m = BetaAdicSet(b, dag.AnyWord([0,1]))
            sage: a = m.reduced_word_automaton()
            sage: m = BetaAdicSet(m.b, a.mirror())
            sage: m.plot_list(mirror=True)

        """
        cdef Surface s = NewSurface(sx, sy)
        cdef BetaAdic2 b
        sig_on()
        b = getBetaAdic2(self, la=la, prec=prec, mirror=mirror, verb=verb)
        sig_off()
        # dessin
        if n is None:
            n = -1

        # Manage colors
        if backcolor is None:
            backcolor = (.5, .5, .5, .5)
        cdef ColorList cl
        sig_on()
        cl = NewColorList(b.na)
        if isinstance(colormap, list):
            # if b.na > len(colormap):
            #    raise ValueError("The list of color must contain at least %d elements."%b.na)
            for i in range(b.na):
                if i < len(colormap):
                    cl[i] = getColor(colormap[i])
                else:
                    cl[i] = randColor(255)
        elif isinstance(colormap, str):
            from matplotlib import cm
            if not colormap in cm.datad.keys():
                raise ValueError("Color map %s not known (type 'from matplotlib import cm' and look at cm for valid names)" % colormap)
            colormap = cm.__dict__[colormap]
            cl[0] = getColor(backcolor)
            for i in range(b.na-1):
                cl[i+1] = getColor(colormap(float(i)/float(b.na-1)))
        else:
            raise TypeError("Type of option colormap (=%s) must be list of colors or str" % colormap)
        DrawList(b, s, n, ajust, cl, opacity, self.a.spectral_radius(), nprec, verb)
        sig_off()
        # enregistrement du résultat
        sig_on()
        im = surface_to_img(s)
        sig_off()
        if verb:
            print("Free...")
        sig_on()
        FreeSurface(s)
        if la is None:
            FreeAutomatons(b.a, b.na)
        FreeBetaAdic2(b)
        FreeColorList(cl)
        sig_off()
        return im

    def relations_automaton(self, t=0, bool isvide=False, list Ad=None, list A=None, list B=None,
                             bool couples=False, bool ext=False, mirror=None,
                             bool prune=True, int nhash=1000003, int prec=53, int algo=1, int coeff=1, bool verb=False):
        r"""
        Compute the relation automaton of the beta-adic monoid.
        For beta algebraic integer only.
        If isvide is True, it only checks if the automaton is trivial or not.
        Cd is the set of differences A-B where A and B
        are the alphabets to compare.
        t is the translation of one of the side
        (initial state of the automaton).
        ext : automate des relations à l'infini ou pas.

         INPUT:

        - ``t`` integer (default: 0) is the translation of one of the side

        - ``isvide`` boolean - (default: ''False'') If isvide is True,
          it only checks if the automaton is trivial or not.

        - ``Ad`` - list (default: ``None``)
          Ad alphabet of differences  A-B where A and B
          are the alphabets to compare.

        - ``A`` -  (default: ``None``) alphabet on one side
          (used if Ad is None)

        - ``B`` -  (default: ``None``) alphabet on the other side
         (used if Ad is None)

        - ``couples``  boolean - (default: ''False'')

        - ``ext``  boolean - (default: ''False'')
          where automaton has relations at infinity or not

        - ``mirror``  boolean - (default: ''None'')

        - ``prune`` boolean - (default: ''False'')

        - ``nhash`` int (default: 1000003)

        - ''prec'' int (default:53)

        - ''algo'' int (default: 1) for any one else that 1 use 
          initInfoBetaAdic

        - ``verb`` - bool (default: ``False``)
          Print informations for debugging.

        OUTPUT:
        A DetAutomaton  corresponding to relation

        EXAMPLES::

            sage: e = QQbar(1/(1+I))
            sage: m = BetaAdicSet(e, dag.AnyWord([0,1,3]))
            sage: m.relations_automaton()
            DetAutomaton with 49 states and an alphabet of 7 letters
            sage: m.relations_automaton(algo=0)
            DetAutomaton with 49 states and an alphabet of 7 letters

        """
        cdef InfoBetaAdic ib
        cdef Automaton a
        cdef Element e
        cdef DetAutomaton r
        cdef bool tb

        t0 = t
        if mirror is not None:
            try:
                tb = mirror
            except Exception:
                raise ValueError("mirror=%s must be a bool."%mirror)

        b = self.b
        K = b.parent()
        if not K.is_field():
            raise ValueError("b must live in a field!")
        if not K.is_exact() or not hasattr(K, 'abs_val'):
            raise ValueError("b must live in a number field!")
        pi = b.minpoly()
        pi = pi*pi.denominator()
        # alphabet
        if Ad is None:
            if A is None:
                A = self.a.A
            if B is None:
                B = self.a.A
            Ad = list(set([a1-b1 for a1 in A for b1 in B]))
        else:
            try:
                list(Ad[0])
                Ad = list(set([a1-b1 for a1, b1 in Ad]))
            except Exception:
                pass
        if verb:
            print("Ad=%s" % Ad)
        if algo == 1:
            if mirror is None:
                mirror = True
            if ext:
                b = 1/b
                pi = b.minpoly()
                pi = pi*pi.denominator()
                mirror = not mirror
            # find absolute values for which b is greater than one
            places = []
            narch = 0
            # archimedian places
            for p in K.places(prec=prec):
                if K.abs_val(p, b) > 1:
                    places.append(p)
                    narch+=1
            # ultra-metric places
            from sage.arith.misc import prime_divisors
            lc = pi.leading_coefficient()
            for p in prime_divisors(lc):
                for P in K.primes_above(p):
                    if K.abs_val(P, b, prec=prec) > 1:
                        places.append(P)
            if verb:
                print(places)
            # bounds
            bo = []
            for i, p in enumerate(places):
                if i < narch:
                    bo.append(
                        coeff*max(
                            [K.abs_val(p, x) for x in Ad])/(K.abs_val(p, b) - 1))
                else:
                    bo.append(
                        coeff*max(
                            [K.abs_val(p, x) for x in Ad])/K.abs_val(p, b))
            if verb:
                print("bounds=%s"%bo)
            # compute the automaton
            L = []
            S = [0]  # remaining state to look at
            d = dict()  # states already seen and their number
            d[0] = 0
            c = 1  # count the states seen
            while len(S) > 0:
                S2 = []
                for s in S:
                    for t in Ad:
                        ss = b*s + t
                        # test if we keep ss
                        keep = True
                        for p, m in zip(places, bo):
                            if K.abs_val(p, ss) > m + .00000001:
                                keep = False
                                break
                        if keep:
                            if not d.has_key(ss):
                                S.append(ss)
                                d[ss] = c
                                c += 1
                            L.append((d[s], d[ss], t))
                S = S2
            r = DetAutomaton(L, i=0, final_states=[0])
            if verb:
                print("before pruning: %s" % r)
            if mirror:
                r = r.mirror_det()
            if prune:
                if verb:
                    print("prune...")
                if ext:
                    r = r.prune_inf()
                else:
                    r = r.prune()
            if ext:
                r.set_final_states(range(r.a.n))
        elif algo == 2:
            if mirror is None:
                mirror = False
            sig_on()
            ib = initInfoBetaAdic(self, Ad=Ad, plus=False, nhash=nhash, verb=verb)
            e = NewElement(ib.n)
            K = self.b.parent()
            t = K(t)
            getElement(t, e, ib.n)
            a = RelationsAutomatonT(&ib, e, isvide, ext, verb)
            r = DetAutomaton(None)
            r.a[0] = a
            if verb:
                print("a (%s etats)" % a.n)
                print("Free element...")
            FreeElement(e)
            r.A = Ad
            if verb:
                print("Free InfoBetaAdic...")
            freeInfoBetaAdic(&ib)
            sig_off()
            if isvide:
                return a.na != 0
            if prune:
                if verb:
                    print("prune...")
                if ext:
                    r = r.prune_inf()
                    r.set_final_states(r.states)
                else:
                    r = r.prune()
            if mirror:
                r = r.mirror_det()
        else:
            if mirror is None:
                mirror = False
            # find absolute values for which b is less than one
            places = []
            narch = 0
            # archimedian places
            for p in K.places(prec=prec):
                if K.abs_val(p, b) < 1:
                    places.append(p)
                    narch+=1
            # ultra-metric places
            from sage.arith.misc import prime_divisors
            for p in prime_divisors(pi(0)):
                for P in K.primes_above(p):
                    if K.abs_val(P, b, prec=prec) < 1:
                        places.append(P)
            if verb:
                print(places)
            # bounds
            bo = []
            for i, p in enumerate(places):
                if i < narch:
                    bo.append(
                        coeff*max(
                            [K.abs_val(p, x) for x in Ad])/(1 - K.abs_val(p, b)))
                else:
                    bo.append(
                        coeff*max([K.abs_val(p,x) for x in Ad]))
            if verb:
                print("bounds=%s" % bo)
            # compute the automaton
            L = []
            S = [0]  # remaining state to look at
            d = dict()  # states already seen and their number
            d[0] = 0
            c = 1  # count the states seen
            while len(S) > 0:
                S2 = []
                for s in S:
                    for t in Ad:
                        ss = (s - t)/b
                        # test if we keep ss
                        keep = True
                        for p, m in zip(places, bo):
                            if K.abs_val(p, ss) > m + .00000001:
                                if verb:
                                    print("|%s|=%s > %s"
                                          % (ss, K.abs_val(p, ss), m))
                                keep = False
                                break
                        if keep:
                            if not d.has_key(ss):
                                S.append(ss)
                                d[ss] = c
                                c += 1
                            L.append((d[s], d[ss], t))
                            # L.append((s, ss, t))
                S = S2
            r = DetAutomaton(L, i=0, final_states=[0])
            if verb:
                print("before pruning: %s" % r)
            if mirror:
                r = r.mirror_det()
            if prune:
                if verb:
                    print("prune...")
                if ext:
                    r = r.prune_inf()
                else:
                    r = r.prune()
            if ext:
                r.set_final_states(range(r.a.n))
        if couples:
            if A is None or B is None:
                raise ValueError("Alphabets A and B must be defined !")
            d = {}
            for c1 in A:
                for c2 in B:
                    if not d.has_key(c1-c2):
                        d[c1-c2] = []
                    d[c1-c2].append((c1, c2))
            if verb:
                print(d)
            r = r.duplicate(d, verb=verb)
        return r

    def critical_exponent_aprox(self, niter=10, verb=False):
        """
        print a approximated value of the critical exponent
        INPUT:

        - ``niter`` int (default: 10) number of iterations

        - ``verb`` - bool (default: ``False``)
          verbose mode

        OUTPUT:
        print a approximated value of the critical exponent

        EXAMPLES::

        #.  sage: m = BetaAdicSet(1/(1+I), dag.AnyWord([0,1]))
            sage: m.critical_exponent_aprox()
            2.00000000000000

        #.  sage: s = WordMorphism('1->12,2->13,3->1')
            sage: m = s.DumontThomas()
            sage: m.critical_exponent_aprox()
            2.09949525214019

        """
        cdef set S, S2, S3
        b = self.b
        K = b.parent()
        A = self.a.alphabet
        S = set([K.zero()])
        for i in range(niter):
            S2 = set([])
            for s in S:
                for c in A:
                    S2.add((s+c)/b)
            # intervertit S et S2
            S3 = S2
            S2 = S
            S = S3
            if verb:
                print(len(S))
        # from sage.functions.log import log
        print("%s" % (log(len(S)).n() / (niter * log(mahler(b.minpoly()).n()))))

    def complexity(self, Ad=None, prec=None, verb=False):
        r"""
        Return a estimation of an upper bound of the number of states
        of the relations automaton.

        INPUT:

         - ``verb`` - Boolean (default: False) Display informations for debug.

        OUTPUT:

        A positive real number.

        EXAMPLES::

            sage: b = (x^3-x^2-x-1).roots(ring=QQbar)[1][0]
            sage: m = BetaAdicSet(b, dag.AnyWord([0,1]))
            sage: m.complexity()
            108.523461214115
        """
        b = self.b
        K = b.parent()
        pi = b.minpoly()
        pi = pi*pi.denominator()

        if verb:
            print(K)

        A = self.a.A
        if Ad is None:
            Ad = list(set([c1-c2 for c1 in A for c2 in A]))

        # find absolute values for which b is greater than one
        places = []
        narch = 0
        # archimedian places
        for p in K.places(prec=prec):
            if K.abs_val(p, b) > 1:
                places.append(p)
                narch += 1
        # ultra-metric places
        from sage.arith.misc import prime_divisors
        lc = pi.leading_coefficient()
        for p in prime_divisors(lc):
            for P in K.primes_above(p):
                if K.abs_val(P, b, prec=prec) > 1:
                    places.append(P)
        if verb:
            print(places)
        # bounds
        bo = []
        vol = 1.
        for i, p in enumerate(places):
            if i < narch:
                bo.append(
                    max([K.abs_val(p, x) for x in Ad])/(K.abs_val(p, b) - 1))
                if verb:
                    print("bo = %s" % bo[-1])
                if p(b).imag() == 0:
                    vol *= 2*bo[-1]
                else:
                    vol *= pi_number*bo[-1]^2
            else:
                bo.append(max([K.abs_val(p, x) for x in Ad])/K.abs_val(p, b))
                vol *= bo[-1]
        if verb:
            print("bounds=%s" % bo)
        # from sage.functions.other import ceil
        return ceil(vol)

    def intersection(self, BetaAdicSet m, t=0, ext=False, algo=2, verb=False):
        r"""
        Compute the intersection of two beta-adic sets.

        INPUT:

        - ``m`` - the other beta-adic set

        - ``t`` - translate m by t

        - ``ext`` - bool (default: ``False``)
          If True, compute the extended relations automaton.

        - ``verb``- bool (default: ``False``)
          If True, verbose mode.

        OUTPUT:

        A BetaAdicSet.

        EXAMPLES::

            #. Compute the boundary of the dragon fractal (see intersection_words for an easier way) ::

                sage: m = BetaAdicSet(1/(1+I), dag.AnyWord([0,1]))
                sage: m1 = m.prefix([0])
                sage: m2 = m.prefix([1])
                sage: mi = m1.intersection(m2, ext=True)
                sage: mi
                b-adic set with b root of x^2 - x + 1/2, and an automaton of 21 states and 2 letters.
                sage: mi.plot(mirror=False)
        """
        cdef DetAutomaton a, ar, ai

        if self.b != m.b:
            raise ValueError("The two beta-adic sets must have same beta.")

        a = self.a.zero_complete2().product(m.a.zero_complete2()).prune().minimize()
        if verb:
            print("Product = %s" % a)

        ar = self.relations_automaton(ext=ext, t=t, algo=algo, couples=True, A=self.a.A, B=m.a.A, verb=verb)
        if verb:
            print("Arel = %s" % ar)

        ai = ar.intersection(a)
        if verb:
            print("ai = %s" % ai)

        ai = ai.proji(0)
        if verb:
            print("ai = %s" % ai)

        if ext:
            ai = ai.prune_inf()
        else:
            ai = ai.prune().minimize()
        ai.zero_completeOP()
        return BetaAdicSet(self.b, ai)

    def prefix(self, w):
        """
        Compute the prefix of word ``w``

        INPUT:

        - ``w`` - list  word to get prefix

        OUTPUT:

        DetAutomaton.

        EXAMPLES::

            sage: pi = x^3-x^2-x-1
            sage: b = pi.roots(ring=QQbar)[1][0]
            sage: m = BetaAdicSet(b, dag.AnyWord([0,1]))
            sage: m.prefix([0, 1, 1, 1])
            b-adic set with b root of x^3 - x^2 - x - 1, and an automaton of 5 states and 2 letters.

        """
        return BetaAdicSet(self.b, self.a.prefix(w))

    def intersection_words(self, w1, w2, ext=True, verb=False):
        r"""
        Compute the intersection of the two beta-adic sets corresponding to
        words with prefix w1 and prefix w2.

        INPUT:

        - ``w1``- word
          The first prefix.

        - ``w2``- word
          The second prefix.

        OUTPUT:

        A Automaton.

        EXAMPLES::

            #. Compute the boundary of the dragon fractal::

                sage: e = QQbar(1/(1+I))
                sage: m = BetaAdicSet(e, dag.AnyWord([0,1]))
                sage: m.intersection_words(w1=[0], w2=[1])
                Finite automaton with 21 states

            #. Draw the intersection of two sub-sets of a limit set::

                sage: m = BetaAdicSet(1/(1+I), dag.AnyWord([0,1]))
                sage: ssi = m.intersection_words(w1=[0], w2=[1])
                sage: m.plot(n=10, ss=ssi)                        # long time
        """
        m1 = self.prefix(w1)
        m2 = self.prefix(w2)
        mi = m1.intersection(m2, ext=ext, verb=verb)
        return mi

    # to be put in generators
    #     - ``aut`` - DetAutomaton (default: ``None``, full language)
    #       Automaton describing the language in which we live.
    def reduced_words_automaton(self, full=False, step=100,
                                mirror=False, verb=False):  # , DetAutomaton aut=None):
        r"""
        Compute the reduced words automaton of the ``BetaAdicSet``
        (without considering the automaton of authorized words).
        See http://www.latp.univ-mrs.fr/~paul.mercat/Publis/
        Semi-groupes%20fortement%20automatiques.pdf for a definition of such automaton.
        Use fast C-functions but works only for algebraic integer.
        (Consider using reduced_words_automaton() if you're not in this case.)

        INPUT:

        - ``step`` - int (default: 100)
          number of steps

        - ``verb`` - bool (default: ``False``)
          If True, print informations for debugging.

        - ``transpose`` - bool (default: ``False``)


        OUTPUT:

        DetAutomaton.

        EXAMPLES::

            sage: pi = x^3-x^2-x-1
            sage: b = pi.roots(ring=QQbar)[1][0]
            sage: m = BetaAdicSet(b, dag.AnyWord([0,1]))
            sage: ared = m.reduced_words_automaton()
            sage: ared
            DetAutomaton with 4 states and an alphabet of 2 letters

        """
        cdef list A
        cdef list Ad
        cdef list Adp
        cdef int nAd, nA
        cdef DetAutomaton arel
        cdef int ne, ei

        A = self.a.A
        nA = len(A)

        if full:
            # compute the relations automaton
            arel = self.relations_automaton(mirror=mirror)
            if verb:
                print("arel = %s" % arel)
            if step == 1:
                return arel

            # add a new state
            ei = arel.a.i
            ne = arel.a.n  # new added state
            arel.add_state(True)
            arel.set_final_state(ei, final=False)  # the new state is final
            if step == 2:
                return arel

            Ad = arel.A
            nAd = len(Ad)

            # add edges from the new state (copy edges from the initial state)
            for j in range(nAd):
                arel.set_succ(ne, j, arel.succ(ei, j))
            if step == 3:
                return arel

            Adp = [i for i in range(
                nAd) if Ad[i] in [x-y for j, x in enumerate(A) for y in A[:j]]]

            # suppress some edges from the initial state
            for j in Adp:
                arel.set_succ(ei, j, -1)
            if step == 4:
                return arel

            # change edges that point to the initial state :
            # make them point to the new state
            for e in arel.states:
                if e != ei:
                    for j in range(nAd):
                        if arel.succ(e, j) == ei:
                            arel.set_succ(e, j, ne)
            if step == 5:
                return arel

            # project, determinise and take the complementary
            d = {}
            for a in A:
                for b in A:
                    if not d.has_key(a - b):
                        d[a-b] = []
                    d[a-b].append((a, b))
            if verb:
                print(d)
            arel = arel.duplicate(d)  # replace differences with couples
            d = {}
            for j in A:
                for i in A:
                    d[(i, j)] = i
            if verb:
                print(d)
                print(arel)
            arel = arel.determinize_proj(d, noempty=False, nof=True)  # , verb=True)
            # project on the first value of the couple, determinise and take the complementary
            if verb:
                print(arel)
            arel = arel.prune()
            if step == 10:
                return arel
            return arel.minimize()
        else:
            arel = self.relations_automaton(couples=True, ext=False)
            if verb:
                print("arel=%s" % arel)
            ap = self.a.product(self.a)
            if verb:
                print("ap=%s" % ap)
            ai = ap.intersection(arel)
            if verb:
                print("ai=%s" % ai)
            alex = DetAutomaton([(0, 0, (i, i)) for i in A]
                                + [(0, 1, (A[i], A[j]))
                                   for i in range(nA) for j in range(i)]
                                + [(1, 1, (i, j)) for i in A for j in A],
                                i=0, final_states=[1])
            if verb:
                print("alex=%s" % alex)
            ai = ai.intersection(alex)
            if verb:
                print("ai=%s" % ai)
            ai = ai.proji(0)
            if verb:
                print("ai=%s" % ai)
            ai.complementary_op()
            if verb:
                print("ai=%s" % ai)
            return ai.intersection(self.a)

    def reduced(self, mirror=False, verb=False):
        r"""
        Compute the reduced  of the ``BetaAdicSet``


        INPUT:

        - ``mirror`` bool -- (default ``False) st to ``True`` to to the mirror

        - ``verb`` - bool (default: ``False``)
          If True, print informations for debugging.


        OUTPUT:

        DetAutomaton.

        EXAMPLES::

            sage: pi = x^3-x^2-x-1
            sage: b = pi.roots(ring=QQbar)[1][0]
            sage: m = BetaAdicSet(b, dag.AnyWord([0,1]))
            sage: ared = m.reduced()
            sage: ared
        """
        return BetaAdicSet(self.b, self.reduced_words_automaton(mirror=mirror,
                                                                verb=verb))

#     def reduced_words_automaton(self, ss=None, Iss=None, ext=False,
#                                 verb=False, step=None, arel=None):
#         r"""
#         Compute the reduced words automaton of the beta-adic monoid (with or without subshift).
#         See http://www.latp.univ-mrs.fr/~paul.mercat/Publis/Semi-groupes%20fortement%20automatiques.pdf for a definition of such automaton (without subshift).
# 
#         WARNING: It seems there is a bug : result may be incorrect if ss is not None.
# 
#         INPUT:
# 
#         - ``ss``- Automaton (default: ``None``)
#           The first subshift to associate to the beta-adic monoid for this operation.
# 
#         - ``Iss``- set of states of ss (default: ``None``)
# 
#         - ``ext`` - bool (default: ``True``)
#           If True, compute the extended relations automaton (which permit to describe infinite words in the monoid).  
# 
#         - ``verb`` - bool (default: ``False``)
#           If True, print informations for debugging.
# 
#         - ``step`` - int (default: ``None``)
#           Stop to a intermediate state of the computing to make verifications.
# 
#         - ``arel`` - Automaton (default: ``None``)
#           Automaton of relations.
#
#         OUTPUT:
#
#         A Automaton.
#
#         EXAMPLES::
#
#             #. 3-adic expansion with numerals set {0,1,3}::
#
#                 sage: m = BetaAdicSet(3, {0,1,3})
#                 sage: mr = m.reduced()
#                 Finite automaton with 2 states
#
#             #. phi-adic expansion with numerals set {0,1}::
#
#                 sage: m = BetaAdicSet((1+sqrt(5))/2, {0,1})
#                 sage: m.reduced_words_automaton()
#                 Finite automaton with 3 states
#
#             #. beta-adic expansion with numerals set {0,1} where beta is the plastic number::
#                 sage: b = (x^3-x-1).roots(ring=QQbar)[0][0]
#                 sage: m = BetaAdicSet(b, {0,1})
#                 sage: m.reduced_words_automaton()        # long time
#                 Finite automaton with 5321 states
#         """
#         if ss is None:
#             if hasattr(self, 'ss'):
#                 ss = self.ss
#                 if hasattr(self.ss, 'I'):
#                     Iss = self.ss.I
#
#         if step is None:
#             step = 1000
#
#         K = self.C[0].parent()
#
#         if verb:
#             print("Computation of relations's automata")
#             # "Calcul de l'automate des relations..."
#
#         if arel is None:
#             a = self.relations_automaton(noss=True)
#         else:
#             a = arel
#
#         if verb:
#             print(" -> %s" % a)
#
#         if step == 1:
#             return ("relations's automata", a)
#
#         # add a state copy of K.0 (it will be the new initial state)
#         a.add_vertex('O')
#
#         #        #add transitions to K.0 to 'O'
#         #        for f, d, l in a.incoming_edges(K.zero(), labels=True):
#         #            if f == K.zero():
#         #                a.add_edge('O', 'O', l)
#         #            else:
#         #                a.add_edge(f, 'O', l)
# 
#         # subset of positives labels
#         Cdp = []
#         for i in range(self.C.cardinality()):
#             for j in range(i):
#                 Cdp += [self.C[i] - self.C[j]]
#
#         # redirect positives transitions from K.0
#         for f, d, l in a.outgoing_edges(K.zero(), labels=True):
#             if l in Cdp:
#             #                a.delete_edge(K.zero(), d, l)
#                 # add the edge
#                 a.add_edge('O', d, l)
#
#         a.add_edge('O', 'O', a.edge_label(K.zero(), K.zero()))
#
#         if verb:
#             print(a.incoming_edges(K.zero(), labels=True))
#
#         # remove outgoing edges from K.0 (except from K.0 to K.0)
#         for f, d, l in a.outgoing_edges(K.zero(), labels=True):
#             if f != d:
#                 a.delete_edge(f, d, l)
#
#         if step == 2:
#             a.I = ['O']
#             a.F = Set([K.zero()])
#             return ("automaton of ordoned relations", a)
#         a.pruneI(I=['O'])
# 
#         if step == 3:
#             return ("pruned automaton of ordoned relations", a)
# 
#         if ss is not None:  # not full sub-shift
#             if Iss is None:
#                 Iss = [ss.vertices()[0]]
#             # maps actual edges to the list of corresponding couple
#             m = dict([])
#             for c in self.C:
#                 for c2 in self.C:
#                     if m.has_key(c - c2):
#                         m[c-c2] += [(c, c2)]
#                     else:
#                         m[c-c2] = [(c, c2)]
#             # if verb: print "m=%s"%m
# 
#             # calculate the 'product to the right' of a with ss
#             d = dict([])
#             La = a.edge_labels()
#             Lss = ss.edge_labels()
#             for ka in La:
#                 for kss in Lss:
#                     d[(ka, kss)] = None
#                     for k in m[ka]:
#                         if k[1] == kss:
#                             d[(ka, kss)] = k[0]
#                             break
# 
#             # if verb: print "d=%s"%d
#             if verb:
#                 # "avant produit : a=%s (%s etats)"%(a, a.num_verts())
#                 print(" before product : a=%s (%s states)" % (a, a.num_verts()))
#             a = a.product(A=ss, d=d)
#             if verb:
#                 print(" after product : a=%s" % a)
#             if step == 4:
#                 return ("non reduce general words automata", a) #"automate des mots généraux non réduits", a)
# 
#             I = [('O', i) for i in Iss]
#             nof = Set([(K.zero(), i) for i in ss.vertices()])
# 
#             # if verb: print "I=%s, F=%s"%(I, nof)
# 
#             if ext:
#                 # a.emondeI(I=I)
#                 # a.emonde0(I=I) #pour retirer les états puits
#                 a = a.emonde0_simplify(I=I)
#             else:
#                 a = a.emonde0_simplify(I=I)
#                 a.emonde(I=I, F=nof)
#             # a.emondeI(I=I)
#             # a.emondeF(F=nof)
#             # if step == 4:
#             #    return ("automate des mots généraux non réduits, émondé", a)
#             # a.emondeF(F=nof)
# 
#             if verb:
#                 print("After emondation : a=%s" % a)
#             if step == 5:
#                 return("emonded automaton of non reducted general words", a)
# 
#             # return a
#         else:
#             # maps actual edges to element of self.C (the left part when writted c-c2)
#             m = dict([])
#             for c in self.C:
#                 for c2 in self.C:
#                     if m.has_key(c-c2):
#                         m[c-c2] += [c]
#                     else:
#                         m[c-c2] = [c]
#             # if verb: print "m=%s"%m
# 
#             a.allow_multiple_edges(True)
#             # replace each label by its mapping
#             for f, d, l in a.edges():
#                 a.delete_edge(f, d, l)
#                 for l2 in m[l]:
#                     a.add_edge(f, d, l2)
# 
#             I = ['O']
#             nof = Set([K.zero()])
# 
#         a.I = I
#         a.F = nof
#         a.C = self.C
# 
#         if verb:
#             print("Before determinisation : a=%s" % a)
#         if step == 6:
#             return ("emonded automaton of non reducted general words", a)
# 
#         # rend l'automate plus simple
#         a = a.emonde0_simplify()
# 
#         if verb:
#             print("simplification : a=%s" % a)
# 
#         if verb:
#             print("Determinization...")
#         # determinize
#         ad = a.determinize2(nof=a.F)
#         # ad = a.determinize(nof=a.F, verb=False)
#         # ad = a.determinize(I, self.C, nof, verb=verb)
# 
#         if verb:
#             print(" -> %s" % ad)
#         if step == 7:
#             return ("automate des mots généraux réduits", ad)
# 
#         if ss is not None:  # not full sub-shift
#             # calculate the intersection with ss
#             ad = ad.emonde0_simplify()
#             ad = ad.intersection(ss)
#             if verb:
#                 print("after intersection : a=%s" % ad)
# 
#         if step == 8:
#             return ("automaton of reduces words", ad)
# 
#         # F2=[e for e in a.vertices() nof in e[0]]
#         # if verb: print "I2=%s"%I2 #, F2=%s"%(I2,F2)
#         ad.A = self.C
#         # ad.emondeI(I=I2) #, F=F2)
#         ad = ad.emonde0_simplify()
#         ad.F = ad.vertices()
# 
#         if verb:
#             print("after emondation : a=%s" % ad)
#         if step == 9:
#             return ("emonded automaton of reduced words", ad)
#
#         return ad

    def critical_exponent_free(self, prec=None, verb=False):
        r"""
        Compute the critical exponent of the beta-adic set,
        assuming it is free (or reduced, i.e. there is no relation).
        When the beta-adic set is moreover algebraic,
        this critical exponent is equal to the Hausdorff
        dimension of the limit set on the contracting space.

        Rk: beta-adic sets coming from WordMorphism.DumontThomas()
        are always free and algebraic.

        INPUT:

        - ``prec``- precision (default: ``None``)

        - ``verb``- bool (default: ``False``)
          If True, print informations for debugging.

        OUTPUT:

        A real number.

        EXAMPLES::

            #. Hausdorff dimension of limit set of 3-adic expansion with numerals set {0,1,3}::

                sage: m = BetaAdicSet(3, dag.AnyWord([0,1,3]))
                sage: mr = m.reduced()
                sage: mr.critical_exponent_free()
                log(y)/log(|3|) where y is the max root of x^2 - 3*x + 1
                0.8760357589...

            #. Hausdorff dimension of limit set of phi-adic expansion with numerals set {0,1}::

                sage: m = BetaAdicSet((1+sqrt(5))/2, dag.AnyWord([0,1]))
                sage: m = m.reduced()
                sage: m.critical_exponent_free()
                log(y)/log(|b|) where y is the max root of x^2 - x - 1
                1.0000000000...

            #. Hausdorff dimension of the boundary of the dragon fractal::

                sage: m = BetaAdicSet(1/(1+I), dag.AnyWord([0,1]))
                sage: mi = m.intersection_words(w1=[0], w2=[1])
                sage: mi.critical_exponent_free()
                log(y)/log(|b|) where y is the max root of x^3 - x^2 - 2
                1.5236270862...

            #. Hausdorff dimension of the boundary of a Rauzy fractal::

                sage: s = WordMorphism('1->12,2->13,3->1')
                sage: m = s.DumontThomas()
                sage: mi = m.intersection_words(w1=[0], w2=[1])
                sage: mi.critical_exponent_free()
                log(y)/log(|b|) where y is the max root of x^4 - 2*x - 1
                1.0933641642...

            #. Hausdorff dimension of a non-Pisot Rauzy fractal::

                sage: s = WordMorphism({1:[3,2], 2:[3,3], 3:[4], 4:[1]})
                sage: m = s.DumontThomas()
                sage: m2 = BetaAdicSet(1/m.b, m.a.mirror())
                sage: m.critical_exponent_free()
                log(y)/log(|1/2*b^2 - 1/2*b + 1/2|) where y is the max root of x^3 - x^2 + x - 2
                1.5485260383...
        """
        M = self.a.adjacency_matrix()
        if verb:
            print("Eigen values...")
        e = M.eigenvalues()
        if verb:
            print("max...")
        y = max(e, key=abs)
        if verb:
            print("")
        m = mahler(self.b.minpoly())
        print("log(y)/log(%s) where y is the max root of %s, and %s is root of %s." % (m, QQbar(y).minpoly(), m, m.minpoly()))
        y = y.n(prec)
        # from sage.functions.log import log
        m = m.n(prec)
        if verb:
            print("y=%s, m=%s" % (y, m))
        return log(y) / log(m)

    def critical_exponent(self, prec=None, verb=False):
        r"""
        Compute the critical exponent of the beta-adic set.
        If the beta-adic set is algebraic and conformal, then it is equal
        to the Hausdorff dimension of the limit set in the
        contracting space (R or C). If the beta-adic set is algebraic but not conformal,
        then this critical exponent is equal to the dimension of the limit set
        in the contracting space (product of R, C and p-adic spaces), for an appropriate notion of dimension.

        INPUT:

        - ``prec``- precision (default: ``None``)

        - ``verb``- bool (default: ``False``)
          If True, print informations for debugging.

        OUTPUT:

        A real number.

        EXAMPLES::

            #. Hausdorff dimension of limit set of 3-adic expansion with numerals set {0, 1, 3}::

                sage: m = BetaAdicSet(3, dag.AnyWord([0,1,3]))
                sage: m.critical_exponent()
                log(y)/log(3) where y is the max root of x^2 - 3*x + 1
                0.8760357589...

            #. Hausdorff dimension of limit set of phi-adic expansion with numerals set {0, 1}::

                sage: m = BetaAdicSet((1+sqrt(5))/2, dag.AnyWord([0,1]))
                sage: m.critical_exponent()
                log(y)/log(|b|) where y is the max root of x^2 - x - 1
                1.0000000000...

            #. A non-conformal example::

                sage: P = x^7 - 2*x^6 + x^3 - 2*x^2 + 2*x - 1
                sage: b = P.roots(ring=QQbar)[3][0]
                sage: m = BetaAdicSet(b, dag.AnyWord([0,1]))
                sage: m.critical_exponent()                    # long time
                log(y)/log(|b|) where y is the max root of x^11 - 2*x^10 - 4*x^2 + 8*x + 2
                3.3994454205...

            #. See more examples with doc critical_exponent_free()

        """
        if verb:
            print("Computation of reduce words' automata")
        m = self.reduced(verb=verb)
        return m.critical_exponent_free(prec=prec, verb=verb)

#    # test if 0 is an inner point of the limit set
#    def ZeroInner(self, verb=False):
#
#        if not hasattr(self, 'ss'):
#            self.ss = self.default_ss()
#
#        if verb:
#            print("relations automaton...")
#
#        ar = self.relations_automaton(ext=True)
#        ar.complementary()
#
#        if verb:
#            print("complementary : %s" % ar)
#        # return ar
#
#        a = self.default_ss().product(self.ss)
#
#        if verb:
#            print("a = %s" % a)
#        # return a
#
#        # a = ar.intersection(a)
#
#        if verb:
#            print("product...")
#
#        L = a.edge_labels()
#        Lr = ar.edge_labels()
#        d = dict([])
#        for k in L:
#            for kr in Lr:
#                if k == kr and k[0] == 0:
#                    d[(k, kr)] = 0
#                else:
#                    d[(k, kr)] = None
#        a2 = a.product(A=ar, d=d)
#
#        if verb:
#            print("product = %s" % a2)
#        # return a2
#
#        # test if there is a cycle in the graph
#        if a2.is_directed_acyclic():
#            print("0 is not an inner point.")
#        else:
#            ss = self.ss
#            self.ss = None
#            print("Zero is an inner point iff the %s has non-empty interior." % self)
#            self.ss = ss

    # complete the language of a
    def complete(self, list A=None,
                 ext=False, arel=None, simplify=True, verb=False):
        r"""
        Return the language of all words over the alphabet A
        that describe points of the beta-adic set.
        If ''ext'' is True, it includes words that can be
        prolongated to infinite words that fall
        into the limit set.

        INPUT:

        - ``A`` - list -- (default : ``None``) alphabet of the result.

        - ``ext`` - bool -- (default: ``False``)
          If ''ext'' is True, this also include words equal at infinity.

        - ``arel`` - Automaton (default: ``None``)
            Automaton of relations (if already computed, this permits to
            avoid recomputing it).

        - ``simplify`` - bool (default: ``True``)
            Prune and minimize the result if True.

        - ``verb``- bool (default: ``False``)
          If True, print informations for debugging.

        OUTPUT:

        An automaton.

        EXAMPLES::

            sage: m = BetaAdicSet(3, dag.AnyWord([0,1,3]))
            sage: m.complete(dag.AnyWord([0,1,2]))
            DetAutomaton with 1 states and an alphabet of 3 letters
        """
        cdef DetAutomaton a
        if 0 not in self.a.A:
            a = self.a.bigger_alphabet([0]+self.a.A)
        else:
            a = self.a
        if A is None:
            A = self.a.A
        z = A.index(0)
        from sage.combinat.words.cautomata_generators import dag
        ap = a.zero_complete2(z=z).product(dag.AnyWord(A))
        if arel is None:
            arel = self.relations_automaton(couples=True, ext=ext, A=a.A, B=A)
        ai = ap.intersection(arel)
        ai = ai.proji(1)
        if ext:
            ai = ai.prune_inf()
        ai.zero_completeOP()
        if simplify:
            ai = ai.prune().minimize()
        return BetaAdicSet(self.b, ai)

#        ap = DetAutomaton([], A=list(C)).product(a)
#        if ext:
#            ap = ap.prefix_closure()
#        if verb:
#            if ap.n_states < 100:
#                ap.plot()
#            print("ap=%s" % ap)
#        d = dict()
#        Ad = [c - c2 for c in self.a.A for c2 in A]
#        for c in Cd:
#            d[c] = []
#        for c in C:
#            for c2 in a.A:
#                d[c - c2].append((c, c2))
#        if arel is None:
#            arel = self.relations_automaton(Ad=Cd, ext=ext).duplicate(d)
#        else:
#            arel = arel.duplicate(d)
#        if verb:
#            if arel.n_states < 100:
#                arel.plot()
#            print("arel=%s" % arel)
#        ai = ap.intersection(arel)
#        if ext:
#            ai = ai.prune_inf()
#        ai = ai.prune()
#        ai = ai.minimize()
#        if verb:
#            if ai.n_states < 100:
#                ai.plot()
#            print("ai=%s" % ai)
#        d = dict()
#        for c in C:
#            for c2 in a.A:
#                d[(c, c2)] = c
#        ac = ai.determinize_proj(d)
#        if ext:
#            ac = ac.prune_inf()
#        ac = ac.prune()
#        ac = ac.minimize()
#        return ac
#
#    # donne l'automate décrivant l'adhérence de l'ensemble limite avec un nouvel alphabet C
#    def adherence(self, tss=None, C=None, C2=None,
#                  ext=False, verb=False, step=None):
#        """
#        Return an automaton describing the adhesion of the limit set
#        with a new alphabet C
#
#        INPUT:
#
#        - ``tss``
#        - ``C`` list -- (default : ``None``)list of digits .
#        - ``C2`` list -- (default : ``None``)list of digits .
#        - ``ext``  bool -- (default: ``False``)
#          If ''ext'' is True, this also include words equal at infinity.
#        - ``verb``- bool (default: ``False``)
#          If True, print informations for debugging.
#        - ``step`` - int (default: ``None``)
#          Stop to a intermediate state of the computing to make verifications.
#
#        OUTPUT:
#
#        Return an automaton describing the adhesion of the limit set
#        with a new alphabet C
#
#        EXAMPLES::
#            sage: from sage.combinat.words.cautomata_generators import dag
#            sage: m = BetaAdicSet(3, dag.AnyWord([0,1,3]))
#            sage: m.adherence()
#            DetAutomaton with 1 states and an alphabet of 3 letters
#        """
#        if tss is None:
#            if hasattr(self, 'tss'):
#                tss = self.tss
#            else:
#                tss = self.a
#        if C is None:
#            C = list(set(self.a.alphabet))
#        if C2 is None:
#            C2 = list(set(tss.alphabet))
#        if verb:
#            print("Calcul de l'automate des relations...")
#        Cd = list(set([c1 - c2 for c1 in C2 for c2 in C]))
#        if verb:
#            print("Cd=%s" % Cd)
#        a = self.relations_automaton(Ad=Cd, ext=ext)
#        if verb:
#            print(" -> %s" % a)
#        if step == 1:
#            return a
#        if ext:
#            a = a.prune_inf()
#        a = a.prune()
#        if verb:
#            print(" Après émondation : %s" % a)
#        if step == 2:
#            return a
#        d = {}
#        for c1 in C2:
#            for c2 in C:
#                if not d.has_key(c1 - c2):
#                    d[c1-c2] = []
#                d[c1-c2].append((c1, c2))
#        if verb:
#            print(d)
#        a2 = a.duplicate(d, verb=verb)
#        if verb:
#            print(a2.alphabet)
#            print(a2)
#        if step == 3:
#            return a2
#        ap = tss.product(DetAutomaton(self.a), verb=verb)
#        if ext:
#            ap = ap.prefix_closure()
#        if step == 4:
#            return ap
#        a2 = ap.intersection(a2)
#        if step == 5:
#            return a2
#        if ext:
#            a2 = a2.prune_inf()
#        a2 = a2.prune()
#        if step == 6:
#            return a2
#        a2 = a2.minimize()
#        if step == 7:
#            return a2
#        if verb:
#            print("determine...")
#        d = {}
#        for c1, c2 in a2.alphabet:
#            d[(c1, c2)] = c2
#        a2 = a2.determinize_proj(d, verb=verb)
#        if step == 8:
#            return a2
#        if verb:
#            print(" -> %s" % a2)
#        if ext:
#            a2 = a2.prune_inf()
#        a2 = a2.prune()
#        if step == 9:
#            return a2
#        if verb:
#            print("After simplification : %s" % a2)
#        return a2.minimize()

    # project the translation by t of self on the zero completion of a
    def proj(self, a, t=0, arel=None, algo=2, bool aut=False):
        r"""
        project the translation by t of self on the zero completion of a
        aut -  ?

        INPUT:

        - ``a`` automaton
        - ``t`` int (default : ``0``)
        - ``arel`` list -- (default : ``None``) list of digits .
        - ``aut``  bool -- (default: ``False``)

        OUTPUT:

        Return a DetAutomaton or a BetaAdicSet

        EXAMPLES::
            sage: from sage.combinat.words.cautomata_generators import dag
            sage: a = dag.AnyWord([0,1,2])
            sage: m = BetaAdicSet(3, dag.AnyWord([0,1,3]))
            sage: m.proj(a)
            b-adic set with b root of x - 3, and an automaton of 2 states and 3 letters.

        """
        cdef DetAutomaton ai
        cdef DetAutomaton r

        a = getDetAutomaton(self, a)
        if arel is None:
            # compute the relations automaton with translation t
            arel = self.relations_automaton(t=t, couples=True, algo=algo,
                                            A=self.a.alphabet, B=a.alphabet)
        ai = arel.intersection(a.zero_complete2().product(self.a.zero_complete2()))
        r = ai.proji(0)
        r.zero_completeOP()
        if aut:
            return r
        else:
            return BetaAdicSet(self.b, r)

#    # donne l'automate décrivant le translaté de +t de a,
#    # avec les chiffres A au départ et B à l'arrivée, le tout dans l'ensemble décrit par b
#    def move2(self, t, DetAutomaton a=None, DetAutomaton b=None,
#              list A=None, list B=None, ar=None, verb=False):
#        if a is None:
#            if hasattr(self, 'tss'):
#                if isinstance(self.tss, DetAutomaton):
#                    a = self.tss
#                else:
#                    a = DetAutomaton(self.tss)
#            else:
#                a = DetAutomaton(None)
#        if b is None:
#            b = DetAutomaton(None)
#            #            if hasattr(self, 'tss'):
#            #                if isinstance(self.tss, DetAutomaton):
#            #                    b = self.tss
#            #                else:
#            #                    b = DetAutomaton(self.tss)
#            #            else:
#            #                b = DetAutomaton(self.default_ss())
#        if A is None:
#            A = list(set(a.A))
#        if B is None:
#            B = list(set(b.A))
#        if ar is None:
#            # compute the relations automaton with translation t
#            ar = self.relations_automaton(t=t, A=A, B=B,
#                                          couples=True, verb=False)
#        # compute the product of a and b
#        if verb:
#            print("product...")
#        ap = a.zero_complete2().product(b.zero_complete2())
#        if verb:
#            print("ap = %s" % ap)
#        # compute the intersections
#        if verb:
#            print("intersection...")
#        ai = ar.intersection(ap)
#        if verb:
#            print("ai = %s" % ai)
#        if verb:
#            print("min...")
#        ai = ai.minimize()
#        if verb:
#            print("ai = %s" % ai)
#        # project on one side
#        d = {}
#        for c1 in A:
#            for c2 in B:
#                d[(c1, c2)] = c2
#        if verb:
#            print("d=%s" % d)
#        if verb:
#            print("determinize...")
#        ai = ai.determinize_proj(d, verb=verb)
#        if verb:
#            print("ai=%s" % ai)
#        if verb:
#            print("min")
#        ai.zero_completeOP()
#        return ai.prune().minimize()
#

    def shift_op(self, w):
        """
        Shift the automaton of self by w ON PLACE.

        INPUT:

        - ``w`` list  or object converted to list- word to shift

        OUTPUT:

        Return the shifted BetaAdicSet

        EXAMPLES::
            sage: from sage.combinat.words.cautomata_generators import dag
            sage: a = dag.AnyWord([0,1,2])
            sage: m = BetaAdicSet(3, dag.AnyWord([0,1,3]))
            sage: m.shift_op([0,1, 0])
            sage: m
            b-adic set with b root of x^3 - x^2 - x - 1, and an automaton of 1 states and 2 letters.

        """
        try:
            w = list(w)
            self.a.shift_listOP(w)
        except Exception:
            self.a.shift1OP(w)

    def shift(self, w):
        """
        Shift the automaton of self.

        INPUT:

        - ``w`` list - word to shift


        OUTPUT:

        Return the shifted BetaAdicSet

        EXAMPLES::
            sage: from sage.combinat.words.cautomata_generators import dag
            sage: a = dag.AnyWord([0,1,2])
            sage: m = BetaAdicSet(3, dag.AnyWord([0,1,3]))
            sage: m.shift([0,1, 0])
            b-adic set with b root of x^3 - x^2 - x - 1, and an automaton of 1 states and 2 letters.

        """
        m = self.copy()
        m.shift_op(w)
        return m

#    # calcule l'intersection des ensembles limites
#    def intersection3(self, DetAutomaton a, DetAutomaton b, ext=True):
#        a2 = self.complete(a, ext=ext)
#        b2 = self.complete(b, ext=ext)
#        return a2.intersection(b2).prune()
#
#    # determine if the limit sets intersect
#    def intersect(self, DetAutomaton a, DetAutomaton b, ext=True, verb=False):
#        a2 = self.complete(a, ext=ext)
#        if verb:
#            print("a2=%s" % a2)
#        b2 = self.complete(b, ext=ext)
#        if verb:
#            print("b2=%s" % b2)
#        return not a2.intersection(b2).is_empty(ext)
#
#    # Dit si toutes les tuiles du pavages autosimilaire sont connexes ou pas
#    def is_all_connected(self, DetAutomaton a=None, ext=True, verb=False):
#        if a is None:
#            if hasattr(self, 'tss'):
#                if isinstance(self.tss, DetAutomaton):
#                    a = m.tss
#                else:
#                    a = DetAutomaton(self.tss)
#            else:
#                a = DetAutomaton(None).full(list(self.C))
#
#        from sage.graphs.graph import Graph
#        n = a.n_states
#        na = len(a.alphabet)
#        d = dict([])  # dictionnaire des automates complétés
#        if verb:
#            print("Automaton of relations...")
#        arel = self.relations_automaton(ext=ext)
#        for i in range(n):
#            if verb:
#                print("piece %s" % i)
#            g = Graph({j: {} for j in range(na) if a.succ(i, j) != -1})
#            # compute the neighboorhood graph of the piece i
#            for j in g.vertices():
#                for k in g.vertices():
#                    if k >= j:
#                        continue
#                    if verb:
#                        print(" intersection %s et %s..." % (j, k))
#                    la = []
#                    la.append(a.piece(j, e=i).minimize())
#                    la.append(a.piece(k, e=i).minimize())
#                    for l in range(2):
#                        a2 = d.get(la[l])
#                        # récupère le complété dans le dictionnaire s'il y est
#                        if a2 is None:
#                            if verb:
#                                print("  complete %s..." % la[l])
#                            a2 = self.complete(la[l], ext=ext)
#                            d[la[l]] = a2
#                            la[l] = a2
#                        else:
#                            la[l] = a2
#                            if verb:
#                                print("  already calculated !")
#                    if verb:
#                        print("  intersect...")
#                    # if self.intersect(a.piece(j, e=i), a.piece(k, e=i), ext=ext, verb=verb):
#                    if la[0].intersect(la[1], ext=ext):
#                        if verb:
#                            print("  yes !")
#                        g.add_edge(j, k)
#            if not g.is_connected():
#                return False
#        return True
#
#    # Dit si l'ensemble limite est connexe ou pas
#    def is_connected(self, DetAutomaton a=None):
#        if a is None:
#            if hasattr(self, 'tss'):
#                a = DetAutomaton(self.tss)
#            else:
#                a = DetAutomaton(None).full(self.C)
#
#        n = a.n_states
#        na = len(a.alphabet)
#        rules = [[[l] for l in a.alphabet] for i in range(n)]
#        gvois = [Graph(na) for i in range(n)]  # graphe des morceaux voisins
#        gnvois = [Graph(na) for i in range(n)]  # graphe des morceaux non voisins
#
#        # liste des morceaux dont il faut tester
#        # la connexité du graphe de voisinage
#        m = [a.initial_state]
#
#        while len(m) > 0:
#            i = m.pop()
#            gvois[i].connected_component_containing_vertex(i)
#
#        raise ValueError("Not implemented !")
#
#    # Dit si l'ensemble limite est simplement connexe ou pas
#    def is_simply_connected(self, DetAutomaton a=None):
#        if a is None:
#            if hasattr(self, 'tss'):
#                a = DetAutomaton(self.tss)
#            else:
#                a = DetAutomaton(None).full(self.C)
#        # TODO!
#        else:
#            raise ValueError("Not implemented !")

    # used by Approx
    def _approx_rec(self, DetAutomaton a, test, f, x, int n, int n2):
        r"""
        used by approx

        INPUT:

        - ``a``  DetAutomaton
        - ``test``
        - ``f``
        - ``x``
        - ``n``  int
        - ``n2``  int


        OUTPUT:

        number of state or -1

        TESTS::

            sage: from sage.combinat.words.cautomata_generators import dag
            sage: m = BetaAdicSet((x^3-x^2-x-1).roots(ring=QQbar)[1][0], dag.AnyWord([0,1]))
            sage n = 13
            sage: pm = m.b.parent().places()[1]
            sage: test = lambda x: (pm(x).real())^2 + (pm(x).imag())^2 < .4
            sage: a = DetAutomaton(None, A=m.a.alphabet)
            sage: f = a.add_state(1)
            sage: e = m._approx_rec(a, test, f, 0, n, n)
            sage: e
            3537

        """
        if n == 0:
            if test(x):
                return f
            else:
                return -1
        else:
            e = dict()
            add = False
            for t in a.A:
                e[t] = self._approx_rec(a, test, f, x+t*self.b**(n2-n), n-1, n2)
                if e[t] != -1:
                    add = True
            if add:
                e3 = a.add_state(0)
                for t in self.a.A:
                    if e[t] != -1:
                        a.add_edge(e3, t, e[t])
                return e3
            return -1

    # TO BE PUT IN GENERATORS
    # gives a automaton describing a approximation of a set defined by
    # the characteritic function test
    # rk : can be improve using a reduced words automaton
    def approx(self, n, test, get_aut=False, bool simplify=True):
        """
        gives a automaton describing a approximation of a set defined by the
        characteritic function test
        rk : can be improve using a reduced words automaton

        INPUT:

        - ``n``  int
        - ``test`` function
        - ``get_aut``  bool -- (default ``False``)
          if ``False`` return  DetAutomaton
        - ``simplify``  bool -- (default ``True``) set
          to ``True`` to minimize the automaton

        OUTPUT:

        Return a DetAutomaton or a BetaAdicSet

        EXAMPLES::

            sage: m = BetaAdicSet((x^3-x^2-x-1).roots(ring=QQbar)[1][0], dag.AnyWord([0,1]))
            sage: pm = m.b.parent().places()[1]
            sage: a = m.approx(13, lambda x: (pm(x).real())^2 + (pm(x).imag())^2 < .4 )
            sage: print(a)
            DetAutomaton with 3538 states and an alphabet of 2 letters
        """
        cdef DetAutomaton a
        a = DetAutomaton(None, A=self.a.A)
        f = a.add_state(1)
        e = self._approx_rec(a, test, f, 0, n, n)
        for t in self.a.A:
            a.add_edge(f, t, f)
        a.a.i = e
        if simplify:
            a = a.minimize()
        if get_aut:
            return a
        else:
            return BetaAdicSet(self.b, a)

    def full(self, list A=None, bool verb=False):
        """
        Return the BetaAdicSet describing the same set of points,
        but with the maximal language over the alphabet A

        INPUT:

        - ``A``  list -- (default : ``None``)  alphabet list
        - ``verb`` bool -- (default : ``False``) set to ``True`` for verbose mode

        OUTPUT:

        Return the BetaAdicSet describing the same set of points,
        but with the maximal language over the alphabet A

        EXAMPLE::

            sage: m = BetaAdicSet((x^3-x^2-x-1).roots(ring=QQbar)[1][0], dag.AnyWord([0,1]))
            sage: m.full()
            b-adic set with b root of x^3 - x^2 - x - 1, and an automaton of 1 states and 2 letters.

        """
        from sage.combinat.words.cautomata_generators import dag
        if verb:
            print("a = %s" % A)
        if A is None:
            A = self.a.A
        aoc = self.proj(dag.AnyWord(A))
        return aoc

    def union(self, a):
        """
        Return the union of BetaAdicSet and automaton a

        INPUT:

        - ``a``  automaton

        OUTPUT:

        Return the BetaAdicSet union of ``a`` and ``self.a``

        EXAMPLE::

            sage: m = BetaAdicSet((x^3-x^2-x-1).roots(ring=QQbar)[1][0], dag.AnyWord([0,1]))
            sage: a = dag.AnyWord([0, 1, 2, 4])
            sage: m.union(a)
            b-adic set with b root of x^3 - x^2 - x - 1, and an automaton of 1 states and 2 letters
        """
        a = getDetAutomaton(self, a)
        return BetaAdicSet(self.b, self.a.union(a))

    def unshift(self, l):
        """
        Return a BetaAdicSet with a unshiftted ``self.a`` of ``l``

        INPUT:

        - ``l``  list of indices of letters or the index of a letter

        OUTPUT:

        Return a BetaAdicSet with a unshiftted ``self.a`` of ``l``

        EXAMPLE::

            sage: m = BetaAdicSet((x^3-x^2-x-1).roots(ring=QQbar)[1][0], dag.AnyWord([0,1]))
            sage: m.unshift(1)
            b-adic set with b root of x^3 - x^2 - x - 1, and an automaton of 2 states and 2 letters.
            sage: m = BetaAdicSet((x^3-x^2-x-1).roots(ring=QQbar)[1][0], dag.AnyWord([0,1]))
            sage: m.unshift([0,1])
            b-adic set with b root of x^3 - x^2 - x - 1, and an automaton of 3 states and 2 letters.
        """
        try:
            l = list(l)
            return BetaAdicSet(self.b, self.a.unshiftl(l))
        except:
            return BetaAdicSet(self.b, self.a.unshift1(l))

    # compute the difference of two beta-adic sets.
    # it is a beta-adic set which is the set of differences of the two beta-adic sets
    def diff(self, a):
        """
        compute the difference of two beta-adic sets.
        it is a beta-adic set which is the set of differences of the two beta-adic sets

        INPUT:

        - ``a``  an automaton

        OUTPUT:

        Return the difference of two beta-adic sets.


        EXAMPLES::

            sage: m = BetaAdicSet((x^3-x^2-x-1).roots(ring=QQbar)[1][0], dag.AnyWord([0,1]))
            sage: a = dag.AnyWord([0, 1, 2, 4])
            sage: m.diff(a)
            b-adic set with b root of x^3 - x^2 - x - 1, and an automaton of 1 states and 6 letters.

        """
        a = getDetAutomaton(self, a)
        return BetaAdicSet(self.b, self.a.diff(a))

    def is_Pisot(self, bool verb=False):
        """
        Test if the number b is the conjugate of a Pisot number or not.


        INPUT:

        - ``verb`` bool -- (default : ``False``) set to ``True`` for verbose mode
          If true, explains why we return False when it happens.

        OUTPUT:
        Return ``True`` or ``False``

        EXAMPLES::

            sage: m = BetaAdicSet(x^2-x-1, [0,1])
            sage: m.is_Pisot()
            True

            sage: m = BetaAdicSet(x^4-2*x^3+x^2-2*x+1, [0,1])
            sage: m.is_Pisot()
            False

            sage: m = BetaAdicSet(1+I, [0,1])
            sage: m.is_Pisot(verb=True)
            There are more than one conjugate of modulus > 1.
            False

        """
        try:
            if not self.b.is_integral():
                if verb:
                    print("b is not an algebraic integer.")
                return False
            pi = self.b.minpoly()
            rr = [r[0] for r in pi.roots(ring=QQbar)]
            np = 0
            for r in rr:
                if abs(r) > 1:
                    if np != 0:
                        if verb:
                            print("There are more than one conjugate of modulus > 1.")
                        return False
                    np = 1
                elif abs(r) == 1:
                    if verb:
                        print("There is a conjugate of modulus one.")
                    return False
            if np == 0:
                if verb:
                    print("There is no conjugate of modulus > 1.")
                return False
            return True
        except Exception:
            if verb:
                print("b is not an algebraic number.")
            return False

    def points(self, int n=1000, int npts=10000):
        """
        Compute points (in the number field of b) corresponding to words of length k recognized by the automaton,
        where k is at most n, and the total number of points is approximatively npts.
        Return (k, list of couples (state, point))

        INPUT:

        - ``n`` - integer (default: 1000)
          The maximum number of iterations used to plot the fractal.
          Default values: between ``5`` and ``16`` depending on the number
          of generators.

        - ``npts`` - integer (default: 10000 )
          Approximation of the number of points computed.

        OUTPUT:

        Return (k, list of couples (state, point)), where k is the number of iterations computed.

        EXAMPLES::

            #. The dragon fractal::
            sage: m = BetaAdicSet(1/(1+I), [0, 1])
            sage: print(m)
            b-adic set with b root of x^2 - x + 1/2, and an automaton of 1 states and 2 letters.
            sage: P = m.points()
            sage: P[0]
            13
            sage: len(P[1])
            8192
            sage: points([x for i,x in P[1]], aspect_ratio=1) # long time
        """
        cdef int i, j, k, f, nA
        nA = self.a.a.na
        l = self.a.spectral_radius()
        n = min(n, <int>(log(<double>npts)/log(<double>l)))
        r = [(self.a.a.i, 0)]
        bn = 1
        for i in range(n):
            rr = []
            for j, t in r:
                for k in range(nA):
                    f = self.a.a.e[j].f[k]
                    if f != -1:
                        rr.append((f, t + bn*self.a.A[k]))
            bn = bn*self.b
            r = rr
        return (n, r)

    def zero_ball(self, p, int npts=1000):
        """
        Compute the radius of a ball centered at 0 and that covers the BetaAdicSet for the place p.
        We assume that abs(p(self.b)) < 1.

        INPUT:

        - ``p`` - integer

        - ``npts`` - integer (default: 10000 )
          State of the automaton of self taken as the initial state .

        """
        pts = self.points(npts=npts)
        M = abs(p(self.b**pts[0]))*max([abs(p(c))
                                        for c in self.a.A])/abs(1-abs(self.b))
        return max([abs(p(c[1]))+M for c in pts[1]])

    def diameter(self, p, int n=10, bool verb=False):
        """
        Compute an upper bound of the diameter of the BetaAdicSet for the place p.
        The error has order p(self.b)^n.
        (The algorithm used here is not optimal.)

        INPUT:

        - ``p`` - integer

        - ``n`` - integer (default: 10 )

        - ``verb`` bool -- (default : ``False``) set to ``True`` for verbose mode

        OUTPUT:

        Return the diameter  beta-adic sets.


        EXAMPLES::

            sage: m = BetaAdicSet((x^3-x^2-x-1).roots(ring=QQbar)[1][0], dag.AnyWord([0,1]))
            sage: p =
            sage: m.diameter()
        """
        cdef int i, j, k, f, f2, nrr, nA
        cdef double d, dmm, dm2
        nA = self.a.a.na
        r = [(self.a.a.i, 0)]
        bn = 1
        M = max([abs(p(c)) for c in self.a.A])/abs(1-abs(self.b))
        import numpy as np
        for i in range(n):
            rr = []
            for j, t in r:
                for k in range(nA):
                    f = self.a.a.e[j].f[k]
                    if f != -1:
                        rr.append((f, t + bn*self.a.A[k]))
            bn = bn*self.b
            if verb:
                print("rr : %s elements" % len(rr))
            r = []
            # compute the diameter of the set rr (this could be improved)
            dmm = 0
            dm = np.zeros(len(rr), dtype=np.float)
            v = np.empty(len(rr), dtype=np.complex)
            for f, (j, t) in enumerate(rr):
                v[f] = p(t)
            nrr = len(rr)
            for f in range(nrr):
                dm2 = 0
                for f2 in range(nrr):
                    d = abs(v[f] - v[f2])
                    if d > dm2:
                        dm2 = d
                dmm = fmax(dmm, dm2)
                dm[f] = dm2
            if verb:
                print("dmm = %s" % dmm)
            M2 = 2*abs(p(bn))*M
            if i == n-1:
                return dmm+M2
            for f, (j, t) in enumerate(rr):
                if dm[f]+M2 >= dmm:
                    r.append((j, t))
            if verb:
                print("r : %s elements" % len(r))

    def translations_iterator(self, bool test_Pisot=True, int ndiam=20, bool verb=False):
        """
        Assume that self.b is a Pisot number.
        Compute a list of numbers containing the positive
        part of the BetaAdicSet, ordered in the expanding direction.

        INPUT:

        - ``test_Pisot``  bool -- (default : ``True``) : test if b is the conjugate of a Pisot number as needed
          B : basis of a lattice containing the BetaAdicSet

        - ``verb`` bool -- (default : ``False``) set to ``True`` for verbose mode

        - ``ndiam`` int  -- (default : 20): number of iterations
          used for the estimation of the diameter

        OUTPUT:
        Return an iterator.


        EXAMPLES::

            sage: m = BetaAdicSet((x^3-x^2-x-1).roots(ring=QQbar)[1][0], dag.AnyWord([0,1]))
            sage: m.translations_iterator().next()

        """
        cdef int n, i, j
        if test_Pisot:
            if not self.is_Pisot():
                raise ValueError("b must be the conjugate of a Pisot number")
        # take a basis of the lattice
        d = self.b.minpoly().degree()
        B = [self.b**i for i in range(d)]
        # compute the min of the differences for every place
        Bd = set([a-b for a in B for b in B if a != b])
        K = self.b.parent()
        n = -2147483648
        # from sage.functions.other import ceil
        # from sage.functions.log import log
        P = [p for p in K.places() if abs(p(self.b)) < 1]
        M = [self.diameter(p, n=ndiam) for p in P]
        for i, p in enumerate(P):
            m = min([abs(p(b)) for b in Bd])
            if verb:
                print("p=%s, m=%s, M=%s" % (p,m,M))
                print("%s" % (log(m/(2*M[i]))/log(abs(p(self.b)))))
            n = max(n, <int>floor(log(m/(2*M[i]))/log(abs(p(self.b)))))
        if verb:
            print("n=%s" % n)
        # multiply the bound by this power of b
        bn = self.b**n
        M = [M[i]*abs(p(bn)) for i, p in enumerate(P)]
        # compute the matrix corresponding to the multiplication by M to the left
        from sage.matrix.constructor import identity_matrix
        I = identity_matrix(d)
        pi = self.b.minpoly()
        pi /= pi.leading_coefficient()
        from sage.matrix.constructor import matrix

        m = matrix(
            [I[i] for i in range(1, d)] +
            [[-c for c in pi.list()[:d]]]).transpose()

        if verb:
            print("m=%s" % m)
        # compute the Perron-Frobenius eigenvector
        from sage.modules.free_module_element import vector
        v = vector(max(
            [r[1][0] for r in m.right_eigenvectors()], key=lambda x: x[0]))
        v /= sum(v)
        vB = vector(B)
        if verb:
            print("v=%s" % v)
        r = []
        from itertools import count
        for j in count(start=1):
            vi = vector([<int> round(j * x) for x in v])
            t = vi * vB
            if t == 0:
                continue
            if verb:
                print("j=%s, t=%s" % (j, t))
            # test if t is in the domain
            keep = True
            for i, p in enumerate(P):
                if abs(p(t)) > M[i]:
                    keep = False
                    break
            if keep:
                yield t/bn

    def translations_diff_iterator(self, bool test_Pisot=True, 
                                   int ndiam=20, bool verb=False):
        """
        Assume that self.b is a Pisot number.
        Compute a list that contains the set of differences of points of the BetaAdicSet.
        The list is increasing for the expanding place.

        INPUT:

        - ``test_Pisot``  bool -- (default : ``True``) : test if b is 
          the conjugate of a Pisot number as needed
          B : basis of a lattice containing the BetaAdicSet

        - ``ndiam`` int -- (default : 20): number of iterations used
          for the estimation of the diameter

        - ``verb`` bool -- (default : ``False``) set to ``True`` for verbose mode

        OUTPUT:
        Return an iterator.

        EXAMPLES::

            sage: m = BetaAdicSet((x^3-x^2-x-1).roots(ring=QQbar)[1][0], dag.AnyWord([0,1]))
            sage: m.translations_diff_iterator().next()
            2*b^2 - 3*b - 1

        """
        cdef int n, i, j
        if test_Pisot:
            if not self.is_Pisot():
                raise ValueError("b must be the conjugate of a Pisot number")
        # take a basis of the lattice
        d = self.b.minpoly().degree()
        B = [self.b**i for i in range(d)]
        # compute the min of the differences for every place
        Bd = set([a-b for a in B for b in B if a != b])
        K = self.b.parent()
        n = -2147483648
        # from sage.functions.other import ceil
        # from sage.functions.log import log
        P = [p for p in K.places() if abs(p(self.b)) < 1]
        M = [self.diameter(p) for p in P]
        for i, p in enumerate(P):
            m = min([abs(p(b)) for b in Bd])
            if verb:
                print("p=%s, m=%s, M=%s" % (p, m,M))
                print("%s" % (log(m/(2*M[i]))/log(abs(p(self.b)))))
            n = max(n, <int> floor(log(m/(2*M[i])) / log(abs(p(self.b)))))
        if verb:
            print("n=%s" % n)
        # multiply the bound by this power of b
        bn = self.b**n
        M = [M[i]*abs(p(bn)) for i, p in enumerate(P)]
        # compute the matrix corresponding to the multiplication by M to the left
        from sage.matrix.constructor import identity_matrix
        I = identity_matrix(d)
        pi = self.b.minpoly()
        pi /= pi.leading_coefficient()
        if verb:
            print("pi=%s" % pi)
        from sage.matrix.constructor import matrix

        m = matrix(
            [I[i] for i in range(1,d)] +
            [[-c for c in pi.list()[:d]]]).transpose()

        if verb:
            print("m=%s" % m)
        # compute the Perron-Frobenius eigenvector
        from sage.modules.free_module_element import vector
        v = vector(
            max([r[1][0] for r in m.right_eigenvectors()], key=lambda x: x[0]))
        v /= sum(v)
        vB = vector(B)
        if verb:
            print("v=%s" % v)
        r = []
        from itertools import count
        for j in count(start=1):
            vi = vector([<int>round(j * x) for x in v])
            t = vi*vB
            if t == 0:
                continue
            if verb:
                print("j=%s, t=%s"%(j,t))
            # test if t is in the domain
            keep = True
            for i, p in enumerate(P):
                if abs(p(t)) > M[i]:
                    keep = False
                    break
            if keep:
                yield t/bn

        
    def domain_exchange(self, n=None, int algo=1, bool test_Pisot=True,
                        int ndiam=30, bool verb=False):

        """
        Assume that self.b is a Pisot number.
        Compute the domain exchange describing the BetaAdicSet.
        Return a list of (translation, BetaAdicSet).

        INPUT:

        - ``n``  int -- (default : ``None``)

        - ``algo``  int -- (default : 1) nomro of algorithm

        - ``test_Pisot``  bool -- (default : ``True``) : test if b is 
          the conjugate of a Pisot number as needed
          B : basis of a lattice containing the BetaAdicSet

        - ``ndiam`` int -- (default : 30) : number of iterations used for
           the estimation of the diameter

        - ``verb`` bool -- (default : ``False``) set to ``True`` 
          for verbose mode


        OUTPUT:
        List of tuple ``BetaAdicSet``

        EXAMPLES::

            #Domain exchange of the Tribonnacci substitution
            sage: m = BetaAdicSet(x^3-x^2-x-1, [0,1])
            sage: l = m.domain_exchange(); l
            [(b^2 - b - 1,
              b-adic set with b root of x^3 - x^2 - x - 1, and an automaton of 4 states and 2 letters.),
             (b - 1,
              b-adic set with b root of x^3 - x^2 - x - 1, and an automaton of 4 states and 2 letters.),
             (1,
              b-adic set with b root of x^3 - x^2 - x - 1, and an automaton of 4 states and 2 letters.)]
            sage: m.plot_list([a for t,a in l])             # not tested
            sage: m.plot_list([a.proj(m, t) for t,a in l])  # random
            <PIL.Image.Image image mode=RGBA size=800x600 at 0x7F57DFF3BC10>

            # A more complicated domain exchange
            sage: m = BetaAdicSet((x^3 - x^2 - x - 1).roots(ring=QQbar)[1][0], DetAutomaton([[0, 1], [(0, 17, 0), (0, 4, 1), (1, 16, 0), (2, 17, 0), (2, 4, 1), (3, 17, 0), (4, 17, 0), (5, 7, 0), (5, 0, 1), (6, 5, 0), (6, 0, 1), (7, 6, 0), (8, 10, 0), (9, 8, 0), (9, 0, 1), (10, 9, 0), (11, 15, 0), (11, 1, 1), (12, 14, 0), (12, 11, 1), (13, 8, 0), (13, 2, 1), (14, 13, 0), (14, 18, 1), (15, 5, 0), (15, 2, 1), (16, 17, 0), (16, 0, 1), (17, 17, 0), (17, 0, 1), (18, 16, 0), (18, 3, 1)]], i=12, final_states=[0, 1, 2, 3, 4, 16, 17, 18]))
            sage: l = m.domain_exchange(); l
            [(b^2 - b - 1,
              b-adic set with b root of x^3 - x^2 - x - 1, and an automaton of 5 states and 2 letters.),
             (b - 1,
              b-adic set with b root of x^3 - x^2 - x - 1, and an automaton of 9 states and 2 letters.),
             (1,
              b-adic set with b root of x^3 - x^2 - x - 1, and an automaton of 8 states and 2 letters.),
             (2,
              b-adic set with b root of x^3 - x^2 - x - 1, and an automaton of 6 states and 2 letters.),
             (2*b - 1,
              b-adic set with b root of x^3 - x^2 - x - 1, and an automaton of 7 states and 2 letters.)]
            sage: m.plot_list([a for t,a in l])             # random
            <PIL.Image.Image image mode=RGBA size=800x600 at 0x7F57DFE50450>
            sage: m.plot_list([a.proj(m, t) for t,a in l])  # random
            <PIL.Image.Image image mode=RGBA size=800x600 at 0x7F57DFE50BD0>

        """
        if algo == 1:
            if verb:
                print("compute translations...")
            it = self.translations_diff_iterator(test_Pisot=test_Pisot,
                                                 ndiam=ndiam, verb=verb)
        else:
            if verb:
                print("diff...")
            md = self.diff(test_Pisot=test_Pisot)
            if verb:
                print("compute translations...")
            it = md.translations_iterator(verb=verb, ndiam=ndiam)
        m = self.copy()
        # from sage.combinat.words.cautomata_generators import dag
        # a = self.a.intersection(dag.AnyWord([0], A2=self.a.A).complementary())
        a = self.a.copy()
        r = []
        if n is None:
            n = -1
        for t in it:
            if verb:
                print("t=%s" % t)
            mi = m.intersection(m, -t)
            mia = mi.a.intersection(a)
            if not mia.is_empty():
                if verb:
                    print("not empty ! mia=%s" % mia)
                mi = BetaAdicSet(m.b, mia)
                r.append((t, mi))
                a = a.intersection(mi.a.complementary())
                if a.is_empty():
                    return r
            n -= 1
            if n == 0:
                return r

    def way(self, A, a, e, t, n, bn):
        """
        Describes the words of ``a``  of length ``n`` starting from ``e``

        INPUT:

        - ``A`` alphabet
        - ``a``  DetAutomaton an automaton
        - ``e``  begin states
        - ``t``  transition
        - ``n``  int length
        - ``verb`` bool -- (default : ``False``) set to ``True

        OUTPUT:
        Return computed sorted list

        EXAMPLES::

            sage: m = BetaAdicSet((x^3-x^2-x-1).roots(ring=QQbar)[1][0], dag.AnyWord([0,1]))
            sage: aoc = dag.AnyWord([0, 1, 2, 4])
            sage: m.compute_translations(aoc=aoc)

        """
        # print "Parcours e=%s t=%s n=%s bn=%s"%(e,t,n,bn)

        if n == 0:
            if a.is_final(e):
                return [t]
            else:
                return []
        else:
            l = []
            for i in range(len(A)):
                f = a.succ(e, i)
                if f != -1:
                    l += self.way(A, a, f, t + bn * A[i], n - 1, bn*self.b)
            if a.is_final(e):
                l.append(t)
            return l

    def substitution(self, lt=None, get_aut=False, np=None, verb=False):
        r"""
        Assume that b is a conjugate of a Pisot number.
        Compute a substitution whose discrete line is this BetaAdicSet.

        Return a WordMorphism. If get_aut is True, return also a list of (translation, automaton) describing each piece of the Rauzy fractal.
        np -- int (default: None) - power of b used to compute the substitution. If np is None, take the smallest one possible.
        """
        #test is b is a Pisot number
        if not self.is_Pisot():
            raise ValueError("The number b of the BetaAdicSet must be for the conjugate of a Pisot number.")
        #ensure that the alphabet of a contains 0
        a = self.a.copy()
        A = a.A
        try:
            l0 = A.index(0)
        except:
            A = [0]+A
            a = a.bigger_alphabet([0]+A)
            l0 = 0
        #find np such that b^np*self is included in self
        if np is None:
            an = a.copy()
            for i in range(1, 100):
                an = an.unshift(l0)
                if BetaAdicSet(self.b, an).is_included(a):
                    break
            np = i
        zn = [l0 for i in range(np)]
        ba = a.unshift(zn)
        if not BetaAdicSet(self.b, ba).is_included(a):
            raise ValueError("The BetaAdicSet is not invariant by multiplication by b^np with np=%s !"%np)
        #compute the domain exchange
        if lt is None:
            lt = self.domain_exchange(test_Pisot=False)
        #for each piece P, compute b^(-np)P projected on a
        #lm = []
        #for t,m in l:
        #    m2 = m.proj(an).shift(zn)
        #    if not m2.is_empty():
        #        lm.append((t,m2))
        
        if verb:
            print("Exchange of %s pieces" % len(lt))
        # computation of the induction, starting from the list (translation, domain)
        # precomputing
        if verb:
            print("Pre-computation...")
        #arel = dict()
        #for t,a in lt:
        #    arel[t] = m.relations_automaton(t=-t, A=aa.A,
        #                                     B=ap.A, couples=True)
        #    if verb:
        #        print("arel[%s]=%s" % (t, arel[t]))
        if verb:
            print("ba : %s" % ba)
        # tree of subdivision of the pieces
        tree = [range(1, len(lt) + 1)] + [[] for i in range(len(lt))] 
        if verb:
            print("initial tree: %s" % tree)
        #lm = [(0, a)] + lt  # list of the translations, pieces
        lm = lt        
        if verb:
            print("lm = %s" % lm)
        # browse the pieces
        d = [[] for i in range(len(lm))]
        if verb:
            print("d = %s" % d)
        lf = range(1, len(lm))  # list of sleeves
        if verb:
            print("lf = %s" % lf)

        from copy import copy

        if verb:
            print("\n**********************\n   Step 1   \n**********************")

        # étape 1 : completion of the words of the substitution
        for i, (a1, t1) in enumerate(lm):
            if tree[i] != []:
                continue  # this piece is not a sleeve
            if verb:
                print("\nCompute the piece %s/%s (%s, %s)..." % (i, len(lm), a1, t1))
                # print "lf = %s"%lf
                # print "d = %s"%d
                # print "tree = %s"%tree
            tr = 0  # total translation
            if d[i] != []:
                if d[i][-1] == -1:
                    continue  # the computation of this piece was already finished
                # va à la fin du mot
                for j in d[i]:
                    if j < 0:
                        break
                    tr += lm[j][1]
#            # calcule b^np*a + tr
#            a = a1.unshift(0, np).prune().minimize()
#            if tr != 0:
#                if verb:
#                    print("Translation de %s..." % tr)
#            # m.move2(t=-tr, a=a)
#            # TODO : ne pas recalculer cet automate déjà calculé
#            a = m.Proj(a, ap, t=-tr)
#            while True:
#                # split selon les autres morceaux
#                j = included(a, lf, lm)
#                if j is None:
#                    # détermine les morceaux qui intersectent a
#                    l = []
#                    for j in lf:
#                        if lm[j][0].intersect(a):
#                            l.append(j)
#                    if len(l) < 2:
#                        print("Error : intersection with %s piece but not included !!!"%len(l))
#                    if verb:
#                        print("Subdivision on %s pieces..." % len(l))
#                    # calcule les intersections (découpe en morceaux a1)
#                    for j in l:
#                        a2 = lm[j][0]
#                        # découpe a selon a2
#                        # m.move2(t=tr, a=a2) #translate a2 de -tr
#                        a = m.Proj(a2, ap.unshift(0, np), t=tr)
#                        a.shiftOP(0, np)  # multiplie par b^(-np)
#                        a = a.prune().minimize()
#                        k = len(lm)  # indice du nouveau morceau
#                        lf.append(k)  # nouvelle feuille
#                        tree[i].append(k)
#                        tree.append([])
#                        from copy import copy
#                        # print copy
#                        d.append(copy(d[i]))
#                        d[k].append(j)  # ajoute la translation suivante
#                        # ajoute le nouveau morceau à la liste
#                        lm.append((a.intersection(a1), t1))
#                        # split selon ba
#                        (ab, abc) = split_ba(k, tr+lm[j][1], np,
#                                             lm, m, aa, ap, verb)
#                        if ab is None:
#                            if verb:
#                                print("k=%s, tr=%s+%s : calcul à continuer" % (k, tr, lm[j][1]))
#                        else:
#                            if abc is None:
#                                if verb:
#                                    print("tr=%s : calcul terminé" % tr)
#                                d[k].append(-1)  # indique que le calcul de ce morceau est terminé
#                            else:
#                                if verb:
#                                    print("tr=%s : subdivision of %s by ba (new %s)..." % (tr, i, len(lm)))
#                                lf.append(len(lm))  # nouvelle feuille
#                                tree[k].append(len(lm))
#                                tree.append([])
#                                d.append(copy(d[k]))
#                                # indique que le calcul est terminé pour ce morceau (pour l'étape 1)
#                                d[len(lm)].append(-1)
#                                lm.append((ab, t1))
#                                lf.append(len(lm))  # nouvelle feuille
#                                tree[k].append(len(lm))
#                                tree.append([])
#                                d.append(copy(d[k]))
#                                lm.append((abc, t1))
#                                lf.remove(k)  # le morceau k n'est plus une feuille
#                    lf.remove(i)  # le morceau i n'est plus une feuille
#                    # calcul fini pour ce morceau puisque ce n'est plus une feuille
#                    break
#                else:
#                    # ajoute le morceau à la liste et translate
#                    d[i].append(j)
#                    # if verb: print "Translation de %s..."%lm[j][1]
#                    # m.move2(t=-lm[j][1], a=a, ar=arel[lm[j][1]])
#                    a = m.Proj(a, ap, t=-lm[j][1], arel=arel[lm[j][1]])  
#                    tr += lm[j][1]
#                # split selon ba
#                (ab, abc) = split_ba(i, tr, np, lm, m, aa, ap, verb)
#                if ab is None:
#                    pass
#                    # if verb: print "tr=%s : calcul à continuer"%tr
#                else:
#                    if abc is None:
#                        if verb:
#                            print("tr=%s : end of computation" % tr)
#                    else:
#                        if verb:
#                            print("tr=%s : subdivision of %s by ba (new %s)..." % (tr, i, len(lm)))
#                        lf.append(len(lm))  # nouvelle feuille
#                        tree[i].append(len(lm))
#                        tree.append([])
#                        d.append(copy(d[i]))
#                        # indique que le calcul est terminé pour ce morceau (pour l'étape 1)
#                        d[len(lm)].append(-1)
#                        lm.append((ab, t1))
#                        lf.append(len(lm))  # nouvelle feuille
#                        tree[i].append(len(lm))
#                        tree.append([])
#                        d.append(copy(d[i]))
#                        lm.append((abc, t1))
#                        lf.remove(i)  # le morceau i n'est plus une feuille
#                    break  # calcul fini pour ce morceau (pour cette étape)
#
#        if verb:
#            print("\n*************\n   Step 2   \n*************")
#
#        # étape 2 : remplacement des lettres qui ne sont pas des feuilles
#        while True:
#            end = True
#            for i in lf:
#                a1, t1 = lm[i]
#                if verb:
#                    print("\nPiece %s/%s..." % (i, len(lm)))
#                tr = 0  # translation totale
#                if d[i] == []:
#                    print("Error : empty sheet !!!!")
#                # va à la fin du mot
#                for ij, j in enumerate(d[i]):
#                    if j < 0:
#                        break
#                    if tree[j] != []:  # il faut recalculer cette lettre
#                        # calcule b^np*a + tr
#                        a = a1.unshift(0, np).prune().minimize()
#                        if tr != 0:
#                            if verb:
#                                print("Translation of %s..." % tr)
#                        # m.move2(t=-tr, a=a)
#                        # TODO : ne pas recalculer cet automate déjà calculé
#                        a = m.Proj(a, ap, t=-tr)
#                        # split selon les autres morceaux
#                        f = fils(tree, j)
#                        if verb:
#                            print("Split by %s pieces" % len(f))
#                        k = included(a, f, lm)
#                        if k is None:
#                            end = False
#                            # détermine les morceaux qui intersectent a
#                            l = []
#                            for k in lf:
#                                if lm[k][0].intersect(a):
#                                    l.append(k)
#                            if len(l) < 2:
#                                print("Error : intersection with %s pieces but not included !!!" % len(l))
#                            if verb:
#                                print("Subdivision of %s pieces..." % len(l))
#                            # calcule les intersections (découpe en morceaux a1)
#                            for j2 in l:
#                                a2 = lm[j2][0]
#                                # découpe selon a2
#                                # a = m.move2(t=tr, a=a2) #translate a2 de -tr
#                                # a.zero_completeOP()
#                                a = m.Proj(a2, ap.unshift(0, np), t=tr)
#                                a.shiftOP(0, np)  # multiplie par b^(-np)
#                                a = a.prune().minimize()
#                                k = len(lm)  # indice du nouveau morceau
#                                lf.append(k)  # nouvelle feuille
#                                tree[i].append(k)
#                                tree.append([])
#                                d.append(copy(d[i]))
#                                d[k][ij] = j2  # remplace la lettre
#                                # ajoute le nouveau morceau à la liste
#                                lm.append((a.intersection(a1), t1))
#                            lf.remove(i)  # i n'est plus une feuille
#                            if verb:
#                                print("break...")
#                            break  # le morceau n'est plus une feuille
#                        else:
#                            # remplace la lettre
#                            d[i][ij] = k
#                    tr += lm[j][1]
#            if end:
#                break
#        # compute the substitution
#        s = dict()
#        for i in lf:
#            if d[i][-1] < 0:
#                d[i].pop()
#            s[i] = d[i]
#        # recode the substitution
#        l = s.keys()
#        dl = dict()  # inverse of l
#        for i, k in enumerate(l):
#            dl[k] = i+1
#        d = dict()
#        for i in s:
#            d[dl[i]] = [dl[j] for j in s[i]]
#        if get_aut:
#            return d, [(a, t) for i, (a, t) in enumerate(lm) if tree[i] == []]
#        else:
#            return d
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        

    # to be rewritten
    def compute_substitution(self, DetAutomaton a=None,
                             np=None, lt=None, method=2,
                             method_tr=1, iplus=2, imax=None,
                             get_aut=False, verb=True):
        r"""Compute a substitution whose fixed point is the g-beta-expansion given
        by the beta-adic monoid with automaton a.

        INPUT:

        - ``a``- DetAutomaton (default: ``None``)
            Automaton of the g-beta-expansion.

        - ``np``- int (default: ``None``)
            Power of beta for the computing. The g-beta-expansion must be b^np invariant.

        - ``lt``- list of elements of the integer rings
            List of translations to compute the pieces exchange.

        - ``get_aut``- Bool (default: ``False``)
            If True, gives also the list of automata.

        - ``verb``- bool (default: ``True``)
          If True, print informations about the computing.

        OUTPUT:

        A word morphism given by a dictionnary.

        EXAMPLES::

            #. Full Tribonnacci::

                sage: from sage.combinat.words.cautomata_generators import dag
                sage: m = BetaAdicSet((x^3-x^2-x-1).roots(ring=QQbar)[1][0], dag.AnyWord([0,1]))
                sage: m.compute_substitution(verb=False)      # long time
                {1: [1, 3], 2: [1], 3: [1, 2]}

        """
        m = self
        if a is None:
            if hasattr(self, 'tss'):
                a = DetAutomaton(self.tss)
            else:
                a = DetAutomaton(a=None, A=list(self.a.alphabet))
        a.zero_completeOP()
        A = a.A
        # complete a
        aoc = m.move2(t=0, a=a)
        aoc.zero_completeOP()
        aoc = aoc.prune().minimize()
        if verb:
            print("aoc = %s" % aoc)
        # test if np is big enough
        if np is None:
            for i in range(1, 300):
                baoc = aoc.unshift(0, i)
                if baoc.included(aoc):
                    np = i
                    break
            if np is None:
                raise ValueError('The g-beta-expansion must be b^np invariant for some natural integer np.')
        else:
            baoc = aoc.unshift(0, np)
            if not baoc.included(aoc):
                raise ValueError('The g-beta-expansion must be b^np invariant (here np=%s).' % np)
        if verb:
            print("np = %s" % np)
        # compute the pieces exchange
        if lt is None:
            if verb:
                print("compute the pieces exchange...")
            if method == 1:
                lt = self.compute_morceaux(aoc, method=method_tr,
                                           imax=imax, verb=verb)
            else:
                lt = self.compute_morceaux2(aoc, iplus, verb=verb)
        if verb:
            print("Exchange of %s pieces" % len(lt))
        # calcule l'induction à partir de la liste de (morceau, translation)
        # précalculs
        if verb:
            print("Pre- computation...")
        arel = dict()
        for a, t in lt:
            arel[t] = m.relations_automaton(t=-t, A=a.A, B=m.C, couples=True)
            if verb:
                print("arel[%s]=%s" % (t, arel[t]))
        baoc = aoc.unshift(0, np)  # multiplie par b
        baoc = m.move2(t=0, a=baoc, b=aoc)  # complete
        baoc.zero_completeOP()
        if verb:
            print("baoc : %s" % baoc)
        # tree de subdivision des morceaux
        tree = [range(1, len(lt) + 1)] + [[] for i in range(len(lt))]
        if verb:
            print("initial tree: %s" % tree)
        lm = [(aoc, 0)] + lt  # liste des morceaux, translations
        if verb:
            print("lm = %s" % lm)
        # parcours de chaque morceau (donné par une liste de morceaux)
        d = [[] for i in range(len(lm))]
        if verb:
            print("d = %s" % d)
        lf = range(1, len(lm))  # liste des feuilles
        if verb:
            print("lf = %s" % lf)

        from copy import copy

        if verb:
            print("\n********************\n   Step 1   \n********************")

        # étape 1 : complétion des mots
        for i, (a1, t1) in enumerate(lm):
            if tree[i] != []:
                continue  # ce morceau n'est pas une feuille
            if verb:
                print("\nComputation of piece %s/%s (%s, %s)..." % (i, len(lm), a1, t1))
                # print "lf = %s"%lf
                # print "d = %s"%d
                # print "tree = %s"%tree
            tr = 0  # translation totale
            if d[i] != []:
                if d[i][-1] == -1:
                    continue  # le morceau était déjà fini de calculé
                # va à la fin du mot
                for j in d[i]:
                    if j < 0:
                        break
                    tr += lm[j][1]
                # calcule b^np*a + tr
            a = a1.unshift(0, np).prune().minimize()
            if tr != 0:
                if verb:
                    print("Translation of %s..." % tr)
                # TODO : ne pas recalculer cet automate déjà calculé
                a = m.move2(t=-tr, a=a)
            while True:
                # split selon les autres morceaux
                j = included(a, lf, lm)
                if j is None:
                    # détermine les morceaux qui intersectent a
                    l = []
                    for j in lf:
                        if lm[j][0].intersect(a):
                            l.append(j)
                    if len(l) < 2:
                        print("Error : intersection with %s pieces not included !!!" % len(l))
                    if verb:
                        print("Subdivision on %s pieces..." % len(l))
                    # calcule les intersections (découpe en morceaux a1)
                    for j in l:
                        a2 = lm[j][0]
                        # découpe a selon a2
                        a = m.move2(t=tr, a=a2)  # translate a2 de -tr
                        a.zero_completeOP()
                        a.shiftOP(0, np)  # multiplie par b^(-np)
                        a = a.prune().minimize()
                        k = len(lm)  # indice du nouveau morceau
                        lf.append(k)  # nouvelle feuille
                        tree[i].append(k)
                        tree.append([])
                        from copy import copy
                        # print copy
                        d.append(copy(d[i]))
                        d[k].append(j)  # ajoute la translation suivante
                        # ajoute le nouveau morceau à la liste
                        lm.append((a.intersection(a1), t1))
                        # split selon baoc
                        (ab, abc) = split_baoc(k, tr + lm[j][1], np,
                                               lm, m, aoc, verb)
                        if ab is None:
                            if verb:
                                print("k=%s, tr=%s+%s : computation to continu" % (k, tr, lm[j][1]))
                        else:
                            if abc is None:
                                if verb:
                                    print("tr=%s : end of computation" % tr)
                                # indique que le calcul de ce morceau est terminé
                                d[k].append(-1)
                            else:
                                if verb:
                                    print("tr=%s : subdivision of %s by baoc (new %s)..." % (tr, i, len(lm)))
                                lf.append(len(lm))  # nouvelle feuille
                                tree[k].append(len(lm))
                                tree.append([])
                                d.append(copy(d[k]))
                                # indique que le calcul est terminé pour ce morceau (pour l'étape 1)
                                d[len(lm)].append(-1)
                                lm.append((ab, t1))
                                lf.append(len(lm))  # nouvelle feuille
                                tree[k].append(len(lm))
                                tree.append([])
                                d.append(copy(d[k]))
                                lm.append((abc, t1))
                                # le morceau k n'est plus une feuille
                                lf.remove(k)
                    lf.remove(i)  # le morceau i n'est plus une feuille
                    # calcul fini pour ce morceau puisque ce n'est plus une feuille
                    break
                else:
                    # ajoute le morceau à la liste et translate
                    d[i].append(j)
                    # if verb: print "Translation de %s..."%lm[j][1]
                    a = m.move2(t=-lm[j][1], a=a, ar=arel[lm[j][1]])
                    tr += lm[j][1]
                # split selon baoc
                (ab, abc) = split_baoc(i, tr, np, lm, m, aoc, verb)
                if ab is None:
                    # if verb: print "tr=%s : calcul à continuer"%tr
                    pass
                else:
                    if abc is None:
                        if verb:
                            print("tr=%s : end of computation" % tr)
                    else:
                        if verb:
                            print("tr=%s : subdivision of %s by baoc (new %s)..." % (tr, i, len(lm)))
                        lf.append(len(lm))  # nouvelle feuille
                        tree[i].append(len(lm))
                        tree.append([])
                        d.append(copy(d[i]))
                        # indique que le calcul est terminé pour ce morceau (pour l'étape 1)
                        d[len(lm)].append(-1)
                        lm.append((ab, t1))
                        lf.append(len(lm))  # nouvelle feuille
                        tree[i].append(len(lm))
                        tree.append([])
                        d.append(copy(d[i]))
                        lm.append((abc, t1))
                        lf.remove(i)  # le morceau i n'est plus une feuille
                    break  # calcul fini pour ce morceau (pour cette étape)
        if verb:
            print("\n*************\n   Step 2   \n*************")

        # étape 2 : remplacement des lettres qui ne sont pas des feuilles
        while True:
            end = True
            for i in lf:
                a1, t1 = lm[i]
                if verb:
                    print("\nPiece %s/%s..." % (i, len(lm)))
                tr = 0  # translation totale
                if d[i] == []:
                    print("Error : empty sheet !!!!")
                # va à la fin du mot
                for ij, j in enumerate(d[i]):
                    if j < 0:
                        break
                    if tree[j] != []:  # il faut recalculer cette lettre
                        # calcule b^np*a + tr
                        a = a1.unshift(0, np).prune().minimize()
                        if tr != 0:
                            if verb:
                                print("Translation of %s..." % tr)
                            # TODO : ne pas recalculer cet automate déjà calculé
                            a = m.move2(t=-tr, a=a)
                        # split selon les autres morceaux
                        f = fils(tree, j)
                        if verb:
                            print("Split selon %s morceaux" % len(f))
                        k = included(a, f, lm)
                        if k is None:
                            end = False
                            # détermine les morceaux qui intersectent a
                            l = []
                            for k in lf:
                                if lm[k][0].intersect(a):
                                    l.append(k)
                            if len(l) < 2:
                                print("Error : intersection with %s pieces but not included !!!" % len(l))
                            if verb:
                                print("Subdivision en %s morceaux..." % len(l))
                            # calcule les intersections (découpe en morceaux a1)
                            for j2 in l:
                                a2 = lm[j2][0]
                                # découpe selon a2
                                a = m.move2(t=tr, a=a2)  # translate a2 de -tr
                                a.zero_completeOP()
                                a.shiftOP(0, np)  # multiplie par b^(-np)
                                a = a.prune().minimize()
                                k = len(lm)  # indice du nouveau morceau
                                lf.append(k)  # nouvelle feuille
                                tree[i].append(k)
                                tree.append([])
                                d.append(copy(d[i]))
                                d[k][ij] = j2  # remplace la lettre
                                # ajoute le nouveau morceau à la liste
                                lm.append((a.intersection(a1), t1))
                            lf.remove(i)  # i n'est plus une feuille
                            if verb:
                                print("break...")
                            break  # le morceau n'est plus une feuille
                        else:
                            # remplace la lettre
                            d[i][ij] = k
                    tr += lm[j][1]
            if end:
                break
        # compute the substitution
        s = dict()
        for i in lf:
            if d[i][-1] < 0:
                d[i].pop()
            s[i] = d[i]
        # recode the substitution
        l = s.keys()
        dl = dict()  # inverse of l
        for i, k in enumerate(l):
            dl[k] = i+1
        d = dict()
        for i in s:
            d[dl[i]] = [dl[j] for j in s[i]]
        if get_aut:
            return d, [(a, t) for i, (a, t) in enumerate(lm) if tree[i] == []]
        else:
            return d

    #to be rewritten
    def compute_substitution2(self, DetAutomaton a, DetAutomaton ap=None,
                              np=None, lt=None, method=2, method_tr=1,
                              iplus=2, imax=None, need_included=True,
                              get_aut=False, verb=True):
        r"""
        Compute a substitution whose fixed point is the g-beta-expansion given
        by the beta-adic monoid with automaton a.

        INPUT:

        - ``a``- DetAutomaton
            Automaton of the g-beta-expansion.

        - ``ap``- DetAutomaton (default: ``None``)
            Language used to do the computations : we project everything on it.

        - ``np``- int (default: ``None``)
            Power of beta for the computing. The g-beta-expansion
            must be b^np invariant.

        - ``lt``- list of elements of the integer rings
            List of translations to compute the pieces exchange.

        - ``get_aut``- Bool (default: ``False``)
            If True, gives also the list of automata.

        - ``verb``- bool (default: ``True``)
          If True, print informations about the computing.

        OUTPUT:

        A word morphism given by a dictionnary.

        EXAMPLES::

            #. Full Tribonnacci::

                sage: m = BetaAdicSet((x^3-x^2-x-1).roots(ring=QQbar)[1][0], )
                sage: m.compute_substitution(verb=False)          # long time
                {1: [1, 3], 2: [1], 3: [1, 2]}
        """
        m = self
        if ap is None:
            if hasattr(self, 'tss'):
                ap = DetAutomaton(self.tss)
            else:
                ap = DetAutomaton(None).full(list(self.C))
        if verb:
            print("ap=%s" % ap)
        cdef DetAutomaton aa
        if not a.included(ap):
            aa = a.copy()
            aa.zero_completeOP()
            # check that Qap contains Qaa
            if not m.Proj(ap, aa).equals_langages(aa) and need_included:
                raise ValueError("The g-beta-set described by a is not included in the one described by ap.")
            # project aa on ap
            aa = m.Proj(aa, ap)
        else:
            aa = a
        if verb:
            print("aa=%s" % aa)
        A = aa.A
        # test if np is big enough
        if np is None:
            for i in range(1, 300):
                ba = aa.unshift(0, i)
                ba.zero_completeOP()
                if m.Proj(aa, ba).equals_langages(ba):
                    ba = m.Proj(ba, aa)
                    np = i
                    break
            if np is None:
                raise ValueError('The g-beta-expansion must be b^np invariant for some natural integer np.')
        else:
            ba = aa.unshift(0, np)
            ba.zero_completeOP()
            if not m.Proj(aa, ba).equals_langages(ba):
                raise ValueError('The g-beta-expansion must be b^np invariant (here np=%s).' % np)
            ba = m.Proj(ba, aa)
        if verb:
            print("np = %s" % np)
        # compute the pieces exchange
        if lt is None:
            raise NotImplementedError("You have to compute the domain exchange yourself for the moment !")
        lt = [(m.Proj(a, ap), t) for a, t in lt]
        if verb:
            print("Exchange of %s pieces" % len(lt))
        # calcule l'induction à partir de la liste de (morceau, translation)
        # précalculs
        if verb:
            print("Pre-computation...")
        arel = dict()
        for a, t in lt:
            arel[t] = m.relations_automaton(t=-t, A=aa.A,
                                             B=ap.A, couples=True)
            if verb:
                print("arel[%s]=%s" % (t, arel[t]))
        if verb:
            print("ba : %s" % ba)
        # tree de subdivision des morceaux
        tree = [range(1, len(lt) + 1)] + [[] for i in range(len(lt))] 
        if verb:
            print("initial tree: %s" % tree)
        lm = [(aa, 0)] + lt  # liste des morceaux, translations
        if verb:
            print("lm = %s" % lm)
        # parcours de chaque morceau (donné par une liste de morceaux)
        d = [[] for i in range(len(lm))]
        if verb:
            print("d = %s" % d)
        lf = range(1, len(lm))  # liste des feuilles
        if verb:
            print("lf = %s" % lf)

        from copy import copy

        if verb:
            print("\n**********************\n   Step 1   \n**********************")

        # étape 1 : complétion des mots
        for i, (a1, t1) in enumerate(lm):
            if tree[i] != []:
                continue  # ce morceau n'est pas une feuille
            if verb:
                print("\nCalcul du morceau %s/%s (%s, %s)..." % (i, len(lm), a1, t1))
                # print "lf = %s"%lf
                # print "d = %s"%d
                # print "tree = %s"%tree
            tr = 0  # translation totale
            if d[i] != []:
                if d[i][-1] == -1:
                    continue  # le morceau était déjà fini de calculé
                # va à la fin du mot
                for j in d[i]:
                    if j < 0:
                        break
                    tr += lm[j][1]
            # calcule b^np*a + tr
            a = a1.unshift(0, np).prune().minimize()
            if tr != 0:
                if verb:
                    print("Translation de %s..." % tr)
            # m.move2(t=-tr, a=a)
            # TODO : ne pas recalculer cet automate déjà calculé
            a = m.Proj(a, ap, t=-tr)
            while True:
                # split selon les autres morceaux
                j = included(a, lf, lm)
                if j is None:
                    # détermine les morceaux qui intersectent a
                    l = []
                    for j in lf:
                        if lm[j][0].intersect(a):
                            l.append(j)
                    if len(l) < 2:
                        print("Error : intersection with %s piece but not included !!!"%len(l))
                    if verb:
                        print("Subdivision on %s pieces..." % len(l))
                    # calcule les intersections (découpe en morceaux a1)
                    for j in l:
                        a2 = lm[j][0]
                        # découpe a selon a2
                        # m.move2(t=tr, a=a2) #translate a2 de -tr
                        a = m.Proj(a2, ap.unshift(0, np), t=tr)
                        a.shiftOP(0, np)  # multiplie par b^(-np)
                        a = a.prune().minimize()
                        k = len(lm)  # indice du nouveau morceau
                        lf.append(k)  # nouvelle feuille
                        tree[i].append(k)
                        tree.append([])
                        from copy import copy
                        # print copy
                        d.append(copy(d[i]))
                        d[k].append(j)  # ajoute la translation suivante
                        # ajoute le nouveau morceau à la liste
                        lm.append((a.intersection(a1), t1))
                        # split selon ba
                        (ab, abc) = split_ba(k, tr+lm[j][1], np,
                                             lm, m, aa, ap, verb)
                        if ab is None:
                            if verb:
                                print("k=%s, tr=%s+%s : calcul à continuer" % (k, tr, lm[j][1]))
                        else:
                            if abc is None:
                                if verb:
                                    print("tr=%s : calcul terminé" % tr)
                                d[k].append(-1)  # indique que le calcul de ce morceau est terminé
                            else:
                                if verb:
                                    print("tr=%s : subdivision of %s by ba (new %s)..." % (tr, i, len(lm)))
                                lf.append(len(lm))  # nouvelle feuille
                                tree[k].append(len(lm))
                                tree.append([])
                                d.append(copy(d[k]))
                                # indique que le calcul est terminé pour ce morceau (pour l'étape 1)
                                d[len(lm)].append(-1)
                                lm.append((ab, t1))
                                lf.append(len(lm))  # nouvelle feuille
                                tree[k].append(len(lm))
                                tree.append([])
                                d.append(copy(d[k]))
                                lm.append((abc, t1))
                                lf.remove(k)  # le morceau k n'est plus une feuille
                    lf.remove(i)  # le morceau i n'est plus une feuille
                    # calcul fini pour ce morceau puisque ce n'est plus une feuille
                    break
                else:
                    # ajoute le morceau à la liste et translate
                    d[i].append(j)
                    # if verb: print "Translation de %s..."%lm[j][1]
                    # m.move2(t=-lm[j][1], a=a, ar=arel[lm[j][1]])
                    a = m.Proj(a, ap, t=-lm[j][1], arel=arel[lm[j][1]])  
                    tr += lm[j][1]
                # split selon ba
                (ab, abc) = split_ba(i, tr, np, lm, m, aa, ap, verb)
                if ab is None:
                    pass
                    # if verb: print "tr=%s : calcul à continuer"%tr
                else:
                    if abc is None:
                        if verb:
                            print("tr=%s : end of computation" % tr)
                    else:
                        if verb:
                            print("tr=%s : subdivision of %s by ba (new %s)..." % (tr, i, len(lm)))
                        lf.append(len(lm))  # nouvelle feuille
                        tree[i].append(len(lm))
                        tree.append([])
                        d.append(copy(d[i]))
                        # indique que le calcul est terminé pour ce morceau (pour l'étape 1)
                        d[len(lm)].append(-1)
                        lm.append((ab, t1))
                        lf.append(len(lm))  # nouvelle feuille
                        tree[i].append(len(lm))
                        tree.append([])
                        d.append(copy(d[i]))
                        lm.append((abc, t1))
                        lf.remove(i)  # le morceau i n'est plus une feuille
                    break  # calcul fini pour ce morceau (pour cette étape)

        if verb:
            print("\n*************\n   Step 2   \n*************")

        # étape 2 : remplacement des lettres qui ne sont pas des feuilles
        while True:
            end = True
            for i in lf:
                a1, t1 = lm[i]
                if verb:
                    print("\nPiece %s/%s..." % (i, len(lm)))
                tr = 0  # translation totale
                if d[i] == []:
                    print("Error : empty sheet !!!!")
                # va à la fin du mot
                for ij, j in enumerate(d[i]):
                    if j < 0:
                        break
                    if tree[j] != []:  # il faut recalculer cette lettre
                        # calcule b^np*a + tr
                        a = a1.unshift(0, np).prune().minimize()
                        if tr != 0:
                            if verb:
                                print("Translation of %s..." % tr)
                        # m.move2(t=-tr, a=a)
                        # TODO : ne pas recalculer cet automate déjà calculé
                        a = m.Proj(a, ap, t=-tr)
                        # split selon les autres morceaux
                        f = fils(tree, j)
                        if verb:
                            print("Split by %s pieces" % len(f))
                        k = included(a, f, lm)
                        if k is None:
                            end = False
                            # détermine les morceaux qui intersectent a
                            l = []
                            for k in lf:
                                if lm[k][0].intersect(a):
                                    l.append(k)
                            if len(l) < 2:
                                print("Error : intersection with %s pieces but not included !!!" % len(l))
                            if verb:
                                print("Subdivision of %s pieces..." % len(l))
                            # calcule les intersections (découpe en morceaux a1)
                            for j2 in l:
                                a2 = lm[j2][0]
                                # découpe selon a2
                                # a = m.move2(t=tr, a=a2) #translate a2 de -tr
                                # a.zero_completeOP()
                                a = m.Proj(a2, ap.unshift(0, np), t=tr)
                                a.shiftOP(0, np)  # multiplie par b^(-np)
                                a = a.prune().minimize()
                                k = len(lm)  # indice du nouveau morceau
                                lf.append(k)  # nouvelle feuille
                                tree[i].append(k)
                                tree.append([])
                                d.append(copy(d[i]))
                                d[k][ij] = j2  # remplace la lettre
                                # ajoute le nouveau morceau à la liste
                                lm.append((a.intersection(a1), t1))
                            lf.remove(i)  # i n'est plus une feuille
                            if verb:
                                print("break...")
                            break  # le morceau n'est plus une feuille
                        else:
                            # remplace la lettre
                            d[i][ij] = k
                    tr += lm[j][1]
            if end:
                break
        # compute the substitution
        s = dict()
        for i in lf:
            if d[i][-1] < 0:
                d[i].pop()
            s[i] = d[i]
        # recode the substitution
        l = s.keys()
        dl = dict()  # inverse of l
        for i, k in enumerate(l):
            dl[k] = i+1
        d = dict()
        for i in s:
            d[dl[i]] = [dl[j] for j in s[i]]
        if get_aut:
            return d, [(a, t) for i, (a, t) in enumerate(lm) if tree[i] == []]
        else:
            return d

