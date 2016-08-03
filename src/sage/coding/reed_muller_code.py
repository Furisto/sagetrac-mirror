r"""
Reed-Muller code

Given integers `m, r` and a finite field `F`,
the corresponding Reed-Muller Code is the set:

.. math::

    \{ (f(\alpha_i)\mid \alpha_i \in F^m)  \mid  f \in F[x_1,x_2,\ldots,x_m], \deg f \leq r \}

This file contains the following elements:

    - :class:`QAryReedMullerCode`, the class for Reed-Muller codes over non-binary field of size q and `r<q`
    - :class:`BinaryReedMullerCode`, the class for Reed-Muller codes over binary field and `r<=m`
    - :class:`ReedMullerVectorEncoder`, an encoder with a vectorial message space (for both the two code classes)
    - :class:`ReedMullerPolynomialEncoder`, an encoder with a polynomial message space (for both the code classes)
    - :class:`BinaryReedMullerMajorityDecoder`, a decoder for binary Reed-Muller codes which corrects using majority vote algorithm
    - :class:`QAryReedMullerRSDecoder`, an decoder for q-ary Reed-Muller code which corrects by treating the code as a sub code of a Reed Solomon code
"""
#*****************************************************************************
#       Copyright (C) 2016 Parthasarathi Panda <parthasarathipanda314@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from operator import mul
from sage.matrix.constructor import matrix
from sage.functions.other import binomial
from sage.calculus.var import var
from sage.misc.functional import symbolic_sum
from sage.coding.linear_code import AbstractLinearCode, LinearCodeSyndromeDecoder
from sage.coding.encoder import Encoder
from sage.coding.decoder import Decoder
from sage.coding.grs import GeneralizedReedSolomonCode
from sage.combinat.subset import Subsets
from sage.combinat.tuple import Tuples
from sage.categories.finite_fields import FiniteFields
from sage.rings.finite_rings.finite_field_constructor import GF
from sage.rings.integer import Integer
from sage.modules.free_module_element import vector
from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing
from sage.misc.cachefunc import cached_method
from sage.sets.set import Set
from functools import reduce
from copy import copy


def _binomial_sum(n, k):
    r"""
    Returns the sum of all binomials `\binom{n}{i}`,
    with `i` ranging from `0` to `k` and including `k`.

    INPUT:

    - ``n, k`` - integers

    EXAMPLES::

        sage: from sage.coding.reed_muller_code import _binomial_sum
        sage: _binomial_sum(4, 2)
        11
    """
    s = 1
    nCi = 1
    for i in range(k):
        nCi = ((n - i) * nCi) // (i + 1)
        s = nCi + s
    return s


def _multivariate_polynomial_interpolation(evaluation, order, polynomial_ring):
    r"""
    Returns `f \in \GF(q)[X_1,...,X_m]` such that `f(\mathbf a) = v[i(\mathbf a)]`
    for all `\mathbf a \in \GF(q^m)`, where `v \in GF(q){qm}` is a given
    vector of evaluations, and `i(a)` is a specific ordering of `GF(q^m)` (see below for details)

    The ordering `i(a)` is the one used by Sage when listing the elements
    of a Finite Field with a call to the method ``list``.

    In case the polynomial `f` does not exist, this method returns an arbitray polynomial.

    INPUT:

    - ``evaluation`` -- A vector or a list of evaluation of the polynomial at all the points.

    - ``num_of_var`` -- The number of variables used in the polynomial to interpolate

    - ``order`` -- The degree of the polynomial to interpolate

    - ``polynomial_ring`` -- The Polynomial Ring the polynomial in question is from

    EXAMPLES::

        sage: from sage.coding.reed_muller_code import _multivariate_polynomial_interpolation
        sage: F = GF(3)
        sage: R.<x,y> = F[]
        sage: v = vector(F, [1, 2, 0, 0, 2, 1, 1, 1, 1])
        sage: _multivariate_polynomial_interpolation(v, 2, R)
        x*y + y^2 + x + y + 1

    If there does not exist
    """
    def _interpolate(evaluation, num_of_var, order):
        if num_of_var == 0 or order == 0:
            return evaluation[0]
        base_field = polynomial_ring.base_ring()
        q = base_field.cardinality()
        n_by_q = q**(num_of_var - 1)
        d = min(order + 1, q)
        multipoint_evaluation_list = []
        uni_poly_ring = PolynomialRing(base_field, 'x')
        base_field_zero = base_field.zero()
        for k in range(n_by_q):
            iterator = iter(base_field)
            points = []
            for i in range(d):
                xcoordinate = iterator.next()
                points.append((xcoordinate, evaluation[k + i * n_by_q]))
            polyVector = uni_poly_ring.lagrange_polynomial(
                points).coefficients(sparse=False)
            if len(polyVector) < d:
                # adding zeros to represet a (d-1) degree polynomial
                polyVector += [base_field_zero] * (d - len(polyVector))
            multipoint_evaluation_list.append(polyVector)
        poly = polynomial_ring.zero()
        z = 1
        x = polynomial_ring.gen(num_of_var - 1)
        for k in range(d):  # computing the polynomial
            poly = poly + z * _interpolate([multipoint_evaluation_list[i][k]
                                            for i in range(n_by_q)], num_of_var - 1, order - k)
            z *= x
        return poly
    return _interpolate(evaluation, polynomial_ring.ngens(), order)


def _set_to_mask(s, m):
    r"""
    Maps the set to an integer.
    The integer is given by `\sum^{m-1}_{i=0} 2^i\delta(i\in s)`.

    INPUT::

    - ``s`` -- A subset of `\{0,1,\ldots,m-1\}`.

    - ``m`` -- The number of elements in the super set.

    EXAMPLES::

        sage: from sage.coding.reed_muller_code import _set_to_mask
        sage: _set_to_mask(Set([1,3,4]),5)
        26
    """
    ans = 0
    p = 1
    for i in range(m):
        if (i in s):
            ans += p
        p <<= 1
    return ans

@cached_method
def _list_polynomial(base_field, y, dim):
    r"""
    Returns the list of all polynomials of degree ``dim-1`` over ``base_field``. 

    INPUT::

    - ``base_field`` -- A finite field 

    - ``y`` -- The generator of the polynomial ring.

    - ``dim`` -- An integer.

    EXAMPLES::

        sage: from sage.coding.reed_muller_code import _list_polynomial
        sage: F=GF(2)
        sage: R.<x>=F[]
        sage: _list_polynomial(F, R.gen(), 3)
        [0, 1, x, x + 1, x^2, x^2 + 1, x^2 + x, x^2 + x + 1]
    """
    base_field_tuple = Tuples(base_field.list(), dim)
    one = base_field.one()
    zero = base_field.zero()
    v = []
    for x in base_field_tuple:
        t = one
        sum = zero
        for i in range(dim):
            sum += x[i] * t
            t *= y
        v.append(sum)
    return v


def _reed_solomon_supercode(code, p=None):
    r"""
    Returns the Reed Solomon supercode of the given Reed-Muller code.
    The Reed Solomon supercode can be obtained my mapping each element of a vector field `\Bold{F}^m_{q}` to `\Bold{F}_{q^m}`
    via a linear transformation over `\Bold{F}_q` and then using them as evaluation points of Reed-Solomon code. 
    This process gives a supercode of the Reed-Muller code which is a Reed-Solomon code. 
    
    INPUT::

    - ``code`` -- A Reed-Muller code. 

    - ``p`` -- An irreducible polynomial over the base field of ``code`` of degree same as number of variables used in ``code``.

    EXAMPLES::

        sage: from sage.coding.reed_muller_code import _reed_solomon_supercode
        sage: C = codes.ReedMullerCode(GF(3), 2, 5)
        sage: sC = _reed_solomon_supercode(C)
        sage: sC
        [243, 163, 81] Generalized Reed-Solomon Code over Finite Field in y of size 3^5

    A polynomial ``p`` can be passed to direct the extension field::

        sage: F = GF(4)
        sage: R.<x> = F[]
        sage: p = x^4 + x^3 + F.gen()*x^2 + x + 1
        sage: p.is_irreducible()
        True
        sage: C = codes.ReedMullerCode(F, 2, 4)
        sage: sC = _reed_solomon_supercode(C, p)
        sage: sC
        [256, 129, 128] Generalized Reed-Solomon Code over Univariate Quotient Polynomial Ring in y over Finite Field in z2 of size 2^2 with modulus y^4 + y^3 + z2*y^2 + y + 1

    """
    n = code.length()
    order = code.order()
    num_of_var = code.number_of_variables()
    base_field = code.base_field()
    q = base_field.cardinality()
    if p is None:
        p = PolynomialRing(base_field, 'x').irreducible_element(num_of_var)
    else:
        if not p.is_irreducible():
            raise ValueError('p must be an irreducible polynomial')
        if p.degree() != code.number_of_variables():
            raise ValueError(
                'the degree of p must be same as the number of variables used in the Reed-Muller code')
    extended_field = base_field.extension(p, 'y')
    evalPoints = _list_polynomial(
        base_field, extended_field.gen(), num_of_var)
    dimension = min(((n * order) // q) + 1, n)
    RS_code = GeneralizedReedSolomonCode(evalPoints, dimension)
    return RS_code


def ReedMullerCode(base_field, order, num_of_var):
    r"""
    Returns a Reed-Muller code.

    A Reed-Muller Code of order `r` and number of variables `m` over a finite field `F` is the set:

    .. math::

        \{ (f(\alpha_i)\mid \alpha_i \in F^m)  \mid  f \in F[x_1,x_2,\ldots,x_m], \deg f \leq r \}

    INPUT:

    - ``base_field`` -- The finite field `F` over which the code is built.

    - ``order`` -- The order of the Reed-Muller Code, which is the maximum
                   degree of the polynomial to be used in the code.

    - ``num_of_var`` -- The number of variables used in polynomial.

    .. WARNING::

        For now, this implementation only supports Reed-Muller codes whose order is less than q.
        Binary Reed-Muller codes must have their order less than or
        equal to their number of variables.

    EXAMPLES:

    We build a Reed-Muller code::

        sage: F = GF(3)
        sage: C = codes.ReedMullerCode(F, 2, 2)
        sage: C
        Reed-Muller Code of order 2 and 2 variables over Finite Field of size 3

    We ask for its parameters::

        sage: C.length()
        9
        sage: C.dimension()
        6
        sage: C.minimum_distance()
        3

    If one provides a finite field of size 2, a Binary Reed-Muller code is built::

        sage: F = GF(2)
        sage: C = codes.ReedMullerCode(F, 2, 2)
        sage: C
        Binary Reed-Muller Code of order 2 and number of variables 2
    """
    if not(base_field in FiniteFields):
        raise ValueError("The parameter `base_field` must be a finite field")
    q = base_field.cardinality()
    if q == 2:
        return BinaryReedMullerCode(order, num_of_var)
    else:
        return QAryReedMullerCode(base_field, order, num_of_var)


class QAryReedMullerCode(AbstractLinearCode):
    r"""
    Representation of a q-ary Reed-Muller code.

    For details on the definition of Reed-Muller codes, refer to
    :meth:`ReedMullerCode`.

    .. NOTE::

        It is better to use the aforementioned method rather than calling
        this class directly, as :meth:`ReedMullerCode` creates either
        a binary or a q-ary Reed-Muller code according to the arguments it receives.

    INPUT:

    - ``base_field`` -- A finite field, which is the base field of the code.

    - ``order`` -- The order of the Reed-Muller Code, i.e., the maximum degree of the polynomial to be used in the code.

    - ``num_of_var`` -- The number of variables used in polynomial.

    .. WARNING::

        For now, this implementation only supports Reed-Muller codes whose order is less than q.

    EXAMPLES::

        sage: from sage.coding.reed_muller_code import QAryReedMullerCode
        sage: F = GF(3)
        sage: C = QAryReedMullerCode(F, 2, 2)
        sage: C
        Reed-Muller Code of order 2 and 2 variables over Finite Field of size 3
    """

    _registered_encoders = {}
    _registered_decoders = {}

    def __init__(self, base_field, order, num_of_var):
        r"""
        TESTS:

        Note that the order given cannot be greater than (q-1). An error is raised if that happens::

            sage: from sage.coding.reed_muller_code import QAryReedMullerCode
            sage: C = QAryReedMullerCode(GF(3), 4, 4)
            Traceback (most recent call last):
            ...
            ValueError: The order must be less than 3

        The order and the number of variable must be integers::

            sage: C = QAryReedMullerCode(GF(3),1.1,4)
            Traceback (most recent call last):
            ...
            ValueError: The order of the code must be an integer

        The base_field parameter must be a finite field::

            sage: C = QAryReedMullerCode(QQ,1,4)
            Traceback (most recent call last):
            ...
            ValueError: the input `base_field` must be a FiniteField
        """
        # input sanitization
        if not(base_field in FiniteFields):
            raise ValueError("the input `base_field` must be a FiniteField")
        if not(isinstance(order, (Integer, int))):
            raise ValueError("The order of the code must be an integer")
        if not(isinstance(num_of_var, (Integer, int))):
            raise ValueError("The number of variables must be an integer")
        q = base_field.cardinality()
        if (order >= q):
            raise ValueError("The order must be less than %s" % q)

        super(QAryReedMullerCode, self).__init__(base_field,
                                                 q**num_of_var, "EvaluationVector", "Syndrome")
        self._order = order
        self._num_of_var = num_of_var
        self._dimension = binomial(num_of_var + order, order)

    def order(self):
        r"""
        Returns the order of ``self``.

        Order is the maximum degree of the polynomial used in the Reed-Muller code.

        EXAMPLES::

            sage: from sage.coding.reed_muller_code import QAryReedMullerCode
            sage: F = GF(59)
            sage: C = QAryReedMullerCode(F, 2, 4)
            sage: C.order()
            2
        """
        return self._order

    def number_of_variables(self):
        r"""
        Returns the number of variables of the polynomial ring used in ``self``.

        EXAMPLES::

            sage: from sage.coding.reed_muller_code import QAryReedMullerCode
            sage: F = GF(59)
            sage: C = QAryReedMullerCode(F, 2, 4)
            sage: C.number_of_variables()
            4
        """
        return self._num_of_var

    def minimum_distance(self):
        r"""
        Returns the minimum distance between two words in ``self``.

        The minimum distance of a q-ary Reed-Muller code with order `d` and number of variables `m` is `(q-d)q^{m-1}`

        EXAMPLES::

            sage: from sage.coding.reed_muller_code import QAryReedMullerCode
            sage: F = GF(5)
            sage: C = QAryReedMullerCode(F, 2, 4)
            sage: C.minimum_distance()
            375
        """
        d = self.order()
        q = self.base_field().cardinality()
        n = self.length()
        return ((q - d) * n) // q

    def _repr_(self):
        r"""
        Returns a string representation of ``self``.

        EXAMPLES::

            sage: from sage.coding.reed_muller_code import QAryReedMullerCode
            sage: F = GF(59)
            sage: C = QAryReedMullerCode(F, 2, 4)
            sage: C
            Reed-Muller Code of order 2 and 4 variables over Finite Field of size 59
        """
        return "Reed-Muller Code of order %s and %s variables over %s" % (
            self.order(), self.number_of_variables(), self.base_field())

    def _latex_(self):
        r"""
        Returns a latex representation of ``self``.

        EXAMPLES::

            sage: from sage.coding.reed_muller_code import QAryReedMullerCode
            sage: F = GF(59)
            sage: C = QAryReedMullerCode(F, 2, 4)
            sage: latex(C)
            \textnormal{Reed-Muller Code of order} 2 \textnormal{and }4 \textnormal{variables over} \Bold{F}_{59}
        """
        return "\\textnormal{Reed-Muller Code of order} %s \\textnormal{and }%s \\textnormal{variables over} %s"\
            % (self.order(), self.number_of_variables(), self.base_field()._latex_())

    def __eq__(self, other):
        r"""
        Tests equality between Reed-Muller Code objects.

        EXAMPLES::

            sage: from sage.coding.reed_muller_code import QAryReedMullerCode
            sage: F = GF(59)
            sage: C1 = QAryReedMullerCode(F, 2, 4)
            sage: C2 = QAryReedMullerCode(GF(59), 2, 4)
            sage: C1.__eq__(C2)
            True
        """
        # I am not comparing the base field directly because of possible change
        # in variables
        return isinstance(other, QAryReedMullerCode) \
            and self.base_field() == other.base_field() \
            and self.order() == other.order() \
            and self.number_of_variables() == other.number_of_variables()

    def reed_solomon_supercode(self, p = None):
        r"""
        Returns the Reed Solomon supercode of the given Reed-Muller code.
        The Reed Solomon supercode can be obtained my mapping each element of a vector field `\Bold{F}^m_{q}` to `\Bold{F}_{q^m}`
        via a linear transformation over `\Bold{F}_q` and then using them as evaluation points of Reed-Solomon code. 
        This process gives a supercode of the Reed-Muller code which is a Reed-Solomon code. 

        INPUT::

        - ``p`` -- An irreducible polynomial over the base field of ``code`` of degree same as number of variables used in ``code``.

        EXAMPLES::

            sage: C = codes.ReedMullerCode(GF(3), 2, 5)
            sage: sC = C.reed_solomon_supercode()
            sage: sC
            [243, 163, 81] Generalized Reed-Solomon Code over Finite Field in y of size 3^5

        A polynomial ``p`` can be passed to direct the extension field::

            sage: F = GF(4)
            sage: R.<x> = F[]
            sage: p = x^4 + x^3 + F.gen()*x^2 + x + 1
            sage: p.is_irreducible()
            True
            sage: C = codes.ReedMullerCode(F, 2, 4)
            sage: sC = C.reed_solomon_supercode(p)
            sage: sC
            [256, 129, 128] Generalized Reed-Solomon Code over Univariate Quotient Polynomial Ring in y over Finite Field in z2 of size 2^2 with modulus y^4 + y^3 + z2*y^2 + y + 1

        """
        return _reed_solomon_supercode(self, p)


class BinaryReedMullerCode(AbstractLinearCode):
    r"""
    Representation of a binary Reed-Muller code.

    For details on the definition of Reed-Muller codes, refer to
    :meth:`ReedMullerCode`.

    .. NOTE::

        It is better to use the aforementioned method rather than calling
        this class directly, as :meth:`ReedMullerCode` creates either
        a binary or a q-ary Reed-Muller code according to the arguments it receives.


    INPUT:

    - ``order`` -- The order of the Reed-Muller Code, i.e., the maximum degree of the polynomial to be used in the code.

    - ``num_of_var`` -- The number of variables used in the polynomial.

    EXAMPLES:

    A binary Reed-Muller code can be constructed by simply giving the order of the code and the number of variables::

        sage: C = codes.BinaryReedMullerCode(2, 4)
        sage: C
        Binary Reed-Muller Code of order 2 and number of variables 4
    """

    _registered_encoders = {}
    _registered_decoders = {}

    def __init__(self, order, num_of_var):
        r"""
        TESTS:

        If the order given is greater than the number of variables an error is raised::

            sage: C = codes.BinaryReedMullerCode(5, 4)
            Traceback (most recent call last):
            ...
            ValueError: The order must be less than or equal to 4

        The order and the number of variable must be integers::

            sage: C = codes.BinaryReedMullerCode(1.1,4)
            Traceback (most recent call last):
            ...
            ValueError: The order of the code must be an integer
        """
        # input sanitization
        if not(isinstance(order, (Integer, int))):
            raise ValueError("The order of the code must be an integer")
        if not(isinstance(num_of_var, (Integer, int))):
            raise ValueError("The number of variables must be an integer")
        if (num_of_var < order):
            raise ValueError(
                "The order must be less than or equal to %s" %
                num_of_var)

        super(BinaryReedMullerCode, self).__init__(GF(2), 2**num_of_var,
                                                   "EvaluationVector", "Syndrome")
        self._order = order
        self._num_of_var = num_of_var
        self._dimension = _binomial_sum(num_of_var, order)

    def order(self):
        r"""
        Returns the order of ``self``. Order is the maximum degree of the polynomial used in the Reed-Muller code.

        EXAMPLES::

            sage: C = codes.BinaryReedMullerCode(2, 4)
            sage: C.order()
            2
        """
        return self._order

    def number_of_variables(self):
        r"""
        Returns the number of variables of the polynomial ring used in ``self``.

        EXAMPLES::

            sage: C = codes.BinaryReedMullerCode(2, 4)
            sage: C.number_of_variables()
            4
        """
        return self._num_of_var

    def minimum_distance(self):
        r"""
        Returns the minimum distance of ``self``.
        The minimum distance of a binary Reed-Muller code of order $d$ and number of variables $m$ is $q^{m-d}$

        EXAMPLES::

            sage: C = codes.BinaryReedMullerCode(2, 4)
            sage: C.minimum_distance()
            4
        """
        return 2**(self.number_of_variables() - self.order())

    def _repr_(self):
        r"""
        Returns a string representation of ``self``.

        EXAMPLES::

            sage: C = codes.BinaryReedMullerCode(2, 4)
            sage: C
            Binary Reed-Muller Code of order 2 and number of variables 4
        """
        return "Binary Reed-Muller Code of order %s and number of variables %s" % (
            self.order(), self.number_of_variables())

    def _latex_(self):
        r"""
        Returns a latex representation of ``self``.

        EXAMPLES::

            sage: C = codes.BinaryReedMullerCode(2, 4)
            sage: latex(C)
            \textnormal{Binary Reed-Muller Code of order} 2 \textnormal{and number of variables} 4
        """
        return "\\textnormal{Binary Reed-Muller Code of order} %s \\textnormal{and number of variables} %s" % (
            self.order(), self.number_of_variables())

    def __eq__(self, other):
        r"""
        Tests equality between Reed-Muller Code objects.

        EXAMPLES::

            sage: C1 = codes.BinaryReedMullerCode(2, 4)
            sage: C2 = codes.BinaryReedMullerCode(2, 4)
            sage: C1.__eq__(C2)
            True
        """
        return isinstance(other, BinaryReedMullerCode) \
            and self.order() == other.order() \
            and self.number_of_variables() == other.number_of_variables()

    def reed_solomon_supercode(self, p = None):
        r"""
        Returns the Reed Solomon supercode of the given Reed-Muller code.
        The Reed Solomon supercode can be obtained my mapping each element of a vector field `\Bold{F}^m_{q}` to `\Bold{F}_{q^m}`
        via a linear transformation over `\Bold{F}_q` and then using them as evaluation points of Reed-Solomon code. 
        This process gives a supercode of the Reed-Muller code which is a Reed-Solomon code. 

        INPUT::

        - ``p`` -- An irreducible polynomial over the base field of ``code`` of degree same as number of variables used in ``code``.

        EXAMPLES::

            sage: C = codes.ReedMullerCode(GF(2), 2, 5)
            sage: sC = C.reed_solomon_supercode()
            sage: sC
            [32, 32, 1] Generalized Reed-Solomon Code over Finite Field in y of size 2^5

        A polynomial ``p`` can be passed to direct the extension field::

            sage: F = GF(2)
            sage: R.<x> = F[]
            sage: p = x^4 + x + 1
            sage: p.is_irreducible()
            True
            sage: C = codes.ReedMullerCode(F, 2, 4)
            sage: sC = C.reed_solomon_supercode(p)
            sage: sC
            [16, 16, 1] Generalized Reed-Solomon Code over Finite Field in y of size 2^4

        """
        return _reed_solomon_supercode(self, p)




class ReedMullerVectorEncoder(Encoder):
    r"""
    Encoder for Reed-Muller codes which encodes vectors into codewords.

    Consider a Reed-Muller code of order `r`, number of variables `m`, length `n`,
    dimension `k` over some finite field `F`.
    Let those variables be `(x_1, x_2, \dots, x_m)`.
    We order the monomials by lowest power on lowest index variables. If we have three monomials
    `x_1 \times x_2`, `x_1 \times x_2^2` and `x_1^2 \times x_2`, the ordering is:
    `x_1 \times x_2 < x_1 \times x_2^2 < x_1^2 \times x_2`

    Let now `(v_1,v_2,\ldots,v_k)` be a vector of `F`, which corresponds to the polynomial
    `f = \Sigma^{k}_{i=1} v_i \times x_i`.

    Let `(\beta_1, \beta_2, \ldots, \beta_q)` be the elements of `F` ordered as they are
    returned by Sage when calling ``F.list()``.

    The aforementioned polynomial `f` is encoded as:

    `(f(\alpha_{11},\alpha_{12},\ldots,\alpha_{1m}),f(\alpha_{21},\alpha_{22},\ldots,
    \alpha_{2m}),\ldots,f(\alpha_{q^m1},\alpha_{q^m2},\ldots,\alpha_{q^mm}`, with
    `\alpha_{ij}=\beta_{i \ mod \ q^j} \forall (i,j)`

    INPUT:

    - ``code`` -- The associated code of this encoder.

    EXAMPLES::

        sage: C1=codes.ReedMullerCode(GF(2), 2, 4)
        sage: E1=codes.encoders.ReedMullerVectorEncoder(C1)
        sage: E1
        Evaluation vector-style encoder for Binary Reed-Muller Code of order 2 and number of variables 4
        sage: C2=codes.ReedMullerCode(GF(3), 2, 2)
        sage: E2=codes.encoders.ReedMullerVectorEncoder(C2)
        sage: E2
        Evaluation vector-style encoder for Reed-Muller Code of order 2 and 2 variables over Finite Field of size 3

    Actually, we can construct the encoder from ``C`` directly::

        sage: C=codes.ReedMullerCode(GF(2), 2, 4)
        sage: E = C.encoder("EvaluationVector")
        sage: E
        Evaluation vector-style encoder for Binary Reed-Muller Code of order 2 and number of variables 4
    """

    def __init__(self, code):
        r"""
        TESTS:

        If ``code`` is not a Reed-Muller code, an error is raised::

            sage: C  = codes.RandomLinearCode(10, 4, GF(11))
            sage: codes.encoders.ReedMullerVectorEncoder(C)
            Traceback (most recent call last):
            ...
            ValueError: the code has to be a Reed-Muller code
        """
        if not (
            isinstance(
                code,
                QAryReedMullerCode) or isinstance(
                code,
                BinaryReedMullerCode)):
            raise ValueError("the code has to be a Reed-Muller code")
        super(ReedMullerVectorEncoder, self).__init__(code)

    def _repr_(self):
        r"""
        Returns a string representation of ``self``.

        EXAMPLES::

            sage: F = GF(11)
            sage: C = codes.ReedMullerCode(F, 2, 4)
            sage: E=codes.encoders.ReedMullerVectorEncoder(C)
            sage: E
            Evaluation vector-style encoder for Reed-Muller Code of order 2 and 4 variables over Finite Field of size 11
        """
        return "Evaluation vector-style encoder for %s" % self.code()

    def _latex_(self):
        r"""
        Returns a string representation of ``self``.

        EXAMPLES::

            sage: F = GF(11)
            sage: C = codes.ReedMullerCode(F, 2, 4)
            sage: E=codes.encoders.ReedMullerVectorEncoder(C)
            sage: latex(E)
            \textnormal{Evaluation vector-style encoder for }\textnormal{Reed-Muller Code of order} 2 \textnormal{and }4 \textnormal{variables over} \Bold{F}_{11}
        """
        return "\\textnormal{Evaluation vector-style encoder for }%s" % self.code()._latex_()

    def __eq__(self, other):
        r"""
        Tests equality between ReedMullerVectorEncoder objects.

        EXAMPLES::

            sage: F = GF(11)
            sage: C = codes.ReedMullerCode(F, 2, 4)
            sage: D1 = codes.encoders.ReedMullerVectorEncoder(C)
            sage: D2 = codes.encoders.ReedMullerVectorEncoder(C)
            sage: D1.__eq__(D2)
            True
            sage: D1 is D2
            False
        """
        return (isinstance(other, ReedMullerVectorEncoder)
                ) and self.code() == other.code()

    @cached_method
    def generator_matrix(self):
        r"""
        Returns a generator matrix of ``self``

        EXAMPLES::

            sage: F = GF(3)
            sage: C = codes.ReedMullerCode(F, 2, 2)
            sage: E = codes.encoders.ReedMullerVectorEncoder(C)
            sage: E.generator_matrix()
            [1 1 1 1 1 1 1 1 1]
            [0 1 2 0 1 2 0 1 2]
            [0 0 0 1 1 1 2 2 2]
            [0 1 1 0 1 1 0 1 1]
            [0 0 0 0 1 2 0 2 1]
            [0 0 0 1 1 1 1 1 1]
        """
        C = self.code()
        base_field = C.base_field()
        order = C.order()
        num_of_var = C.number_of_variables()
        q = base_field.cardinality()
        dimension = C.dimension()
        points = base_field**num_of_var
        matrix_list = []
        max_individual_degree = min(order, (q - 1))
        for degree in range(order + 1):
            exponents = Subsets(range(num_of_var) * max_individual_degree,
                                degree, submultiset=True)
            matrix_list += [[reduce(mul, [x[i] for i in exponent], 1)
                             for x in points] for exponent in exponents]
        return matrix(base_field, matrix_list)

    def points(self):
        r"""
        Returns the points of $F^m$, where $F$ is base field and $m$ is the number of variables, in order of which polynomials are evaluated on.

        EXAMPLES::

            sage: F = GF(3)
            sage: Fx.<x0,x1> = F[]
            sage: C = codes.ReedMullerCode(F, 2, 2)
            sage: E = C.encoder("EvaluationVector")
            sage: E.points()
            [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1), (0, 2), (1, 2), (2, 2)]
        """
        code = self.code()
        return ((code.base_field())**code.number_of_variables()).list()


class ReedMullerPolynomialEncoder(Encoder):
    r"""
    Encoder for Reed-Muller codes which encodes appropiate multivariate polynomials into codewords.

    Consider a Reed-Muller code of order `r`, number of variables `m`, length `n`,
    dimension `k` over some finite field `F`.
    Let those variables be `(x_1, x_2, \dots, x_m)`.
    We order the monomials by lowest power on lowest index variables. If we have three monomials
    `x_1 \times x_2`, `x_1 \times x_2^2` and `x_1^2 \times x_2`, the ordering is:
    `x_1 \times x_2 < x_1 \times x_2^2 < x_1^2 \times x_2`

    Let now `f` be a polynomial of the multivariate polynomial ring `F[x_1, \dots, x_m]`.

    Let `(\beta_1, \beta_2, \ldots, \beta_q)` be the elements of `F` ordered as they are
    returned by Sage when calling ``F.list()``.

    The aforementioned polynomial `f` is encoded as:

    `(f(\alpha_{11},\alpha_{12},\ldots,\alpha_{1m}),f(\alpha_{21},\alpha_{22},\ldots,
    \alpha_{2m}),\ldots,f(\alpha_{q^m1},\alpha_{q^m2},\ldots,\alpha_{q^mm}`, with
    `\alpha_{ij}=\beta_{i \ mod \ q^j} \forall (i,j)`


    INPUT:

    - ``code`` -- The associated code of this encoder.

    -``polynomial_ring`` -- (default:``None``) The polynomial ring from which the message is chosen.
                            If this is set to ``None``, a polynomial ring in `x` will be built
                            from the code parameters.

    EXAMPLES::

        sage: C1=codes.ReedMullerCode(GF(2), 2, 4)
        sage: E1=codes.encoders.ReedMullerPolynomialEncoder(C1)
        sage: E1
        Evaluation polynomial-style encoder for Binary Reed-Muller Code of order 2 and number of variables 4
        sage: C2=codes.ReedMullerCode(GF(3), 2, 2)
        sage: E2=codes.encoders.ReedMullerPolynomialEncoder(C2)
        sage: E2
        Evaluation polynomial-style encoder for Reed-Muller Code of order 2 and 2 variables over Finite Field of size 3

    We can also pass a predefined polynomial ring::

        sage: R=PolynomialRing(GF(3), 2, 'y')
        sage: C=codes.ReedMullerCode(GF(3), 2, 2)
        sage: E=codes.encoders.ReedMullerPolynomialEncoder(C, R)
        sage: E
        Evaluation polynomial-style encoder for Reed-Muller Code of order 2 and 2 variables over Finite Field of size 3

    Actually, we can construct the encoder from ``C`` directly::

        sage: E = C1.encoder("EvaluationPolynomial")
        sage: E
        Evaluation polynomial-style encoder for Binary Reed-Muller Code of order 2 and number of variables 4
    """

    def __init__(self, code, polynomial_ring=None):
        r"""
        TESTS:

        If ``code`` is not a Reed-Muller code, an error is raised::

            sage: C  = codes.RandomLinearCode(10, 4, GF(11))
            sage: codes.encoders.ReedMullerPolynomialEncoder(C)
            Traceback (most recent call last):
            ...
            ValueError: the code has to be a Reed-Muller code

        If the polynomial ring passed is not according to the requirement (over a different field or different number of variables) then an error is raised::

            sage: F=GF(59)
            sage: R.<x,y,z,w>=F[]
            sage: C=codes.ReedMullerCode(F, 2, 3)
            sage: E=codes.encoders.ReedMullerPolynomialEncoder(C, R)
            Traceback (most recent call last):
            ...
            ValueError: The Polynomial ring should be on Finite Field of size 59 and should have 3 variables
        """
        if not (
            isinstance(code, QAryReedMullerCode)
                or isinstance(code, BinaryReedMullerCode)):
            raise ValueError("the code has to be a Reed-Muller code")
        super(ReedMullerPolynomialEncoder, self).__init__(code)
        if polynomial_ring is None:
            self._polynomial_ring = PolynomialRing(code.base_field(),
                                                   code.number_of_variables(), 'x')
        else:
            if (polynomial_ring.base_ring() == code.base_field()) and (
                    len(polynomial_ring.variable_names()) == code.number_of_variables()):
                self._polynomial_ring = polynomial_ring
            else:
                raise ValueError(
                    "The Polynomial ring should be on %s and should have %s variables" %
                    (code.base_field(), code.number_of_variables()))

    def _repr_(self):
        r"""
        Returns a string representation of ``self``.

        EXAMPLES::

            sage: F = GF(59)
            sage: C = codes.ReedMullerCode(F, 2, 4)
            sage: E=codes.encoders.ReedMullerPolynomialEncoder(C)
            sage: E
            Evaluation polynomial-style encoder for Reed-Muller Code of order 2 and 4 variables over Finite Field of size 59
        """
        return "Evaluation polynomial-style encoder for %s" % self.code()

    def _latex_(self):
        r"""
        Returns a string representation of ``self``.

        EXAMPLES::

            sage: F = GF(59)
            sage: C = codes.ReedMullerCode(F, 2, 4)
            sage: E=codes.encoders.ReedMullerPolynomialEncoder(C)
            sage: latex(E)
            \textnormal{Evaluation polynomial-style encoder for }\textnormal{Reed-Muller Code of order} 2 \textnormal{and }4 \textnormal{variables over} \Bold{F}_{59}
        """
        return "\\textnormal{Evaluation polynomial-style encoder for }%s" % self.code()._latex_()

    def __eq__(self, other):
        r"""
        Tests equality between ReedMullerVectorEncoder objects.

        EXAMPLES::

            sage: F = GF(11)
            sage: C = codes.ReedMullerCode(F, 2, 4)
            sage: D1 = codes.encoders.ReedMullerPolynomialEncoder(C)
            sage: D2 = codes.encoders.ReedMullerPolynomialEncoder(C)
            sage: D1.__eq__(D2)
            True
            sage: D1 is D2
            False
        """
        return isinstance(other, ReedMullerPolynomialEncoder) \
            and self.code() == other.code()

    def encode(self, p):
        r"""
        Transforms the polynomial ``p`` into a codeword of :meth:`code`.

        INPUT:

        - ``p`` -- A polynomial from the message space of ``self`` of degree
          less than ``self.code().order()``.

        OUTPUT:

        - A codeword in associated code of ``self``

        EXAMPLES::

            sage: F = GF(3)
            sage: Fx.<x0,x1> = F[]
            sage: C = codes.ReedMullerCode(F, 2, 2)
            sage: E = C.encoder("EvaluationPolynomial")
            sage: p = x0*x1 + x1^2 + x0 + x1 + 1
            sage: c = E.encode(p); c
            (1, 2, 0, 0, 2, 1, 1, 1, 1)
            sage: c in C
            True

        If a polynomial with good monomial degree but wrong monomial
        degree is given,an error is raised::

            sage: p = x0^2*x1
            sage: E.encode(p)
            Traceback (most recent call last):
            ...
            ValueError: The polynomial to encode must have degree at most 2

        If ``p`` is not an element of the proper polynomial ring, an error is raised::

            sage: Qy.<y1,y2> = QQ[]
            sage: p = y1^2 + 1
            sage: E.encode(p)
            Traceback (most recent call last):
            ...
            ValueError: The value to encode must be in Multivariate Polynomial Ring in x0, x1 over Finite Field of size 3
        """
        M = self.message_space()
        if p not in M:
            raise ValueError("The value to encode must be in %s" % M)
        C = self.code()
        if p.degree() > C.order():
            raise ValueError("The polynomial to encode must have degree at most %s"
                             % C.order())
        base_fieldTuple = Tuples(
            C.base_field().list(), C.number_of_variables())
        return vector(C.base_ring(), [p(x) for x in base_fieldTuple])

    def unencode_nocheck(self, c):
        r"""
        Returns the message corresponding to the codeword ``c``.

        Use this method with caution: it does not check if ``c``
        belongs to the code, and if this is not the case, the output is
        unspecified. Instead, use :meth:`unencode`.

        INPUT:

        - ``c`` -- A codeword of :meth:`code`.

        OUTPUT:

        - An polynomial of degree less than ``self.code().order()``.

        EXAMPLES::

            sage: F = GF(3)
            sage: C = codes.ReedMullerCode(F, 2, 2)
            sage: E = C.encoder("EvaluationPolynomial")
            sage: c = vector(F, (1, 2, 0, 0, 2, 1, 1, 1, 1))
            sage: c in C
            True
            sage: p = E.unencode_nocheck(c); p
            x0*x1 + x1^2 + x0 + x1 + 1
            sage: E.encode(p) == c
            True

        Note that no error is thrown if ``c`` is not a codeword, and that the
        result is undefined::

            sage: c = vector(F, (1, 2, 0, 0, 2, 1, 0, 1, 1))
            sage: c in C
            False
            sage: p = E.unencode_nocheck(c); p
            -x0*x1 - x1^2 + x0 + 1
            sage: E.encode(p) == c
            False

        """
        return _multivariate_polynomial_interpolation(
            c,
            self.code().order(),
            self.polynomial_ring())

    def message_space(self):
        r"""
        Returns the message space of ``self``

        EXAMPLES::

            sage: F = GF(11)
            sage: C = codes.ReedMullerCode(F, 2, 4)
            sage: E = C.encoder("EvaluationPolynomial")
            sage: E.message_space()
            Multivariate Polynomial Ring in x0, x1, x2, x3 over Finite Field of size 11
        """
        return self._polynomial_ring

    def polynomial_ring(self):
        r"""
        Returns the polynomial ring associated with ``self``

        EXAMPLES::

            sage: F = GF(11)
            sage: C = codes.ReedMullerCode(F, 2, 4)
            sage: E = C.encoder("EvaluationPolynomial")
            sage: E.polynomial_ring()
            Multivariate Polynomial Ring in x0, x1, x2, x3 over Finite Field of size 11
        """
        return self._polynomial_ring

    def points(self):
        r"""
        Returns the evaluation points in the appropriate order as used by ``self`` when
        encoding a message.

        EXAMPLES::

            sage: F = GF(3)
            sage: Fx.<x0,x1> = F[]
            sage: C = codes.ReedMullerCode(F, 2, 2)
            sage: E = C.encoder("EvaluationPolynomial")
            sage: E.points()
            [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1), (0, 2), (1, 2), (2, 2)]
        """
        code = self.code()
        return ((code.base_field())**code.number_of_variables()).list()


class BinaryReedMullerMajorityDecoder(Decoder):
    r"""
    Decoder for Binary Reed-Muller codes which uses majority vote
    decoding algorithm to correct errors in codewords.

    The algorithm takes the linear combination of bits of the codewords which would  
    give the same bit of the message symbol if uncorrupted and chooses the majority
    from them to decide the message bit.     

    The decoder corrects the error and returns the message symbol as a vector in
    `\Bold{F}_{2}` as described in :class:`ReedMullerVectorEncoder`. 

    INPUT:

    - ``code`` -- The associated code of this encoder.

    EXAMPLES::

        sage: F = GF(2)
        sage: C = codes.ReedMullerCode(F, 2, 5)
        sage: D = codes.decoders.BinaryReedMullerMajorityDecoder(C)
        sage: D
        Majority vote decoder for Binary Reed-Muller Code of order 2 and number of variables 5

    Actually, we can construct the decoder from ``C`` directly::

        sage: D = C.decoder("MajorityVote")
        sage: D
        Majority vote decoder for Binary Reed-Muller Code of order 2 and number of variables 5
    """

    def __init__(self, code):
        r"""
        TESTS:

        If ``code`` is not a Binary Reed-Muller code, an error is raised::

            sage: C  = codes.RandomLinearCode(10, 4, GF(11))
            sage: codes.decoders.BinaryReedMullerMajorityDecoder(C)
            Traceback (most recent call last):
            ...
            ValueError: code has to be a binary Reed-Muller code
        """
        if not isinstance(code, BinaryReedMullerCode):
            raise ValueError("code has to be a binary Reed-Muller code")
        super(BinaryReedMullerMajorityDecoder, self).__init__(code, code.ambient_space(),
                                                              "EvaluationVector")

    def _repr_(self):
        r"""
        Returns a string representation of ``self``.

        EXAMPLES::

            sage: F = GF(2)
            sage: C = codes.ReedMullerCode(F, 3, 5)
            sage: D = codes.decoders.BinaryReedMullerMajorityDecoder(C)
            sage: D
            Majority vote decoder for Binary Reed-Muller Code of order 3 and number of variables 5
        """
        return "Majority vote decoder for %s" % self.code()

    def _latex_(self):
        r"""
        Returns a latex representation of ``self``.

        EXAMPLES::

            sage: F = GF(2)
            sage: C = codes.ReedMullerCode(F, 3, 5)
            sage: D = codes.decoders.BinaryReedMullerMajorityDecoder(C)
            sage: latex(D)
            \textnormal{Majority vote decoder for }\textnormal{Binary Reed-Muller Code of order} 3 \textnormal{and number of variables} 5
        """
        return "\\textnormal{Majority vote decoder for }%s" % self.code()._latex_()

    def __eq__(self, other):
        r"""
        Tests equality between BinaryReedMullerMajorityDecoder objects.

        EXAMPLES::

            sage: F = GF(2)
            sage: C = codes.ReedMullerCode(F, 2, 6)
            sage: D1 = codes.decoders.BinaryReedMullerMajorityDecoder(C)
            sage: D2 = C.decoder("MajorityVote")
            sage: D1.__eq__(D2)
            True
            sage: D1 is D2
            False
        """
        return isinstance(other, BinaryReedMullerMajorityDecoder) \
            and self.code() == other.code()

    def decode_to_message(self, word):
        r"""
        Decode ``word`` to an element in message space of ``self``

        INPUT:

        - ``word`` -- a codeword of ``self``

        OUTPUT:

        - a vector of ``self`` message space

        EXAMPLES::

            sage: F = GF(2)
            sage: C = codes.ReedMullerCode(F, 2, 5)
            sage: D = codes.decoders.BinaryReedMullerMajorityDecoder(C)
            sage: c = C.random_element()
            sage: Chan = channels.StaticErrorRateChannel(C.ambient_space(), D.decoding_radius())
            sage: y = Chan(c)
            sage: f_dec = D.decode_to_message(y)
            sage: f_dec == D.connected_encoder().unencode(c)
            True

        """
        message = []
        degree = self.code().order()
        num_of_var = self.code().number_of_variables()
        n = word.length()
        F = self.code().base_field()
        one = F.one()
        zero = F.zero()
        total_votes = 1 << (num_of_var - degree)
        while degree >= 0:  # iterating through the degree of monomial
            Sub = Subsets(range(num_of_var), degree)
            subset = Sub.first()
            m = []
            while (True):  # iterating through monomials of degree t
                dict = {}
                mask = _set_to_mask(subset, num_of_var)
                num_of_one = 0
                for i in range(n):
                    key = i - (i & mask)
                    if dict.has_key(key):
                        dict[key] += word[i]
                        if word[i] == one:  # counting number of ones
                            if dict[key] == one:
                                num_of_one += 1
                            else:
                                num_of_one -= 1
                    else:
                        dict[key] = word[i]
                        if word[i] == one:  # counting number of ones
                            num_of_one += 1
                if (2 * num_of_one > total_votes):  # determining majority
                    m.append(one)
                    subset_complement = Set(
                        range(num_of_var)).difference(subset)
                    for s in Subsets(subset_complement):
                        word[_set_to_mask(s, num_of_var) + mask] += one
                else:
                    m.append(zero)
                if (subset == Sub.last()):
                    break
                else:
                    subset = Sub.next(subset)
            message = m + message
            degree -= 1
            total_votes <<= 1
        return vector(F, message)

    def decoding_radius(self):
        r"""
        Returns maximal number of errors that ``self`` can decode.

        OUTPUT:

        - the number of errors as an integer

        EXAMPLES::

            sage: F = GF(2)
            sage: C = codes.ReedMullerCode(F, 2, 5)
            sage: D = codes.decoders.BinaryReedMullerMajorityDecoder(C)
            sage: D.decoding_radius()
            3
        """
        return (self.code().minimum_distance() - 1) // 2


class QAryReedMullerRSDecoder(Decoder):
    r"""
    Decoder for q-ary Reed-Muller codes which decodes by treating them as a 
    sub-code of a Reed Solomon code and uses decoders for the same to correct the errors.

    The decoder corrects the error and returns the message symbol as a vector in `F`,
    where `F` is the base field, as described in :class:`ReedMullerVectorEncoder`. 

    INPUT:

    - ``code`` -- The associated code of this encoder.

    - ``reed_solomon_decoder`` -- (default: ``None``) the decoder that will be used over the reed solomon super code.
      It has to be a decoder object over the Reed Solomon supercode.
      Note that this argument takes precedence over any other argument given in ``kwargs``

    - ``irreducible_polynomial`` -- (default: ``None``) an irreducible polynomial used to extend the base field

    - ``**kwargs`` -- all extra arguments are forwarded to original code's decoder

    EXAMPLES::

        sage: F = GF(3)
        sage: C = codes.ReedMullerCode(F, 2, 3)
        sage: D = codes.decoders.QAryReedMullerRSDecoder(C)
        sage: D
        Reed Solomon based decoder for Reed-Muller Code of order 2 and 3 variables over Finite Field of size 3 that uses Gao decoder for [27, 19, 9] Generalized Reed-Solomon Code over Finite Field in y of size 3^3

    We can also construct the decoder from ``C`` directly.::

        sage: D = C.decoder("ReedSolomon")
        sage: D
        Reed Solomon based decoder for Reed-Muller Code of order 2 and 3 variables over Finite Field of size 3 that uses Gao decoder for [27, 19, 9] Generalized Reed-Solomon Code over Finite Field in y of size 3^3

    We can use other decoders for the Reed-Solomon supercode as well,

        sage: sC = C.reed_solomon_supercode()
        sage: D = codes.decoders.QAryReedMullerRSDecoder(C, sC.decoder("BerlekampWelch"))
        sage: D 
        Reed Solomon based decoder for Reed-Muller Code of order 2 and 3 variables over Finite Field of size 3 that uses Berlekamp-Welch decoder for [27, 19, 9] Generalized Reed-Solomon Code over Finite Field in y of size 3^3

    The decoder also works on binary Reed-Muller codes of order `<2`.

        sage: F = GF(2)
        sage: C = codes.ReedMullerCode(F, 1, 4)
        sage: D = codes.decoders.QAryReedMullerRSDecoder(C)
        sage: D
        Reed Solomon based decoder for Binary Reed-Muller Code of order 1 and number of variables 4 that uses Gao decoder for [16, 9, 8] Generalized Reed-Solomon Code over Finite Field in y of size 2^4

    We can pass a irreducible polynomial to control the way the base field is extended. 

        sage: F = GF(4)
        sage: R.<x> = F[]
        sage: p = x^4 + x^3 + F.gen()*x^2 + x + 1
        sage: p.is_irreducible()
        True
        sage: C = codes.ReedMullerCode(F, 2, 4)
        sage: D = codes.decoders.QAryReedMullerRSDecoder(C, irreducible_polynomial = p)
        sage: D
        Reed Solomon based decoder for Reed-Muller Code of order 2 and 4 variables over Finite Field in z2 of size 2^2 that uses Gao decoder for [256, 129, 128] Generalized Reed-Solomon Code over Univariate Quotient Polynomial Ring in y over Finite Field in z2 of size 2^2 with modulus y^4 + y^3 + z2*y^2 + y + 1

    """

    def __init__(self, code, reed_solomon_decoder=None, irreducible_polynomial=None, **kwargs):
        r"""
        TESTS:

        If ``code`` is not a Reed-Muller code with appropriate order, an error is raised::

            sage: C  = codes.RandomLinearCode(10, 4, GF(11))
            sage: codes.decoders.QAryReedMullerRSDecoder(C)
            Traceback (most recent call last):
            ...
            ValueError: The code must be a Reed-Muller code
        """
        if not isinstance(code, (QAryReedMullerCode, BinaryReedMullerCode)):
            raise ValueError('The code must be a Reed-Muller code')
        if isinstance(code, BinaryReedMullerCode):
            if code.order() > 1:
                raise ValueError(
                    'For binary Reed-Muller codes, the order must be less than 2')
        supercode = code.reed_solomon_supercode(irreducible_polynomial)
        if reed_solomon_decoder is not None:
            if not isinstance(reed_solomon_decoder, Decoder):
                raise TypeError(
                    "reed_solomon_decoder must be a decoder object")
            if not reed_solomon_decoder.code() == supercode:
                raise ValueError(
                    "the decoder must have the reed solomon supercode as it's associated code")
            self._reed_solomon_decoder = reed_solomon_decoder
        else:
            self._reed_solomon_decoder = supercode.decoder(**kwargs)
        self._decoder_type = copy(self._decoder_type)
        self._decoder_type.remove("dynamic")
        self._decoder_type = self._reed_solomon_decoder.decoder_type()
        self._reed_solomon_supercode = supercode
        super(QAryReedMullerRSDecoder, self).__init__(code, code.ambient_space(),
                                                      "EvaluationVector")

    def _repr_(self):
        r"""
        Returns a string representation of ``self``.

        EXAMPLES::

            sage: F = GF(3)
            sage: C = codes.ReedMullerCode(F, 2, 5)
            sage: D = codes.decoders.QAryReedMullerRSDecoder(C)
            sage: D
            Reed Solomon based decoder for Reed-Muller Code of order 2 and 5 variables over Finite Field of size 3 that uses Gao decoder for [243, 163, 81] Generalized Reed-Solomon Code over Finite Field in y of size 3^5
        """
        return "Reed Solomon based decoder for %s that uses %s" % (self.code(), self.reed_solomon_decoder())

    def _latex_(self):
        r"""
        Returns a latex representation of ``self``.

        EXAMPLES::

            sage: F = GF(3)
            sage: C = codes.ReedMullerCode(F, 2, 5)
            sage: D = codes.decoders.QAryReedMullerRSDecoder(C)
            sage: latex(D)
            \textnormal{Reed Solomon based decoder for }\textnormal{Reed-Muller Code of order} 2 \textnormal{and }5 \textnormal{variables over} \Bold{F}_{3}\textnormal{ that uses }\textnormal{Gao decoder for }[243, 163, 81] \textnormal{ Generalized Reed-Solomon Code over } \Bold{F}_{3^{5}}
        """
        return "\\textnormal{Reed Solomon based decoder for }%s\\textnormal{ that uses }%s" % (self.code()._latex_(), self.reed_solomon_decoder()._latex_())

    def __eq__(self, other):
        r"""
        Tests equality between QAryReedMullerRSDecoder objects.

        EXAMPLES::

            sage: F = GF(3)
            sage: C = codes.ReedMullerCode(F, 2, 5)
            sage: D1 = codes.decoders.QAryReedMullerRSDecoder(C)
            sage: D2 = C.decoder("ReedSolomon")
            sage: D1.__eq__(D2)
            True
            sage: D1 is D2
            False

        Note that using a differnt Reed-Solomon decoder would lead to a different QAryReedMullerRSDecoder.

            sage: sC = C.reed_solomon_supercode()
            sage: D3 = codes.decoders.QAryReedMullerRSDecoder(C, sC.decoder("BerlekampWelch"))
            sage: D1.__eq__(D3)
            False
        """
        return isinstance(other, QAryReedMullerRSDecoder) \
            and self.code() == other.code() and self.reed_solomon_decoder() == other.reed_solomon_decoder()

    def decode_to_code(self, word):
        r"""
        Corrects the errors in ``word`` and returns a codeword.

        INPUT:

        - ``word`` -- a vector of the ambient space of ``self.code()``

        OUTPUT:

        - a vector of ``self.code()``

        EXAMPLES::

            sage: F = GF(4)
            sage: C = codes.ReedMullerCode(F, 2, 3)
            sage: D = codes.decoders.QAryReedMullerRSDecoder(C)
            sage: c = C.random_element()
            sage: Chan = channels.StaticErrorRateChannel(C.ambient_space(), D.decoding_radius())
            sage: y = Chan(c)
            sage: c_dec = D.decode_to_code(y)
            sage: c_dec == c
            True

        """
        return self.reed_solomon_decoder().decode_to_code(word)

    def reed_solomon_supercode(self):
        r"""
        Returns the Reed-Solomon supercode the Reed-Muller code is embedded in.

        EXAMPLES::

            sage: F = GF(3)
            sage: C = codes.ReedMullerCode(F, 2, 5)
            sage: D = codes.decoders.QAryReedMullerRSDecoder(C)
            sage: D.reed_solomon_supercode()
            [243, 163, 81] Generalized Reed-Solomon Code over Finite Field in y of size 3^5
        """
        return self._reed_solomon_supercode

    def reed_solomon_decoder(self):
        r"""
        Returns the Reed-Solomon supercode the Reed-Muller code is embedded in.

        EXAMPLES::

            sage: F = GF(3)
            sage: C = codes.ReedMullerCode(F, 2, 5)
            sage: D = codes.decoders.QAryReedMullerRSDecoder(C)
            sage: D.reed_solomon_decoder()
            Gao decoder for [243, 163, 81] Generalized Reed-Solomon Code over Finite Field in y of size 3^5
        """
        return self._reed_solomon_decoder

    def decoding_radius(self, *args, **kwargs):
        r"""
        Returns maximal number of errors that ``self`` can decode.

        OUTPUT:

        - the number of errors as an integer

        EXAMPLES::

            sage: F = GF(3)
            sage: C = codes.ReedMullerCode(F, 2, 5)
            sage: D = codes.decoders.QAryReedMullerRSDecoder(C)
            sage: D.decoding_radius()
            40
        """
        return self.reed_solomon_decoder().decoding_radius(*args, **kwargs)

####################### registration ###############################

QAryReedMullerCode._registered_encoders["EvaluationVector"] = ReedMullerVectorEncoder
QAryReedMullerCode._registered_encoders["EvaluationPolynomial"] = ReedMullerPolynomialEncoder

QAryReedMullerCode._registered_decoders["ReedSolomon"] = QAryReedMullerRSDecoder
QAryReedMullerRSDecoder._decoder_type = {"dynamic"}

BinaryReedMullerCode._registered_encoders["EvaluationVector"] = ReedMullerVectorEncoder
BinaryReedMullerCode._registered_encoders["EvaluationPolynomial"] = ReedMullerPolynomialEncoder

BinaryReedMullerCode._registered_decoders["MajorityVote"] = BinaryReedMullerMajorityDecoder
BinaryReedMullerMajorityDecoder._decoder_type = {"hard-decision", "unique"}
