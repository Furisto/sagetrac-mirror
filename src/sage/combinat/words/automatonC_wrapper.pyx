# coding=utf8
"""
Wrapper for automatonC  of Finite state machines using C


AUTHORS:

- Paul Mercat (2013)- I2M AMU Aix-Marseille Universite - initial version
- Dominique Benielli (2018) Labex Archimede - I2M -
  AMU Aix-Marseille Universite - Integration in -SageMath


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
# *****************************************************************************
from __future__ import print_function
from libc.stdlib cimport malloc, free

cimport sage.combinat.words.automatonC_wrapper
from cysignals.signals cimport sig_on, sig_off, sig_check
from cpython cimport bool as c_bool
from .cautomata import  FastAutomaton, NFastAutomaton
from .cautomata cimport getAutomaton, list_to_Dict

cdef extern from "automataC.h":
    cdef cppclass Dict:
        int* e
        int n
    cdef cppclass InvertDict:
        Dict* d
        int n
    bool DotExists()
    #    Automaton NewAutomaton (int n, int na)
    #    void FreeAutomaton (Automaton *a)
    void FreeNAutomaton(NAutomaton *a)
    Automaton CopyAutomaton(Automaton a, int nalloc, int naalloc)
    Automaton PieceAutomaton(Automaton a, int *w, int n, int e)
    void init(Automaton *a)
    void printAutomaton(Automaton a)
    void plotDot(const char *file, Automaton a, const char **labels, const char *graph_name, double sx, double sy, const char **vlabels, bool html, bool verb, bool run_dot)
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


def _dotExists_wrapper():
    """
    Test the Doexist c Function.

    OUTPUT:

    Return ``True`` or `False `` if file exist

    TESTS::

        sage: _dotExists_wrapper()
        sage: True


    """
    sig_on()
    if DotExists():
        sig_off()
        return True
    sig_off()
    return False


# def _copyAutomaton_wrapper(fa):
#     """
#     Test the copyAutomaton c Function.
# 
# 
#     INPUT:
# 
#     - ``fa`` -- FastAutomaton
# 
# 
#     OUTPUT:
# 
#     Return a copy of c automaton
# 
# 
#     TESTS::
# 
#         sage: a = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)
#         sage: _copyAutomaton_wrapper(a)
# 
#     """
#     cdef Automaton aut
#     cdef Automaton * pa = fa.a
#     sig_on()
#     aut = CopyAutomaton(pa[0], fa.a.n+1, fa.a.na)
#     sig_off()
#     return aut


# def _NewDict(n):
#     """
#     Test the _NewDict c Function.
# 
# 
#     INPUT:
# 
#     - ``n`` -- number of eleme,ts of the new dict
# 
# 
#     OUTPUT:
# 
#     Return a new dict of c automaton
# 
#     TESTS::
# 
#         sage: r = _NewDict(3)
#         sage: r
# 
#     """
#     cdef Dict r
#     sig_on()
#     r = NewDict(n)
#     sig_off()
#     return r


def _RecWord(fa, li):
    """
    Test the _NewDict c Function.


    INPUT:

    - ``a`` -- automaton

    - `d` -- dictionary

    OUTPUT:

    Return ``True`` or `False `` if 


    TESTS::

        sage: a = [(0, 1, 'a'), (2, 3, 'b')] 
        sage: fa = FastAutomaton([(0, 1, 'a'), (2, 3, 'b')], i=0)

        sage: fa = DiGraph(a, multiedges=True, loops=True)
        sage: b = _RecWord(fa, d)
        sage: b

    """
    cdef bool res
    cdef Automaton a
    cdef Dict d
    a = getAutomaton(fa)
    d = list_to_Dict(li)
    sig_on()
    res = rec_word(a, d)
    sig_off()
    return c_bool(res)
    