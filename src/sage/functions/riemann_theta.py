r"""
Riemann Theta Functions

This module implements the algorithms for computing Riemann theta functions
and their derivatives featured in the paper *"Computing Riemann Theta
Functions"* by Deconinck, Heil, Bobenko, van Hoeij, and Schmies [CRTF]_.


**DEFINITION OF THE RIEMANN THETA FUNCTION:**


Let `g` be a positive integer, the *genus* of the Riemann theta
function.  Let `H_g` denote the Siegel upper half space of dimension
`g(g+1)/2` over `\CC` , that is the space of symmetric complex matrices whose
imaginary parts are positive definite.  When `g = 1`, this is just the complex
upper half plane.

The Riemann theta function `\theta : \CC^g \times H_g \to \CC`
is defined by the infinite series

.. math::

    \theta( z | \Omega ) = \sum_{ n \in \ZZ^g } e^{ 2 \pi i \left( \tfrac{1}{2} n \cdot \Omega n + n \cdot z \right) }

It is holomorphic in both `z` and `\Omega`. It is quasiperiodic in `z` with
respect to the lattice `\{ M + \Omega N | M,N \in \ZZ^g \}`, meaning that
`\theta(z|\Omega)` is periodic upon translation of `z` by vectors in `\ZZ^g`
and periodic up to a multiplicative exponential factor upon translation of `z`
by vectors in `\Omega \ZZ^g`. As a consequence, `\theta(z | \Omega)` has
exponential growth in the imaginary parts of `z`.

When `g=1`, the Riemann theta function is the third Jacobi theta function.

.. math::

    \theta( z | \Omega) = \theta_3(\pi z | \Omega) = 1 + 2 \sum_{n=1}^\infty e^{i \pi \Omega n^2} \cos(2 \pi n z)

Riemann theta functions are the fundamental building blocks for Abelian
functions, which generalize the classical elliptic functions to multiple
variables. Like elliptic functions, Abelian functions and consequently
Riemann theta functions arise in many applications such as integrable
partial differential equations, algebraic geometry, and optimization.

For more information about the basic facts of and definitions associated with
Riemann theta funtions, see the Digital Library of Mathematics Functions
``http://dlmf.nist.gov/21``.


**ALGORITHM:**


The algorithm in [CRTF]_ is based on the observation that the exponential
growth of `\theta` can be factored out of the sum. Thus, we only need to
find an approximation for the oscillatory part. The derivation is
omitted here but the key observation is to write `z = x + i y` and
`\Omega = X + i Y` where `x`, `y`, `X`, and `Y` are real vectors and matrices.
With the exponential growth part factored out of the sum, the goal is to find
the integral points `n \in \ZZ^g` such that the sum over these points is
within `O(\epsilon)` accuracy of the infinite sum, for a given `z \in \CC^g`
and numerical accuracy `\epsilon`.

By default we use the uniform approximation formulas which use the same integral points for all `z` for a fixed `\Omega`. This can be
changed by setting ``uniform=False``. This is ill-advised if you need
to compute the Riemann theta function for a fixed `\Omega` for many different `z`.


**EXAMPLES:**


We start by creating a genus 2 Riemann theta function from a Riemann matrix::

    sage: R = ComplexField(20); I = R.gen()
    sage: Omega = matrix(R,2,2,[I,-1/2,-1/2,I])
    sage: theta = RiemannTheta(Omega)
    sage: theta
    Riemann theta function with defining Riemann matrix
    [1.0000*I -0.50000]
    [-0.50000 1.0000*I]
    over the base ring Complex Field with 20 bits of precision

Since ``Omega`` above is defined over the complex field with 20 bits of
precision, ``RiemannTheta`` can be evaluated at any point in `\CC^2` with
the same precision. (These values are checked against the Maple
implementation of Riemann theta written by Bernard Deconinck and Mark van
Hoeij; two of the authors of [CRTF]_.)::

    sage: theta([0,0])
    1.1654 - 1.9522e-15*I
    sage: theta([I,I])
    -438.94 + 0.00056160*I

One can also compute the exponential and oscillatory parts of the Riemann
theta function separately::

    sage: u,v = theta.exp_and_osc_at_point([I,I])
    sage: (u,v)
    (6.2832, -0.81969 + 1.0488e-6*I)
    sage: e^u*v
    -438.94 + 0.00056160*I

Directional derivatives of theta can also be computed. The directional
derivative can be specified in the construction of the Riemann theta function
or as input to evaluation::

    sage: theta10 = RiemannTheta(Omega, deriv=[[1,0]])
    sage: z = [I,I]
    sage: theta10(z)
    0.0031244 + 2757.9*I
    sage: theta = RiemannTheta(Omega)
    sage: theta(z,[[1,0]])
    0.0031244 + 2757.9*I

Symbolic evaluation and differentiation work::

    sage: f = theta([x^2,pi*sin(x)]); f
    theta(x^2, pi*sin(x))
    sage: fx = f.derivative(x,1); fx
    pi*cos(x)*theta_01(x^2, pi*sin(x)) + 2*x*theta_10(x^2, pi*sin(x))
    sage: w = fx(x=I); w
    -(1.0631e7 + 1.4805e20*I)*pi - 6.2625e11 - 7.0256e12*I
    sage: CC(w)
    -6.26279686008491e11 - 4.65101957990761e20*I

It is important to note that the absolute value of the "oscillatory" part
of the Riemann theta function grows polynomially with degree equal to the
number of derivatives taken. (e.g. the absolute value of the oscillatory part
of the first directional derivative of the function grows linearly) Therefore,
a radius of accuracy (Default: 5) must be specified to ensure that the value
of the derivative(s) of the Riemann theta function for `z` in a sphere of this
radius in `\ZZ^g` are accurate to within the desired numerical accuracy
specified by the base field of the Riemann matrix.

This radius of accuracy for values of the derivatives of the Riemann theta
function can be adjusted::

    sage: theta01 = RiemannTheta(Omega, deriv=[[0,1]], deriv_accuracy_radius=2)
    sage: theta01([0.3,0.4*I])   # guaranteed accurate to 20 bits
    2.6608e-8 - 3.4254*I
    sage: z = [1.7+2.3*I,3.9+1.7*I]
    sage: theta01(z)             # not guaranteed accurate to 20 bits
    -9.5887e11 - 4.7112e11*I

TESTS::

    sage: loads(dumps(RiemannTheta)) == RiemannTheta
    True

REFERENCES:

.. [CRTF] Computing Riemann Theta Functions. Bernard Deconinck, Matthias
  Heil, Alexander Bobenko, Mark van Hoeij and Markus Schmies.  Mathematics
  of Computation 73 (2004) 1417-1442.  The paper is available at
  http://www.amath.washington.edu/~bernard/papers/pdfs/computingtheta.pdf.
  Accompanying Maple code is available at
  http://www.math.fsu.edu/~hoeij/RiemannTheta/

.. :wikipedia:`Theta_function`

.. http://mathworld.wolfram.com/JacobiThetaFunctions.html

.. Digital Library of Mathematics Functions - Riemann Theta Functions ( http://dlmf.nist.gov/21 ).

AUTHORS:

- Nick Alexander (2009-03): initial version
- Chris Swierczewski (2011-11): major overhaul to match notation of [CRTF]_, numerous bug fixes, documentation, doctests, symbolic evaluation
"""
#*****************************************************************************
#       Copyright (C) 2011 Chris Swierczewski <cswiercz@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#*****************************************************************************
from sage.calculus.var import SR, var
from sage.ext.fast_callable import fast_callable
from sage.modules.free_module_element import vector
from sage.misc.misc_c import prod
from sage.plot.all import implicit_plot
from sage.rings.all import RDF, RealField, ZZ, PolynomialRing
from sage.symbolic.function import BuiltinFunction
from sage.symbolic.expression import is_Expression
from scipy.optimize import fsolve
from scipy.special import gamma, gammaincc, gammainccinv


def RiemannTheta_Constructor(Omega, deriv=[], uniform=True,
                             deriv_accuracy_radius=5):
    r"""
    Create an instance of the Riemann theta function parameterized by a
    Riemann matrix ``Omega``, directional derivative ``derivs``, and
    derivative evaluation accuracy radius. See module level documentation
    for more information about the Riemann theta function.

    The Riemann theta function `\theta : \CC^g \times H_g \to \CC` is defined
    by the infinite series

    .. math::

        \theta( z | \Omega ) = \sum_{ n \in \ZZ^g } e^{ 2 \pi i \left( \tfrac{1}{2} \langle \Omega n, n \rangle +  \langle z, n \rangle \right) }


    The precision of Riemann theta function evaluation is determined by
    the precision of the base ring.

    As shown in [CRTF]_, `n` th order derivatives introduce polynomial
    growth in the oscillatory part of the Riemann theta approximations
    thus making a global approximation formula impossible. Therefore,
    one must specify a ``deriv_accuracy_radius`` of guaranteed
    accuracy when computing derivatives of `\theta(z | \Omega)`.

    INPUT:

    - ``Omega`` -- a Riemann matrix (symmetric with positive definite
      imaginary part)

    - ``deriv`` -- (default: ``[]``) a list of `g`-tuples representing
      a directional derivative of `\theta`. A list of `n` lists
      represents an `n`th order derivative.

    - ``uniform`` -- (default: ``True``) a unform approximation allows
      the accurate computation of the Riemann theta function without
      having to recompute the integer points over which to take the
      finite sum. See [CRTF] for a more in-depth definition.

    - ``deriv_accuracy_radius`` -- (default: 5) the guaranteed radius
      of accuracy in computing derivatives of theta. This parameter is
      necessary due to the polynomial growth of the non-doubly
      exponential part of theta

    OUTPUT:

    - ``Function_RiemannTheta`` -- a Riemann theta function
      parameterized by the Riemann matrix `\Omega`, derivatives
      ``deriv``, whether or not to use a uniform approximation, and
      derivative accuracy radius ``deriv_accuracy_radius``.

    .. NOTE::

        For now, only second order derivatives are
        implemented. Approximation formulas are derived in [CRTF]_. It
        is not exactly clear how to generalize these formulas. In most
        applications, second order derivatives are suficient.

    EXAMPLES:

    We start by creating a genus 2 Riemann theta function from a
    Riemann matrix.::

        sage: R = ComplexField(20)
        sgae: I = R.gen()
        sage: Omega = matrix(R,2,2,[I,-1/2,-1/2,I])
        sage: theta = RiemannTheta(Omega)
        sage: theta
        Riemann theta function with defining Riemann matrix
        [1.0000*I -0.50000]
        [-0.50000 1.0000*I]
        over the base ring Complex Field with 20 bits of precision

    Since ``Omega`` above is defined over the complex field with 20
    bits of precision, ``RiemannTheta`` can be evaluated at any point
    in `\CC^2` with the same precision. (These values are checked
    against the Maple implementation of Riemann theta written by
    Bernard Deconinck and Mark van Hoeij; two of the authors of
    [CRTF]_.)::

        sage: theta([0,0])
        1.1654 - 1.9522e-15*I
        sage: theta([I,I])
        -438.94 + 0.00056160*I

    One can also compute the exponential and oscillatory parts of the Riemann
    theta function separately::

        sage: u,v = theta.exp_and_osc_at_point([I,I])
        sage: (u,v)
        (6.2832, -0.81969 + 1.0488e-6*I)
        sage: e^u*v
        -438.94 + 0.00056160*I

    Directional derivatives of theta can also be computed. The directional
    derivative can be specified in the construction of the Riemann theta
    function or as input to evaluation.::

        sage: theta10 = RiemannTheta(Omega, deriv=[[1,0]])
        sage: z = [I,I]
        sage: theta10(z)
        0.0031244 + 2757.9*I
        sage: theta = RiemannTheta(Omega)
        sage: theta(z,[[1,0]])
        0.0031244 + 2757.9*I

    Symbolic evaluation and differentiation works::

        sage: f = theta([x^2,pi*sin(x)]); f
        theta(x^2, pi*sin(x))
        sage: fx = f.derivative(x,1); fx
        pi*cos(x)*theta_01(x^2, pi*sin(x)) + 2*x*theta_10(x^2, pi*sin(x))
        sage: w = fx(x=I); w
        -(1.0631e7 + 1.4805e20*I)*pi - 6.2625e11 - 7.0256e12*I
        sage: CC(w)
        -6.26279686008491e11 - 4.65101957990761e20*I

    It it important to note that the "oscillatory" part of Riemann
    theta grows polynomially in absolute value where the degree of the
    polynomial is equal to the degree of the directional
    derivative. (e.g.  the oscillatory part of the first directional
    derivative of theta grows linearly in absolute value.) A radius of
    accuracy must therefore be specified to ensure that the value of
    the derivative(s) of the Riemann theta function are
    accurate. (Default: 5) This is the radius of the complex
    `g`-sphere where accuracy of the directional derivative of Riemann
    theta is guaranteed to be within the desired numerical accuracy
    specified by the base field of the Riemann matrix.

    This radius of accuracy for the derivatives of the Riemann theta function
    can be adjusted::

        sage: theta01 = RiemannTheta(Omega, deriv=[[0,1]], deriv_accuracy_radius=2)
        sage: theta01([0.3,0.4*I])   # guaranteed accurate to 20 bits
        2.6608e-8 - 3.4254*I
        sage: z = [1.7+2.3*I,3.9+1.7*I]
        sage: theta10(z)             # not guaranteed accurate to 20 bits
        -1.0103e12 - 4.6132e11*I

    TESTS:

        sage: sage.functions.riemann_theta.RiemannTheta_Constructor == RiemannTheta
        True
    """
    # set __repr__ formatting
    if not deriv:
        name = "theta"
        latex_name = r"\theta"
    else:
        s = ""
        for d in deriv:
            for i in d:
                s += str(i)
            s += ","
        name = "theta_" + s[:-1]
        latex_name = r"\theta_{" + s[:-1] + "}"
        nargs = ZZ(Omega.nrows())

    nargs = ZZ(Omega.nrows())
    conversions = {}

    # construct and return instance of Riemann theta with input arguments
    class RiemannTheta(Function_RiemannTheta):
        r"""
        An instance of the Riemann theta function parameterized by a
        Riemann matrix ``Omega``, directional derivative ``derivs``, and
        derivative evaluation accuracy radius. See module level documentation
        for more information about the Riemann theta function.

        The Riemann theta function `\theta : \CC^g \times H_g \to \CC` is
        defined by the infinite series

        .. math::

            \theta( z | \Omega ) = \sum_{ n \in \ZZ^g } e^{ 2 \pi i \left( \tfrac{1}{2} \langle \Omega n, n \rangle +  \langle z, n \rangle \right) }


        The precision of Riemann theta function evaluation is determined by
        the precision of the base ring.

        As shown in [CRTF]_, `n` th order derivatives introduce polynomial
        growth in the oscillatory part of the Riemann theta approximations
        thus making a global approximation formula impossible. Therefore, one
        must specify a ``deriv_accuracy_radius`` of guaranteed accuracy when
        computing derivatives of `\theta(z | \Omega)`.
        """
        def __init__(self, name, nargs, latex_name, conversions):
            """
            Defines parameters in constructed class instance.

            EXAMPLE:

            An example does not really make sense, so we demonstrate the
            construction of a Riemann theta function::

                sage: R = ComplexField(20); I = R.gen()
                sage: Omega = matrix(R,2,2,[I,-1/2,-1/2,I])
                sage: theta = RiemannTheta(Omega, deriv=[[1,0]], deriv_accuracy_radius=6.0)
                sage: theta.deriv
                [[1, 0]]
                sage: theta.deriv_accuracy_radius
                6.00000000000000
            """
            self.Omega = Omega
            self.deriv = deriv
            self.uniform = uniform
            self.deriv_accuracy_radius = deriv_accuracy_radius
            Function_RiemannTheta.__init__(self, name, nargs,
                                           latex_name, conversions)

    return RiemannTheta(name, nargs, latex_name, conversions)

RiemannTheta = RiemannTheta_Constructor


class Function_RiemannTheta(BuiltinFunction):
    r"""
    Riemann theta function class.

    The Riemann theta function class subclasses ``BuiltinFunction`` so as
    to allow symbolic evaluation. An instance of ``Function_RiemannTheta``
    is created by ``RiemannTheta_Constructor``. This is done since
    the ``Function_RiemannTheta`` is parameterized by several variables
    such as the Riemann matrix `\Omega`.
    """
    def __init__(self, name, nargs, latex_name, conversions=None):
        r"""
        The ``__init__`` method wraps ``BuiltinFunction.__init__()``. This
        Computes the real and imaginary components of the Riemann matrix under
        some transformations.

        INPUT:

        - ``name`` -- the name of the function

        - ``nargs`` -- the number of

        - ``latex_name`` -- the name of the funciton as it would appear when LaTeX-ifying the object

        - ``conversions`` -- for talking to 3rd party software (e.g. Maple)

        EXAMPLES:

        Here we define a Riemann theta function using a `2 \times 2` Riemann
        matrix::

            sage: from sage.functions.riemann_theta import RiemannTheta
            sage: R = ComplexField(36); I = R.gen()
            sage: Omega = matrix(R,2,2,[1.690983006 + 0.9510565162*I, 1.5 + 0.363271264*I, 1.5 + 0.363271264*I, 1.309016994+ 0.9510565162*I])
            sage: theta = RiemannTheta(Omega)
            sage: theta
            Riemann theta function with defining Riemann matrix
            [1.690983006 + 0.9510565162*I 1.500000000 + 0.3632712640*I]
            [1.500000000 + 0.3632712640*I 1.309016994 + 0.9510565162*I]
            over the base ring Complex Field with 36 bits of precision
        """
        BuiltinFunction.__init__(self, name=name,
                                 nargs=nargs, latex_name=latex_name,
                                 conversions=conversions)

        self._max_points_in_one_evaluation = 32000
        self._g = ZZ(self.Omega.nrows())
        assert self._g == self.Omega.ncols()

        # store the base ring and a RealField of the same precision
        self._ring = self.Omega.base_ring()
        self._prec = self._ring.prec()
        self._realring = RealField(self._prec)

        # require that Omega be symmetric and the imaginary part be positive
        # positive definite. The check for positive definiteness is inherent
        # in the computation of the Cholesky decomposition below
        if (self.Omega - self.Omega.transpose()).norm() > 10 ** (-15):
            raise ValueError("Riemann matrix is not symmetric.")

        # compute real and imaginary parts of the Riemann matrix as well as
        # the Cholesky decomposition of the imaginary part
        self._X = self.Omega.apply_map(lambda t: t.real()).change_ring(self._realring)
        self._Y = self.Omega.apply_map(lambda t: t.imag()).change_ring(self._realring)
        self._T = self._Y.cholesky().transpose()

        # cache radii and inverses
        self._rad = None
        self._intpoints = None
        self._Xinv = self._X.inverse()
        self._Yinv = self._Y.inverse()
        self._Tinv = self._T.inverse()

    def __str__(self):
        r"""
        ``str(theta)`` returns a string representation of the Riemann theta
        function which is given by the defining Riemann matrix and the base
        ring.

        EXAMPLES::

            sage: R = ComplexField(36); I = R.gen()
            sage: Omega = matrix(R,2,2,[1.690983006 + 0.9510565162*I, 1.5 + 0.363271264*I, 1.5 + 0.363271264*I, 1.309016994+ 0.9510565162*I])
            sage: theta = RiemannTheta(Omega)
            sage: str(theta)
            'Riemann theta function with defining Riemann matrix\n[1.690983006 + 0.9510565162*I 1.500000000 + 0.3632712640*I]\n[1.500000000 + 0.3632712640*I 1.309016994 + 0.9510565162*I]\nover the base ring Complex Field with 36 bits of precision'
        """
        return repr(self)

    def __repr__(self):
        r"""
        String representation of Riemann theta function. Shows defining Riemann
        matrix and base ring.

        EXAMPLES::

            sage: R = ComplexField(36); I = R.gen()
            sage: Omega = matrix(R,2,2,[1.690983006 + 0.9510565162*I, 1.5 + 0.363271264*I, 1.5 + 0.363271264*I, 1.309016994+ 0.9510565162*I])
            sage: theta = RiemannTheta(Omega)
            sage: theta
            Riemann theta function with defining Riemann matrix
            [1.690983006 + 0.9510565162*I 1.500000000 + 0.3632712640*I]
            [1.500000000 + 0.3632712640*I 1.309016994 + 0.9510565162*I]
            over the base ring Complex Field with 36 bits of precision
        """
        if self.deriv == []:
            return "Riemann theta function with defining Riemann matrix\n" + \
                   str(self.Omega) + "\nover the base ring " + str(self._ring)
        else:
            return "Derivative of Riemann theta function in the " + \
                   str(self.deriv) + " direction(s) with defining Riemann matrix\n" + \
                   str(self.Omega) + "\nover the base ring " + str(self._ring)

    def lattice(self):
        r"""
        Compute the complex lattice corresponding to the Riemann matix. Uses
        the :module:sage.functions.complex_lattice module.

        .. NOTE::

            Not yet implemented.

        EXAMPLES::

            sage: from sage.functions.riemann_theta import RiemannTheta
            sage: R = ComplexField(20); I = R.gen()
            sage: Omega = matrix(R,2,2,[I,-1/2,-1/2,I])
            sage: theta = RiemannTheta(Omega)
            sage: theta.lattice() # optional: not implemented
            Traceback (most recent call last)
            ...
            NotImplementedError
        """
        raise NotImplementedError()

    def genus(self):
        r"""
        The genus of the algebraic curve from which the Riemann matrix is
        calculated. If `\Omega` is not block decomposable then this is just
        the dimension of the matrix.

        .. NOTE::

            Block decomposablility detection is difficult and not yet
            implemented. Currently, ``self.genus()`` just returns the size
            of the matrix.

        EXAMPLES:

        The following Riemann matrix is `2 \times 2` and is not block
        decomposable. So its genus should be two::

            sage: from sage.functions.riemann_theta import RiemannTheta
            sage: R = ComplexField(36); I = R.gen()
            sage: Omega = matrix(R,2,2,[1.690983006 + 0.9510565162*I, 1.5 + 0.363271264*I, 1.5 + 0.363271264*I, 1.309016994+ 0.9510565162*I])
            sage: theta = RiemannTheta(Omega)
            sage: theta.genus()
            2
        """
        return self._g

    def _plot_bounding_ellipsoid(self, z, R):
        r"""
        Returns a plot of the bounding ellipsoid of radius ``R`` centered
        at the complex point ``z``. Used to test validity of the
        ``RiemannTheta.integer_points()`` method.

        INPUT:

        - ``z``: the complex point at which the bounding ellipsoid is centered

        - ``R``: the radius of the ellipsoid

        EXAMPLES:

        The bounding ellipsoid for the below Riemann matrix should be a
        circle::

            sage: R = ComplexField(20); I = R.gen()
            sage: Omega = matrix(R,2,2,[I,-1/2,-1/2,I])
            sage: theta = RiemannTheta(Omega)
            sage: P = theta._plot_bounding_ellipsoid([0,0],5)
        """
        y = vector(self._ring, z).apply_map(lambda t: t.imag())
        shift = self._Yinv * y
        intshift = shift.apply_map(lambda t: t.round())
        c = shift - intshift

        if self._g == 2:
            # 2-D case
            xx, yy = var('xx,yy')
            v = vector(SR, [xx, yy])
            f = self._ring.pi() * (v - c).dot_product(self._Y * (v - c)) - R ** 2
            return implicit_plot(f, (xx, -R, R), (yy, -R, R))
        if self._g == 3:
            # 3-D case
            xx, yy, zz = var('xx,yy,zz')
            v = vector(SR, [xx, yy, zz])
            f = self._ring.pi() * (v + c).dot_product(self._Y * (v + c)) - R ** 2
            return implicit_plot(f, (xx, -R, R), (yy, -R, R), (zz, -R, R))
        # N-D case
        raise ValueError("Cannot visualize g=%d - dimensional ellipsoid." % self._g)

    def integer_points(self, z, R):
        r"""
        The set, `U_R`, of the integral points needed to compute Riemann
        theta at the complex point $z$ to the numerical precision given
        by the Riemann matirix base field precision.

        The set `U_R` of [CRTF], (21).

        .. math::

            \left\{ n \in \ZZ^g : \pi ( n - c )^{t} \cdot Y \cdot
            (n - c ) < R^2, |c_j| < 1/2, j=1,\ldots,g \right\}

        Since `Y` is positive definite it has Cholesky decomposition
        `Y = T^t T`. Letting `\Lambda` be the lattice of vectors
        `v(n), n \in ZZ^g` of the form `v(n)=\sqrt{\pi} T (n + [[ Y^{-1} n]])`,
        we have that

        .. math::

            S_R = \left\{ v(n) \in \Lambda : || v(n) || < R \right\} .

        Note that since the integer points are only required for oscillatory
        part of Riemann theta all over these points are near the point
        `0 \in \CC^g`. Additionally, if ``uniform == True`` then the set of
        integer points is independent of the input points `z \in \CC^g`.

        .. note::

            To actually compute `U_R` one needs to compute the convex hull of
            `2^{g}` bounding ellipsoids. Since this is computationally
            expensive, an ellipsoid centered at `0 \in \CC^g` with large
            radius is computed instead. This can cause accuracy issues with
            ill-conditioned Riemann matrices, that is, those that produce
            long and narrow bounding ellipsoies. See [CRTF] Section ### for
            more information.

        INPUTS:

        - ``z`` -- the point `z \in \CC` at which to compute `\theta(z|\Omega)`

        - ``R`` -- the first ellipsoid semi-axis length as computed by
          ``self.radius()``

        OUTPUTS:

        - (list) -- a list of integer points in `\ZZ^g` that fall
          within the pointwise approximation ellipsoid defined in
          [CRTF]

        .. warning::

            At times we work over ``RDF``, which have very low
            precision (53 bits). This could be a problem when given
            ill-conditioned input. The general computing theta functions with
            such ill-conditioned input will not be possible, so
            we do not concern outselves with this case. This can be resolved
            by implementing the Siegel transformation discussed in [CRTF].

        EXAMPLES:
        ``integer_points()`` returns the points over which the finite sum
        is computed given the first major axis of the bounding ellipsoid.
        Here, we simply provide such a radius for testing purposes.::

            sage: from sage.functions.riemann_theta import RiemannTheta
            sage: R = ComplexField(36); I = R.gen()
            sage: Omega = matrix(R,2,2,[I,-1/2,-1/2,I])
            sage: theta = RiemannTheta(Omega)
            sage: theta.integer_points([0,0],2)
            [[-1, 0], [0, 0], [1, 0]]
            sage: theta.integer_points([0,0],3)
            [[-1, -1], [0, -1], [1, -1], [-1, 0], [0, 0], [1, 0], [-1, 1], [0, 1], [1, 1]]
        """
        R = self._ring(R).real()
        pi = self._ring.pi()
        z = vector(self._ring, z)
        # x = z.apply_map(lambda t: t.real())
        y = z.apply_map(lambda t: t.imag())
        T = self._T

        # determine center of ellipsoid.
        if self.uniform:
            c = vector(self._ring, [0] * self._g)
            intc = vector(self._ring, [0] * self._g)
            leftc = vector(self._ring, [0] * self._g)
        else:
            c = self._Yinv * y
            intc = c.apply_map(lambda t: ZZ(t.round()))
            leftc = c - intc

        def find_integer_points(g, c, R, start):
            r"""
            Recursion function for computing the integer points needed in
            each coordinate direction.

            INPUT:

            - ``g`` -- the genus. recursively used to determine
              integer poiints along each axis.

            - ``c`` -- center of integer point computation. `0 \in
              \CC^g` is used when using the uniform approximation.

            - ``R`` -- the radius of the ellipsoid along the current
              axis.

            - ``start`` -- the starting integer point for each
              recursion along each axis.

            OUTPUT:

            - ``intpoints`` -- (list) a list of all of the integer
              points inside the bounding ellipsoid

            .. TODO::

                Recursion can be memory intensive in Python. For genus `g<30`
                this is a reasonable computation but can be sped up by
                writing a loop instead.
            """
            a = (c[g] - R / T[g, g]).real().ceil()
            b = (c[g] + R / T[g, g]).real().floor()

            # check if we reached the edge of the ellipsoid
            if not a < b:
                return []
            # last dimension reached: append points
            if g == 0:
                return [[i] + start for i in range(a, b + 1)]

            # compute new shifts, radii, start, and recurse
            newg = g - 1
            newT = T.submatrix(nrows=newg + 1, ncols=newg + 1)
            newTinv = newT.inverse()
            pts = []
            for n in range(a, b + 1):
                chat = vector(self._ring, c[:newg + 1])
                that = vector(self._ring, T.column(g)[:newg + 1])
                newc = chat - newTinv * that * (n - c[g])
                newR = (R ** 2 / pi - (T[g, g] * (n - c[g])) ** 2).sqrt()
                newstart = [n] + start
                pts += find_integer_points(newg, newc, newR, newstart)

            return pts

        return find_integer_points(self._g - 1, leftc, R, [])

    def radius(self, deriv=[]):
        r"""
        Calculate the radius `R` to compute the value of the theta function
        to within `2^{-P + 1}` bits of precision where `P` is the
        real / complex precision given by the input matrix. Used primarily
        by ``RiemannTheta.integer_points()``.

        `R` is the radius of [CRTF] Theorems 2, 4, and 6.

        INPUT:

        - ``deriv`` -- (list) (default=``[]``) the derivative, if given. Radius increases as order of derivative increases.

        EXAMPLES:

        Computing the radius. Note that the radius increases as a function of
        the precision::

            sage: R = ComplexField(10); I = R.gen()
            sage: Omega = matrix(R,2,2,[I,-1/2,-1/2,I])
            sage: theta = RiemannTheta(Omega)
            sage: theta.radius([])
            3.61513411073

            sage: R = ComplexField(40); I = R.gen()
            sage: Omega = matrix(R,2,2,[I,-1/2,-1/2,I])
            sage: theta = RiemannTheta(Omega)
            sage: theta.radius([])
            6.02254252538
            sage: theta.radius([[1,0]])
            6.37024100817
        """
        Pi = self._ring.pi()
        # I = self._ring.gen()
        g = self._g

        # compute the length of the shortest lattice vector
        U = self._T._pari_().qflll()._sage_()
        v = (U * self._T).column(0)
        r = RDF(v.norm())
        normTinv = self._Tinv.norm()

        # solve for the radius using:
        #   * Theorem 3 of [CRTF] (no derivative)
        #   * Theorem 5 of [CRTF] (first order derivative)
        #   * Theorem 7 of [CRTF] (second order derivative)
        if len(deriv) == 0:
            eps = RDF(2) ** RDF(-(self._ring.prec() + 2))
            lhs = RDF(eps * (2 / g) * (r / 2) ** g * gamma(g / 2))
            ins = RDF(gammainccinv(g / 2, lhs))
            R = ins.sqrt() + r / 2
            rad = max(R, ((2 * g).sqrt() + r) / 2)
        elif len(deriv) == 1:
            # solve for left-hand side
            L = self.deriv_accuracy_radius
            normderiv = vector(self._ring, deriv[0]).norm()
            eps = RDF(2) ** RDF(-(self._ring.prec() + 2))
            lhs = RDF(eps * (r / 2) ** g) / (Pi.sqrt() * g *
                                             normderiv * normTinv)

            # define right-hand-side function involving the incomplete gamma
            # function
            def rhs(ins):
                """
                Right-hand side function for computing the bounding ellipsoid
                radius given a desired maximum error bound for the first
                derivative of the Riemann theta function.

                INPUT:

                - ``ins`` -- the quantity `(R-\rho)^2` where `R` is the radius we must solve for and `\rho` is the length of the shortest lattice vector in the integer lattice defined by `\Omega`.

                EXAMPLES:

                Since this function is used implicitly in
                ``RiemannTheta.radius()`` we use an example input from above::

                    sage: R = ComplexField(40); I = R.gen()
                    sage: Omega = matrix(R,2,2,[I,-1/2,-1/2,I])
                    sage: theta = RiemannTheta(Omega)
                    sage: theta.radius([])
                    6.02254252538
                    sage: theta.radius([[1,0]])
                    6.37024100817
                """
                return (gamma((g + 1) / 2) * gammaincc((g + 1) / 2, ins) +
                        Pi.sqrt() * normTinv * L * gamma(g / 2) *
                        gammaincc(g / 2, ins) -
                        float(lhs))

            #  define lower bound (guess) and attempt to solve for the radius
            lbnd = (g + 2 + (g ** 2 + 8).sqrt()).sqrt() + r
            try:
                ins = RDF(fsolve(rhs, float(lbnd))[0])
            except RuntimeWarning:
                # fsolve had trouble finding the solution. We try
                # a larger initial guess since the radius increases
                # as desired precision increases
                try:
                    ins = RDF(fsolve(rhs, float(2 * lbnd))[0])
                except RuntimeWarning:
                    raise ValueError("Could not find an accurate bound for the radius. Consider using higher precision.")

            # solve for radius
            R = ins.sqrt() + r / 2
            rad = max(R, lbnd)

        elif len(deriv) == 2:
            # solve for left-hand side
            L = self.deriv_accuracy_radius
            prodnormderiv = prod([vector(self._ring, d).norm() for d in deriv])

            eps = RDF(2) ** RDF(-(self._ring.prec() + 2))
            lhs = RDF(eps * (r / 2) ** g) / (2 * Pi * g *
                                             prodnormderiv * normTinv ** 2)

            # define right-hand-side function involving the incomplete gamma
            # function
            def rhs(ins):
                """
                Right-hand side function for computing the bounding ellipsoid
                radius given a desired maximum error bound for the second
                derivative of the Riemann theta function.

                INPUT:

                    - ``ins`` -- the quantity `(R-\rho)^2` where `R` is the radius we must solve for and `\rho` is the length of the shortest lattice vector in the integer lattice defined by `\Omega`.

                EXAMPLES:

                Since this function is used implicitly in
                ``RiemannTheta.radius()`` we use an example input from above::

                    sage: R = ComplexField(40); I = R.gen()
                    sage: Omega = matrix(R,2,2,[I,-1/2,-1/2,I])
                    sage: theta = RiemannTheta(Omega)
                    sage: theta.radius([])
                    6.02254252538
                    sage: theta.radius([[1,0]])
                    6.37024100817
                """
                return (gamma((g + 2) / 2) * gammaincc((g + 2) / 2, ins) +
                        2 * Pi.sqrt() * normTinv * L *
                        gamma((g + 1) / 2) * gammaincc((g + 1) / 2, ins) +
                        Pi * normTinv ** 2 * L ** 2 *
                        gamma(g / 2) * gammaincc(g / 2, ins) - float(lhs))

            #  define lower bound (guess) and attempt to solve for the radius
            lbnd = (g + 4 + (g ** 2 + 16).sqrt()).sqrt() + r
            try:
                ins = RDF(fsolve(rhs, float(lbnd))[0])
            except RuntimeWarning:
                # fsolve had trouble finding the solution. We try
                # a larger initial guess since the radius increases
                # as desired precision increases
                try:
                    ins = RDF(fsolve(rhs, float(2 * lbnd))[0])
                except RuntimeWarning:
                    raise ValueError("Could not find an accurate bound for the radius. Consider using higher precision.")

            # solve for radius
            R = ins.sqrt() + r / 2
            rad = max(R, lbnd)

        else:
            # can't computer higher derivatives, yet
            raise NotImplementedError("Ellipsoid radius for first and second derivatives not yet implemented.")

        return RDF(rad)

    def exp_and_osc_at_point(self, z, deriv=[]):
        r"""
        Calculate the exponential and oscillating parts of `\theta(z,\Omega)`.
        (Or a given directional derivative of `\theta`.) That is, compute
        complex numbers `u,v \in \CC` such that `\theta(z,\Omega) = e^u v`
        where the value of `v` is oscillatory as a function of `z`.

        INPUT:

        - ``z`` -- a list or tuple representing the complex `\CC^g` point at which to evaluate `\theta(z | \Omega)`

        - ``deriv`` -- (default: ``[]``) list representing the directional derivative of `\theta(z | \Omega)` you wish to compute

        OUTPUT:

        - ``(u,v)`` -- data pair such that `\theta(z,\Omega) = e^u v`.

        EXAMPLES:

        First, define a Riemann matrix and Riemann theta function::

            sage: from sage.functions.riemann_theta import RiemannTheta
            sage: R = ComplexField(36); I = R.gen()
            sage: Omega = matrix(R,2,2,[1.690983006 + 0.9510565162*I, 1.5 + 0.363271264*I, 1.5 + 0.363271264*I, 1.309016994+ 0.9510565162*I])
            sage: theta = RiemannTheta(Omega)

        Some example evaluations::

            sage: theta.exp_and_osc_at_point([0,0])
            (0, 1.050286258 - 0.1663490011*I)
            sage: theta.exp_and_osc_at_point([0.3+0.5*I,0.9+1.2*I])
            (4.763409165, 0.1568397231 - 1.078369835*I)
            sage: theta.exp_and_osc_at_point([0.3+0.5*I,0.9+1.2*I], deriv=[[1,0]])
            (4.763409165, -0.5864936847 + 0.04570614011*I)

        Defining a Riemann theta function, we demonstrate that the oscillatory
        part is periodic in each component with period 1::

            sage: theta.exp_and_osc_at_point([0,0])
            (0, 1.050286258 - 0.1663490011*I)
            sage: theta.exp_and_osc_at_point([1,3])
            (0, 1.050286258 - 0.1663490011*I)
        """
        domain = self._realring
        pi = domain.pi()

        # extract real and imaginary parts of input z
        z = vector(self._ring, z)
        x = z.apply_map(lambda t: t.real())
        x = x.change_ring(domain)
        y = z.apply_map(lambda t: t.imag())
        y = y.change_ring(domain)

        # convert derivatives to vector type
        _deriv = [vector(self._ring, d) for d in self.deriv]
        _deriv.extend([vector(self._ring, d) for d in deriv])
        deriv = _deriv

        # compute integer points: check for uniform approximation
        if self.uniform:
            # check if we've already computed the uniform radius and intpoints
            if not self._rad:
                self._rad = self.radius(deriv=deriv)
            if not self._intpoints:
                # fudge factor for uniform radius
                origin = [0] * self._g
                self._intpoints = self.integer_points(origin, 1.5 * self._rad)
            # R = self._rad
            S = self._intpoints
        else:
            # R = self.radius(deriv=deriv)
            S = self.integer_points(z, self._rad)

        # compute oscillatory and exponential terms
        Yinv = self._Yinv
        Yinv = Yinv.change_ring(domain)
        v = self._ring(self._finite_sum(x, y, S, deriv, domain))
        u = self._ring(pi * y.dot_product(Yinv * y))

        return u, v

    def value_at_point(self, z, deriv=[]):
        r"""
        Return the value of `\theta(z,\Omega)` at a point `z`.

        INPUT:

        - ``z`` -- the complex `\CC^g` point at which to evaluate
          `\theta(z,\Omega)`

        - ``deriv`` -- (default: ``[]``) list representing the
          directional derivative of `\theta(z | \Omega)` you wish to
          compute

        OUTPUT:

        - `\theta(z | \Omega)` -- value of `\theta` at `z`

        EXAMPLES:

        Computing the value of a genus 2 Riemann theta function at the origin::

            sage: from sage.functions.riemann_theta import RiemannTheta
            sage: R = ComplexField(36); I = R.gen()
            sage: Omega = matrix(R,2,2,[1.690983006 + 0.9510565162*I, 1.5 + 0.363271264*I, 1.5 + 0.363271264*I, 1.309016994+ 0.9510565162*I])
            sage: theta = RiemannTheta(Omega)
            sage: theta.value_at_point([0,0])
            1.050286258 - 0.1663490011*I
            sage: theta([0,0])
            1.050286258 - 0.1663490011*I
        """
        exp_part, osc_part = self.exp_and_osc_at_point(z, deriv=deriv)
        return exp_part.exp() * osc_part

    def _finite_sum(self, x, y, S, deriv, domain):
        """
        Compute the oscillatory part of the finite sum

        .. math::

            \theta( z | \Omega ) = \sum_{ U_R } e^{ 2 \pi i \left( \tfrac{1}{2} \langle \Omega n, n \rangle +  \langle z, n \rangle \right) }

        where

        .. math::

            U_R = \left\{ n \in \ZZ^g : \pi ( n - c )^{t} \cdot Y \cdot
            (n - c ) < R^2, |c_j| < 1/2, j=1,\ldots,g \right\}.

        The oscillatory part

        .. note::

            For accuracy issues we split the computation into its real and
            imaginary components.

        INPUT:

        - ``x`` -- the real part of the input vector `z`

        - ``y`` -- the imaginary part of the input vector `z`

        - ``S`` -- the set of integer points over which to compute the finite sum. Often, this is set to `U_R` by calling ``RiemannTheta.integer_points()`.

        - ``deriv`` -- the derivative, if any

        - ``domain`` -- a ``RealField`` object. Sets the ring over which comptuations are performed. For computational accuracy, we separate real and imaginary parts of the finite sum and compute over the reals.

        OUTPUT:

        - the value of the oscillatory part of the Riemann theta function

        EXAMPLES:

        ``_finite_sum`` is implicitly called when, for example, computing the
        value of a genus 2 Riemann theta function at the origin::

            sage: from sage.functions.riemann_theta import RiemannTheta
            sage: R = ComplexField(36); I = R.gen()
            sage: Omega = matrix(R,2,2,[1.690983006 + 0.9510565162*I, 1.5 + 0.363271264*I, 1.5 + 0.363271264*I, 1.309016994+ 0.9510565162*I])
            sage: theta = RiemannTheta(Omega)
            sage: theta.value_at_point([0,0])
            1.050286258 - 0.1663490011*I
        """
        # create polynomial ring for fast_callable computation (see below)
        if self._g > 1:
            R = PolynomialRing(domain, 'u', self._g)
        else:
            R = PolynomialRing(domain, 'u')

        X = self._X
        # Y = self._Y
        T = self._T
        I = self._ring.gen()
        Yinv = self._Yinv
        pi = domain.pi()
        twopi = domain(2.0) * pi
        half = domain(0.5)

        # define shifted vectors
        shift = Yinv * y
        intshift = shift.apply_map(lambda t: t.round())
        fracshift = shift - intshift

        # fast callable matrix-vector operations
        a_ = vector(R.gens())
        exppart_ = twopi * (a_ - intshift) * (half * X * (a_ - intshift) + x)
        exppart = fast_callable(exppart_, domain=domain)
        normpart_ = - pi * (T * (a_ + fracshift)) * (T * (a_ + fracshift))
        normpart = fast_callable(normpart_, domain=domain)

        if not deriv == []:
            # for ease of computation, we perform derivative product
            # computation in a complex ring
            derivprod_ = prod(2 * pi * I * d * (a_ - intshift) for d in deriv)
            derivprod = fast_callable(derivprod_, domain=self._ring)

        # compute the finite sum
        fsum_real = domain(0)
        fsum_imag = domain(0)
        for n in S:
            ep = exppart(*n)
            np = normpart(*n).exp()
            cpart = np * ep.cos()
            spart = np * ep.sin()

            if deriv:
                dp = derivprod(*n)
                dpr = dp.real()
                dpi = dp.imag()
                fsum_real += dpr * cpart - dpi * spart
                fsum_imag += dpi * cpart + dpr * spart
            else:
                fsum_real += cpart
                fsum_imag += spart

        return self._ring(fsum_real) + I * self._ring(fsum_imag)

    def __call__(self, *args, **kwds):
        r"""
        Return the value of `\theta(z,\Omega)` at a point `z`.

        Lazy evaluation is done if the input contains symbolic variables.

        INPUT:

        - ``z`` -- the complex `\CC^g` point at which to evaluate
          `\theta(z,\Omega)`

        - ``deriv`` -- (default: ``[]``) list representing the
          directional derivative of `\theta(z | \Omega)` you wish to
          compute

        OUTPUT:

        - `\theta(z | \Omega)` -- value of `\theta` at `z`

        EXAMPLES:

        Computing the value of a genus 2 Riemann theta function at the origin::

            sage: from sage.functions.riemann_theta import RiemannTheta
            sage: R = ComplexField(36); I = R.gen()
            sage: Omega = matrix(R,2,2,[1.690983006 + 0.9510565162*I, 1.5 + 0.363271264*I, 1.5 + 0.363271264*I, 1.309016994+ 0.9510565162*I])
            sage: theta = RiemannTheta(Omega)
            sage: theta([0,0])
            1.050286258 - 0.1663490011*I

        Performs lazy evaluation of symbolic input::

            sage: var('x')
            x
            sage: f = theta([x^2,sin(x)]); f
            theta(x^2, sin(x))
            sage: f(x=1.0*I)
            -94.35488925 - 59.48498251*I
        """
        if any(is_Expression(arg) for arg in args[0]):
            return BuiltinFunction.__call__(self, *args[0])
        else:
            return self.value_at_point(*args, **kwds)

    def _eval_(self, *args, **kwds):
        r"""
        Enables symbolic evaluation of Riemann theta.

        EXAMPLES:

        Testing symbolic evaluation of Riemann Theta::

            sage: R = ComplexField(10); I = R.gen()
            sage: Omega = matrix(R,2,2,[I,-1/2,-1/2,I])
            sage: theta = RiemannTheta(Omega)
            sage: var('x')
            x
            sage: f = theta([x^2,1+x]); f
            theta(x^2, x + 1)
            sage: f(x=I)
            23. + 0.045*I
        """
        has_symbolic = False
        for arg in args:
            try:
                self._ring(arg)
            except TypeError:
                has_symbolic = True

        if has_symbolic:
            return None
        else:
            return self.value_at_point(*(args,), **kwds)

    def _derivative_(self, *args, **kwds):
        r"""
        Enables computation of symbolic derivatives of Riemann theta.

        Note that directional derivatives of Riemann theta are separate
        objects since the class is parameterized by the directional derivative.
        Hence, the derivative with respect to a symbolic variable return a
        sum of separate Riemann theta objects.

        EXAMPLES:

            sage: R = ComplexField(10); I = R.gen()
            sage: Omega = matrix(R,2,2,[I,-1/2,-1/2,I])
            sage: theta = RiemannTheta(Omega)
            sage: f = theta([x^2,1+x])
            sage: f.derivative(x,1)
            2*x*theta_10(x^2, x + 1) + theta_01(x^2, x + 1)
        """
        diff_param = kwds['diff_param']
        deriv = (self._g * [0])
        deriv[diff_param] = 1
        newderiv = [d for d in self.deriv]  # to avoid deep copy
        newderiv.append(deriv)

        return RiemannTheta_Constructor(self.Omega, newderiv,
                                        uniform=self.uniform,
                                        deriv_accuracy_radius=self.deriv_accuracy_radius)(*(args,), **kwds)
