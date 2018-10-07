"""
Neighbors
"""
from __future__ import print_function

from sage.modules.free_module_element import vector
from sage.rings.integer_ring import ZZ
from sage.rings.all import GF
from copy import deepcopy
from sage.quadratic_forms.extras import extend_to_primitive
from sage.matrix.constructor import matrix
#from sage.quadratic_forms.quadratic_form import QuadraticForm    ## This creates a circular import! =(


####################################################################################
## Routines used for understanding p-neighbors, and computing classes in a genus. ##
####################################################################################


def find_primitive_p_divisible_vector__random(self, p):
    """
    Finds a random `p`-primitive vector in `L/pL` whose value is `p`-divisible.

    .. note::

        Since there are about `p^{(n-2)}` of these lines, we have a `1/p`
        chance of randomly finding an appropriate vector.

    .. warning::

        If there are local obstructions for this to happen, then this algorithm
        will never terminate... =(  We should check for this too!

    EXAMPLES::

        sage: Q = QuadraticForm(ZZ, 2, [10,1,4])
        sage: Q.find_primitive_p_divisible_vector__random(5)    # random
        (1, 1)
        sage: Q.find_primitive_p_divisible_vector__random(5)    # random
        (1, 0)
        sage: Q.find_primitive_p_divisible_vector__random(5)    # random
        (2, 0)
        sage: Q.find_primitive_p_divisible_vector__random(5)    # random
        (2, 2)
        sage: Q.find_primitive_p_divisible_vector__random(5)    # random
        (3, 3)
        sage: Q.find_primitive_p_divisible_vector__random(5)    # random
        (3, 3)
        sage: Q.find_primitive_p_divisible_vector__random(5)    # random
        (2, 0)

    """
    n = self.dim()
    v = vector([ZZ.random_element(p)  for i in range(n)])

    ## Repeatedly choose random vectors, and evaluate until the value is p-divisible.
    while True:
        if (self(v) % p == 0) and (v != 0):
            return v
        else:
            v[ZZ.random_element(n)] = ZZ.random_element(p)      ## Replace a random entry and try again.




#def find_primitive_p_divisible_vector__all(self, p):
#    """
#    Finds all random p-primitive vectors (up to scaling) in L/pL whose
#    value is p-divisible.
#
#    Note: Since there are about p^(n-2) of these lines, we should avoid this for large n.
#    """
#    pass


def find_primitive_p_divisible_vector__next(self, p, v=None):
    """
    Finds the next `p`-primitive vector (up to scaling) in `L/pL` whose
    value is `p`-divisible, where the last vector returned was `v`.  For
    an initial call, no `v` needs to be passed.

    Returns vectors whose last non-zero entry is normalized to 0 or 1 (so no
    lines are counted repeatedly).  The ordering is by increasing the
    first non-normalized entry.  If we have tested all (lines of)
    vectors, then return None.

    OUTPUT:

        vector or None

    EXAMPLES::

        sage: Q = QuadraticForm(ZZ, 2, [10,1,4])
        sage: v = Q.find_primitive_p_divisible_vector__next(5); v
        (1, 1)
        sage: v = Q.find_primitive_p_divisible_vector__next(5, v); v
        (1, 0)
        sage: v = Q.find_primitive_p_divisible_vector__next(5, v); v


    """
    ## Initialize
    n = self.dim()
    if v is None:
        w = vector([ZZ(0) for i in range(n-1)] + [ZZ(1)])
    else:
        w = deepcopy(v)


    ## Handle n = 1 separately.
    if n <= 1:
        raise RuntimeError("Sorry -- Not implemented yet!")


    ## Look for the last non-zero entry (which must be 1)
    nz = n - 1
    while w[nz] == 0:
        nz += -1

    ## Test that the last non-zero entry is 1 (to detect tampering).
    if w[nz] != 1:
        print("Warning: The input vector to QuadraticForm.find_primitive_p_divisible_vector__next() is not normalized properly.")



    ## Look for the next vector, until w == 0
    while True:


        ## Look for the first non-maximal (non-normalized) entry
        ind = 0
        while (ind < nz) and (w[ind] == p-1):
            ind += 1

        ## Increment
        if (ind < nz):
            w[ind] += 1
            for j in range(ind):
                w[j] = 0
        else:
            for j in range(ind+1):    ## Clear all entries
                w[j] = 0

            if nz != 0:               ## Move the non-zero normalized index over by one, or return the zero vector
                w[nz-1] = 1
                nz += -1


        ## Test for zero vector
        if w == 0:
            return None

        ## Test for p-divisibility
        if (self(w) % p == 0):
            return w


def neighbor_from_vec(self, p, y):
    r"""
    """
    p = ZZ(p)
    if not (p).divides(self(y)):
        raise ValueError("v=%s must be of square divisible by p^2=%s"%(v,p))
    n = self.dim()
    G = self.Hessian_matrix()

    q = y*G*y
    if not q % p == 0:
        raise ValueError("")
    if q % p**2 != 0:
        for k in range(n):
            w = y*G
            if w[k] % p != 0:
                z = (ZZ**n).gen(k)
                break
        z *= (2*y*G*z).inverse_mod(p)
        y = y - q*z
    if p == 2:
        raise NotImplementedError("")

    w = G*y
    Ly = w.change_ring(GF(p)).column().kernel().matrix().lift()
    B = Ly.stack(p*matrix.identity(n)) #??
    B = y.row().stack(p*B)

    B = B.hermite_form()[:n, :] / p
    assert B.det().abs() == 1
    QuadraticForm = type(self)
    Gnew = (B*G*B.T).change_ring(ZZ)
    return QuadraticForm(Gnew)

def p_neighbor(self, p):
    r"""
    """
    v = self.find_primitive_p_divisible_vector__next(p)
    return self.find_p_neighbor_from_vec(p, v)

## ----------------------------------------------------------------------------------------------

def find_p_neighbor_from_vec(self, p, v):
    r"""
    Finds the `p`-neighbor of this quadratic form associated to a given
    vector `v` satisfying:

    #. `Q(v) = 0  \pmod p`
    #. `v` is a non-singular point of the conic `Q(v) = 0 \pmod p`.

    Reference:  Gonzalo Tornaria's Thesis, Thrm 3.5, p34.

    EXAMPLES::

        sage: Q = DiagonalQuadraticForm(ZZ,[1,1,1,1])
        sage: v = vector([0,2,1,1])
        sage: X = Q.find_p_neighbor_from_vec(3,v); X
        Quadratic form in 4 variables over Integer Ring with coefficients:
        [ 3 10 0 -4 ]
        [ * 9 0 -6 ]
        [ * * 1 0 ]
        [ * * * 2 ]
    """
    R = self.base_ring()
    n = self.dim()
    B2 = self.matrix()

    ## Find a (dual) vector w with B(v,w) != 0 (mod p)
    v_dual = B2 * vector(v)     ## We want the dot product with this to not be divisible by 2*p.
    y_ind = 0
    while ((y_ind < n) and (v_dual[y_ind] % p) == 0):   ## Check the dot product for the std basis vectors!
        y_ind += 1
    if y_ind == n:
        raise RuntimeError("Oops!  One of the standard basis vectors should have worked.")
    w = vector([R(i == y_ind)  for i in range(n)])
    vw_prod = (v * self.matrix()).dot_product(w)

    ## DIAGNOSTIC
    #if vw_prod == 0:
    #   print "v = ", v
    #   print "v_dual = ", v_dual
    #   print "v_dual[y_ind] = ", v_dual[y_ind]
    #   print "(v_dual[y_ind] % p) = ", (v_dual[y_ind] % p)
    #   print "w = ", w
    #   print "p = ", p
    #   print "vw_prod = ", vw_prod
    #   raise RuntimeError, "ERROR: Why is vw_prod = 0?"

    ## DIAGNOSTIC
    #print "v = ", v
    #print "w = ", w
    #print "vw_prod = ", vw_prod


    ## Lift the vector v to a vector v1 s.t. Q(v1) = 0 (mod p^2)
    s = self(v)
    if (s % p**2 != 0):
        al = (-s / (p * vw_prod)) % p
        v1 = v + p * al * w
        v1w_prod = (v1 * self.matrix()).dot_product(w)
    else:
        v1 = v
        v1w_prod = vw_prod

    ## DIAGNOSTIC
    #if (s % p**2 != 0):
    #    print "al = ", al
    #print "v1 = ", v1
    #print "v1w_prod = ", v1w_prod


    ## Construct a special p-divisible basis to use for the p-neighbor switch
    good_basis = extend_to_primitive([v1, w])
    for i in range(2,n):
        ith_prod = (good_basis[i] * self.matrix()).dot_product(v)
        c = (ith_prod / v1w_prod) % p
        good_basis[i] = good_basis[i] - c * w  ## Ensures that this extension has <v_i, v> = 0 (mod p)

    ## DIAGNOSTIC
    #print "original good_basis = ", good_basis

    ## Perform the p-neighbor switch
    good_basis[0]  = vector([x/p  for x in good_basis[0]])    ## Divide v1 by p
    good_basis[1]  = good_basis[1] * p                          ## Multiply w by p

    ## Return the associated quadratic form
    M = matrix(good_basis)
    new_Q = deepcopy(self)                        ## Note: This avoids a circular import of QuadraticForm!
    new_Q.__init__(R, M * self.matrix() * M.transpose())
    return new_Q
    return QuadraticForm(R, M * self.matrix() * M.transpose())


## ----------------------------------------------------------------------------------------------


#def find_classes_in_genus(self):

def neighbor_iteration_orbits(self, p, verbose=False):
    r"""
    Return all classes in the `p`-neighbor graph of ``self``.

    Starting from the given quadratic form, this function successively
    finds p-neighbors untill no new quadratic form (class) is obtained.

    INPUT:

    - ``p`` -- a prime number

    OUTPUT:

    - a list of quadratic forms

    EXAMPLES::

        sage: Q = QuadraticForm(ZZ,3,[1,0,0,2,1,3])
        sage: Q.det()
        46
        sage: Q.neighbor_method(3)
        [Quadratic form in 3 variables over Integer Ring with coefficients:
        [ 1 0 0 ]
        [ * 2 1 ]
        [ * * 3 ], Quadratic form in 3 variables over Integer Ring with coefficients:
        [ 1 0 -1 ]
        [ * 1 0 ]
        [ * * 6 ], Quadratic form in 3 variables over Integer Ring with coefficients:
        [ 1 -1 -1 ]
        [ * 1 1 ]
        [ * * 8 ]]
    """
    def _normalize_vec(v):
        r"""
        """
        # the find_p_neighbor_from_vec method
        # has undocumented stupid assumptions for example that the last coordinate is 1
        for k in range(v.degree()):
            if v[-1-k] != 0:
                return (v/v[-1-k]).lift()

    isom_classes = [self.lll()]
    waiting_list = [isom_classes[0]]
    c_mass = isom_classes[0].number_of_automorphisms()**(-1)
    c_mass_0 = isom_classes[0].conway_mass()
    while len(waiting_list) > 0 and c_mass < c_mass_0:
        # find all p-neighbors of Q
        Q = waiting_list.pop()
        vecs = [_normalize_vec(v) for v in Q.orbits_mod_p(p) if v!=0 and Q(v.lift()).valuation(p) > 0]
        for v in vecs:
            Q_neighbor = Q.find_p_neighbor_from_vec(p, v).lll()
            for S in isom_classes:
                if Q_neighbor.is_globally_equivalent_to(S):
                    break
            else:
                isom_classes.append(Q_neighbor)
                waiting_list.append(Q_neighbor)
                c_mass += Q_neighbor.number_of_automorphisms()**(-1)
                if verbose:
                    print(Q_neighbor,c_mass_0 - c_mass)
    # sanity check
    if c_mass != c_mass_0:
        print("some classes are missing")
    return isom_classes


def neighbor_iteration_exaustion(self, p, verbose=False):
    r"""
    Return all classes in the `p`-neighbor graph of ``self``.

    Starting from the given quadratic form, this function successively
    finds p-neighbors untill no new quadratic form (class) is obtained.

    INPUT:

    - ``p`` -- a prime number

    OUTPUT:

    - a list of quadratic forms

    EXAMPLES::

        sage: Q = QuadraticForm(ZZ,3,[1,0,0,2,1,3])
        sage: Q.det()
        46
        sage: Q.neighbor_method(3)
        [Quadratic form in 3 variables over Integer Ring with coefficients:
        [ 1 0 0 ]
        [ * 2 1 ]
        [ * * 3 ], Quadratic form in 3 variables over Integer Ring with coefficients:
        [ 1 0 -1 ]
        [ * 1 0 ]
        [ * * 6 ], Quadratic form in 3 variables over Integer Ring with coefficients:
        [ 1 -1 -1 ]
        [ * 1 1 ]
        [ * * 8 ]]
    """

    isom_classes = [self.lll()]
    waiting_list = [isom_classes[0]]
    c_mass = isom_classes[0].number_of_automorphisms()**(-1)
    c_mass_0 = isom_classes[0].conway_mass()
    while len(waiting_list) > 0 and c_mass < c_mass_0:
        # find all p-neighbors of Q
        Q = waiting_list.pop()
        v = Q.find_primitive_p_divisible_vector__next(p)
        while not v is None:
            Q_neighbor = Q.neighbor_from_vec(p, v).lll()
            for S in isom_classes:
                if Q_neighbor.is_globally_equivalent_to(S):
                    break
            else:
                isom_classes.append(Q_neighbor)
                waiting_list.append(Q_neighbor)
                c_mass += Q_neighbor.number_of_automorphisms()**(-1)
                if verbose:
                    print(Q_neighbor,c_mass_0 - c_mass)
            v = Q.find_primitive_p_divisible_vector__next(p, v)
    # sanity check
    #assert c_mass == c_mass_0, "some classes are missing!"
    return isom_classes


def neighbor_iteration_random(self, p, verbose=False, max_trys=1000):
    r"""
    Return all classes in the `p`-neighbor graph of ``self``.

    Starting from the given quadratic form, this function successively
    finds p-neighbors untill the mass matches the mass of the genus or
    the maximum number of tries is reached

    INPUT:

    - ``p`` -- a prime number

    OUTPUT:

    - a list of quadratic forms
    - max_trys -- (default:`1000`) an Integer

    EXAMPLES::

        sage: Q = QuadraticForm(ZZ,3,[1,0,0,2,1,3])
        sage: Q.det()
        46
        sage: Q.neighbor_method(3)
        [Quadratic form in 3 variables over Integer Ring with coefficients:
        [ 1 0 0 ]
        [ * 2 1 ]
        [ * * 3 ], Quadratic form in 3 variables over Integer Ring with coefficients:
        [ 1 0 -1 ]
        [ * 1 0 ]
        [ * * 6 ], Quadratic form in 3 variables over Integer Ring with coefficients:
        [ 1 -1 -1 ]
        [ * 1 1 ]
        [ * * 8 ]]
    """
    from sage.quadratic_forms.genera.genus import Genus
    isom_classes = [self.lll()]
    genus = Genus(isom_classes[0].Hessian_matrix())
    waiting_list = [isom_classes[0]]
    c_mass = isom_classes[0].number_of_automorphisms()**(-1)
    c_mass_0 = isom_classes[0].conway_mass()
    while len(waiting_list) > 0 and c_mass < c_mass_0:
        # find all p-neighbors of Q
        Q = waiting_list.pop()
        v = Q.find_primitive_p_divisible_vector__random(p)
        for k in range(max_trys):
            Q_neighbor = Q.find_p_neighbor_from_vec(p, v).lll()
            for S in isom_classes:
                if Q_neighbor.is_globally_equivalent_to(S):
                    break
            else:
                # TODO: there is a bug here
                gen = Genus(Q_neighbor.Hessian_matrix())
                if gen == genus:
                    isom_classes.append(Q_neighbor)
                    waiting_list.append(Q_neighbor)
                    c_mass += Q_neighbor.number_of_automorphisms()**(-1)
                    if c_mass == c_mass_0:
                        break
                    if verbose:
                        print(Q_neighbor,c_mass_0 - c_mass)
                else:
                    return Q,v,Q_neighbor
            v = Q.find_primitive_p_divisible_vector__random(p)
    # sanity check
    #assert c_mass == c_mass_0, "some classes are missing!"
    return isom_classes

def orbits_mod_p(self, p):
    r"""
    Let `(L, q)` be a lattice. This returns representatives of the
    orbits of `L/pL` under the orthogonal group of `q`.

    INPUT:

    - ``p`` -- a prime number

    OUTPUT:

    - a list of vectors
    """
    from sage.libs.gap.libgap import libgap
    from sage.rings.all import GF
    G = self.automorphism_group()
    orbs = libgap.function_factory("""function(G, p)
    local one, gens, reps, V;
    one:= One(GF(p));
    gens:=List(GeneratorsOfGroup(G), g -> g*one);
    G:= Group(gens);
    n:= Size(gens[1]);
    V:= GF(p)^n;
    orb:= OrbitsDomain(G, V, OnLines);
    reps:= List(orb, g->g[1]);
    return reps;
    end;""")
    M = GF(p)**self.dim()
    return [M(m.sage()) for m in orbs(G.gap(), p)]
