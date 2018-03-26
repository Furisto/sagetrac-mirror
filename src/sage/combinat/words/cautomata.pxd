
#import os
#os.chdir(os.path.dirname(__file__))

cdef extern from "Automaton.h":
    ctypedef char bool
    cdef cppclass Etat:
        int* f
        bool final
    cdef cppclass Automate:
        Etat* e # états
        int n   # nombre d'états
        int na  # nombre de lettres
        int i # état initial

cdef extern from "automataC.h":
    Automate NewAutomaton (int n, int na)
    void FreeAutomaton (Automate *a)

ctypedef Automate Automaton

cdef class FastAutomaton:
    cdef Automate* a
    cdef public list A
    cdef set_a(self, Automate a)

cdef extern from "Automaton.h":
    ctypedef char bool
    cdef cppclass Arete:
        int l # label
        int e # état d'arrivée
    cdef cppclass NEtat:
        Arete* a
        int n
        bool final
        bool initial
    cdef cppclass NAutomate:
        NEtat* e # états
        int n   # nombre d'états
        int na  # nombre de lettres

cdef class NFastAutomaton:
    cdef NAutomate* a
    cdef list A
