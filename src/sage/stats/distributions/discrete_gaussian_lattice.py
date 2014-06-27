# -*- coding: utf-8 -*-
r"""
Discrete Gaussian Samplers over Lattices.

This file implements oracles which return samples from a lattice
following a discrete Gaussian distribution. That is, if `σ` is big
enough relative to the provided basis, then vectors are returned with
a probability proportional to `\exp(-|x-c|_2^2/(2σ^2))`. More precisely lattice vectors in `x ∈ Λ`
are returned with probability:

    `\exp(-|x-c|_2^2/(2σ²))/(∑_{x ∈ Λ} \exp(-|x|_2^2/(2σ²)))`

AUTHOR: Martin Albrecht <martinralbrecht+dgs@googlemail.com>

EXAMPLES::

  sage: from sage.stats.distributions.discrete_gaussian_lattice import DiscreteGaussianLatticeSampler
  sage: D = DiscreteGaussianLatticeSampler(ZZ^10, 3.0)
  sage: D(), D(), D()
  ((3, 0, 5, 0, 1, 3, 3, 2, -4, 7), (0, 1, 2, -4, 4, -4, 0, -1, -4, 3), (0, -4, -5, 0, 1, -3, 2, 0, 1, -2))
"""

from sage.functions.log import exp
from sage.functions.other import ceil
from sage.rings.all import RealField, RR, ZZ, QQ
from discrete_gaussian_integer import DiscreteGaussianIntegerSampler
from sage.structure.sage_object import SageObject
from sage.matrix.constructor import matrix, identity_matrix
from sage.modules.free_module import FreeModule
from sage.modules.free_module_element import vector

def _iter_vectors(n, lower, upper, step=None):
    """
    Iterate over all integer vectors of length `n` between `lower` and `upper` bound.

    INPUT:

    - ``n`` - length, integer `>0`,
    - ``lower`` - lower bound (inclusive), integer ``< upper``.
    - ``upper`` - upper bound (exclusive), integer ``> lower``.
    - ``step`` - used for recursion, ignore.

    EXAMPLE::

      sage: from sage.stats.distributions.discrete_gaussian_lattice import _iter_vectors
      sage: list(_iter_vectors(2, -1, 2))
      [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    """
    if step is None:
        if ZZ(lower) >= ZZ(upper):
            raise ValueError("Expected lower < uppper, but got %d >= %d"%(lower, upper))
        if ZZ(n) <= 0:
            raise ValueError("Expected n>0 but got %d <= 0"%(n))
        step = n

    if step <= 0:
        raise RuntimeError("We reached an impossible state.")
    elif step == 1:
        for x in xrange(lower, upper):
            v = vector(ZZ, n)
            v[0] = x
            yield v
        return
    else:
        for x in range(lower, upper):
            for v in _iter_vectors(n, lower, upper, step-1):
                v[n-1] = x
                yield v

class DiscreteGaussianLatticeSampler(SageObject):
    """
    GPV sampler for Discrete Gaussians over Lattices.

    EXAMPLE::

        sage: from sage.stats.distributions.discrete_gaussian_lattice import DiscreteGaussianLatticeSampler
        sage: D = DiscreteGaussianLatticeSampler(ZZ^10, 3.0); D
        Discrete Gaussian sampler with σ = 3.000000, c=(0, 0, 0, 0, 0, 0, 0, 0, 0, 0) over lattice with basis
        <BLANKLINE>
        [1 0 0 0 0 0 0 0 0 0]
        [0 1 0 0 0 0 0 0 0 0]
        [0 0 1 0 0 0 0 0 0 0]
        [0 0 0 1 0 0 0 0 0 0]
        [0 0 0 0 1 0 0 0 0 0]
        [0 0 0 0 0 1 0 0 0 0]
        [0 0 0 0 0 0 1 0 0 0]
        [0 0 0 0 0 0 0 1 0 0]
        [0 0 0 0 0 0 0 0 1 0]
        [0 0 0 0 0 0 0 0 0 1]
          
    REFERENCES:

    .. [GPV08] Craig Gentry, Chris Peikert, Vinod Vaikuntanathan. *How to Use a
               Short Basis: Trapdoors for Hard Lattices and New Cryptographic
               Constructions*. STOC 2008. http://www.cc.gatech.edu/~cpeikert/pubs/trap_lattice.pdf

    .. automethod:: __init__
    .. automethod:: __call__
    """

    @staticmethod
    def compute_precision(precision, sigma):
        """
        Compute precision to use.

        INPUT:

        - ``precision`` - an integer `> 53` nor ``None``.
        - ``sigma`` - if ``precision=None`` then sigma's precision is used.

        EXAMPLE::

            sage: from sage.stats.distributions.discrete_gaussian_lattice import DiscreteGaussianLatticeSampler
            sage: DiscreteGaussianLatticeSampler.compute_precision(100, RR(3))
            100
            sage: DiscreteGaussianLatticeSampler.compute_precision(100, RealField(200)(3))
            100
            sage: DiscreteGaussianLatticeSampler.compute_precision(100, 3)
            100
            sage: DiscreteGaussianLatticeSampler.compute_precision(None, RR(3))
            53
            sage: DiscreteGaussianLatticeSampler.compute_precision(None, RealField(200)(3))
            200
            sage: DiscreteGaussianLatticeSampler.compute_precision(None, 3)
            53
          
        """
        if precision is None:
            try:
                precision = ZZ(sigma.precision())
            except AttributeError:
                pass
        precision = max(53, precision)
        return precision

    def _normalisation_factor_zz(self, tau=3):
        """
        This function returns an approximation of `∑_{x ∈ \\ZZ^n} \exp(-|x|_2^2/(2σ²))`,
        i.e. the normalisation factor such that the sum over all probabilities is 1 for `\\ZZⁿ`.

        If this `B` is not an identity matrix over `\\ZZ` a ``NotImplementedError`` is raise.

        INPUT:

        - ``tau`` -- all vectors `v` with `|v|_∞ ≤ τ·σ` are enumerated (default: ``3``).

        EXAMPLE::

            sage: from sage.stats.distributions.discrete_gaussian_lattice import DiscreteGaussianLatticeSampler
            sage: n = 3; sigma = 1.0; m = 1000
            sage: D = DiscreteGaussianLatticeSampler(ZZ^n, sigma)
            sage: f = D.f
            sage: c = D._normalisation_factor_zz(); c
            37.34...

            sage: l = [D() for _ in xrange(m)]
            sage: v = vector(ZZ, n, (0, 0, 0))
            sage: l.count(v), ZZ(round(m*f(v)/c))
            (53, 27)
        
        """
        if self.B != identity_matrix(ZZ, self.B.nrows()):
            raise NotImplementedError("This function is only implemented when B is an identity matrix.")

        f = self.f
        n = self.B.ncols()
        sigma = self._sigma
        return sum(f(x) for x in _iter_vectors(n, -ceil(tau*sigma), ceil(tau*sigma)))

    def __init__(self, B, sigma=1, c=None, precision=None):
        """
        Construct a discrete Gaussian sampler over the lattice `Λ(B)`
        with parameter `σ` and center `c`.

        INPUT:

        - ``B`` -- a basis for the lattice, one of the following:

          - an integer matrix,
          - an object with a ``matrix()`` method, e.g. ``ZZ^n``, or
          - an object where ``matrix(B)`` succeeds, e.g. a list of vectors.

        - ``sigma`` -- Gaussian parameter `σ>0`.
        - ``c`` -- center `c`, any vector in `\\ZZ^n` is supported, but `c ∈ Λ(B)` is faster.
        - ``precision`` -- bit precision `≥ 53`.

        EXAMPLE::

            sage: from sage.stats.distributions.discrete_gaussian_lattice import DiscreteGaussianLatticeSampler
            sage: n = 2; sigma = 3.0; m = 5000
            sage: D = DiscreteGaussianLatticeSampler(ZZ^n, sigma)
            sage: f = D.f
            sage: c = D._normalisation_factor_zz(); c
            56.2162803067524

            sage: l = [D() for _ in xrange(m)]
            sage: v = vector(ZZ, n, (-3,-3))
            sage: l.count(v), ZZ(round(m*f(v)/c))
            (30, 33)

            sage: target = vector(ZZ, n, (0,0))
            sage: l.count(target), ZZ(round(m*f(target)/c))
            (93, 89)

            sage: from sage.stats.distributions.discrete_gaussian_lattice import DiscreteGaussianLatticeSampler
            sage: qf = QuadraticForm(matrix(3, [2, 1, 1,  1, 2, 1,  1, 1, 2]))
            sage: D = DiscreteGaussianLatticeSampler(qf, 3.0); D
            Discrete Gaussian sampler with σ = 3.000000, c=(0, 0, 0) over lattice with basis
            <BLANKLINE>
            [2 1 1]
            [1 2 1]
            [1 1 2]
            sage: D()
            (-4, -2, -6)           
        """
        precision = DiscreteGaussianLatticeSampler.compute_precision(precision, sigma)

        self._RR = RealField(precision)
        self._sigma = self._RR(sigma)

        try:
            B = matrix(B)
        except ValueError:
            pass

        try:
            B = B.matrix()
        except AttributeError:
            pass

        self.B = B
        self.G = B.gram_schmidt()[0]

        try:
            c = vector(ZZ, B.ncols(), c)
        except TypeError:
            try:
                c = vector(QQ, B.ncols(), c)
            except TypeError:
                c = vector(RR, B.ncols(), c)

        self._c = c

        self.f = lambda x: exp(-(vector(ZZ, B.ncols(), x)-c).norm()**2/(2*self._sigma**2))

        w = B.solve_left(c)
        if w in ZZ**B.nrows():
            self._c_in_lattice = True
            D = []
            for i in range(self.B.nrows()):
                sigma_ = self._sigma/self.G[i].norm()
                D.append( DiscreteGaussianIntegerSampler(sigma=sigma_) )
            self.D = tuple(D)
            self.VS = FreeModule(ZZ, B.nrows())
        else:
            self._c_in_lattice = False

    def __call__(self):
        """
        Return a new sample.

        EXAMPLE::

            sage: from sage.stats.distributions.discrete_gaussian_lattice import DiscreteGaussianLatticeSampler
            sage: D = DiscreteGaussianLatticeSampler(ZZ^3, 3.0, c=(1,0,0))
            sage: L = [D() for _ in range(2^12)]
            sage: abs(mean(L).n() - D.c)
            0.10...
            
            sage: D = DiscreteGaussianLatticeSampler(ZZ^3, 3.0, c=(1/2,0,0))
            sage: L = [D() for _ in range(2^12)]
            sage: mean(L).n() - D.c
            (0.058..., -0.13..., 0.02...)

        """
        if self._c_in_lattice:
            return self._call_in_lattice()
        else:
            return self._call()
    @property
    def sigma(self):
        """Gaussian parameter `σ`.

        Samples from this sampler will have expected norm `\sqrt{n}σ` where `n`
        is the dimension of the lattice.

        EXAMPLE::

            sage: from sage.stats.distributions.discrete_gaussian_lattice import DiscreteGaussianLatticeSampler
            sage: D = DiscreteGaussianLatticeSampler(ZZ^3, 3.0, c=(1,0,0))
            sage: D.sigma
            3.00000000000000

        """
        return self._sigma
    @property
    def c(self):
        """Center `c`.

        Samples from this sampler will be centered at `c`.

        EXAMPLE::

            sage: from sage.stats.distributions.discrete_gaussian_lattice import DiscreteGaussianLatticeSampler
            sage: D = DiscreteGaussianLatticeSampler(ZZ^3, 3.0, c=(1,0,0)); D
            Discrete Gaussian sampler with σ = 3.000000, c=(1, 0, 0) over lattice with basis
            <BLANKLINE>
            [1 0 0]
            [0 1 0]
            [0 0 1]

            sage: D.c
            (1, 0, 0)
        """
        return self._c
            
    def __repr__(self):
        """
        EXAMPLE::

            sage: from sage.stats.distributions.discrete_gaussian_lattice import DiscreteGaussianLatticeSampler
            sage: D = DiscreteGaussianLatticeSampler(ZZ^3, 3.0, c=(1,0,0)); D
            Discrete Gaussian sampler with σ = 3.000000, c=(1, 0, 0) over lattice with basis
            <BLANKLINE>
            [1 0 0]
            [0 1 0]
            [0 0 1]

        """
        return "Discrete Gaussian sampler with σ = %f, c=%s over lattice with basis\n\n%s"%(self._sigma, self._c, self.B)
            
    def _call_in_lattice(self):
        """
        Return a new sample assuming `c ∈ Λ(B)`.

        EXAMPLE::

            sage: from sage.stats.distributions.discrete_gaussian_lattice import DiscreteGaussianLatticeSampler
            sage: D = DiscreteGaussianLatticeSampler(ZZ^3, 3.0, c=(1,0,0))
            sage: L = [D._call_in_lattice() for _ in range(2^12)]
            sage: abs(mean(L).n() - D.c)
            0.10...

        .. note::

           Do not call this method directly, call :func:`DiscreteGaussianLatticeSampler.__call__` instead.
        """
        w = self.VS([d() for d in self.D], check=False)
        return w*self.B + self._c

    def _call(self):
        """
        Return a new sample.

        EXAMPLE::

            sage: from sage.stats.distributions.discrete_gaussian_lattice import DiscreteGaussianLatticeSampler
            sage: D = DiscreteGaussianLatticeSampler(ZZ^3, 3.0, c=(1/2,0,0))
            sage: L = [D._call() for _ in range(2^12)]
            sage: mean(L).n() - D.c
            (-0.049..., -0.034..., -0.026...)

        .. note::

           Do not call this method directly, call :func:`DiscreteGaussianLatticeSampler.__call__` instead.
        """
        v = 0
        c, sigma, B = self._c, self._sigma, self.B

        m = self.B.nrows()

        for i in range(m)[::-1]:
            b_ = self.G[i]
            c_ = c.dot_product(b_) / b_.dot_product(b_)
            sigma_ = sigma/b_.norm()
            assert(sigma_ > 0)
            z = DiscreteGaussianIntegerSampler(sigma=sigma_, c=c_, algorithm="uniform+online")()
            c = c - z*B[i]
            v = v + z*B[i]
        return v