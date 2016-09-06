r"""
Joint Spectral Radius

This modules contains algorithms in conjunction with the
:wikipedia:`joint spectral radius <Joint_spectral_radius>`.


Various
=======

AUTHORS:

- Daniel Krenn (2016)

ACKNOWLEDGEMENT:

- Daniel Krenn is supported by the
  Austrian Science Fund (FWF): P 24644-N26.


Functions
=========
"""
#*****************************************************************************
#       Copyright (C) 2016 Daniel Krenn <dev@danielkrenn.at>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************


def joint_spectral_radius(S, delta=None, norm=None, ring=None):
    r"""
    Return a lower and upper bound for the joint spectral radius
    of the given matrices.

    INPUT:

    - ``S`` -- an tuple or other iterable of matrices.

    - TODO

    TESTS::

        sage: import logging
        sage: logging.basicConfig()
        sage: logger = logging.getLogger()
        sage: logger.setLevel(logging.INFO)

    Gripenberg, Section 4 (result is between `0.6596789`
    and `0.6596924`)::

        sage: joint_spectral_radius(  # long time
        ....:     (Matrix([[3, 0],  [1, 3]]) / 5,
        ....:      Matrix([[3, -3], [0, -1]]) / 5),
        ....:     delta=RIF(0.0001))
        verbose 1 (joint_spectral_radius) lower bound: 0.659678908955284?
        verbose 1 (joint_spectral_radius) upper bound: 0.659778908955284?
        verbose 1 (joint_spectral_radius) iterations m: 48
        verbose 1 (joint_spectral_radius) max size of T_m: 21
        (0.659678908955284?, 0.659778908955284?)

    ::

        sage: logger.setLevel(logging.WARNING)

    Dumas, Example 3 (result is `1`)::

        sage: A0 = Matrix([[1, 1, 1], [0, 0, 0],  [0, 0, 0]])
        sage: A1 = Matrix([[1, 0, 0], [0, 1, -1], [0, 0, 0]])
        sage: A2 = Matrix([[0, 0, 0], [1, 1, 0],  [0, 0, 1]])
        sage: A3 = Matrix([[0, 0, 0], [0, 0, 0],  [1, -1, 1]])
        sage: joint_spectral_radius((A0, A1, A2, A3),  # long time
        ....:     delta=RIF(0.1))
        (1, 1.200000000000000?)

    Dumas, Example 4 (result is `1`)::

        sage: A0 = Matrix([[1, 1/2, 0], [0, 1/2, 0], [0, 1/2, 1]])
        sage: A1 = Matrix([[1/2, 0, 0], [1/2, 1, 0], [1/2, 0, 1]])
        sage: joint_spectral_radius((A0, A1), delta=RIF(0.2))

    Dumas, Example 5 (result is `3\sqrt{2}=4.24\dots`)::

        sage: A0 = Matrix([[1, 0], [0, 1]])
        sage: A1 = Matrix([[3, -3], [3, 3]])
        sage: joint_spectral_radius((A0, A1), delta=RIF(0.2))
        (4.242640687119285?, 4.2426406871192848?)

    Dumas, Example 6 (result is `1`)::

        sage: B0 = Matrix([[1/2, 0], [1/2, 1]])
        sage: B1 = Matrix([[1/2, 0], [-1/2, 1]])
        sage: Z = zero_matrix(2, 2)
        sage: A0 = block_matrix([[B1, Z], [Z, B0]])
        sage: A1 = block_matrix([[Z, Z], [B0, B1]])
        sage: joint_spectral_radius((A0, A1), delta=RIF(0.2))
        (1, 1.200000000000000?)
    """
    #from itertools import count
    from sage.arith.srange import srange
    from sage.misc.misc_c import prod

    import logging
    logger = logging.getLogger(__name__)

    S = tuple(S)
    if ring is None:
        from sage.rings.real_mpfi import RIF
        ring = RIF
    R = ring
    if delta is None:
        delta = R(0.2)
    if norm is None:
        norm = lambda M: M.norm(2)
    Rnorm = lambda M: R(norm(M))

    def rho(M):
        return max(R(abs(v)) for v in M.eigenvalues())

    def pp(X, j):
        return Rnorm(prod(X[:j]))**(1/R(j))

    def p(X):
        return min(pp(X, j) for j in srange(1, len(X)+1))

    T = tuple(((M,), Rnorm(M)) for M in S)
    alpha = max(rho(M) for M in S)
    beta = max(pX for X, pX in T)  # pX equals Rnorm(M) here
    ell = 0

    for mm in srange(2, 1000):  #count(1):
        m = mm   # TODO; m = ZZ(mm)

        prepreT = tuple((X + (M,), pX)
                        for X, pX in T for M in S)
        preT = tuple((X, min(pX, pp(X, len(X)))) for X, pX in prepreT)
        T = tuple((X, pX) for X, pX in preT if pX > alpha + delta)

        ell = max(ell, len(T))
        if T:
            alpha = max(alpha,
                        max(rho(prod(Y))**(1/R(m)) for Y, pY in T))
            beta = min(beta,
                       max(alpha + delta,
                           max(pY for Y, pY in T)))
        else:
            beta = min(beta, alpha + delta)

        logger.debug('m=%s, alpha=%s, beta=%s, len(T)=%s',
                     m, alpha, beta, len(T))

        if not T:
            break

    logger.info('lower bound: %s', alpha)
    logger.info('upper bound: %s', beta)
    logger.info('iterations m: %s', m)
    logger.info('max size of T_m: %s', ell)

    print "beta-alpha <= delta", beta - alpha, delta  # TODO
    return (alpha, beta)

#def test():
#    A0 = Matrix([[1,1,1], [0,0,0], [0,0,0]])
#    A1 = Matrix([[1,0,0], [0,1,-1], [0,0,0]])
#    A2 = Matrix([[0,0,0], [1,1,0], [0,0,1]])
#    A3 = Matrix([[0,0,0], [0,0,0], [1,-1,1]])
#    print joint_spectral_radius([A0, A1, A2, A3])

#test()
