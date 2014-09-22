###########################################################################
#       Copyright (C) 2014 Martin Raum <martin@raum-brothers.eu>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
###########################################################################

from sage.misc.citation_items.citation_item import CitationItem

class ginac_CitationItem( CitationItem ):
    _name = "ginac"

    _bibtex = r"""
@misc{software-ginac,
    author = {Kreckel, Richard and others},
    title = {{GiNaC}},
    howpublished = {{\url{http://www.ginac.de}}}
}
    """
