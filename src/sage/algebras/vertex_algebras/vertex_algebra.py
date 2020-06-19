r"""
Vertex Algebra

AUTHORS:

- Reimundo Heluani (08-09-2019): Initial implementation.

.. include:: ../../../vertex_algebras/vertex_algebra_desc.inc

EXAMPLES:

The base class for all vertex algebras is :class:`VertexAlgebra`.
All subclasses are called through its method ``__classcall_private__``.
We provide some convenience classes to define named vertex algebras
like :class:`VirasoroVertexAlgebra` and :class:`AffineVertexAlgebra` and
super vertex algebras like :class:`NeveuSchwarzVertexAlgebra` and
:class:`FreeFermionsVertexAlgebra`.

- We create the Universal Virasoro Vertex algebra of central charge
  c=1/2 and perform some basic computations::

    sage: V = VirasoroVertexAlgebra(QQ,1/2); V.inject_variables()
    Defining L
    sage: L*L
    L_-2L_-2|0>
    sage: (L*L).T()
    2*L_-3L_-2|0>+L_-5|0>
    sage: sorted(L.bracket(L*L).items())
    [(0, 2*L_-3L_-2|0>+L_-5|0>),
     (1, 4*L_-2L_-2|0>),
     (2, 3*L_-3|0>),
     (3, 17/2*L_-2|0>),
     (5, 3/2*|0>)]

- We compute its irreducible quotient::

    sage: V.find_singular(6)
    [L_-2L_-2L_-2|0>-33/8*L_-4L_-2|0>+93/64*L_-3L_-3|0>-27/16*L_-6|0>]
    sage: I = V.ideal(_); I
    ideal of The Virasoro vertex algebra of central charge 1/2 over Rational Field generated by (L_-2L_-2L_-2|0> + 93/64*L_-3L_-3|0> - 33/8*L_-4L_-2|0> - 27/16*L_-6|0>,)
    sage: Q = V.quotient(I); Q
    Quotient of The Virasoro vertex algebra of central charge 1/2 over Rational Field by ideal of The Virasoro vertex algebra of central charge 1/2 over Rational Field generated by (L_-2L_-2L_-2|0> + 93/64*L_-3L_-3|0> - 33/8*L_-4L_-2|0> - 27/16*L_-6|0>,)
    sage: Q.retract(L*(L*L))
    -93/64*L_-3L_-3|0> + 33/8*L_-4L_-2|0> + 27/16*L_-6|0>

- We compute the singular support and the classical limit of ``Q``::

    sage: P = Q.singular_support(); P
    Quotient of The classical limit of The Virasoro vertex algebra of central charge 1/2 over Rational Field by the ideal generated by (L2^3,)
    sage: R = Q.classical_limit(); R
    The classical limit of Quotient of The Virasoro vertex algebra of central charge 1/2 over Rational Field by ideal of The Virasoro vertex algebra of central charge 1/2 over Rational Field generated by (L_-2L_-2L_-2|0> + 93/64*L_-3L_-3|0> - 33/8*L_-4L_-2|0> - 27/16*L_-6|0>,)
    sage: P.hilbert_series(10)
    1 + q^2 + q^3 + 2*q^4 + 2*q^5 + 3*q^6 + 3*q^7 + 5*q^8 + 6*q^9 + O(q^10)
    sage: R.hilbert_series(10)
    1 + q^2 + q^3 + 2*q^4 + 2*q^5 + 3*q^6 + 3*q^7 + 5*q^8 + 5*q^9 + O(q^10)

- The result above indicates that ``Q`` is not *classically free*::

    sage: f = R.singular_support_cover; f
    Ring morphism:
      From: Quotient of The classical limit of The Virasoro vertex algebra of central charge 1/2 over Rational Field by the ideal generated by (L2^3,)
      To:   The classical limit of Quotient of The Virasoro vertex algebra of central charge 1/2 over Rational Field by ideal of The Virasoro vertex algebra of central charge 1/2 over Rational Field generated by (L_-2L_-2L_-2|0> + 93/64*L_-3L_-3|0> - 33/8*L_-4L_-2|0> - 27/16*L_-6|0>,)
      Defn: L2 |--> L2
    sage: f.kernel(9)
    Free module generated by {0} over Rational Field
    sage: _.an_element().lift()
    2*L4*L3*L2 + 1/3*L5*L2^2

- We construct the universal Affine vertex algebra for
  `\mathfrak{sl}_3` at level 2 and perform some basic computations::

    sage: V = AffineVertexAlgebra(QQ,'A2',2)
    sage: V.gens()
    (E(alpha[2])_-1|0>,
     E(alpha[1])_-1|0>,
     E(alpha[1] + alpha[2])_-1|0>,
     E(alphacheck[1])_-1|0>,
     E(alphacheck[2])_-1|0>,
     E(-alpha[2])_-1|0>,
     E(-alpha[1])_-1|0>,
     E(-alpha[1] - alpha[2])_-1|0>)
    sage: e = V.gen(0); f = V.gen(7)
    sage: e.bracket(f)
    {0: -E(-alpha[1])_-1|0>}
    sage: e*f
    E(alpha[2])_-1E(-alpha[1] - alpha[2])_-1|0>

- We construct the universal affine vertex algebra for
  `\mathfrak{sl}_2` at level 3 and check that a vector is singular::

    sage: V = AffineVertexAlgebra(QQ,'A1',3)
    sage: V.gens()
    (E(alpha[1])_-1|0>, E(alphacheck[1])_-1|0>, E(-alpha[1])_-1|0>)
    sage: e = V.gen(0)
    sage: e*(e*(e*e))
    E(alpha[1])_-1E(alpha[1])_-1E(alpha[1])_-1E(alpha[1])_-1|0>
    sage: (e*(e*(e*e))).is_singular()
    True

- We construct the classical limit of `V` and check that the
  multiplication is associative in this limit while not in `V`::

    sage: P = V.classical_limit()
    sage: P
    The Poisson vertex algebra quasi-classical limit of The universal affine vertex algebra of CartanType ['A', 1] at level 3
    sage: f = V.gen(2)
    sage: e*(e*f) == (e*e)*f
    False
    sage: e=P(e); e.parent()
    The Poisson vertex algebra quasi-classical limit of The universal affine vertex algebra of CartanType ['A', 1] at level 3
    sage: f=P(f)
    sage: e*(e*f) == (e*e)*f
    True

"""


#******************************************************************************
#       Copyright (C) 2019 Reimundo Heluani <heluani@potuz.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from sage.structure.unique_representation import UniqueRepresentation
from sage.structure.parent import Parent
from sage.categories.commutative_rings import CommutativeRings
from sage.categories.lie_conformal_algebras import LieConformalAlgebras
from sage.categories.vertex_algebras import VertexAlgebras

class VertexAlgebra(UniqueRepresentation):
    @staticmethod
    def __classcall_private__(cls, base_ring=None,
                              lie_conformal_algebra = None,
                              category=None,
                              central_parameters=None,
                              names=None,
                              latex_names=None):

        if base_ring not in CommutativeRings():
            raise ValueError("base_ring must must be a commutative ring, "+
                             "got {}".format(base_ring))

        try:
            if base_ring.has_coerce_map_from(lie_conformal_algebra.base_ring())\
                and lie_conformal_algebra in LieConformalAlgebras(
                    lie_conformal_algebra.base_ring()):
                from .universal_enveloping_vertex_algebra import \
                                                UniversalEnvelopingVertexAlgebra
                return UniversalEnvelopingVertexAlgebra(base_ring,
                        lie_conformal_algebra,
                        category=category,
                        central_parameters=central_parameters,
                        names=names,latex_names=latex_names)
        except AttributeError:
            pass

        raise NotImplementedError("Not Implemented")

    def __init__(self, R, category=None, names=None, latex_names=None):
        r"""Vertex algebras base class and factory

        INPUT:

        - ``base_ring`` -- a commutative ring (default: ``None``); the
          base `ring of this vertex
          algebra. Behaviour is undefined if it is not a field of
          characteristic zero

        - ``lie_conformal_algebra`` a :class:`LieConformalAlgebra` (
          default: ``None``); if specified, this class
          returns the quotient of its universal enveloping vertex
          algebra by the central ideal defined by the parameter
          ``central_parameters``

        - ``central_parameters`` -- A finite family (default: ``None``);
          a family defining a central ideal in the
          universal enveloping vertex algebra of the Lie conformal
          algebra ``lie_conformal_algebra``

        .. NOTE::

          There are several methods of constructing vertex
          algebras. Currently we only support the construction as the
          universal enveloping
          vertex algebra of a Lie conformal algebra, which is best
          achieved by calling
          :meth:`~sage.categories.lie_conformal_algebras.ParentMethods.universal_enveloping_algebra`,
          or as derived constructions like quotients by calling
          :func:`~sage.categories.vertex_algebras.VertexAlgebras.ParentMethods.quotient`.



        EXAMPLES::

            sage: Vir = VirasoroLieConformalAlgebra(CC)
            sage: Vir.inject_variables()
            Defining L, C
            sage: cp = Family({C:1/3})
            sage: V = VertexAlgebra(CC,Vir,central_parameters=cp)
            sage: V
            The universal enveloping vertex algebra of Lie conformal algebra on 2 generators
            (L, C) over Complex Field with 53 bits of precision.

        """
        category = VertexAlgebras(R).or_subcategory(category)
        super(VertexAlgebra, self).__init__(R, names=names,
                                            category = category)
        self._latex_names = latex_names


    def base_ring(self):
        """The base ring of this vertex algebra
        EXAMPLES::

            sage: V = VirasoroVertexAlgebra(QQ,1/2); V
            The Virasoro vertex algebra of central charge 1/2
            sage: V.base_ring()
            Rational Field
        """
        return self.category().base_ring()
