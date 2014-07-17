include "sage/libs/flint/fmpz.pxi"

cdef extern from "flint/fmpz_mod_poly.h":
    ctypedef void* fmpz_mod_poly_t

    void fmpz_mod_poly_init(fmpz_mod_poly_t poly, const fmpz_t p)
    void fmpz_mod_poly_clear(fmpz_mod_poly_t poly)

    void fmpz_mod_poly_set_coeff_fmpz(fmpz_mod_poly_t poly, long n, const fmpz_t x)
    void fmpz_mod_poly_get_coeff_fmpz(fmpz_t x, const fmpz_mod_poly_t poly, long n)
