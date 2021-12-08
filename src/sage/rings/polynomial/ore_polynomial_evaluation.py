from sage.rings.morphism import RingMap
from sage.categories.homset import Hom



class OrePolynomialEvaluation(RingMap):

    
    def __init__(self, P, c):
        r"""
        Define the evaluation map for P and c.
        
        TESTS::

            sage: A = GF(5^3)
            sage: Frob = A.frobenius_endomorphism()
            sage: der = A.derivation(A.random_element(), twist = Frob)
            sage: K = OrePolynomialRing(A, der, 'X')
            sage: P = K.random_element(4)
            sage: Q = K.random_element(4)
            sage: c = A.random_element()
            sage: eval = P.eval(c)
            sage: TestSuite(eval).run()
            sage: x = A.random_element()
            sage: y = A.random_element()
            sage: P.eval(c)(x) + Q.eval(c)(x) == (P+Q).eval(c)(x)
            True
            sage: y*(P.eval(c)(x)) == (y*P).eval(c)(x)
            True
            sage: (P*Q).eval(c)(x) == P.eval(c)(Q.eval(c)(x))
            True
            sage: P.hilbert_shift(y).eval(c-y)(x) == P.eval(c)(x)
            True
            
        """
        self.P = P
        self.c = c
        self.coeffs = P.list()
        parent = P.parent()
        self._domain = parent.base_ring()
        RingMap.__init__(self, Hom(self._domain, self._domain))
        if parent.twisting_morphism() is None:
            self._sigma = Hom(self._domain, self._domain).identity()
        else:
            self._sigma = parent.twisting_morphism()
        if parent.twisting_derivation() is None:
            self._derivation = lambda x: 0
        else:
            self._derivation = parent.twisting_derivation()

    def _call_(self, a):
        if len(self.coeffs) == 0:
            return self.P.parent()(0)
        result = self.coeffs[0]*a
        for i in self.coeffs[1:]:
            a = self.c*self._sigma(a) + self._derivation(a)
            result += i * a
        return result

    def _repr_(self):
        n = len(self.coeffs)
        if n == 0:
            s = "Defn:   a |----> 0"
            return s
        if n == 1:
            s += "Defn:   a |----> %s" %(self.coeffs[0])
            return s
        if self.P.parent().twisting_derivation() is None:
            der = ""
        else:
            der = "der"
        if self.c == 0:
            sig = ""
        else:
            if self.P.parent().twisting_derivation() is not None:
                der += " + "
            sig = "%s*sig" %(self.c)
        evc = der + sig
        s = "Ore evaluation endomorphism of %s by the pseudo-linear morphism "%(self.P) + evc + " with :"
        if self.P.parent().twisting_derivation() is not None:
            s += "\n der is %s" %(self._derivation)
        if self.c != 0:
            s += "\n sig is %s" %(self._sigma)
        s += "\n Defn:   a |----> "
        if n == 0:
            s += "0"
            return s
        if n == 1:
            s += "%s" %(self.coeffs[0])
            return s
        for i in reversed(self.coeffs):
            n -= 1
            if n > 1:
                if i == 1:
                    s += "(" + evc + ")^%s(a) + " %(n)
                elif i != 0:
                    s += "%s*(" %(i) + evc + ")^%s(a) + " %(n)
            elif n == 1:
                if i == 1:
                    s += "(" + evc + ")(a) + "
                elif i != 0:
                    s += "%s*(" %(i) + evc + ")(a) + "
            elif n == 0:
                if i != 0:
                    s += "%s*a+ " %(i)
        s = s[:-2]
        return s

    #def _update_slots(self):
        
    def _hash_(self):
        return hash((self.P.parent(), self.P, self.c))
    
    def _repr_short(self):
        if self.P.parent().twisting_derivation() is None:
            der = ""
        else:
            der = "der"
        if self.c == 0:
            sig = ""
        else:
            if self.P.parent().twisting_derivation() is not None:
                der += " + "
            sig = "%s*sig" %(self.c)
        evc = der + sig
        s = "a |----> "
        n = len(self.coeffs)
        if n == 0:
            s += "0"
            return s
        if n == 1:
            s += "%s" %(self.coeffs[0])
            return s
        for i in reversed(self.coeffs):
            n -= 1
            if n > 1:
                if i == 1:
                    s += "(" + evc + ")^%s(a) + " %(n)
                elif i != 0:
                    s += "%s*(" %(i) + evc + ")^%s(a) + " %(n)
            elif n == 1:
                if i == 1:
                    s += "(" + evc + ")(a) + "
                elif i != 0:
                    s += "%s*(" %(i) + evc + ")(a) + "
            elif n == 0:
                if i != 0:
                    s += "%s*a+ " %(i)
        s = s[:-2]
        return s
  
    def _latex_(self):
        r"""
        EXAMPLES::
        
            sage: A = GF(5^2)
            sage: A.<t> = A[]
            sage: A = A.fraction_field()
            sage: der = A.derivation()
            sage: K = OrePolynomialRing(A, der, 'X')
            sage: x = K.gen()
            sage: (x.eval(t+1))._latex_()
            'ev_{t + 1}(X)'

        """
        return "ev_{%s}(%s)" %(self.c._latex_(), self.P._latex_())
