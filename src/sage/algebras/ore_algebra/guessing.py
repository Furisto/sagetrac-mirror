
"""
guessing
========

"""


#############################################################################
#  Copyright (C) 2013, 2014                                                 #
#                Manuel Kauers (mkauers@gmail.com),                         #
#                Maximilian Jaroschek (mjarosch@risc.jku.at),               #
#                Fredrik Johansson (fjohanss@risc.jku.at).                  #
#                                                                           #
#  Distributed under the terms of the GNU General Public License (GPL)      #
#  either version 2, or (at your option) any later version                  #
#                                                                           #
#  http://www.gnu.org/licenses/                                             #
#############################################################################


######### development mode ###########

try:
    if sys.modules.has_key('ore_algebra'):
        del sys.modules['ore_algebra']
except:
    pass

#######################################

from sage.rings.integer_ring import ZZ
from sage.rings.rational_field import QQ
from sage.rings.finite_rings.all import GF
from sage.rings.finite_rings.finite_field_base import is_FiniteField
from sage.matrix.constructor import Matrix, matrix
from sage.rings.arith import xgcd
from sage.parallel.decorate import parallel
from sage.rings.polynomial.polynomial_ring import is_PolynomialRing

from ore_algebra import *

from datetime import datetime
import nullspace
import math
from nullspace import _hermite

def guess_rec(data, n, S, **kwargs):
    """
    Shortcut for ``guess`` applied with an Ore algebra of shift operators in `S` over `K[n]`
    where `K` is the parent of ``data[0]``.

    See the docstring of ``guess`` for further information.    
    """
    R = data[0].parent()[n]; x = R.gen()
    return guess(data, OreAlgebra(R, (S, {n:n+R.one()}, {})), **kwargs)

def guess_deq(data, x, D, **kwargs):
    """
    Shortcut for ``guess`` applied with an Ore algebra of differential operators in `D` over `K[x]`
    where `K` is the parent of ``data[0]``.

    See the docstring of ``guess`` for further information.    
    """
    R = data[0].parent()[x]; x = R.gen()
    return guess(data, OreAlgebra(R, (D, {}, {x:R.one()})), **kwargs)

def guess_qrec(data, qn, Q, q, **kwargs):
    """
    Shortcut for ``guess`` applied with an Ore algebra of `q`-recurrence operators in `Q` over `K[qn]`
    where `K` is the parent of `q`.

    See the docstring of ``guess`` for further information.    
    """
    R = q.parent()[qn]; x = R.gen()
    return guess(data, OreAlgebra(R, (Q, {qn:q*qn}, {qn:R.one()})), **kwargs)

def guess(data, algebra, **kwargs):
    """
    Searches for an element of the algebra which annihilates the given data.

    INPUT:

    - ``data`` -- a list of elements of the algebra's base ring's base ring `K` (or at least
      of objects which can be casted into this ring). If ``data`` is a string, it is assumed
      to be the name of a text file which contains the terms, one per line, encoded in a way
      that can be interpreted by the element constructor of `K`. 
    - ``algebra`` -- a univariate Ore algebra over a univariate polynomial ring whose
      generator is the standard derivation, the standard shift, the forward difference,
      a q-shift, or a commutative variable. 

    Optional arguments:

    - ``cut`` -- if `N` is the minimum number of terms needed for some particular
      choice of order and degree, and if ``len(data)`` is more than ``N+cut``,
      use ``data[:N+cut]`` instead of ``data``. This must be a nonnegative integer
      or ``None``. Default: ``None``.
    - ``ensure`` -- if `N` is the minimum number of terms needed for some particular
      choice of order and degree, and if ``len(data)`` is less than ``N+ensure``,
      raise an error. This must be a nonnegative integer. Default: 0.
    - ``ncpus`` -- number of processors to be used. Defaut: 1.
    - ``order`` -- bounds the order of the operators being searched for.
      Default: infinity.
    - ``min_order`` -- smallest order to be considered in the search. The output
      may nevertheless have lower order than this bound. Default: 1
    - ``degree`` -- bounds the degree of the operators being searched for.
      The method may decide to overrule this setting if it thinks this may speed up
      the calculation. Default: infinity.
    - ``min_degree`` -- smallest degree to be considered in the search. The output
      may nevertheless have lower degree than this bound. Default: 0
    - ``path`` -- a list of pairs `(r, d)` specifying which orders and degrees
      the method should attempt. If this value is equal to ``None`` (default), a
      path is chosen which examines all the `(r, d)` which can be tested with the
      given amount of data. 
    - ``solver`` -- function to be used for computing the right kernel of a matrix
      with elements in `K`. 
    - ``infolevel`` -- an integer specifying the level of details of progress
      reports during the calculation. 

    OUTPUT:

    - An element of ``algebra`` which annihilates the given ``data``.

    An error is raised if no such element is found. 

    .. NOTE::

    - This method is designed to find equations for D-finite objects. It may exhibit strange
      behaviour for objects which are holonomic but not D-finite. 
    - When the generator of the algebra is a commutative variable, the method searches for 
      algebraic equations.

    EXAMPLES::

      sage: rec = guess([(2*i+1)^15 * (1 + 2^i + 3^i)^2 for i in xrange(1000)], OreAlgebra(ZZ['n'], 'Sn'))
      sage: rec.order(), rec.degree()
      (6, 90)
      sage: R.<t> = QQ['t']
      sage: rec = guess([1/(i+t) + t^i for i in xrange(100)], OreAlgebra(R['n'], 'Sn'))
      sage: rec
      ((t - 1)*n^2 + (2*t^2 + t - 2)*n + t^3 + 2*t^2)*Sn^2 + ((-t^2 + 1)*n^2 + (-2*t^3 - 3*t^2 + 2*t + 1)*n - t^4 - 3*t^3 - t^2 + t)*Sn + (t^2 - t)*n^2 + (2*t^3 - t)*n + t^4 + t^3 - t^2
    
    """

    A = algebra; R = A.base_ring(); K = R.base_ring(); x = R.gen()

    if type(data) == str:
        with open(data, 'r') as f:
            data = [ K(line) for line in f ]

    if A.ngens() > 1 or R.ngens() > 1:
        raise TypeError, "unexpected algebra: " + str(A)
    
    elif R.is_field():
        return guess(data, A.change_ring(R.ring()), **kwargs)

    elif A.is_F() is not False:
        # reduce to shift case; note that this does not alter order or degrees
        if kwargs.has_key('infolevel') and kwargs['infolevel'] >= 1:
            print "Translating problem to shift case..."
        A0 = OreAlgebra(R, ('S', {x:x+K.one()}, {}))
        return guess(data, A0, **kwargs).change_ring(R).to_F(A)

    elif (not A.is_S() and not A.is_D() and not A.is_Q() and not A.is_C()):
        raise TypeError, "unexpected algebra: " + str(A)

    elif K.is_prime_field() and K.characteristic() > 0:
        return _guess_via_gcrd(data, A, **kwargs)

    elif K is ZZ:
        # CRA
        return _guess_via_hom(data, A, _word_size_primes(), lambda mod : GF(mod), **kwargs)

    elif is_PolynomialRing(K) and K.base_ring().is_prime_field() and K.characteristic() > 0:  # K == GF(p)[t]
        # eval/interpol
        mod = _linear_polys(K.gen(), 7, K.characteristic())
        to_hom = lambda mod : (lambda pol : pol(-mod[0]))
        return _guess_via_hom(data, A, mod, to_hom, **kwargs)

    elif is_PolynomialRing(K) and K.base_ring() is ZZ:  # K == ZZ[t]
        # CRA + eval/interpol

        KK = QQ[K.gens()].fraction_field() ## all elements of 'data' must be coercible to KK
        KK2 = ZZ[K.gens()].fraction_field() ## rewrite them as elements of KK2

        def cleanup(rat):
            rat = KK(rat)
            n, d = rat.numerator(), rat.denominator() # live in QQ[t]
            nn, nd = n.numerator(), n.denominator()
            dn, dd = d.numerator(), d.denominator()
            return KK2(K(nn*dd)/K(nd*dn))

        data = map(cleanup, data)

        def to_hom(mod):
            KK3 = GF(mod); KK4 = KK3[K.gens()]; KK5 = KK4.fraction_field()
            return lambda rat: KK5(KK4(rat.numerator()).map_coefficients(KK3, KK3) / \
                                   KK4(rat.denominator()).map_coefficients(KK3, KK3))

        return _guess_via_hom(data, A, _word_size_primes(), to_hom, **kwargs)

    elif K is QQ:
        return guess(data, A.change_ring(ZZ[x]), **kwargs)

    elif K.is_field():
        return guess(data, A.change_ring(K.ring()[x]), **kwargs)

    elif is_PolynomialRing(K) and K.base_ring() is QQ:
        return guess(data, A.change_ring(ZZ[K.gens()][x]), **kwargs)

    else:
        raise TypeError, "unexpected coefficient domain: " + str(K)

###########################################################################################

def guess_raw(data, A, order=-1, degree=-1, lift=None, solver=None, cut=25, ensure=0, infolevel=0):
    """
    Guesses recurrence or differential equations for a given sample of terms.

    INPUT:

    - ``data`` -- list of terms
    - ``A`` -- an Ore algebra of recurrence operators, differential operators,
      or q-differential operators. 
    - ``order`` -- maximum order of the sought operators
    - ``degree`` -- maximum degree of the sought operators
    - ``lift`` (optional) -- a function to be applied to the terms in ``data``
      prior to computation
    - ``solver`` (optional) -- a function to be used to compute the nullspace
      of a matrix with entries in the base ring of the base ring of ``A``
    - ``cut`` (optional) -- if `N` is the minimum number of terms needed for
      the the specified order and degree and ``len(data)`` is more than ``N+cut``,
      use ``data[:N+cut]`` instead of ``data``. This must be a nonnegative integer
      or ``None``.
    - ``ensure`` (optional) -- if `N` is the minimum number of terms needed
      for the specified order and degree and ``len(data)`` is less than ``N+ensure``,
      raise an error. This must be a nonnegative integer.
    - ``infolevel`` (optional) -- an integer indicating the desired amount of
      progress report to be printed during the calculation. Default: 0 (no output).

    OUTPUT:

    A basis of the ``K``-vector space of all the operators `L` in ``A`` of order
    at most ``order`` and degree at most ``degree`` such that `L` applied to
    ``data`` gives an array of zeros. (resp. `L` applied to the truncated power
    series with ``data`` as terms gives the zero power series) 

    An error is raised in the following situations:

    * the algebra ``A`` has more than one generator, or its unique generator
      is neither a standard shift nor a q-shift nor a standard derivation.
    * ``data`` contains some item which does not belong to ``K``, even after
      application of ``lift``
    * if the condition on ``ensure`` is violated. 
    * if the linear system constructed by the method turns out to be
      underdetermined for some other reason, e.g., because too many linear
      constraints happen to be trivial.

    ALGORITHM:

    Ansatz and linear algebra.

    .. NOTE::

      This is a low-level method. Don't call it directly unless you know what you
      are doing. In usual applications, the right method to call is ``guess``.

    EXAMPLES::

      sage: K = GF(1091); R.<n> = K['n']; A = OreAlgebra(R, 'Sn')
      sage: data = [(5*n+3)/(3*n+4)*fibonacci(n)^3 for n in xrange(200)]
      sage: guess_raw(data, A, order=5, degree=3, lift=K)
      [(n^3 + 546*n^2 + 588*n + 786)*Sn^5 + (356*n^3 + 717*n^2 + 381*n + 449)*Sn^4 + (8*n^3 + 569*n^2 + 360*n + 214)*Sn^3 + (31*n^3 + 600*n^2 + 784*n + 287)*Sn^2 + (1078*n^3 + 1065*n^2 + 383*n + 466)*Sn + 359*n^3 + 173*n^2 + 503, (n^3 + 1013*n^2 + 593*n + 754)*Sn^5 + (797*n^3 + 56*n^2 + 7*n + 999)*Sn^4 + (867*n^3 + 1002*n^2 + 655*n + 506)*Sn^3 + (658*n^3 + 834*n^2 + 1036*n + 899)*Sn^2 + (219*n^3 + 479*n^2 + 476*n + 800)*Sn + 800*n^3 + 913*n^2 + 280*n]
    
    """

    if min(order, degree) < 0:
        return [] 

    R = A.base_ring(); K = R.base_ring(); q = A.is_Q()

    def info(bound, msg):
        if bound <= infolevel:
            print msg

    info(1, datetime.today().ctime() + ": raw guessing started.")
    info(1, "len(data)=" + str(len(data)) + ", algebra=" + str(A._latex_()))

    if A.ngens() > 1 or (not A.is_S() and not A.is_Q() and not A.is_D() ):
        raise TypeError, "unexpected algebra"

    diff_case = True if A.is_D() else False
    deform = (lambda n: q[1]**n) if q is not False else (lambda n: n)
    min_len_data = (order + 1)*(degree + 2)

    if cut is not None and len(data) > min_len_data + cut:
        data = data[:min_len_data + cut]

    if len(data) < min_len_data + ensure:
        raise ValueError, "not enough terms"

    if lift is not None:
        data = map(lift, data)

    if not all(p in K for p in data):
        raise ValueError, "illegal term in data list"

    if solver is None:
        solver = A._solver(K)
        
    if solver is None:
        solver = nullspace.sage_native

    sys = {(0,0):data}
    nn = [deform(n) for n in xrange(len(data))]
    z = [K.zero()]

    if diff_case:
        # sys[i, j] contains ( x^i * D^j ) (data)
        nn = nn[1:]
        for j in xrange(order):
            sys[0, j + 1] = map(lambda a,b: a*b, sys[0, j][1:], nn)
            nn.pop(); 
        for i in xrange(degree):
            for j in xrange(order + 1):
                sys[i + 1, j] = z + sys[i, j]
    else:
        # sys[i, j] contains ( (n+j)^i * S^j ) (data)
        for i in xrange(degree):
            sys[i + 1, 0] = map(lambda a,b: a*b, sys[i, 0], nn)
        for j in xrange(order):
            for i in xrange(degree + 1):
                sys[i, j + 1] = sys[i, j][1:]

    sys = [sys[i, j] for j in xrange(order + 1) for i in xrange(degree + 1) ]

    trim = min(len(c) for c in sys)
    for i in xrange(len(sys)):
        if len(sys[i]) > trim:
            sys[i] = sys[i][:trim]

    sys = matrix(K, zip(*sys))

    info(2, datetime.today().ctime() + ": matrix construction completed. size=" + str(sys.dimensions()))
    sol = solver(sys, infolevel=infolevel - 2)
    del sys 
    info(2, datetime.today().ctime() + ": nullspace computation completed. size=" + str(len(sol)))

    sigma = A.sigma()
    for l in xrange(len(sol)):
        c = []; s = list(sol[l])
        for j in xrange(order + 1):
            c.append(sigma(R(s[j*(degree + 1):(j + 1)*(degree + 1)]), j))
        sol[l] = A(c)
        sol[l] *= ~sol[l].leading_coefficient().leading_coefficient()

    return sol

###########################################################################################

def guess_hp(data, A, order=-1, degree=-1, lift=None, cut=25, ensure=0, infolevel=0):
    """
    Guesses differential equations or algebraic equations for a given sample of terms.

    INPUT:

    - ``data`` -- list of terms
    - ``A`` -- an Ore algebra of differential operators or ordinary polynomials. 
    - ``order`` -- maximum order of the sought operators
    - ``degree`` -- maximum degree of the sought operators
    - ``lift`` (optional) -- a function to be applied to the terms in ``data``
      prior to computation
    - ``cut`` (optional) -- if `N` is the minimum number of terms needed for
      the the specified order and degree and ``len(data)`` is more than ``N+cut``,
      use ``data[:N+cut]`` instead of ``data``. This must be a nonnegative integer
      or ``None``.
    - ``ensure`` (optional) -- if `N` is the minimum number of terms needed
      for the specified order and degree and ``len(data)`` is less than ``N+ensure``,
      raise an error. This must be a nonnegative integer.
    - ``infolevel`` (optional) -- an integer indicating the desired amount of
      progress report to be printed during the calculation. Default: 0 (no output).

    OUTPUT:

    A basis of the ``K``-vector space of all the operators `L` in ``A`` of order
    at most ``order`` and degree at most ``degree`` such that `L` applied to
    the truncated power series with ``data`` as terms gives the zero power series.

    An error is raised in the following situations:

    * the algebra ``A`` has more than one generator, or its unique generator
      is neither a standard derivation nor a commutative variable. 
    * ``data`` contains some item which does not belong to ``K``, even after
      application of ``lift``
    * if the condition on ``ensure`` is violated. 

    ALGORITHM:

    Hermite-Pade approximation.

    .. NOTE::

      This is a low-level method. Don't call it directly unless you know what you
      are doing. In usual applications, the right method to call is ``guess``.

    EXAMPLES::

      sage: K = GF(1091); R.<x> = K['x']; 
      sage: data = [binomial(2*n, n)*fibonacci(n)^3 for n in xrange(2000)]
      sage: guess_hp(data, OreAlgebra(R, 'Dx'), order=4, degree=4, lift=K)
      [(x^4 + 819*x^3 + 136*x^2 + 17*x + 635)*Dx^4 + (14*x^3 + 417*x^2 + 952*x + 605)*Dx^3 + (598*x^2 + 497*x + 99)*Dx^2 + (598*x + 794)*Dx + 893]
      sage: len(guess_hp(data, OreAlgebra(R, 'C'), order=16, degree=64, lift=K))
      1
    
    """

    if min(order, degree) < 0:
        return [] 

    R = A.base_ring(); K = R.base_ring()

    def info(bound, msg):
        if bound <= infolevel:
            print msg

    info(1, datetime.today().ctime() + ": Hermite/Pade guessing started.")
    info(1, "len(data)=" + str(len(data)) + ", algebra=" + str(A._latex_()))

    if A.ngens() > 1 or (not A.is_C() and not A.is_D() ):
        raise TypeError, "unexpected algebra"

    diff_case = True if A.is_D() else False
    min_len_data = (order + 1)*(degree + 2)

    if cut is not None and len(data) > min_len_data + cut:
        data = data[:min_len_data + cut]

    if len(data) < min_len_data + ensure:
        raise ValueError, "not enough terms"

    if lift is not None:
        data = map(lift, data)

    if not all(p in K for p in data):
        raise ValueError, "illegal term in data list"

    if diff_case:
        series = [R(data)]
        for i in xrange(order):
            series.append(series[-1].derivative())
        truncate = len(data) - order 
        series = [s.truncate(truncate) for s in series]
    else:
        truncate = len(data)
        series = [R.one(), R(data)]
        for i in xrange(order - 1):
            series.append((series[1]*series[-1]).truncate(truncate))

    info(2, datetime.today().ctime() + ": matrix construction completed.")
    sol = _hermite(True, matrix(R, [series]), [degree], infolevel - 2, truncate = truncate - 1)
    info(2, datetime.today().ctime() + ": hermite pade approximation completed.")

    sol = [A(map(R, s)) for s in sol]
    sol = [(~L.leading_coefficient().leading_coefficient())*L for L in sol]

    return sol    

###########################################################################################

def _guess_via_hom(data, A, modulus, to_hom, **kwargs):
    """
    Implementation of guessing via homomorphic images.

    INPUT:

    - ``data``: list of terms
    - ``A``: an algebra of the form K[x][X]
    - ``modulus``: an iterator which produces appropriate moduli
    - ``to_hom``: a callable which turns a given modulus to a map from K to some hom image domain

    OUTPUT:

    - ``L`` in ``A``, the guessed operator.
    - if the option ``return_short_path`` is given and ``True``, return the pair ``(L, path)``.
    
    Covers three cases:

    1. K == ZZ ---> GF(p) and back via CRA.
       In this case, ``modulus`` is expected to iterate over primes `p`
    2. K == GF(p)[t] --> GF(p) and back via interpolation.
       In this case, ``modulus`` is expected to iterate over linear polynomial in `K`
    3. K == ZZ[t] --> GF(p)[t] and back via CRA.
       In this case, ``modulus`` is expected to iterate over primes `p`. The method
       produces problem instances of type 2, which are handled recursively.     

    """

    if kwargs.has_key('infolevel'):
        infolevel = kwargs['infolevel']
        kwargs['infolevel'] = infolevel - 2
    else:
        infolevel = 0
        
    def info(bound, msg):
        if bound <= infolevel:
            print msg

    R = A.base_ring(); x = R.gen(); K = R.base_ring(); 
    atomic = not ( is_PolynomialRing(K) and K.base_ring() is ZZ )

    info(1, datetime.today().ctime() + ": guessing via homomorphic images started.")
    info(1, "len(data)=" + str(len(data)) + ", algebra=" + str(A._latex_()))

    L = A.zero()
    mod = K.one() if atomic else ZZ.one()
    order_adjustment = None

    nn = 0; path = []; ncpus = 1
    return_short_path = kwargs.has_key('return_short_path') and kwargs['return_short_path'] is True

    while mod != 0:

        nn += 1 # iteration counter

        if nn == 1:
            # 1st iteration: use the path specified by the user (or a default path)
            kwargs['return_short_path'] = True

        elif nn == 2 and atomic and path[0][0] >= Lp.order() + 2:
            # 2nd iteration: try to optimize the path obtained in the 1st iteration 
            r0 = Lp.order(); d0 = Lp.degree(); r1, d1 = path[0]
            # determine the hyperbola through (r0,d0) and (r1,d1) and 
            # choose (r2,d2) as the point on this hyperbola for which (r2+1)*(d2+1) is minimized
            try: 
                r2 = r0 - 1 + math.sqrt(abs((d0-d1)*r0*(r0-1.-r1)/(d0+r0+d1*(r0-1.-r1)-r1)))
                d2 = (d1*(r0-1-r1)*(r0-r2) + d0*(r1-r2))/((r0-r1)*(r0-1-r2))
                r2 = int(math.ceil(r2)); d2 = int(math.ceil(d2))
                if abs(r2 - r1) >= 2 and abs(d2 - d1) >= 2:
                    path = [ (i, d2 + ((d1-d2)*(i-r2))/(r1-r2)) for i in xrange(r2, r1, cmp(r1, r2)) ] + path
                    kwargs['path'] = path
                else:
                    del kwargs['return_short_path']
            except:
                del kwargs['return_short_path']

            if A.is_C():
                kwargs['path'] = [(Lp.order(), Lp.degree())] # there is no curve for algebraic equations

        elif kwargs.has_key('return_short_path'):
            # subsequent iterations: stick to the path we have.                 
            del kwargs['return_short_path']

        if not kwargs.has_key('path'):
            kwargs['return_short_path'] = True

        if ncpus == 1:
            # sequential version 

            imgs = [];
            for i in xrange(max(1, nn - 3)): # do several imgs before proceeding with a reconstruction attempt
                
                data_mod = None
                while data_mod is None:
                    p = modulus.next(); hom = to_hom(p)
                    info(2, "modulus = " + str(p))
                    try:
                        data_mod = map(hom, data)
                    except ArithmeticError:
                        info(2, "unlucky modulus discarded.")

                qq = A.is_Q()
                if not qq:
                    Lp = guess(data_mod, A.change_ring(hom(K.one()).parent()[x]), **kwargs)
                else:
                    qq = hom(qq[1])
                    Lp = guess(data_mod, OreAlgebra(hom(K.one()).parent()[x], (A.var(), {x:qq*x}, {}), q=qq), **kwargs)
                if type(Lp) is tuple and len(Lp) == 2:  ## this implies nn < 3  
                    Lp, path = Lp
                    kwargs['path'] = path

                imgs.append((Lp, p))

            if len(imgs) == 1:
                Lp, p = imgs[0]
            else:
                Lp = A.zero(); p = K.one()
                for (Lpp, pp) in imgs:
                    try:
                        Lp, p = _merge_homomorphic_images(Lp, p, Lpp, pp, reconstruct=False)
                    except:
                        info(2, "unlucky modulus " + str(pp) + " discarded")

        else:
            # we can assume at this point that nn >= 3 and 'return_short_path' is switched off.
            primes = [modulus.next() for i in xrange(ncpus)]
            info(2, "moduli = " + str(primes))
            primes = [ (p, to_hom(p)) for p in primes ]
            primes = [ (p, hom, A.change_ring(hom(K.one()).parent()[x])) for (p, hom) in primes ]
            Lp = A.zero(); p = K.one()
            out = [ (arg[0][0], arg[0][2], Lpp) for (arg, Lpp) in forked_guess(primes) ]
            for (pp, alg, Lpp) in out:
                Lpp = alg(Lpp)
                try:
                    Lp, p = _merge_homomorphic_images(Lp, p, Lpp, pp, reconstruct=False)
                except:
                    info(2, "unlucky modulus " + str(pp) + " discarded")

        if nn == 1:
            info(2, "solution of order " + str(Lp.order()) + " and degree " + str(Lp.degree()) + " predicted")

        elif nn == 2 and kwargs.has_key('ncpus') and kwargs['ncpus'] > 1:
            info(2, "Switching to multiprocessor code.")
            ncpus = kwargs['ncpus']
            del kwargs['ncpus']
            kwargs['infolevel'] = 0
            
            @parallel(ncpus=ncpus)
            def forked_guess(p, hom, alg):
                try:
                    return guess(map(hom, data), alg, **kwargs).polynomial()
                except ArithmeticError:
                    return None
                
        elif nn == 3 and kwargs.has_key('infolevel'):
            kwargs['infolevel'] = kwargs['infolevel'] - 2

        if not Lp.is_zero():
            info(2, "Reconstruction attempt...")
            s = Lp.parent().sigma()
            if not s.is_identity() and mod.parent() is ZZ:
                try:
                    if order_adjustment is None:
                        order_adjustment = Lp.order() // ZZ(2)
                    Lp = Lp.map_coefficients(lambda p: s(p, -order_adjustment))
                except:
                    L = A.zero(); mod = ZZ.zero(); order_adjustment = 0

            L, mod = _merge_homomorphic_images(L, mod, Lp, p)

    if order_adjustment > 0:
        s = L.parent().sigma()
        L = L.map_coefficients(lambda p: s(p, order_adjustment))

    return (L, path) if return_short_path else L

###########################################################################################

def _guess_via_gcrd(data, A, **kwargs):
    """
    Implementation of guessing by taking gcrd of small equations. 

    INPUT:

    - ``data``: list of terms
    - ``A``: an algebra of the form GF(p)[x][X]

    OUTPUT:

    - ``L`` in ``A``, the guessed operator.

    raises an error if no equation is found.
    """

    if kwargs.has_key('infolevel'):
        infolevel = kwargs['infolevel']
        kwargs['infolevel'] = infolevel - 2
    else:
        infolevel = 0
        
    def info(bound, msg):
        if bound <= infolevel:
            print msg

    R = A.base_ring(); x = R.gen(); K = R.base_ring(); 

    info(1, datetime.today().ctime() + ": guessing via gcrd started.")
    info(1, "len(data)=" + str(len(data)) + ", algebra=" + str(A._latex_()))

    if kwargs.has_key('ncpus'):
        del kwargs['ncpus']

    if kwargs.has_key('return_short_path'):
        return_short_path = True
        del kwargs['return_short_path']
    else:
        return_short_path = False
        
    ensure = kwargs['ensure'] if kwargs.has_key('ensure') else 0

    N = len(data) - ensure
    
    if kwargs.has_key('path'):
        path = kwargs['path']; del kwargs['path']
        sort_key = lambda p: (p[0] + 1)*(p[1] + 1)
        prelude = []
    else:
        r2d = lambda r: (N - 2*r - 2)/(r + 1) # python integer division intended.
        path = [(r, r2d(r)) for r in xrange(1, N)] 
        path = filter(lambda p: min(p[0] - 1, p[1]) >= 0, path)
        (r, d) = (1, 1); prelude = []
        while d <= r2d(r):
            prelude.append((r, d))
            (r, d) = (d, r + d)
        path = prelude + path
        sort_key = lambda p: 2*p[0] + (p[0] + 1)*(p[1] + 1) # give some preference to small orders

    max_deg = max_ord = len(data); min_deg = 0; min_ord = 1;

    if kwargs.has_key('degree'):
        max_deg = kwargs['degree']; del kwargs['degree']
    elif kwargs.has_key('max_degree'):
        max_deg = kwargs['max_degree']; del kwargs['max_degree']

    if kwargs.has_key('min_degree'):
        min_deg = kwargs['min_degree']; del kwargs['min_degree']

    if kwargs.has_key('order'):
        max_ord = kwargs['order']; del kwargs['order']
    elif kwargs.has_key('max_order'):
        max_ord = kwargs['max_order']; del kwargs['max_order']

    if kwargs.has_key('min_order'):
        min_ord = kwargs['min_order']; del kwargs['min_order']

    path = filter(lambda p: min_ord <= p[0] and p[0] <= max_ord and min_deg <= p[1] and p[1] <= max_deg, path)

    path.sort(key=sort_key)
    # autoreduce
    for i in xrange(len(prelude), len(path)):
        (r, d) = path[i]
        for j in xrange(len(path)):
            if i != j and path[j] is not None and path[j][0] >= r and path[j][1] >= d:
                path[i] = None                    
    path = filter(lambda p: p is not None, path)

    info(2, "Going through a path with " + str(len(path)) + " points")

    # search equation

    subguesser = guess_hp if A.is_C() else guess_raw
    neg_probes = []
    def probe(r, d):
        if (r, d) in neg_probes:
            return []        
        kwargs['order'], kwargs['degree'] = r, d
        sols = subguesser(data, A, **kwargs)
        info(2, str(len(sols)) + " sols for (r, d)=" + str((r, d)))
        if len(sols) == 0:
            neg_probes.append((r, d))
        return sols

    L = []; short_path = []; 
    
    for i in xrange(len(path)):

        r, d = path[i]
        for (r1, d1) in short_path:
            if r >= r1:
                d = min(d, d1 - 1)

        if d < 0:
            continue

        sols = probe(r, d)
        
        while return_short_path and d > 0 and len(sols) > 1:
            new = probe(r, d - 1)
            if len(new) == 0:
                break
            m = len(sols) - len(new) 
            if m == 0:
                # assuming subsolver returned minimal degrees (as does, e.g., a h/p solver)
                d = max(p.degree() for p in sols)
                break
            d2 = max(int(math.ceil(d - len(sols)*1.0/m)), 0)
            sols = probe(r, d2) if d2 < d - 1 else new
            d = d2
            if len(sols) == 0:
                while len(sols) == 0:
                    d += 1; sols = probe(r, d)
                break

        if len(sols) > 0:
            short_path.append((r, d))
            L = L + sols
        if len(L) >= 2:
            break

    info(2, datetime.today().ctime() + ": search completed.")

    if len(L) == 0:
        raise ValueError, "No relations found."
    elif len(L) == 1:
        L = L[0]
    else:
        L = L[0].gcrd(L[1])
        info(2, datetime.today().ctime() + ": gcrd completed.")

    L = (~L.leading_coefficient().leading_coefficient())*L

    return (L, short_path) if return_short_path else L

###########################################################################################

from sage.ext.multi_modular import MAX_MODULUS
from sage.rings.arith import previous_prime as pp

def _word_size_primes(init=2**23, bound=1000):
    """
    returns an iterator which enumerates the primes smaller than ``init`` and bigger than ``bound``,
    in decreasing order. 
    """
    p = pp(init)
    while p > bound:
        yield p
        p = pp(p)

def _linear_polys(x, init=7, bound=None):
    """
    returns an iterator which enumerates the polynomials x-a for a ranging within the given bounds
    """
    p = x - init; step = -x.parent().one()
    if bound is not None:
        bound = x - bound
    while p != bound:
        yield p; p += step

###########################################################################################

def _merge_homomorphic_images(L, mod, Lp, p, reconstruct=True):
    """
    Interpolation or chinese remaindering on the coefficients of operators.

    INPUT:

    - ``L`` -- an operator in R[x][X]
    - ``mod`` -- an element of R such that there is some hypothetical
      operator in R[x][X] of which ``L`` can be obtained by taking its
      coefficients mod ``mod``.
    - ``Lp`` -- an operator in r[x][X]
    - ``p`` -- an element of R such that the hypothetical operator
      gives `Lp` when its coeffs are reduced mod ``p``.
    - ``reconstruct`` (default: ``True``) -- if set to ``False``, only 
      do Chinese remaindering, but no rational reconstruction.       

    OUTPUT:

    A pair `(M, m)` where

    - `M` is in R[x][X] and obtained from `L` and `Lp`
      by chinese remindering or interpolation, possibly followed by rational
      reconstruction.
    - `m` is either `mod*p` or `0`, depending on whether rational reconstruction
      succeeded.

    If `L` is the zero operator, the method returns ``(Lp, p)``. Otherwise, if
    orders and degrees of `L` and `Lp` don't match, an exception is raised. 

    Possible ground rings:

    - R=ZZ, r=GF(p). The method will apply chinese remaindering on the coefficients. 
    - R=ZZ[q], r=GF(p)[q]. The method will apply chinese remaindering on the coefficients of the coefficients. 
    - R=GF(p)[q], r=GF(p)[q]. The method will apply interpolation on the coefficients.

    """

    B = L.base_ring().base_ring()
    R = mod.parent()
    r = Lp.base_ring().base_ring()
    if r is not R:
        Lp = Lp.change_ring(L.base_ring())

    atomic = (B is ZZ) or (B.characteristic() > 0)
    poly = not atomic     

    if mod == 0:
        return L, R.zero()

    elif L.is_zero():
        Lmod, mod = Lp, R(p)

    elif (L.order(), L.degree()) != (Lp.order(), Lp.degree()):
        raise ValueError

    else:

        p = R(p); mod = R(mod)    
        if poly:
            p = R.base_ring()(p)
            mod = R.base_ring()(mod)

        # cra / interpolation
    
        (_, mod0, p0) = p.xgcd(mod)
        mod0 = R(mod0*p); p0 = R(p0*mod)

        coeffs = []
        
        for i in xrange(L.order() + 1):
            cL = L[i]; cLp = Lp[i]; c = []; coeffs.append(c)
            for j in xrange(max(cL.degree(), cLp.degree()) + 1):
                c.append(mod0*cL[j] + p0*B(cLp[j]))

        Lmod = L.parent()(coeffs)
        mod *= p

    if not reconstruct:
        return Lmod, mod

    # rational reconstruction attempt
    
    if R.characteristic() == 0:
        mod2 = mod // ZZ(2)
        adjust = lambda c : ((c + mod2) % mod) - mod2 
    else:
        if mod.degree() <= 5: # require at least 5 evaluation points
            return Lmod, mod        
        adjust = lambda c : c % mod

    coeffs = Lmod.coeffs()

    try:
        d = R.one()
        for i in xrange(len(coeffs), 0, -1):
            c = coeffs[i - 1]
            for j in xrange(c.degree(), -1, -1):
                if poly:
                    cc = c[j]
                    for l in xrange(cc.degree(), -1, -1): 
                        d *= _rat_recon(d*cc[l], mod)[1]
                else:
                    d *= _rat_recon(d*c[j], mod)[1]
    except (ArithmeticError, ValueError):
        return Lmod, mod # reconstruction failed

    # rat recon succeeded, the common denominator is d. clear it and normalize numerators.

    for i in xrange(len(coeffs)):
        c = d*coeffs[i]
        if adjust is not None:
            if poly:
                c = c.parent()([ cc.map_coefficients(adjust) for cc in c.coeffs() ])
            else:
                c = c.map_coefficients(adjust)
        coeffs[i] = c

    return L.parent()(coeffs), R.zero()

###########################################################################################

def _rat_recon(a, m, u=None):
    """
    if m.parent() is ZZ:

      find (p, q) such that a == p/q mod m and abs(p*q) < m/1000
      if u is not None, require abs(q) <= u.
      raises ArithmeticError if no p/q is found.
      if m < 1000000, we use sage's builtin

    if m.parent() is GF(p)[t]: 
    
      find (p, q) such that a == p/q mod m and deg(p) + deg(q) < deg(m) - 3
      if u is not None, require deg(q) <= deg(u).
      raises ArithmeticError if no p/q is found.
      if deg(m) < 6, we use sage's builtin

    """
    
    K = m.parent() # GF(p)[t] or ZZ
    
    if K is ZZ:
        score_fun = lambda p, q: abs(p*q)
        bound = m // ZZ(10000)
        early_termination_bound = m // ZZ(1000000)
        if u is None:
            u = m
    else:
        score_fun = lambda p, q: p.degree() + q.degree()
        bound = m.degree() - 3
        early_termination_bound = m.degree() - 6
        if u is None:
            u = m.degree()
    
    zero = K.zero(); one = K.one(); mone = -one    
    
    if a in (zero, one, mone):
        return a, one
    elif early_termination_bound <= 0:
        out = a.rational_reconstruct(m)
        return (a.numerator(), a.denominator())

    # p = q*a + r*m for some r
    p = K(a) % m; q = one;   
    pp = m;       qq = zero; 
    out = (p, one); score = score_fun(p, one)
    if K is ZZ:
        mp = m - p; mps = score_fun(mp, one)
        if mps < score:
            out = (mp, -ZZ.one()); score = mps
        if score < early_termination_bound:
            return out

    while True:

        quo = pp // p
        (pp, qq, p, q) = (p, q, pp - quo*p, qq - quo*q)

        if p.is_zero() or score_fun(q, one) > u:
            break

        s = score_fun(p, q)
        if s < score:
            out = (p, q); score = s
            if score < early_termination_bound:
                break

    if score < bound:
        if K is ZZ:
            return out
        else:
            lc = out[1].leading_coefficient()
            return (out[0]/lc, out[1]/lc)
    else:
        raise ArithmeticError

###########################################################################################

