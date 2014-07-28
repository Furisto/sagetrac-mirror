r"""
Database of small combinatorial designs

This module implements known constructions combinatorial designs, and in
particular of :mod:`Orthogonal Arrays
<sage.combinat.designs.orthogonal_arrays>`. Most of them come from the chapter
on :mod:`Mutually Orthogonal Latin Squares
<sage.combinat.designs.latin_squares>` from the Handbook of Combinatorial
Designs.

Most of this would only be a dream without the mathematical knowledge and help
of Julian R. Abel.

All the designs returned by these functions can be obtained through the
``designs.<tab>`` functions.

Implemented constructions :

- :func:`OA(7,18) <OA_7_18>`,
  :func:`OA(6,20) <OA_6_20>`,
  :func:`OA(7,21) <OA_7_21>`,
  :func:`OA(5,22) <OA_5_22>`,
  :func:`OA(9,24) <OA_9_24>`,
  :func:`OA(6,26) <OA_6_26>`,
  :func:`OA(7,28) <OA_7_28>`,
  :func:`OA(6,30) <OA_6_30>`,
  :func:`OA(7,33) <OA_7_33>`,
  :func:`OA(6,34) <OA_6_34>`,
  :func:`OA(7,35) <OA_7_35>`,
  :func:`OA(10,36) <OA_10_36>`,
  :func:`OA(6,38) <OA_6_38>`,
  :func:`OA(7,39) <OA_7_39>`,
  :func:`OA(9,40) <OA_9_40>`,
  :func:`OA(7,42) <OA_7_42>`,
  :func:`OA(7,44) <OA_7_44>`,
  :func:`OA(8,45) <OA_8_45>`,
  :func:`OA(6,46) <OA_6_46>`,
  :func:`OA(10,48) <OA_10_48>`,
  :func:`OA(8,50) <OA_8_50>`,
  :func:`OA(7,51) <OA_7_51>`,
  :func:`OA(7,52) <OA_7_52>`,
  :func:`OA(7,54) <OA_7_54>`,
  :func:`OA(8,55) <OA_8_55>`,
  :func:`OA(9,56) <OA_9_56>`,
  :func:`OA(9,57) <OA_9_57>`,
  :func:`OA(7,60) <OA_7_60>`,
  :func:`OA(7,62) <OA_7_62>`,
  :func:`OA(7,66) <OA_7_66>`,
  :func:`OA(7,68) <OA_7_68>`,
  :func:`OA(8,69) <OA_8_69>`,
  :func:`OA(7,74) <OA_7_74>`,
  :func:`OA(9,75) <OA_9_75>`,
  :func:`OA(8,76) <OA_8_76>`,
  :func:`OA(11,80) <OA_11_80>`,
  :func:`OA(10,82) <OA_10_82>`,
  :func:`OA(10,100) <OA_10_100>`,
  :func:`OA(15,112) <OA_15_112>`,
  :func:`OA(9,120) <OA_9_120>`,
  :func:`OA(9,135) <OA_9_135>`,
  :func:`OA(12,144) <OA_12_144>`,
  :func:`OA(10,154) <OA_10_154>`,
  :func:`OA(11,160) <OA_11_160>`,
  :func:`OA(16,176) <OA_16_176>`,
  :func:`OA(16,208) <OA_16_208>`,
  :func:`OA(12,210) <OA_12_210>`,
  :func:`OA(15,224) <OA_15_224>`,
  :func:`OA(10,262) <OA_10_262>`,
  :func:`OA(18,273) <OA_18_273>`,
  :func:`OA(12,276) <OA_12_276>`,
  :func:`OA(12,298) <OA_12_298>`,
  :func:`OA(12,342) <OA_12_342>`,
  :func:`OA(20,352) <OA_20_352>`,
  :func:`OA(20,416) <OA_20_416>`,
  :func:`OA(12,474) <OA_12_474>`,
  :func:`OA(9,514) <OA_9_514>`,
  :func:`OA(20,544) <OA_20_544>`,
  :func:`OA(17,560) <OA_17_560>`,
  :func:`OA(11,640) <OA_11_640>`,
  :func:`OA(10,796) <OA_10_796>`,
  :func:`OA(15,896) <OA_15_896>`,
  :func:`OA(14,950) <OA_14_950>`,
  :func:`OA(33,993) <OA_33_993>`,
  :func:`OA(10,1046) <OA_10_1046>`,
  :func:`OA(10,1059) <OA_10_1059>`,
  :func:`OA(11,2164) <OA_11_2164>`,
  :func:`OA(12,3992) <OA_12_3992>`,
  :func:`OA(12,3994) <OA_12_3994>`

- :func:`two MOLS of order 10 <MOLS_10_2>`,
  :func:`five MOLS of order 12 <MOLS_12_5>`,
  :func:`four MOLS of order 14 <MOLS_14_4>`,
  :func:`four MOLS of order 15 <MOLS_15_4>`,
  :func:`three MOLS of order 18 <MOLS_18_3>`

- :func:`DF(21,5,1) <CDF_21_5_1>`
  :func:`DF(25,4,1) <ADF_5x5_4_1>`
  :func:`DF(37,4,1) <CDF_37_4_1>`
  :func:`DF(81,5,1) <CDF_81_5_1>`
  :func:`DF(91,6,1) <CDF_91_6_1>`
  :func:`DF(121,5,1) <CDF_121_5_1>`
  :func:`DF(141,5,1) <CDF_141_5_1>`
  :func:`DF(161,5,1) <CDF_161_5_1>`
  :func:`DF(201,5,1) <CDF_201_5_1>`
  :func:`DF(221,5,1) <CDF_221_5_1>`

- :func:`RBIBD(120,8,1) <RBIBD_120_8_1>`

**Dictionaries**

The functions defined here are used by
:func:`~sage.combinat.designs.orthogonal_arrays.orthogonal_array`. Thus, the
functions are indexed by dictionary which associates to every integer ``n`` a
pair ``(k,f)`` where ``f`` is a function such that ``f()`` is a `OA(k,n)`. This
dictionary is defined right after the constructions of OA in the file.

The same goes for the constructions of MOLS, used by
:func:`~sage.combinat.designs.latin_squares.mutually_orthogonal_latin_squares`.

REFERENCES:

.. [DesignHandbook] Handbook of Combinatorial Designs (2ed)
  Charles Colbourn, Jeffrey Dinitz
  Chapman & Hall/CRC
  2012

Functions
---------
"""

from sage.combinat.designs.orthogonal_arrays import (OA_from_quasi_difference_matrix,
                                                     OA_from_Vmt,
                                                     QDM_from_Vmt,
                                                     OA_from_wider_OA,
                                                     OA_from_PBD,
                                                     orthogonal_array)
from orthogonal_arrays import wilson_construction

# Cyclic shift of a list
cyclic_shift = lambda l,i : l[-i:]+l[:-i]

def TD_6_12():
    r"""
    Returns a `TD(6,12)` as built in [Hanani75]_.

    This design is Lemma 3.21 from [Hanani75]_.

    EXAMPLE::

        sage: from sage.combinat.designs.database import TD_6_12
        sage: from sage.combinat.designs.orthogonal_arrays import is_transversal_design
        sage: TD = TD_6_12()
        sage: is_transversal_design(TD,6,12)
        True

    The design is available from the general constructor::

        sage: designs.transversal_design(6,12,existence=True)
        True

    REFERENCES:

    .. [Hanani75] Haim Hanani,
      Balanced incomplete block designs and related designs,
      http://dx.doi.org/10.1016/0012-365X(75)90040-0,
      Discrete Mathematics, Volume 11, Issue 3, 1975, Pages 255-369.
    """
    from sage.groups.additive_abelian.additive_abelian_group import AdditiveAbelianGroup
    G = AdditiveAbelianGroup([2,6])
    d = [[(0,0),(0,0),(0,0),(0,0),(0,0),(0,0)],
         [(0,0),(0,1),(1,0),(0,3),(1,2),(0,4)],
         [(0,0),(0,2),(1,2),(1,0),(0,1),(1,5)],
         [(0,0),(0,3),(0,2),(0,1),(1,5),(1,4)],
         [(0,0),(0,4),(1,1),(1,3),(0,5),(0,2)],
         [(0,0),(0,5),(0,1),(1,5),(1,3),(1,1)],
         [(0,0),(1,0),(1,3),(0,2),(0,3),(1,2)],
         [(0,0),(1,1),(1,5),(1,2),(1,4),(1,0)],
         [(0,0),(1,2),(0,4),(0,5),(0,2),(1,3)],
         [(0,0),(1,3),(1,4),(0,4),(1,1),(0,1)],
         [(0,0),(1,4),(0,5),(1,1),(1,0),(0,3)],
         [(0,0),(1,5),(0,3),(1,4),(0,4),(0,5)]]

    r = lambda x : int(x[0])*6+int(x[1])
    TD = [[i*12+r(G(x)+g) for i,x in enumerate(X)] for X in d for g in G]
    for x in TD: x.sort()

    return TD

def _MOLS_from_string(s,k):
    r"""
    Returns MOLS from a string

    INPUT:

    - ``s`` (string) -- represents the MOLS with entries in a-z. To understand
      how the string should be formatted, read the source code of a constructor
      that uses it.

    - ``k`` (integer) -- the number of MOLS encoded by the string.

    EXAMPLES::

        sage: _ = designs.mutually_orthogonal_latin_squares(2,10) # indirect doctest
    """
    from sage.matrix.constructor import Matrix
    matrices = [[] for _ in range(k)]
    for i,l in enumerate(s.split()):
        l = [ord(x) - 97 for x in l]
        matrices[i%k].append(l)
    return map(Matrix, matrices)

def MOLS_10_2():
    r"""
    Returns a pair of MOLS of order 10

    Data obtained from
    `<http://www.cecm.sfu.ca/organics/papers/lam/paper/html/POLS10/POLS10.html>`_

    EXAMPLES::

        sage: from sage.combinat.designs.latin_squares import are_mutually_orthogonal_latin_squares
        sage: from sage.combinat.designs.database import MOLS_10_2
        sage: MOLS = MOLS_10_2()
        sage: print are_mutually_orthogonal_latin_squares(MOLS)
        True

    The design is available from the general constructor::

        sage: designs.mutually_orthogonal_latin_squares(2,10,existence=True)
        True
    """
    from sage.matrix.constructor import Matrix
    return [Matrix([[1,8,9,0,2,4,6,3,5,7],
                    [7,2,8,9,0,3,5,4,6,1],
                    [6,1,3,8,9,0,4,5,7,2],
                    [5,7,2,4,8,9,0,6,1,3],
                    [0,6,1,3,5,8,9,7,2,4],
                    [9,0,7,2,4,6,8,1,3,5],
                    [8,9,0,1,3,5,7,2,4,6],
                    [2,3,4,5,6,7,1,8,9,0],
                    [3,4,5,6,7,1,2,0,8,9],
                    [4,5,6,7,1,2,3,9,0,8]]),

            Matrix([[1,7,6,5,0,9,8,2,3,4],
                    [8,2,1,7,6,0,9,3,4,5],
                    [9,8,3,2,1,7,0,4,5,6],
                    [0,9,8,4,3,2,1,5,6,7],
                    [2,0,9,8,5,4,3,6,7,1],
                    [4,3,0,9,8,6,5,7,1,2],
                    [6,5,4,0,9,8,7,1,2,3],
                    [3,4,5,6,7,1,2,8,0,9],
                    [5,6,7,1,2,3,4,0,9,8],
                    [7,1,2,3,4,5,6,9,8,0]])]

def MOLS_12_5():
    r"""
    Returns 5 MOLS of order 12

    These MOLS have been found by Brendan McKay.

    EXAMPLES::

        sage: from sage.combinat.designs.latin_squares import are_mutually_orthogonal_latin_squares
        sage: from sage.combinat.designs.database import MOLS_12_5
        sage: MOLS = MOLS_12_5()
        sage: print are_mutually_orthogonal_latin_squares(MOLS)
        True
    """
    M = """
        abcdefghijkl abcdefghijkl abcdefghijkl abcdefghijkl abcdefghijkl
        badcfehgjilk ghefklijcdab dcbahgfelkji jilkbadcfehg klijcdabghef
        cdabghefklij efghijklabcd lkjidcbahgfe ijklabcdefgh fehgjilkbadc
        dcbahgfelkji cdabghefklij ghefklijcdab badcfehgjilk hgfelkjidcba
        ijklabcdefgh klijcdabghef efghijklabcd fehgjilkbadc jilkbadcfehg
        jilkbadcfehg fehgjilkbadc hgfelkjidcba dcbahgfelkji lkjidcbahgfe
        klijcdabghef hgfelkjidcba jilkbadcfehg cdabghefklij dcbahgfelkji
        lkjidcbahgfe ijklabcdefgh badcfehgjilk efghijklabcd ghefklijcdab
        efghijklabcd jilkbadcfehg fehgjilkbadc lkjidcbahgfe cdabghefklij
        fehgjilkbadc dcbahgfelkji cdabghefklij ghefklijcdab badcfehgjilk
        ghefklijcdab badcfehgjilk klijcdabghef hgfelkjidcba ijklabcdefgh
        hgfelkjidcba lkjidcbahgfe ijklabcdefgh klijcdabghef efghijklabcd
        """

    return _MOLS_from_string(M,5)

def MOLS_14_4():
    r"""
    Returns four MOLS of order 14

    These MOLS were shared by Ian Wanless.

    EXAMPLES::

        sage: from sage.combinat.designs.latin_squares import are_mutually_orthogonal_latin_squares
        sage: from sage.combinat.designs.database import MOLS_14_4
        sage: MOLS = MOLS_14_4()
        sage: print are_mutually_orthogonal_latin_squares(MOLS)
        True

    The design is available from the general constructor::

        sage: designs.mutually_orthogonal_latin_squares(4,14,existence=True)
        True
    """
    M = """
        bjihgkecalnfmd  bfmcenidgjhalk  bcdefghijklmna  bcdefghijklmna
        fckjbhledimagn  jcgndfalehkbim  gnkjdmiclbhaef  jflhnkaecmgdib
        mgdlkcbafejnih  ikdhaegnmfblcj  lifhbjemkangcd  emkdjbgfnliahc
        cnhemldbigfkaj  hjlebifkangcmd  dalmgnbjehcfik  anighmflkbdcej
        edabfnmkcjhgli  gbkmfcjeliahdn  njcaeifhbdgkml  kebcajimdgfhln
        nfeicgajldkbhm  khclngdafmjibe  mfbkcdlagnjihe  cgnflembihakjd
        iagfjdhnkmelcb  elbdmahfignkjc  aemnhkjdcifblg  ilabkdnhfcjegm
        dlnkeafimhcjbg  ceabkjnihdmgfl  hdnikbagmcelfj  ljgnihecbamfdk
        gemalfihjnbdkc  adficlkmjbenhg  cgjflhnbiekdam  ndmabcjglfeikh
        jhfnimgdbkacel  liegjdmhnkcfab  fkibmagenldhjc  mbhiefljadkncg
        hkbgajnmeclidf  nmjfhkecbaldgi  imhlneckdfajgb  difjcnkamehgbl
        ablchikgnfdmje  fankgbljdcimeh  klegafdnhjmcbi  ghckmlbdeinjaf
        licmdbjfhagenk  mgialhcbkedjnf  jhadicmlfgbekn  fajlgidkhncbme
        kmjdneclgbihfa  dnhjimbgclfeka  ebgcjlkfamindh  hkemdacngjblfi
        """

    return _MOLS_from_string(M,4)

def MOLS_15_4():
    r"""
    Returns 4 MOLS of order 15.

    These MOLS were shared by Ian Wanless.

    EXAMPLES::

        sage: from sage.combinat.designs.latin_squares import are_mutually_orthogonal_latin_squares
        sage: from sage.combinat.designs.database import MOLS_15_4
        sage: MOLS = MOLS_15_4()
        sage: print are_mutually_orthogonal_latin_squares(MOLS)
        True

    The design is available from the general constructor::

        sage: designs.mutually_orthogonal_latin_squares(4,15,existence=True)
        True
    """
    M = """
        bcdefghijklmnoa  bdgiknfcamehjlo  bhealiofmdjgcnk  blhcmdinejofakg
        abcdefghijklmno  acehjlogdbnfikm  lcifbmjagnekhdo  hcmidnejofkagbl
        oabcdefghijklmn  nbdfikmahecogjl  amdjgcnkbhoflie  midnjeofkaglbhc
        noabcdefghijklm  mocegjlnbifdahk  fbnekhdolciagmj  dnjeokfaglbhmci
        mnoabcdefghijkl  lnadfhkmocjgebi  kgcoflieamdjbhn  jeokfalgbhmcind
        lmnoabcdefghijk  jmobegilnadkhfc  olhdagmjfbnekci  ekfalgbmhcindjo
        klmnoabcdefghij  dknacfhjmobelig  jamiebhnkgcofld  aflgbmhcnidjoek
        jklmnoabcdefghi  helobdgiknacfmj  ekbnjfciolhdagm  lbgmhcnidojekaf
        ijklmnoabcdefgh  kifmacehjlobdgn  nflcokgdjamiebh  gmchnidojeakflb
        hijklmnoabcdefg  oljgnbdfikmaceh  iogmdalhekbnjfc  chndiojeakfblgm
        ghijklmnoabcdef  iamkhocegjlnbdf  djahnebmiflcokg  ndioejakfblgcmh
        fghijklmnoabcde  gjbnliadfhkmoce  hekbiofcnjgmdal  ioejafkblgcmhdn
        efghijklmnoabcd  fhkcomjbegilnad  miflcjagdokhneb  ojafkbglcmhdnie
        defghijklmnoabc  egildankcfhjmob  cnjgmdkbhealiof  fakbglchmdnieoj
        cdefghijklmnoab  cfhjmeboldgikna  gdokhnelcifbmja  kgblchmdineojfa
        """

    return _MOLS_from_string(M,4)

def MOLS_18_3():
    r"""
    Returns 3 MOLS of order 18.

    These MOLS were shared by Ian Wanless.

    EXAMPLES::

        sage: from sage.combinat.designs.latin_squares import are_mutually_orthogonal_latin_squares
        sage: from sage.combinat.designs.database import MOLS_18_3
        sage: MOLS = MOLS_18_3()
        sage: print are_mutually_orthogonal_latin_squares(MOLS)
        True

    The design is available from the general constructor::

        sage: designs.mutually_orthogonal_latin_squares(3,18,existence=True)
        True
    """
    M = """
        bgejhkmodcnarilpfq  beqpodgcflkrjahnim  bcdefghijklmnopqra
        echfbilnprdokajmqg  gcfrqpehdnmlabkioj  rbkamfgdehqjinopcl
        qfdigcjmohaeplkbnr  ehdgarqfibonmkcljp  mlbqhifgajdcrenopk
        prgejhdbnaikfqmlco  jfiehkargqcponldmb  hijbcdefgqraklmnop
        oqahfbiecpkjlgrnmd  hbgjfilkacrdqpomen  gderbkamfpclhqjino
        dprkigcjfeqlbmhaon  kichbgjmlodaerqpnf  fgamlbqhiopkjdcren
        geqaljhdbofrmcnikp  mljdichbngpekfarqo  efghijbcdnopqraklm
        chfrkmbieqpgandojl  onmbejdicphqflgkar  amfgderbkinopclhqj
        fdigalncjmrqhkoepb  dponcfbejaqirgmhlk  qhifgamlbrenopkjdc
        lnbqcogpakmhdrifej  crhapeoqmkbgidnjfl  leqjponacbkidfgmhr
        kmocrdphqblnieajgf  ndaikqfprmlchjeobg  kjmcrponhlbqeafgid
        rlnpdaeqigcmojfkbh  aoekjlrgqhnmdibfpc  dqriklponajbcmhfge
        jamoqekfrihdnpbglc  rkpflbmahdionejcgq  nacleqjpomhrbkidfg
        abknprflgdjieoqchm  ialqgmcnkrejpofbdh  onhkjmcrpgidlbqeaf
        hkcloqagmnebjfprdi  ljkmrhndoiafbqpgce  pondqriklfgeajbcmh
        nildmprkhjofcbgqae  pmblnaioefjkgcrqhd  jponacleqdfgmhrbki
        iojmenqalfbpgdchrk  fqncmokjpegblhdari  crponhkjmeafgidlbq
        mjpbnforklgcqhedia  qgrodnplbjfhcmieka  iklpondqrcmhfgeajb
        """

    return _MOLS_from_string(M,3)

# Index of the MOLS constructions
#
# Associates to n the pair (k,f) where f() is a function that returns k MOLS of order n
#
# This dictionary is used by designs.mutually_orthogonal_latin_squares(k,n).

MOLS_constructions = {
    10 : (2, MOLS_10_2),
    12 : (5, MOLS_12_5),
    14 : (4, MOLS_14_4),
    15 : (4, MOLS_15_4),
    18 : (3, MOLS_18_3)
}

def OA_7_18():
    r"""
    Returns an OA(7,18)

    Proved in [JulianAbel13]_.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_quasi_difference_matrix`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_7_18
        sage: OA = OA_7_18()
        sage: print is_orthogonal_array(OA,7,18,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(7,18,existence=True)
        True
    """
    M = """
        000 100 100 000 100 100 100 000 000 000 100 000
        000 020 100 100 000 120 110 110 010 020 010 120
        000 100 022 102 112 001 101 120 121 001 020 002
        000 002 100 002 102 122 010 111 110 121 021 001
        000 021 000 100 020 112 100 021 112 102 102 012
        000 000 011 010 100 010 110 122 011 121 120 111
        000 100 002 022 011 121 020 122 100 010 112 112
        """
    from sage.rings.finite_rings.integer_mod_ring import IntegerModRing as AdditiveCyclic
    from sage.categories.cartesian_product import cartesian_product
    G = cartesian_product([AdditiveCyclic(2),AdditiveCyclic(3),AdditiveCyclic(3)])
    M = [G(map(int,xxx)) for xxx in M.split()]
    M = [M[i*12:(i+1)*12] for i in range(7)]

    Mb = [[] for _ in range(7)]

    for a,b,c,d,e,f,g in zip(*M):
        for y in range(3):
            Mb[0].append(a + G((0,  0  , 0 )))
            Mb[1].append(b + G((0,  0  , y )))
            Mb[2].append(c + G((0,  y  , 0 )))
            Mb[3].append(d + G((0, 2*y , y )))
            Mb[4].append(e + G((0, 2*y ,2*y)))
            Mb[5].append(f + G((0,  y  ,2*y)))
            Mb[6].append(g + G((0,  0  ,2*y)))

    M = OA_from_quasi_difference_matrix(Mb,G,add_col=False)
    M = M[:len(M)/2] # only develop w.r.t the last two coordinates
    return M

def OA_6_20():
    r"""
    Returns an OA(6,20)

    As explained in the Handbook III.3.49 [DesignHandbook]_.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_quasi_difference_matrix`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_6_20
        sage: OA = OA_6_20()
        sage: print is_orthogonal_array(OA,6,20,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(6,20,existence=True)
        True
    """
    M=[[None,   7,  13,   1,  16,   9,   2],
       [   0,   1,  15,   7,  17,   6,  14],
       [   0,  11,  10,  11,   5,   4,   3],
       [   7,None,  13,  16,   1,   2,   9],
       [   1,   0,  15,  17,   7,  14,   6],
       [  11,   0,  10,   5,  11,   3,   4]]

    Mb=[[],[],[],[],[],[]]

    for R in zip(*M):
        a,b,c,d,e,f = R
        Mb[0].extend([a,b,c])
        Mb[1].extend([b,c,a])
        Mb[2].extend([c,a,b])
        Mb[3].extend([d,f,e])
        Mb[4].extend([e,d,f])
        Mb[5].extend([f,e,d])

    from sage.rings.finite_rings.integer_mod_ring import IntegerModRing as AdditiveCyclic
    M = OA_from_quasi_difference_matrix(Mb,AdditiveCyclic(19),add_col=False)

    return M

def OA_7_21():
    r"""
    Returns an OA(7,21)

    As explained in the Handbook III.3.50 [DesignHandbook]_.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_quasi_difference_matrix`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_7_21
        sage: OA = OA_7_21()
        sage: print is_orthogonal_array(OA,7,21,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(7,21,existence=True)
        True
    """
    M = [[  8,  17,  20,   2],
         [  9,  16,   4,  15],
         [ 11,   5,  10,   6],
         [ 14,   1,   3,  13],
         [ 18,  19,  12,   7]]

    Mb = [[0],[0],[0],[0],[0],[0]]
    for a,b,c,d,e in zip(*M):
        Mb[0].extend([a,b,c,d,e])
        Mb[1].extend([b,c,d,e,a])
        Mb[2].extend([c,d,e,a,b])
        Mb[3].extend([d,e,a,b,c])
        Mb[4].extend([e,a,b,c,d])
        Mb[5].extend([0,0,0,0,0])

    from sage.rings.finite_rings.integer_mod_ring import IntegerModRing as AdditiveCyclic
    M = OA_from_quasi_difference_matrix(Mb,AdditiveCyclic(21))
    return M

def OA_5_22():
    r"""
    Returns an OA(5,22)

    As explained in the Handbook III.3.51 [DesignHandbook]_.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_quasi_difference_matrix`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_5_22
        sage: OA = OA_5_22()
        sage: print is_orthogonal_array(OA,5,22,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(5,22,existence=True)
        True
    """
    from sage.rings.finite_rings.integer_mod_ring import IntegerModRing as AdditiveCyclic
    G = AdditiveCyclic(21)
    M = [
        [   1,  13,  18,   3,  16,  19,None],
        [  16,  19,   1,  13,  18,   3,   0],
        [  18,   3,  16,  19,   1,  13,   0],
        [   6,  15,   6,  15,   6,  15,   0],
        [  12,   9,  19,  16,   5,   2,   0],
        ]

    Mb=[[],[],[],[],[]]

    for R in zip(*M):
        a,b,c,d,e = [G(x) if x is not None else None for x in R]
        Mb[0].extend([a,16*c,4*b])
        Mb[1].extend([b,None if a is None else 16*a,4*c])
        Mb[2].extend([c,16*b,None if a is None else 4*a])
        Mb[3].extend([d,16*d+7,4*d+14])
        Mb[4].extend([e,16*e+14,4*e+7])

    Mb[0].extend([0,0])
    Mb[1].extend([7,14])
    Mb[2].extend([14,7])
    Mb[3].extend([None,0])
    Mb[4].extend([0,None])

    M = OA_from_quasi_difference_matrix(Mb,G,add_col=False)
    return M

def OA_9_24():
    r"""
    Returns an OA(9,24)

    As explained in the Handbook III.3.52 [DesignHandbook]_.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_quasi_difference_matrix`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_9_24
        sage: OA = OA_9_24()
        sage: print is_orthogonal_array(OA,9,24,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(9,24,existence=True)
        True
    """
    M = ("0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 "+
         "0000 0010 0100 0110 1000 1010 1100 1110 2000 2010 2100 2110 "+
         "0000 0011 1001 2110 0111 2011 2111 1000 0100 1100 1101 2010 "+
         "0000 1010 1011 2000 1101 2110 0001 0101 2100 2001 0111 1100 "+
         "0000 0001 2010 1111 2111 2100 1101 0011 1010 2101 1000 0110 "+
         "0000 1000 2001 1011 0100 1100 0110 2101 2111 0010 1111 2011 "+
         "0000 1001 0111 2100 2000 0010 1110 2011 1100 1011 0101 2111 "+
         "0000 1011 2101 0100 2110 1001 2000 0110 0101 1111 2011 1010 ")

    from sage.groups.additive_abelian.additive_abelian_group import AdditiveAbelianGroup
    G = AdditiveAbelianGroup([3,2,2,2])
    rlabel = {(x%2,x%3):x for x in range(6)}
    M = [G([int(c),int(d),rlabel[int(b),int(a)]]) for a,b,c,d in M.split()]
    M = [M[i*12:(i+1)*12] for i in range(8)]
    Mb = [[] for _ in range(8)]
    for a,b,c,d,e,f,g,h in zip(*M):
        Mb[0].extend([a, a + G([0,0,rlabel[0,0]])])
        Mb[1].extend([b, b + G([0,1,rlabel[0,0]])])
        Mb[2].extend([c, c + G([1,0,rlabel[0,0]])])
        Mb[3].extend([d, d + G([1,1,rlabel[0,0]])])
        Mb[4].extend([e, e + G([0,0,rlabel[1,0]])])
        Mb[5].extend([f, f + G([0,1,rlabel[1,0]])])
        Mb[6].extend([g, g + G([1,0,rlabel[1,0]])])
        Mb[7].extend([h, h + G([1,1,rlabel[1,0]])])

    M = OA_from_quasi_difference_matrix(Mb,G)
    return M

def OA_6_26():
    r"""
    Returns an OA(6,26)

    As explained in the Handbook III.3.53 [DesignHandbook]_.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_quasi_difference_matrix`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_6_26
        sage: OA = OA_6_26()
        sage: print is_orthogonal_array(OA,6,26,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(6,26,existence=True)
        True
    """
    M = [
        [None,None,None,None,None],
        [   0,   0,   0,   0,   0],
        [   1,   6,   7,   8,  14],
        [   3,  11,  20,  18,  10],
        [   6,  10,  14,   1,   5],
        [   4,  19,   5,  12,   2],
        ]

    from sage.rings.finite_rings.integer_mod_ring import IntegerModRing as AdditiveCyclic
    G = AdditiveCyclic(21)
    Mb=[[0],[0],[0],[0],[0],[0]]

    for R in zip(*M):
        a,b,c,d,e,f = R
        Mb[0].extend([a,b,c,d,e,f])
        Mb[1].extend([b,c,d,e,f,a])
        Mb[2].extend([c,d,e,f,a,b])
        Mb[3].extend([d,e,f,a,b,c])
        Mb[4].extend([e,f,a,b,c,d])
        Mb[5].extend([f,a,b,c,d,e])

    M = OA_from_quasi_difference_matrix(Mb,G,add_col = False)
    return M

def OA_7_28():
    r"""
    Returns an OA(7,28)

    As explained in the Handbook III.3.54 [DesignHandbook]_.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_quasi_difference_matrix`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_7_28
        sage: OA = OA_7_28()
        sage: print is_orthogonal_array(OA,7,28,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(7,28,existence=True)
        True
    """
    z=2
    M = [
        [(0,0), (z+1,6),(1,1)  ,(1,1)  ,(1,3)  ,(1,4)  ,(0,0)  ,(1,4), (z,5)  ],
        [(z,2), (0,0)  ,(1,5)  ,(z,1)  ,(z,2)  ,(z,6)  ,(z+1,3),(0,0), (z,1)  ],
        [(z,3), (z+1,4),(0,0)  ,(z+1,5),(z+1,2),(z+1,4),(z+1,2),(1,6), (0,0)  ],
        [(0,5), (z,6)  ,(0,5)  ,(0,6)  ,(z,3)  ,(0,0)  ,(0,4)  ,(1,5), (z+1,4)],
        [(0,3), (0,3)  ,(z+1,5),(0,0)  ,(0,5)  ,(z+1,6),(1,1)  ,(0,1), (z,3)  ],
        [(1,3), (0,6)  ,(0,6)  ,(1,5)  ,(0,0)  ,(0,3)  ,(z+1,6),(z,2), (0,2)  ],
        ]

    from sage.groups.additive_abelian.additive_abelian_group import AdditiveAbelianGroup
    from sage.modules.free_module_element import free_module_element as vector
    G = AdditiveAbelianGroup([2,2,7])
    M = [[G(vector([x//2,x%2,y])) for x,y in L] for L in M]

    Mb=[[0],[0],[0],[0],[0],[0]]

    for R in zip(*M):
        a,b,c,d,e,f = R
        Mb[0].extend([a,b,c])
        Mb[1].extend([b,c,a])
        Mb[2].extend([c,a,b])
        Mb[3].extend([d,f,e])
        Mb[4].extend([e,d,f])
        Mb[5].extend([f,e,d])

    M = OA_from_quasi_difference_matrix(Mb,G,add_col = True)
    return M

def OA_6_30():
    r"""
    Returns an OA(6,30)

    As explained in the Handbook III.3.55 [DesignHandbook]_.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_quasi_difference_matrix`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_6_30
        sage: OA = OA_6_30()
        sage: print is_orthogonal_array(OA,6,30,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(6,30,existence=True)
        True
    """
    M = [
        [(0,0),None,(0,0),(0,0),(0,0),(0,0),(0,0)],
        [(0,0),(0,0),None,(0,4),(0,2),(0,3),(0,1)],
        [(0,0),(3,1),(3,0),None,(4,0),(1,0),(2,0)],
        [(0,0),(3,0),(0,2),(1,2),None,(0,1),(0,3)],
        [(0,0),(3,3),(1,2),(4,2),(2,0),None,(0,4)],
        [(0,0),(4,2),(2,4),(0,3),(2,3),(3,2),None]
        ]

    from sage.groups.additive_abelian.additive_abelian_group import AdditiveAbelianGroup
    from sage.modules.free_module_element import free_module_element as vector
    G = AdditiveAbelianGroup([5,5])
    M = [[None if x is None else G(vector(x)) for x in L] for L in M]

    Mb=[[],[],[],[],[],[]]

    for R in zip(*M):
        a,b,c,d,e,f = R
        for i in range(5):
            Mb[0].append(None if a is None else a+G(vector((i,i))))
            Mb[1].append(None if b is None else b+G(vector((2*i,i))))
            Mb[2].append(None if c is None else c+G(vector((i,0))))
            Mb[3].append(None if d is None else d+G(vector((4*i,0))))
            Mb[4].append(None if e is None else e+G(vector((3*i,4*i))))
            Mb[5].append(None if f is None else f+G(vector((4*i,4*i))))

    M = OA_from_quasi_difference_matrix(Mb,G,add_col = False)
    return M

def OA_7_33():
    r"""
    Returns an OA(7,33)

    As explained in the Handbook III.3.56 [DesignHandbook]_.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_quasi_difference_matrix`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_7_33
        sage: OA = OA_7_33()
        sage: print is_orthogonal_array(OA,7,33,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(7,33,existence=True)
        True
    """
    M = [
        [   0,   0,   0,   0,   0,   0],
        [  15,  11,  22,   4,  17,   8],
        [  19,   7,  14,  32,  22,  18],
        [  22,  19,   8,  24,  21,   6],
        [   9,  12,  15,   7,  26,  14],
        [  14,  28,  23,   2,  19,   3]
        ]

    from sage.rings.finite_rings.integer_mod_ring import IntegerModRing as AdditiveCyclic
    G = AdditiveCyclic(33)

    Mb=[[0,1,7],[0,4,28],[0,16,13],[0,31,19],[0,25,10],[0,22,0]]

    for R in zip(*M):
        a,b,c,d,e,f = R
        for i in range(5):
            Mb[0].append(a)
            Mb[1].append(b)
            Mb[2].append(c)
            Mb[3].append(d)
            Mb[4].append(e)
            Mb[5].append(f)
            a,b,c,d,e,f = 4*e,4*a,4*b,4*c,4*d,4*f

    M = OA_from_quasi_difference_matrix(Mb,G,add_col = True)
    return M

def OA_6_34():
    r"""
    Returns an OA(6,34)

    As explained in the Handbook III.3.57 [DesignHandbook]_.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_quasi_difference_matrix`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_6_34
        sage: OA = OA_6_34()
        sage: print is_orthogonal_array(OA,6,34,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(6,34,existence=True)
        True
    """
    M = [
        [None,   0,   0,   0,   0,   0],
        [  30,  17,  10,  25,  23,   8],
        [  22,   4,  32,  29,  28,  22],
        [  25,  10,  20,  15,  21,  16],
        [   0,  12,  15,  16,  32,  23],
        [   6,  11,  18,  14,   9,  20]
        ]

    from sage.rings.finite_rings.integer_mod_ring import IntegerModRing as AdditiveCyclic
    G = AdditiveCyclic(33)

    Mb=[[0,1,3,10,5],[0,4,12,7,20],[0,16,15,28,14],[0,31,27,13,23],[0,25,9,19,26],[0,11,11,0,None]]

    times4 = lambda x : None if x is None else 4*x
    for R in zip(*M):
        a,b,c,d,e,f = [None if x is None else G(x) for x in R]
        for i in range(5):
            Mb[0].append(a)
            Mb[1].append(b)
            Mb[2].append(c)
            Mb[3].append(d)
            Mb[4].append(e)
            Mb[5].append(f)
            a,b,c,d,e,f = map(times4,[e,a,b,c,d,f])

    M = OA_from_quasi_difference_matrix(Mb,G,add_col = False)
    return M

def OA_7_35():
    r"""
    Returns an OA(7,35)

    As explained in the Handbook III.3.58 [DesignHandbook]_.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_quasi_difference_matrix`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_7_35
        sage: OA = OA_7_35()
        sage: print is_orthogonal_array(OA,7,35,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(7,35,existence=True)
        True
    """
    M = [
        [  0, 15, 30, 10, 25,  1, 16, 31, 11, 26,  2, 17, 32, 12,  6,  3, 18, 33, 27, 21,  4, 19, 13,  7, 22,  5, 34, 28,  8, 23, 20, 14, 29,  9, 24],
        [  0, 22, 16,  3,  4,  9, 10, 32, 26, 13, 18,  5, 27, 14, 15, 20,  7,  1, 23, 31, 29,  2, 24, 11, 19, 17, 25, 12,  6, 28, 33, 34, 21,  8, 30],
        [  0, 29,  2, 31, 18, 10, 32, 26, 34, 28, 27, 21, 15,  9, 17, 30,  3,  4,  5, 20, 12,  6, 14, 22, 16,  8, 23, 24, 25, 33, 11, 19, 13,  7,  1],
        [  0,  8,  9, 17, 11, 25, 19, 27, 28,  1, 15, 23, 31,  4, 26, 12,  6, 14, 29, 16,  2,  3, 18, 33, 34, 20,  7, 22, 30, 24, 10, 32,  5, 13, 21],
        [  0,  1, 23, 24, 32, 33,  6,  7, 29, 30, 10, 11, 12, 13, 28,  8,  9, 31,  4,  5, 27, 14, 15, 16,  3, 25, 26, 34, 21, 22,  2, 17, 18, 19, 20],
        [0]*35
        ]

    from sage.rings.finite_rings.integer_mod_ring import IntegerModRing as AdditiveCyclic
    G = AdditiveCyclic(35)

    M = OA_from_quasi_difference_matrix(M,G,add_col = True)
    return M

def OA_10_36():
    r"""
    Returns an OA(10,36)

    As explained in the Handbook III.3.59 [DesignHandbook]_.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_quasi_difference_matrix`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_10_36
        sage: OA = OA_10_36()
        sage: print is_orthogonal_array(OA,10,36,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(10,36,existence=True)
        True
    """
    M = [
        [(0,0,0,0), (0,0,0,0), (0,0,0,0), (0,0,0,0), (0,0,0,0), (0,0,0,0), (0,0,0,0), (0,0,0,0), (0,0,0,0), (0,0,0,0), (0,0,0,0), (0,0,0,0)],
        [(0,0,0,0), (0,1,0,0), (1,0,0,0), (1,1,0,0), (0,0,0,1), (0,1,0,1), (1,0,0,1), (1,1,0,1), (0,0,0,2), (0,1,0,2), (1,0,0,2), (1,1,0,2)],
        [(0,0,0,0), (1,1,1,2), (0,0,2,1), (0,0,1,2), (0,1,2,0), (0,1,0,2), (1,1,1,1), (0,1,1,1), (1,1,1,0), (1,0,2,2), (1,0,0,1), (1,0,1,0)],
        [(0,0,0,0), (0,0,1,0), (1,0,1,0), (0,1,0,0), (1,1,0,0), (1,0,2,0), (1,0,0,0), (0,1,2,0), (1,1,2,0), (0,0,2,0), (1,1,1,0), (0,1,1,0)],
        [(0,0,0,0), (0,1,2,0), (0,0,1,0), (1,1,1,0), (1,0,2,0), (1,0,1,0), (0,1,0,0), (0,0,2,0), (0,1,1,0), (1,1,0,0), (1,1,2,0), (1,0,0,0)],
        [(0,0,0,0), (0,1,1,0), (0,1,2,0), (1,1,2,0), (1,1,0,2), (0,0,1,2), (1,1,2,2), (1,0,0,2), (1,0,0,1), (1,0,1,1), (0,0,2,1), (0,1,1,1)],
        [(0,0,0,0), (1,0,1,0), (1,1,0,1), (1,0,1,2), (1,0,2,2), (0,0,2,1), (0,1,0,1), (0,1,0,0), (1,1,2,2), (0,1,1,0), (0,0,1,2), (1,1,2,1)],
        [(0,0,0,0), (1,1,0,0), (0,1,1,0), (1,0,2,1), (0,1,0,2), (1,0,2,2), (0,0,2,2), (1,1,1,0), (1,0,1,1), (0,1,2,1), (1,1,1,1), (0,0,0,2)],
        [(0,0,0,0), (1,0,0,0), (1,1,1,0), (0,1,1,2), (1,1,2,1), (0,1,1,1), (0,0,1,1), (1,0,2,0), (0,1,2,2), (1,1,0,2), (1,0,2,2), (0,0,0,1)]
        ]

    from sage.groups.additive_abelian.additive_abelian_group import AdditiveAbelianGroup
    from sage.modules.free_module_element import free_module_element as vector
    G = AdditiveAbelianGroup([2,2,3,3])
    M = [[G(vector(x)) for x in L] for L in M]

    Mb=[[],[],[],[],[],[],[],[],[]]

    for R in zip(*M):
        a,b,c,d,e,f,g,h,i = R
        for y in range(3):
            Mb[0].append(a+G(vector([0,0,0,0])))
            Mb[1].append(b+G(vector([0,0,y,0])))
            Mb[2].append(c+G(vector([0,0,2*y,0])))
            Mb[3].append(d+G(vector([0,0,0,y])))
            Mb[4].append(e+G(vector([0,0,0,2*y])))
            Mb[5].append(f+G(vector([0,0,y,y])))
            Mb[6].append(g+G(vector([0,0,2*y,2*y])))
            Mb[7].append(h+G(vector([0,0,y,2*y])))
            Mb[8].append(i+G(vector([0,0,2*y,y])))

    M = OA_from_quasi_difference_matrix(Mb,G,add_col = True)
    return M

def OA_6_38():
    r"""
    Returns an OA(6,38)

    As explained in the Handbook III.3.60 [DesignHandbook]_.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_quasi_difference_matrix`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_6_38
        sage: OA = OA_6_38()
        sage: print is_orthogonal_array(OA,6,38,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(6,38,existence=True)
        True
    """
    M = [
        [None,  10,   1,   2,   6,   3,  22,   5,   7,   9,  14,  18,  28],
        [   0,   1,  10,  20,  23,  30,  35,  13,  33,  16,  29,  32,  21],
        [   0,  26,  26,  15,   8,   4,  17,  19,  34,  12,  31,  24,  25],
        [  10,None,  10,   6,   2,  22,   3,   7,   5,  14,   9,  28,  18],
        [   1,   0,  26,  23,  20,  35,  30,  33,  13,  29,  16,  21,  32],
        [  26,   0,   1,   8,  15,  17,   4,  34,  19,  31,  12,  25,  24]
        ]

    from sage.rings.finite_rings.integer_mod_ring import IntegerModRing as AdditiveCyclic
    G = AdditiveCyclic(37)

    Mb=[[],[],[],[],[],[]]

    for R in zip(*M):
        a,b,c,d,e,f = R
        Mb[0].extend([a,b,c])
        Mb[1].extend([b,c,a])
        Mb[2].extend([c,a,b])
        Mb[3].extend([d,f,e])
        Mb[4].extend([e,d,f])
        Mb[5].extend([f,e,d])

    M = OA_from_quasi_difference_matrix(Mb,G,add_col = False)
    return M

def OA_7_39():
    r"""
    Returns an OA(7,39)

    As explained in the Handbook III.3.61 [DesignHandbook]_.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_quasi_difference_matrix`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_7_39
        sage: OA = OA_7_39()
        sage: print is_orthogonal_array(OA,7,39,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(7,39,existence=True)
        True
    """
    M = [
        [   0,   0,   0,   0,   0,   0],
        [   4,  23,  13,   5,  12,  11],
        [  25,  11,  22,  34,  23,   6],
        [  13,   4,  20,  17,  15,  29],
        [  27,  21,   8,  16,  19,  26],
        [  16,  19,  34,  38,  26,  21]
        ]

    from sage.rings.finite_rings.integer_mod_ring import IntegerModRing as AdditiveCyclic
    G = AdditiveCyclic(39)

    Mb=[[0,1,-1],[0,16,-16],[0,22,-22],[0,17,-17],[0,38,-38],[0,23,-23]]

    for R in zip(*M):
        a,b,c,d,e,f = [None if x is None else G(x) for x in R]
        for i in range(3):
            Mb[0].extend([a,-a])
            Mb[1].extend([b,-b])
            Mb[2].extend([c,-c])
            Mb[3].extend([d,-d])
            Mb[4].extend([e,-e])
            Mb[5].extend([f,-f])
            a,b,c,d,e,f = [16*x for x in [c,a,b,f,d,e]]

    M = OA_from_quasi_difference_matrix(Mb,G,add_col = True)
    return M

def OA_9_40():
    r"""
    Returns an OA(9,40)

    As explained in the Handbook III.3.62 [DesignHandbook]_.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_quasi_difference_matrix`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_9_40
        sage: OA = OA_9_40()
        sage: print is_orthogonal_array(OA,9,40,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(9,40,existence=True)
        True
    """

    A = [
        [(0,None),(0,None),(0,None),(0,None),(0,None),(0,None),(0,None),(0,None),(0,None),(0,None)],
        [(0,None),(1,None),   (2,2),   (3,2),   (4,2),(2,None),(3,None),(4,None),   (0,2),   (1,2)],
        [(0,None),   (2,5),   (4,5),   (1,2),   (3,6),   (3,4),   (0,0),   (2,1),   (4,1),   (1,6)],
        [(0,None),   (3,4),   (1,4),   (4,0),   (2,5),(3,None),   (1,0),   (4,1),   (2,2),   (0,3)],
        [(0,None),   (4,6),(3,None),   (2,3),   (1,4),   (2,1),(1,None),   (0,4),   (4,0),   (3,2)],
        [(0,None),   (1,2),   (4,6),   (4,4),   (1,0),   (0,6),   (2,3),   (3,6),   (3,5),   (2,5)],
        [(1,None),   (0,3),   (1,2),   (4,5),(4,None),   (2,3),   (0,0),   (2,2),   (3,0),(3,None)],
        [(4,None),   (1,3),   (0,0),   (1,1),   (4,0),   (3,1),   (2,5),(0,None),   (2,1),(3,None)]
        ]
    Y = [None, 0, 1, 6, 5, 4, 3, 2]

    return _helper_function_when_n_is_prime_times_power_of_2(9,40,A,Y)

def OA_7_42():
    r"""
    Returns an OA(7,42)

    As explained in the Handbook III.3.63 [DesignHandbook]_.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_quasi_difference_matrix`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_7_42
        sage: OA = OA_7_42()
        sage: print is_orthogonal_array(OA,7,42,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(7,42,existence=True)
        True
    """
    M = [
        [None,None,None,None,None,None,None],
        [   0,   0,   0,   0,   0,   0,   0],
        [  18, -18,  11, -11,   5,  -5,   4],
        [  26, -26,  10, -10,  30, -30,  23],
        [  20, -20,   3,  -3,  33, -33,  23],
        [   5,  -5,  25, -25,  24, -24,   4],
        [  17, -17,   4,  -4,  22, -22,   0]
        ]

    from sage.rings.finite_rings.integer_mod_ring import IntegerModRing as AdditiveCyclic
    G = AdditiveCyclic(35)

    Mb=[[],[],[],[],[],[],[]]

    for R in zip(*M):
        for i in range(7):
            Mb[i].extend(cyclic_shift(R,i))

    M = OA_from_quasi_difference_matrix(Mb,G,add_col = False)
    return M

def OA_7_44():
    r"""
    Returns an OA(7,44)

    As explained in the Handbook III.3.64 [DesignHandbook]_.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_quasi_difference_matrix`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_7_44
        sage: OA = OA_7_44()
        sage: print is_orthogonal_array(OA,7,44,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(7,44,existence=True)
        True
    """
    from sage.rings.finite_rings.integer_mod_ring import IntegerModRing as AdditiveCyclic
    from sage.categories.cartesian_product import cartesian_product

    G2 = AdditiveCyclic(2)
    G11 = AdditiveCyclic(11)
    G2211 = cartesian_product((G2,G2,G11))

    M = [
        [(0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0)],
        [(1,1,4), (0,1,4), (1,1,7), (1,0,6), (1,1,9), (0,1,2), (0,1,5), (0,1,1)],
        [(1,0,6), (0,1,3), (1,0,0), (0,1,9), (1,1,1), (0,1,4), (1,1,9), (1,0,9)],
        [(1,1,6), (1,1,9), (0,1,2), (1,1,0), (0,1,0), (1,1,5), (0,0,4), (0,0,9)],
        [(1,0,9), (0,0,2), (0,0,1), (1,0,2), (0,0,7), (1,1,6), (1,1,0), (1,0,7)],
        [(1,0,1), (1,0,6), (1,1,3), (0,1,5), (0,0,5), (0,1,3), (0,1,0), (1,1,0)]
        ]

    M = [[G2211(x) for x in L] for L in M]

    Mb=[[],[],[],[],[],[]]

    for R in zip(*M):
        for c in range(5):
            (x1,y1,z1),(x2,y2,z2),(x3,y3,z3),(x4,y4,z4),(x5,y5,z5),(x6,y6,z6) = R
            for i,e in enumerate(R):
                Mb[i].append(e)
            R = [(x5,y5,5*z5),
                 (x1,y1,5*z1),
                 (x2,y2,5*z2),
                 (x3,y3,5*z3),
                 (x4,y4,5*z4),
                 (x6,y6,5*z6)]

    for x,y,z in [(0,0,0), (1,0,1),(1,1,2),(0,0,8)]:
        Mb[0].append((x,y,z))
        Mb[1].append((x,y,5*z))
        Mb[2].append((x,y,3*z))
        Mb[3].append((x,y,4*z))
        Mb[4].append((x,y,9*z))
        Mb[5].append((0,0,0))

    M = OA_from_quasi_difference_matrix(Mb,G2211,add_col = True)
    return M

def OA_8_45():
    r"""
    Returns an OA(8,45)

    As explained in the Handbook III.3.65 [DesignHandbook]_.

    ... whose description contained a very deadly typo, kindly fixed by Julian
    R. Abel.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_quasi_difference_matrix`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_8_45
        sage: OA = OA_8_45()
        sage: print is_orthogonal_array(OA,8,45,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(8,45,existence=True)
        True
    """
    from sage.rings.finite_rings.constructor import FiniteField
    from sage.categories.cartesian_product import cartesian_product

    G533 = cartesian_product((FiniteField(5),FiniteField(3),FiniteField(3)))

    M = [
        [(0,0,0), (2,2,1), (3,1,1), (4,1,2), (4,0,1), (0,1,1), (0,2,1), (3,2,2)],
        [(0,0,0), (1,2,1), (4,2,2), (1,2,0), (4,1,0), (3,1,1), (3,0,0), (2,1,2)],
        [(0,0,0), (4,1,1), (2,2,1), (3,2,0), (1,2,0), (2,1,0), (1,0,0), (3,2,1)],
        [(0,0,0), (0,1,0), (2,1,1), (4,0,0), (0,0,2), (4,2,2), (3,2,2), (1,2,2)],
        [(0,0,0), (3,1,2), (2,1,0), (0,2,2), (4,2,1), (0,2,1), (2,0,1), (1,1,2)],
        [(0,0,0), (2,1,1), (1,2,2), (3,0,1), (2,0,1), (1,0,0), (4,2,1), (1,1,0)],
        [(0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0)]
        ]

    for i in range(6):
        M[i].extend(M[5-i][1:8])

    M[6].extend(M[6][1:8])

    Mb=[[],[],[],[],[],[],[]]

    for R in zip(*M):
        (x1,y1,z1),(x2,y2,z2),(x3,y3,z3),(x4,y4,z4),(x5,y5,z5),(x6,y6,z6),(x7,y7,z7) = R
        for i in range(3):
            Mb[0].append((x1, y1    , z1+i  ))
            Mb[1].append((x2, y2+2*i, z2    ))
            Mb[2].append((x3, y3+i  , z3+2*i))
            Mb[3].append((x4, y4+2*i, z4+i  ))
            Mb[4].append((x5, y5+i  , z5    ))
            Mb[5].append((x6, y6    , z6+2*i))
            Mb[6].append((x7, y7    , z7    ))

    M = OA_from_quasi_difference_matrix(Mb,G533,add_col = True)
    return M

def OA_6_46():
    r"""
    Returns an OA(6,46)

    As explained in the Handbook III.3.66 [DesignHandbook]_.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_Vmt`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_6_46
        sage: OA = OA_6_46()
        sage: print is_orthogonal_array(OA,6,46,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(6,46,existence=True)
        True
    """
    M = OA_from_Vmt(4,9,[0, 1, 3, 2, 8])
    return M

def OA_10_48():
    r"""
    Returns an OA(10,48)

    As explained in the Handbook III.3.67 [DesignHandbook]_.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_quasi_difference_matrix`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_10_48
        sage: OA = OA_10_48()
        sage: print is_orthogonal_array(OA,10,48,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(10,48,existence=True)
        True
    """
    from sage.rings.finite_rings.constructor import FiniteField
    F16 = FiniteField(16,prefix='x',conway=True)
    F3 = FiniteField(3)
    F3F16 = F3.cartesian_product(F16)
    w = F16.gens()[0]
    assert w**4 == w+1

    A = [
        [ (0, 4), (2, 2),  (2,2), (0,13),  (0,4), (2,13),  (0,1),  (0,7), (1,7) , (2,2) ,  (0,6),  (2,9)],
        [ (2, 7), (0, 9),  (2,7), (2,3) ,  (0,3), (0,9) , (1,12),  (0,6), (0,12), (2,14),  (2,7), (0,11)],
        [ (2,12), (2,12), (0,14), (0,14),  (2,8), (0,8) ,  (0,2),  (1,2), (0,11), (0,1) ,  (2,4), (2,12)],
        [ (1, 3), (0, 2), (0,10), (0,14),  (0,9), (1,3) , (0,12), (2,13), (2,1) , (2,9) ,  (2,0),  (1,7)],
        [ (0, 0), (1, 8),  (0,7), (1,8) ,  (0,4), (0,14),  (2,6),  (0,2), (2,3) , (1,12), (2,14),  (2,5)],
        [ (0,12), (0, 5), (1,13), (0,4) , (1,13), (0,9) ,  (2,8), (2,11), (0,7) , (2,10),  (1,2),  (2,4)],
        [ (1,12), (2, 0), (1,14), (0,6) ,  (1,9), (0,14),  (1,4),  (0,5), (1,8) , (1,3) ,  (2,1),  (1,1)],
        [ (1, 4), (1, 2),  (2,5), (0,4) , (0,11), (1,14), (1,13),  (1,9), (0,10), (1,6) ,  (1,8),  (2,6)],
        [ (2,10), (1, 9),  (1,7), (1,4) ,  (0,9), (0,1) ,  (0,0),  (1,3), (1,14), (2,11), (1,11), (1,13)],
        ]

    A = [[F3F16((F3(a),w**b)) for a,b in L] for L in A]

    Mb = [[] for _ in range(9)]
    for L in zip(*A):
        for i,e in enumerate(L):
            Mb[i].append(e)

        for u in [0,1,4]:
            V = [12,2,7,0,5,10,3,8,13]
            for i,(e,x) in enumerate(zip(L,V)):
                Mb[i].append(e+F3F16((F3(0),w**(x+u))))

    M = OA_from_quasi_difference_matrix(Mb,F3F16,add_col = True)
    return M

def OA_8_50():
    r"""
    Returns an OA(8,50)

    As explained in the Handbook III.3.68 [DesignHandbook]_.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_Vmt`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_8_50
        sage: OA = OA_8_50()
        sage: print is_orthogonal_array(OA,8,50,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(8,50,existence=True)
        True
    """
    M = OA_from_Vmt(6,7,[0, 1, 3, 16, 35, 26, 36])
    return M

def OA_7_51():
    r"""
    Returns an OA(7,51)

    As explained in the Handbook III.3.69 [DesignHandbook]_.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_quasi_difference_matrix`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_7_51
        sage: OA = OA_7_51()
        sage: print is_orthogonal_array(OA,7,51,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(7,51,existence=True)
        True
    """
    from sage.rings.finite_rings.integer_mod_ring import IntegerModRing as AdditiveCyclic
    G = AdditiveCyclic(51)

    M = [
        [   5,  33,  29,  30,   1],
        [   8,   3,  47,  10,  13],
        [  14,  27,   6,  12,  28],
        [   9,  16,  44,  49,  11],
        [  34,  32,  36,  26,  20]
        ]

    Mb=[[0],[0],[0],[0],[0],[0]*51]

    for R in zip(*M):
        for i in range(5):
            for RR in [R, [-x for x in R]]:
                for i,x in enumerate(RR):
                    Mb[i].append(x)
            R = cyclic_shift(R,1)

    M = OA_from_quasi_difference_matrix(Mb,G,add_col = True)
    return M

def OA_7_52():
    r"""
    Returns an OA(7,52)

    As explained in the Handbook III.3.70 [DesignHandbook]_.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_quasi_difference_matrix`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_7_52
        sage: OA = OA_7_52()
        sage: print is_orthogonal_array(OA,7,52,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(7,52,existence=True)
        True
    """
    from sage.rings.finite_rings.integer_mod_ring import IntegerModRing as AdditiveCyclic
    from sage.rings.finite_rings.constructor import FiniteField
    F4  = FiniteField(4,prefix='z',conway=True)
    G13 = FiniteField(13)
    G = F4.cartesian_product(G13)
    z = F4.gens()[0]
    assert z**2 == z+1

    M = [
        [    (0,0),    (0,0),    (0,0),    (0,0),   (0,0)],
        [(z**2,10),    (0,7),   (1,10),   (z,10),(z**2,3)],
        [   (z,10), (z**2,2),   (1,11),    (z,2),(z**2,7)],
        [    (z,8),(z**2,12),   (0,10),(z**2,11),(z**2,6)],
        [    (1,2),    (0,2), (z**2,8),    (z,3),   (z,7)],
        [    (1,6),   (z,12),    (0,7), (z**2,6),   (z,2)]
        ]

    M2 = [
        [    (1,1),(z**2,11)],
        [    (z,3),    (1,7)],
        [ (z**2,9),    (z,8)],
        [    (1,4), (z**2,3)],
        [   (z,12),    (1,9)],
        [(z**2,10),    (z,1)]
        ]

    M = [[G(x) for x in L] for L in M]
    M2= [[G(x) for x in L] for L in M2]

    Mb=[[(0,0)]*6]

    from itertools import product
    p = lambda x,y : G(tuple([x*yy for yy in G(y)]))

    def t1(i,R):
        if i > 1:
            return t1(1,t1(i-1,R))
        ((x1,y1),(x2,y2),(x3,y3),(x4,y4),(x5,y5),(x6,y6)) = R
        return [(z*x3, 3*y3), (z*x1, 3*y1), (z*x2, 3*y2), (z*x6, 3*y6), (z*x4, 3*y4), (z*x5, 3*y5)]

    def t2(i,R):
        if i > 1:
            return t2(1,t2(i-1,R))
        ((x1,y1),(x2,y2),(x3,y3),(x4,y4),(x5,y5),(x6,y6)) = R
        return [(  x3,   y3), (  x1,   y1), (  x2,   y2), (  x5,   y5), (  x6,   y6), (  x4,   y4)]

    for R in zip(*M):
        for c1,c2 in product([1,2,3],repeat=2):
            Mb.append(t2(c2,t1(c1,R)))

    for R in zip(*M2):
        for c2 in [1,2,3]:
            Mb.append(t2(c2,R))

    Mb = zip(*Mb)
    M = OA_from_quasi_difference_matrix(Mb,G,add_col = True)
    return M

def OA_7_54():
    r"""
    Returns an OA(7,54)

    As explained in the Handbook III.3.71 [DesignHandbook]_.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_quasi_difference_matrix`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_7_54
        sage: OA = OA_7_54()
        sage: print is_orthogonal_array(OA,7,54,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(7,54,existence=True)
        True
    """
    from sage.rings.finite_rings.integer_mod_ring import IntegerModRing as AdditiveCyclic
    G = AdditiveCyclic(45)

    M = [
        [None,None,None,None,None,None,None,None,None],
        [   0,   0,   0,   0,   0,   0,   0,   0,   0],
        [   1,  27,  16,   7,  -1, -27, -16,  -7,   3],
        [  24,  40,   1,  35, -24, -40,  -1, -35,   7],
        [  10,  30,  22,  44, -10, -30, -22, -44,   7],
        [   5,  18,  14,  33,  -5, -18, -14, -33,   3],
        [  30,  16,  33,  27, -30, -16, -33, -27,   0],
        ]

    Mb=[[] for _ in range(7)]

    for R in zip(*M):
        for c in range(7):
            for i,x in enumerate(cyclic_shift(R,c)):
                Mb[i].append(x)

    M = OA_from_quasi_difference_matrix(Mb,G,add_col = False)
    return M

def OA_8_55():
    r"""
    Returns an OA(8,55)

    As explained in the Handbook III.3.72 [DesignHandbook]_.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_quasi_difference_matrix`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_8_55
        sage: OA = OA_8_55()
        sage: print is_orthogonal_array(OA,8,55,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(8,55,existence=True)
        True
    """
    from sage.rings.finite_rings.integer_mod_ring import IntegerModRing as AdditiveCyclic
    G = AdditiveCyclic(55)

    M = [
        [ 1  ,  7 , 14 , 19 , 28 , 33 , 40 , 46 , 50],
        [ 2  , 13 , 25 , 38 , 52 , 12 , 20 , 32 , 45],
        [ 39 , 6  ,  8 , 26 , 24 , 51 , 11 , 34 , 37],
        [ 54 , 48 , 41 , 36 , 27 , 22 , 15 , 9  ,  5],
        [ 53 , 42 , 30 , 17 , 3  , 43 , 35 , 23 , 10],
        [ 16 , 49 , 47 , 29 , 31 , 4  , 44 , 21 , 18]
        ]

    Mb=[[0],[0],[0],[0],[0],[0],[0]*55]

    for R in zip(*M):
        for c in range(6):
            for i,x in enumerate(cyclic_shift(R,c)):
                Mb[i].append(x)

    M = OA_from_quasi_difference_matrix(Mb,G,add_col = True)
    return M


def OA_9_56():
    r"""
    Returns an OA(9,56)

    As explained in the Handbook III.3.73 [DesignHandbook]_.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_quasi_difference_matrix`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_9_56
        sage: OA = OA_9_56()
        sage: print is_orthogonal_array(OA,9,56,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(9,56,existence=True)
        True
    """
    from sage.rings.finite_rings.constructor import FiniteField
    F8  = FiniteField(8,prefix='w',conway=True)
    F7  = FiniteField(7)
    G   = F8.cartesian_product(F7)

    w = F8.gens()[0]
    assert w**3 == w+1

    M = [
        [(0,0), (w**0,0), (w**1,0), (w**2,0), (w**3,0), (w**4,0), (w**5,0), (w**6,0)],
        [(0,1), (w**1,6), (w**2,1), (w**3,1), (w**4,6), (w**5,1), (w**6,6), (w**0,6)],
        [(0,4), (w**2,3), (w**3,4), (w**4,4), (w**5,3), (w**6,4), (w**0,3), (w**1,3)],
        [(0,2), (w**3,5), (w**4,2), (w**5,2), (w**6,5), (w**0,2), (w**1,5), (w**2,5)],
        [(0,2), (w**4,5), (w**5,2), (w**6,2), (w**0,5), (w**1,2), (w**2,5), (w**3,5)],
        [(0,4), (w**5,3), (w**6,4), (w**0,4), (w**1,3), (w**2,4), (w**3,3), (w**4,3)],
        [(0,1), (w**6,6), (w**0,1), (w**1,1), (w**2,6), (w**3,1), (w**4,6), (w**5,6)],
        [(1,0), (   1,0), (   1,0), (   1,0), (   1,0), (   1,0), (   1,0), (   1,0)]
        ]

    Mb=[[] for _ in range(8)]

    for R in zip(*M):
        for _ in range(7):
            for i,e in enumerate(R):
                Mb[i].append(e)
            (x1,y1),(x2,y2),(x3,y3),(x4,y4),(x5,y5),(x6,y6),(x7,y7),(x8,y8) = R
            R = [(w*x7,y7), (w*x1,y1), (w*x2,y2), (w*x3,y3), (w*x4,y4), (w*x5,y5), (w*x6,y6), (w*x8,y8)]

    M = OA_from_quasi_difference_matrix(Mb,G,add_col = True)
    return M

def OA_9_57():
    r"""
    Returns an OA(9,57)

    Given by Julian R. Abel.

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_9_57
        sage: OA = OA_9_57()
        sage: print is_orthogonal_array(OA,9,57,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(9,57,existence=True)
        True
    """
    M = orthogonal_array(8,8)
    M = [R for R in M if any(x!=R[0] for x in R)] # removing the 0..0, 1..1, 7..7 rows.
    B = (1,6,7,9,19,38,42,49) # base block of a (57,8,1) BIBD
    M = [[B[x] for x in R] for R in M]
    M.append([0]*8)
    Mb = zip(*M)

    from sage.rings.finite_rings.integer_mod_ring import IntegerModRing as AdditiveCyclic
    G = AdditiveCyclic(57)
    M = OA_from_quasi_difference_matrix(Mb,G,add_col=True)
    return M

def OA_7_60():
    r"""
    Returns an OA(7,60)

    As explained in [JulianAbel13]_.

    REFERENCES:

    .. [JulianAbel13] Existence of Five MOLS of Orders 18 and 60
      R. Julian R. Abel
      Journal of Combinatorial Designs
      2013

    http://onlinelibrary.wiley.com/doi/10.1002/jcd.21384/abstract

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_quasi_difference_matrix`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_7_60
        sage: OA = OA_7_60()
        sage: print is_orthogonal_array(OA,7,60,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(7,60,existence=True)
        True
    """
    M60 = [[(0,  0), (0, 0), (0,  0), (0,  0), (0,  0), (0,  0), (0,  0), (0,  0), (0,  0), (0,  0)],
           [(1, 10), (1, 6), (0, 17), (0,  7), (1,  5), (0,  9), (0,  3), (1, 13), (1, 17), (0, 13)],
           [(1, 22), (1, 1), (1,  8), (0,  9), (1, 21), (1, 29), (1,  0), (0,  2), (0, 12), (1, 15)],
           [(1, 24), (1, 1), (0, 14), (0,  0), (0, 16), (0, 18), (0,  8), (0, 28), (0, 17), (0,  7)],
           [(0, 17), (0, 7), (0, 20), (0,  1), (1,  4), (0, 26), (0, 19), (0, 28), (1, 21), (0,  6)],
           [(1, 14), (1, 9), (0, 10), (0, 27), (1, 20), (0, 11), (0, 13), (1, 12), (0, 28), (1, 18)]]

    from sage.groups.additive_abelian.additive_abelian_group import AdditiveAbelianGroup
    G = AdditiveAbelianGroup([2,30])
    M60b=[[],[],[],[],[],[]]
    onezero = G((1,0))

    for R in zip(*M60):
        a,b,c,d,e,f = map(G,R)
        M60b[0].extend([a,c,b,-d,-e,-f])
        M60b[1].extend([b,a,c,-e,-f,-d])
        M60b[2].extend([c,b,a,-f,-d,-e])
        M60b[3].extend([d,e,f,-a+onezero,-c+onezero,-b+onezero])
        M60b[4].extend([e,f,d,-b+onezero,-a+onezero,-c+onezero])
        M60b[5].extend([f,d,e,-c+onezero,-b+onezero,-a+onezero])

    M = OA_from_quasi_difference_matrix(M60b,G)
    return M

def OA_7_62():
    r"""
    Returns an OA(7,62)

    As explained in the Handbook III.3.74 [DesignHandbook]_.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_quasi_difference_matrix`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_7_62
        sage: OA = OA_7_62()
        sage: print is_orthogonal_array(OA,7,62,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(7,62,existence=True)
        True
    """
    from sage.rings.finite_rings.integer_mod_ring import IntegerModRing as AdditiveCyclic
    G = AdditiveCyclic(54)

    M = [
        [ 0 ,None,None,None, 0   ,None ,None ,None,None,None],
        [17 , 0  , 0  , 0  , -17 ,  0  ,  0  ,  0 ,  1 , 11 ],
        [29 , 28 , 35 , 23 , -29 , -28 , -35 , -23,  3 , 19 ],
        [36 , 50 , 5  , 33 , -36 , -50 , -5  , -33,  7 , 33 ],
        [31 ,  2 , 43 , 30 , -31 , - 2 , -43 , -30, 34 , 33 ],
        [16 , 47 , 44 , 51 , -16 , -47 , -44 , -51, 30 , 19 ],
        [41 , 11 ,  1 , 17 , -41 , -11 , - 1 , -17, 28 , 11 ]
        ]

    Mb=[[] for _ in range(7)]

    for R in zip(*M):
        for c in range(7):
            for i,x in enumerate(cyclic_shift(R,c)):
                Mb[i].append(x)

    M = OA_from_quasi_difference_matrix(Mb,G,add_col = False)
    return M

def OA_9_65():
    r"""
    Returns an OA(9,65)

    Construction shared by Julian R. Abel

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_quasi_difference_matrix`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_9_65
        sage: OA = OA_9_65()
        sage: print is_orthogonal_array(OA,9,65,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(9,65,existence=True)
        True
    """
    from sage.rings.finite_rings.integer_mod_ring import IntegerModRing as G

    B = [None,1, 6, 7, 9, 19, 38, 42, 49] # Base block of a (57,8,1)-BIBD
    OA = orthogonal_array(9,9,2)
    M = [R for R in OA if any(R[0] != x for x in R)]

    M = [[B[x] for x in R] for R in M] # replacing [0,..,8] by the elements of B
    M.append([0]*9)

    M = OA_from_quasi_difference_matrix(zip(*M), G(57),add_col=False)
    return M

def OA_7_66():
    r"""
    Returns an OA(7,66)

    Construction shared by Julian R. Abel.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_PBD`

    EXAMPLES::

        sage: from sage.combinat.designs.orthogonal_arrays import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_7_66
        sage: OA = OA_7_66()
        sage: print is_orthogonal_array(OA,7,66,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(7,66,existence=True)
        True
    """

    # base block of a (73,9,1) BIBD
    B = [0, 19, 26, 14, 63, 15, 32, 35, 65]
    # The corresponding BIBD
    BIBD= [[(x+i)%73 for x in B] for i in range(73)]
    # the first 7 elements of an oval
    #
    # (this is the only difference with the OA(7,68) construction)
    oval = [(-x)%73 for x in B][:7]
    # PBD minus the oval
    PBD = [[x for x in B if x not in oval] for B in BIBD]
    # We relabel the points to 0,1,2,...
    V = [x for x in range(73) if x not in oval]
    rel = dict(zip(V,range(len(V))))
    PBD = [[rel[x] for x in B] for B in PBD]
    return OA_from_PBD(7,66,PBD,check=False)

def OA_7_68():
    r"""
    Returns an OA(7,68)

    Construction shared by Julian R. Abel.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_PBD`

    EXAMPLES::

        sage: from sage.combinat.designs.orthogonal_arrays import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_7_68
        sage: OA = OA_7_68()
        sage: print is_orthogonal_array(OA,7,68,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(7,68,existence=True)
        True
    """

    # base block of a (73,9,1) BIBD
    B = [0, 19, 26, 14, 63, 15, 32, 35, 65]
    # The corresponding BIBD
    BIBD= [[(x+i)%73 for x in B] for i in range(73)]
    # the first 5 elements of an oval
    #
    # (this is the only difference with the OA(7,66) construction)
    oval = [(-x)%73 for x in B][:5]
    # PBD minus the oval
    PBD = [[x for x in B if x not in oval] for B in BIBD]
    # We relabel the points to 0,1,2,...
    V = [x for x in range(73) if x not in oval]
    rel = dict(zip(V,range(len(V))))
    PBD = [[rel[x] for x in B] for B in PBD]
    return OA_from_PBD(7,68,PBD,check=False)

def OA_8_69():
    r"""
    Returns an OA(8,69)

    Construction shared by Julian R. Abel.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_PBD`

    EXAMPLES::

        sage: from sage.combinat.designs.orthogonal_arrays import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_8_69
        sage: OA = OA_8_69()
        sage: print is_orthogonal_array(OA,8,69,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(8,69,existence=True)
        True
    """
    # base block of a (73,9,1) BIBD
    B = [1,2,4,8,16,32,37,55,64]
    # The corresponding BIBD
    BIBD= [[(x+i)%73 for x in B] for i in range(73)]
    oval = [72,71,69,65]
    # PBD minus the oval
    PBD = [[x for x in B if x not in oval] for B in BIBD]

    sets_of_size_seven = [R for R in PBD if len(R) == 7]
    others             = [R for R in PBD if len(R) != 7]

    # 68, 27, and 52 are the only elements appearing twice in the rows of
    # sets_of_size_seven, and each row contains exactly one of them.

    # We split them into "balanced" halves.
    O1 = sets_of_size_seven[:3]
    O2 = sets_of_size_seven[-3:]
    assert all(x in sum(O1,[]) for x in (68,27,52))
    assert all(x in sum(O2,[]) for x in (68,27,52))

    # Blocks of "others", without the 0..0,1..1,2..2 ... rows
    OA = OA_from_PBD(8,69,others,check=False)[:-69]

    # Blocks of O1
    OA_8_7 = orthogonal_array(8,7,check=False)
    for B in O1:
        for BB in OA_8_7:
            OA.append([B[i] for i in BB])

    # Blocks of O2
    OA_8_7_minus_TD_8_1 = OA_8_7
    OA_8_7_minus_TD_8_1.remove([0]*8)
    for B in O2:
        # Making sure the double element is the first one
        B.sort(key=lambda x: int(bool(x not in (68,27,52))))
        for BB in OA_8_7:
            OA.append([B[i] for i in BB])


    # Adding the  missing 0..0,1..1,... rows
    done = sum(O1,[])+sum(O2,[])
    missing = [x for x in range(73) if x not in done and x not in oval]
    for x in missing:
        OA.append([x]*8)

    # Relabelling everything to 0..68
    relabel = dict(zip([x for x in range(73) if x not in oval],range(69)))
    OA = [[relabel[x] for x in B] for B in OA]
    return OA

def OA_7_74():
    r"""
    Returns an OA(7,74)

    Construction shared by Julian R. Abel.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_PBD`

    EXAMPLES::

        sage: from sage.combinat.designs.orthogonal_arrays import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_7_74
        sage: OA = OA_7_74()
        sage: print is_orthogonal_array(OA,7,74,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(7,74,existence=True)
        True
    """

    # base block of a (91,10,1) BIBD
    B = [0,1,3,9,27,81,61,49,56,77]
    # The corresponding BIBD
    BIBD= [[(x+i)%91 for x in B] for i in range(91)]
    # an oval
    oval = [(-x)%91 for x in B][-7:]
    # PBD minus the oval+B
    to_delete = oval + B
    PBD = [[x for x in B if x not in to_delete] for B in BIBD]
    PBD.remove([])
    # We relabel the points to 0,1,2,...
    V = [x for x in range(91) if x not in to_delete]
    rel = dict(zip(V,range(len(V))))
    PBD = [[rel[x] for x in B] for B in PBD]
    return OA_from_PBD(7,74,PBD,check=False)

def OA_9_75():
    r"""
    Returns an OA(9,75)

    As explained in the Handbook III.3.75 [DesignHandbook]_.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_quasi_difference_matrix`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_9_75
        sage: OA = OA_9_75()
        sage: print is_orthogonal_array(OA,9,75,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(9,75,existence=True)
        True
    """
    from sage.rings.finite_rings.constructor import FiniteField
    from sage.categories.cartesian_product import cartesian_product

    F3 = FiniteField(3)
    F5 = FiniteField(5)
    G  = cartesian_product((F3,F5,F5))

    M = [
        [(2,0,0), (0,0,0), (0,0,0), (1,0,0), (0,0,0), (1,0,0), (1,0,0), (0,0,0)],
        [(0,2,3), (1,4,4), (1,1,3), (1,0,4), (2,4,3), (0,0,3), (1,4,4), (0,0,0)],
        [(1,3,2), (2,1,1), (1,4,0), (0,3,0), (1,0,4), (2,4,1), (0,1,2), (0,0,0)],
        [(0,2,4), (1,3,1), (2,0,2), (0,0,1), (2,4,0), (1,2,2), (0,0,0), (0,0,0)],
        [(1,1,2), (2,2,3), (0,3,1), (1,4,2), (2,1,0), (1,4,3), (2,4,4), (0,0,0)],
        [(0,1,4), (0,4,4), (2,4,1), (1,3,0), (1,3,1), (2,0,0), (2,4,0), (0,0,0)],
        [(0,4,4), (2,0,1), (2,3,3), (2,3,2), (0,0,2), (2,1,2), (1,4,2), (0,0,0)],
        [(2,4,2), (2,4,1), (2,3,1), (1,2,2), (1,3,0), (0,0,2), (2,4,2), (0,0,0)]
        ]

    for i in range(8):
        M[i].extend(M[7-i][:7])

    Mb=[]

    for R in zip(*M):
        for x in range(5):
            V = [(0,0,x), (0,x,0), (0,x,2*x),(0,2*x,2*x), (0,3*x,3*x), (0,4*x,3*x), (0,4*x,0), (0,0,4*x)]
            Mb.append([G(e)+G(ee) for e,ee in zip(R,V)])

    Mb = zip(*Mb)
    M = OA_from_quasi_difference_matrix(Mb,G,add_col = True)
    return M

def OA_8_76():
    r"""
    Returns an OA(8,76)

    Construction shared by Julian R. Abel.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_PBD`

    EXAMPLES::

        sage: from sage.combinat.designs.orthogonal_arrays import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_8_76
        sage: OA = OA_8_76()
        sage: print is_orthogonal_array(OA,8,76,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(8,76,existence=True)
        True
    """
    # base block of a (91,10,1) BIBD
    B = [0,1,3,9,27,81,61,49,56,77]
    # The corresponding BIBD
    BIBD= [[(x+i)%91 for x in B] for i in range(91)]
    oval = [2,4,5,12,24]
    to_remove = oval + B
    # PBD minus the oval
    PBD = [[x for x in B if x not in to_remove] for B in BIBD]
    PBD.remove([])

    sets_of_size_seven = [R for R in PBD if len(R) == 7]
    others             = [R for R in PBD if len(R) != 7]

    # critical_points are the 10 elements appearing twice in the rows of the 10
    # sets_of_size_seven, and each row contains exactly two of them
    critical_points = [57,83,52,13,15,64,37,50,63,31]

    # We reorder the rows such that every element of critical_points is exactly
    # once the first element of a row.
    for i,x in zip(critical_points,sets_of_size_seven):
        x.sort(key=lambda x:-int(x==i))
        assert x[0]==i

    # Blocks of "others", without the 0..0,1..1,2..2 ... rows
    OA = OA_from_PBD(8,76,others,check=False)[:-76]

    OA_8_7 = orthogonal_array(8,7,check=False)
    OA_8_7_minus_TD_8_1 = OA_8_7
    OA_8_7_minus_TD_8_1.remove([0]*8)
    for B in sets_of_size_seven:
        for BB in OA_8_7:
            OA.append([B[i] for i in BB])

    # Adding the  missing 0..0,1..1,... rows
    done = sum(sets_of_size_seven,[])
    missing = [x for x in range(91) if x not in done and x not in to_remove]
    for x in missing:
        OA.append([x]*8)

    # Relabelling everything to 0..68
    relabel = dict(zip([x for x in range(91) if x not in to_remove],range(91)))
    OA = [[relabel[x] for x in B] for B in OA]
    return OA

def OA_11_80():
    r"""
    Returns an OA(11,80)

    As explained in the Handbook III.3.76 [DesignHandbook]_.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_quasi_difference_matrix`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_11_80
        sage: OA = OA_11_80()
        sage: print is_orthogonal_array(OA,11,80,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(11,80,existence=True)
        True
    """
    A = [
        [(0,None), (0,None), (0,None), (0,None), (0,None), (0,None), (0,None), (0,None), (0,None), (0,None)],
        [(0,None), (1,None),    (2,3), (3,None),    (4,3), (2,None),    (3,3), (4,None),    (0,3),    (1,3)],
        [(0,None),    (2,8),    (4,6),    (1,3),    (3,3),   (3,13),   (0,13),    (2,6),   (4,14),   (1,12)],
        [(0,None),   (3,11),    (1,0),    (4,9),    (2,0),    (3,7),    (1,8),   (4,10),   (2,10),   (0,11)],
        [(0,None),    (4,8),   (3,14),   (2,14),   (1,12),   (2,10),   (1,10),    (0,3),    (4,5),    (3,8)],
        [(0,None),    (1,8),   (4,14),   (4,12),    (1,1),    (0,1),    (2,8),   (3,12),    (3,6),    (2,1)],
        [(1,None),    (0,6),    (1,1),    (4,4),   (4,13),    (2,6),   (0,14),    (2,9),    (3,0),    (3,3)],
        [(4,None),    (1,9),    (0,7),    (1,1),    (4,8),    (3,5),   (2,14),    (0,0), (2,None),    (3,0)],
        [(4,None),    (4,6),    (1,2), (0,None),   (1,13),    (3,8),    (3,2),    (2,0),   (0,14), (2,None)],
        [(1,None),    (4,9),    (4,1),    (1,0),    (0,4),    (2,5), (3,None),    (3,5), (2,None), (0,None)]
        ]
    Y = [None, 0, 1, 14, 12, 7, 2, 11, 3, 6]
    return _helper_function_when_n_is_prime_times_power_of_2(11,80,A,Y)

def OA_10_82():
    r"""
    Returns an OA(10,82)

    Given by Julian R. Abel, using a `V(m,t)` from the Handbook
    [DesignHandbook]_.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_Vmt`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_10_82
        sage: OA = OA_10_82()
        sage: print is_orthogonal_array(OA,10,82,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(10,82,existence=True)
        True
    """
    M = OA_from_Vmt(8,9,[0,1,20,70,23,59,3,8,19])
    return M

def OA_10_100():
    r"""
    Returns an OA(10,100)

    Given by Julian R. Abel, using a `V(m,t)` from the Handbook
    [DesignHandbook]_.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_Vmt`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_10_100
        sage: OA = OA_10_100()
        sage: print is_orthogonal_array(OA,10,100,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(10,100,existence=True)
        True
    """
    M = OA_from_Vmt(8,11,[0,1,6,56,22,35,47,23,60])
    return M

def OA_15_112():
    r"""
    Returns an OA(15,112)

    Published by Julian R. Abel in [AbelThesis]_.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_quasi_difference_matrix`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_15_112
        sage: OA = OA_15_112()
        sage: print is_orthogonal_array(OA,15,112,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(15,112,existence=True)
        True
    """
    A = [
        [(0,None), (0,None), (0,None), (0,None), (0,None), (0,None), (0,None), (0,None), (1,None), (4,None), (2,None), (2,None), (4,None), (1,None)],
        [(0,None), (1,None), (2,None), (3,   5), (4,   9), (5,  11), (6,  12), (1,  10), (0,  10), (1,  11), (4,  13), (2,   6), (2,   2), (4,   1)],
        [(0,None), (2,   3), (4,   6), (6,   0), (1,   1), (3,  12), (5,   6), (4,   2), (1,   9), (0,   3), (1,   7), (4,   7), (2,   8), (2,   5)],
        [(0,None), (3,   3), (6,   2), (2,   3), (5,   2), (1,   9), (4,  13), (2,   8), (4,  12), (1,  12), (0,   7), (1,  10), (4,  11), (2,  14)],
        [(0,None), (4,None), (1,   0), (5,   1), (2,   0), (6,   7), (3,   4), (2,  11), (2,   9), (4,  13), (1,   3), (0,   7), (1,  11), (4,   2)],
        [(0,None), (5,None), (3,  14), (1,   7), (6,   5), (4,   3), (2,   1), (4,   6), (2,   5), (2,  14), (4,  12), (1,   1), (0,   2), (1,   2)],
        [(0,None), (6,None), (5,   0), (4,   4), (3,  11), (2,   2), (1,   7), (1,  13), (4,   8), (2,  11), (2,   3), (4,None), (1,   8), (0,  10)],
        [(0,None), (4,   3), (2,  14), (1,   5), (1,   4), (2,   5), (4,   2), (0,   8), (6,  10), (3,  11), (5,   6), (5,   5), (3,   0), (6,  11)],
        [(0,None), (5,   3), (4,   0), (4,   6), (5,   4), (0,   3), (3,  11), (6,None), (0,   4), (6,   5), (3,  13), (5,   6), (5,   4), (3,   4)],
        [(0,None), (6,   3), (6,   4), (0,   5), (2,   5), (5,   5), (2,None), (3,   6), (6,   7), (0,  12), (6,  12), (3,  12), (5,None), (5,  10)],
        [(0,None), (0,   3), (1,None), (3,   9), (6,   8), (3,  14), (1,  14), (5,   6), (3,   8), (6,  13), (0,   8), (6,   3), (3,   9), (5,   0)], # the last 3,9 was a 3,3
        [(0,None), (1,   3), (3,   1), (6,   6), (3,None), (1,  10), (0,   1), (5,   7), (5,   7), (3,  14), (6,   0), (0,  10), (6,   9), (3,   6)],
        [(0,None), (2,None), (5,   3), (2,  10), (0,   8), (6,   5), (6,   0), (3,   7), (5,   1), (5,  12), (3,  14), (6,   4), (0,  10), (6,   4)],
        [(0,None), (3,None), (0,   4), (5,   6), (4,   1), (4,   7), (5,   1), (6,   8), (3,   2), (5,   2), (5,   2), (3,  13), (6,   7), (0,   2)]
    ]
    Y = [None, 0, 1, 14, 12, 7, 2, 11, 3, 4, 5, 10, 8, 6]

    return _helper_function_when_n_is_prime_times_power_of_2(15,112,zip(*A),Y)

def OA_9_120():
    r"""
    Returns an OA(9,120)

    Construction shared by Julian R. Abel:

        From a resolvable `(120,8,1)-BIBD`, one can obtain 7 `MOLS(120)` or a
        resolvable `TD(8,120)` by forming a resolvable `TD(8,8) - 8.TD(8,1)` on
        `I_8 \times B` for each block `B` in the BIBD.  This gives a `TD(8,120)
        - 120 TD(8,1)` (which is resolvable as the BIBD is resolvable).

    .. SEEALSO::

        :func:`RBIBD_120_8_1`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_9_120
        sage: OA = OA_9_120()
        sage: print is_orthogonal_array(OA,9,120,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(9,120,existence=True)
        True
    """
    from incidence_structures import IncidenceStructure
    RBIBD_120 = RBIBD_120_8_1()
    equiv = [RBIBD_120[i*15:(i+1)*15] for i in range(17)]

    OA8 = orthogonal_array(9,8)
    assert all( (len(set(B[:-1])) == 1) == (B[-1] == 0) for B in OA8)
    OA = []

    for i,classs in enumerate(equiv):
        for S in classs:
            for B in OA8:
                if B[-1] != 0:
                    OA.append([S[x] for x in B[:-1]]+[i*7+B[-1]])

    for i in range(120):
        OA.append([i]*8+[0])

    return OA

def OA_9_135():
    r"""
    Returns an OA(9,135)

    Construction shared by Julian R. Abel:

        This design can be built by Wilson's method (`135 = 8.16 + 7`) applied
        to an Orthogonal Array `OA(9+7,16)` with 7 groups truncated to size 1 in
        such a way that a block contain 0, 1 or 3 points of the truncated
        groups.

        This is possible, because `PG(2,2)` (the projective plane over `GF(2)`)
        is a subdesign in `PG(2,16)` (the projective plane over `GF(16)`); in a
        cyclic `PG(2,16)` or `BIBD(273,17,1)` the points `\equiv 0
        \pmod{39}` form such a subdesign (note that `273=16^2 + 16 +1` and
        `273 = 39 \times 7` and `7 = 2^2 + 2 + 1`).

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_9_135
        sage: OA = OA_9_135()
        sage: print is_orthogonal_array(OA,9,135,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(9,135,existence=True)
        True

    As this orthogonal array requires a `(273,17,1)` cyclic difference set, we check that
    it is available::

        sage: G,D = designs.difference_family(273,17,1)
        sage: G
        Ring of integers modulo 273
    """
    from bibd import BIBD_from_difference_family
    G,B = CDF_273_17_1()
    PG16 = BIBD_from_difference_family(G,B)

    n = 273

    # PG2 is a (7,3,1)-design (fano plane) contained in PG16. It is a set of 7
    # points that any block of PG16 intersect on 0,1, or 3 points.
    #
    # We build it, then check that it works
    PG2 = set([x*39 for x in range(7)])
    traces = [[x for x in B if x%39 == 0] for B in PG16]
    assert set(map(len,traces)) == set([0,1,3])

    # We now build an OA(17,16) from our PG16, in such a way that all points of
    # PG2 are in different columns. For this, we need to find a point p that is
    # not located on any of the lines defined by the points of PG2

    lines = [B for B in PG16 if len([x for x in B if x%39 == 0]) == 3]
    union_of_the_lines = set(sum(lines,[]))
    p = (set(range(237))-union_of_the_lines).pop()

    # We can now build a TD from our PG16 by removing p.
    for B in PG16:
        B.sort(key=lambda x:int(x not in PG2))
    PG16.sort(key=lambda B:sum(x for x in B if x in PG2))

    r = {}
    for B in PG16:
        if p in B:
            for x in B:
                if x != p:
                    r[x] = len(r)
    r[p] = n-1

    # The columns containing points from PG2 will be the last 7
    assert all(r[x] >= (n-1)-16*7 for x in PG2)
    # Those points are the first of each column
    assert all(r[x]%16 == 0 for x in PG2)

    PG = [sorted([r[x] for x in B]) for B in PG16]
    OA = [[x%16 for x in B] for B in PG if n-1 not in B]

    # We truncate the last 7 columns to size 1. We also drop the first column
    truncated_OA = [B[1:-7]+[x if x==0 else None for x in B[-7:]] for B in OA]

    # And call Wilson's construction
    return wilson_construction(truncated_OA, 9, 16, 8,7,(1,)*7,check=False)

def OA_12_144():
    r"""
    Returns an OA(12,144)

    Given by Julian R. Abel, using a `V(m,t)` from the Handbook
    [DesignHandbook]_.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_Vmt`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_12_144
        sage: OA = OA_12_144()
        sage: print is_orthogonal_array(OA,12,144,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(12,144,existence=True)
        True
    """
    M = OA_from_Vmt(10,13,[0, 1, 5, 10, 22, 6, 14, 9, 53, 129, 84])
    return M

def OA_10_154():
    r"""
    Returns an OA(10,154)

    Given by Julian R. Abel, using a `V(m,t)` from the Handbook
    [DesignHandbook]_.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_Vmt`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_10_154
        sage: OA = OA_10_154()
        sage: print is_orthogonal_array(OA,10,154,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(10,154,existence=True)
        True
    """
    M = OA_from_Vmt(8,17,[0,1,3,2,133,126,47,109,74])
    return M

def OA_11_160():
    r"""
    Returns an OA(11,160)

    Published by Julian R. Abel in [AbelThesis]_.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_quasi_difference_matrix`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_11_160
        sage: OA = OA_11_160()
        sage: print is_orthogonal_array(OA,11,160,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(11,160,existence=True)
        True

    REFERENCES:

    .. [AbelThesis] On the Existence of Balanced Incomplete Block Designs and Transversal Designs,
      Julian R. Abel,
      PhD Thesis,
      University of New South Wales,
      1995
    """
    A = [
         [(0,None), (0,None), (0,None), (0,None), (0,None), (0,None), (1,None), (4,None), (4,None), (1,None)],
         [(0,None), (1,None), (2,   5), (3,   9), (4,   9), (1,  16), (0,  20), (1,  23), (4,  24), (4,  19)],
         [(0,None), (2,   4), (4,   3), (1,  10), (3,  10), (4,  20), (1,   1), (0,  24), (1,   5), (4,   2)],
         [(0,None), (3,None), (1,  28), (4,   7), (2,   6), (4,   4), (4,  23), (1,   5), (0,   8), (1,   1)],
         [(0,None), (4,   4), (3,  25), (2,  24), (1,  13), (1,   6), (4,   6), (4,   2), (1,  18), (0,   1)],
         [(0,None), (2,None), (3,   3), (3,  21), (2,  18), (0,   6), (2,  20), (3,   3), (3,  11), (2,   1)],
         [(0,None), (3,   4), (0,   5), (1,  27), (1,  30), (2,None), (0,   0), (2,   2), (3,   2), (3,  18)],
         [(0,None), (4,None), (2,  19), (4,  26), (0,  12), (3,  19), (2,   4), (0,   2), (2,   0), (3,   0)],
         [(0,None), (0,   4), (4,  29), (2,  29), (4,None), (3,   0), (3,   0), (2,   1), (0,  18), (2,None)],
         [(0,None), (1,   4), (1,   5), (0,  19), (3,   2), (2,   0), (3,None), (3,   0), (2,None), (0,None)],
        ]

    Y = [None, 0, 1, 2, 15, 27, 22, 12, 3, 28]
    return _helper_function_when_n_is_prime_times_power_of_2(11,160,zip(*A),Y)

def OA_16_176():
    r"""
    Returns an OA(16,176)

    Published by Julian R. Abel in [AbelThesis]_.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_quasi_difference_matrix`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_16_176
        sage: OA = OA_16_176()
        sage: print is_orthogonal_array(OA,16,176,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(16,176,existence=True)
        True
    """
    A = [
        [(0 ,None),(0 ,None),(0 ,None),(0 ,None),(0 ,None),(0 ,None),(0 ,None),(0 ,None),(0 ,None),(0 ,None),(0 ,None),(0 ,None),(1 ,None),(4 ,None),(9 ,None)],
        [(0 ,None),(1 ,None),(2 ,None),(3 ,   0),(4 ,   2),(5 ,  12),(6 ,   5),(7 ,   6),(8 ,  13),(9 ,   9),(10,  11),(1 ,   3),(0 ,   6),(1 ,  14),(4 ,  12)],
        [(0 ,None),(2 ,None),(4 ,   4),(6 ,   4),(8 ,   7),(10,   2),(1 ,   2),(3 ,  13),(5 ,   0),(7 ,   3),(9 ,   7),(4 ,   6),(1 ,  12),(0 ,   1),(1 ,  10)], # 5,1 became 5,0
        [(0 ,None),(3 ,None),(6 ,   3),(9 ,   4),(1 ,   6),(4 ,  13),(7 ,   1),(10,   1),(2 ,   7),(5 ,   1),(8 ,   0),(9 ,   6),(4 ,   4),(1 ,   5),(0 ,   1)],
        [(0 ,None),(4 ,None),(8 ,  13),(1 ,   8),(5 ,   0),(9 ,   5),(2 ,  14),(6 ,None),(10,   5),(3 ,   7),(7 ,  10),(5 ,   3),(9 ,  10),(4 ,  11),(1 ,  14)],
        [(0 ,None),(5 ,None),(10,  10),(4 ,   2),(9 ,   7),(3 ,   2),(8 ,   3),(2 ,  13),(7 ,   7),(1 ,   9),(6 ,None),(3 ,   7),(5 ,   1),(9 ,  10),(4 ,  11)],
        [(0 ,None),(6 ,None),(1 ,   8),(7 ,  14),(2 ,   2),(8 ,   3),(3 ,  11),(9 ,  12),(4 ,   8),(10,  13),(5 ,   1),(3 ,   6),(3 ,   5),(5 ,  10),(9 ,   9)],
        [(0 ,None),(7 ,None),(3 ,   3),(10,None),(6 ,  14),(2 ,   4),(9 ,   1),(5 ,   7),(1 ,   5),(8 ,   7),(4 ,  13),(5 ,   6),(3 ,   6),(3 ,  11),(5 ,   3)],
        [(0 ,None),(8 ,None),(5 ,  14),(2 ,  11),(10,  14),(7 ,   8),(4 ,  14),(1 ,  14),(9 ,   9),(6 ,  14),(3 ,   9),(9 ,   2),(5 ,   6),(3 ,   3),(3 ,  10)],
        [(0 ,None),(9 ,None),(7 ,   5),(5 ,   5),(3 ,   8),(1 ,   8),(10,None),(8 ,  12),(6 ,   9),(4 ,  12),(2 ,   9),(4 ,   7),(9 ,   2),(5 ,   0),(3 ,   7)],
        [(0 ,None),(10,None),(9 ,  11),(8 ,   7),(7 ,   6),(6 ,  12),(5 ,None),(4 ,   1),(3 ,  13),(2 ,   8),(1 ,   9),(1 ,None),(4 ,   3),(9 ,   7),(5 ,  13)],
        [(0 ,None),(6 ,   3),(2 ,   0),(10,   8),(8 ,  12),(7 ,   9),(7 ,   2),(8 ,   0),(10,   7),(2 ,  10),(6 ,   4),(0 ,   7),(10,  10),(7 ,   3),(2 ,  11)],
        [(0 ,None),(7 ,   3),(4 ,None),(2 ,  12),(1 ,  10),(1 ,   3),(2 ,   8),(4 ,   9),(7 ,   0),(0 ,   1),(5 ,   6),(10,   3),(0 ,   9),(10,  13),(7 ,  11)],
        [(0 ,None),(8 ,   3),(6 ,   8),(5 ,   2),(5 ,  13),(6 ,   1),(8 ,   9),(0 ,   2),(4 ,  10),(9 ,   8),(4 ,  12),(7 ,   7),(10,   2),(0 ,  12),(10,   4)],
        [(0 ,None),(9 ,   3),(8 ,   3),(8 ,   9),(9 ,   1),(0 ,   4),(3 ,   3),(7 ,  11),(1 ,   9),(7 ,  10),(3 ,   8),(2 ,  10),(7 ,   6),(10,  14),(0 ,   3)],
        [(0 ,None),(10,   3),(10,   5),(0 ,   1),(2 ,   1),(5 ,   8),(9 ,   2),(3 ,   5),(9 ,   5),(5 ,   3),(2 ,   4),(6 ,  12),(2 ,   6),(7 ,  11),(10,   7)],
        [(0 ,None),(0 ,   3),(1 ,None),(3 ,   2),(6 ,   8),(10,  11),(4 ,   6),(10,None),(6 ,None),(3 ,   1),(1 ,   1),(8 ,   0),(6 ,  14),(2 ,   0),(7 ,  14)],
        [(0 ,None),(1 ,   3),(3 ,   8),(6 ,   9),(10,   8),(4 ,  10),(10,   1),(6 ,  10),(3 ,   0),(1 ,   8),(0 ,  11),(8 ,  10),(8 ,  14),(6 ,  10),(2 ,  14)],
        [(0 ,None),(2 ,   3),(5 ,   1),(9 ,   8),(3 ,   4),(9 ,  14),(5 ,   5),(2 ,   4),(0 ,   2),(10,   2),(10,None),(6 ,   2),(8 ,   5),(8 ,   1),(6 ,   9)],
        [(0 ,None),(3 ,   3),(7 ,   0),(1 ,None),(7 ,   1),(3 ,  10),(0 ,   8),(9 ,  13),(8 ,None),(8 ,  10),(9 ,  14),(2 ,   0),(6 ,   5),(8 ,   5),(8 ,   7)], # 2,None became 2,0
        [(0 ,None),(4 ,   3),(9 ,  10),(4 ,  14),(0 ,  14),(8 ,  14),(6 ,  14),(5 ,   6),(5 ,  13),(6 ,   5),(8 ,  12),(7 ,   1),(2 ,   4),(6 ,   3),(8 ,   6)],
        [(0 ,None),(5 ,   3),(0 ,   8),(7 ,   3),(4 ,  10),(2 ,   1),(1 ,   3),(1 ,  10),(2 ,None),(4 ,   8),(7 ,  12),(10,   6),(7 ,  10),(2 ,   6),(6 ,   1)], # 7,12 became 4,8
    ]

    Y = [None, 0, 1, 2, 8, 6, 9, 4, 10, 3, 5, 11, 13, 14, 12]
    return _helper_function_when_n_is_prime_times_power_of_2(16,176,zip(*A),Y)

def OA_16_208():
    r"""
    Returns an OA(16,208)

    Published by Julian R. Abel in [AbelThesis]_.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_quasi_difference_matrix`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_16_208
        sage: OA = OA_16_208()                        # not tested -- too long
        sage: print is_orthogonal_array(OA,16,208,2)  # not tested -- too long
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(16,208,existence=True)
        True
    """
    A = [
        [(0 ,None), (0 ,None), (0 ,None), (0 ,None), (0 ,None), (0 ,None), (0 ,None), (0 ,None), (0 ,None), (0 ,None), (0 ,None), (0 ,None), (0 ,None), (0 ,None), (1 ,None)],
        [(0 ,None), (1 ,None), (2 ,   0), (3 ,   7), (4 ,   1), (5 ,  11), (6 ,   2), (7 ,  10), (8 ,None), (9 ,  10), (10,None), (11,   3), (12,   3), (1 ,   4), (0 ,   8)],
        [(0 ,None), (2 ,None), (4 ,   4), (6 ,   3), (8 ,   0), (10,   5), (12,  14), (1 ,None), (3 ,  10), (5 ,   7), (7 ,   3), (9 ,  12), (11,   6), (4 ,   9), (1 ,  14)],
        [(0 ,None), (3 ,None), (6 ,   4), (9 ,   6), (12,  10), (2 ,  11), (5 ,  14), (8 ,   3), (11,  13), (1 ,   1), (4 ,  12), (7 ,  14), (10,   1), (9 ,   7), (4 ,   8)],
        [(0 ,None), (4 ,None), (8 ,   9), (12,   5), (3 ,  10), (7 ,  14), (11,   0), (2 ,   6), (6 ,  11), (10,  11), (1 ,   9), (5 ,   3), (9 ,   9), (3 ,   6), (9 ,   8)],
        [(0 ,None), (5 ,None), (10,   5), (2 ,   5), (7 ,   3), (12,   3), (4 ,  12), (9 ,   3), (1 ,   2), (6 ,   2), (11,None), (3 ,  13), (8 ,   7), (12,  10), (3 ,   1)],
        [(0 ,None), (6 ,None), (12,  13), (5 ,   5), (11,  13), (4 ,   6), (10,   6), (3 ,   2), (9 ,   4), (2 ,  12), (8 ,  13), (1 ,  13), (7 ,   2), (10,   8), (12,None)],
        [(0 ,None), (7 ,None), (1 ,   2), (8 ,  12), (2 ,   4), (9 ,  12), (3 ,   0), (10,  10), (4 ,  14), (11,  11), (5 ,  14), (12,   9), (6 ,   8), (10,   3), (10,   6)],
        [(0 ,None), (8 ,None), (3 ,None), (11,   4), (6 ,  12), (1 ,  12), (9 ,  14), (4 ,   2), (12,   9), (7 ,   9), (2 ,None), (10,   1), (5 ,  14), (12,   5), (10,   8)],
        [(0 ,None), (9 ,None), (5 ,   9), (1 ,   7), (10,   6), (6 ,   3), (2 ,   6), (11,  10), (7 ,  11), (3 ,  13), (12,   2), (8 ,   0), (4 ,  13), (3 ,   3), (12,  14)],
        [(0 ,None), (10,None), (7 ,   7), (4 ,   1), (1 ,   8), (11,   1), (8 ,  11), (5 ,   4), (2 ,  11), (12,   8), (9 ,  12), (6 ,   4), (3 ,   0), (9 ,   4), (3 ,   8)],
        [(0 ,None), (11,None), (9 ,   3), (7 ,  11), (5 ,  14), (3 ,  10), (1 ,  10), (12,   0), (10,   2), (8 ,   2), (6 ,   6), (4 ,   2), (2 ,  12), (4 ,   8), (9 ,  10)],
        [(0 ,None), (12,None), (11,   4), (10,   9), (9 ,   2), (8 ,None), (7 ,   9), (6 ,  12), (5 ,   5), (4 ,None), (3 ,   7), (2 ,  10), (1 ,  13), (1 ,   6), (4 ,   0)],
        [(0 ,None), (5 ,   3), (7 ,   5), (6 ,   5), (2 ,  14), (8 ,   5), (11,   1), (11,   6), (8 ,  13), (2 ,  13), (6 ,   9), (7 ,None), (5 ,  10), (0 ,   5), (2 ,   8)],
        [(0 ,None), (6 ,   3), (9 ,   4), (9 ,  13), (6 ,   4), (0 ,   5), (4 ,   6), (5 ,   2), (3 ,None), (11,  14), (3 ,   3), (5 ,   7), (4 ,   1), (2 ,   8), (0 ,   2)],
        [(0 ,None), (7 ,   3), (11,   5), (12,  12), (10,None), (5 ,   5), (10,   7), (12,   9), (11,   9), (7 ,   7), (0 ,   0), (3 ,  12), (3 ,  11), (8 ,  13), (2 ,  14)],
        [(0 ,None), (8 ,   3), (0 ,   8), (2 ,   6), (1 ,None), (10,   9), (3 ,  12), (6 ,   8), (6 ,   4), (3 ,   9), (10,   2), (1 ,  11), (2 ,   7), (5 ,   2), (8 ,   2)],
        [(0 ,None), (9 ,   3), (2 ,   3), (5 ,   3), (5 ,   8), (2 ,   0), (9 ,   1), (0 ,   3), (1 ,  14), (12,   3), (7 ,   6), (12,   4), (1 ,   3), (6 ,  10), (5 ,   7)],
        [(0 ,None), (10,   3), (4 ,   2), (8 ,   0), (9 ,   8), (7 ,   1), (2 ,   5), (7 ,None), (9 ,   2), (8 ,   4), (4 ,  14), (10,  13), (0 ,  10), (11,   7), (6 ,  10)],
        [(0 ,None), (11,   3), (6 ,   9), (11,  14), (0 ,  10), (12,  13), (8 ,   6), (1 ,   8), (4 ,   7), (4 ,   0), (1 ,  14), (8 ,   2), (12,   8), (7 ,  10), (11,   7)], # 6,10 became 6,9
        [(0 ,None), (12,   3), (8 ,  12), (1 ,   9), (4 ,   6), (4 ,  13), (1 ,   6), (8 ,   1), (12,   4), (0 ,   7), (11,   5), (6 ,   6), (11,  14), (7 ,   3), (7 ,   5)],
        [(0 ,None), (0 ,   3), (10,  10), (4 ,   2), (8 ,   1), (9 ,None), (7 ,   2), (2 ,  10), (7 ,  13), (9 ,   5), (8 ,  14), (4 ,   7), (10,  11), (11,  13), (7 ,   0)],
        [(0 ,None), (1 ,   3), (12,  11), (7 ,  12), (12,  13), (1 ,   2), (0 ,   9), (9 ,   6), (2 ,  13), (5 ,   4), (5 ,  13), (2 ,   4), (9 ,  12), (6 ,   5), (11,   1)],
        [(0 ,None), (2 ,   3), (1 ,   8), (10,None), (3 ,  13), (6 ,None), (6 ,   1), (3 ,   0), (10,   4), (1 ,  14), (2 ,   0), (0 ,   3), (8 ,  13), (5 ,   1), (6 ,   7)], # 2,None became 2,0
        [(0 ,None), (3 ,   3), (3 ,  14), (0 ,   1), (7 ,  14), (11,   4), (12,   9), (10,   1), (5 ,   9), (10,None), (12,  13), (11,None), (7 ,   7), (8 ,   6), (5 ,   0)],
        [(0 ,None), (4 ,   3), (5 ,  10), (3 ,   8), (11,   8), (3 ,   0), (5 ,   7), (4 ,  12), (0 ,  13), (6 ,None), (9 ,  11), (9 ,   5), (6 ,   0), (2 ,   5), (8 ,   8)],
    ]

    Y = [None, 0, 1, 2, 12, 9, 13, 11, 7, 4, 8, 5, 14, 6, 3]

    return _helper_function_when_n_is_prime_times_power_of_2(16,208,zip(*A),Y)

def OA_12_210():
    r"""
    Returns an OA(12,210)

    Given by Julian R. Abel, using a `V(m,t)` from the Handbook
    [DesignHandbook]_.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_Vmt`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_12_210
        sage: OA = OA_12_210()
        sage: print is_orthogonal_array(OA,12,210,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(12,210,existence=True)
        True
    """
    M = OA_from_Vmt(10,19,[0, 1, 3, 96, 143, 156, 182, 142, 4, 189, 25])
    return M

def OA_15_224():
    r"""
    Returns an OA(15,224)

    Published by Julian R. Abel in [AbelThesis]_.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_quasi_difference_matrix`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_15_224
        sage: OA = OA_15_224()                         # not tested -- too long
        sage: print is_orthogonal_array(OA,15,224,2)   # not tested -- too long
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(15,224,existence=True)
        True
    """
    A = [
        [(0,None), (0,None), (0,None), (0,None), (0,None), (0,None), (0,None), (0,None), (1,None), (4,None), (2,None), (2,None), (4,None), (1,None)],
        [(0,None), (1,None), (2,   9), (3,  23), (4,  29), (5,   4), (6,  30), (1,  26), (0,None), (1,  11), (4,   2), (2,  28), (2,None), (4,  13)],
        [(0,None), (2,None), (4,   8), (6,None), (1,  29), (3,  21), (5,   4), (4,   5), (1,   4), (0,  14), (1,   5), (4,   6), (2,   0), (2,   2)],
        [(0,None), (3,None), (6,   8), (2,  12), (5,   4), (1,   1), (4,   2), (2,   1), (4,  18), (1,  27), (0,   5), (1,None), (4,   1), (2,None)],
        [(0,None), (4,None), (1,   9), (5,   2), (2,  29), (6,  17), (3,   0), (2,  12), (2,   5), (4,  22), (1,   0), (0,  29), (1,  19), (4,None)],
        [(0,None), (5,None), (3,  26), (1,   0), (6,  29), (4,  16), (2,  11), (4,  21), (2,  28), (2,  16), (4,   0), (1,   3), (0,  11), (1,   2)],
        [(0,None), (6,None), (5,   3), (4,  19), (3,  24), (2,  20), (1,  28), (1,  12), (4,  23), (2,   0), (2,   5), (4,  29), (1,   0), (0,   2)],
        [(0,None), (4,   4), (2,  14), (1,  23), (1,  22), (2,  17), (4,  17), (0,  25), (6,  21), (3,  11), (5,   2), (5,  27), (3,   5), (6,   2)],
        [(0,None), (5,   4), (4,   3), (4,   0), (5,  20), (0,   4), (3,   8), (6,  28), (0,  16), (6,   1), (3,  22), (5,   0), (5,   0), (3,   2)],
        [(0,None), (6,   4), (6,None), (0,  18), (2,   0), (5,  20), (2,   4), (3,  11), (6,  15), (0,  18), (6,   5), (3,   0), (5,None), (5,   2)],
        [(0,None), (0,   4), (1,  15), (3,  29), (6,  20), (3,  24), (1,  13), (5,  30), (3,   2), (6,None), (0,  10), (6,   3), (3,   0), (5,None)],
        [(0,None), (1,   4), (3,   4), (6,  12), (3,  28), (1,  27), (0,   6), (5,   7), (5,  29), (3,   0), (6,   0), (0,   0), (6,   0), (3,None)], # 6,19 became 6,12
        [(0,None), (2,   4), (5,  11), (2,   5), (0,  21), (6,  11), (6,  24), (3,  24), (5,  11), (5,  30), (3,None), (6,None), (0,None), (6,   1)],
        [(0,None), (3,   4), (0,  11), (5,  11), (4,  22), (4,   2), (5,  23), (6,  22), (3,  27), (5,   1), (5,   0), (3,None), (6,None), (0,None)]
    ]

    Y = [None, 0, 1, 2, 27, 22, 11, 4, 26, 25, 29, 24, 7, 20]

    return _helper_function_when_n_is_prime_times_power_of_2(15,224,zip(*A),Y)

def OA_10_262():
    r"""
    Returns an OA(10,262)

    Given by Julian R. Abel.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_Vmt`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_10_262
        sage: OA = OA_10_262()
        sage: print is_orthogonal_array(OA,10,262,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(10,262,existence=True)
        True
    """
    return OA_from_Vmt(8,29,[0,1,4,11,94,60,85,16,198])

def OA_18_273():
    r"""
    Returns an OA(18,273)

    Given by Julian R. Abel.

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_18_273
        sage: OA = OA_18_273()
        sage: print is_orthogonal_array(OA,18,273,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(18,273,existence=True)
        True
    """
    M = orthogonal_array(17,17)
    M = [R for R in M if any(x!=R[0] for x in R)] # removing the 0..0, 1..1, ... rows.
    B = (1,2,4,8,16,32,64,91,117,128,137,182,195,205,234,239,256) # (273,17,1) difference set
    M = [[B[x] for x in R] for R in M]
    M.append([0]*17)
    Mb = zip(*M)

    from sage.rings.finite_rings.integer_mod_ring import IntegerModRing as AdditiveCyclic
    G = AdditiveCyclic(273)
    M = OA_from_quasi_difference_matrix(Mb,G,add_col=True)
    return M

def OA_12_276():
    r"""
    Returns an OA(12,276)

    Given by Julian R. Abel, using a `V(m,t)` from the Handbook
    [DesignHandbook]_.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_Vmt`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_12_276
        sage: OA = OA_12_276()
        sage: print is_orthogonal_array(OA,12,276,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(12,276,existence=True)
        True
    """
    M = OA_from_Vmt(10,25,[0,1,3,85,140,178,195,22,48,179,188])
    return M

def OA_12_298():
    r"""
    Returns an OA(12,298)

    Given by Julian R. Abel, using a `V(m,t)` from the Handbook
    [DesignHandbook]_.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_Vmt`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_12_298
        sage: OA = OA_12_298()
        sage: print is_orthogonal_array(OA,12,298,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(12,298,existence=True)
        True
    """
    M = OA_from_Vmt(10,27,[0,1,3,82,109,241,36,112,141,263,126])
    return M

def OA_12_342():
    r"""
    Returns an OA(12,342)

    Given by Julian R. Abel, using a `V(m,t)` from the Handbook
    [DesignHandbook]_.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_Vmt`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_12_342
        sage: OA = OA_12_342()
        sage: print is_orthogonal_array(OA,12,342,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(12,342,existence=True)
        True
    """
    M = OA_from_Vmt(10,31,[0,1,3,57,128,247,289,239,70,271,96])
    return M

def OA_20_352():
    r"""
    Returns an OA(20,352)

    Published by Julian R. Abel in [AbelThesis]_.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_quasi_difference_matrix`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_20_352
        sage: OA = OA_20_352()                        # not tested (~25s)
        sage: print is_orthogonal_array(OA,20,352,2)  # not tested (~25s)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(20,352,existence=True)
        True
    """
    # Column 8, line 6 : 4,25 became 4,27
    #           line 17: 3,0  became 3,None
    # Column 14,line 1 : 4,1  became 4,0
    # Column 18,line 18: 0,0  became 0,None
    A = [
        [(0,None),(0, None),(0,None),(0,None),(0,None),(0,None),(0,None),(0,None),(0,None),(0,None),(0,None),(0,None),(1,None),(4,None),(9,None),(5, None),(3,None),(3,None),(5,None)],
        [(0,None),(1, None),(2,  13),(3,   2),(4,   0),(5,   8),(6,  30),(7,   0),(8,  13),(9,  26),(10, 10),(1,  29),(0,   9),(1,  11),(4,   0),(9,   23),(5,   7),(3,  25),(3,  29)],
        [(0,None),(2, None),(4,  29),(6,   6),(8,   3),(10, 18),(1,  21),(3,  24),(5,   4),(7,   7),(9,  29),(4,  22),(1,   2),(0,  27),(1,  10),(4,   13),(9,  22),(5,   6),(3,  20)],
        [(0,None),(3, None),(6,  25),(9,  21),(1,  23),(4,  25),(7,  12),(10, 16),(2,  26),(5,  27),(8,  19),(9,  27),(4,   6),(1,   5),(0,   6),(1,   15),(4,  10),(9,   2),(5,  14)],
        [(0,None),(4, None),(8,   3),(1,  23),(5,  17),(9,   7),(2,   7),(6,  25),(10, 27),(3,  30),(7,   5),(5,  23),(9,  24),(4,  16),(1,  12),(0,    8),(1,  12),(4,  17),(9,  28)],
        [(0,None),(5, None),(10, 10),(4,  27),(9,   4),(3,  24),(8,  21),(2,   3),(7,  22),(1,  21),(6,  24),(3,  28),(5,   3),(9,  26),(4,  29),(1,    9),(0,  19),(1,   2),(4,   0)],
        [(0,None),(6, None),(1,  11),(7,   9),(2,  14),(8,  15),(3,  11),(9,   7),(4,  27),(10, 13),(5,   4),(3,  18),(3,   0),(5,   5),(9,   2),(4,    7),(1,  30),(0,  10),(1,None)],
        [(0,None),(7, None),(3,  25),(10,  7),(6,  29),(2,   4),(9,  10),(5,  22),(1,  25),(8,  18),(4,  11),(5,  21),(3,  29),(3,  14),(5,  12),(9,   25),(4,   2),(1,  13),(0,  19)],
        [(0,None),(8, None),(5,  27),(2,  30),(10, 24),(7,   4),(4,   6),(1,   4),(9,   5),(6,  27),(3,   0),(9,   2),(5,  20),(3,  10),(3,  13),(5,    2),(9,   5),(4,  21),(1,  12)],
        [(0,None),(9, None),(7,  21),(5,   0),(3,   9),(1,  13),(10, 17),(8,   1),(6,  15),(4,  30),(2,  28),(4,   3),(9,  28),(5,   0),(3,None),(3,    2),(5,  23),(9,  10),(4,  15)],
        [(0,None),(10,None),(9,  29),(8,   8),(7,   6),(6,   6),(5,  18),(4,  20),(3,  22),(2,   7),(1,  13),(1,  24),(4,  13),(9,  14),(5,  29),(3,   27),(3,  16),(5,  12),(9,   4)],
        [(0,None),(6,    4),(2,  17),(10, 16),(8,  26),(7,  17),(7,  21),(8,   9),(10,  2),(2,  25),(6,  27),(0,  20),(10,  8),(7,  12),(2,  26),(6,   22),(8,   8),(8,  16),(6,  13)],
        [(0,None),(7,    4),(4,   1),(2,   0),(1,   8),(1,  18),(2,  10),(4,   9),(7,   2),(0,  11),(5,  27),(10, 27),(0,  16),(10, 19),(7,   0),(2,    2),(6,  26),(8,  30),(8,   6)],
        [(0,None),(8,    4),(6,  19),(5,  24),(5,  16),(6,  20),(8,None),(0,  17),(4,   5),(9,  23),(4,  27),(7,  22),(10, 25),(0,  23),(10, 11),(7,   10),(2,  16),(6,  28),(8,   3)],
        [(0,None),(9,    4),(8,  14),(8,  30),(9,  16),(0,   0),(3,  25),(7,  30),(1,  27),(7,   4),(3,  10),(2,   5),(7,   3),(10, 11),(0,  21),(10,None),(7,   7),(2,  19),(6,  24)],
        [(0,None),(10,   4),(10, 30),(0,  12),(2,   9),(5,   9),(9,   0),(3,  14),(9,  17),(5,  17),(2,  18),(6,  10),(2,   0),(7,  16),(10, 23),(0,    1),(10, 26),(7,  18),(2,   9)],
        [(0,None),(0,    4),(1,  13),(3,  28),(6,  25),(10, 28),(4,  16),(10, 17),(6,  23),(3,   7),(1,  22),(8,  22),(6,  27),(2,  29),(7,   5),(10,  14),(0,  12),(10, 14),(7,   6)],
        [(0,None),(1,    4),(3,   6),(6,   4),(10, 13),(4,  12),(10, 15),(6,  27),(3,None),(1,  26),(0,   3),(8,  21),(8,  26),(6,  13),(2,  27),(7,   11),(10,  5),(0,   3),(10,  3)],
        [(0,None),(2,    4),(5,  12),(9,  27),(3,   7),(9,  21),(5,None),(2,  22),(0,  28),(10, 30),(10, 25),(6,  12),(8,   6),(8,  30),(6,  28),(2,    6),(7,  26),(10,  3),(0,None)],
        [(0,None),(3,    4),(7,  22),(1,   7),(7,   8),(3,  12),(0,  27),(9,   1),(8,  17),(8,   4),(9,  12),(2,  16),(6,  23),(8,  14),(8,   2),(6,   26),(2,  14),(7,  22),(10, 30)],
        [(0,None),(4,    4),(9,  21),(4,  25),(0,   9),(8,  23),(6,   5),(5,  20),(5,  13),(6,  19),(8,   0),(7,  30),(2,  29),(6,  24),(8,  18),(8,   10),(6,   9),(2,  20),(7,   4)],
        [(0,None),(5,    4),(0,  25),(7,   4),(4,  20),(2,   3),(1,None),(1,  21),(2,None),(4,  26),(7,   1),(10, 23),(7,  20),(2,   3),(6,   5),(8,   19),(8,   9),(6,  23),(2,   7)],
    ]

    Y = [None, 0, 1, 2, 18, 5, 11, 4, 13, 26, 25, 29, 24, 7, 20, 19, 9, 12, 15]

    return _helper_function_when_n_is_prime_times_power_of_2(20,352,zip(*A),Y)

def OA_20_416():
    r"""
    Returns an OA(20,416)

    Published by Julian R. Abel in [AbelThesis]_.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_quasi_difference_matrix`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_20_416
        sage: OA = OA_20_416()                        # not tested (~35s)
        sage: print is_orthogonal_array(OA,20,416,2)  # not tested
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(20,416,existence=True)
        True
    """
    Z = None
    A=[
        [(0,Z), (0 , Z), (0 , Z), (0 , Z), (0 , Z), (0 , Z), (0 , Z), (0 , Z), (0 , Z), (0 , Z), (0 , Z), (0 , Z), (0 , Z), (0 , Z), (1 , Z), (4 , Z), (9 , Z), (3 , Z), (12, Z)],
        [(0,Z), (1 , Z), (2 ,18), (3 , 2), (4 ,20), (5 ,22), (6 ,11), (7 ,19), (8 , 0), (9 ,26), (10, Z), (11, 5), (12,27), (1 ,17), (0 ,30), (1 ,22), (4 ,29), (9 , 6), (3 ,19)],
        [(0,Z), (2 , 4), (4 ,21), (6 ,10), (8 ,24), (10,13), (12, 7), (1 ,11), (3 ,29), (5 ,12), (7 ,21), (9 , 2), (11,11), (4 , 5), (1 ,11), (0 ,23), (1 ,13), (4 , 6), (9 ,15)],
        [(0,Z), (3 , 4), (6 ,17), (9 ,20), (12,26), (2 , 2), (5 ,12), (8 ,29), (11, 1), (1 , Z), (4 ,15), (7 ,16), (10,27), (9 , 2), (4 , 7), (1 , 5), (0 ,23), (1 ,24), (4 , 8)],
        [(0,Z), (4 , 4), (8 ,29), (12, 8), (3 , 3), (7 , 8), (11, 2), (2 ,17), (6 , 4), (10, 2), (1 ,21), (5 ,29), (9 ,20), (3 , 2), (9 , 1), (4 ,14), (1 ,21), (0 ,24), (1 ,28)],
        [(0,Z), (5 , 4), (10,22), (2 ,18), (7 , 6), (12, 2), (4 ,18), (9 ,27), (1 ,15), (6 , Z), (11,20), (3 ,15), (8 , 9), (12, 9), (3 , 3), (9 ,13), (4 , 4), (1 , 7), (0 ,14)],
        [(0,Z), (6 , Z), (12,23), (5 ,13), (11,11), (4 ,10), (10, 0), (3 , 4), (9 ,16), (2 ,28), (8 ,27), (1 , 1), (7 ,23), (10,17), (12, 9), (3 ,20), (9 ,16), (4 ,17), (1 ,26)],
        [(0,Z), (7 , Z), (1 , 3), (8 ,13), (2 , 8), (9 , 9), (3 , 0), (10,26), (4 , 5), (11, 6), (5 ,22), (12, 1), (6 ,17), (10,10), (10, 5), (12,15), (3 ,25), (9 , Z), (4 , 4)],
        [(0,Z), (8 , 4), (3 ,10), (11, 3), (6 ,17), (1 ,21), (9 ,18), (4 , 5), (12,27), (7 ,20), (2 ,16), (10,25), (5 ,22), (12,21), (10,25), (10,12), (12,28), (3 ,19), (9 ,29)],
        [(0,Z), (9 , 4), (5 , 6), (1 ,16), (10, 4), (6 ,24), (2 ,14), (11,11), (7 , 2), (3 , 9), (12,30), (8 ,28), (4 , 2), (3 , 7), (12, 6), (10,17), (10, 2), (12,13), (3 ,26)],
        [(0,Z), (10, 4), (7 ,11), (4 ,18), (1 ,23), (11,21), (8 ,28), (5 ,21), (2 ,29), (12,20), (9 , 0), (6 , 8), (3 , 6), (9 , 7), (3 ,12), (12, 5), (10, 1), (10,21), (12, 5)],
        [(0,Z), (11, 4), (9 ,22), (7 ,11), (5 ,17), (3 , Z), (1 ,17), (12,25), (10,14), (8 ,18), (6 , 2), (4 ,17), (2 ,25), (4 ,29), (9 , 6), (3 , 2), (12, 8), (10,13), (10,14)],
        [(0,Z), (12, Z), (11, 7), (10,26), (9 ,24), (8 , 4), (7 ,25), (6 , Z), (5 ,13), (4 , 9), (3 , 5), (2 ,19), (1 ,10), (1 ,26), (4 ,14), (9 , 7), (3 ,11), (12, 9), (10,20)],
        [(0,Z), (5 , Z), (7 , 7), (6 ,27), (2 , 5), (8 , 1), (11,23), (11, Z), (8 ,23), (2 ,21), (6 ,20), (7 , 5), (5 , 6), (0 , 2), (2 ,12), (8 ,15), (5 ,22), (6 ,25), (11,10)],
        [(0,Z), (6 , 4), (9 ,24), (9 ,18), (6 ,26), (0 ,26), (4 ,17), (5 ,24), (3 , 5), (11, 9), (3 ,15), (5 ,23), (4 ,22), (2 ,26), (0 , 8), (2 ,21), (8 ,25), (5 ,15), (6 , 8)],
        [(0,Z), (7 , 4), (11,11), (12, 9), (10,10), (5 , 6), (10, 1), (12,24), (11, 6), (7 ,26), (0 , 8), (3 ,10), (3 ,29), (8 , 3), (2 ,24), (0 ,22), (2 ,13), (8 , 2), (5 , 0)],
        [(0,Z), (8 , Z), (0 ,27), (2 , 0), (1 ,25), (10,21), (3 ,10), (6 ,20), (6 ,14), (3 , 1), (10, 3), (1 ,15), (2 ,14), (5 ,12), (8 ,11), (2 ,28), (0 ,15), (2 ,13), (8 ,22)],
        [(0,Z), (9 , Z), (2 ,13), (5 ,11), (5 , 6), (2 ,24), (9 , 9), (0 ,14), (1 ,30), (12, 1), (7 ,15), (12,15), (1 , 5), (6 ,23), (5 , 9), (8 , 3), (2 ,27), (0 ,28), (2 ,12)],
        [(0,Z), (10, Z), (4 ,18), (8 ,23), (9 ,27), (7 , 4), (2 , 2), (7 , Z), (9 ,10), (8 , 8), (4 , 0), (10,12), (0 ,21), (11,28), (6 ,15), (5 ,23), (8 , 5), (2 ,28), (0 , 7)],
        [(0,Z), (11, Z), (6 , 7), (11,27), (0 , 0), (12,17), (8 ,11), (1 ,12), (4 ,22), (4 ,15), (1 ,16), (8 , 0), (12, 6), (7 ,16), (11,30), (6 ,21), (5 ,14), (8 ,17), (2 ,26)],
        [(0,Z), (12, 4), (8 ,28), (1 ,22), (4 , 2), (4 ,15), (1 , 6), (8 ,12), (12,19), (0 ,21), (11, 2), (6 , 4), (11,19), (7 ,30), (7 ,11), (11,12), (6 ,20), (5 , 3), (8 , 7)],
        [(0,Z), (0 , 4), (10,21), (4 , 4), (8 , 1), (9 , 6), (7 ,30), (2 , 4), (7 , 8), (9 ,30), (8 , 3), (4 ,22), (10, 3), (11,25), (7 , 1), (7 ,24), (11,20), (6 ,30), (5 , 4)],
        [(0,Z), (1 , 4), (12,21), (7 , 3), (12, 2), (1 , 1), (0 , 6), (9 ,14), (2 ,19), (5 , 6), (5 ,12), (2 , 9), (9 , 9), (6 ,19), (11, Z), (7 , 4), (7 , 6), (11,29), (6 ,15)],
        [(0,Z), (2 , Z), (1 ,22), (10, Z), (3 , 5), (6 ,30), (6 ,26), (3 , 1), (10,12), (1 ,16), (2 ,28), (0 ,20), (8 ,11), (5 ,29), (6 , 7), (11,21), (7 ,14), (7 , 8), (11,11)],
        [(0,Z), (3 , Z), (3 , 4), (0 ,18), (7 , 2), (11,16), (12,28), (10, 4), (5 ,28), (10, 0), (12, 4), (11,10), (7 ,11), (8 ,17), (5 , 6), (6 ,16), (11, 4), (7 ,22), (7 ,28)],
        [(0,Z), (4 , Z), (5 ,22), (3 ,18), (11, Z), (3 ,15), (5 , 1), (4 ,26), (0 ,10), (6 , 8), (9 , 9), (9 ,29), (6 , Z), (2 ,23), (8 ,28), (5 ,30), (6 , 8), (11,24), (7 ,16)]
    ]

    Y = [None, 0, 1, 2, 18, 5, 11, 4, 13, 26, 25, 29, 24, 7, 20, 19, 9, 12, 15]

    return _helper_function_when_n_is_prime_times_power_of_2(20,416,zip(*A),Y)

def OA_12_474():
    r"""
    Returns an OA(12,474)

    Given by Julian R. Abel, using a `V(m,t)` from the Handbook
    [DesignHandbook]_.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_Vmt`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_12_474
        sage: OA = OA_12_474()
        sage: print is_orthogonal_array(OA,12,474,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(12,474,existence=True)
        True
    """
    M = OA_from_Vmt(10,43,[0,1,6,29,170,207,385,290,375,32,336])
    return M

def OA_9_514():
    r"""
    Returns an OA(9,514)

    Construction shared by Julian R. Abel:

        A `V(8,57)` vector appears on page p281 of the Brouwer-Van Rees paper
        [BvR82]_. This gives a `TD(8+2, 514) - TD(8+2,57)`. Using a `TD(9,57)`
        (not a `TD(10,57)`) it yields a `TD(9,514)`.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_Vmt`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_9_514
        sage: OA = OA_9_514()
        sage: print is_orthogonal_array(OA,9,514,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(9,514,existence=True)
        True
    """
    from sage.rings.finite_rings.constructor import FiniteField
    q = 8*57+1
    Fq = FiniteField(q)

    Vm8_57 = [0,1,3,2,12,333,363,154,340]
    QDM = QDM_from_Vmt(8,57,Vm8_57)
    QDM = QDM[:-1]
    return OA_from_quasi_difference_matrix(QDM,Fq,add_col=False)

def OA_20_544():
    r"""
    Returns an OA(20,544)

    Published by Julian R. Abel in [AbelThesis]_.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_quasi_difference_matrix`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_20_544
        sage: OA = OA_20_544()                        # not tested (too long ~1mn)
        sage: print is_orthogonal_array(OA,20,544,2)  # not tested
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(20,544,existence=True)
        True
    """
    Z = None

    A=[
        [(0,Z),(0 , Z),(0 , Z),(0 , Z),(0 , Z),(0 , Z),(0 , Z),(0 , Z),(0 , Z),(0 , Z),(0 , Z),(0 , Z),(0 , Z),(0 , Z),(0 , Z),(0 , Z),(0 , Z),(0 , Z),(1 , Z)],
        [(0,Z),(1 , 4),(2 , 7),(3 ,30),(4 ,17),(5 , 2),(6 ,22),(7 ,23),(8 ,28),(9 , 2),(10,27),(11,26),(12,13),(13,25),(14,18),(15,15),(16,18),(1 ,14),(0 , 1)],
        [(0,Z),(2 , 4),(4 ,20),(6 ,29),(8 ,27),(10, 7),(12,20),(14,19),(16,26),(1 ,28),(3 , Z),(5 ,27),(7 , Z),(9 ,11),(11, Z),(13,17),(15, 1),(4 ,14),(1 ,14)],
        [(0,Z),(3 , Z),(6 ,14),(9 ,26),(12,17),(15,15),(1 ,26),(4 ,24),(7 ,27),(10,13),(13,10),(16, 7),(2 , 1),(5 , Z),(8 , 1),(11,15),(14,18),(9 ,21),(4 , 6)],
        [(0,Z),(4 , 4),(8 , Z),(12, 2),(16,23),(3 ,19),(7 ,26),(11, 7),(15,26),(2 , 3),(6 ,11),(10,16),(14,23),(1 ,30),(5 , 1),(9 ,30),(13,19),(16,10),(9 , 4)],
        [(0,Z),(5 , Z),(10,17),(15,19),(3 ,13),(8 , 4),(13,21),(1 , 9),(6 , 7),(11, 4),(16,24),(4 , 6),(9 ,11),(14, Z),(2 , 6),(7 ,14),(12,10),(8 ,12),(16, 1)],
        [(0,Z),(6 , Z),(12, 1),(1 ,23),(7 ,21),(13,10),(2 , 0),(8 ,15),(14,19),(3 ,30),(9 ,21),(15,17),(4 ,25),(10,20),(16,15),(5 ,16),(11,15),(2 ,22),(8 ,29)], # 2,Z -> 2,0
        [(0,Z),(7 , Z),(14,30),(4 ,26),(11,24),(1 ,22),(8 ,22),(15,27),(5 ,23),(12,13),(2 ,18),(9 ,22),(16, 6),(6 ,27),(13,19),(3 , 1),(10,16),(15, 9),(2 , 5)],
        [(0,Z),(8 , 4),(16, 5),(7 ,18),(15,11),(6 , 1),(14,21),(5 ,28),(13,19),(4 , 7),(12,19),(3 ,15),(11,13),(2 ,23),(10, 1),(1 ,23),(9 ,19),(13,27),(15,25)], # 13,9 -> 15,25
        [(0,Z),(9 , Z),(1 , 3),(10, 4),(2 ,29),(11,13),(3 ,27),(12,11),(4 ,30),(13, 9),(5 ,18),(14,17),(6 ,18),(15,10),(7 ,11),(16,28),(8 ,26),(13,12),(13, 9)],
        [(0,Z),(10, Z),(3 ,18),(13,21),(6 , 8),(16, 1),(9 ,11),(2 ,11),(12,12),(5 ,20),(15,21),(8 ,12),(1 , 5),(11,28),(4 ,16),(14,16),(7 ,21),(15, 0),(13,20)],
        [(0,Z),(11, 4),(5 ,25),(16, 2),(10,18),(4 , 6),(15,20),(9 ,29),(3 ,13),(14,24),(8 ,18),(2 ,22),(13, 1),(7 , 8),(1 ,21),(12,16),(6 ,23),(2 ,10),(15,26)],
        [(0,Z),(12, 4),(7 ,11),(2 , 4),(14,25),(9 , 0),(4 , 5),(16,21),(11,18),(6 ,18),(1 ,22),(13,27),(8 ,23),(3 ,20),(15,18),(10, 7),(5 ,10),(8 ,11),(2 ,18)],
        [(0,Z),(13, Z),(9 ,21),(5 ,17),(1 ,26),(14,30),(10,11),(6 , 1),(2 , 8),(15, 9),(11, 5),(7 ,29),(3 ,17),(16, 3),(12, 3),(8 ,30),(4 , 3),(16, 5),(8 ,21)],
        [(0,Z),(14, Z),(11,20),(8 ,24),(5 , Z),(2 , 2),(16,24),(13,12),(10,21),(7 ,26),(4 ,29),(1 , 1),(15, 1),(12,19),(9 , 8),(6 ,26),(3 ,10),(9 ,20),(16,21)],
        [(0,Z),(15, Z),(13,21),(11,10),(9 , 7),(7 ,21),(5 ,11),(3 ,19),(1 ,29),(16,13),(14, 9),(12, 9),(10, 8),(8 ,16),(6 ,15),(4 ,14),(2 ,29),(4 ,16),(9 , 9)],
        [(0,Z),(16, 4),(15,19),(14,21),(13, 0),(12,13),(11,28),(10,21),(9 , 5),(8 ,18),(7 , 2),(6 , Z),(5 ,20),(4 ,26),(3 , 8),(2 , 9),(1 ,23),(1 ,19),(4 ,23)], # 13,Z -> 13,0
        [(0,Z),(3 , 4),(12,11),(10,17),(14,14),(7 , 1),(6 ,27),(11,25),(5 , 2),(5 ,24),(11,15),(6 , 8),(7 ,28),(14,21),(10, 4),(12,20),(3 ,26),(0 , 5),(3 ,12)],
        [(0,Z),(4 , Z),(14,17),(13,26),(1 ,12),(12,12),(12,23),(1 ,13),(13, 7),(14,10),(4 ,28),(0 ,11),(2 , 7),(10,15),(7 , Z),(10, 1),(2 , 6),(3 ,24),(0 ,18)],
        [(0,Z),(5 , 4),(16,24),(16, 1),(5 ,27),(0 ,14),(1 ,11),(8 ,13),(4 ,25),(6 ,25),(14,14),(11, 6),(14, 4),(6 ,24),(4 , 4),(8 ,28),(1 ,14),(12,22),(3 ,11)],
        [(0,Z),(6 , 4),(1 ,10),(2 , 6),(9 ,12),(5 , 3),(7 ,11),(15,30),(12,21),(15,26),(7 , 3),(5 ,12),(9 , 0),(2 ,25),(1 , 2),(6 , 0),(0 ,13),(10,13),(12,14)],
        [(0,Z),(7 , 4),(3 ,24),(5 ,25),(13,20),(10,19),(13,16),(5 , 4),(3 ,23),(7 ,20),(0 , 8),(16, 4),(4 ,19),(15, 0),(15,10),(4 ,11),(16, 7),(14,11),(10, 6)],
        [(0,Z),(8 , Z),(5 , 1),(8 ,21),(0 , 1),(15,17),(2 ,26),(12, 2),(11, 6),(16, 2),(10,15),(10,13),(16,16),(11,12),(12,22),(2 ,11),(15,22),(7 ,30),(14,22)], # 8,9 -> 8,21
        [(0,Z),(9 , 4),(7 ,20),(11,24),(4 , 7),(3 ,11),(8 ,21),(2 ,23),(2 , 2),(8 ,12),(3 , 8),(4 ,13),(11,17),(7 , 4),(9 , 3),(0 ,18),(14,12),(6 ,26),(7 ,28)],
        [(0,Z),(10, 4),(9 ,22),(14,23),(8 , 5),(8 , 8),(14,12),(9 , 6),(10,20),(0 ,11),(13,23),(15,26),(6 ,12),(3 ,15),(6 , Z),(15,18),(13, 1),(11,22),(6 ,24)],
        [(0,Z),(11, Z),(11,11),(0 ,28),(12,16),(13,18),(3 , 3),(16,22),(1 , 9),(9 , Z),(6 ,21),(9 , 6),(1 , 0),(16, 1),(3 , 2),(13,28),(12, 6),(5 ,18),(11, 9)],
        [(0,Z),(12, Z),(13, 5),(3 ,14),(16,22),(1 , 5),(9 , 1),(6 , Z),(9 , 3),(1 , 9),(16,21),(3 ,18),(13,17),(12,29),(0 ,13),(11, 4),(11,18),(5 ,21),(5 , 6)],
        [(0,Z),(13, 4),(15,27),(6 ,26),(3 ,20),(6 ,29),(15,11),(13,18),(0 , 4),(10, 5),(9 ,16),(14,26),(8 ,20),(8 , 8),(14,11),(9 ,10),(10, 9),(11,17),(5 ,21)],
        [(0,Z),(14, 4),(0 ,29),(9 , 8),(7 , 2),(11,18),(4 ,22),(3 ,22),(8 ,13),(2 ,23),(2 ,21),(8 , 9),(3 ,30),(4 ,21),(11, 5),(7 ,25),(9 , Z),(6 , 0),(11,17)],
        [(0,Z),(15, 4),(2 ,27),(12,27),(11,28),(16, 0),(10, 6),(10,12),(16,11),(11,15),(12, 2),(2 ,10),(15,19),(0 ,11),(8 ,10),(5 , 6),(8 , 5),(7 , 7),(6 ,16)],
        [(0,Z),(16, Z),(4 ,23),(15, 4),(15,30),(4 ,27),(16,12),(0 , 8),(7 , 9),(3 , 6),(5 ,26),(13,28),(10,12),(13,14),(5 ,30),(3 ,27),(7 , 6),(14,15),(7 ,18)],
        [(0,Z),(0 , 4),(6 ,13),(1 ,14),(2 , 2),(9 ,11),(5 , 5),(7 ,13),(15,24),(12,16),(15,20),(7 ,24),(5 ,19),(9 ,25),(2 ,26),(1 ,20),(6 ,28),(10, 5),(14,11)],
        [(0,Z),(1 , Z),(8 ,25),(4 , 5),(6 , 6),(14, 6),(11,11),(14,22),(6 , 2),(4 , 2),(8 ,14),(1 ,13),(0 , 3),(5 , 6),(16,21),(16,11),(5 , 8),(12,15),(10,20)], # 12,14->12,15
        [(0,Z),(2 , Z),(10,19),(7 ,29),(10,22),(2 ,23),(0 ,15),(4 ,19),(14, 6),(13,14),(1 , 5),(12,24),(12, 8),(1 , 4),(13, 1),(14,21),(4 ,17),(3 , 3),(12,27)],
    ]

    Y = [None, 0, 1, 2, 18, 5, 11, 4, 13, 26, 25, 29, 24, 7, 20, 19, 9, 12, 15]
    return _helper_function_when_n_is_prime_times_power_of_2(20,544,zip(*A),Y)

def OA_17_560():
    r"""
    Returns an OA(17,560)

    This OA is built in Corollary 2.2 of [Thwarts]_.

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_17_560
        sage: OA = OA_17_560()
        sage: print is_orthogonal_array(OA,17,560,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(17,560,existence=True)
        True
    """
    from sage.rings.finite_rings.constructor import FiniteField as GF
    alpha = 5
    beta  = 4
    p     = 2
    k     = 17
    m     = 16
    n     = p**alpha

    G = GF(p**alpha,prefix='x',conway=True)
    G_set = sorted(G) # sorted by lexicographic order, G[1] = 1
    G_to_int = {v:i for i,v in enumerate(G_set)}
    # Builds an OA(n+1,n) whose last n-1 colums are
    #
    # \forall x \in G and x!=0, C_x(i,j) = i+x*j
    #
    # (only the necessary columns are built)
    OA = [[G_to_int[i+x*j] for i in G_set for j in G_set] for x in G_set[k+1:0:-1]]
    OA.append([j for i in range(n) for j in range(n)])
    OA.append([i for i in range(n) for j in range(n)])

    # The additive group F_{p^beta} appears in F_{p^alpha} as all polynomials
    # with degree < beta
    #
    # We remove all elements except those from F_{p^alpha} in the last three
    # columns

    elements_of_subgroup = set([x for x in G_set if x.polynomial().degree() < beta])
    relabel = {G_to_int[v]:i for i,v in enumerate(elements_of_subgroup)}
    for x in range(p**alpha):
        if x not in relabel:
            relabel[x] = None

    for C in OA[-3:]:
        for i,x in enumerate(C):
            C[i] = relabel[x]

    OA=zip(*OA)

    return wilson_construction(OA,k,n,m,3,[p**beta]*3,check=False)

def OA_11_640():
    r"""
    Returns an OA(11,640)

    Published by Julian R. Abel in [AbelThesis]_.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_quasi_difference_matrix`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_11_640
        sage: OA = OA_11_640()                        # not tested (too long)
        sage: print is_orthogonal_array(OA,11,640,2)  # not tested (too long)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(11,640,existence=True)
        True
    """
    A = [
        [(0,None), (0,None), (0,None), (0,None), (0,None), (0,None), (1,None), (4,None), (4,None), (1,None)],
        [(0,None), (1,None), (2,   7), (3,  55), (4,  54), (1,  87), (0, 124), (1, 123), (4,  83), (4,  61)], # 0,25 became 0,124
        [(0,None), (2,None), (4,  14), (1,  63), (3,   6), (4,  87), (1,  16), (0,  47), (1,  29), (4,  16)],
        [(0,None), (3,None), (1,   1), (4,  15), (2,   5), (4,  32), (4,  30), (1,   3), (0,  12), (1,  14)],
        [(0,None), (4,None), (3,  28), (2,  62), (1,  64), (1,  55), (4,  63), (4,   4), (1,   0), (0,   0)],
        [(0,None), (2,   6), (3,   8), (3,   7), (2,  12), (0,   1), (2,   6), (3,  97), (3,  45), (2,   0)],
        [(0,None), (3,   6), (0,  63), (1,   5), (1,   6), (2,  97), (0,  28), (2,  63), (3,   0), (3,   2)],
        [(0,None), (4,   6), (2,   4), (4,  65), (0,   6), (3,  68), (2,   1), (0,  14), (2,   1), (3,   0)],
        [(0,None), (0,   6), (4,   9), (2,None), (4,  29), (3,  15), (3,   0), (2,   1), (0,   7), (2,   4)],
        [(0,None), (1,   6), (1,  14), (0,  14), (3,   4), (2,   0), (3,None), (3,   4), (2,   0), (0,None)]
    ]
    Y = [None, 0, 1, 2, 121, 66, 77, 78, 41, 100]
    return _helper_function_when_n_is_prime_times_power_of_2(11,640,zip(*A),Y)

def OA_10_796():
    r"""
    Returns an OA(10,796)

    Construction shared by Julian R. Abel, from [AC07]_:

        Truncate one block of a `TD(17,47)` to size `13`, then add an extra
        point. Form a block on each group plus the extra point: we obtain a
        `(796, \{13,16,17,47,48\})`-PBD in which only the extra point lies in
        more than one block of size `48` (and each other point lies in exactly 1
        such block).

        For each block `B` (of size `k` say) not containing the extra point,
        construct a `TD(10, k) - k.TD(k,1)` on `I(10) X B`.  For each block `B`
        (of size `k=47` or `48`) containing the extra point, construct a
        `TD(10,k) - TD(k,1)` on `I(10) X B`, the size `1` hole being on `I(10) X
        P` where `P` is the extra point. Finally form `1` extra block of size
        `10` on `I(10) X P`.

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_10_796
        sage: OA = OA_10_796()
        sage: print is_orthogonal_array(OA,10,796,2)
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(10,796,existence=True)
        True
    """
    from sage.combinat.designs.orthogonal_arrays import OA_relabel
    from sage.combinat.designs.orthogonal_arrays import OA_from_PBD
    from orthogonal_arrays import incomplete_orthogonal_array

    OA = orthogonal_array(17,47)
    OA = OA_relabel(OA,17,47,blocks=[OA[0]]) # making sure [46]*17 is a block
    PBD = [[i*47+x for i,x in enumerate(B) if (x<46 or i<13)] for B in OA]
    extra_point = 10000
    PBD.extend([range(i*47,(i+1)*47-int(i>=13))+[extra_point] for i in range(17)]) # Adding the columns

    rel = {v:i for i,v in enumerate(set(range(17*47)).difference([(i+1)*47-1 for i in range(13,17)]))}
    rel[extra_point] = len(rel)

    PBD = [[rel[x] for x in B] for B in PBD]
    assert set(map(len,PBD)) == set([13, 16, 17, 47, 48])
    extra_point = rel[extra_point]

    others = []
    OA = []
    span = set()
    iOA = {47: incomplete_orthogonal_array(10,47,(1,)),
           48: incomplete_orthogonal_array(10,48,(1,))}

    for B in PBD:
        if len(B) >= 47:
            B.sort(key=lambda x:int(x==extra_point))
            OA.extend([[B[i] for i in BB] for BB in iOA[len(B)]])
            span.update(B[:-1])
        else:
            others.append(B)

    OA.extend(OA_from_PBD(10,796,others,check=False))
    OA = OA[:-796] # removes the [x]*k

    for x in set(range(796)).difference(span):
        OA.append([x]*10)

    return OA

def OA_15_896():
    r"""
    Returns an OA(15,896)

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_quasi_difference_matrix`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_15_896
        sage: OA = OA_15_896()                          # not tested -- too long (~2min)
        sage: print is_orthogonal_array(OA,15,896,2)    # not tested -- too long
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(15,896,existence=True)
        True
    """
    A = [
        [(0,None), (0,None), (0,None), (0,None), (0,None), (0,None), (0,None), (0,None), (1,None), (4,None), (2,None), (2,None), (4,None), (1,None)],
        [(0,None), (1,None), (2,  17), (3,  20), (4,  49), (5,   4), (6,  59), (1,  15), (0, 114), (1,  76), (4, 106), (2,  87), (2, 118), (4,  49)], # 4,120 became the leftmost 4,49
        [(0,None), (2,None), (4,   2), (6,  98), (1,  53), (3,  97), (5, 123), (4,   3), (1,  32), (0,  10), (1,  45), (4,   3), (2,   1), (2,  14)],
        [(0,None), (3,None), (6,  16), (2,  86), (5, 102), (1,  64), (4,  69), (2,  11), (4,  55), (1,  90), (0, 115), (1,  15), (4,   7), (2,   0)],
        [(0,None), (4,None), (1,   4), (5, 110), (2,  51), (6, 118), (3,   8), (2,  81), (2,  79), (4,  98), (1,   2), (0,   3), (1,   7), (4,None)],
        [(0,None), (5,None), (3,  66), (1,  70), (6, 102), (4, 119), (2,  20), (4,  86), (2,  59), (2,  15), (4,  63), (1, 126), (0,   1), (1,   0)],
        [(0,None), (6,None), (5,  94), (4,  48), (3,  90), (2,   2), (1,  13), (1,  53), (4, 117), (2,  21), (2,   2), (4,   1), (1,   0), (0,   0)],
        [(0,None), (4,   6), (2,  21), (1, 112), (1,  36), (2,  14), (4,  60), (0,   1), (6,  64), (3,   0), (5,  31), (5,   3), (3,   3), (6,  14)],
        [(0,None), (5,   6), (4,  61), (4,None), (5, 108), (0,  91), (3,  10), (6,  15), (0,None), (6,  15), (3,   7), (5,   0), (5,   1), (3,   0)],
        [(0,None), (6,   6), (6, 107), (0,  88), (2,  12), (5,  44), (2,  31), (3,  64), (6,   0), (0,None), (6,   2), (3,   3), (5,None), (5,   0)],
        [(0,None), (0,   6), (1,  52), (3, 115), (6,  30), (3,  78), (1,  64), (5,  63), (3,   5), (6,None), (0,None), (6,   3), (3,   1), (5,None)],
        [(0,None), (1,   6), (3, 117), (6,  19), (3,   9), (1,  31), (0,  56), (5,   0), (5,  63), (3,None), (6,None), (0,None), (6,   7), (3,None)],
        [(0,None), (2,   6), (5, 116), (2,   3), (0,   0), (6,None), (6,   1), (3,   0), (5,   0), (5,   2), (3,None), (6,None), (0,None), (6,   0)],
        [(0,None), (3,   6), (0,   0), (5,   0), (4,   1), (4,None), (5,None), (6,   0), (3,   2), (5,   0), (5,None), (3,None), (6,None), (0,None)] # 0,0 became the rightmost 0,None
    ]

    Y = [None, 0,1,2,121,66,77,78,41,100,74,118,108,43]

    return _helper_function_when_n_is_prime_times_power_of_2(15,896,zip(*A),Y)

def OA_14_950():
    r"""
    Returns an OA(14,950)

    Given by Julian R. Abel.

    .. SEEALSO::

        :func:`sage.combinat.designs.orthogonal_arrays.OA_from_Vmt`

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_14_950
        sage: OA = OA_14_950()                        # not tested -- around 10s
        sage: print is_orthogonal_array(OA,14,950,2)  # not tested
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(14,950,existence=True)
        True
    """
    return OA_from_Vmt(12,73,[0, 1, 607, 719, 837, 496, 240, 645, 184, 829, 451, 830, 770])

def OA_33_993():
    r"""
    Returns an OA(33,993)

    Given by Julian R. Abel.

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_33_993
        sage: OA = OA_33_993()                          # not tested -- too long
        sage: print is_orthogonal_array(OA,33,993,2)    # not tested -- too long
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(33,993,existence=True)
        True
    """
    M = orthogonal_array(32,32)
    M = [R for R in M if any(x!=R[0] for x in R)] # removing the 0..0, 1..1, ... rows.
    B = (0,74,81,126,254,282,308,331,344,375,387,409,525,563, # (993,32,1) difference set
         572,611,631,661,694,702,734,763,798,809,814,851,906,
         908,909,923,927,933)
    M = [[B[x] for x in R] for R in M]
    M.append([0]*32)
    Mb = zip(*M)

    from sage.rings.finite_rings.integer_mod_ring import IntegerModRing as AdditiveCyclic
    G = AdditiveCyclic(993)
    M = OA_from_quasi_difference_matrix(Mb,G,add_col=True)
    return M

def OA_10_1046():
    r"""
    Returns an `OA(10,1046)`.

    Proved by Lemma 3.5 from [Thwarts]_.

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_10_1046
        sage: OA = OA_10_1046()                           # not tested -- around 5s
        sage: print is_orthogonal_array(OA,10,1046,2)     # not tested
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(10,1046,existence=True)
        True
    """
    from sage.combinat.designs.orthogonal_arrays_recursive import thwart_lemma_3_5
    return thwart_lemma_3_5(10, 13, 78, 9, 9, 13, 1, complement=True)

def OA_10_1059():
    r"""
    Returns an `OA(10,1059)`.

    Proved by Lemma 3.5 from [Thwarts]_.

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_10_1059
        sage: OA = OA_10_1059()                           # not tested -- around 6s
        sage: print is_orthogonal_array(OA,10,1059,2)     # not tested
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(10,1059,existence=True)
        True
    """
    from sage.combinat.designs.orthogonal_arrays_recursive import thwart_lemma_3_5
    return thwart_lemma_3_5(10, 13, 79, 9, 9, 13, 1, complement=True)

def OA_11_2164():
    r"""
    Returns an `OA(11,2164)`.

    Proved by Lemma 3.5 from [Thwarts]_.

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_11_2164
        sage: OA = OA_11_2164()                           # not tested -- around 15s
        sage: print is_orthogonal_array(OA,11,2164,2)     # not tested
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(10,2164,existence=True)
        True
    """
    from sage.combinat.designs.orthogonal_arrays_recursive import thwart_lemma_3_5
    return thwart_lemma_3_5(11, 27, 78, 16, 17, 25, 0, complement=True)

def OA_12_3992():
    r"""
    Returns an `OA(12,3992)`.

    Proved by Lemma 3.5 from [Thwarts]_.

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_12_3992
        sage: OA = OA_12_3992()                           # not tested -- around 60s
        sage: print is_orthogonal_array(OA,12,3992,2)     # not tested
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(12,3992,existence=True)
        True
    """
    from sage.combinat.designs.orthogonal_arrays_recursive import thwart_lemma_3_5
    return thwart_lemma_3_5(12, 19, 208, 11, 13, 16, 0, complement=True)

def OA_12_3994():
    r"""
    Returns an `OA(12,3994)`.

    Proved by Lemma 3.5 from [Thwarts]_.

    EXAMPLES::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_12_3994
        sage: OA = OA_12_3994()                           # not tested -- around 60s
        sage: print is_orthogonal_array(OA,12,3994,2)     # not tested
        True

    The design is available from the general constructor::

        sage: designs.orthogonal_array(12,3994,existence=True)
        True
    """
    from sage.combinat.designs.orthogonal_arrays_recursive import thwart_lemma_3_5
    return thwart_lemma_3_5(12, 19, 208, 13, 13, 16, 0, complement=True)

def _helper_function_when_n_is_prime_times_power_of_2(k,n,A,Y):
    r"""
    This is an helper function to build `OA(k,p2^c)`

    The same construction appears many times in Julian R. Abel's papers to build
    `OA(k,p2^c)`. Having this function avoids a lot of copy/paste.

    For more information on what the parameters should be, see the documentation
    of the functions which calls this one, and their associated bibliographical
    references.

    INPUT:

    - ``k,n`` (integers) -- parameters of the desired `OA`

    - ``A`` -- a matrix

    - ``Y`` -- a vector

    EXAMPLE::

        sage: from sage.combinat.designs.designs_pyx import is_orthogonal_array
        sage: from sage.combinat.designs.database import OA_9_40
        sage: OA = OA_9_40()                       # indirect doctest
        sage: print is_orthogonal_array(OA,9,40,2) # indirect doctest
        True
    """
    from sage.rings.finite_rings.constructor import FiniteField
    from sage.rings.integer import Integer
    from itertools import combinations

    c = Integer(n).valuation(2)
    F = FiniteField(n//2**c)
    Fq = FiniteField(2**c,prefix='w',conway=True)
    G = F.cartesian_product(Fq)
    w = Fq.gens()[0]

    r = lambda x : Fq(0) if x is None else w**x
    A = [[G((a,r(b))) for a,b in L] for L in A]

    Y = map(r,Y)

    t = lambda i,x : G((0,Y[x]*w**i))

    Mb = [[] for _ in A]
    Subsets = [S for s in range(c) for S in combinations(range(c-1),s)]
    assert len(Subsets) == 2**(c-1)

    for x,R in enumerate(A):
        tt = [t(i,x) for i in range(c-1)]
        for y,e in enumerate(R):
            Mb[x].extend([e+sum([tt[ii] for ii in S],G.zero()) for S in Subsets])

    M = OA_from_quasi_difference_matrix(Mb,G,add_col = int(k-len(A)))
    return M

# Index of the OA constructions
#
# Associates to n the pair (k,f) where f() is a function that returns an OA(k,n)
#
# This dictionary is used by designs.orthogonal_array(k,n).

OA_constructions = {
    18  : (7  , OA_7_18),
    20  : (6  , OA_6_20),
    21  : (7  , OA_7_21),
    22  : (5  , OA_5_22),
    24  : (9  , OA_9_24),
    26  : (6  , OA_6_26),
    28  : (7  , OA_7_28),
    30  : (6  , OA_6_30),
    33  : (7  , OA_7_33),
    34  : (6  , OA_6_34),
    35  : (7  , OA_7_35),
    36  : (10 , OA_10_36),
    38  : (6  , OA_6_38),
    39  : (7  , OA_7_39),
    40  : (9  , OA_9_40),
    42  : (7  , OA_7_42),
    44  : (7  , OA_7_44),
    45  : (8  , OA_8_45),
    46  : (6  , OA_6_46),
    48  : (10 , OA_10_48),
    50  : (8  , OA_8_50),
    51  : (7  , OA_7_51),
    52  : (7  , OA_7_52),
    54  : (7  , OA_7_54),
    55  : (8  , OA_8_55),
    56  : (9  , OA_9_56),
    57  : (9  , OA_9_57),
    60  : (7  , OA_7_60),
    62  : (7  , OA_7_62),
    65  : (9  , OA_9_65),
    66  : (7  , OA_7_66),
    68  : (7  , OA_7_68),
    69  : (8  , OA_8_69),
    74  : (7  , OA_7_74),
    75  : (9  , OA_9_75),
    76  : (8  , OA_8_76),
    80  : (11 , OA_11_80),
    82  : (10 , OA_10_82),
    100 : (10 , OA_10_100),
    112 : (15 , OA_15_112),
    120 : (9  , OA_9_120),
    135 : (9  , OA_9_135),
    144 : (12 , OA_12_144),
    154 : (10 , OA_10_154),
    160 : (11 , OA_11_160),
    176 : (16 , OA_16_176),
    208 : (16 , OA_16_208),
    210 : (12 , OA_12_210),
    224 : (15 , OA_15_224),
    262 : (10 , OA_10_262),
    273 : (18 , OA_18_273),
    276 : (12 , OA_12_276),
    298 : (12 , OA_12_298),
    342 : (12 , OA_12_342),
    352 : (20 , OA_20_352),
    416 : (20 , OA_20_416),
    474 : (12 , OA_12_474),
    514 : (9  , OA_9_514),
    544 : (20 , OA_20_544),
    560 : (17 , OA_17_560),
    640 : (11 , OA_11_640),
    796 : (10 , OA_10_796),
    896 : (15 , OA_15_896),
    950 : (14 , OA_14_950),
    993 : (33 , OA_33_993),
    1046: (10,  OA_10_1046),
    1059: (10,  OA_10_1059),
    2164: (11,  OA_11_2164),
    3992: (12,  OA_12_3992),
    3994: (12,  OA_12_3994)
}

def CDF_21_5_1():
    r"""
    A cyclic `(21,5,1)`-difference family.

    From the examples VI.16.16 of [DesignHandbook]_.

    EXAMPLES::

        sage: from sage.combinat.designs.database import CDF_21_5_1
        sage: from sage.combinat.designs.difference_family import is_difference_family
        sage: G, D = CDF_21_5_1()
        sage: is_difference_family(G,D,21,5,1)
        True

    The difference family is available from the constructor::

        sage: _ = designs.difference_family(21,5,1)
    """
    D = [[0,1,4,14,16]]
    from sage.rings.finite_rings.integer_mod_ring import Zmod
    return Zmod(21), D

def ADF_5x5_4_1():
    r"""
    An Abelian difference family on `(\ZZ / 5 \ZZ)^2`.

    This is the example 7.26 of [Stinson2004]_.

    EXAMPLES::

        sage: from sage.combinat.designs.database import ADF_5x5_4_1
        sage: from sage.combinat.designs.difference_family import is_difference_family
        sage: G,D = ADF_5x5_4_1()
        sage: is_difference_family(G,D,25,4,1)
        True
    """
    D = [[(0,0),(0,1),(1,0),(2,2)],[(0,0),(0,2),(2,0),(4,4)]]
    from sage.rings.finite_rings.integer_mod_ring import Zmod
    from sage.categories.cartesian_product import cartesian_product
    return cartesian_product([Zmod(5),Zmod(5)]), D

def CDF_37_4_1():
    r"""
    A cyclic `(37,4,1)`-difference family.

    It appears as example 7.28 in [Stinson2004]_ and in the examples VI.16.14 of [DesignHandbook]_.

    EXAMPLES::

        sage: from sage.combinat.designs.database import CDF_37_4_1
        sage: from sage.combinat.designs.difference_family import is_difference_family
        sage: G, D = CDF_37_4_1()
        sage: is_difference_family(G,D,37,4,1)
        True

    The difference family is available from the constructor::

        sage: _ = designs.difference_family(37,4,1)

    """
    D = [[0,1,3,24],[0,4,26,32],[0,10,18,30]]
    from sage.rings.finite_rings.integer_mod_ring import Zmod
    return Zmod(37), D

def CDF_81_5_1():
    r"""
    A cyclic `(81,5,1)`-difference family.

    From the examples VI.16.16 of [DesignHandbook]_.

    EXAMPLES::

        sage: from sage.combinat.designs.database import CDF_81_5_1
        sage: from sage.combinat.designs.difference_family import is_difference_family
        sage: G, D = CDF_81_5_1()
        sage: is_difference_family(G,D,81,5,1)
        True

    The difference family is available from the constructor::

        sage: _ = designs.difference_family(81,5,1)
    """
    D = [[0,1,5,12,26],[0,2,10,40,64],[0,3,18,47,53],[0,9,32,48,68]]
    from sage.rings.finite_rings.integer_mod_ring import Zmod
    return Zmod(81), D

def CDF_91_6_1():
    r"""
    A cyclic `(91,6,1)`-difference family.

    From the examples VI.16.18 of [DesignHandbook]_.

    EXAMPLES::

        sage: from sage.combinat.designs.database import CDF_91_6_1
        sage: from sage.combinat.designs.difference_family import is_difference_family
        sage: G, D = CDF_91_6_1()
        sage: is_difference_family(G,D,91,6,1)
        True

    The difference family is available from the constructor::

        sage: _ = designs.difference_family(91,6,1)
    """
    D = [[0,1,3,7,25,38], [0,16,21,36,48,62], [0,30,40,63,74,82]]
    from sage.rings.finite_rings.integer_mod_ring import Zmod
    return Zmod(91), D

def CDF_121_5_1():
    r"""
    A cyclic `(121,5,1)`-difference family.

    From the examples VI.16.16 of [DesignHandbook]_.

    EXAMPLES::

        sage: from sage.combinat.designs.database import CDF_121_5_1
        sage: from sage.combinat.designs.difference_family import is_difference_family
        sage: G, D = CDF_121_5_1()
        sage: is_difference_family(G,D,121,5,1)
        True

    The difference family is available from the constructor::

        sage: _ = designs.difference_family(121,5,1)
    """
    D = [[0,14,26,51,60],[0,15,31,55,59],[0,10,23,52,58],[0,3,36,56,57],
         [0,7,18,45,50],[0,8,30,47,49]]
    from sage.rings.finite_rings.integer_mod_ring import Zmod
    return Zmod(121), D

def CDF_141_5_1():
    r"""
    A cyclic `(141,5,1)`-difference family.

    From the examples VI.16.16 of [DesignHandbook]_.

    EXAMPLES::

        sage: from sage.combinat.designs.database import CDF_141_5_1
        sage: from sage.combinat.designs.difference_family import is_difference_family
        sage: G, D = CDF_141_5_1()
        sage: is_difference_family(G,D,141,5,1)
        True

    The difference family is available from the constructor::

        sage: _ = designs.difference_family(141,5,1)
    """
    D = [[0,33,60,92,97], [0,3,45,88,110], [0,18,39,68,139],
         [0,12,67,75,113], [0,1,15,84,94], [0,7,11,24,30],
         [0,36,90,116,125]]
    from sage.rings.finite_rings.integer_mod_ring import Zmod
    return Zmod(141), D

def CDF_161_5_1():
    r"""
    A cyclic `(161,5,1)`-difference family.

    From the examples VI.16.16 of [DesignHandbook]_.

    EXAMPLES::

        sage: from sage.combinat.designs.database import CDF_161_5_1
        sage: from sage.combinat.designs.difference_family import is_difference_family
        sage: G, D = CDF_161_5_1()
        sage: is_difference_family(G,D,161,5,1)
        True

    The difference family is available from the constructor::

        sage: _ = designs.difference_family(161,5,1)
    """
    D = [[0,19,34,73,80], [0,16,44,71,79], [0,12,33,74,78],
         [0,13,30,72,77], [0,11,36,67,76], [0,18,32,69,75],
         [0,10,48,68,70], [0,3,29,52,53]]
    from sage.rings.finite_rings.integer_mod_ring import Zmod
    return Zmod(161), D

def CDF_201_5_1():
    r"""
    A cyclic `(201,5,1)`-difference family.

    From the examples VI.16.16 of [DesignHandbook]_.

    EXAMPLES::

        sage: from sage.combinat.designs.database import CDF_201_5_1
        sage: from sage.combinat.designs.difference_family import is_difference_family
        sage: G, D = CDF_201_5_1()
        sage: is_difference_family(G,D,201,5,1)
        True

    The difference family is available from the constructor::

        sage: _ = designs.difference_family(201,5,1)
    """
    D = [[0,1,45,98,100], [0,3,32,65,89], [0,4,54,70,75],
         [0,6,49,69,91], [0,7,58,81,95], [0,8,34,72,90],
         [0,9,36,77,96], [0,10,35,83,94], [0,12,40,79,92],
         [0,15,46,76,93]]
    from sage.rings.finite_rings.integer_mod_ring import Zmod
    return Zmod(201), D

def CDF_221_5_1():
    r"""
    A cyclic `(221,5,1)`-difference family.

    From the examples VI.16.16 of [DesignHandbook]_.

    EXAMPLES::

        sage: from sage.combinat.designs.database import CDF_221_5_1
        sage: from sage.combinat.designs.difference_family import is_difference_family
        sage: G, D = CDF_221_5_1()
        sage: is_difference_family(G,D,221,5,1)
        True

    The difference family is available from the constructor::

        sage: _ = designs.difference_family(221,5,1)
    """
    D = [[0,1,24,61,116], [0,3,46,65,113], [0,4,73,89,130],
         [0,5,77,122,124], [0,6,39,50,118], [0,7,66,81,94],
         [0,8,38,64,139], [0,9,29,80,107], [0,10,35,93,135],
         [0,12,34,52,88], [0,14,31,63,84]]
    from sage.rings.finite_rings.integer_mod_ring import Zmod
    return Zmod(221), D

def CDF_273_17_1():
    r"""
    A cyclic `(273,17,1)`-difference set.

    EXAMPLES::

        sage: from sage.combinat.designs.database import CDF_273_17_1
        sage: from sage.combinat.designs.difference_family import is_difference_family
        sage: G,D = CDF_273_17_1()
        sage: is_difference_family(G,D,273,17,1)
        True

    The difference family is available from the constructor::

        sage: _ = designs.difference_family(273,17,1)
    """
    from sage.rings.finite_rings.integer_mod_ring import Zmod
    D = [(1,2,4,8,16,32,64,91,117,128,137,182,195,205,234,239,256)]
    return Zmod(273), D

# Index of the (right now cyclic or Abelian) difference families constructions
#
# Associates to triple (v,k,lambda) a function that return a
# (n,k,lambda)-difference family.
#
# This dictionary is used by designs.difference_family

DF_constructions = {
    (21,5,1): CDF_21_5_1,
    (25,4,1): ADF_5x5_4_1,
    (37,4,1): CDF_37_4_1,
    (81,5,1): CDF_81_5_1,
    (91,6,1): CDF_91_6_1,
    (121,5,1): CDF_121_5_1,
    (141,5,1): CDF_141_5_1,
    (161,5,1): CDF_161_5_1,
    (201,5,1): CDF_201_5_1,
    (221,5,1): CDF_221_5_1,
    (273,17,1): CDF_273_17_1,
}

def RBIBD_120_8_1():
    r"""
    Returns a resolvable `BIBD(120,8,1)`

    This function output a list ``L`` of `17\times 15` blocks such that
    ``L[i*15:(i+1)*15]`` is a partition of `120`.

    Construction shared by Julian R. Abel:

        Seiden's method: Start with a cyclic `(273,17,1)-BIBD` and let `B` be an
        hyperoval, i.e. a set which intersects any block of the BIBD in either 0
        (153 blocks) or 2 points (120 blocks). Dualise this design and take
        these last 120 blocks as points in the design; blocks in the design will
        correspond to the `273-18=255` non-hyperoval points.

        The design is also resolvable.  In the original `PG(2,16)` take any
        point `T` in the hyperoval and consider a block `B1` containing `T`.
        The `15` points in `B1` that do not belong to the hyperoval correspond
        to `15` blocks forming a parallel class in the dualised design. The
        other `16` parallel classes come in a similar way, by using point `T`
        and the other `16` blocks containing `T`.

    .. SEEALSO::

        :func:`OA_9_120`

    EXAMPLES::

        sage: from sage.combinat.designs.database import RBIBD_120_8_1
        sage: from sage.combinat.designs.bibd import _check_pbd
        sage: RBIBD = RBIBD_120_8_1()
        sage: _ = _check_pbd(RBIBD,120,[8])

    It is indeed resolvable, and the parallel classes are given by 17 slices of
    consecutive 15 blocks::

        sage: for i in range(17):
        ....:     assert len(set(sum(RBIBD[i*15:(i+1)*15],[]))) == 120

    The BIBD is available from the constructor::

        sage: _ = designs.balanced_incomplete_block_design(120,8)
    """
    from incidence_structures import IncidenceStructure
    n=273

    # Base block of a cyclic BIBD(273,16,1)
    B = [1,2,4,8,16,32,64,91,117,128,137,182,195,205,234,239,256]
    BIBD = [[(x+c)%n for x in B] for c in range(n)]

    # A (precomputed) set that every block of the BIBD intersects on 0 or 2 points
    hyperoval = [128, 192, 194, 4, 262, 140, 175, 48, 81, 180, 245, 271, 119, 212, 249, 189, 62, 255]
    #for B in BIBD:
    #    len_trace = sum(x in hyperoval for x in B)
    #    assert len_trace == 0 or len_trace == 2

    # Equivalence classes
    p = hyperoval[0]
    equiv = []
    new_BIBD = []
    for B in BIBD:
        if any(x in hyperoval for x in B):
            if p in B:
                equiv.append([x for x in B if x not in hyperoval])
        else:
            new_BIBD.append([x for x in B])

    BIBD = new_BIBD

    r = {v:i for i,v in enumerate(x for x in range(n) if x not in hyperoval)}
    BIBD  = [[r[x] for x in B] for B in BIBD ]
    equiv = [[r[x] for x in B] for B in equiv]

    BIBD = IncidenceStructure(range(255),BIBD)
    M = BIBD.incidence_matrix()

    equiv = [[M.nonzero_positions_in_row(x) for x in S] for S in equiv]
    return [B for S in equiv for B in S]

# Index of the BIBD constructions
#
# Associates to triple (v,k,lambda) a function that return a
# (n,k,lambda)-BIBD family.
#
# This dictionary is used by designs.BalancedIncompleteBlockDesign

BIBD_constructions = {
    (120,8,1): RBIBD_120_8_1,
}
