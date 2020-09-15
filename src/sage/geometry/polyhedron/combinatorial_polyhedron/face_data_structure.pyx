"""
Cython data structure for combinatorial faces.
"""
# ****************************************************************************
#       Copyright (C) 2020 Jonathan Kliem <jonathan.kliem@fu-berlin.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  https://www.gnu.org/licenses/
# ****************************************************************************

include "sage/data_structures/bitset.pxi"

from sage.ext.memory_allocator  cimport MemoryAllocator

ctypedef int simple
ctypedef long standard

ctypedef fused algorithm_variant:
    simple
    standard

#############################################################################
# Face Initalization
#############################################################################

cdef inline bint face_init(face_t face, mp_bitcnt_t n_coatoms, mp_bitcnt_t n_atoms, MemoryAllocator mem) except -1:
    """
    Initialize and clear ``face`` using the memory allocator.
    """
    bitset_init_with_allocator(face.atoms, n_atoms, mem)
    bitset_init_with_allocator(face.coatoms, n_coatoms, mem)

cdef inline bint face_check_alignment(face_t face):
    """
    Return whether the data is correctly aligned.
    """
    return bitset_check_alignment(face.atoms) and bitset_check_alignment(face.coatoms)

cdef inline void face_clear(face_t face):
    """
    Remove all atoms and coatoms from face.
    """
    bitset_clear(face.atoms)
    bitset_clear(face.coatoms)

cdef inline void face_copy(face_t dst, face_t src):
    """
    Copy src to dst overwriting dst.

    dst may contain more atoms and coatoms, but not less.
    """
    bitset_copy_flex(dst.atoms, src.atoms)
    bitset_copy_flex(dst.coatoms, src.coatoms)


#############################################################################
# Face Comparison
#############################################################################

cdef inline bint face_isempty(face_t face) nogil:
    """
    Return whether ``face`` contains no coatoms.
    """
    return bitset_isempty(face.atoms)

cdef inline int face_cmp(face_t a, face_t b):
    """
    Return ``0`` if the faces are equal and consistently
    ``-1`` and ``1`` if not.
    """
    return bitset_cmp(a.atoms, b.atoms)

cdef inline bint face_issubset(face_t a, face_t b, algorithm_variant algorithm=<standard> 0) nogil:
    """
    Return whether ``a`` is a subface of ``b``.
    """
    if algorithm_variant is standard:
        return bitset_issubset(a.atoms, b.atoms)
    else:
        return bitset_issuperset(a.coatoms, b.coatoms)


#############################################################################
# Face Bit Manipulation
#############################################################################

cdef inline bint face_atom_in(face_t face, mp_bitcnt_t n):
    """
    Return whether ``n`` is an atom of ``face``.
    """
    return bitset_in(face.atoms, n)

cdef inline void face_add_atom(face_t face, mp_bitcnt_t n):
    """
    Add atom `n` to the face.
    """
    bitset_add(face.atoms, n)

cdef inline int face_add_atom_safe(face_t face, mp_bitcnt_t n) except -1:
    """
    Add atom `n` to the face.
    """
    if (n > face.atoms.size):
        raise KeyError(n)
    bitset_add(face.atoms, n)

cdef inline void face_discard_atom(face_t face, mp_bitcnt_t n):
    """
    Discard atom `n` of the face.
    """
    bitset_discard(face.atoms, n)

cdef inline void facet_set_coatom(face_t face, mp_bitcnt_t n):
    """
    Set the facet to be coatom ``n``.
    """
    bitset_clear(face.coatoms)
    bitset_add(face.coatoms, n)

cdef inline void face_set_first_n_atoms(face_t face, mp_bitcnt_t n):
    """
    Set exactly the first ``n`` atoms.
    """
    bitset_set_first_n(face.atoms, n)


#############################################################################
# Face Searching
#############################################################################

cdef inline long face_next_atom(face_t face, mp_bitcnt_t n):
    """
    Return the index of the next atom in ``face`` with index >= ``n``.

    In case there are none, return ``-1``.
    """
    return bitset_next(face.atoms, n)

cdef inline long face_len_atoms(face_t face) nogil:
    """
    Calculate the number of atoms in the face.
    """
    return bitset_len(face.atoms)


#############################################################################
# Arithmetic
#############################################################################

cdef inline void intersection(face_t dest, face_t A, face_t B, algorithm_variant algorithm=<standard> 0) nogil:
    """
    Set ``dest`` to the intersection of ``A`` and ``B``.
    """
    bitset_intersection(dest.atoms, A.atoms, B.atoms)
    if algorithm_variant is simple:
        bitset_union(dest.coatoms, A.coatoms, B.coatoms)

