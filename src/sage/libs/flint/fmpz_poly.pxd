include "sage/ext/stdsage.pxi"

from flint cimport *
include "fmpz_poly.pxi"

from sage.structure.sage_object cimport SageObject

cdef class Fmpz_poly(SageObject):
    cdef fmpz_poly_t poly

<<<<<<< HEAD
=======
cdef extern from "flint/fmpz_poly.h":
    cdef void fmpz_poly_revert_series(fmpz_poly_t output, fmpz_poly_t input,
            unsigned long length)
>>>>>>> 18a4842... trac #16583, oops, correcting wrong merge
