r"""
Finite Dimensional Lie Algebras With Basis

AUTHORS:

- Travis Scrimshaw (07-15-2013): Initial implementation
"""
#*****************************************************************************
#  Copyright (C) 2013 Travis Scrimshaw <tscrim at ucdavis.edu>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#******************************************************************************

from sage.misc.abstract_method import abstract_method
from sage.misc.cachefunc import cached_method
from sage.categories.category_types import Category_over_base_ring
from sage.categories.finite_dimensional_modules_with_basis import FiniteDimensionalModulesWithBasis
from sage.categories.lie_algebras_with_basis import LieAlgebrasWithBasis
from sage.rings.all import ZZ
from sage.algebras.free_algebra import FreeAlgebra
from sage.algebras.lie_algebras.lie_algebra_element import LieBracket
from sage.sets.family import Family
from sage.matrix.constructor import matrix

class FiniteDimensionalLieAlgebrasWithBasis(Category_over_base_ring):
    """
    Category of finite dimensional Lie algebras with a basis.
    """
    @cached_method
    def super_categories(self):
        """
        EXAMPLES::

            sage: FiniteDimesnionalLieAlgebrasWithBasis(QQ).super_categories()
            [Category of vector spaces over Rational Field]
        """
        return [LieAlgebrasWithBasis(self.base_ring()), FiniteDimensionalModulesWithBasis(self.base_ring())]

    class ParentMethods:
        @cached_method
        def _construct_UEA(self):
            """
            Construct the universal enveloping algebra of ``self``.

            EXAMPLES::

                sage: L.<x,y,z> = LieAlgebra(QQ, {('x','y'):{'z':1}, ('y','z'):{'x':1}, ('z','x'):{'y':1}})
                sage: L._construct_UEA()
            """
            # Create the UEA relations
            # We need to get names for the basis elements, not just the generators
            try:
                names = self.variable_names()
            except ValueError:
                names = tuple('b{}'.format(i) for i in range(self.dimension()))
            I = self._indices
            F = FreeAlgebra(self.base_ring(), names)
            gens = F.gens()
            d = F.gens_dict()
            rels = {}
            S = self.structure_coefficients()
            for k in S.keys():
                g0 = d[names[I.index(k._left)]]
                g1 = d[names[I.index(k._right)]]
                if g0 < g1:
                    rels[g1*g0] = g0*g1 - sum(val*d[g._name] for g, val in S[k])
                else:
                    rels[g0*g1] = g1*g0 + sum(val*d[g._name] for g, val in S[k])
            return F.g_algebra(rels)

        def killing_matrix(self, x, y):
            r"""
            Return the Killing matrix of ``x`` and ``y``.

            The Killing form is defined as the matrix corresponding to the
            action of `\mathrm{ad}_x \circ \mathrm{ad}_y` in the basis
            of ``self``.

            EXAMPLES::

                sage: L.<x,y> = LieAlgebra(QQ, {('x','y'):{'x':1}})
                sage: L.killing_matrix(x, y)
                [ 0  0]
                [-1  0]
            """
            return x.adjoint_matrix() * y.adjoint_matrix()

        def killing_form(self, x, y):
            r"""
            Return the Killing form on ``x`` and ``y``.

            The Killing form is defined as

            .. MATH::

                \langle x \mid y \rangle = \mathrm{tr}\left( \mathrm{ad}_x
                \circ \mathrm{ad}_y \right).
            """
            return self.killing_matrix(x, y).trace()

        @cached_method
        def killing_form_matrix(self):
            """
            Return the matrix of the Killing form of ``self``.
            """
            B = self.basis()
            m = matrix([[self.killing_form(x, y) for x in B] for y in B])
            m.set_immutable()
            return m

        @cached_method
        def structure_coefficients(self):
            """
            Return the non-trivial structure coefficients of ``self``.
            In particular, if `[x, y] = 0`, then we don't include it in the
            output.
            """
            d = {}
            B = self.basis()
            K = self.basis().keys()
            one = self.base_ring().one()
            for i,x in enumerate(K):
                for y in K[i+1:]:
                    bx = B[x]
                    by = B[x]
                    if self._basis_cmp(x, y) > 0:
                        d[LieBracket(y, x)] = self.bracket(by, bx)
                    else:
                        d[LieBracket(x, y)] = self.bracket(bx, by)
            return Family(d)

        def centralizer(self, S):
            """
            Return the centralizer of ``S`` in ``self``.
            """
            from sage.algebras.lie_algebras.subalgebra import LieSubalgebra
            if isinstance(S, LieSubalgebra) or S is self:
                K = S
            else:
                K = self.subalgebra(S)

            m = K.basis_matrix()
            S = self.structure_coefficients()
            sc = {k: S[k].to_vector() for k in S}
            X = self.basis()
            d = self.dimension()
            c_mat = matrix([[sum(r[j]*sc[x,X[j]][k] for j in range(d)) for x in X]
                            for r in m for k in range(d)])
            C = c_mat.right_kernel()
            return self.subalgebra(C) # TODO: convert C back to elements of ``self``

        def center(self):
            """
            Return the center of ``self``.
            """
            return self.centralizer(self)

        def normalizer(self, V):
            """
            Return the normalizer of ``V`` in ``self``.
            """
            from sage.algebras.lie_algebras.subalgebra import LieSubalgebra
            if not isinstance(V, LieSubalgebra) and V is not self:
                V = self.subalgebra(V)

            m = V.basis_matrix()
            S = self.structure_coefficients()
            sc = {k: S[k].to_vector() for k in S}
            X = self.basis()
            d = self.dimension()
            t = m.nrows()
            n_mat = matrix([[sum(r[j]*sc[x,X[j]][k] for j in range(d)) for x in X]
                            + [0]*(t*l) + [m[j][k] for j in range(t)] + [0]*(t*(t-l-1))
                            for l,r in enumerate(m.rows()) for k in range(d)])
            N = n_mat.right_kernel()
            # TODO: convert N back to elements of ``self`` by taking the first ``n`` coefficients
            return self.subalgebra(N)

        def product_space(self, L):
            r"""
            Return the product space ``[self, L]``.

            EXAMPLES::

                sage: L.<x,y> = LieAlgebra(QQ, {('x','y'):{'x':1}})
                sage: Lp = L.product_space(L)
                sage: Lp
                Subalgebra generated of Lie algebra on 2 generators (x, y) over Rational Field with basis:
                (x,)
                sage: Lp.product_space(L)
                Subalgebra generated of Lie algebra on 2 generators (x, y) over Rational Field with basis:
                (x,)
                sage: L.product_space(Lp)
                Subalgebra generated of Lie algebra on 2 generators (x, y) over Rational Field with basis:
                (x,)
                sage: Lp.product_space(Lp)
                Subalgebra generated of Lie algebra on 2 generators (x, y) over Rational Field with basis:
                ()
            """
            # Make sure we lift everything to the ambient space
            try:
                A = self._ambient
            except AttributeError:
                try:
                    A = L._ambient
                except AttributeError:
                    A = self

            B = self.basis()
            LB = L.basis()
            K = B.keys()
            LK = LB.keys()
            # We echelonize the matrix here
            b_mat = matrix(A.base_ring(), [A.bracket(B[a], LB[b]).to_vector()
                                           for a in K for b in LK])
            b_mat.echelonize()
            r = b_mat.rank()
            I = A._ordered_indices
            gens = [A.element_class(A, {I[i]: v for i,v in row.iteritems()})
                    for row in b_mat.rows()[:r]]
            return A.subalgebra(gens)

        @cached_method
        def derived_subalgebra(self):
            """
            Return the derived subalgebra of ``self``.

            EXAMPLES::
            """
            return self.product_space(self)

        @cached_method
        def derived_series(self):
            r"""
            Return the derived series `(\mathfrak{g}^{(i)})_i` of ``self``
            where the rightmost
            `\mathfrak{g}^{(k)} = \mathfrak{g}^{(k+1)} = \cdots`.

            We define the derived series of a Lie algebra `\mathfrak{g}`
            recursively by `\mathfrak{g}^{(0)} := \mathfrak{g}` and

            .. MATH::

                \mathfrak{g}^{(k+1)} =
                [\mathfrak{g}^{(k)}, \mathfrak{g}^{(k)}]

            and recall that
            `\mathfrak{g}^{(k)} \subseteq \mathfrak{g}^{(k+1)}`.
            Alternatively we canexpress this as

            .. MATH::

                \mathfrak{g} \subseteq [\mathfrak{g}, \mathfrak{g}] \subseteq
                \bigl[ [\mathfrak{g}, \mathfrak{g}], [\mathfrak{g},
                \mathfrak{g}] \bigr] \subseteq
                \biggl[ \bigl[ [\mathfrak{g}, \mathfrak{g}], [\mathfrak{g},
                \mathfrak{g}] \bigr], \bigl[ [\mathfrak{g}, \mathfrak{g}],
                [\mathfrak{g}, \mathfrak{g}] \bigr] \biggr] \subseteq \cdots.


            EXAMPLES::

                sage: L.<x,y> = LieAlgebra(QQ, {('x','y'):{'x':1}})
                sage: L.derived_series()
                (Lie algebra on 2 generators (x, y) over Rational Field,
                 Subalgebra generated of Lie algebra on 2 generators (x, y) over Rational Field with basis:
                (x,),
                 Subalgebra generated of Lie algebra on 2 generators (x, y) over Rational Field with basis:
                ())
            """
            L = [self]
            while L[-1].dimension() > 0:
                p = L[-1].derived_subalgebra()
                if L[-1].dimension() == p.dimension():
                    break
                L.append(p)
            return tuple(L)

        @cached_method
        def lower_central_series(self):
            r"""
            Return the lower central series `(\mathfrak{g}_{i})_i`
            of ``self`` where the rightmost
            `\mathfrak{g}_k = \mathfrak{g}_{k+1} = \cdots`.

            We define the lower central series of a Lie algebra `\mathfrak{g}`
            recursively by `\mathfrak{g}_0 := \mathfrak{g}` and

            .. MATH::

                \mathfrak{g}_{k+1} = [\mathfrak{g}, \mathfrak{g}_{k}]

            and recall that `\mathfrak{g}_k} \subseteq \mathfrak{g}_{k+1}`.
            Alternatively we can express this as

            .. MATH::

                \mathfrak{g} \subseteq [\mathfrak{g}, \mathfrak{g}] \subseteq
                \bigl[ [\mathfrak{g}, \mathfrak{g}], \mathfrak{g} \bigr]
                \subseteq\biggl[\bigl[ [\mathfrak{g}, \mathfrak{g}],
                \mathfrak{g} \bigr], \mathfrak{g}\biggr] \subseteq \cdots.

            EXAMPLES::

                sage: L.<x,y> = LieAlgebra(QQ, {('x','y'):{'x':1}})
                sage: L.derived_series()
                (Lie algebra on 2 generators (x, y) over Rational Field,
                 Subalgebra generated of Lie algebra on 2 generators (x, y) over Rational Field with basis:
                (x,))
            """
            L = [self]
            while L[-1].dimension() > 0:
                s = self.product_space(L[-1])
                if L[-1].dimension() == s.dimension():
                    break
                L.append(s)
            return tuple(L)

        @cached_method
        def upper_central_series(self):
            """
            Return the upper central series `(C_i)_i` of ``self``
            where the rightmost `C_k = C_{k+1} = \cdots`.

            EXAMPLES::
            """
            C = [self.center()]
            d = self.dimension()
            while C[-1].dimension() < d:
                s = self.centralizer(self.quotient(C[-1]))
                s = C[-1].product_space(s, self)
                if C[-1].dimension() == s.dimension():
                    break
                C.append(s)
            return tuple(C)

        def hypercenter(self):
            """
            Return the hypercenter of ``self``.
            """
            return upper_central_series()[-1]

        def is_abelian(self):
            """
            Return if ``self`` is an abelian Lie algebra.

            EXAMPLES::

                sage: L.<x,y> = LieAlgebra(QQ, {('x','y'):{'x':1}})
                sage: L.is_abelian()
                False
            """
            return not self.structure_coefficients()

        def is_solvable(self):
            r"""
            Return if ``self`` is a solvable Lie algebra.

            A Lie algebra is solvable if the derived series eventually
            becomes `0`.

            EXAMPLES::

                sage: L.<x,y> = LieAlgebra(QQ, {('x','y'):{'x':1}})
                sage: L.is_abelian()
                False
            """
            return not self.derived_series()[-1].dimension()

        def is_nilpotent(self):
            r"""
            Return if ``self`` is a nilpotent Lie algebra.

            A Lie algebra is nilpotent if the lower central series eventually
            becomes `0`.
            """
            return not self.lower_central_series()[-1].dimension()

        def is_semisimple(self):
            """
            Return if ``self`` if a semisimple Lie algebra.

            A Lie algebra is semisimple if the solvable radical is zero. This
            is equivalent to saying the Killing form is non-degenerate
            (in characteristic 0).
            """
            return not self.killing_form_matrix().is_singular()

        def dimension(self):
            """
            Return the dimension of ``self``.

            EXAMPLES::

                sage: L = LieAlgebra(QQ, 'x,y', {('x','y'): {'x':1}})
                sage: L.dimension()
                2
            """
            return ZZ(len(self.basis()))

    class ElementMethods:
        def to_vector(self):
            """
            Return ``self`` as a vector.
            """
            M = self.parent().free_module()
            if not self:
                return M.zero()
            B = M.basis()
            return M.sum(B[k]*self[k] for k in self.parent()._ordered_indices)

            # I wonder if this is more generic than the above and would
            #   work with combinatorial free modules?
            M = self.parent().free_module()
            if not self:
                return M.zero()
            gd = self.parent().gens_dict()
            basis = self.parent().basis()
            ret = [0]*len(basis)
            # Since we always expand in the basis when bracketing,
            #   the monomials should be basis elements
            for k,c in self:
                ret[basis.index(gd[k._name])] = c
            return M(ret)

        def adjoint_matrix(self): # In #11111 (more or less) by using matrix of a mophism
            """
            Return the matrix of the adjoint action of ``self``.

            EXAMPLES::

                sage: L.<x,y> = LieAlgebra(QQ, {('x','y'):{'x':1}})
                sage: x.adjoint_matrix()
                [1 0]
                [0 0]
                sage: y.adjoint_matrix()
                [ 0  0]
                [-1  0]
            """
            P = self.parent()
            basis = P.basis()
            return matrix([P.bracket(self, b).to_vector() for b in basis])

