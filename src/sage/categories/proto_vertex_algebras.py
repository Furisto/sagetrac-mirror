r"""
Proto Vertex Algebras

AUTHORS:

- Reimundo Heluani (2020-08-26): Initial implementation.
"""
#******************************************************************************
#       Copyright (C) 2020 Reimundo Heluani <heluani@potuz.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from .category_types import Category_over_base_ring
from .lambda_bracket_algebras import LambdaBracketAlgebras
from sage.misc.abstract_method import abstract_method
from sage.misc.cachefunc import cached_method
from sage.categories.commutative_rings import CommutativeRings
from sage.misc.lazy_import import LazyImport
from sage.functions.other import factorial
from sage.categories.quotients import QuotientsCategory
from sage.rings.all import ZZ
_CommutativeRings = CommutativeRings()


class ProtoVertexAlgebras(Category_over_base_ring):
    r"""
    The category of proto vertex algebras.

    This is an abstract base category for vertex algebras and super
    vertex algebras.
    """
    @staticmethod
    def __classcall_private__(cls, R, check=True):
        r"""
        INPUT:

        - `R` -- a commutative ring
        - ``check`` -- a boolean (default: ``True``); whether to check
          that `R` is a commutative ring

        EXAMPLES::

            sage: VertexAlgebras(QuaternionAlgebra(2))
            Traceback (most recent call last):
            ValueError: base must be a commutative ring got Quaternion Algebra (-1, -1) with base ring Rational Field
            sage: VertexAlgebras(ZZ)
            Category of vertex algebras over Integer Ring
        """
        if check:
            if not (R in _CommutativeRings):
                    raise ValueError("base must be a commutative ring got {}".format(R))
        return super(ProtoVertexAlgebras, cls).__classcall__(cls, R)

    @cached_method
    def super_categories(self):
        """
        The list of super categories of this category.

        EXAMPLES::

            sage: from sage.categories.proto_vertex_algebras import ProtoVertexAlgebras
            sage: ProtoVertexAlgebras(QQ).super_categories()
            [Category of Lambda bracket algebras over Rational Field]
        """
        return [LambdaBracketAlgebras(self.base_ring())]

    def _repr_object_names(self):
        """
        The name of the objects of this category.

        EXAMPLES::

            sage: from sage.categories.proto_vertex_algebras import ProtoVertexAlgebras
            sage: ProtoVertexAlgebras(QQ)
            Category of proto vertex algebras over Rational Field
        """
        return "proto vertex algebras over {}".format(self.base_ring())

    class SubcategoryMethods:

        def FinitelyGeneratedAsProtoVertexAlgebra(self):
            """
            The category of finitely generated proto vertex algebras.

            EXAMPLES::

                sage: VertexAlgebras(QQ).FinitelyGenerated()
                Category of finitely generated vertex algebras over Rational Field
            """
            return self._with_axiom("FinitelyGeneratedAsProtoVertexAlgebra")

        def FinitelyGenerated(self):
            """
            The category of finitely generated proto vertex algebras.

            EXAMPLES::

                sage: VertexAlgebras(QQ).FinitelyGenerated()
                Category of finitely generated vertex algebras over Rational Field
            """
            return self._with_axiom("FinitelyGeneratedAsProtoVertexAlgebra")

    class ParentMethods:
        
        @abstract_method(optional=True)
        def arc_algebra(self):
            r"""
            The arc algebra of this vertex algebra.

            The graded Poisson vertex algebra freely generated
            as a differential algebra by the `C_2` quotient of this
            vertex algebra.

            .. TODO::

                We only support arc algebras of universal enveloping
                vertex algebras and their quotients.

            EXAMPLES:

            Let us prove that the simple N=1 super vertex algebra at
            level `7/10` is not classically free. We start by
            computing the irreducible quotient, its arc algebra
            and its classical limit::

                sage: V = vertex_algebras.NeveuSchwarz(QQ,7/10)
                sage: Q = V.quotient(V.ideal(V.find_singular(4)))
                sage: P = Q.classical_limit()
                sage: R = Q.arc_algebra()
                sage: R
                Quotient of The classical limit of The Neveu-Schwarz super vertex algebra of central charge 7/10 over Rational Field by the ideal generated by (L_2^2,)
                sage: P
                The classical limit of Quotient of The Neveu-Schwarz super vertex algebra of central charge 7/10 over Rational Field by the ideal generated by (L_-2L_-2|0> - 3/2*G_-5/2G_-3/2|0> + 3/10*L_-4|0>,)

            We now check that the arc algebra properly surjects
            onto the classical limit::

                sage: R.hilbert_series(5)
                1 + q^(3/2) + q^2 + q^(5/2) + q^3 + 2*q^(7/2) + 2*q^4 + 3*q^(9/2) + O(q^5)
                sage: P.hilbert_series(5)
                1 + q^(3/2) + q^2 + q^(5/2) + q^3 + 2*q^(7/2) + 2*q^4 + 2*q^(9/2) + O(q^5)

            We compute a vector in the kernel of the projection::

                sage: P.arc_algebra_cover
                Ring morphism:
                  From: Quotient of The classical limit of The Neveu-Schwarz super vertex algebra of central charge 7/10 over Rational Field by the ideal generated by (L_2^2,)
                  To:   The classical limit of Quotient of The Neveu-Schwarz super vertex algebra of central charge 7/10 over Rational Field by the ideal generated by (L_-2L_-2|0> - 3/2*G_-5/2G_-3/2|0> + 3/10*L_-4|0>,)
                  Defn: L_2 |--> L_2
                        G_3/2 |--> G_3/2
                sage: K = P.arc_algebra_cover.kernel(9/2)
                sage: v= K.an_element().lift(); v
                2*L_3*G_3/2 - 8/3*L_2*G_5/2

            We check that indeed this vector vanishes in the classical
            limit of the quotient by showing that it is equivalent to
            a vector deeper in the Li filtration::

                sage: v.lift()
                2*L_3*G_3/2 - 8/3*L_2*G_5/2
                sage: v.lift().parent()
                The classical limit of The Neveu-Schwarz super vertex algebra of central charge 7/10 over Rational Field
                sage: w = v.lift().lift(); w
                2*L_-3G_-3/2|0> - 8/3*L_-2G_-5/2|0>
                sage: w.parent()
                The Neveu-Schwarz super vertex algebra of central charge 7/10 over Rational Field
                sage: t = Q.retract(w); t
                -16/5*G_-9/2|0>
                sage: t.li_filtration_degree()
                3
                sage: w.li_filtration_degree()
                1
            """
            raise NotImplementedError("arc_algebra is not implemented "\
                                      "for {}".format(self))

        @abstract_method(optional=True)
        def ideal(self, *gens):
            """
            The ideal of this vertex algebra generated by ``gens``.

            INPUT:

            - ``gens`` -- a list or tuple of elements of this vertex
              algebra.

            EXAMPLES:

            We construct the ideal defining the *Virasoro Ising*
            module::

                sage: V = vertex_algebras.Virasoro(QQ,1/2)
                sage: L = V.0
                sage: v = L*(L*L) + 93/64*L.T()*L.T() - 33/16*L.T(2)*L - 9/128*L.T(4)
                sage: I = V.ideal(v)
                sage: I
                ideal of The Virasoro vertex algebra of central charge 1/2 over Rational Field generated by (L_-2L_-2L_-2|0> + 93/64*L_-3L_-3|0> - 33/8*L_-4L_-2|0> - 27/16*L_-6|0>,)
            """
            raise NotImplementedError("ideals of {} are not implemented yet"\
                                        .format(self))

        @abstract_method(optional=True)
        def quotient(self, I, names=None):
            """
            The quotient of this vertex algebra by the ideal ``I``.

            INPUT:

            - ``I`` -- a
              :class:`~sage.algebras.vertex_algebras.vertex_algebra_ideal.VertexAlgebraIdeal`
            - ``names`` a list of ``str`` or ``None``
              (default: ``None``); alternative names for the generators

            EXAMPLES::

                sage: V = vertex_algebras.Virasoro(QQ,1/2)
                sage: L = V.0
                sage: v = L*(L*L) + 93/64*L.T()*L.T() - 33/16*L.T(2)*L - 9/128*L.T(4)
                sage: I = V.ideal(v)
                sage: Q = V.quotient(I); Q
                Quotient of The Virasoro vertex algebra of central charge 1/2 over Rational Field by the ideal generated by (L_-2L_-2L_-2|0> + 93/64*L_-3L_-3|0> - 33/8*L_-4L_-2|0> - 27/16*L_-6|0>,)
                sage: Q(L*(L*L))
                -93/64*L_-3L_-3|0> + 33/8*L_-4L_-2|0> + 27/16*L_-6|0>
            """
            raise NotImplementedError("quotients of {} are not implemented yet"\
                                        .format(self))

        def classical_limit(self):
            """
            The Poisson vertex algebra classical limit of this vertex
            algebra.

            EXAMPLES:

            We construct the classical limit of the universal Virasoro
            vertex algebra of central charge `1/2`::

                sage: V = vertex_algebras.Virasoro(QQ, 1/2)
                sage: P = V.classical_limit()
                sage: V.inject_variables()
                Defining L
                sage: (L*L)*L == L*(L*L)
                False
                sage: (P(L)*P(L))*P(L) == P(L)*(P(L)*P(L))
                True
                sage: L.bracket(L)
                {0: L_-3|0>, 1: 2*L_-2|0>, 3: 1/4*|0>}
                sage: P(L).bracket(P(L))
                {}

            We construct the classical limit of the *Ising* model::

                sage: V = vertex_algebras.Virasoro(QQ,1/2); L = V.0
                sage: v = L*(L*L) + 93/64*L.T()*L.T() - 33/16*L.T(2)*L - 9/128*L.T(4)
                sage: Q = V.quotient(V.ideal(v)); P = Q.classical_limit()
                sage: L*(L*L)
                L_-2L_-2L_-2|0>
                sage: Q(L)*(Q(L)*Q(L))
                -93/64*L_-3L_-3|0> + 33/8*L_-4L_-2|0> + 27/16*L_-6|0>
                sage: P(Q(L))*(P(Q(L))*P(Q(L)))
                0

            We check that multiplication is not associative on the
            Free Boson but it is associative in its classical limit::

                sage: V = vertex_algebras.FreeBosons(QQ); P = V.classical_limit()
                sage: V.inject_variables()
                Defining alpha
                sage: (alpha*alpha)*alpha - alpha*(alpha*alpha)
                2*alpha_-3|0>
                sage: a = P(alpha)
                sage: (a*a)*a - a*(a*a)
                0
            """
            from sage.algebras.poisson_vertex_algebras.poisson_vertex_algebra \
                 import PoissonVertexAlgebra
            return PoissonVertexAlgebra(self.base_ring(), self)

        @abstract_method
        def vacuum(self):
            """
            The vacuum vector of this vertex algebra.

            EXAMPLES::

                sage: V = vertex_algebras.Virasoro(QQ, 3)
                sage: V.vacuum()
                |0>
            """

        @abstract_method
        def zero(self):
            """
            The zero vector in this vertex algebra.

            EXAMPLES::

                sage: V = vertex_algebras.Virasoro(QQ, 1/2); V.register_lift(); L = V.0
                sage: v = L*(L*L) + 93/64*L.T()*L.T() - 33/16*L.T(2)*L - 9/128*L.T(4)
                sage: Q = V.quotient(V.ideal(v))
                sage: Q(0)
                0
                sage: V(0)
                0
                sage: V(0) == V.zero()
                True
                sage: Q(0) == Q.zero()
                True
            """

        def central_charge(self):
            """
            The central charge of this vertex algebra.

            EXAMPLES::

                sage: V = vertex_algebras.Virasoro(QQ, 1/2)
                sage: V.central_charge()
                1/2
                sage: B = vertex_algebras.FreeBosons(QQ, 5)
                sage: B.central_charge()
                5
                sage: F = vertex_algebras.FreeFermions(QQ,5)
                sage: F.central_charge()
                5/2
                sage: V = vertex_algebras.Affine(QQ, 'B3', 1)
                sage: V.central_charge()
                7/2
            """
            try:
                return self._c
            except AttributeError:
                raise NotImplementedError("the central charge of {} is not "\
                                          "implemented".format(self))

        def is_graded(self):
            """
            If this vertex algebra is H-Graded.

            EXAMPLES::

                sage: V = vertex_algebras.Virasoro(QQ, 3)
                sage: V.is_graded()
                True
                sage: W = vertex_algebras.Affine(QQ, 'A1', 1)
                sage: W.is_graded()
                True
            """
            return self in ProtoVertexAlgebras(self.base_ring()).Graded()

    class ElementMethods:

        def _nproduct_(self,rhs,n):
            r"""
            The ``n``-th product of these two elements.

            EXAMPLES::

                sage: V = vertex_algebras.Virasoro(QQ,1/2); L = V.0
                sage: L.nproduct(L,3)
                1/4*|0>
                sage: L.nproduct(L,-3)
                L_-4L_-2|0>
            """
            if n not in ZZ:
                raise ValueError("n must be an integer number")
            if n >= 0:
                return self._bracket_(rhs).get(n,self.parent().zero())
            else:
                return self.T(-n-1)._mul_(rhs)/factorial(-1-n)

        @abstract_method(optional=True)
        def li_filtration_degree(self):
            """
            The smallest space `F^p` in the Li filtration of this
            vertex algebra containing this element.

            EXAMPLES::

                sage: V = vertex_algebras.Virasoro(QQ,1/2); L = V.0
                sage: L.li_filtration_degree()
                0
                sage: (L.T(2)*L.T()).li_filtration_degree()
                3
            """
    WithBasis = LazyImport("sage.categories.proto_vertex_algebras_with_basis",
                           "ProtoVertexAlgebrasWithBasis", "WithBasis")

    FinitelyGeneratedAsProtoVertexAlgebra = LazyImport(
        'sage.categories.finitely_generated_proto_vertex_algebras',
        'FinitelyGeneratedProtoVertexAlgebras')

    Graded = LazyImport("sage.categories.graded_proto_vertex_algebras",
                        "GradedProtoVertexAlgebras", "Graded")

    class Quotients(QuotientsCategory):
        """
        The category of quotients of proto vertex algebras.

        This is an abstract base category for quotients of vertex and
        super vertex algebras.

        EXAMPLES::

            sage: VertexAlgebras(QQbar).Quotients()
            Category of quotients of vertex algebras over Algebraic Field
        """
        def example(self):
            """
            An example parent in this category.

            EXAMPLES::

                sage: VertexAlgebras(QQbar).Quotients().example()
                Quotient of The universal affine vertex algebra of CartanType ['A', 1] at level 1 over Algebraic Field by the ideal generated by (e_-1e_-1|0>, e_-1f_-1|0> + e_-2|0>, f_-1f_-1|0> - 2*e_-1h_-1|0> + f_-2|0>, f_-1h_-1|0> + h_-2|0>, h_-1h_-1|0>)
            """
            from sage.algebras.vertex_algebras.affine_vertex_algebra import \
                                                            AffineVertexAlgebra
            V = AffineVertexAlgebra(self.base_ring(), 'A1', 1,
                                    names=('e','f', 'h'))
            return V.quotient(V.ideal(V.find_singular(2)))

        class ParentMethods:

            @abstract_method
            def defining_ideal(self):
                """
                The defining ideal of this quotient.

                EXAMPLES::

                    sage: V = vertex_algebras.Virasoro(QQ,1/2)
                    sage: Q = V.quotient(V.ideal(V.find_singular(6)))
                    sage: Q.defining_ideal()
                    ideal of The Virasoro vertex algebra of central charge 1/2 over Rational Field generated by (L_-2L_-2L_-2|0> + 93/64*L_-3L_-3|0> - 33/8*L_-4L_-2|0> - 27/16*L_-6|0>,)

                    sage: V = vertex_algebras.Affine(QQ, 'A1', 1, names = ('e','h','f'));
                    sage: Q = V.quotient(V.ideal(V.find_singular(2)))
                    sage: Q.defining_ideal()
                    ideal of The universal affine vertex algebra of CartanType ['A', 1] at level 1 over Rational Field generated by (e_-1e_-1|0>, e_-1h_-1|0> + e_-2|0>, h_-1h_-1|0> - 2*e_-1f_-1|0> + h_-2|0>, h_-1f_-1|0> + f_-2|0>, f_-1f_-1|0>)
                """

            @abstract_method
            def cover_algebra(self):
                """
                The covering vertex algebra of this quotient.

                EXAMPLES::

                    sage: V = vertex_algebras.NeveuSchwarz(QQ,7/10); V.register_lift()
                    sage: Q = V.quotient(V.ideal(V.find_singular(4)))
                    sage: I = Q.defining_ideal()
                    sage: I.gens()
                    (L_-2L_-2|0> - 3/2*G_-5/2G_-3/2|0> + 3/10*L_-4|0>,)
                    sage: Q.cover_algebra()
                    The Neveu-Schwarz super vertex algebra of central charge 7/10 over Rational Field
                    sage: Q.cover_algebra() is V
                    True
                """

            def ambient(self):
                """
                The covering vertex algebra of this quotient.

                EXAMPLES::

                    sage: V = vertex_algebras.NeveuSchwarz(QQ,7/10)
                    sage: Q = V.quotient(V.ideal(V.find_singular(4)))
                    sage: I = Q.defining_ideal()
                    sage: I.gens()
                    (L_-2L_-2|0> - 3/2*G_-5/2G_-3/2|0> + 3/10*L_-4|0>,)
                    sage: Q.cover_algebra()
                    The Neveu-Schwarz super vertex algebra of central charge 7/10 over Rational Field
                    sage: Q.cover_algebra() is V
                    True
                """
                return self.cover_algebra()

            def _an_element_(self):
                """
                An element of this quotient.

                EXAMPLES::

                    sage: V = vertex_algebras.NeveuSchwarz(QQ,7/10)
                    sage: Q = V.quotient(V.ideal(V.find_singular(4)));
                    sage: Q.an_element()
                    |0> + 2*G_-3/2|0> + 3*L_-2|0> + L_-2G_-3/2|0>
                """
                return self.retract(self.cover_algebra()._an_element_())

            @cached_method
            def zero(self):
                """
                The zero element of this quotient.

                EXAMPLES::

                    sage: V = vertex_algebras.Virasoro(QQ,1/2)
                    sage: Q = V.quotient(V.ideal(V.find_singular(6)))
                    sage: Q.zero()
                    0

                TESTS::

                    sage: Q.zero() == Q.retract(V.zero())
                    True
                """
                return self.retract(self.cover_algebra().zero())

            @cached_method
            def vacuum(self):
                """
                The vacuum vector of this quotient.

                EXAMPLES::

                    sage: V = vertex_algebras.Affine(QQ, 'A1', 1); V.register_lift()
                    sage: Q = V.quotient(V.ideal(V.find_singular(2)))
                    sage: Q.vacuum()
                    |0>
                """
                return self.retract(self.cover_algebra().vacuum())

        class ElementMethods:

            @abstract_method
            def lift(self):
                """
                Lift this element to the cover vertex algebra.

                EXAMPLES::

                    sage: V = vertex_algebras.Affine(QQ, 'A1', 1, names = ('e','h','f'))
                    sage: Q = V.quotient(V.ideal(V.find_singular(2)))
                    sage: v = Q.an_element(); v
                    |0> + 2*e_-1|0> + 3*h_-1|0> + e_-2|0>
                    sage: v.lift()
                    |0> + 2*e_-1|0> + 3*h_-1|0> + e_-2|0>
                    sage: v.lift().parent()
                    The universal affine vertex algebra of CartanType ['A', 1] at level 1 over Rational Field
                """

            def is_even_odd(self):
                r"""
                Return `0` if this element is *even* and `1` if it is
                *odd*.

                EXAMPLES::

                    sage: V = vertex_algebras.NeveuSchwarz(QQ,7/10)
                    sage: Q = V.quotient(V.ideal(V.find_singular(4)))
                    sage: Q.inject_variables()
                    Defining L, G
                    sage: L.is_even_odd()
                    0
                    sage: G.is_even_odd()
                    1
                """
                return self.lift().is_even_odd()
