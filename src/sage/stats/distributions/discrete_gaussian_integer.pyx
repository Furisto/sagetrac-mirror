# -*- coding: utf-8 -*-
"""Discrete Gaussian Samplers over the Integers.

This class realizes oracles which returns integers proportionally to
`\exp(-(x-c)^2/(2σ^2))`. All oracles are implemented using rejection
sampling. See :func:`DiscreteGaussianIntegerSampler.__init__` for which algorithms are
available.

AUTHOR: Martin Albrecht <martinralbrecht+dgs@googlemail.com>

EXAMPLE::

    sage: from sage.stats.distributions.discrete_gaussian_integer import DiscreteGaussianIntegerSampler
    sage: sigma = 3.0; n=100000
    sage: D = DiscreteGaussianIntegerSampler(sigma=sigma)
    sage: l = [D() for _ in xrange(n)]
    sage: c = sum([exp(-x^2/(2*sigma^2)) for x in xrange(-6*sigma,sigma*6+1)]); c
    7.519...
    sage: x=0; l.count(x), ZZ(round(n*exp(-x^2/(2*sigma^2))/c))
    (13350, 13298)
    sage: x=4; l.count(x), ZZ(round(n*exp(-x^2/(2*sigma^2))/c))
    (5543, 5467)
    sage: x=-10; l.count(x), ZZ(round(n*exp(-x^2/(2*sigma^2))/c))
    (46, 51)

REFERENCES:

.. [DDLL13] Léo Ducas, Alain Durmus, Tancrède Lepoint and Vadim
   Lyubashevsky. *Lattice Signatures and Bimodal Gaussians*; in Advances in
   Cryptology – CRYPTO 2013; Lecture Notes in Computer Science Volume 8042,
   2013, pp 40-56 http://www.di.ens.fr/~lyubash/papers/bimodal.pdf

"""

include '../../ext/interrupt.pxi' 

from sage.rings.real_mpfr cimport RealNumber, RealField
from sage.libs.mpfr cimport mpfr_set, GMP_RNDN
from sage.rings.integer cimport Integer
from sage.misc.randstate cimport randstate, current_randstate

from dgs cimport dgs_disc_gauss_mp_init, dgs_disc_gauss_mp_clear, dgs_disc_gauss_mp_flush_cache
from dgs cimport dgs_disc_gauss_dp_init, dgs_disc_gauss_dp_clear, dgs_disc_gauss_dp_flush_cache
from dgs cimport DGS_DISC_GAUSS_UNIFORM_TABLE, DGS_DISC_GAUSS_UNIFORM_ONLINE, DGS_DISC_GAUSS_UNIFORM_LOGTABLE, DGS_DISC_GAUSS_SIGMA2_LOGTABLE

cdef class DiscreteGaussianIntegerSampler(SageObject):
    """
    A Discrete Gaussian Sampler using rejection sampling.

    .. automethod:: __init__
    .. automethod:: __call__
    """

    # We use tables for σt ≤ table_cutoff
    table_cutoff = 10**6

    def __init__(self, sigma, c=0, tau=6, algorithm=None, precision="mp"):
        """
        Construct a new sampler for a discrete Gaussian distribution.
        
        INPUT:

        - ``sigma`` - samples `x` are accepted with probability proportional to
          `\exp(-(x-c)^2/(2σ^2))`

        - ``c`` - the mean of the distribution. The value of ``c`` does not have
          to be an integer. However, some algorithms only support integer-valued
          `c` (default: ``0``)
        
        - ``tau`` - samples outside the range `(⌊c⌉-⌈στ⌉,...,⌊c⌉+⌈στ⌉)` are
          considered to have probability zero. This bound applies to algorithms which 
          sample from the uniform distribution (default: ``6``)

        - ``algorithm`` - see list below (default: ``"uniform+table"`` for
           `σt` bounded by ``DiscreteGaussianIntegerSampler.table_cutoff`` and
           ``"uniform+online"`` for bigger `στ`)

        - ``precision`` - either "mp" for multi-precision where the actual
          precision used is taken from sigma or "dp" for double precision. In
          the latter case results are not reproducible across
          plattforms. (default: ``"mp"``)

        ALGORITHMS:

        - ``"uniform+table"`` - classical rejection sampling, sampling from the
          uniform distribution and accepted with probability proportional to
          `\exp(-(x-c)^2/(2σ^2))` where `\exp(-(x-c)^2/(2σ^2))` is precomputed and
          stored in a table. Any real-valued `c` is supported.

        - ``"uniform+logtable"`` - samples are drawn from a uniform distribution and
          accepted with probability proportional to `\exp(-(x-c)^2/(2σ^2))` where
          `\exp(-(x-c)^2/(2σ^2))` is computed using logarithmically many calls to
          Bernoulli distributions. See [DDLL13]_ for details.  Only
          integer-valued `c` are supported.

        - ``"uniform+online"`` - samples are drawn from a uniform distribution and
          accepted with probability proportional to `\exp(-(x-c)^2/(2σ^2))` where
          `\exp(-(x-c)^2/(2σ^2))` is computed in each invocation. Typically this
          is very slow.  See [DDLL13]_ for details.  Any real-valued `c` is
          accepted.

        - ``"sigma2+logtable"`` - samples are drawn from an easily samplable
          distribution with `σ = k·σ_2` with `σ_2 = \sqrt{1/(2\log 2)}` is and accepted
          with probability proportional to `\exp(-(x-c)^2/(2σ^2))` where
          `\exp(-(x-c)^2/(2σ^2))` is computed using  logarithmically many calls to Bernoulli
          distributions (but no calls to `\exp`). See [DDLL13]_ for details. Note that this
          sampler adjusts sigma to match `σ_2·k` for some integer `k`.
          Only integer-valued `c` are supported.

        EXAMPLES::

            sage: from sage.stats.distributions.discrete_gaussian_integer import DiscreteGaussianIntegerSampler
            sage: DiscreteGaussianIntegerSampler(3.0, algorithm="uniform+online")
            Discrete Gaussian sampler over the Integers with sigma = 3.000000 and c = 0
            sage: DiscreteGaussianIntegerSampler(3.0, algorithm="uniform+table")
            Discrete Gaussian sampler over the Integers with sigma = 3.000000 and c = 0
            sage: DiscreteGaussianIntegerSampler(3.0, algorithm="uniform+logtable")
            Discrete Gaussian sampler over the Integers with sigma = 3.000000 and c = 0

        Note that "sigma2+logtable" adjusts sigma::
        
            sage: DiscreteGaussianIntegerSampler(3.0, algorithm="sigma2+logtable")
            Discrete Gaussian sampler over the Integers with sigma = 3.397287 and c = 0

        TESTS:

        We are testing invalid inputs::

            sage: from sage.stats.distributions.discrete_gaussian_integer import DiscreteGaussianIntegerSampler
            sage: DiscreteGaussianIntegerSampler(-3.0)
            Traceback (most recent call last):
            ...
            ValueError: sigma must be > 0.0 but got -3.000000

            sage: DiscreteGaussianIntegerSampler(3.0, tau=-1)
            Traceback (most recent call last):
            ...
            ValueError: tau must be >= 1 but got -1

            sage: DiscreteGaussianIntegerSampler(3.0, tau=2, algorithm="superfastalgorithmyouneverheardof")        
            Traceback (most recent call last):
            ...
            ValueError: Algorithm 'superfastalgorithmyouneverheardof' not supported by class 'DiscreteGaussianIntegerSampler'

            sage: DiscreteGaussianIntegerSampler(3.0, c=1.5, algorithm="sigma2+logtable")
            Traceback (most recent call last):
            ...
            ValueError: algorithm 'uniform+logtable' requires c%1 == 0

        We are testing correctness for mult precision::

            sage: from sage.stats.distributions.discrete_gaussian_integer import DiscreteGaussianIntegerSampler
            sage: D = DiscreteGaussianIntegerSampler(1.0, c=0, tau=2)
            sage: l = [D() for _ in xrange(2^16)]
            sage: min(l) == 0-2*1.0, max(l) == 0+2*1.0, abs(mean(l)) < 0.01
            (True, True, True)

            sage: from sage.stats.distributions.discrete_gaussian_integer import DiscreteGaussianIntegerSampler
            sage: D = DiscreteGaussianIntegerSampler(1.0, c=2.5, tau=2)
            sage: l = [D() for _ in xrange(2^18)]
            sage: min(l)==2-2*1.0, max(l)==2+2*1.0, mean(l).n()
            (True, True, 2.45...)  

            sage: from sage.stats.distributions.discrete_gaussian_integer import DiscreteGaussianIntegerSampler
            sage: D = DiscreteGaussianIntegerSampler(1.0, c=2.5, tau=6)
            sage: l = [D() for _ in xrange(2^18)]
            sage: min(l), max(l), abs(mean(l)-2.5) < 0.01
            (-2, 7, True)

        We are testing correctness for double precision::

            sage: from sage.stats.distributions.discrete_gaussian_integer import DiscreteGaussianIntegerSampler
            sage: D = DiscreteGaussianIntegerSampler(1.0, c=0, tau=2, precision="dp")
            sage: l = [D() for _ in xrange(2^16)]
            sage: min(l) == 0-2*1.0, max(l) == 0+2*1.0, abs(mean(l)) < 0.01
            (True, True, True)

            sage: from sage.stats.distributions.discrete_gaussian_integer import DiscreteGaussianIntegerSampler
            sage: D = DiscreteGaussianIntegerSampler(1.0, c=2.5, tau=2, precision="dp")
            sage: l = [D() for _ in xrange(2^18)]
            sage: min(l)==2-2*1.0, max(l)==2+2*1.0, mean(l).n()
            (True, True, 2.45...)  

            sage: from sage.stats.distributions.discrete_gaussian_integer import DiscreteGaussianIntegerSampler
            sage: D = DiscreteGaussianIntegerSampler(1.0, c=2.5, tau=6, precision="dp")
            sage: l = [D() for _ in xrange(2^18)]
            sage: min(l), max(l), abs(mean(l)-2.5) < 0.01
            (-2, 7, True)

        We plot a histogram::

            sage: from sage.stats.distributions.discrete_gaussian_integer import DiscreteGaussianIntegerSampler
            sage: D = DiscreteGaussianIntegerSampler(17.0)
            sage: S = [D() for _ in range(2^16)]
            sage: list_plot([(v,S.count(v)) for v in set(S)])

        These generators cache random bits for performance reasons. Hence, resetting
        the seed of the PRNG might not have the expected outcome. You can flush this cache with
        ``DiscreteGaussianIntegerSampler.flush_cache``::

            sage: from sage.stats.distributions.discrete_gaussian_integer import DiscreteGaussianIntegerSampler
            sage: D = DiscreteGaussianIntegerSampler(3.0)
            sage: sage.misc.randstate.set_random_seed(0); D()
            3
            sage: sage.misc.randstate.set_random_seed(0); D()
            3
            sage: sage.misc.randstate.set_random_seed(0); D._flush_cache(); D()
            3

            sage: D = DiscreteGaussianIntegerSampler(3.0)
            sage: sage.misc.randstate.set_random_seed(0); D()
            3
            sage: sage.misc.randstate.set_random_seed(0); D()
            3
            sage: sage.misc.randstate.set_random_seed(0); D()
            -3        
        """

        if sigma <= 0.0:
            raise ValueError("sigma must be > 0.0 but got %f"%sigma)

        if tau < 1:
            raise ValueError("tau must be >= 1 but got %d"%tau)

            
        if algorithm is None:
            if sigma*tau <= DiscreteGaussianIntegerSampler.table_cutoff:
                algorithm = "uniform+table"
            else:
                algorithm = "uniform+online"

        algorithm_str = algorithm
                
        if algorithm == "uniform+table":
            algorithm = DGS_DISC_GAUSS_UNIFORM_TABLE
        elif algorithm == "uniform+online":
            algorithm = DGS_DISC_GAUSS_UNIFORM_ONLINE
        elif algorithm == "uniform+logtable":
            if (c%1):
                raise ValueError("algorithm 'uniform+logtable' requires c%1 == 0")
            algorithm = DGS_DISC_GAUSS_UNIFORM_LOGTABLE
        elif algorithm == "sigma2+logtable":
            if (c%1):
                raise ValueError("algorithm 'uniform+logtable' requires c%1 == 0")
            algorithm = DGS_DISC_GAUSS_SIGMA2_LOGTABLE
        else:
            raise ValueError("Algorithm '%s' not supported by class 'DiscreteGaussianIntegerSampler'"%(algorithm))

        if precision == "mp":
            if not isinstance(sigma, RealNumber):
                RR = RealField()
                sigma = RR(sigma)

            if not isinstance(c, RealNumber):
                c = sigma.parent()(c)
            sig_on()
            self._gen_mp = dgs_disc_gauss_mp_init((<RealNumber>sigma).value, (<RealNumber>c).value, tau, algorithm)
            sig_off()
            self._gen_dp = NULL
            self.sigma = sigma.parent()(0)
            mpfr_set(self.sigma.value, self._gen_mp.sigma, GMP_RNDN)
            self.c = c
        elif precision == "dp":
            RR = RealField()
            if not isinstance(sigma, RealNumber):
                sigma = RR(sigma)
            sig_on()
            self._gen_dp = dgs_disc_gauss_dp_init(sigma, c, tau, algorithm)
            sig_off()
            self._gen_mp = NULL
            self.sigma = RR(sigma)
            self.c = RR(c)
        else:
            raise ValueError("Parameter precision '%s' not supported."%precision)
            
        self.tau = Integer(tau)
        self.algorithm = algorithm_str

    def _flush_cache(self):
        """
        Flush the internal cache of random bits.

        EXAMPLE::
          
            sage: from sage.stats.distributions.discrete_gaussian_integer import DiscreteGaussianIntegerSampler

            sage: f = lambda: sage.misc.randstate.set_random_seed(0)

            sage: f()
            sage: D = DiscreteGaussianIntegerSampler(30.0)
            sage: for i in range(16):
            ...      print D(),
            ...
            21 23 37 6 -64 29 8 -22 -3 -10 7 -43 1 -29 25 38
            
            sage: f()
            sage: D = DiscreteGaussianIntegerSampler(30.0)
            sage: for i in range(16):
            ...      f(); print D(),
            ...
            21 21 21 21 -21 21 21 -21 -21 -21 21 -21 21 -21 21 21
            
            sage: f()
            sage: D = DiscreteGaussianIntegerSampler(30.0)
            sage: for i in range(16):
            ...      f(); D._flush_cache(); print D(),
            ...
            21 21 21 21 21 21 21 21 21 21 21 21 21 21 21 21
        """
        if self._gen_mp:
            dgs_disc_gauss_mp_flush_cache(self._gen_mp)
        if self._gen_dp:
            dgs_disc_gauss_dp_flush_cache(self._gen_dp)
        
    def __dealloc__(self):
        """
        TESTS::

            sage: from sage.stats.distributions.discrete_gaussian_integer import DiscreteGaussianIntegerSampler
            sage: D = DiscreteGaussianIntegerSampler(3.0, algorithm="uniform+online")
            sage: del D
        """
        if self._gen_mp:
            dgs_disc_gauss_mp_clear(self._gen_mp)
        if self._gen_dp:
            dgs_disc_gauss_dp_clear(self._gen_dp)

    def __call__(self):
        """
        Return a new sample.

        EXAMPLES::

            sage: from sage.stats.distributions.discrete_gaussian_integer import DiscreteGaussianIntegerSampler
            sage: DiscreteGaussianIntegerSampler(3.0, algorithm="uniform+online")()
            -3
            sage: DiscreteGaussianIntegerSampler(3.0, algorithm="uniform+table")()
            3

        TESTS::

            sage: from sage.stats.distributions.discrete_gaussian_integer import DiscreteGaussianIntegerSampler
            sage: DiscreteGaussianIntegerSampler(3.0, algorithm="uniform+logtable", precision="dp")() # random output
            13
        """
        cdef randstate rstate
        cdef Integer rop
        if self._gen_mp:
            rstate = current_randstate()
            rop = Integer()
            self._gen_mp.call(rop.value, self._gen_mp, rstate.gmp_state)
            return rop
        else:
            r = self._gen_dp.call(self._gen_dp)
            return Integer(r)
            

    def _repr_(self):
        """
        TESTS::
        
            sage: from sage.stats.distributions.discrete_gaussian_integer import DiscreteGaussianIntegerSampler
            sage: repr(DiscreteGaussianIntegerSampler(3.0, 2))
            'Discrete Gaussian sampler over the Integers with sigma = 3.000000 and c = 2'
        """
        return "Discrete Gaussian sampler over the Integers with sigma = %f and c = %d"%(self.sigma, self.c)
