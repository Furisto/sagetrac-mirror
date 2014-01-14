r"""
Reduced Affine Crystals

This class in the category of Crystals is a takeoff on
CrystalOfLSPaths(CartanType,HighestWeight) in which the elements are
redefined to be a tuple of length rank of algebra representing the content.
It implements the non-recursive construction of `P(\Lambda)` in [BFS]_.

Unlike the vertices in the crystal of Littelman paths, which correspond to
basis elements in a highest weight module, these vertices correspond
one-to-one to weights and represent blocks in Khovanov-Lauda-Rouquier
algebras or in some cases of cyclotomic Hecke algebras.

REFERENCES:

.. [BFS] Barchevsky, O., Fayers, M., Schaps, M. *A nonrecursive criterion for
   weights in the highest weight module of an affine Lie algebra*,
   Israel Jour. of Math.
"""
from sage.structure.unique_representation import UniqueRepresentation
from sage.structure.element_wrapper       import ElementWrapper
from sage.structure.parent                import Parent
from sage.categories.crystals             import Crystals
from sage.categories.highest_weight_crystals import HighestWeightCrystals
from sage.categories.finite_crystals      import FiniteCrystals
from sage.categories.regular_crystals      import RegularCrystals
from sage.combinat.root_system.cartan_type import CartanType
from sage.combinat.root_system.root_system import RootSystem
from sage.rings.integer                   import Integer
from sage.functions.other                 import floor
from sage.misc.latex                      import latex
from sage.misc.cachefunc                   import cached_function
from sage.rings.all                         import QQ

######################################################################################
#
#
#                   Non-recursive Weight Space Criterion
#
#
#####################################################################################

# This maybe should belong to CartanType... for now, I'm just going to cache it
#    and assume it gets an actual object of type CartanType as input.
@cached_function
def T_lattice(cartan_type):
    r"""
    Generates the vector `(d_1, \ldots, d_m)` such that `\{d_1 alpha_1, \ldots,
    d_m \alpha_m\}` form a set of generators for the lattice `<` parametrizing
    the abelian subgroup `T` of the infinite Weyl group `W`. Currently
    implemented for types `A_n^{(1)}`, `D_n^{(1)}`, and twisted types.

    INPUT:

    - ``cartan_type`` -- the affine Cartan type

    OUTPUT

    The tuple `(d_1, ..., d_m)`.

    EXAMPLES::

        sage: d = T_lattice(CartanType(['A',2,1])); d
        (1, 1)
        sage: d = T_lattice(CartanType(['D',4,1])); d
        (1, 1, 1, 1)
    """
    if not cartan_type.is_affine():
        raise ValueError("Implemented only for affine Cartan types")
    m = cartan_type.rank() - 1
    if cartan_type.is_untwisted_affine():
        if cartan_type.type() not in ['A','D']:
            raise NotImplementedError
        d = tuple([1]*m)
    else: # Twisted case
        if cartan_type.type() == 'BC': # Don't need to consider the dual.  This case treated specially so that d will be integral
            d = tuple([1]*m)
        else:
            raise NotImplementedError
    return d

def tilde(lst, level, d, a):
    r"""
    INPUT:

    - ``lst`` -- list of integers representing coefficients of simple roots in
      `\alpha` for a weight `\Lm - \alpha`
    - ``level`` -- the level of the highest weight
    - ``d`` -- the `T` lattice tuple
    - ``a`` -- the coefficients of `\delta`

    OUTPUT:

    A hashable tuple in fundamental region.

    EXAMPLES::

        sage: tilde([1,1,0,0,0],2,(1,1,1,1),[1,1,2,1,1])
        (0, 0, 1, 1, 0)
        sage: tilde([2,0,2],4,(1,1),[1,1,1])
        (2, 0, 0)
    """
    new = len(d)*[0]
    for j in range(1, len(lst)):
        new[j-1] = (lst[j]*a[0] - lst[0]*a[j]) % (level*d[j-1])
    # If type BC, then a[0] == 2 and we need to keep track of the parity
    # Otherwise is doesn't matter and a[0] == 1 so we get 0 by taking mod 1
    new.append(lst[0] % a[0])
    return tuple(new)

def absval(list):
    absv = sum(abs(list[i]) for i in range(len(list)))
    return absv

def sym_prod_hub_root(list_hub, list_root, a, acheck):
    r"""
    Computes the symmectic product in the weight space for weight with root.

    INPUT:

    - ``list_hub`` -- the set of coefficients of the fundamental weights. There
      is not a need for the delta coeff
    - ``list_root`` -- a list of coefficients wrt to the simple roots.  Both
      lists have the same length
    - ``a`` -- the coeffients of the null root
    - ``acheck`` -- the coefficients of the central element

    OUTPUT:

    The ``sym_prod``, an integer which is the symmetric product of a hub,
    that is, a list of coefficients with respect to fundamental weights,
    with an element of the integer root lattice.

    EXAMPLES::

        sage: sym_prod_hub_root([3,-1,0,0,0],[1,0,0,0,0],[1,1,2,1,1,],[1,1,2,1,1,])
        3
        sage: sym_prod_hub_root([1,2,1],[2,1,0],[1,1,1,],[1,1,1,])
        4
    """
    return sum(list_hub[i]*list_root[i]*acheck[i]/a[i] for i in range(len(list_hub)))

def positive_hubs(cartan_type, hw):
    r"""
    INPUT:

    - ``cartan_type`` -- the affine Cartan type
    - ``hw`` -- highest weight vector as a tuple

    OUTPUT:

    The list of positive hubs.

    EXAMPLES::

        sage: cartan_type = CartanType(['A', 2, 1])
        sage: La = cartan_type.root_system().weight_lattice(extended=True).fundamental_weights()
        sage: hw = La[0] + 2*La[1] + La[2]
        sage: positive_hubs(cartan_type, hw)
        [[3, 1, 0], [2, 0, 2], [1, 2, 1], [0, 4, 0], [0, 1, 3]]
    """
    pos_hubs = []
    rank = cartan_type.rank()
    acheck = cartan_type.acheck()
    level = hw.level()
    type_A_reduction = cartan_type.type() == 'A' and cartan_type.is_untwisted_affine()

    for j in range(1, level+1):
        L = [v for v in IntegerVectors(j, rank)
             if sum(acheck[i]*v[i] for i in range(rank)) == level]

        # Now reduce to positive hub for P(\Lm) using theorems in Barshevky-Fayers-Schaps
        if type_A_reduction:
            L = filter(lambda x: sum(i*(hw[i]-x[i]) for i in range(rank)) % rank == 0, L)

        pos_hubs += L
    return pos_hubs

def FundamentalRegionKey(cartan_type, level):
    r"""
    Generates a set of representatives for the fundamental region of the
    lattice of indices, parametrizing the abelian subgroup `T` of the
    infinite Weyl group `W`.  The dimension is `k^m \prod_i d_i`. 
    Not yet implemented for spin case.

    INPUT:

    - ``level`` -- the (positive) level of the highest weight vector
    - ``d`` -- the set of integers produced by :func:`T_lattice`
    - ``rank`` --the rank of the Cartan type

    OUTPUT:

    The list of tuples to serve as keys in content_dictionary.

    EXAMPLES::

        sage: cartan_type = CartanType(['A', 2, 1])
        sage: La = cartan_type.root_system().weight_lattice(extended=True).fundamental_weights()
        sage: hw = La[0] + 2*La[1] + La[2]
        sage: FundamentalRegionKey(cartan_type, hw.level())
        [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2), (1, 3),
         (2, 0), (2, 1), (2, 2), (2, 3), (3, 0), (3, 1), (3, 2), (3, 3)]
    """
    d = T_lattice(cartan_type)
    rank = cartan_type.rank()
    prods = range(level*d[1])
    for i in range(1, rank-1): # Need to watch out for a degenerate case like A_1^(1)!!!
        prods = CartesianProduct(prods, range(level*d[i])).list()
        prods = map(flatten, prods)
    for i in range(len(prods)):
        prods[i].append(0)
    if cartan_type.type() == 'BC':
        from copy import deepcopy
        cp = deepcopy(prods)
        for i in range(len(prods)):
            cp[i][-1] = 1
        prods += cp
    key = map(tuple, prods)
    return key

def FundamentalRegion(cartan_type, hw):
    r"""
    Generate a set of representatives for the fundamental region of the lattice
    of indices, parametrizing the abelian subgroup `T` of the infinite Weyl
    group `W`.  The dimension is `k^m \prod_i(d_i)`.  Not yet implemented for
    spin case.

    INPUT:

    - ``cartan_type`` -- the affine Cartan type
    - ``hw`` -- the highest weight of the representation as an element in the
      weight space

    OUTPUT:

    The dictionary giving the content of an element of the weight lattice of
    each tuple in the region. That is to say, the dictionary matching hashable
    key of length rank-1 with contents of elements of weight space.

    EXAMPLES::

        sage: cartan_type = CartanType(['A', 2, 1])
        sage: La = cartan_type.root_system().weight_space().fundamental_weights()
        sage: hw = La[0] + 2*La[1] + La[2]
        sage: sorted(FundamentalRegion(cartan_type, hw).iteritems())
        [((0, 0), [0, 0, 0]),
         ((0, 1), [0, 0, 1]),
         ((0, 2), [2, 2, 0]),
         ((0, 3), [1, 1, 0]),
         ((1, 0), [0, 1, 0]),
         ((1, 1), [0, 1, 1]),
         ((1, 2), [0, 1, 2]),
         ((1, 3), [1, 2, 0]),
         ((2, 0), [0, 2, 0]),
         ((2, 1), [0, 2, 1]),
         ((2, 2), [0, 2, 2]),
         ((2, 3), [1, 3, 0]),
         ((3, 0), [1, 0, 1]),
         ((3, 1), [1, 0, 2]),
         ((3, 2), [2, 1, 0]),
         ((3, 3), [1, 0, 0])]
    """
    if not cartan_type.is_affine():
        raise ValueError("Implemented only for affine Cartan types")

    # Construct the necessary data
    rank = cartan_type.rank()
    cm = cartan_type.cartan_matrix()
    d = T_lattice(cartan_type)
    a = cartan_type.a()
    level = hw.level()
    # First we find the list of keys for the dictionary
    key = FundamentalRegionKey(cartan_type, level)
    cont_dict = {x:None for x in key}
    # Now we start to construct the crystal, starting at the highest weight
    #   and iterating on the height of the content
    zero_list = [0] * rank

    hw_list = [hw[i] for i in range(rank)] # Make sure we don't get any delta's
    warehouse = [[0, zero_list, hw_list]] # [level, content, weight]
    zero_tup = tuple([0] * rank)
    cont_dict[zero_tup] = zero_list

    for j in range(2*level):
        for w in filter(lambda w: w[0] == j, warehouse): # Look at current level
            for i in filter(lambda i: w[2][i] > 0, range(rank)):
                for k in range(1, w[2][i]+1):
                    newlist = w[1][:]
                    newlist[i] = newlist[i] + k
                    newhub = [w[2][j] - k*cm[j][i] for j in range(len(w[2]))]
                    newentry = [w[0]+k, newlist, newhub]
                    newkey = tilde(newlist, level, d, a)
                    if cont_dict[newkey] is None:
                        cont_dict[newkey] = newlist
                        warehouse.append(newentry)
    return cont_dict

###################################################################
#
#  Affine Crystal
#
#    Mary Schaps
#    Travis Scrimshaw
###################################################################

class ReducedAffineCrystal(Parent, UniqueRepresentation):
    r"""
    The crystal of weights of highest weight representation of affine
    Lie algebra.

    INPUT:

    - ``cartan_type`` -- an affine Cartan type
    - ``hw`` -- a dominant highest weight in the weight space

    EXAMPLES::

        sage: La = RootSystem(['A', 2, 1]).weight_lattice().fundamental_weights()
        sage: B = ReducedAffineCrystal(['A',2,1], La[0] + 2*La[1] + La[2]); B
        The crystal of weights of type ['A', 2, 1] and highest weight Lambda[0] + 2*Lambda[1] + Lambda[2]
    """
    @staticmethod
    def __classcall_private__(cls, cartan_type, hw):
        """
        Normalize arguments to ensure a unique representation.
        """
        cartan_type = CartanType(cartan_type)
        if not cartan_type.is_affine():
            raise ValueError("Implemented only for affine types")

        # Make sure we have an element in the weight space
        WS = RootSystem(cartan_type).weight_space()
        if isinstance(hw, (list, tuple)):
            La = WS.fundamental_weights()
            hw = sum(hw[i]*La[i] for i in range(cartan_type.n))
        else:
            hw = WS(hw)

        if not hw.is_dominant():
            raise ValueError("The starting weight hw must be dominant.")
        if hw == WS.zero():
            raise ValueError("The starting weight must be positive")

        return super(ReducedAffineCrystal, cls).__classcall__(cls, cartan_type, hw)

    def __init__(self, cartan_type, hw):
        """
        Initalize ``self``.

        EXAMPLES::

            sage: La = RootSystem(['A', 2, 1]).weight_lattice().fundamental_weights()
            sage: B = ReducedAffineCrystal(['A',2,1], La[0] + 2*La[1] + La[2])
            sage: TestSuite(B).run()
        """
        self._cartan_type = cartan_type
        Parent.__init__( self, category=(RegularCrystals(), HighestWeightCrystals()) )

        #Our attributes
        self._hw = hw
        self._level = hw.level() # Cached since it is called frequently
        self._d = T_lattice(cartan_type)

        self.pos_hubs = positive_hubs(cartan_type, hw)
        self.cont_dict = FundamentalRegion(cartan_type, hw)
        self.module_generators = (self(tuple([0]*cartan_type.rank())),)

    def _repr_(self):
        """
        Return a string representation of ``self``.
        """
        return "The crystal of weights of type %s and highest weight %s"%(self._cartan_type, self._hw)

    def delta_shift(self, content):
        r"""
        Compute the delta shift of ``self``.

        INPUT:

        - ``content`` -- a list of the number of times `f_i` has been applied

        OUTPUT:

        Integer `s` for a weight `\zeta` with content list such that `\zeta +
        s \cdot \delta` in a maximal weight for `P(\lambda)`.

        EXAMPLES::

            sage: La = RootSystem(['A', 2, 1]).weight_lattice().fundamental_weights()
            sage: B = ReducedAffineCrystal(['A',2,1], La[0] + 2*La[1] + La[2])
            sage: B.delta_shift([1, 1, 1])
            -1
            sage: B.delta_shift([2, 2, 0])
            0
            sage: B.delta_shift([1, 1, -1])
            1
        """
        cm = self._cartan_type.cartan_matrix()
        a = self._cartan_type.a()
        rank = self._cartan_type.rank()
        new_key = tilde(content, self._level, self._d, a)
        new_cont = self.cont_dict[new_key]

        difference = [content[i]-new_cont[i] for i in range(rank)]
        shift = -difference[0] / a[0]
        alf = [(difference[i]*a[0] - difference[0]*a[i]) / (self._level*a[0]) for i in range(rank)]
        #print "alf[-1] is", alf[-1]
        #if a[0] == 2: This was wrong:
        #    assert alf[-1] % 2 == 0, "type BC and odd last entry: %s"%self._value
        #    alf[-1] /= Integer(2)
        hub_zeta = [sum(cm[i][j] * new_cont[j] for j in range(rank)) for i in range(rank)]
        list_zeta = [self._hw[i] - hub_zeta[i] for i in range(rank)]
        shift -= sym_prod_hub_root(list_zeta, alf, a, self._cartan_type.acheck()) 
        #print shift next is awkward evaluation of the symmetric product of roots.
        shift +=  sum(sum(alf[i]* a[i]**(-1)*self._cartan_type.acheck()[i]*cm[i][j] for i in range(rank))*alf[j] for j in range(rank)) * (self._level / 2)
        #print shift
        return shift

    def blockreduced(self, max_depth=5):
        
        r"""
        produces tikzcode for a diagramof the block-reduced graph of ``self``.

        INPUT:

        - ``max_depth`` -- the number ofsteps down the graph to illustrate

        OUTPUT:

        A printed list of tikz code for the edges and then the vertices,in reversed order
        EXAMPLES::

            ssage: La = RootSystem(['BC',2,2]).weight_lattice().fundamental_weights()
            sage: B = ReducedAffineCrystal(['BC',2,2], La[0])
            sage: B.blockreduced(max_depth=6)
           \draw[lbluex](-2\lf+2\ri,-5\dd)--++(+\ri,-\dd);
\draw[purplex](-2\lf+2\ri,-5\dd)--++(-\lf,-\dd);
\draw[purplex](-\lf+2\ri,-4\dd)--++(-\lf,-\dd);
\draw[lbluex](-2\lf+\ri,-4\dd)--++(+\ri,-\dd);
\draw[lbluex](-\lf+\ri,-3\dd)--++(+\ri,-\dd);
\draw[purplex](-\lf+\ri,-3\dd)--++(-\lf,-\dd);
\draw[greyx](-2\lf+\ri,-3\dd)--++(+0,-\dd);
\draw[greyx](-\lf+\ri,-2\dd)--++(+0,-\dd);
\draw[purplex](-\lf+\ri,-2\dd)--++(-\lf,-\dd);
\draw[lbluex](-\lf,-\dd)--++(+\ri,-\dd);
\draw([purplex](0,0)--++(-\lf,-\dd);
\draw(-2\lf+2\ri,-5\dd)node[lbluex,fill=white,inner sep=0pt]{\nod2211};
\draw(-\lf+2\ri,-4\dd)node[lbluex,fill=white,inner sep=0pt]{\nod1210};
\draw(-2\lf+\ri,-4\dd)node[lbluex,fill=white,inner sep=0pt]{\nod2110};
\draw(-\lf+\ri,-3\dd)node[lbluex,fill=white,inner sep=0pt]{\nod1110};
\draw(-2\lf+\ri,-3\dd)node[purplex,fill=white,inner sep=0pt]{\nod2100};
\draw(-\lf+\ri,-2\dd)node[purplex,fill=white,inner sep=0pt]{\nod1100};
\draw(-\lf,-\dd)node[purplex,fill=white,inner sep=0pt]{\nod1000};
\draw(0,0)node[purplex,fill=white,inner sep=0pt]{\nod0000};

        """
        m = self._cartan_type.rank()
        half = int(m/2)
        sign = half*['-']+(m-half)*['+']
        sizeminus = 3.0
        sizeplus = 2.1
        sizedown = 1.1
        shift = '\lf'
        displace = []
        for i in range(1, half+1):
            shifty = shift +str(i)
            displace += [shifty]
            print '\setlength'+shifty+'{'+str(sizeminus*(QQ(1)/QQ(i)))+'cm}'
        shift = '\\ri'
        displace += []
        for i in range(1, m-half):
            shiftnew = shift + str(i)
            displace += [shiftnew]
            print '\setlength'+shiftnew+'{'+str(sizeplus*(QQ(1)/QQ(m-half-i)))+'cm}'
        displace += ['0']
        print '\setlength\dd{'+str(sizedown)+'cm}'
        vertex=self(tuple([0]*m))
        self.vertex_list = [vertex]
        style_list = ['purplex', 'lbluex','greyx','lgreenx','redx','bluex','greenx']
        current_node = '\draw(0,0)node['+style_list[0]+',fill=white,inner sep=0pt]{\\nod0000};\n'
        node_list =[current_node]
        edge_list = []
        for u in range(m):
            if u == 0:   #should be: if vertex.f(u) != None:
                charstr_edge='\draw(['+style_list[u]+'](0,0)--++('+sign[u]+displace[u]+','+'-\dd);'
                #print charstr_edge
                #print vertex.f(u)
                edge_list.append(charstr_edge)        
        #print vertex.value
        #print current_node
        for j in range(1,max_depth):
            self.new_vertex_list=[]
            for x in self.vertex_list:
                for i in range(m):
                    if x.f(i) != None:
                        self.tempvertex=x.f(i)
                        if not (self.tempvertex  in self.new_vertex_list):
                            val = self.tempvertex.value
                            nodpos1 = ''
                            for k in range(m-1):
                                if val[k] > 1:
                                    nodpos1 += sign[k]+str(val[k])+displace[k]
                                elif val[k] == 1:
                                    nodpos1 += sign[k]+displace[k]
                            if nodpos1 == '':
                                nodpos1 = '0'
                            down = sum(val[y] for y in range(m))
                            if down > 1:
                                nodpos2 = '-'+str(down)+'\dd'
                            elif down == 1:
                                nodpos2 = '-'+'\dd'
                            else:
                                nodpos2 = '0'                            
                            charstr ='\draw('+nodpos1+','+nodpos2+')node['+style_list[val[-1]]+',fill=white,inner sep=0pt]{\\nod'+str(val[0])+str(val[1])+str(val[2])+str(self.tempvertex.defect())+'};'
                            #print charstr
                            #print self.tempvertex.value
                            self.new_vertex_list.append(self.tempvertex)
                            node_list.append(charstr)
                            #print edge_list
                            for u in range(m):
                                if self.tempvertex.f(u) != None:
                                     charstr_edge='\draw['+style_list[u]+']('+nodpos1+','+nodpos2+')--++('+sign[u]+displace[u]+','+'-\dd);'
                                     edge_list.append(charstr_edge)
            self.vertex_list = self.new_vertex_list
        edge_list.reverse()
        for v in range(len(edge_list)):
            print edge_list[v]
        node_list.reverse()
        for v in range(len(node_list)):
            print node_list[v]
        return repr(self)
 
 
class ATElement(ElementWrapper):
    def _repr_(self):
        """
        Return a string representation of ``self``.
        """
        return repr(self.value) + " + %s delta shifts"%self.parent().delta_shift(self.value)

    def _latex_(self):
        """
        Return the weight of ``self``.
        """
        from sage.misc.latex import latex
        wt = self.weight()
        ret = ""
        for i,c in wt: # Should never iterate over a coeff of 0
            if c > 0:
                ret += "+"
            else:
                ret += "-"
            if abs(c) != 1:
                ret += latex(abs(c))
            ret += "\\Lambda_{%s}"%i
        if ret[0] == "+":
            ret = ret[1:] # Remove the leading +

        r = self.parent().delta_shift(self.value)
        if r == 0:
            return ret

        if r > 0:
            ret += "-"
        else:
            ret += "+"
        return ret + "%s [\\delta]"%r

    def e(self, i, power=1):
        r"""
        Return the trivial `i`-th raising operator.
        """
        if self.value[i] == 0:
            return None

        content = list(self.value)
        for k in range(power):
            content[i] -= 1
            if self.parent().delta_shift(content) > 0:
                return None

        return self.parent()(tuple(content))

    def f(self, i, power=1):
        r"""
        Return the trivial `i`-th lowering operator.
        """
        content = list(self.value)
        for k in range(power):
            content[i] += 1
            if self.parent().delta_shift(content) > 0:
                return None
        return self.parent()(tuple(content))

    def epsilon(self, i):
        r"""
        Return the value of `\varepsilon_i` of ``self``.
        """
        if self.value[i] == 0:
            return None

        content = list(self.value)
        content[i] -= 1
        ep = 0
        while wt[i] != 0 and self.parent().delta_shift(content) > 0:
            ep += 1
            content[i] -= 1
        return ep

    def phi(self, i):
        r"""
        Return the value of `\varphi_i` of ``self``.
        """
        content = list(self.value)
        content[i] -= 1
        phi = 0
        while wt[i] != 0 and self.parent().delta_shift(content) > 0:
            phi += 1
            content[i] -= 1
        return phi

    def weight(self):
        """
        Return the weight of ``self``.
        """
        alpha = self.parent()._cartan_type.root_system().weight_space().simple_roots()
        wt = self.parent()._hw - sum([c*alpha[i] for i,c in enumerate(self.value)])
        return wt



    def defect(self):
        r"""
        If it ever works, it should return (lam|alpha)-(1/2)*(alpha|alpha) where lam-alpha is  the weight of ``self``.
        """
        m = self.parent()._cartan_type.rank()
        alpha = self.parent()._cartan_type.root_system().weight_space().simple_roots()
        a = self.parent()._cartan_type.a()
        acheck = self.parent()._cartan_type.acheck()
        cm = self.parent()._cartan_type.cartan_matrix()
        lam = self.parent()._hw
        alf = sum([c*alpha[i] for i,c in enumerate(self.value)])
        d = sum((2*lam[i]-alf[i])* a[i]**(-1)*acheck[i]*c for i,c in enumerate(self.value))
        d = d/2        
        return d

ReducedAffineCrystal.Element = ATElement

