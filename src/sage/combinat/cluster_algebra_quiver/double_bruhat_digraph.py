from sage.combinat.root_system.cartan_matrix import CartanMatrix
from sage.graphs.graph import DiGraph
#from sage.rings.integer import sign
from six.moves import range

def DoubleBruhatDigraph(CartanType, u,v,word = False):
    '''Returns a quiver from the Weyl group elements u and v, along with lists of exchangeable and frozen vertices, using the algorithm outlined in Cluster Algebras III.  
    
    INPUT:

    - ``u`` and ``v`` -- can be any of the following::
        * WeylGroupElement
        * Permutation
        * str - a string representation of a permutation
        * PermutationGroupElement
        * Matrix
    - CartanType -- the Cartan type of the underlying group, i.e. ['A', 5], ['C',6], etc.
    - ``word`` -- (default: False) a chosen reduced word for (u,v) as an element of W x W, using the convention that simple reflections in v are associated to negative integers.

    Examples::

        sage: from sage.combinat.cluster_algebra_quiver.double_bruhat_digraph import DoubleBruhatDigraph
        sage: W = WeylGroup(['C',4])
        sage: s1,s2,s3,s4 = W.simple_reflections()
        sage: D,F,S = DoubleBruhatDigraph(['C',4],s1*s2*s3*s4,s4*s3*s2*s1)
        sage: D
        Digraph on 12 vertices
        sage: F
        [-4, -3, -2, -1, 5, 6, 7, 8]
        sage: S
        [[-1, 1, 8], [-2, 2, 7], [-3, 3, 6], [-4, 4, 5]]


''' 
    
    typeChar = CartanType[0]
    r = CartanType[1]
   
    lu = u.length()
    lv = v.length()
    
    # Constructs a reduced word if none is specified
    if not word:
        word = u.reduced_word()
        for n in v.reduced_word():
            word.append(-n)
          
    # Pads the list with frozen variables (Note: there will be other frozen variable in the final quiver)
    word = list(range(-r,0)) + word
    indices = list(range(-r,0)) + list(range(1,lu+lv+1))   
    M = CartanMatrix(CartanType)
    
    # Determines the exchangeable vertices
    exchangeables = []
    frozen = []
    for character in indices:
        if iExchangeable(character, word, r):
            exchangeables.append(character)
        else: 
            frozen.append(character) 
            
    # Constructs the digraph described by BFZ in Cluster Algebras III
    dg = DiGraph()
    dg.add_vertices(indices)

    iks=[]

    for k0 in range(len(word)):
        iks.append(word[k0])
        for l0 in range(k0+1,len(word)):
            
            # There are some unfortunate indexing gymnastics to avoid the '0' problem
            ik = word[k0] 
            il = word[l0]
            k = indices[k0]
            l = indices[l0]
            
            
            kplus = plus(k,word,r)
            lplus = plus(l,word,r)
            if kplus in indices:
                ikplus = word[indices.index(kplus)]
            if lplus in indices: 
                ilplus = word[indices.index(lplus)]
                    
            # This runs through BFZ's three conditions under which there can be an edge between k and l
            if k in exchangeables or l in exchangeables:
                
                # horizontal edges
                if l == kplus: 
                    if il>0:
                        dg.add_edge(k,l)
                    else:
                        dg.add_edge(l,k)
                        
                # inclined edges        
                elif l<kplus and kplus<lplus and M[abs(ik)-1,abs(il)-1]<0 and il/abs(il) == ikplus/abs(ikplus): 
                    if il<0:
                        dg.add_edge(k,l,(-M[abs(ik)-1,abs(il)-1],M[abs(il)-1,abs(ik)-1]))
                    else:
                        dg.add_edge(l,k,(-M[abs(il)-1,abs(ik)-1],M[abs(ik)-1,abs(il)-1]))
                
                # inclined edges
                elif l<lplus and lplus<kplus and M[abs(ik)-1,abs(il)-1]<0 and il/abs(il)==- ilplus/abs(ilplus): 
                    if il<0:
                        dg.add_edge((k,l,(-M[abs(ik)-1,abs(il)-1],M[abs(il)-1,abs(ik)-1])))
                    else:
                        dg.add_edge(l,k,(-M[abs(il)-1,abs(ik)-1],M[abs(ik)-1,abs(il)-1]))
   
    return dg,frozen,strings(indices,iks,r)

def plus(k,word,r):
    '''Returns the index 'k+', being the smallest index l in 'word' such that k<l and the index k and l entries of 'word' agree.  NOTE: the 'index' is assumed to be following the indexing conventions of DoubleBruhatDigraph, not the standard python conventions.

    INPUT:
    - ``k`` -- An index for `word` in the convention of DoubleBruhatQuiver.
    - ``word`` -- The reduced word constructed in DoubleBruhatQuiver.
    - ``r`` -- The number of additional frozen variables in the beginning of `word` (which is the rank of the underlying Cartan matrix).'''

    # fix for index 0
    if k<0:
        ik = abs(word[k+r])
    else:
        ik = abs(word[k+r-1]) 

    for l in range(k+1,len(word) - r+1):
        if l<0 and abs(word[l + r]) == ik:
            return l
        elif l>0 and abs(word[l+r-1]) == ik:
            return l

    return len(word) - r + 1        

def iExchangeable(k,word,r):
    '''Returns True if index k is exchangeable, and False otherwise.

    INPUT:

    - ``k`` -- An index for `word` in the convention of DoubleBruhatDigraph.
    - ``word`` -- The reduced word constructed in DoubleBruhatDigraph.
    - ``r`` -- The number of additional frozen variables in the beginning of `word` (which is the rank of the underlying Cartan matrix).'''

    if (k >=1 and k<=(len(word) - r)) and (plus(k,word,r) >=1 and plus(k,word,r)<=(len(word) - r)):
        return True

    return False

def strings(indices,iks,r):
    listk=[]  
    for l in range(0, r):
        listl=[]
        for k in range(0,len(iks)):
            if abs(iks[l]) == abs(iks[k]):
                listl.append(indices[k])
          
        listk.append(listl)
    listk.reverse()
    return listk

        

